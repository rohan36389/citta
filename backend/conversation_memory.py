import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ConversationState:
    session_id: str
    tenant_id: str = "cittaai"
    active_entity: Optional[str] = None
    active_topics: List[str] = field(default_factory=list)
    active_intent: Optional[str] = None
    turn_count: int = 0
    history: List[Dict[str, str]] = field(default_factory=list)

class ConversationMemory:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConversationMemory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.sessions: Dict[str, ConversationState] = {}

    def get_state(self, session_id: str, tenant_id: str = "cittaai") -> ConversationState:
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationState(session_id=session_id, tenant_id=tenant_id)
        return self.sessions[session_id]

    def update_state(
        self,
        session_id: str,
        entity_id: Optional[str] = None,
        topics: Optional[List[str]] = None,
        intent: Optional[str] = None,
        user_message: Optional[str] = None,
        assistant_response: Optional[str] = None
    ):
        state = self.get_state(session_id)
        state.turn_count += 1
        
        if entity_id:
            state.active_entity = entity_id
        if topics:
            state.active_topics = topics
        if intent:
            state.active_intent = intent
            
        if user_message:
            state.history.append({"role": "user", "content": user_message})
        if assistant_response:
            state.history.append({"role": "assistant", "content": assistant_response})
            
        if len(state.history) > 10:
            state.history = state.history[-10:]

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session memory for {session_id}")

def get_conversation_memory() -> ConversationMemory:
    return ConversationMemory()
