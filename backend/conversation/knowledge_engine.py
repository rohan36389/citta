import logging
from typing import Dict, Any, List
from backend.conversation.models import ConversationContext, IntentAnalysis, ToolSelection
from backend.conversation.interfaces import IKnowledgeEngine

logger = logging.getLogger(__name__)

class KnowledgeEngine(IKnowledgeEngine):
    """
    Decides on tooling requirements (Registry, RAG, CRM, External API),
    orchestrates evidence gathering, and marks knowledge gaps.
    """
    def __init__(self):
        pass

    def select_tools(self, intent: IntentAnalysis, context: ConversationContext) -> ToolSelection:
        """
        Determines target components/APIs to trigger based on intent analysis.
        """
        tools: List[str] = []
        queries: Dict[str, str] = {}
        
        # Determine tools needed
        if intent.primary_intent in ["comparison", "general_inquiry"]:
            tools.append("KnowledgeRegistry")
        if intent.primary_intent in ["pricing_inquiry", "technical_validation"]:
            tools.append("KnowledgeRegistry")
            tools.append("RAGService")
        if intent.primary_intent == "leadership_lookup":
            tools.append("KnowledgeRegistry")
            
        return ToolSelection(selected_tools=tools, queries=queries)

    def orchestrate_knowledge(self, tool_sel: ToolSelection, query: str) -> Dict[str, Any]:
        """
        Queries selected tools, rankings/merges sources, and aggregates data.
        """
        results: Dict[str, Any] = {}
        
        # Stubs for tool execution outputs
        for tool in tool_sel.selected_tools:
            if tool == "KnowledgeRegistry":
                results["registry_data"] = f"Canonical metadata matching for '{query}'"
            elif tool == "RAGService":
                results["rag_data"] = f"Semantic retrieval chunks matching '{query}'"
                
        return results

    def detect_knowledge_gap(self, retrieved_data: Dict[str, Any], query: str) -> bool:
        """
        Checks if gathered evidence contains sufficient info or is empty.
        """
        # If no key contains data, it is a knowledge gap
        if not retrieved_data:
            return True
        
        # Check if dummy stubs show no matches found
        for v in retrieved_data.values():
            if "not_found" in str(v).lower() or not v:
                return True
                
        return False

def get_knowledge_engine() -> IKnowledgeEngine:
    return KnowledgeEngine()
