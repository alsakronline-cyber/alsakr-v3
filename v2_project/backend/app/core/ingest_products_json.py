"""
Elasticsearch Product Ingestion Script (JSON)
Import SICK products from JSON to Elasticsearch with proper mapping
"""
import json
import sys
import os
from typing import Dict, List, Optional
from elasticsearch import Elasticsearch, helpers
from datetime import datetime

# We can import config/settings if the path allows, or just hardcode/env var for standalone
# Assuming running inside container as module: python -m app.core.ingest_products_json
from app.core.config import settings, get_es_url

JSON_PATH = "/data/products.json"

class ProductIngesterJSON:
    """Handle product data ingestion from JSON into Elasticsearch"""
    
    def __init__(self):
        self.es = Elasticsearch([get_es_url()], request_timeout=30)
        self.index_name = settings.ES_PRODUCTS_INDEX
        self.json_path = JSON_PATH
        
    def create_index(self):
        """Create Elasticsearch index with proper mapping"""
        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "index.mapping.total_fields.limit": 5000,
                "analysis": {
                    "analyzer": {
                        "product_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "asciifolding"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "part_number": {"type": "keyword"},
                    "url": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "analyzer": "product_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "product_analyzer"
                    },
                    "category": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "actual_part_no": {"type": "keyword"},
                    "price_teaser": {"type": "text"},
                    "phased_out": {"type": "boolean"},
                    "successor_product": {"type": "text"},
                    "certificates": {"type": "keyword"},
                    "specifications": {"type": "flattened"},
                    "suitable_accessories": {"type": "text"},
                    "image_urls": {"type": "keyword"},
                    "local_image_paths": {"type": "keyword"},
                    "pdf_url": {"type": "keyword"},
                    "indexed_at": {"type": "date"}
                }
            }
        }
        
        if self.es.indices.exists(index=self.index_name):
            print(f"⚠️  Index '{self.index_name}' already exists. Deleting...")
            self.es.indices.delete(index=self.index_name)
        
        self.es.indices.create(index=self.index_name, body=mapping)
        print(f"✅ Created index: {self.index_name}")
    
    def parse_json_field(self, value: str) -> Optional[Dict]:
        """Parse JSON string fields safely"""
        if not value or value == "N/A":
            return None
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
    
    def parse_boolean(self, value: str) -> bool:
        """Convert string to boolean"""
        if isinstance(value, bool):
            return value
        return str(value).lower() in ['yes', 'true', '1']
    
    def parse_list(self, value: str, delimiter: str = '|') -> List[str]:
        """Parse delimited string to list"""
        if not value or value == "N/A":
            return []
        if isinstance(value, list):
            return value
        return [item.strip() for item in value.split(delimiter) if item.strip()]
    
    def process_product(self, row: Dict) -> Dict:
        """Transform JSON item to Elasticsearch document"""
        return {
            "part_number": str(row.get("part_number", "")).strip(),
            "url": row.get("url", "").strip(),
            "name": row.get("name", "").strip(),
            "description": row.get("description", "").strip(),
            "category": row.get("category", "").strip(),
            "actual_part_no": str(row.get("actual_part_no", "")).strip(),
            "price_teaser": row.get("price_teaser", "").strip(),
            "phased_out": self.parse_boolean(row.get("phased_out", "No")),
            "successor_product": row.get("successor_product", "").strip(),
            "certificates": self.parse_list(row.get("certificates", "")),
            "specifications": self.parse_json_field(row.get("specifications", "")),
            "suitable_accessories": row.get("suitable_accessories", "").strip(),
            "image_urls": self.parse_list(row.get("image_urls", "")),
            "local_image_paths": self.parse_list(row.get("local_image_paths", "")),
            "pdf_url": row.get("pdf_url", "").strip(),
            "indexed_at": datetime.utcnow().isoformat()
        }
    
    def bulk_index_products(self) -> Dict:
        """Read JSON and bulk index all products"""
        print(f"📖 Reading products from: {self.json_path}")
        
        actions = []
        processed = 0
        errors = 0
        
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
                
                if not isinstance(products, list):
                    print("❌ JSON root is not a list")
                    return {"success": False, "error": "Invalid JSON format"}
                
                total = len(products)
                print(f"📊 Found {total} products in JSON")

                for row in products:
                    try:
                        doc = self.process_product(row)
                        
                        if not doc['part_number']:
                            continue
                        
                        action = {
                            "_index": self.index_name,
                            "_id": doc['part_number'],
                            "_source": doc
                        }
                        actions.append(action)
                        processed += 1
                        
                        if len(actions) >= 100:
                            success, failed = helpers.bulk(self.es, actions, raise_on_error=False)
                            if failed:
                                for item in failed:
                                    print(f"  ✗ Index error for {item['index']['_id']}: {item['index']['error']['reason']}")
                            errors += len(failed)
                            actions = []
                            print(f"  ✓ Indexed {processed}/{total} products...")
                            
                    except Exception as e:
                        print(f"  ✗ Error processing item: {e}")
                        errors += 1
                
                if actions:
                    success, failed = helpers.bulk(self.es, actions, raise_on_error=False)
                    if failed:
                        for item in failed:
                            print(f"  ✗ Index error for {item['index']['_id']}: {item['index']['error']['reason']}")
                    errors += len(failed)
        
        except FileNotFoundError:
            print(f"❌ JSON file not found: {self.json_path}")
            return {"success": False, "error": "JSON file not found"}
        
        self.es.indices.refresh(index=self.index_name)
        count = self.es.count(index=self.index_name)['count']
        
        return {
            "success": True,
            "processed": processed,
            "indexed": count,
            "errors": errors
        }
    
    def verify_index(self):
        count = self.es.count(index=self.index_name)['count']
        print(f"\n📊 Total products indexed: {count}")
        result = self.es.search(index=self.index_name, body={"query": {"match_all": {}}, "size": 1})
        if result['hits']['hits']:
            sample = result['hits']['hits'][0]['_source']
            print(f"\n📦 Sample product: {sample.get('part_number')} - {sample.get('name')}")

def main():
    print("=" * 70)
    print("🚀 SICK Product Ingestion to Elasticsearch (JSON)")
    print("=" * 70)
    ingester = ProductIngesterJSON()
    print("\n[Step 1/3] Creating Elasticsearch index...")
    ingester.create_index()
    print("\n[Step 2/3] Importing products from JSON...")
    result = ingester.bulk_index_products()
    if result['success']:
        print(f"\n✅ Import completed! Indexed: {result['indexed']}")
    else:
        print(f"\n❌ Import failed: {result.get('error')}")
        return 1
    print("\n[Step 3/3] Verifying index...")
    ingester.verify_index()
    print("\nDONE.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
