import logging
from typing import Dict, Any
from backend.conversation.models import ConversationContext
from backend.conversation.interfaces import IContextEngine, IMemoryStore
from backend.conversation.config import STAGE_TRANSITIONS

logger = logging.getLogger(__name__)

class ContextEngine(IContextEngine):
    """
    Manages session-level context, stage transition state machines,
    and history integration from the memory store.
    """
    def __init__(self, memory_store: IMemoryStore):
        self.memory_store = memory_store
        self._contexts: Dict[str, ConversationContext] = {}

    def get_or_create_context(self, session_id: str) -> ConversationContext:
        """
        Retrieves or creates context for a session, syncing historical messages from the MemoryStore.
        """
        if session_id not in self._contexts:
            history = self.memory_store.load_memory(session_id)
            self._contexts[session_id] = ConversationContext(
                session_id=session_id,
                history=history,
                turn_count=len(history) // 2
            )
        return self._contexts[session_id]

    def update_context(self, context: ConversationContext, updates: Dict[str, Any]) -> None:
        """
        Applies updates directly to the conversation context.
        """
        context.turn_count += 1
        for k, v in updates.items():
            if hasattr(context, k):
                setattr(context, k, v)
        
        # Keep MemoryStore in sync
        self.memory_store.save_memory(context.session_id, context.history)

    def transition_stage(self, context: ConversationContext, next_stage: str) -> bool:
        """
        Transitions conversation stages using the transition matrix.
        """
        curr = context.current_stage
        allowed = STAGE_TRANSITIONS.get(curr, [])
        if next_stage in allowed or next_stage == curr:
            logger.info(f"ContextEngine: Transitioning session {context.session_id} from {curr} to {next_stage}")
            context.current_stage = next_stage
            return True
        logger.warning(f"ContextEngine: Invalid transition request from {curr} to {next_stage} for session {context.session_id}")
        return False

def get_context_engine(memory_store: IMemoryStore) -> IContextEngine:
    return ContextEngine(memory_store)
