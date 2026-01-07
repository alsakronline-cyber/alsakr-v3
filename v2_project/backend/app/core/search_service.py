"""
Search Service Layer
Unified search interface for Elasticsearch and Qdrant (Asynchronous)
"""
from typing import List, Dict, Optional
from elasticsearch import AsyncElasticsearch
from qdrant_client import AsyncQdrantClient
import httpx
import logging

from .config import settings, get_es_url, get_qdrant_url

logger = logging.getLogger(__name__)

class SearchService:
    """Unified asynchronous search service for products"""
    
    def __init__(self):
        self.es = AsyncElasticsearch([get_es_url()])
        # Note: QdrantClient has an async version but usually we use AsyncQdrantClient
        self.qdrant = AsyncQdrantClient(url=get_qdrant_url())
        self.ollama_url = settings.OLLAMA_HOST
    
    async def text_search(self, query: str, size: int = 10, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Full-text search in Elasticsearch (Async)
        """
        # Build query - use should clauses for better part number matching
        should_clauses = [
            {
                "term": {
                    "part_number": {
                        "value": query,
                        "boost": 10.0
                    }
                }
            },
            {
                "match": {
                    "part_number": {
                        "query": query,
                        "boost": 5.0
                    }
                }
            },
            {
                "multi_match": {
                    "query": query,
                    "fields": ["name^3", "description^2", "category"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            }
        ]
        
        filter_clauses = []
        if filters:
            if 'category' in filters:
                filter_clauses.append({"term": {"category.keyword": filters['category']}})
            if 'phased_out' in filters:
                filter_clauses.append({"term": {"phased_out": filters['phased_out']}})
        
        es_query = {
            "query": {
                "bool": {
                    "should": should_clauses,
                    "filter": filter_clauses,
                    "minimum_should_match": 1
                }
            },
            "size": size,
            "highlight": {
                "fields": {
                    "name": {},
                    "description": {}
                }
            }
        }
        
        try:
            result = await self.es.search(
                index=settings.ES_PRODUCTS_INDEX,
                body=es_query
            )
            
            products = []
            for hit in result['hits']['hits']:
                product = hit['_source']
                product['_score'] = hit['_score']
                product['_highlights'] = hit.get('highlight', {})
                products.append(product)
            
            return products
            
        except Exception as e:
            logger.error(f"Elasticsearch search error: {e}")
            return []
    
    async def semantic_search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Vector similarity search in Qdrant (Async)
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": settings.OLLAMA_EMBEDDING_MODEL,
                        "prompt": query
                    },
                    timeout=30
                )
            
            if response.status_code != 200:
                logger.error(f"Ollama embedding failed: {response.text}")
                return []
            
            query_vector = response.json()['embedding']
            
            # Search Qdrant
            results = await self.qdrant.search(
                collection_name=settings.QDRANT_PRODUCTS_COLLECTION,
                query_vector=query_vector,
                limit=limit
            )
            
            products = []
            for result in results:
                product = result.payload
                product['_score'] = result.score
                products.append(product)
            
            return products
            
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            return []
    
    async def hybrid_search(self, query: str, size: int = 10) -> List[Dict]:
        """
        Combine text and semantic search for best results (Async)
        """
        # Get results from both
        text_results = await self.text_search(query, size=size)
        semantic_results = await self.semantic_search(query, limit=size)
        
        merged = {}
        
        for product in text_results:
            part_no = product.get('part_number')
            if part_no:
                merged[part_no] = product
                merged[part_no]['text_score'] = product.get('_score', 0)
                merged[part_no]['combined_score'] = product.get('_score', 0) * 0.3
        
        for product in semantic_results:
            part_no = product.get('part_number')
            if part_no:
                if part_no in merged:
                    merged[part_no]['semantic_score'] = product.get('_score', 0)
                    merged[part_no]['combined_score'] = (
                        merged[part_no]['text_score'] * 0.6 +
                        product.get('_score', 0) * 0.4
                    )
                else:
                    merged[part_no] = product
                    merged[part_no]['semantic_score'] = product.get('_score', 0)
                    merged[part_no]['combined_score'] = product.get('_score', 0) * 0.4
        
        results = sorted(
            merged.values(),
            key=lambda x: x.get('combined_score', 0),
            reverse=True
        )
        
        return results[:size]
    
    async def get_product(self, part_number: str) -> Optional[Dict]:
        """Get single product by part number (Async)"""
        try:
            result = await self.es.get(
                index=settings.ES_PRODUCTS_INDEX,
                id=part_number
            )
            return result['_source']
        except:
            return None
    
    async def get_similar_products(self, part_number: str, limit: int = 5) -> List[Dict]:
        """Find similar products based on a given product (Async)"""
        product = await self.get_product(part_number)
        if not product:
            return []
        
        query = f"{product.get('name')} {product.get('description', '')}"
        results = await self.semantic_search(query, limit=limit + 1)
        
        return [r for r in results if r.get('part_number') != part_number][:limit]
    
    async def get_categories(self) -> List[str]:
        """Get all unique product categories (Async)"""
        try:
            result = await self.es.search(
                index=settings.ES_PRODUCTS_INDEX,
                body={
                    "size": 0,
                    "aggs": {
                        "categories": {
                            "terms": {
                                "field": "category.keyword",
                                "size": 100
                            }
                        }
                    }
                }
            )
            
            buckets = result['aggregations']['categories']['buckets']
            return [b['key'] for b in buckets]
            
        except:
            return []

    async def close(self):
        """Cleanly close connections"""
        await self.es.close()
        # Qdrant client close if needed
