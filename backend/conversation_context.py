import re
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

PRONOUN_TRIGGERS = {"it", "its", "they", "them", "their", "this", "that", "company", "the company", "organization"}

@dataclass
class SessionState:
    session_id: str
    active_company: str = "CittaAI"
    active_product: Optional[str] = None
    active_solution: Optional[str] = None
    active_service: Optional[str] = None
    active_industry: Optional[str] = None
    active_person: Optional[str] = None
    active_role: Optional[str] = None
    previous_intent: Optional[str] = None
    turn_count: int = 0
    history: List[Dict[str, str]] = field(default_factory=list)
    preferred_industry: Optional[str] = None

class ConversationContextManager:
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}

    def get_or_create(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id=session_id)
        return self.sessions[session_id]

    def update_context(
        self,
        session_id: str,
        intent: Optional[str] = None,
        company: Optional[str] = None,
        product: Optional[str] = None,
        solution: Optional[str] = None,
        service: Optional[str] = None,
        industry: Optional[str] = None,
        person: Optional[str] = None,
        role: Optional[str] = None
    ):
        state = self.get_or_create(session_id)
        state.turn_count += 1
        if intent:
            state.previous_intent = intent
        if company:
            state.active_company = company
        if product:
            state.active_product = product
        if solution:
            state.active_solution = solution
        if service:
            state.active_service = service
        if industry:
            state.active_industry = industry
            state.preferred_industry = industry
        if person:
            state.active_person = person
        if role:
            state.active_role = role

    def resolve_follow_up(self, session_id: str, query: str) -> Dict[str, Any]:
        state = self.get_or_create(session_id)
        q_tokens = set(re.findall(r"\b[a-z0-9_-]+\b", query.lower()))

        is_follow_up = bool(q_tokens.intersection(PRONOUN_TRIGGERS)) or len(q_tokens) <= 4

        # In-session personalization hints
        personalized_solution = None
        if state.preferred_industry:
            ind_lower = state.preferred_industry.lower()
            if "health" in ind_lower or "pharma" in ind_lower or "medical" in ind_lower:
                personalized_solution = "Pharma & Healthcare OS"
            elif "retail" in ind_lower or "ecommerce" in ind_lower:
                personalized_solution = "E-Commerce OS"
            elif "education" in ind_lower or "school" in ind_lower:
                personalized_solution = "Education OS"
            elif "real estate" in ind_lower:
                personalized_solution = "Real Estate OS"

        return {
            "is_follow_up": is_follow_up,
            "target_company": state.active_company,
            "target_person": state.active_person,
            "target_role": state.active_role,
            "preferred_industry": state.preferred_industry,
            "active_product": state.active_product,
            "active_solution": state.active_solution,
            "active_service": state.active_service,
            "personalized_solution_recommendation": personalized_solution
        }

_context_manager_instance = None

def get_context_manager() -> ConversationContextManager:
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ConversationContextManager()
    return _context_manager_instance

