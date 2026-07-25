import time
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from memory_store import get_memory_store, EnterpriseMemory
from memory_index import get_memory_index
from memory_permission_engine import get_memory_permission_engine

logger = logging.getLogger(__name__)

class ResolvedMemory(BaseModel):
    memory_id: str
    type: str
    content: Any
    confidence: float
    visibility: str
    provenance_source: str
    created_at_iso: str

class MemoryResolver:
    def __init__(self):
        self.store = get_memory_store()
        self.index = get_memory_index()
        self.perm_engine = get_memory_permission_engine()

    def resolve_relevant_memories(
        self,
        user_id: str,
        organization_id: str,
        user_role: str,
        entity_id: Optional[str] = None,
        intent: Optional[str] = None,
        workflow_id: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[ResolvedMemory]:
        now_ms = time.time() * 1000.0

        # Search candidates
        candidates = self.index.search(
            user_id=user_id,
            org_id=organization_id,
            entity_id=entity_id
        )

        # Also search global & org preferences
        pref_candidates = self.index.search(user_id=user_id, memory_type="PREFERENCE")
        for p in pref_candidates:
            if p not in candidates:
                candidates.append(p)

        resolved = []
        for mem in candidates:
            # 1. Expired check
            if mem.expires_at_ms and mem.expires_at_ms < now_ms:
                continue

            # 2. Permission check
            perm_res = self.perm_engine.check_read_access(mem, user_id, organization_id, user_role)
            if not perm_res.allowed:
                continue

            # 3. Dynamic Decayed Confidence check
            decayed_conf = mem.get_decayed_confidence(now_ms)
            if decayed_conf < 0.35:
                continue

            resolved.append(ResolvedMemory(
                memory_id=mem.memory_id,
                type=mem.type,
                content=mem.content,
                confidence=decayed_conf,
                visibility=mem.visibility,
                provenance_source=mem.provenance.source_type,
                created_at_iso=mem.provenance.created_at_iso
            ))

        return resolved

_memory_resolver_instance = None

def get_memory_resolver() -> MemoryResolver:
    global _memory_resolver_instance
    if _memory_resolver_instance is None:
        _memory_resolver_instance = MemoryResolver()
    return _memory_resolver_instance
