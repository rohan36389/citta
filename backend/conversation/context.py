import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    session_id: str
    last_entity: Optional[str] = None
    last_registry: Optional[str] = None
    last_section: Optional[str] = None
    last_category: Optional[str] = None
    last_product: Optional[str] = None
    last_solution: Optional[str] = None
    last_service: Optional[str] = None
    last_person: Optional[str] = None
    last_case_study: Optional[str] = None
    last_capability: Optional[str] = None
    turn_count: int = 0

class ConversationContextManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConversationContextManager, cls).__new__(cls)
            cls._instance._contexts: Dict[str, ConversationContext] = {}
        return cls._instance

    def get_context(self, session_id: str) -> ConversationContext:
        if session_id not in self._contexts:
            self._contexts[session_id] = ConversationContext(session_id=session_id)
        return self._contexts[session_id]

    def update_context(
        self,
        session_id: str,
        entity_id: Optional[str] = None,
        registry: Optional[str] = None,
        section: Optional[str] = None,
        category: Optional[str] = None,
        product: Optional[str] = None,
        solution: Optional[str] = None,
        service: Optional[str] = None,
        person: Optional[str] = None,
        case_study: Optional[str] = None,
        capability: Optional[str] = None
    ):
        ctx = self.get_context(session_id)
        ctx.turn_count += 1
        
        if entity_id:
            ctx.last_entity = entity_id
        if registry:
            ctx.last_registry = registry
        if section:
            ctx.last_section = section
        if category:
            ctx.last_category = category
        if product:
            ctx.last_product = product
        if solution:
            ctx.last_solution = solution
        if service:
            ctx.last_service = service
        if person:
            ctx.last_person = person
        if case_study:
            ctx.last_case_study = case_study
        if capability:
            ctx.last_capability = capability

    def clear_context(self, session_id: str):
        if session_id in self._contexts:
            del self._contexts[session_id]

def get_context_manager() -> ConversationContextManager:
    return ConversationContextManager()
