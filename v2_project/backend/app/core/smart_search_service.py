"""
Smart Search Service
Analyzes user queries for ambiguity and technical specifications.
"""
import logging
import json
import httpx
from typing import List, Dict, Optional
from .config import settings
from .search_service import SearchService

logger = logging.getLogger(__name__)

class SmartSearchService:
    """Intelligent search layer with LLM analysis (Async)"""
    
    def __init__(self):
        self.search_service = SearchService()
        self.ollama_url = f"{settings.OLLAMA_HOST}/api/generate"
        self.model = settings.OLLAMA_CHAT_MODEL
    
    async def analyze_query(self, query: str, context: Optional[List[Dict]] = None) -> Dict:
        """
        Use LLM to detect ambiguity and extract technical constraints (Async)
        """
        # Unified prompt for extraction and ambiguity detection
        prompt = f"""
        Analyze this industrial procurement query: "{query}"
        
        Tasks:
        1. Determine if the query is specific (e.g., includes a part number or detailed spec) or ambiguous/broad.
        2. If specific, extract part numbers and requirements.
        3. If ambiguous, generate a single clear question to narrow down the search.
        
        Return JSON format:
        {{
            "status": "specific" | "ambiguous",
            "extracted_part_number": "string or null",
            "requirements": {{}},
            "clarification_question": "string or null"
        }}
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.ollama_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    },
                    timeout=30 # Increased timeout for slow VPS inference
                )
            
            if response.status_code == 200:
                result = response.json()
                return json.loads(result['response'])
            
            return {"status": "specific", "extracted_part_number": None, "requirements": {}}
            
        except Exception as e:
            logger.error(f"LLM query analysis failed: {e}")
            # Fallback to direct search if LLM fails
            return {"status": "specific", "extracted_part_number": None, "requirements": {}}
    
    async def smart_search(self, query: str, context: List[Dict] = None) -> Dict:
        """
        Orchestrate the smart search flow (Async).
        """
        # 1. Analyze Query with Context
        analysis = await self.analyze_query(query)
        
        # 2. Perform Hybrid Search
        search_query = query
        if context:
            last_msg = context[-1].get('content', '') if context else ''
            if len(query.split()) < 3 and last_msg:
                 search_query = f"{last_msg} {query}"

        results = await self.search_service.hybrid_search(search_query, size=10)
        
        # 3. Handle Ambiguity (Hybrid Mode)
        # We still perform a search even if ambiguous to show preliminary results
        if analysis.get('status') == 'ambiguous' and not results:
            return {
                "type": "clarification",
                "question": analysis.get('clarification_question', "Could you provide more details about the part or application?"),
                "matches": []
            }
            
        # 4. Return Results
        return {
            "type": "clarification" if analysis.get('status') == 'ambiguous' else "results",
            "question": analysis.get('clarification_question') if analysis.get('status') == 'ambiguous' else None,
            "matches": results,
            "alternatives": [] # Placeholder for future logic
        }
