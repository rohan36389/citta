import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from memory_store import get_memory_store, EnterpriseMemory, MemoryProvenance, MemoryVersionRecord
from memory_index import get_memory_index
from memory_policy_engine import get_memory_policy_engine
from memory_validator import get_memory_validator
from memory_categorizer import get_memory_categorizer

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        self.store = get_memory_store()
        self.index = get_memory_index()
        self.policy_engine = get_memory_policy_engine()
        self.validator = get_memory_validator()
        self.categorizer = get_memory_categorizer()

    def create_memory(
        self,
        content: Any,
        owner_user_id: str = "user_default",
        organization_id: str = "org_default",
        visibility: str = "PRIVATE_USER",
        memory_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        intent: Optional[str] = None,
        workflow_id: Optional[str] = None,
        initial_confidence: float = 1.0,
        source_type: str = "MANUAL_USER_INPUT",
        context_query: Optional[str] = None
    ) -> Optional[EnterpriseMemory]:
        m_type = memory_type or self.categorizer.categorize(str(content))

        # 1. Validation check
        val_res = self.validator.validate_candidate(m_type, content, owner_user_id, organization_id, initial_confidence)
        if not val_res.is_valid and not val_res.is_update:
            if val_res.existing_memory_id:
                logger.info(f"Exact duplicate memory found (ID: {val_res.existing_memory_id}); returning existing record.")
                return self.store.get_memory(val_res.existing_memory_id)
            logger.info(f"Memory candidate rejected by MemoryValidator: {val_res.reason}")
            return None

        # 2. Policy Engine check
        pol_res = self.policy_engine.evaluate_policy(m_type, str(content), {})
        if not pol_res.should_store:
            logger.info(f"Memory candidate discarded by MemoryPolicyEngine: {pol_res.reason}")
            return None

        now_ms = round(time.time() * 1000, 2)
        exp_ms = (now_ms + pol_res.ttl_seconds * 1000.0) if pol_res.ttl_seconds else None

        # If update/conflict resolution
        if val_res.is_update and val_res.existing_memory_id:
            existing = self.store.get_memory(val_res.existing_memory_id)
            if existing:
                # Save old version to version_history
                old_ver = MemoryVersionRecord(
                    version=len(existing.version_history) + 1,
                    content=existing.content,
                    updated_at_iso=datetime.now(timezone.utc).isoformat(),
                    updated_by=owner_user_id
                )
                existing.version_history.append(old_ver)
                existing.content = content
                existing.updated_at_ms = now_ms
                existing.expires_at_ms = exp_ms
                self.store.save_to_disk()
                self.index.reindex()
                return existing

        # Create New Memory
        uid = str(uuid.uuid4())[:8]
        mem_id = f"mem_{m_type.lower()}_{uid}"

        prov = MemoryProvenance(
            source_type=source_type,
            source_id=f"src_{uid}",
            created_at_iso=datetime.now(timezone.utc).isoformat(),
            context_query=context_query
        )

        memory = EnterpriseMemory(
            memory_id=mem_id,
            type=m_type,
            owner_user_id=owner_user_id,
            organization_id=organization_id,
            visibility=visibility.upper(),
            content=content,
            entity_id=entity_id,
            intent=intent,
            workflow_id=workflow_id,
            initial_confidence=initial_confidence,
            provenance=prov,
            created_at_ms=now_ms,
            updated_at_ms=now_ms,
            expires_at_ms=exp_ms
        )

        self.store.add_memory(memory)
        self.index.index_memory(memory)
        return memory

    def delete_memory(self, memory_id: str) -> bool:
        mem = self.store.get_memory(memory_id)
        if mem:
            mem.is_deleted = True
            self.store.save_to_disk()
            self.index.reindex()
            return True
        return False

_memory_manager_instance = None

def get_memory_manager() -> MemoryManager:
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance
