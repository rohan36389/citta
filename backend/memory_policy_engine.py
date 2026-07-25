import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Default TTL policies in seconds
TTL_POLICY_SECONDS: Dict[str, Optional[float]] = {
    "PREFERENCE": None,          # Infinite
    "USER": None,                # Infinite
    "ORG": None,                 # Infinite
    "WORKFLOW": 90 * 86400.0,    # 90 Days
    "ACTION": 180 * 86400.0,     # 180 Days
    "CONVERSATION": 30 * 86400.0,# 30 Days
    "REASONING": 60 * 86400.0    # 60 Days
}

EPHEMERAL_PATTERNS = [
    "in 5 mins", "in 10 minutes", "starts in", "right now", "temporarily", "just for now", "ignore this"
]

class MemoryPolicyDecision(BaseModel):
    should_store: bool
    ttl_seconds: Optional[float] = None
    overwrite_behavior: str = "VERSION_ARCHIVE"
    reason: str

class MemoryPolicyEngine:
    def __init__(self):
        pass

    def evaluate_policy(self, candidate_type: str, content_str: str, metadata: Dict[str, Any]) -> MemoryPolicyDecision:
        c_lower = str(content_str).lower().strip()

        # Check ephemeral filter
        if any(pat in c_lower for pat in EPHEMERAL_PATTERNS):
            return MemoryPolicyDecision(
                should_store=False,
                ttl_seconds=0.0,
                reason=f"Candidate contains ephemeral indicator pattern; discarded by MemoryPolicyEngine."
            )

        ttl = TTL_POLICY_SECONDS.get(candidate_type.upper(), 30 * 86400.0)

        return MemoryPolicyDecision(
            should_store=True,
            ttl_seconds=ttl,
            overwrite_behavior="VERSION_ARCHIVE",
            reason=f"Policy approved storage for type '{candidate_type}' with TTL={ttl}s."
        )

_memory_policy_engine_instance = None

def get_memory_policy_engine() -> MemoryPolicyEngine:
    global _memory_policy_engine_instance
    if _memory_policy_engine_instance is None:
        _memory_policy_engine_instance = MemoryPolicyEngine()
    return _memory_policy_engine_instance
