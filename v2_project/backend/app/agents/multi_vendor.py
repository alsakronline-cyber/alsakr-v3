import json
import os
from typing import Dict, Any, List
from .base import BaseAgent, AgentState
from ..core.es_client import es_client
from langchain_core.messages import HumanMessage

class MultiVendorAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
        You are the 'MultiVendor Aggregator' for Al Sakr Online.
        Your goal is to find the best local suppliers for a part.
        """
        super().__init__(name="MultiVendor", system_prompt=system_prompt)

    async def run(self, user_input: str, context: Dict = {}) -> Any:
        """Override run to intercept specific commands."""
        
        # Intercept "Find suppliers" command
        if "Find suppliers for inquiry" in user_input:
            # Extract info (simple parsing)
            try:
                # Expected format: "Find suppliers for inquiry {id} which contains {qty}x {part_number}..."
                # We will just focus on the part number for the search
                import re
                qty_match = re.search(r"(\d+)x", user_input)
                part_match = re.search(r"x\s([A-Za-z0-9-]+)", user_input)
                
                qty = int(qty_match.group(1)) if qty_match else 1
                part_number = part_match.group(1) if part_match else "UNKNOWN"
                
                return await self.find_suppliers_dummy(part_number, qty)
            except Exception as e:
                return f"Error processing supplier search: {e}"
        
        # Default LLM behavior
        return await super().run(user_input, context)

    async def find_suppliers_dummy(self, part_number: str, quantity: int) -> Dict[str, Any]:
        """Simulate finding suppliers using dummy data (Async)."""
        
        # Load Dummy Data
        try:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "dummy_data.json")
            
            def read_json():
                with open(data_path, "r") as f:
                    return json.load(f)
            
            data = await asyncio.to_thread(read_json)
        except Exception as e:
            return {
                "response": "Error: Could not access supplier database (Dummy Data Missing).",
                "data": None
            }

        vendors = data.get("vendors", [])
        products = data.get("products", [])
        
        # Find Product Price Reference
        ref_product = next((p for p in products if p["part_number"] == part_number), None)
        base_price = ref_product["price"] if ref_product else 100.00
        product_name = ref_product["name"] if ref_product else part_number
        category = ref_product["category"] if ref_product else "Industrial Part"

        # Simulate 3 Vendor Options
        import random
        # deterministic seed for demo based on part number
        random.seed(sum(ord(c) for c in part_number))
        
        selected_vendors = random.sample(vendors, min(3, len(vendors)))
        
        options = []
        for v in selected_vendors:
            # Simulate variance
            price_variance = random.uniform(0.9, 1.2)
            lead_time = random.choice(["2 Days", "5 Days", "10 Days", "In Stock"])
            price = round(base_price * price_variance * quantity, 2)
            
            options.append({
                "vendor_id": v.get("email", "unknown"), # Use email as ID for now
                "vendor_name": v["company_name"],
                "rating": v["rating"],
                "total_price": price,
                "unit_price": round(price / quantity, 2),
                "currency": "USD",
                "lead_time": lead_time,
                "status": "Available" if lead_time == "In Stock" else "Backorder",
                "verified": True
            })

        # Find best option for summary
        best_opt = min(options, key=lambda x: x["total_price"])
        
        # Format Text Summary
        summary = f"I found **{len(options)} verified suppliers** for {quantity}x {product_name} ({part_number}).\n\n"
        summary += f"The best price is **${best_opt['total_price']}** from **{best_opt['vendor_name']}**.\n"
        summary += "Please review the comparison cards below to make your selection."

        return {
            "response": summary,
            "data": {
                "type": "vendor_comparison",
                "part_number": part_number,
                "product_name": product_name,
                "category": category,
                "quantity": quantity,
                "options": options
            }
        }
