import logging
from typing import List, Dict, Any
from backend.conversation.models import ConversationContext, ResponseStrategy, DraftResponse
from backend.conversation.interfaces import IResponseEngine

logger = logging.getLogger(__name__)

from backend.conversation.suggestion_engine import get_suggestion_engine

class ResponseEngine(IResponseEngine):
    """
    Drafts natural conversation responses and formats dynamic suggestion chips.
    """
    def __init__(self):
        self.suggestion_engine = get_suggestion_engine()

    def compose_draft(
        self,
        system_prompt: str,
        user_prompt: str,
        strategy: ResponseStrategy,
        context: ConversationContext
    ) -> DraftResponse:
        """
        Formats final response draft blending retrieved facts and strategy context.
        """
        # Formulate pre-sales consultant styled stubs
        text = "Hello! I am your CittaAI pre-sales consultant. "
        
        if strategy.selected_strategy == "Objection":
            text += "We specialize in tailoring bespoke enterprise integrations to your ROI requirements. Rather than quoting standard fees, we recommend a commercial modeling call."
        elif strategy.selected_strategy == "Educational":
            text += "CittaAI features unified REST API connections, modular data ingestion schemas, and full compliance guidelines."
        else:
            text += "CittaAI is an AI-powered quality, compliance and release intelligence platform. Let me know what specific business goals we can help you solve today."
            
        return DraftResponse(
            text=text,
            suggestions=[],
            citations=["KnowledgeRegistry:CittaAI_Overview"]
        )

    def generate_suggestions(self, draft: DraftResponse, context: ConversationContext) -> List[Dict[str, Any]]:
        """
        Creates dynamic suggestion chips via SuggestionEngine.
        """
        persona_profile = context.variables.get("persona_profile")
        intent = context.variables.get("intent")
        
        sug_res = self.suggestion_engine.generate(intent, persona_profile, context)
        
        return [
            {
                "label": s.label,
                "action": s.action,
                "confidence": s.confidence,
                "reasoning": s.reasoning
            }
            for s in sug_res.suggestions
        ]

def get_response_engine() -> IResponseEngine:
    return ResponseEngine()
