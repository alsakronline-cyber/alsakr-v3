"""
Qdrant Vector Embedding Generation Script
Generate and store vector embeddings for SICK products using Ollama
"""
import sys
import json
import time
import uuid
from typing import List, Dict, Optional
from elasticsearch import Elasticsearch
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import requests

from app.core.config import settings, get_es_url, get_qdrant_url


class EmbeddingGenerator:
    """Generate and store product vectors in Qdrant"""
    
    def __init__(self):
        self.es = Elasticsearch([get_es_url()])
        self.qdrant = QdrantClient(url=get_qdrant_url())
        self.collection_name = settings.QDRANT_PRODUCTS_COLLECTION
        self.ollama_url = settings.OLLAMA_HOST
        self.embedding_model = settings.OLLAMA_EMBEDDING_MODEL
        
    def check_ollama(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            # Check health
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
            
            # Check if embedding model exists
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            if not any(self.embedding_model in name for name in model_names):
                print(f"⚠️  Model '{self.embedding_model}' not found.")
                print(f"   Available models: {', '.join(model_names)}")
                print(f"\n   Run: docker exec alsakr-ollama ollama pull {self.embedding_model}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {e}")
            return False
    
    def create_collection(self):
        """Create Qdrant collection for product vectors"""
        # Delete if exists
        try:
            self.qdrant.delete_collection(collection_name=self.collection_name)
            print(f"⚠️  Collection '{self.collection_name}' deleted.")
        except:
            pass
        
        # Create collection
        self.qdrant.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=settings.QDRANT_VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"✅ Created collection: {self.collection_name}")
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['embedding']
            else:
                print(f"  ✗ Embedding error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ✗ Embedding failed: {e}")
            return None
    
    def create_product_text(self, product: Dict) -> str:
        """Create searchable text representation of product"""
        parts = []
        
        # Basic info
        if product.get('name'):
            parts.append(f"Product: {product['name']}")
        
        if product.get('part_number'):
            parts.append(f"Part Number: {product['part_number']}")
        
        if product.get('description'):
            parts.append(f"Description: {product['description']}")
        
        if product.get('category'):
            parts.append(f"Category: {product['category']}")
        
        # Specifications (if available as structured data)
        specs = product.get('specifications')
        if specs and isinstance(specs, dict):
            spec_text = []
            for key, value in specs.items():
                # Limit to key specifications to avoid token limits
                if 'Features' in key or 'product' in key.lower():
                    spec_text.append(f"{key}: {value}")
            
            if spec_text:
                parts.append("Specifications: " + "; ".join(spec_text[:10]))
        
        return " | ".join(parts)
    
    def get_products_from_es(self) -> List[Dict]:
        """Fetch all products from Elasticsearch"""
        products = []
        
        # Use scroll API for large datasets
        result = self.es.search(
            index=settings.ES_PRODUCTS_INDEX,
            body={
                "query": {"match_all": {}},
                "size": 100
            },
            scroll='2m'
        )
        
        scroll_id = result['_scroll_id']
        hits = result['hits']['hits']
        
        while hits:
            for hit in hits:
                products.append({
                    "id": hit['_id'],
                    **hit['_source']
                })
            
            # Get next batch
            result = self.es.scroll(scroll_id=scroll_id, scroll='2m')
            scroll_id = result['_scroll_id']
            hits = result['hits']['hits']
        
        return products
    
    def batch_process_embeddings(self, products: List[Dict]):
        """Process products in batches and store vectors"""
        total = len(products)
        batch_size = settings.BATCH_SIZE
        processed = 0
        errors = 0
        
        print(f"\n📊 Processing {total} products in batches of {batch_size}...")
        
        for i in range(0, total, batch_size):
            batch = products[i:i+batch_size]
            points = []
            
            for product in batch:
                # Create embedding text
                text = self.create_product_text(product)
                
                # Generate embedding
                vector = self.generate_embedding(text)
                
                if vector:
                    # Generate a consistent UUID from the part_number
                    # Qdrant requires IDs to be UUIDs or unsigned 64-bit integers
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"alsakr.product.{product['part_number']}"))
                    
                    # Create point
                    point = PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "part_number": product.get('part_number'),
                            "name": product.get('name'),
                            "description": product.get('description'),
                            "category": product.get('category'),
                            "url": product.get('url'),
                            "image_url": product.get('image_urls', [])[0] if product.get('image_urls') else None,
                            "pdf_url": product.get('pdf_url')
                        }
                    )
                    points.append(point)
                    processed += 1
                else:
                    errors += 1
                
                # Progress indicator
                if (processed + errors) % 10 == 0:
                    print(f"  ✓ {processed + errors}/{total} processed...")
            
            # Upload batch to Qdrant
            if points:
                try:
                    self.qdrant.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                except Exception as e:
                    print(f"  ✗ Batch upload error: {e}")
                    # If it's a 400 error, print more info
                    if hasattr(e, 'response') and e.response is not None:
                        print(f"  Response: {e.response.text}")
                    errors += len(points)
            
            # Small delay to avoid overwhelming Ollama
            time.sleep(0.5)
        
        return {
            "total": total,
            "processed": processed,
            "errors": errors
        }
    
    def verify_collection(self):
        """Verify collection and show sample"""
        info = self.qdrant.get_collection(collection_name=self.collection_name)
        count = info.points_count
        
        print(f"\n📊 Total vectors stored: {count}")
        
        # Get a sample point
        if count > 0:
            result = self.qdrant.scroll(
                collection_name=self.collection_name,
                limit=1,
                with_vectors=True
            )[0]
            
            if result:
                sample = result[0]
                print(f"\n📦 Sample vector:")
                print(f"  ID: {sample.id}")
                print(f"  Payload: {json.dumps(sample.payload, indent=2)}")
                if hasattr(sample, 'vector') and sample.vector:
                    print(f"  Vector dimension: {len(sample.vector)}")
                else:
                    print("  Vector dimension: [Hidden/Not Loaded]")


def main():
    """Main execution"""
    print("=" * 70)
    print("🧠 SICK Product Embedding Generation for Qdrant")
    print("=" * 70)
    
    generator = EmbeddingGenerator()
    
    # Step 0: Check Ollama
    print("\n[Step 0/4] Checking Ollama connection...")
    if not generator.check_ollama():
        print("\n❌ Prerequisites not met. Please ensure:")
        print(f"  1. Ollama is running at {settings.OLLAMA_HOST}")
        print(f"  2. Model '{settings.OLLAMA_EMBEDDING_MODEL}' is pulled")
        return 1
    print(f"✅ Ollama ready with model '{generator.embedding_model}'")
    
    # Step 1: Create collection
    print("\n[Step 1/4] Creating Qdrant collection...")
    generator.create_collection()
    
    # Step 2: Get products
    print("\n[Step 2/4] Fetching products from Elasticsearch...")
    products = generator.get_products_from_es()
    print(f"✅ Retrieved {len(products)} products")
    
    # Step 3: Generate embeddings
    print("\n[Step 3/4] Generating embeddings...")
    print("⏳ This may take 10-30 minutes depending on product count...")
    result = generator.batch_process_embeddings(products)
    
    print(f"\n✅ Embedding generation completed!")
    print(f"  - Total: {result['total']} products")
    print(f"  - Processed: {result['processed']} vectors")
    print(f"  - Errors: {result['errors']}")
    
    # Step 4: Verify
    print("\n[Step 4/4] Verifying collection...")
    generator.verify_collection()
    
    print("\n" + "=" * 70)
    print("✨ Embeddings ready! Semantic search enabled.")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
