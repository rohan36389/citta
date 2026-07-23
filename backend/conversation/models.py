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

from enum import Enum
from typing import Dict, Any, List, Optional, Union

class BusinessIntent(Enum):
    OVERVIEW = "Overview"
    AVAILABILITY = "Availability"
    FEATURES = "Features"
    BENEFITS = "Benefits"
    WORKFLOW = "Workflow"
    ARCHITECTURE = "Architecture"
    PRICING = "Pricing"
    INTEGRATION = "Integration"
    COMPARISON = "Comparison"
    INDUSTRIES = "Industries"
    CASE_STUDIES = "Case Studies"
    IMPLEMENTATION = "Implementation"
    SUPPORT = "Support"
    CONTACT = "Contact"
    LEADERSHIP = "Leadership"
    DEMO_REQUEST = "Demo Request"
    REQUIREMENT_GATHERING = "Requirement Gathering"
    RECOMMENDATION = "Recommendation"
    PROBLEM_STATEMENT = "Problem Statement"
    COMPLIANCE = "Compliance"
    SECURITY = "Security"
    MIGRATION = "Migration"
    LICENSING = "Licensing"
    SCALABILITY = "Scalability"
    UNKNOWN = "Unknown"

class ConversationalIntent(Enum):
    GREETING = "Greeting"
    CONFIRMATION = "Confirmation"
    CLARIFICATION = "Clarification"
    CONTINUE_TOPIC = "Continue Previous Topic"
    GOODBYE = "Goodbye"
    SMALL_TALK = "Small Talk"
    NONE = "None"

class IntentSource(Enum):
    MESSAGE = "Message"
    MEMORY = "Memory"
    CONVERSATION_CONTEXT = "Conversation Context"
    KNOWLEDGE_BASE = "Knowledge Base"

@dataclass
class Signal:
    signal_type: str        # KeywordSignal, EntitySignal, ConversationSignal, MemorySignal
    source: IntentSource
    value: str
    weight: float

@dataclass
class IntentCandidate:
    intent: Union[BusinessIntent, ConversationalIntent]
    signals: List[Signal]
    detection_confidence: float
    ranking_confidence: float
    overall_confidence: float
    reasoning: str

@dataclass
class EnterpriseIntentResult:
    primary_intent: IntentCandidate
    secondary_intents: List[IntentCandidate]
    conversational_intent: Optional[IntentCandidate]
    raw_query: str
    normalized_query: str

@dataclass
class IntentAnalysis:
    primary_intent: str
    secondary_intents: List[str] = field(default_factory=list)
    confidence: float = 1.0
    entities: List[Dict[str, Any]] = field(default_factory=list)
    rich_result: Optional[EnterpriseIntentResult] = None

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
