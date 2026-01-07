"""
PDF Processing and Indexing Script
Download, extract, and index product datasheets for RAG retrieval
"""
import sys
import os
import time
from typing import List, Dict, Optional
from pathlib import Path
import requests
from elasticsearch import Elasticsearch, helpers
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import hashlib
import pdfplumber
from PIL import Image
import io

from app.core.config import settings, get_es_url, get_qdrant_url, get_pdf_dir_path


class PDFProcessor:
    """Process PDF datasheets for product documentation"""
    
    def __init__(self):
        self.es = Elasticsearch([get_es_url()])
        self.qdrant = QdrantClient(url=get_qdrant_url())
        self.pdf_dir = get_pdf_dir_path()
        self.ollama_url = settings.OLLAMA_HOST
        
    def create_es_index(self):
        """Create Elasticsearch index for PDF chunks"""
        index_name = settings.ES_PDF_INDEX
        
        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "part_number": {"type": "keyword"},
                    "product_name": {"type": "text"},
                    "chunk_id": {"type": "keyword"},
                    "chunk_text": {"type": "text"},
                    "chunk_index": {"type": "integer"},
                    "pdf_url": {"type": "keyword"},
                    "local_path": {"type": "keyword"},
                    "page_hint": {"type": "keyword"},
                    "indexed_at": {"type": "date"}
                }
            }
        }
        
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)
        
        self.es.indices.create(index=index_name, body=mapping)
        print(f"✅ Created PDF index: {index_name}")
    
    def create_qdrant_collection(self):
        """Create Qdrant collection for PDF vectors"""
        collection_name = settings.QDRANT_PDF_COLLECTION
        
        try:
            self.qdrant.delete_collection(collection_name=collection_name)
        except:
            pass
        
        self.qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.QDRANT_VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"✅ Created PDF collection: {collection_name}")
    
    def download_pdf(self, url: str, part_number: str) -> Optional[str]:
        """Download PDF and save to local directory"""
        if not url or url == "N/A":
            return None
        
        try:
            # Create safe filename
            filename = f"{part_number}.pdf"
            filepath = os.path.join(self.pdf_dir, filename)
            
            # Skip if already downloaded
            if os.path.exists(filepath):
                return filepath
            
            # Download
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Save
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return filepath
            
        except Exception as e:
            print(f"  ✗ Download failed: {e}")
            return None
    
    def extract_text_simple(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF using pdfplumber
        """
        try:
            text_content = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Extract text
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                    
                    # Optional: access tables via page.extract_tables()
            
            return "\\n".join(text_content)
        except Exception as e:
            print(f"  ✗ PDF Extraction Error: {e}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap
        
        return chunks
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": settings.OLLAMA_EMBEDDING_MODEL,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['embedding']
            return None
            
        except Exception as e:
            print(f"  ✗ Embedding error: {e}")
            return None
    
    def process_pdf(self, product: Dict) -> Dict:
        """Process a single product PDF"""
        part_number = product.get('part_number')
        pdf_url = product.get('pdf_url')
        
        stats = {
            "downloaded": False,
            "chunks_created": 0,
            "chunks_indexed": 0
        }
        
        # Download PDF
        pdf_path = self.download_pdf(pdf_url, part_number)
        if not pdf_path:
            return stats
        
        stats['downloaded'] = True
        
        # Extract text (simplified for now)
        text = self.extract_text_simple(pdf_path)
        if not text:
            return stats
        
        # Chunk text
        chunks = self.chunk_text(text, settings.PDF_CHUNK_SIZE, settings.PDF_CHUNK_OVERLAP)
        stats['chunks_created'] = len(chunks)
        
        # Index chunks
        for idx, chunk_text in enumerate(chunks):
            # Create chunk ID
            chunk_id = hashlib.md5(f"{part_number}_{idx}".encode()).hexdigest()
            
            # Index to Elasticsearch
            doc = {
                "part_number": part_number,
                "product_name": product.get('name'),
                "chunk_id": chunk_id,
                "chunk_text": chunk_text,
                "chunk_index": idx,
                "pdf_url": pdf_url,
                "local_path": pdf_path,
                "page_hint": f"Page ~{idx + 1}"
            }
            
            try:
                self.es.index(index=settings.ES_PDF_INDEX, id=chunk_id, document=doc)
                stats['chunks_indexed'] += 1
            except Exception as e:
                print(f"  ✗ ES indexing error: {e}")
            
            # Generate and store vector (optional - can be slow)
            # Uncomment if you want vectors for PDF chunks
            # vector = self.generate_embedding(chunk_text)
            # if vector:
            #     point = PointStruct(
            #         id=chunk_id,
            #         vector=vector,
            #         payload=doc
            #     )
            #     self.qdrant.upsert(
            #         collection_name=settings.QDRANT_PDF_COLLECTION,
            #         points=[point]
            #     )
        
        return stats
    
    def process_all_pdfs(self):
        """Process all product PDFs"""
        # Get products with PDFs
        result = self.es.search(
            index=settings.ES_PRODUCTS_INDEX,
            body={
                "query": {
                    "bool": {
                        "must_not": {"term": {"pdf_url": "N/A"}},
                        "must": {"exists": {"field": "pdf_url"}}
                    }
                },
                "size": 1000
            }
        )
        
        products = [hit['_source'] for hit in result['hits']['hits']]
        total = len(products)
        
        print(f"\n📊 Found {total} products with PDFs")
        print("⏳ Note: Full PDF processing requires PyPDF2/pdfplumber")
        print("   Currently using placeholder extraction\n")
        
        stats = {
            "total": total,
            "downloaded": 0,
            "chunks_created": 0,
            "chunks_indexed": 0
        }
        
        for i, product in enumerate(products, 1):
            print(f"[{i}/{total}] Processing {product.get('part_number')}...")
            
            result = self.process_pdf(product)
            
            if result['downloaded']:
                stats['downloaded'] += 1
            stats['chunks_created'] += result['chunks_created']
            stats['chunks_indexed'] += result['chunks_indexed']
            
            # Small delay
            time.sleep(0.2)
        
        return stats


def main():
    """Main execution"""
    print("=" * 70)
    print("📄 SICK Product PDF Processing")
    print("=" * 70)
    print("\n⚠️  IMPORTANT: For production PDF text extraction, install:")
    print("   pip install PyPDF2 pdfplumber")
    print("   Then update extract_text_simple() method\n")
    
    processor = PDFProcessor()
    
    # Step 1: Create indices
    print("[Step 1/3] Creating storage indices...")
    processor.create_es_index()
    processor.create_qdrant_collection()
    
    # Step 2: Process PDFs
    print("\n[Step 2/3] Processing PDFs...")
    stats = processor.process_all_pdfs()
    
    print(f"\n✅ PDF processing completed!")
    print(f"  - Total PDFs found: {stats['total']}")
    print(f"  - Downloaded: {stats['downloaded']}")
    print(f"  - Text chunks created: {stats['chunks_created']}")
    print(f"  - Chunks indexed: {stats['chunks_indexed']}")
    
    # Step 3: Verify
    print("\n[Step 3/3] Verifying...")
    count = processor.es.count(index=settings.ES_PDF_INDEX)['count']
    print(f"📊 Total chunks in Elasticsearch: {count}")
    
    print("\n" + "=" * 70)
    print("✨ PDF processing complete!")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
