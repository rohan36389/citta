import time
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ExecutionStrategy(str, Enum):
    CATALOG = "CATALOG"
    SECTION = "SECTION"
    REASONING = "REASONING"
    CONSULTATIVE = "CONSULTATIVE"
    OUT_OF_DOMAIN = "OUT_OF_DOMAIN"
    ACTION = "ACTION"

class EnterpriseIntent(str, Enum):
    OVERVIEW = "OVERVIEW"
    WORKFLOW = "WORKFLOW"
    BENEFITS = "BENEFITS"
    FEATURES = "FEATURES"
    CAPABILITIES = "CAPABILITIES"
    FAQ = "FAQ"
    PRICING = "PRICING"
    CONTACT = "CONTACT"
    INDUSTRIES = "INDUSTRIES"
    TARGET_AUDIENCE = "TARGET_AUDIENCE"
    RELATIONSHIPS = "RELATIONSHIPS"
    LIST = "LIST"
    CLASSIFICATION = "CLASSIFICATION"
    COMPARISON = "COMPARISON"
    RECOMMENDATION = "RECOMMENDATION"
    SUITABILITY = "SUITABILITY"
    INTEGRATION = "INTEGRATION"
    IMPLEMENTATION = "IMPLEMENTATION"
    USE_CASE = "USE_CASE"
    SCHEDULE_DEMO = "SCHEDULE_DEMO"
    CREATE_TICKET = "CREATE_TICKET"
    SEND_PROPOSAL = "SEND_PROPOSAL"
    EXECUTE_ACTION = "EXECUTE_ACTION"

class ConversationState(BaseModel):
    active_entity: Optional[str] = None
    active_category: Optional[str] = None
    last_intent: Optional[str] = None
    last_section: Optional[str] = None

class SessionState(BaseModel):
    recent_entities: List[str] = Field(default_factory=list)
    recently_compared_entities: List[str] = Field(default_factory=list)
    strategy_history: List[str] = Field(default_factory=list)

class DecisionStep(BaseModel):
    stage: str
    result: str
    reason: str
    timestamp_ms: float = Field(default_factory=lambda: round(time.time() * 1000, 2))

class OrchestrationContext(BaseModel):
    session_id: str
    original_query: str
    normalized_query: str = ""
    
    # Entity Resolution
    resolved_entity_id: Optional[str] = None
    resolved_entity_name: Optional[str] = None
    resolved_category: Optional[str] = None
    matched_entity_ids: List[str] = Field(default_factory=list)
    
    # Intent & Section
    intent: str = EnterpriseIntent.OVERVIEW.value
    section: Optional[str] = None
    
    # Strategy & Execution
    execution_strategy: ExecutionStrategy = ExecutionStrategy.CATALOG
    confidence: float = 1.0
    reason: str = ""
    requires_llm: bool = False
    
    # Special Flags
    is_general_catalog_query: bool = False
    is_out_of_domain: bool = False
    is_ambiguous: bool = False
    is_unknown_entity: bool = False
    unknown_entity_name: Optional[str] = None
    
    # State Memory
    conversation_state: ConversationState = Field(default_factory=ConversationState)
    session_state: SessionState = Field(default_factory=SessionState)
    
    # Decision Trace & Results
    decision_trace: List[Dict[str, Any]] = Field(default_factory=list)
    response_text: Optional[str] = None
    citations: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    redirect: Optional[str] = None
    source: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)

    def add_trace(self, stage: str, result: str, reason: str):
        step = DecisionStep(stage=stage, result=result, reason=reason)
        self.decision_trace.append(step.model_dump())
