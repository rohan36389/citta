import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator

# Phase 1 Sub-enums

class UnderstandingIntent(str, Enum):
    ASK = "ASK"
    LIST = "LIST"
    COUNT = "COUNT"
    COMPARE = "COMPARE"
    SEARCH = "SEARCH"
    RECOMMEND = "RECOMMEND"
    SUMMARIZE = "SUMMARIZE"
    MULTI_TOPIC = "MULTI_TOPIC"
    FOLLOW_UP = "FOLLOW_UP"
    CLARIFY_NEEDED = "CLARIFY_NEEDED"

class OutputShape(str, Enum):
    TABLE = "TABLE"
    LIST = "LIST"
    PARAGRAPH = "PARAGRAPH"
    RECOMMENDATION = "RECOMMENDATION"
    COUNT_VALUE = "COUNT_VALUE"

class HallucinationRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ValidationAction(str, Enum):
    SEND = "SEND"
    RETRY_RETRIEVAL = "RETRY_RETRIEVAL"
    RETRY_COMPOSE = "RETRY_COMPOSE"
    ESCALATE_TO_CLARIFY = "ESCALATE_TO_CLARIFY"

# Phase 1 Sub-objects

class Entity(BaseModel):
    name: str
    type: str
    value: Optional[str] = None

class ConfidenceObject(BaseModel):
    intent_confidence: float = Field(..., ge=0.0, le=1.0)
    entity_confidence: float = Field(..., ge=0.0, le=1.0)
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def compute_overall_confidence(self) -> 'ConfidenceObject':
        # DERIVATION RULE: min(intent_confidence, entity_confidence).
        # RATIONALE: We select the minimum of both confidence levels because the understanding 
        # layer acts as a chain where the weakest link determines the overall integrity. A high 
        # intent confidence combined with a low entity extraction confidence still yields an 
        # unreliable execution context for downstream database or RAG retrievals.
        self.overall_confidence = min(self.intent_confidence, self.entity_confidence)
        return self

class UnderstandingResult(BaseModel):
    intent: UnderstandingIntent
    entities: List[Entity] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    resolved_deterministically: bool
    confidence: ConfidenceObject
    requires_clarification: bool
    clarification_question: Optional[str] = None

class PlanTask(BaseModel):
    id: str
    description: str
    requires_llm: bool

class ExecutionPlan(BaseModel):
    intent: UnderstandingIntent
    tasks: List[PlanTask] = Field(default_factory=list)
    required_knowledge: List[str] = Field(default_factory=list)
    is_deterministic: bool
    expected_output_shape: OutputShape

# Budget Definitions

class GlobalBudget(BaseModel):
    max_runtime_ms: int = 5000
    remaining_runtime_ms: int = 5000

class RetrievalBudget(BaseModel):
    max_retrievals: int = 3
    remaining_retrievals: int = 3
    max_context_tokens: int = 6000
    remaining_context_tokens: int = 6000

class LLMBudget(BaseModel):
    max_calls: int = 2
    remaining_calls: int = 2

class ExecutionBudget(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    global_budget: GlobalBudget = Field(default_factory=GlobalBudget, alias="global")
    retrieval: RetrievalBudget = Field(default_factory=RetrievalBudget)
    llm: LLMBudget = Field(default_factory=LLMBudget)

class RetrievalRequest(BaseModel):
    topics: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    max_chunks: int = 5
    ranking_strategy: str = "hybrid"
    retrieval_pass_number: int = Field(default=1, ge=1)
    budget_remaining: ExecutionBudget

class RetrievalChunk(BaseModel):
    content: str
    source: str
    score: float

class RetrievalResult(BaseModel):
    chunks: List[RetrievalChunk] = Field(default_factory=list)
    retrieval_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    sufficient: bool = False
    suggested_next_query: Optional[str] = None

class ResponsePlan(BaseModel):
    structure: List[str] = Field(default_factory=list)
    sections: List[str] = Field(default_factory=list)
    tone: str = "professional"
    low_confidence_flag: bool = False
    draft_response: Optional[str] = None

class ValidationResult(BaseModel):
    is_complete: bool = False
    is_grounded: bool = False
    missing_aspects: List[str] = Field(default_factory=list)
    hallucination_risk: HallucinationRisk = HallucinationRisk.HIGH
    validation_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    action: ValidationAction = ValidationAction.ESCALATE_TO_CLARIFY

# Audit, Event, and History Objects

class Event(BaseModel):
    name: Literal[
        'UNDERSTANDING_COMPLETE',
        'PLAN_COMPLETE',
        'RETRIEVAL_COMPLETE',
        'MORE_EVIDENCE_REQUIRED',
        'VALIDATION_FAILED',
        'VALIDATION_PASSED',
        'TIMEOUT',
        'CLARIFICATION_REQUIRED',
        'BUDGET_EXCEEDED',
        'RETRY_COMPOSE',
        'RETRY_RETRIEVAL'
    ]
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    producer: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Optional[Dict[str, Any]] = None

class LLMMetrics(BaseModel):
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    request_upload_ms: int = 0
    network_wait_ms: int = 0
    estimated_inference_time_ms: int = 0
    response_download_ms: int = 0
    total_llm_duration_ms: int = 0

class ExecutionStep(BaseModel):
    state: str
    duration_ms: int
    result: Literal['SUCCESS', 'FAILURE', 'PARTIAL']
    notes: Optional[str] = None
    start_timestamp: Optional[float] = None
    end_timestamp: Optional[float] = None
    retry_count: int = 0
    emitted_event: Optional[str] = None

class CapabilityResult(BaseModel):
    status: Literal['SUCCESS', 'FAILURE', 'TIMEOUT']
    duration_ms: int
    confidence: Optional[float] = None
    next_event: str
    data: Any
    name: str = "Unknown"
    llm_metrics: Optional[LLMMetrics] = None

class RequestContext(BaseModel):
    query: str
    tenant_id: str
    session_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Primary Runtime Object

class ExecutionContext(BaseModel):
    request: RequestContext
    understanding: Optional[UnderstandingResult] = None
    execution_plan: Optional[ExecutionPlan] = None
    retrieval_request: Optional[RetrievalRequest] = None
    retrieval_result: Optional[RetrievalResult] = None
    response_plan: Optional[ResponsePlan] = None
    validation_result: Optional[ValidationResult] = None
    budget: ExecutionBudget = Field(default_factory=ExecutionBudget)
    events: List[Event] = Field(default_factory=list)
    history: List[ExecutionStep] = Field(default_factory=list)
    capability_results: List[CapabilityResult] = Field(default_factory=list)
