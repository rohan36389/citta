from typing import Protocol, Dict, Any, List, Optional
from backend.conversation.models import (
    ConversationContext,
    IntentAnalysis,
    DiscoveryState,
    LeadQualification,
    ToolSelection,
    ResponseStrategy,
    DraftResponse,
    CriticReview,
    ExplainabilityRecord,
    ResponseComposition
)

class IContextEngine(Protocol):
    def get_or_create_context(self, session_id: str) -> ConversationContext:
        ...
    def update_context(self, context: ConversationContext, updates: Dict[str, Any]) -> None:
        ...
    def transition_stage(self, context: ConversationContext, next_stage: str) -> bool:
        ...

class IUnderstandingEngine(Protocol):
    def analyze_intent(self, query: str, context: ConversationContext) -> IntentAnalysis:
        ...
    def run_discovery(self, query: str, intent: IntentAnalysis, context: ConversationContext) -> DiscoveryState:
        ...
    def qualify_lead(self, discovery: DiscoveryState) -> LeadQualification:
        ...

class IKnowledgeEngine(Protocol):
    def select_tools(self, intent: IntentAnalysis, context: ConversationContext) -> ToolSelection:
        ...
    def orchestrate_knowledge(self, tool_sel: ToolSelection, query: str) -> Dict[str, Any]:
        ...
    def detect_knowledge_gap(self, retrieved_data: Dict[str, Any], query: str) -> bool:
        ...

class IStrategyEngine(Protocol):
    def formulate_strategy(
        self,
        intent: IntentAnalysis,
        discovery: DiscoveryState,
        context: ConversationContext
    ) -> ResponseStrategy:
        ...
    def plan_response(self, strategy: ResponseStrategy, context: ConversationContext) -> List[str]:
        ...

class IPromptEngine(Protocol):
    def build_system_prompt(self, context: ConversationContext, strategy: ResponseStrategy) -> str:
        ...
    def build_user_prompt(self, query: str, retrieved_knowledge: Dict[str, Any]) -> str:
        ...

class IResponseEngine(Protocol):
    def compose_draft(
        self,
        system_prompt: str,
        user_prompt: str,
        strategy: ResponseStrategy,
        context: ConversationContext
    ) -> DraftResponse:
        ...
    def generate_suggestions(self, draft: DraftResponse, context: ConversationContext) -> List[Dict[str, str]]:
        ...

class IQualityEngine(Protocol):
    def review_draft(self, draft: DraftResponse, context: ConversationContext) -> CriticReview:
        ...
    def validate_facts(self, draft: DraftResponse, verified_evidence: Dict[str, Any]) -> bool:
        ...
    def create_explainability_record(
        self,
        context: ConversationContext,
        intent: IntentAnalysis,
        strategy: ResponseStrategy,
        review: CriticReview,
        timings: Dict[str, float]
    ) -> ExplainabilityRecord:
        ...

class IAnalyticsEngine(Protocol):
    def track_turn(self, context: ConversationContext, composition: ResponseComposition) -> None:
        ...
    def track_dropoff(self, session_id: str, stage: str) -> None:
        ...

class IMemoryStore(Protocol):
    def load_memory(self, session_id: str) -> List[Dict[str, str]]:
        ...
    def save_memory(self, session_id: str, messages: List[Dict[str, str]]) -> None:
        ...
    def clear_memory(self, session_id: str) -> None:
        ...
