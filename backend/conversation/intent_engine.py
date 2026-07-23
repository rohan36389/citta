import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from backend.conversation.models import (
    BusinessIntent,
    ConversationalIntent,
    IntentSource,
    Signal,
    IntentCandidate,
    EnterpriseIntentResult,
    ConversationContext
)

logger = logging.getLogger(__name__)

# Common Spelling Typo Maps
TYPO_CORRECTIONS = {
    "intrgration": "integration",
    "integrat": "integrate",
    "priceing": "pricing",
    "pracing": "pricing",
    "costing": "pricing",
    "archtecture": "architecture",
    "architecure": "architecture",
    "feautres": "features",
    "fetures": "features",
    "benifits": "benefits",
    "benefites": "benefits",
    "casestudy": "case study",
    "recomendation": "recommendation",
    "demoo": "demo"
}

# Signal Regex Patterns for Business Intents
BUSINESS_INTENT_PATTERNS: Dict[BusinessIntent, List[Tuple[str, float]]] = {
    BusinessIntent.INTEGRATION: [
        (r"\bintegrat(e|ion|ed|ing|es)?\b", 0.95),
        (r"\bconnect(ed|ion|s)?\b", 0.80),
        (r"\bapi(s)?\b", 0.85),
        (r"\bwebhook(s)?\b", 0.85),
        (r"\bsap\b", 0.70),
        (r"\bsalesforce\b", 0.70),
        (r"\berp\b", 0.75),
        (r"\bcrm\b", 0.75)
    ],
    BusinessIntent.PRICING: [
        (r"\bpric(e|ing|es)?\b", 0.95),
        (r"\bcost(s|ing)?\b", 0.90),
        (r"\bhow\s+much\b", 0.90),
        (r"\bquote\b", 0.85),
        (r"\bcommercial(s)?\b", 0.85),
        (r"\bplan(s)?\b", 0.70),
        (r"\bsubscription\b", 0.80),
        (r"\blicens(e|ing)?\b", 0.85)
    ],
    BusinessIntent.COMPARISON: [
        (r"\bcompar(e|ison|ing|es)?\b", 0.95),
        (r"\bversus\b", 0.90),
        (r"\bvs\b", 0.90),
        (r"\bdifference(s)?\b", 0.85),
        (r"\bbetter\s+than\b", 0.85),
        (r"\bor\b", 0.40)
    ],
    BusinessIntent.BENEFITS: [
        (r"\bbenefit(s)?\b", 0.95),
        (r"\bvalue\b", 0.80),
        (r"\broi\b", 0.90),
        (r"\badvantage(s)?\b", 0.85),
        (r"\bwhy\s+use\b", 0.85),
        (r"\bimpact\b", 0.75)
    ],
    BusinessIntent.FEATURES: [
        (r"\bfeature(s)?\b", 0.95),
        (r"\bcapabilit(y|ies)\b", 0.90),
        (r"\bfunction(ality|s)?\b", 0.85),
        (r"\bwhat\s+can\s+it\s+do\b", 0.85),
        (r"\bmodule(s)?\b", 0.80)
    ],
    BusinessIntent.ARCHITECTURE: [
        (r"\barchitectur(e|al)\b", 0.95),
        (r"\btech\s+stack\b", 0.90),
        (r"\binfrastructure\b", 0.85),
        (r"\bsecurity\b", 0.80),
        (r"\bcloud\b", 0.75),
        (r"\bdatabase\b", 0.75),
        (r"\bdeployment\b", 0.85)
    ],
    BusinessIntent.WORKFLOW: [
        (r"\bworkflow(s)?\b", 0.95),
        (r"\bhow\s+it\s+works\b", 0.90),
        (r"\bprocess\b", 0.80),
        (r"\bstep(s)?\b", 0.75),
        (r"\bpipeline\b", 0.80)
    ],
    BusinessIntent.DEMO_REQUEST: [
        (r"\bdemo\b", 0.95),
        (r"\bschedule\b", 0.85),
        (r"\bbook\b", 0.80),
        (r"\btrial\b", 0.90),
        (r"\bwalkthrough\b", 0.90),
        (r"\bmeeting\b", 0.75)
    ],
    BusinessIntent.CASE_STUDIES: [
        (r"\bcase\s+stud(y|ies)\b", 0.95),
        (r"\bsuccess\s+stor(y|ies)\b", 0.90),
        (r"\bexample(s)?\b", 0.75),
        (r"\bclient(s)?\b", 0.75),
        (r"\bcustomer\s+story\b", 0.90)
    ],
    BusinessIntent.INDUSTRIES: [
        (r"\bindustr(y|ies)\b", 0.90),
        (r"\bsector(s)?\b", 0.85),
        (r"\bhealthcare\b", 0.80),
        (r"\bretail\b", 0.80),
        (r"\bpharma\b", 0.80),
        (r"\bmanufacturing\b", 0.80),
        (r"\breal\s+estate\b", 0.80)
    ],
    BusinessIntent.RECOMMENDATION: [
        (r"\brecommend(ation|ed|s)?\b", 0.95),
        (r"\bsuggest(ion|s)?\b", 0.90),
        (r"\bbest\s+for\b", 0.85),
        (r"\bwhich\s+one\b", 0.85),
        (r"\bwhich\s+should\b", 0.85)
    ],
    BusinessIntent.PROBLEM_STATEMENT: [
        (r"\bslow\b", 0.75),
        (r"\bissue(s)?\b", 0.80),
        (r"\bproblem(s)?\b", 0.85),
        (r"\bchallenge(s)?\b", 0.85),
        (r"\bfriction\b", 0.80),
        (r"\bmanual\b", 0.75)
    ],
    BusinessIntent.REQUIREMENT_GATHERING: [
        (r"\bwe\s+have\b", 0.80),
        (r"\bour\s+team\b", 0.75),
        (r"\bemployees\b", 0.80),
        (r"\bhospitals\b", 0.80),
        (r"\bvolume\b", 0.75)
    ],
    BusinessIntent.OVERVIEW: [
        (r"\boverview\b", 0.95),
        (r"\babout\b", 0.85),
        (r"\bwhat\s+is\b", 0.85),
        (r"\bexplain\b", 0.80),
        (r"\bintroduction\b", 0.90)
    ],
    BusinessIntent.LEADERSHIP: [
        (r"\bleadership\b", 0.95),
        (r"\bfounder(s)?\b", 0.90),
        (r"\bceo\b", 0.90),
        (r"\bcto\b", 0.90),
        (r"\bcoo\b", 0.90),
        (r"\bexecutives\b", 0.85)
    ],
    BusinessIntent.CONTACT: [
        (r"\bcontact\b", 0.95),
        (r"\breach\b", 0.80),
        (r"\bemail\b", 0.85),
        (r"\bphone\b", 0.85),
        (r"\blocation\b", 0.80)
    ]
}

CONVERSATIONAL_INTENT_PATTERNS: Dict[ConversationalIntent, List[Tuple[str, float]]] = {
    ConversationalIntent.GREETING: [
        (r"^(hi|hello|hey|greetings|good\s+morning|good\s+afternoon)\b", 0.95)
    ],
    ConversationalIntent.GOODBYE: [
        (r"^(bye|goodbye|see\s+you|farewell)\b", 0.95)
    ],
    ConversationalIntent.CONFIRMATION: [
        (r"^(yes|yeah|sure|ok|okay|correct|yep)\b", 0.90)
    ],
    ConversationalIntent.CLARIFICATION: [
        (r"\bwhat\s+do\s+you\s+mean\b", 0.90),
        (r"\bcould\s+you\s+explain\b", 0.85)
    ],
    ConversationalIntent.CONTINUE_TOPIC: [
        (r"\btell\s+me\s+more\b", 0.90),
        (r"\bgo\s+on\b", 0.90),
        (r"\belaborate\b", 0.85),
        (r"\bwhat\s+else\b", 0.85)
    ]
}


class EnterpriseIntentEngine:
    """
    Enterprise-grade Intent Understanding Engine.
    Executes a 3-phase pipeline:
    Phase 1: Signal & Candidate Detection
    Phase 2: Candidate Ranking & Confidence Scoring
    Phase 3: Primary & Secondary Intent Selection
    """

    def normalize_query(self, query: str) -> str:
        """Applies typo corrections and basic normalization."""
        if not query:
            return ""
        q = query.lower().strip()
        
        # Replace typos
        words = q.split()
        fixed_words = [TYPO_CORRECTIONS.get(w, w) for w in words]
        q_fixed = " ".join(fixed_words)
        
        for typo, fix in TYPO_CORRECTIONS.items():
            q_fixed = re.sub(rf"\b{re.escape(typo)}\b", fix, q_fixed)
            
        return q_fixed

    def detect_signals(self, query: str, norm_query: str, context: Optional[ConversationContext]) -> List[Tuple[Union[BusinessIntent, ConversationalIntent], Signal]]:
        """
        Phase 1: Candidate Signal Detection.
        Extracts KeywordSignals from message text, plus MemorySignals/ConversationSignals from context.
        """
        detected: List[Tuple[Union[BusinessIntent, ConversationalIntent], Signal]] = []
        
        # 1. Message Keyword Signals for Business Intents
        for intent_enum, patterns in BUSINESS_INTENT_PATTERNS.items():
            for pat, weight in patterns:
                for match in re.finditer(pat, norm_query):
                    matched_str = match.group(0)
                    sig = Signal(
                        signal_type="KeywordSignal",
                        source=IntentSource.MESSAGE,
                        value=matched_str,
                        weight=weight
                    )
                    detected.append((intent_enum, sig))

        # 2. Message Keyword Signals for Conversational Intents
        for intent_enum, patterns in CONVERSATIONAL_INTENT_PATTERNS.items():
            for pat, weight in patterns:
                for match in re.finditer(pat, norm_query):
                    matched_str = match.group(0)
                    sig = Signal(
                        signal_type="KeywordSignal",
                        source=IntentSource.MESSAGE,
                        value=matched_str,
                        weight=weight
                    )
                    detected.append((intent_enum, sig))

        # 3. Memory & Context Dependent Signals
        if context:
            # Short / Context-dependent pricing follow-up: e.g. "What about pricing?" or "How much does it cost?"
            # If the current message has pricing keyword without explicit product entity, but active_entity_id exists in context
            if any(intent == BusinessIntent.PRICING for intent, _ in detected) and context.active_entity_id:
                detected.append((
                    BusinessIntent.PRICING,
                    Signal(
                        signal_type="MemorySignal",
                        source=IntentSource.MEMORY,
                        value=f"active_entity={context.active_entity_id}",
                        weight=0.90
                    )
                ))
            
            # Short follow-up queries: e.g. "Tell me more" or "What about security?"
            if re.search(r"\b(tell\s+me\s+more|what\s+about|how\s+about)\b", norm_query) and context.active_entity_id:
                detected.append((
                    ConversationalIntent.CONTINUE_TOPIC,
                    Signal(
                        signal_type="ConversationSignal",
                        source=IntentSource.CONVERSATION_CONTEXT,
                        value=f"continue_active_entity={context.active_entity_id}",
                        weight=0.85
                    )
                ))

        return detected

    def rank_candidates(self, detected_signals: List[Tuple[Union[BusinessIntent, ConversationalIntent], Signal]]) -> List[IntentCandidate]:
        """
        Phase 2: Intent Candidate Ranking.
        Aggregates signals per intent, calculates multi-faceted confidence, and constructs reasoning traces.
        """
        grouped: Dict[Union[BusinessIntent, ConversationalIntent], List[Signal]] = {}
        for intent_enum, sig in detected_signals:
            if intent_enum not in grouped:
                grouped[intent_enum] = []
            grouped[intent_enum].append(sig)

        candidates: List[IntentCandidate] = []
        
        for intent_enum, sigs in grouped.items():
            # Max signal weight represents raw detection confidence
            det_conf = max(s.weight for s in sigs)
            
            # Additional signals boost ranking confidence
            signal_count_bonus = min(0.15, (len(sigs) - 1) * 0.05)
            rank_conf = min(1.0, det_conf + signal_count_bonus)
            
            overall_conf = round((det_conf * 0.6) + (rank_conf * 0.4), 2)
            
            # Build Reasoning trace string from signal provenance
            signal_desc = []
            for s in sigs:
                signal_desc.append(f"{s.signal_type} '{s.value}' (source: {s.source.value}, weight: {s.weight})")
                
            reasoning_str = f"Inferred intent '{intent_enum.value}' based on: " + "; ".join(signal_desc)
            
            candidates.append(IntentCandidate(
                intent=intent_enum,
                signals=sigs,
                detection_confidence=round(det_conf, 2),
                ranking_confidence=round(rank_conf, 2),
                overall_confidence=overall_conf,
                reasoning=reasoning_str
            ))

        # Sort candidates descending by overall_confidence
        candidates.sort(key=lambda c: c.overall_confidence, reverse=True)
        return candidates

    def select_intents(self, ranked_candidates: List[IntentCandidate], raw_query: str, norm_query: str) -> EnterpriseIntentResult:
        """
        Phase 3: Primary and Secondary Intent Selection.
        Differentiates Business Intents from Conversational Intents.
        """
        business_candidates = [c for c in ranked_candidates if isinstance(c.intent, BusinessIntent)]
        conv_candidates = [c for c in ranked_candidates if isinstance(c.intent, ConversationalIntent)]

        # Primary Business Intent
        if business_candidates:
            primary_intent = business_candidates[0]
            secondary_intents = business_candidates[1:]
        else:
            # Fallback Unknown Business Intent candidate
            primary_intent = IntentCandidate(
                intent=BusinessIntent.UNKNOWN,
                signals=[],
                detection_confidence=0.0,
                ranking_confidence=0.0,
                overall_confidence=0.0,
                reasoning="No strong business intent keyword or context signals detected."
            )
            secondary_intents = []

        # Conversational Intent
        conversational_intent = conv_candidates[0] if conv_candidates else None

        return EnterpriseIntentResult(
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            conversational_intent=conversational_intent,
            raw_query=raw_query,
            normalized_query=norm_query
        )

    def analyze(self, query: str, context: Optional[ConversationContext] = None) -> EnterpriseIntentResult:
        """
        Main entrypoint executing the 3-phase Intent Understanding pipeline.
        """
        norm_query = self.normalize_query(query)
        signals = self.detect_signals(query, norm_query, context)
        candidates = self.rank_candidates(signals)
        result = self.select_intents(candidates, query, norm_query)
        
        logger.info(
            f"EnterpriseIntentEngine: Query '{query}' -> Primary: {result.primary_intent.intent.value} "
            f"(Conf: {result.primary_intent.overall_confidence}), "
            f"Secondaries: {[s.intent.value for s in result.secondary_intents]}"
        )
        return result


_intent_engine_instance: Optional[EnterpriseIntentEngine] = None

def get_enterprise_intent_engine() -> EnterpriseIntentEngine:
    global _intent_engine_instance
    if _intent_engine_instance is None:
        _intent_engine_instance = EnterpriseIntentEngine()
    return _intent_instance if '_intent_instance' in locals() else _intent_engine_instance
