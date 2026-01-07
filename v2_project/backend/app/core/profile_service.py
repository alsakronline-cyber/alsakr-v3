from typing import List, Dict, Optional, Any
import httpx
from pydantic import BaseModel
import os
from .pb_client import pb_client

class VendorProfileCreate(BaseModel):
    user_id: str
    brands: List[str] = []
    categories: List[str] = []
    cr_number: Optional[str] = None
    sector: Optional[str] = None
    location: Optional[str] = None

class ProfileService:
    def __init__(self):
        self.pb_url = os.getenv("PB_URL", "http://pocketbase:8090")
        self.collection = "vendor_profiles"

    async def create_or_update_profile(self, profile: VendorProfileCreate) -> Dict:
        """Create or update a vendor profile in PocketBase."""
        async with httpx.AsyncClient() as client:
            try:
                # Check if profile already exists for this user
                headers = await pb_client.get_headers()
                filter_query = f"user_id='{profile.user_id}'"
                search_resp = await client.get(
                    f"{self.pb_url}/api/collections/{self.collection}/records?filter={filter_query}",
                    headers=headers
                )
                search_data = search_resp.json()
                
                payload = {
                    "user_id": profile.user_id,
                    "brands": profile.brands,
                    "categories": profile.categories,
                    "cr_number": profile.cr_number,
                    "sector": profile.sector,
                    "location": profile.location,
                    "verification_status": "pending"
                }

                if search_data.get("items"):
                    # Update
                    record_id = search_data["items"][0]["id"]
                    response = await client.patch(
                        f"{self.pb_url}/api/collections/{self.collection}/records/{record_id}",
                        json=payload,
                        headers=headers
                    )
                else:
                    # Create
                    response = await client.post(
                        f"{self.pb_url}/api/collections/{self.collection}/records",
                        json=payload,
                        headers=headers
                    )
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error managing profile: {e}")
                raise e

    async def get_profile(self, user_id: str) -> Optional[Dict]:
        """Fetch vendor profile by user ID."""
        async with httpx.AsyncClient() as client:
            try:
                headers = await pb_client.get_headers()
                filter_query = f"user_id='{user_id}'"
                response = await client.get(
                    f"{self.pb_url}/api/collections/{self.collection}/records?filter={filter_query}",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                return data["items"][0] if data.get("items") else None
            except Exception as e:
                print(f"Error fetching profile: {e}")
                return None

profile_service = ProfileService()
