import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ResponseStrategy:
    GREETING = "GREETING"
    YES_NO = "YES_NO"
    DEFINITION = "DEFINITION"
    EXPLANATION = "EXPLANATION"
    OVERVIEW = "OVERVIEW"
    COMPARISON = "COMPARISON"
    LIST = "LIST"
    CONTACT_INFO = "CONTACT_INFO"
    LEADERSHIP_INFO = "LEADERSHIP_INFO"
    PRODUCT_INFO = "PRODUCT_INFO"
    SERVICE_INFO = "SERVICE_INFO"
    INDUSTRY_INFO = "INDUSTRY_INFO"
    TECHNOLOGY_INFO = "TECHNOLOGY_INFO"
    RECOMMENDATION = "RECOMMENDATION"
    PRICING = "PRICING"
    DEMO_REQUEST = "DEMO_REQUEST"
    SMALL_TALK = "SMALL_TALK"
    OUT_OF_DOMAIN = "OUT_OF_DOMAIN"

# Explicit Out-Of-Domain Keywords / Patterns
OOD_PATTERNS = [
    r"\bamitabh\b", r"\bbachchan\b", r"\bipl\b", r"\bcricket\b", r"\bfootball\b", r"\bmessi\b", r"\bronaldo\b",
    r"\btesla\b", r"\bapple\s+iphone\b", r"\bnetflix\b", r"\buber\b", r"\bwho\s+is\s+actor\b",
    r"\bweather\b", r"\brecipe\b", r"\bpizza\b", r"\bcapital\s+of\b", r"\bmovie\b", r"\bcelebrity\b",
    r"\bpresidential\s+election\b", r"\bworld\s+war\b", r"\bbitcoin\s+price\b"
]

# Simple question indicators (Concise 1-sentence response)
SIMPLE_QUESTION_PATTERNS = [
    r"\bwhere\s+(is|are)\s+(you|cittaai|office|located)\b",
    r"\bwho\s+is\s+(the\s+)?(ceo|cto|coo|cmo)\b",
    r"\bwhat\s+is\s+cittaai'?s?\s+email\b",
    r"\bwhen\s+was\s+cittaai\s+founded\b",
    r"\bdo\s+you\s+(have|provide|offer)\b"
]

# Broad question indicators (Structured Overview format)
BROAD_QUESTION_PATTERNS = [
    r"\btell\s+me\s+about\b",
    r"\bexplain\b",
    r"\boverview\b",
    r"\bwhat\s+is\b",
    r"\bhow\s+does\s+.*work\b",
    r"\bdifference\s+between\b",
    r"\bcompare\b",
    r"\bwhat\s+solutions\b",
    r"\bwhat\s+services\b",
    r"\bwhat\s+products\b"
]

@dataclass
class PlanResult:
    strategy: str
    is_out_of_domain: bool
    out_of_domain_response: Optional[str]
    adaptive_length_target: str  # "CONCISE_1_SENTENCE", "PARAGRAPH", "STRUCTURED_OVERVIEW"
    allows_follow_up_suggestions: bool

class ResponsePlanner:
    def plan(self, query: str, context_state: Optional[Dict[str, Any]] = None) -> PlanResult:
        q_lower = query.lower().strip()

        # 1. Out-of-Domain Detection
        for pattern in OOD_PATTERNS:
            if re.search(pattern, q_lower):
                return PlanResult(
                    strategy=ResponseStrategy.OUT_OF_DOMAIN,
                    is_out_of_domain=True,
                    out_of_domain_response=(
                        "I specialize in answering questions about CittaAI, including its products, services, leadership, "
                        "technologies, and enterprise solutions. I don't have verified information about that topic within "
                        "my current knowledge base."
                    ),
                    adaptive_length_target="CONCISE_1_SENTENCE",
                    allows_follow_up_suggestions=False
                )

        # 2. Greeting / Small Talk
        if re.search(r"^(hi|hello|hey|greetings|good\s+morning|good\s+afternoon|good\s+evening)\b", q_lower):
            return PlanResult(
                strategy=ResponseStrategy.GREETING,
                is_out_of_domain=False,
                out_of_domain_response=None,
                adaptive_length_target="CONCISE_1_SENTENCE",
                allows_follow_up_suggestions=True
            )

        if re.search(r"\b(thanks|thank\s+you|bye|goodbye|cool|great)\b", q_lower):
            return PlanResult(
                strategy=ResponseStrategy.SMALL_TALK,
                is_out_of_domain=False,
                out_of_domain_response=None,
                adaptive_length_target="CONCISE_1_SENTENCE",
                allows_follow_up_suggestions=False
            )

        # 3. Yes / No Question
        if re.search(r"^(do|does|can|is|are|will|should)\s+(you|cittaai|your)\b", q_lower):
            return PlanResult(
                strategy=ResponseStrategy.YES_NO,
                is_out_of_domain=False,
                out_of_domain_response=None,
                adaptive_length_target="PARAGRAPH",
                allows_follow_up_suggestions=False
            )

        # 4. Comparison Question
        if re.search(r"\b(difference|compare|vs|versus)\b", q_lower):
            return PlanResult(
                strategy=ResponseStrategy.COMPARISON,
                is_out_of_domain=False,
                out_of_domain_response=None,
                adaptive_length_target="STRUCTURED_OVERVIEW",
                allows_follow_up_suggestions=True
            )

        # 5. Leadership Question
        if re.search(r"\b(ceo|cto|coo|cmo|founder|founders|leadership|who\s+leads|who\s+manages)\b", q_lower):
            is_simple = any(re.search(p, q_lower) for p in SIMPLE_QUESTION_PATTERNS)
            return PlanResult(
                strategy=ResponseStrategy.LEADERSHIP_INFO,
                is_out_of_domain=False,
                out_of_domain_response=None,
                adaptive_length_target="CONCISE_1_SENTENCE" if is_simple else "PARAGRAPH",
                allows_follow_up_suggestions=not is_simple
            )

        # 6. Location / Contact
        if re.search(r"\b(location|address|office|where\s+are\s+you|phone|email|contact)\b", q_lower):
            return PlanResult(
                strategy=ResponseStrategy.CONTACT_INFO,
                is_out_of_domain=False,
                out_of_domain_response=None,
                adaptive_length_target="CONCISE_1_SENTENCE",
                allows_follow_up_suggestions=False
            )

        # 7. Simple Question Check
        if any(re.search(p, q_lower) for p in SIMPLE_QUESTION_PATTERNS) or len(q_lower.split()) <= 3:
            return PlanResult(
                strategy=ResponseStrategy.DEFINITION,
                is_out_of_domain=False,
                out_of_domain_response=None,
                adaptive_length_target="CONCISE_1_SENTENCE",
                allows_follow_up_suggestions=False
            )

        # 8. Broad Explanation / Overview
        return PlanResult(
            strategy=ResponseStrategy.EXPLANATION,
            is_out_of_domain=False,
            out_of_domain_response=None,
            adaptive_length_target="STRUCTURED_OVERVIEW",
            allows_follow_up_suggestions=True
        )

_planner_instance = None

def get_response_planner() -> ResponsePlanner:
    global _planner_instance
    if _planner_instance is None:
        _planner_instance = ResponsePlanner()
    return _planner_instance
