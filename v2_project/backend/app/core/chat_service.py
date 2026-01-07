from typing import List, Dict, Optional, Any
import httpx
from pydantic import BaseModel
import os

from app.core.pb_client import pb_client

class MessageCreate(BaseModel):
    inquiry_id: str
    sender_id: str  # User ID of the sender
    sender_role: str  # 'buyer' or 'vendor'
    content: str

class ChatService:
    def __init__(self):
        self.pb_url = os.getenv("PB_URL", "http://pocketbase:8090")
        self.collection = "messages"

    async def send_message(self, message: MessageCreate) -> Dict:
        """Send a new message in a chat thread."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "inquiry_id": message.inquiry_id,
                    "sender_id": message.sender_id,
                    "sender_role": message.sender_role,
                    "content": message.content,
                    "read": False
                }

                headers = await pb_client.get_headers()

                response = await client.post(
                    f"{self.pb_url}/api/collections/{self.collection}/records",
                    json=payload,
                    headers=headers,
                    timeout=5.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error sending message: {e}")
                raise e

    async def get_messages(self, inquiry_id: str) -> List[Dict]:
        """Get message history for an inquiry."""
        async with httpx.AsyncClient() as client:
            try:
                headers = await pb_client.get_headers()
                response = await client.get(
                    f"{self.pb_url}/api/collections/{self.collection}/records?filter=(inquiry_id='{inquiry_id}')&sort=created",
                    headers=headers,
                    timeout=5.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("items", [])
            except Exception as e:
                print(f"Error fetching messages: {e}")
                return []
class ConversationMemory:
    def __init__(self):
        self.pb_url = os.getenv("PB_URL", "http://pocketbase:8090")
        self.collection = "conversations"

    async def save_interaction(self, user_id: str, new_message: Dict, summary: str = "") -> Dict:
        """Appends a new interaction to the AI conversation history."""
        async with httpx.AsyncClient() as client:
            try:
                headers = await pb_client.get_headers()
                # 1. Get existing
                filter_query = f"user_id='{user_id}'"
                resp = await client.get(
                    f"{self.pb_url}/api/collections/{self.collection}/records?filter={filter_query}",
                    headers=headers
                )
                data = resp.json()
                
                messages = []
                record_id = None
                if data.get("items"):
                    record_id = data["items"][0]["id"]
                    messages = data["items"][0].get("messages", [])
                
                # 2. Append
                messages.append(new_message)
                
                payload = {
                    "user_id": user_id,
                    "messages": messages,
                    "summary": summary
                }

                if record_id:
                    response = await client.patch(
                        f"{self.pb_url}/api/collections/{self.collection}/records/{record_id}",
                        json=payload,
                        headers=headers
                    )
                else:
                    response = await client.post(
                        f"{self.pb_url}/api/collections/{self.collection}/records",
                        json=payload,
                        headers=headers
                    )
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error saving AI memory: {e}")
                raise e

    async def get_history(self, user_id: str) -> List[Dict]:
        """Fetch AI conversation history."""
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
                return data["items"][0].get("messages", []) if data.get("items") else []
            except Exception as e:
                print(f"Error fetching AI history: {e}")
                return []

memory_service = ConversationMemory()
