import logging
from typing import List, Dict
from backend.conversation.models import ConversationContext, ResponseStrategy, DraftResponse
from backend.conversation.interfaces import IResponseEngine

logger = logging.getLogger(__name__)

class ResponseEngine(IResponseEngine):
    """
    Drafts natural conversation responses and formats dynamic suggestion chips.
    """
    def __init__(self):
        pass

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

    def generate_suggestions(self, draft: DraftResponse, context: ConversationContext) -> List[Dict[str, str]]:
        """
        Creates suggestion chips tailored to conversation context and stage.
        """
        stage = context.current_stage
        
        if stage == "Greeting":
            return [
                {"label": "Explore Solutions", "action": "explore_solutions"},
                {"label": "What is CittaAI?", "action": "learn_about_citta"}
            ]
        elif stage == "Discovery":
            return [
                {"label": "Schedule Technical Demo", "action": "request_demo"},
                {"label": "Obtain Integration Specs", "action": "get_specs"}
            ]
            
        return [
            {"label": "Contact Sales Team", "action": "contact_sales"},
            {"label": "Go Back to Start", "action": "go_home"}
        ]

def get_response_engine() -> IResponseEngine:
    return ResponseEngine()
