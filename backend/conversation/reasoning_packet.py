import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class Evidence:
    """Attributed fact item retrieved from registry or RAG source."""
    id: str
    section: str
    text: str
    confidence: float
    source_file: str
    priority: int = 1
    source_type: str = "registry"  # registry, rag, deterministic
    entity_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass(frozen=True)
class ReasoningPacket:
    """
    Immutable Reasoning Packet encapsulating all input state for the Enterprise Reasoning Engine.
    Ensures zero mutation during generative synthesis.
    """
    user_query: str
    active_entity: Optional[str]
    intent: str
    conversation_objective: str
    response_intent: str
    planner_strategy: str
    conversation_stage: str
    memory: Dict[str, Any]
    ranked_evidence: List[Evidence]
    behavior_policy: Dict[str, Any]
    reasoning_constraints: Dict[str, Any]
    validation_constraints: Dict[str, Any]
