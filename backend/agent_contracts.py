import time
import logging
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class AgentID(str, Enum):
    BUSINESS_SOLUTIONS = "BusinessSolutionsAgent"
    TECHNICAL_ARCHITECTURE = "TechnicalArchitectureAgent"
    WORKFLOW = "WorkflowAgent"
    MEMORY = "MemoryAgent"
    RESEARCH = "ResearchAgent"
    REVIEWER = "ReviewerAgent"
    CONSENSUS_BUILDER = "ConsensusBuilder"

class AgentContext(BaseModel):
    agent_id: str
    task: str
    objective: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    relevant_evidence: Dict[str, Any] = Field(default_factory=dict)
    relevant_memory: List[Dict[str, Any]] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)

class AgentOutput(BaseModel):
    agent_id: str
    task: str
    findings: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    evidence_used: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0
    status: str = "SUCCESS"  # SUCCESS, FAILED, FALLBACK, SKIPPED
