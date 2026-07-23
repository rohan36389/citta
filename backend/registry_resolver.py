import re
import logging
from typing import Dict, Any, Tuple, Optional, List

logger = logging.getLogger(__name__)

def resolve_registry(
    query: str,
    resolved_entity_id: Optional[str],
    registry_index: Dict[str, Dict[str, Any]],
    knowledge_graph: Dict[str, Dict[str, Any]],
    disabled_registries: set
) -> Tuple[Optional[str], float]:
    """
    Registry Resolver:
    Inherits the registry type directly from the resolved entity's belongs_to node.
    If no entity is resolved, performs lightweight registry-level keyword matching.
    No duplicate entity alias logic.
    """
    import config
    if getattr(config, "USE_NEW_ENTITY_RESOLVER", True):
        # 1. Inherit from resolved entity belongs_to in KG
        if resolved_entity_id:
            node = knowledge_graph.get(resolved_entity_id)
            if node:
                belongs_to = node.get("belongs_to")
                if belongs_to and belongs_to.upper() not in [d.upper() for d in disabled_registries]:
                    logger.info(f"Registry resolved from entity '{resolved_entity_id}' belongs_to node: {belongs_to}")
                    return belongs_to, 1.0

        # 2. Lightweight registry fallback checks
        q_lower = query.lower().strip()
        
        # Exact keyword checks for registry categories
        registry_keywords = {
            "solutions": "SOLUTIONS",
            "solution": "SOLUTIONS",
            "products": "PRODUCTS",
            "product": "PRODUCTS",
            "services": "SERVICES",
            "service": "SERVICES",
            "leadership": "LEADERSHIP",
            "team": "LEADERSHIP",
            "contact": "CONTACT",
            "location": "LOCATION",
            "address": "LOCATION",
            "faq": "FAQ",
            "faqs": "FAQ",
            "case studies": "CASE_STUDIES",
            "case study": "CASE_STUDIES",
            "awards": "RECOGNITION",
            "award": "RECOGNITION",
            "recognition": "RECOGNITION"
        }
        
        # Word boundary match for lightweight keywords
        for kw, reg_type in registry_keywords.items():
            if re.search(r"\b" + re.escape(kw) + r"\b", q_lower):
                if reg_type.upper() not in [d.upper() for d in disabled_registries]:
                    return reg_type, 0.90
                    
        return None, 0.0

    # Legacy resolution
    if resolved_entity_id:
        node = knowledge_graph.get(resolved_entity_id)
        if node:
            belongs_to = node.get("belongs_to")
            if belongs_to and belongs_to.upper() not in [d.upper() for d in disabled_registries]:
                logger.info(f"Registry resolved from entity '{resolved_entity_id}' belongs_to node: {belongs_to}")
                return belongs_to, 1.0
                
    # Fallback to direct registry alias matching
    q_lower = query.lower().strip()
    best_registry = None
    best_score = 0.0
    
    for reg_type, reg_data in registry_index.items():
        if reg_type.lower() in disabled_registries or reg_data.get("metadata", {}).get("registry_id") in disabled_registries:
            continue
            
        meta = reg_data.get("metadata", {})
        aliases = meta.get("aliases", [])
        
        # Check direct registry type name
        if reg_type.lower() == q_lower:
            return reg_type, 1.0
            
        for alias in aliases:
            alias_clean = alias.lower().strip()
            if not alias_clean:
                continue
            if alias_clean == q_lower:
                return reg_type, 1.0
            elif re.search(rf"\b{re.escape(alias_clean)}\b", q_lower):
                score = 0.90
                if score > best_score:
                    best_score = score
                    best_registry = reg_type
                    
    return best_registry, best_score
