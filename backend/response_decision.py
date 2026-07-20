import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Core Decision Cases mapping
RULES = {
    "DIRECT_CATALOG": {
        "allow_llm": False,
        "allow_navigation": True,
        "suggestions": "contextual",
        "default_text": None,
    },
    "DIRECT_LOOKUP": {
        "allow_llm": True,  # Allow LLM to format the retrieved structured details
        "allow_navigation": True,
        "suggestions": "contextual",
        "default_text": None,
    },
    "CASE_1": {
        "allow_llm": True,
        "allow_navigation": True,
        "suggestions": "contextual",
        "default_text": None,
    },
    "CASE_2": {
        "allow_llm": False,
        "allow_navigation": True,
        "suggestions": "generic",
        "default_text": (
            "I found a relevant CittaAI page for this topic, but its detailed content "
            "hasn't been added to the chatbot's knowledge base yet. You can explore the "
            "page below for the latest information."
        ),
    },
    "CASE_3": {
        "allow_llm": False,
        "allow_navigation": False,
        "suggestions": "generic",
        "default_text": (
            "I couldn't find verified information regarding that request. "
            "Would you like to contact our team or book a strategy call?"
        ),
    },
    "CASE_4": {
        "allow_llm": True,
        "allow_navigation": True,
        "suggestions": "generic",
        "default_text": None,
    }
}

def make_response_decision(
    query: str,
    intent: str,
    strategy: str,
    resolved_entity_id: Optional[str],
    retrieved_chunks: List[Dict[str, Any]],
    confidence_score: float,
    confidence_threshold: float,
    unindexed_routes: Dict[str, str]
) -> Dict[str, Any]:
    """
    Evaluates query planning strategy, resolved entity, and RAG retrieval confidence
    to decide on direct responses, catalog actions, LLM formatting, or low-confidence fallbacks.
    """
    normalized_q = query.lower().strip()
    normalized_q = re.sub(r"[^\w\s\-]", "", normalized_q)
    query_tokens = set(normalized_q.split())

    # 1. Direct Catalog Listing
    if strategy == "Catalog":
        logger.info("Decision: DIRECT_CATALOG selected (Bypassing LLM)")
        decision = RULES["DIRECT_CATALOG"].copy()
        decision["case"] = "DIRECT_CATALOG"
        # Setup catalog redirects
        if intent == "LIST_PRODUCTS":
            decision["redirect"] = "/products/whatsapp-marketing"
        elif intent == "LIST_SOLUTIONS":
            decision["redirect"] = "/solutions/ecommerce-os"
        else:
            decision["redirect"] = "/services"
        decision["section"] = "hero"
        return decision

    # 2. Case_2 Check: Check if query matches an unindexed route (label matches keywords)
    matched_route = None
    for route, label in unindexed_routes.items():
        label_clean = label.lower().strip()
        label_tokens = set(label_clean.split())
        if label_clean in normalized_q or (label_tokens and label_tokens.issubset(query_tokens)):
            matched_route = route
            break
            
    if matched_route:
        logger.info(f"Decision: CASE_2 (Unindexed page) -> {matched_route}")
        decision = RULES["CASE_2"].copy()
        decision["case"] = "CASE_2"
        decision["redirect"] = matched_route
        decision["section"] = None
        return decision

    # 3. Direct Entity Lookup
    if strategy == "Lookup" and resolved_entity_id:
        logger.info(f"Decision: DIRECT_LOOKUP (Structured Entity: {resolved_entity_id})")
        decision = RULES["DIRECT_LOOKUP"].copy()
        decision["case"] = "DIRECT_LOOKUP"
        
        # Link direct route redirect
        from knowledge_registry import get_registry
        reg = get_registry()
        ent = reg.get_entity(resolved_entity_id)
        if ent and ent.get("route"):
            decision["redirect"] = ent["route"]
            decision["section"] = "hero"
        else:
            decision["redirect"] = None
            decision["section"] = None
        return decision

    # 4. Case_3 check: Zero retrieved chunks for RAG or Graph queries
    if len(retrieved_chunks) == 0 and strategy not in ["Graph Traversal", "Comparison"]:
        logger.info("Decision: CASE_3 (Zero RAG retrieval results)")
        decision = RULES["CASE_3"].copy()
        decision["case"] = "CASE_3"
        decision["redirect"] = None
        decision["section"] = None
        return decision

    # 5. Hybrid retrieval evaluation for CASE_1 vs CASE_4
    STOPWORDS = {"what", "is", "the", "in", "and", "a", "for", "to", "of", "on", "with", "at", "by", "an", "this", "that", "it", "its", "are", "you", "your", "we", "our", "about", "how", "does", "do", "can", "tell", "me", "show", "give", "today", "who", "when", "why", "where"}
    meaningful_q_tokens = {t for t in query_tokens if t not in STOPWORDS}
    
    has_meaningful_overlap = False
    if retrieved_chunks and meaningful_q_tokens:
        top_content = retrieved_chunks[0]["content"].lower()
        for token in meaningful_q_tokens:
            if re.search(r"\b" + re.escape(token) + r"\b", top_content):
                has_meaningful_overlap = True
                break
    else:
        has_meaningful_overlap = True

    # CASE_1: Confident retrieval matches threshold (with overlap confirmation or very high score)
    if confidence_score >= confidence_threshold:
        if has_meaningful_overlap or confidence_score >= 0.60:
            logger.info(f"Decision: CASE_1 (Confident match: {confidence_score:.4f} >= {confidence_threshold})")
            decision = RULES["CASE_1"].copy()
            decision["case"] = "CASE_1"
            top_meta = retrieved_chunks[0].get("metadata", {}) if retrieved_chunks else {}
            decision["redirect"] = top_meta.get("url") or top_meta.get("page")
            decision["section"] = top_meta.get("section")
            return decision
        else:
            logger.info(f"Decision: Spurious CASE_1 match detected. Downgrading to CASE_4.")
            decision = RULES["CASE_4"].copy()
            decision["case"] = "CASE_4"
            decision["allow_navigation"] = False
            decision["redirect"] = None
            decision["section"] = None
            return decision

    # CASE_4: Low confidence match (ambiguous or partial context)
    logger.info(f"Decision: CASE_4 (Low confidence: {confidence_score:.4f} < {confidence_threshold})")
    decision = RULES["CASE_4"].copy()
    decision["case"] = "CASE_4"
    if retrieved_chunks and (has_meaningful_overlap or confidence_score >= 0.50):
        top_meta = retrieved_chunks[0].get("metadata", {})
        decision["redirect"] = top_meta.get("url") or top_meta.get("page")
        decision["section"] = top_meta.get("section")
    else:
        decision["allow_navigation"] = False
        decision["redirect"] = None
        decision["section"] = None
    return decision
