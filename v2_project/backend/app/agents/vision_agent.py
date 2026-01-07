import os
import json
import base64
import httpx
import asyncio
import logging
from typing import Dict, Any, List
from .base import BaseAgent
from ..core.config import settings
from ..core.search_service import SearchService

logger = logging.getLogger(__name__)

class VisualMatchAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
        You are the 'VisualMatch' agent.
        Identify industrial parts from images.
        """
        super().__init__(name="VisualMatch", system_prompt=system_prompt)
        self.ollama_url = f"{settings.OLLAMA_HOST}/api/generate"
        self.vision_model = "llava" 
        self.search_service = SearchService()

    async def identify_and_match(self, image_data: str, mode: str = "path") -> Dict[str, Any]:
        """
        Identify part from image using Ollama Vision (Async)
        """
        
        b64_image = ""
        if mode == "path":
            try:
                # Read file in thread to not block loop
                def read_file():
                    with open(image_data, "rb") as f:
                        return base64.b64encode(f.read()).decode("utf-8")
                b64_image = await asyncio.to_thread(read_file)
            except Exception as e:
                return {"error": f"Failed to read image: {str(e)}"}
        else:
            b64_image = image_data

        prompt = "Identify this industrial part. Return JSON with: brand, series, part_number (if visible), and description."

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.ollama_url,
                    json={
                        "model": self.vision_model,
                        "prompt": prompt,
                        "images": [b64_image],
                        "stream": False,
                        "format": "json"
                    },
                    timeout=60
                )
            
            if response.status_code != 200:
                logger.error(f"Ollama Vision Error: {response.text}")
                return {"error": f"Ollama Error: {response.text}"}
                
            result = response.json().get("response", "{}")
            vision_data = json.loads(result)
            
            # Enhancer: Cross-reference with ES if brand/part detected
            matches = []
            if vision_data.get("part_number"):
                # Await the now-async search methods
                matches = await self.search_service.text_search(vision_data["part_number"], size=3)
                
                if not matches and vision_data.get("description"):
                    matches = await self.search_service.semantic_search(vision_data["description"], limit=3)

            return {
                "identification": vision_data,
                "matches": matches,
                "raw_analysis": result
            }

        except Exception as e:
            logger.error(f"Vision processing failed: {e}")
            return {"error": f"Vision processing failed: {str(e)}"}
