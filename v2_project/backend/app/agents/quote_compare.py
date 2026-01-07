import json
from typing import Dict, Any, List
from .base import BaseAgent

class QuoteCompareAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
        You are the 'QuoteCompare & Negotiator' for Al Sakr Online.
        Your goal is to analyze quotes and get the best deal for the buyer.
        
        LOGIC:
        1. CALCULATE LANDED COST: Price + VAT (15%) + Platform Margin (5-10%).
        2. PROJECT BUNDLING: If multiple items belong to one project, prioritize vendors who can fulfill the whole bundle.
        3. AUTO-NEGOTIATION: If the price is > market average, trigger a 'Haggle' response.
        
        RESPONSE FORMAT (JSON):
        {
            "best_quote": {"vendor": "...", "total_cost": 0, "delivery": "..."},
            "comparison_table": [],
            "negotiation_status": "Accepted/Haggling",
            "counter_offer": 0.0,
            "margin_applied": "10%"
        }
        """
        super().__init__(name="QuoteCompare", system_prompt=system_prompt)

    async def analyze_quotes(self, quotes: List[Dict], is_project: bool = False) -> Dict[str, Any]:
        """
        Analyzes incoming quotes from vendors.
        """
        context = {
            "quotes": quotes,
            "is_project": is_project,
            "vat_rate": 0.15
        }
        
        prompt = f"Analyze these quotes: {json.dumps(quotes)}. Is this a Project? {is_project}."
        
        response_text = await self.run(prompt, context=context)
        
        try:
            return json.loads(response_text)
        except:
            return {"raw_response": response_text}

    def calculate_landed_cost(self, base_price: float, shipping: float = 0) -> float:
        """Utility for agents to use."""
        vat = base_price * 0.15
        margin = base_price * 0.05
        return base_price + vat + margin + shipping
