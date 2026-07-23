from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class ConversationContext:
    session_id: str
    turn_count: int = 0
    current_stage: str = "Greeting"
    history: List[Dict[str, str]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    active_entity_id: Optional[str] = None
    active_registry: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntentAnalysis:
    primary_intent: str
    secondary_intents: List[str] = field(default_factory=list)
    confidence: float = 1.0
    entities: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class DiscoveryState:
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    urgency: Optional[str] = None
    timeline: Optional[str] = None
    budget: Optional[str] = None
    missing_fields: List[str] = field(default_factory=list)
    lead_score: float = 0.0

@dataclass
class LeadQualification:
    score: float
    interest_level: str  # LOW, MEDIUM, HIGH, HOT
    readiness_tier: str   # EXPLORATORY, EVALUATING, READY
    next_best_action: str

@dataclass
class ToolSelection:
    selected_tools: List[str] = field(default_factory=list)
    queries: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResponseStrategy:
    selected_strategy: str  # Consultative, Educational, Persuasive, Objection
    audience_level: str     # CEO, Developer, General
    response_length: str    # Short, Medium, Detailed
    checklist: List[str] = field(default_factory=list)
    active_rules: List[str] = field(default_factory=list)

@dataclass
class DraftResponse:
    text: str
    suggestions: List[Dict[str, str]] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)

@dataclass
class CriticReview:
    is_approved: bool
    reasons: List[str] = field(default_factory=list)
    groundedness_score: float = 1.0
    objection_handled_correctly: bool = True
    suggested_rewrite: Optional[str] = None

@dataclass
class ExplainabilityRecord:
    session_id: str
    turn: int
    intent: str
    stage: str
    strategy: str
    tools_called: List[str]
    business_rules_applied: List[str]
    confidence_score: float
    timings_ms: Dict[str, float] = field(default_factory=dict)

@dataclass
class ResponseComposition:
    text: str
    suggestions: List[Dict[str, str]] = field(default_factory=list)
    redirect_url: Optional[str] = None
    explainability: Optional[ExplainabilityRecord] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
