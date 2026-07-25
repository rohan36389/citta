import time
import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple

from orchestration_context import OrchestrationContext, ExecutionStrategy, EnterpriseIntent
from conversation_context_resolver import get_conversation_context_resolver
from phase2_intent_classifier import get_phase2_intent_classifier
from out_of_domain_detector import get_out_of_domain_detector
from execution_strategy import get_execution_strategy_selector
from ambiguity_detector import get_ambiguity_detector
from unknown_entity_handler import get_unknown_entity_handler
from knowledge_registry import get_registry
from entity_resolver import resolve_entity_dynamic

logger = logging.getLogger(__name__)

# General Catalog Query Patterns
GENERAL_CATALOG_PATTERNS = [
    "what products do you offer", "what products", "list products", "show products", "our products", "products offered",
    "what services do you offer", "what services", "list services", "show services", "our services", "services offered",
    "what are the services provided", "services provided", "srevices provided", "what are the srevices provided",
    "what services are provided", "srevices", "serivces", "services",
    "what solutions do you offer", "what solutions", "list solutions", "show solutions", "our solutions", "solutions offered",
    "what do you offer", "list all offerings", "show all solutions", "what platforms"
]

GENERIC_ENTITIES = {"company_info", "faq_general", "contact", "location"}

def check_general_catalog_query(query: str) -> bool:
    q_lower = query.lower().strip()
    if q_lower in GENERAL_CATALOG_PATTERNS:
        return True
    return any(p in q_lower for p in GENERAL_CATALOG_PATTERNS)

class Phase2Orchestrator:
    def __init__(self):
        self.context_resolver = get_conversation_context_resolver()
        self.intent_classifier = get_phase2_intent_classifier()
        self.ood_detector = get_out_of_domain_detector()
        self.strategy_selector = get_execution_strategy_selector()
        self.ambiguity_detector = get_ambiguity_detector()
        self.unknown_handler = get_unknown_entity_handler()
        self.reg = get_registry()

    def _extract_all_entities(self, query: str) -> List[str]:
        q_lower = query.lower().strip()
        matched = []
        
        # Check canonical entity names
        for ent_id, ent_data in self.reg.entities.items():
            if ent_id in GENERIC_ENTITIES:
                continue
            name = (ent_data.get("name") or ent_data.get("title") or "").lower()
            if name and (name in q_lower or (len(name) > 4 and re.search(r"\b" + re.escape(name) + r"\b", q_lower))):
                matched.append(ent_id)

        # Check aliases for non-generic entities
        for alias, ent_id in self.reg.aliases.items():
            if ent_id in GENERIC_ENTITIES:
                continue
            if len(alias) > 3 and alias in q_lower and ent_id in self.reg.entities:
                if ent_id not in matched:
                    matched.append(ent_id)

        return list(dict.fromkeys(matched))

    def orchestrate(self, session_id: str, original_query: str, normalized_query: str) -> OrchestrationContext:
        start_time = time.time()
        
        # 1. Initialize OrchestrationContext
        ctx = OrchestrationContext(
            session_id=session_id,
            original_query=original_query,
            normalized_query=normalized_query
        )
        ctx.add_trace("Initialization", "SUCCESS", f"Context created for query: '{original_query}'")

        # 2. Entity Resolution
        all_matched_entities = self._extract_all_entities(normalized_query)
        detected_entity_id, conf, matched_alias, _ = resolve_entity_dynamic(
            query=normalized_query,
            registry_entities=self.reg.entities,
            entity_lookup=self.reg.entity_lookup,
            alias_index=self.reg.aliases,
            unified_vocabulary=self.reg.unified_vocabulary
        )
        
        ctx.add_trace(
            stage="EntityResolver",
            result=str(detected_entity_id or "None"),
            reason=f"Matched via {matched_alias or 'direct/fuzzy lookup'} (conf={conf})"
        )

        # 3. Conversation & Session Context Resolver
        ctx = self.context_resolver.resolve_context(
            ctx=ctx,
            detected_entity_id=detected_entity_id,
            detected_entities=all_matched_entities
        )
        
        if ctx.resolved_entity_id and ctx.resolved_entity_id in self.reg.entities:
            ent_data = self.reg.entities[ctx.resolved_entity_id]
            ctx.resolved_entity_name = ent_data.get("name") or ent_data.get("title") or ctx.resolved_entity_id
            ctx.resolved_category = ent_data.get("category") or ent_data.get("type")

        # 4. General Catalog Intent Check
        ctx.is_general_catalog_query = check_general_catalog_query(normalized_query)
        if ctx.is_general_catalog_query:
            ctx.add_trace(
                stage="GeneralCatalogCheck",
                result="TRUE",
                reason="Query asks for broad category/offering listing"
            )

        # 5. Out-of-Domain Check (ONLY if no entity AND not general catalog query)
        if not ctx.resolved_entity_id and not ctx.is_general_catalog_query:
            is_ood, ood_msg = self.ood_detector.is_out_of_domain(normalized_query)
            if is_ood:
                ctx.is_out_of_domain = True
                ctx.response_text = ood_msg
                ctx.add_trace(
                    stage="OutOfDomainDetector",
                    result="OUT_OF_DOMAIN",
                    reason="Query identified as outside business domain"
                )

        # 6. Intent Classification
        ctx.intent = self.intent_classifier.classify(normalized_query)
        ctx.add_trace("IntentClassifier", ctx.intent, f"Intent classified as '{ctx.intent}'")

        # 7. Ambiguity & Unknown Entity Checks
        if not ctx.is_out_of_domain:
            ctx = self.ambiguity_detector.check_ambiguity(ctx)
            ctx = self.unknown_handler.check_unknown_entity(ctx)

        # 8. Execution Strategy Selector
        ctx = self.strategy_selector.select_strategy(ctx)

        # 9. Update Context State Memory
        self.context_resolver.update_state_after_response(ctx)

        latency_ms = round((time.time() - start_time) * 1000.0, 2)
        ctx.metrics["latency_ms"] = latency_ms
        ctx.metrics["decision_trace"] = ctx.decision_trace
        ctx.metrics["execution_strategy"] = ctx.execution_strategy.value
        ctx.metrics["intent"] = ctx.intent
        ctx.metrics["resolved_entity"] = ctx.resolved_entity_id or "NONE"
        ctx.metrics["resolved_section"] = ctx.section or "NONE"

        return ctx

_orchestrator_instance = None

def get_phase2_orchestrator() -> Phase2Orchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Phase2Orchestrator()
    return _orchestrator_instance
