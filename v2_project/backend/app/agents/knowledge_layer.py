import json
from typing import Dict, Any, List
from .base import BaseAgent
from ..core.es_client import es_client
from qdrant_client import QdrantClient
from ..core.config import get_qdrant_url, settings
import requests

# AGENT 4: InventoryVoice
class InventoryVoiceAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
        You are the 'InventoryVoice' clerk for Al Sakr Online.
        Your job is to parse voice transcripts into inventory actions.
        
        ACTIONS:
        - QUERY: "How many [Part] do we have?"
        - UPDATE: "We just used 5 [Part]" or "Restocked 20 [Part]".
        
        JSON OUTPUT:
        {
            "action": "QUERY/UPDATE",
            "target": "Part Name/SKU",
            "quantity": 0,
            "response_text": "Friendly confirmation"
        }
        """
        super().__init__(name="InventoryVoice", system_prompt=system_prompt)

    async def parse_voice_command(self, transcript: str) -> Dict[str, Any]:
        """Parses speech text and queries ES."""
        response_text = await self.run(transcript)
        try:
            parsed = json.loads(response_text)
            # If action is QUERY, perform ES lookup
            if parsed["action"] == "QUERY":
                # Logic to query 'inventory' index
                pass
            return parsed
        except:
            return {"raw_response": response_text}

# AGENT 5: Tech Doc Assistant (RAG Enabled)
class TechDocAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
        You are the 'Technical Documentation Assistant'.
        You have access to a database of product manuals and datasheets.
        
        GOAL:
        Answer user questions about technical specifications, wiring, installation, and troubleshooting 
        based STRICTLY on the provided context chunks.
        
        If the context doesn't contain the answer, say "I couldn't find that specific information in the manuals."
        """
        super().__init__(name="TechDoc", system_prompt=system_prompt)
        self.qdrant = QdrantClient(url=get_qdrant_url())
        self.ollama_url = settings.OLLAMA_HOST

    async def _get_embedding(self, text: str) -> List[float]:
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": settings.OLLAMA_EMBEDDING_MODEL,
                    "prompt": text
                },
                timeout=10
            )
            if response.status_code == 200:
                return response.json()['embedding']
        except Exception as e:
            print(f"Embedding error: {e}")
        return []

    async def query_manuals(self, query: str, limit: int = 3) -> str:
        """
        RAG Workflow:
        1. Embed query.
        2. Search Qdrant PDF collection.
        3. Pass chunks + query to LLM.
        """
        # 1. Embed
        query_vector = await self._get_embedding(query)
        if not query_vector:
            return "Error: Could not process query."

        # 2. Search
        try:
            results = self.qdrant.search(
                collection_name=settings.QDRANT_PDF_COLLECTION,
                query_vector=query_vector,
                limit=limit
            )
        except Exception:
            return "Knowledge base unavailable."

        # 3. Construct Context
        context_text = ""
        for hit in results:
            payload = hit.payload
            info = f"Source: {payload.get('product_name')} ({payload.get('part_number')})\nContent: {payload.get('chunk_text')}\n---\n"
            context_text += info

        if not context_text:
            return "No relevant technical documents found."

        # 4. Ask LLM
        prompt = f"""
        Context from Manuals:
        {context_text}
        
        User Question: {query}
        
        Answer based on the context:
        """
        
        return await self.run(prompt)
