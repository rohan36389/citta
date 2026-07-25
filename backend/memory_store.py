import os
import json
import time
import math
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

MEMORY_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MEMORY_DATA_FILE = os.path.join(MEMORY_DATA_DIR, "enterprise_memory.json")

class MemoryProvenance(BaseModel):
    source_type: str = "MANUAL_USER_INPUT"  # CONVERSATION, WORKFLOW, MANUAL_USER_INPUT, CRM, CALENDAR, SUPPORT_TICKET, ADMINISTRATOR
    source_id: Optional[str] = None
    created_at_iso: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context_query: Optional[str] = None

class MemoryVersionRecord(BaseModel):
    version: int
    content: Any
    updated_at_iso: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_by: str = "system"

class EnterpriseMemory(BaseModel):
    memory_id: str
    type: str  # USER, ORG, WORKFLOW, ACTION, PREFERENCE, CONVERSATION, REASONING
    owner_user_id: str = "user_default"
    organization_id: str = "org_default"
    visibility: str = "PRIVATE_USER"  # PRIVATE_USER, TEAM, ORGANIZATION, ADMIN_ONLY, GLOBAL
    
    content: Any
    entity_id: Optional[str] = None
    intent: Optional[str] = None
    workflow_id: Optional[str] = None
    
    initial_confidence: float = 1.0
    half_life_days: float = 180.0
    
    provenance: MemoryProvenance = Field(default_factory=MemoryProvenance)
    version_history: List[MemoryVersionRecord] = Field(default_factory=list)
    
    created_at_ms: float = Field(default_factory=lambda: round(time.time() * 1000, 2))
    updated_at_ms: float = Field(default_factory=lambda: round(time.time() * 1000, 2))
    expires_at_ms: Optional[float] = None
    
    is_archived: bool = False
    is_deleted: bool = False

    def get_decayed_confidence(self, current_time_ms: Optional[float] = None) -> float:
        """Calculates dynamic time-decayed confidence: C(t) = C_0 * (0.5)^(delta_days / half_life)."""
        if self.type == "PREFERENCE" or self.half_life_days <= 0:
            return round(self.initial_confidence, 2)

        now_ms = current_time_ms or (time.time() * 1000.0)
        elapsed_days = (now_ms - self.updated_at_ms) / (1000.0 * 60.0 * 60.0 * 24.0)
        if elapsed_days <= 0:
            return round(self.initial_confidence, 2)

        decayed = self.initial_confidence * math.pow(0.5, elapsed_days / self.half_life_days)
        return round(max(0.0, min(1.0, decayed)), 2)

class MemoryStore:
    def __init__(self):
        self.memories: Dict[str, EnterpriseMemory] = {}
        self._ensure_data_dir()
        self.load_from_disk()

    def _ensure_data_dir(self):
        try:
            os.makedirs(MEMORY_DATA_DIR, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create memory data directory: {e}")

    def load_from_disk(self):
        if os.path.exists(MEMORY_DATA_FILE):
            try:
                with open(MEMORY_DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        mem = EnterpriseMemory(**item)
                        self.memories[mem.memory_id] = mem
            except Exception as e:
                logger.error(f"Error loading enterprise memory from disk: {e}")

    def save_to_disk(self):
        try:
            with open(MEMORY_DATA_FILE, "w", encoding="utf-8") as f:
                json.dumps([m.model_dump() for m in self.memories.values()], indent=2)
                f.write(json.dumps([m.model_dump() for m in self.memories.values()], indent=2))
        except Exception as e:
            logger.error(f"Error saving enterprise memory to disk: {e}")

    def add_memory(self, memory: EnterpriseMemory):
        self.memories[memory.memory_id] = memory
        self.save_to_disk()

    def get_memory(self, memory_id: str) -> Optional[EnterpriseMemory]:
        mem = self.memories.get(memory_id)
        if mem and not mem.is_deleted:
            return mem
        return None

_memory_store_instance = None

def get_memory_store() -> MemoryStore:
    global _memory_store_instance
    if _memory_store_instance is None:
        _memory_store_instance = MemoryStore()
    return _memory_store_instance
