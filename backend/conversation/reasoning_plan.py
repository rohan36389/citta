from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional

class ResponseIntent(Enum):
    EXPLAIN = "EXPLAIN"
    SUMMARIZE = "SUMMARIZE"
    COMPARE = "COMPARE"
    RECOMMEND = "RECOMMEND"
    QUALIFY = "QUALIFY"
    CLARIFY = "CLARIFY"
    WORKFLOW = "WORKFLOW"
    BENEFITS = "BENEFITS"
    NEXT_STEP = "NEXT_STEP"

class ConversationObjective(Enum):
    DISCOVER_PRODUCTS = "DISCOVER_PRODUCTS"
    COMPARE_SOLUTIONS = "COMPARE_SOLUTIONS"
    BOOK_DEMO = "BOOK_DEMO"
    TECHNICAL_EVALUATION = "TECHNICAL_EVALUATION"
    PRICING_INQUIRY = "PRICING_INQUIRY"
    ARCHITECTURE_REVIEW = "ARCHITECTURE_REVIEW"
    LEAD_QUALIFICATION = "LEAD_QUALIFICATION"

@dataclass
class ReasoningPlan:
    """Task-oriented reasoning plan guiding LLM synthesis."""
    goal: str
    already_explained: List[str] = field(default_factory=list)
    need: str = ""
    relevant_evidence_ids: List[str] = field(default_factory=list)
    response_shape: str = "Progressive Disclosure (Overview -> Business Context -> Capabilities -> Qualification)"
    follow_up_prompt: str = ""
