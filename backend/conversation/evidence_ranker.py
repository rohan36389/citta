import logging
from typing import List, Dict, Any
from backend.conversation.reasoning_packet import Evidence

logger = logging.getLogger(__name__)

class EvidenceRanker:
    """
    Enterprise Evidence Ranker.
    Filters and ranks retrieved knowledge sections based on query context and ResponseIntent,
    eliminating prompt noise before LLM synthesis.
    """
    def __init__(self):
        pass

    def rank_evidence(
        self,
        raw_evidence: List[Evidence],
        response_intent: str,
        user_query: str
    ) -> List[Evidence]:
        if not raw_evidence:
            return []

        intent_lower = response_intent.lower()
        query_lower = user_query.lower()

        ranked: List[Evidence] = []
        for ev in raw_evidence:
            score = ev.confidence
            sec_lower = ev.section.lower()

            # Boost relevant sections based on response_intent
            if intent_lower == "workflow" or "how" in query_lower:
                if any(k in sec_lower for k in ["workflow", "mechanics", "implementation", "process"]):
                    score += 0.4
            elif intent_lower == "benefits" or "benefit" in query_lower:
                if any(k in sec_lower for k in ["benefit", "value", "impact", "roi"]):
                    score += 0.4
            elif intent_lower == "security" or "security" in query_lower:
                if any(k in sec_lower for k in ["security", "compliance", "encryption", "auth"]):
                    score += 0.4
            elif intent_lower == "comparison" or "compare" in query_lower:
                if any(k in sec_lower for k in ["overview", "capability", "matrix"]):
                    score += 0.3

            # De-prioritize generic FAQ or disclaimers if specific intent requested
            if intent_lower in ["workflow", "security", "comparison"] and "faq" in sec_lower:
                score -= 0.2

            ev_ranked = Evidence(
                id=ev.id,
                section=ev.section,
                text=ev.text,
                confidence=round(score, 2),
                source_file=ev.source_file,
                priority=ev.priority,
                source_type=ev.source_type,
                entity_id=ev.entity_id,
                timestamp=ev.timestamp
            )
            ranked.append(ev_ranked)

        # Sort by confidence descending
        ranked.sort(key=lambda e: e.confidence, reverse=True)
        
        # Top 5 ranked evidence sections
        selected = ranked[:5]
        logger.info(f"EvidenceRanker: Filtered {len(raw_evidence)} raw evidence items down to top {len(selected)} sections.")
        return selected


_global_evidence_ranker = None

def get_evidence_ranker() -> EvidenceRanker:
    global _global_evidence_ranker
    if _global_evidence_ranker is None:
        _global_evidence_ranker = EvidenceRanker()
    return _global_evidence_ranker
