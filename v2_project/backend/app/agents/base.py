from typing import Any, Dict, List, Optional, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

# 1. Define the Global State for all Agents
class AgentState(TypedDict):
    messages: List[BaseMessage]
    context: Dict[str, Any]  # Shared memory (e.g. user_id, current_project)
    next_step: str

# 2. The Base Agent Class
class BaseAgent:
    def __init__(self, 
                 name: str, 
                 model_name: str = "llama3.2", 
                 system_prompt: str = ""):
        self.name = name
        self.system_prompt = system_prompt
        
        # Initialize Local LLM (Ollama)
        self.llm = ChatOllama(
            model=model_name,
            base_url="http://ollama:11434",
            temperature=0.2  # Low temp for factual accuracy
        )
        
        # Initialize Graph
        self.workflow = StateGraph(AgentState)
        self._build_graph()

    def _build_graph(self):
        """Builds the core LangGraph workflow."""
        self.workflow.add_node("agent", self._call_model)
        self.workflow.set_entry_point("agent")
        self.workflow.add_edge("agent", END)
        self.app = self.workflow.compile()

    async def _call_model(self, state: AgentState) -> Dict:
        """Core logic to call the LLM with System Prompt + History."""
        messages = state["messages"]
        
        # Prepend System Prompt if not present
        if not isinstance(messages[0], SystemMessage):
            messages.insert(0, SystemMessage(content=self.system_prompt))
            
        response = await self.llm.ainvoke(messages)
        return {"messages": [response]}

    async def run(self, user_input: str, context: Dict = {}) -> str:
        """Execution Entry Point."""
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "context": context,
            "next_step": ""
        }
        
        result = await self.app.ainvoke(initial_state)
        return result["messages"][-1].content

# Example Usage:
# agent = BaseAgent("VisualMatch", system_prompt="You are an expert in industrial parts...")
# response = await agent.run("Identify this bearing")
