from typing import List, Dict, Optional, Any
import httpx
from pydantic import BaseModel
import os
import asyncio
from app.core.pb_client import pb_client
from app.core.email_service import email_service

# Pydantic schema for creating an inquiry
class InquiryCreate(BaseModel):
    buyer_id: str
    products: List[Dict[str, Any]] # List of product details (part_number, name, etc.)
    message: str

class InquiryService:
    def __init__(self):
        # Fallback to localhost if env var not set, for local dev
        self.pb_url = os.getenv("PB_URL", "http://pocketbase:8090") 
        self.collection = "inquiries"

    async def create_inquiry(self, inquiry: InquiryCreate) -> Dict:
        """Creates a new inquiry record in PocketBase."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "buyer_id": inquiry.buyer_id,
                    "products": inquiry.products, # PocketBase handles JSON fields
                    "message": inquiry.message,
                    "status": "pending"
                }

                # Get auth headers
                headers = await pb_client.get_headers()
                
                response = await client.post(
                    f"{self.pb_url}/api/collections/{self.collection}/records",
                    json=payload,
                    headers=headers,
                    timeout=5.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Send Notification (Fire & Forget)
                asyncio.create_task(email_service.send_inquiry_notification(data))
                
                return data
            except Exception as e:
                print(f"Error creating inquiry: {e}")
                raise e

    async def get_vendor_inquiries(self) -> List[Dict]:
        """Fetches all inquiries for the vendor dashboard."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.pb_url}/api/collections/{self.collection}/records?sort=-created",
                    timeout=5.0
                )
                response.raise_for_status()
                data = response.json()
                items = data.get("items", [])
                
                # Mask Buyer Details for Privacy
                for item in items:
                    email = item.get("buyer_id", "")
                    if "@" in email:
                        local, domain = email.split("@")
                        masked_email = local[0] + "***" + local[-1] + "@" + domain
                        item["buyer_id"] = masked_email
                
                return items
            except Exception as e:
                print(f"Error fetching inquiries: {e}")
                return []

    async def get_buyer_inquiries(self, buyer_id: str) -> List[Dict]:
        """Fetches inquiries for a specific buyer."""
        async with httpx.AsyncClient() as client:
            try:
                # Filter by buyer_id
                filter_query = f"buyer_id='{buyer_id}'"
                response = await client.get(
                    f"{self.pb_url}/api/collections/{self.collection}/records?filter={filter_query}&sort=-created",
                    timeout=5.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("items", [])
            except Exception as e:
                print(f"Error fetching buyer inquiries: {e}")
                return []

    async def get_inquiry(self, inquiry_id: str) -> Optional[Dict]:
        """Fetches a single inquiry by ID."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.pb_url}/api/collections/{self.collection}/records/{inquiry_id}",
                    timeout=5.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching inquiry {inquiry_id}: {e}")
                return None
