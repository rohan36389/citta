import logging
from typing import List, Dict
from backend.conversation.interfaces import IMemoryStore

logger = logging.getLogger(__name__)

class MemoryStore(IMemoryStore):
    """
    Manages session-level memory stores and persistence of message transcripts.
    """
    def __init__(self):
        self._stores: Dict[str, List[Dict[str, str]]] = {}

    def load_memory(self, session_id: str) -> List[Dict[str, str]]:
        """
        Loads message history for a given session.
        """
        if session_id not in self._stores:
            self._stores[session_id] = []
        return self._stores[session_id]

    def save_memory(self, session_id: str, messages: List[Dict[str, str]]) -> None:
        """
        Saves updated message history for a given session.
        """
        self._stores[session_id] = list(messages)
        logger.info(f"Saved memory state for session {session_id} (count: {len(messages)})")

    def clear_memory(self, session_id: str) -> None:
        """
        Clears message history and memory manager state for a given session.
        """
        if session_id in self._stores:
            del self._stores[session_id]
        from backend.conversation.memory_engine import _managers
        if session_id in _managers:
            del _managers[session_id]
        logger.info(f"Cleared memory store and manager state for session {session_id}")

def get_memory_store() -> IMemoryStore:
    return MemoryStore()
