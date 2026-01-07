import json
from typing import Dict, Any, List
from .base import BaseAgent
from ..core.es_client import es_client

# AGENT 10: SupplierHub & Profile Manager
class SupplierHubAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
        You are the 'SupplierHub & Profile Manager'.
        Your role is to manage Buyer/Vendor registration and verification.
        
        TASKS:
        1. REGISTRATION: Ensure all fields (CR, Sector, Location) are present.
        2. VERIFICATION: Trigger Email/OTP logic.
        3. LINE CARD PARSING: Extract brands from vendor-uploaded company profiles.
        4. CRM SYNC: Ensure data is mirrored in PocketBase.
        
        OUTPUT FORMAT (JSON):
        {
            "registration_status": "Success/Incomplete",
            "verification_next_step": "Email/OTP",
            "extracted_brands": [],
            "pocketbase_id": "...",
            "sync_success": true
        }
        """
        super().__init__(name="SupplierHub", system_prompt=system_prompt)

    async def register_user(self, user_data: Dict) -> Dict[str, Any]:
        """Handles the dual-write registration logic."""
        # 1. Logic to write to PocketBase (CRM)
        # 2. Logic to write to Elasticsearch (Search)
        prompt = f"Register this user: {json.dumps(user_data)}"
        response_text = await self.run(prompt)
        try:
            return json.loads(response_text)
        except:
            return {"raw_response": response_text}

    async def parse_line_card(self, pdf_text: str) -> List[str]:
        """Extracts brands from technical text."""
        prompt = f"Extract all industrial brands (e.g. SKF, Siemens) from this text: {pdf_text}"
        response_text = await self.run(prompt)
        # Process and return list
        return []

# AGENT 9: SafetyGuard
class SafetyGuardAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
        You are the 'SafetyGuard' (EHS Specialist).
        Your goal is to ensure all parts and services meet safety protocols.
        
        LOGIC:
        1. Safety Data Sheets (SDS): Check if a part requires special handling.
        2. Compliance: Ensure the vendor has valid safety certificates.
        
        OUTPUT FORMAT (JSON):
        {
            "is_safe": true/false,
            "safety_protocols": ["Wear Gloves", "High Voltage Warning"],
            "missing_certifications": []
        }
        """
        super().__init__(name="SafetyGuard", system_prompt=system_prompt)
