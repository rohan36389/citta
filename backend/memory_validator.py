import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from memory_store import get_memory_store, EnterpriseMemory, MemoryVersionRecord

logger = logging.getLogger(__name__)

class MemoryValidationResult(BaseModel):
    is_valid: bool
    is_update: bool = False
    existing_memory_id: Optional[str] = None
    reason: str

class MemoryValidator:
    def __init__(self):
        self.store = get_memory_store()

    def validate_candidate(
        self,
        candidate_type: str,
        content: Any,
        owner_user_id: str,
        organization_id: str,
        initial_confidence: float = 1.0
    ) -> MemoryValidationResult:
        if not content:
            return MemoryValidationResult(
                is_valid=False,
                reason="Memory candidate content is empty."
            )

        if initial_confidence < 0.60:
            return MemoryValidationResult(
                is_valid=False,
                reason=f"Candidate confidence ({initial_confidence}) below minimum required threshold (0.60)."
            )

        content_str = str(content).strip().lower()

        for mem_id, mem in self.store.memories.items():
            if mem.is_deleted or mem.owner_user_id != owner_user_id:
                continue

            existing_str = str(mem.content).strip().lower()

            # Exact duplicate
            if existing_str == content_str and mem.type == candidate_type:
                return MemoryValidationResult(
                    is_valid=False,
                    existing_memory_id=mem_id,
                    reason=f"Exact duplicate memory already exists (ID: {mem_id})."
                )

            # Conflict resolution for PREFERENCE memories (e.g. report format)
            if candidate_type == "PREFERENCE" and mem.type == "PREFERENCE":
                if ("format" in content_str or "report" in content_str) and ("format" in existing_str or "report" in existing_str):
                    return MemoryValidationResult(
                        is_valid=True,
                        is_update=True,
                        existing_memory_id=mem_id,
                        reason=f"Conflicting preference memory detected; invalidating older version and creating Version {len(mem.version_history) + 2}."
                    )

        return MemoryValidationResult(
            is_valid=True,
            is_update=False,
            reason="Memory candidate passed validation checks."
        )

_memory_validator_instance = None

def get_memory_validator() -> MemoryValidator:
    global _memory_validator_instance
    if _memory_validator_instance is None:
        _memory_validator_instance = MemoryValidator()
    return _memory_validator_instance
