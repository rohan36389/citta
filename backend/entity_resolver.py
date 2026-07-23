import re
import logging
from typing import Dict, Any, Tuple, Optional, List

logger = logging.getLogger(__name__)

# List of common pronouns that indicate follow-up questions referencing active context
CONTEXT_PRONOUNS = [
    r"\bit\b", r"\bits\b", r"\bthis\b", r"\bthat\b", r"\btheir\b", r"\bthose\b", r"\bthese\b",
    r"\bthe\s+tool\b", r"\bthe\s+platform\b", 
    r"\bthe\s+service\b", r"\bthe\s+solution\b", r"\bthem\b",
    r"\bdesigned\s+for\b", r"\btarget\s+audience\b", r"\bintended\s+users\b", r"\bwho\s+is\s+it\s+for\b"
]

def contains_pronouns(query: str) -> bool:
    q_lower = query.lower()
    return any(re.search(p, q_lower) for p in CONTEXT_PRONOUNS)

def resolve_entity_dynamic(
    query: str,
    registry_entities: Dict[str, Dict[str, Any]],
    entity_lookup: Optional[Dict[str, str]] = None,
    alias_index: Optional[Dict[str, str]] = None,
    unified_vocabulary: Optional[Dict[str, str]] = None,
    active_entity: Optional[str] = None,
    fuzz_threshold: float = 80.0
) -> Tuple[Optional[str], float, Optional[str], Optional[Dict[str, Any]]]:
    """
    Entity Resolver:
    Resolves the canonical entity ID using the single canonical entity_lookup and strict precedence order.
    Supports USE_NEW_ENTITY_RESOLVER rollout feature flag wrapping new core.entity_resolver.
    """
    import config
    if getattr(config, "USE_NEW_ENTITY_RESOLVER", True):
        import core.entity_resolver as core_resolver
        res = core_resolver.resolve(query)
        # Handle context pronoun override if new resolver didn't find one but pronouns match
        if not res["entity_id"] and active_entity and contains_pronouns(query):
            logger.info(f"Re-using active entity from context pronouns: {active_entity}")
            return active_entity, 1.0, "active_context_pronoun", None
        return res["entity_id"], res["entity_confidence"], res["matched_alias"], None

    if not registry_entities:
        return None, 0.0, None, None
        
    q_lower = query.lower().strip()
    alias_index = alias_index or {}
    unified_vocabulary = unified_vocabulary or {}
    
    # If entity_lookup is not provided, build it dynamically from supplied dictionaries
    if entity_lookup is None:
        lookup = {}
        for ent_id, ent in registry_entities.items():
            lookup[ent_id.lower()] = ent_id
            lookup[ent_id.lower().replace("_", " ")] = ent_id
            name = ent.get("name") or ent.get("title")
            if name:
                lookup[name.lower().strip()] = ent_id
            for a in ent.get("aliases", []):
                lookup[str(a).lower().strip()] = ent_id
        for a_key, target in alias_index.items():
            if target in registry_entities:
                lookup[a_key.lower().strip()] = target
        for v_key, target in unified_vocabulary.items():
            if target in registry_entities:
                lookup[v_key.lower().strip()] = target
        entity_lookup = lookup

    # Pronoun check for Active Context Memory
    if active_entity and contains_pronouns(q_lower):
        active_ent_data = registry_entities.get(active_entity)
        if active_ent_data:
            logger.info(f"Re-using active entity from context pronouns: {active_entity}")
            return active_entity, 1.0, "active_context_pronoun", None

    # Step 1: Exact ID match
    for ent_id in registry_entities.keys():
        ent_id_lower = ent_id.lower()
        if ent_id_lower == q_lower or ent_id_lower.replace("_", " ") == q_lower:
            return ent_id, 1.0, ent_id, None

    # Step 2: Exact Name match
    for ent_id, ent in registry_entities.items():
        name = ent.get("name") or ent.get("title")
        if name and name.lower().strip() == q_lower:
            return ent_id, 1.0, name, None

    # Step 3: Entity Name Substring Match (whole-word boundary check)
    for ent_id, ent in registry_entities.items():
        name = ent.get("name") or ent.get("title")
        if name:
            name_lower = name.lower().strip()
            # If name is substring of query, or query is substring of name (with boundary)
            if re.search(rf"\b{re.escape(name_lower)}\b", q_lower) or re.search(rf"\b{re.escape(q_lower)}\b", name_lower):
                if len(q_lower) > 3:  # avoid matching extremely short query fragments like "os"
                    return ent_id, 0.95, name, None

    # Step 4: Canonical Entity Lookup Match (sorted by length descending for longest phrase precedence)
    sorted_lookup_keys = sorted(entity_lookup.keys(), key=lambda k: len(k), reverse=True)
    for alias_key in sorted_lookup_keys:
        target_ent_id = entity_lookup[alias_key]
        alias_lower = alias_key.lower().strip()
        if target_ent_id in registry_entities and alias_lower:
            if alias_lower == q_lower or re.search(rf"\b{re.escape(alias_lower)}\b", q_lower):
                score = 0.95 if len(alias_lower) > 5 else 0.90
                return target_ent_id, score, alias_key, None

    # Step 5: RapidFuzz Match (using canonical entity_lookup)
    try:
        from rapidfuzz import process, fuzz
        candidate_strings = list(entity_lookup.keys())
        match = process.extractOne(q_lower, candidate_strings, scorer=fuzz.WRatio)
        if match and match[1] >= fuzz_threshold:
            best_str = match[0]
            matched_ent_id = entity_lookup[best_str]
            if matched_ent_id in registry_entities:
                return matched_ent_id, match[1] / 100.0, best_str, None
    except Exception as e:
        logger.warning(f"RapidFuzz failed in resolve_entity_dynamic: {e}")

    # Step 6: Semantic / Context boost fallback
    candidates = []
    for ent_id, ent in registry_entities.items():
        context_score = 0.0
        if active_entity and active_entity.lower() == ent_id.lower():
            context_score = 1.0
            
        overall_score = context_score * 0.20
        if overall_score > 0.0:
            candidates.append({
                "id": ent_id,
                "score": overall_score,
                "alias": ent_id,
                "entity": ent
            })
            
    if candidates:
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top = candidates[0]
        if top["score"] >= 0.60:
            return top["id"], top["score"], top["alias"], None
            
    return None, 0.0, None, None
