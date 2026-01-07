import os
from elasticsearch import AsyncElasticsearch, TransportError

ES_HOST = os.getenv("ES_HOST", "elasticsearch")
ES_URL = f"http://{ES_HOST}:9200"

class ElasticsearchClient:
    def __init__(self):
        # Using elasticsearch client 8.11.x to match ES server version
        self.client = AsyncElasticsearch(hosts=[ES_URL])

    async def check_health(self):
        """Verifies connection to Elasticsearch."""
        try:
            return await self.client.info()
        except Exception as e:
            print(f"⚠️ Elasticsearch Connection Failed: {e}")
            return None

    async def create_indices(self):
        """Creates core indices if they don't exist. Retries if ES is not ready."""
        import asyncio
        max_retries = 10
        delay = 5

        for i in range(max_retries):
            try:
                # 1. Parts Index
                if not await self.client.indices.exists(index="parts"):
                    await self.client.indices.create(index="parts", body={
                        "mappings": {
                            "properties": {
                                "sku": {"type": "keyword"},
                                "description": {"type": "text"},
                                "brand": {"type": "keyword"},
                                "specs": {"type": "object"}
                            }
                        }
                    })
                    print("✅ Created Index: parts")

                # 2. Suppliers Index
                if not await self.client.indices.exists(index="suppliers"):
                    await self.client.indices.create(index="suppliers", body={
                        "mappings": {
                            "properties": {
                                "name": {"type": "text"},
                                "brands": {"type": "keyword"},
                                "location": {"type": "geo_point"},
                                "verified": {"type": "boolean"}
                            }
                        }
                    })
                    print("✅ Created Index: suppliers")
                return # Success!
            except Exception as e:
                print(f"⌛ Waiting for Elasticsearch... ({i+1}/{max_retries}) - {e}")
                await asyncio.sleep(delay)
        print("❌ Could not connect to Elasticsearch after 10 attempts.")

    async def close(self):
        await self.client.close()

# Global Instance
es_client = ElasticsearchClient()
