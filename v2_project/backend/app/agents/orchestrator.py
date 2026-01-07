from typing import Dict, Any, List
import json
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

class Orchestrator:

    async def route_request(self, user_input: str) -> Dict[str, Any]:
        """Determines which agent should handle the request or if a direct reply is needed."""
        # Detect Intent using LLM with structured output
        response = await self.llm.ainvoke([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"User Query: {user_input}")
        ])
        
        try:
            # Clean up the response to ensure valid JSON
            content = response.content.strip()
            print(f"DEBUG: Raw LLM Output: [{content}]")
            
            # More robust JSON extraction
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Final attempt to find JSON if there's outside text
            if not (content.startswith("{") and content.endswith("}")):
                start = content.find("{")
                end = content.rfind("}") + 1
                if start != -1 and end != 0:
                    content = content[start:end]

            return json.loads(content)
        except Exception as e:
            # Fallback for parsing errors
            print(f"Orchestrator Error: {e} | Content: {content}")
            return {"action": "chat", "response": "Sorry, I encountered an error processing your request.", "language": "en"}

    def __init__(self):
        self.system_prompt = """
        You are the 'Alsakr AI Supervisor' (مدير الذكاء الاصطناعي للصقر).
        
        **Your Goal**: 
        1. Detect the user's language (Arabic 'ar' or English 'en').
        2. Analyze the user's intent.
        3. Route to a specialist agent OR reply directly.

        **Available Agents**:
        - 'VisualMatch': If user has an image or wants to identify a part (e.g., "What is this part?").
        - 'MultiVendor': Finding suppliers, prices, availability (e.g., "Find me a Siemens motor").
        - 'QuoteCompare': Analyzing or comparing quotes.
        - 'InventoryVoice': Warehouse stock checks.
        - 'TechDoc': Manuals, datasheets, specs.
        - 'Compliance': HS codes, customs regulations.
        - 'Troubleshoot': Machine errors, fixes, maintenance.
        
        **Output Format (JSON ONLY)**:
        
        CASE 1: Routing Needed
        {
            "action": "route",
            "agent": "MultiVendor",
            "reason": "User is looking for suppliers",
            "language": "en"
        }

        CASE 2: Direct Reply (Greetings, General Questions, Clarifications)
        {
            "action": "chat",
            "response": "Hello! How can I help you find industrial parts today?",
            "language": "en"
        }
        
        CASE 3: Direct Reply (Arabic)
        {
            "action": "chat",
            "response": "أهلاً بك! كيف يمكنني مساعدتك في مجال قطع الغيار الصناعية؟",
            "language": "ar"
        }
        """
        
        self.llm = ChatOllama(model="llama3.2", base_url="http://ollama:11434")

# Main Entry Point for the Swarm
class AgentManager:
    def __init__(self):
        self.router = Orchestrator()
        # Initialize all agents
        from .vision_agent import VisualMatchAgent
        from .multi_vendor import MultiVendorAgent
        from .quote_compare import QuoteCompareAgent
        from .knowledge_layer import InventoryVoiceAgent, TechDocAgent
        from .industry_logic_layer import ComplianceGuideAgent, LocalSourcerAgent, AutoReplenishAgent, TroubleshootAgent
        from .management_layer import SupplierHubAgent

        self.agents = {
            "VisualMatch": VisualMatchAgent(),
            "MultiVendor": MultiVendorAgent(),
            "QuoteCompare": QuoteCompareAgent(),
            "InventoryVoice": InventoryVoiceAgent(),
            "TechDoc": TechDocAgent(),
            "Compliance": ComplianceGuideAgent(),
            "Service": LocalSourcerAgent(),  # Agent 7: Local Services
            "Troubleshoot": TroubleshootAgent(), # Agent 9: Troubleshooter
            "Profile": SupplierHubAgent(),       # Agent 10: Profile Manager
        }

    async def handle_request(self, user_input: str, context: Dict = {}):
        routing_decision = await self.router.route_request(user_input)
        
        if routing_decision.get("action") == "route":
            target_agent = routing_decision.get("agent")
            if target_agent in self.agents:
                # Pass context and language info to the sub-agent
                context["language"] = routing_decision.get("language", "en")
                return await self.agents[target_agent].run(user_input, context)
            else:
                return f"Error: Specialist agent '{target_agent}' not found."
        
        elif routing_decision.get("action") == "chat":
            return routing_decision.get("response")
        
        else:
            return "I'm having trouble understanding. Could you please rephrase?"
