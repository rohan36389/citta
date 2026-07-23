import logging
from typing import Dict, Any, Optional
from backend.conversation.models import PersonaProfile, ConversationContext
from backend.conversation.interfaces import IPersonaEngine
from backend.conversation.persona_engine import get_customer_persona_engine

logger = logging.getLogger(__name__)

class PersonaEngine(IPersonaEngine):
    """
    Adapter wrapping CustomerPersonaEngine to fulfill the IPersonaEngine interface.
    """
    def __init__(self):
        self.engine = get_customer_persona_engine()

    def process(self, query: str, context: Optional[ConversationContext] = None) -> PersonaProfile:
        return self.engine.process(query, context)

def get_persona_engine() -> IPromptEngine if False else PersonaEngine:
    return PersonaEngine()
