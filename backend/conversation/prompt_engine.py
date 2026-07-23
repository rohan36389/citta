import logging
from backend.conversation.models import ConversationContext, ResponseStrategy
from backend.conversation.interfaces import IPromptEngine
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PromptEngine(IPromptEngine):
    """
    Centralizes all prompt template construction, context injection,
    and formatting rules for LLM calls.
    """
    def __init__(self):
        pass

    def build_system_prompt(self, context: ConversationContext, strategy: ResponseStrategy) -> str:
        """
        Creates a system prompt that injects persona guidelines, strategy plans, 
        current stage details, and audience-level adaptiveness.
        """
        stage = context.current_stage
        audience = strategy.audience_level
        strat = strategy.selected_strategy
        length = strategy.response_length
        
        prompt = (
            "You are CittaAI's premier pre-sales consultant. Your objective is not just to answer questions, "
            "but to act as an expert business partner who guides potential clients towards discovering CittaAI's value.\n\n"
            f"Current Conversation Stage: {stage}\n"
            f"Audience Executive Profile: {audience}\n"
            f"Response Strategy: {strat}\n"
            f"Desired Output Density: {length}\n\n"
            "Pre-sales Guidelines:\n"
            "- Speak naturally, dynamically, and conversationally. Avoid dry FAQ listings.\n"
            "- Target the business needs of the client, asking consultative qualifying questions when natural.\n"
            "- Adapt language details to the executive profile (CEO = business value/ROI, Developer = API/architecture).\n"
            "- Follow all business rules, never speculate on custom pricing, and direct technical/custom requests to scheduling a sales demo.\n"
        )
        if strategy.checklist:
            prompt += "\nSpecific Points to Address:\n" + "\n".join([f"- {item}" for item in strategy.checklist])
            
        return prompt

    def build_user_prompt(self, query: str, retrieved_knowledge: Dict[str, Any]) -> str:
        """
        Builds the user prompt combining the current query and retrieved registry/RAG contexts.
        """
        context_str = ""
        if retrieved_knowledge:
            context_str = "\n".join([f"Source [{k}]: {v}" for k, v in retrieved_knowledge.items()])
            
        return (
            f"Retrieved Platform Reference Grounding:\n{context_str}\n\n"
            f"User Inquiry: {query}\n\n"
            "Generate your consultative response below:"
        )

def get_prompt_engine() -> IPromptEngine:
    return PromptEngine()
