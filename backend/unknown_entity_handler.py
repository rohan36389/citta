import re
import logging
from typing import Dict, Any, List, Optional
from orchestration_context import OrchestrationContext
from knowledge_registry import get_registry

logger = logging.getLogger(__name__)

KNOWN_TAXONOMY_TERMS = {
    "education os", "pharma os", "real estate os", "smart cities os", "enterprise ai os", "e-commerce os", "ecommerce os",
    "whatsapp marketing platform", "influencer marketing platform", "data engineering", "enterprise & agentic ai", "agentic ai",
    "ai strategy & advisory", "ai strategy", "martech 360", "jewellery brand", "fmcg brand", "spices export", "cittaai",
    "cittaai.", "cittaai's", "citta"
}

GENERIC_ENTITIES = {"company_info", "faq_general"}

class UnknownEntityHandler:
    def __init__(self):
        self.reg = get_registry()

    def check_unknown_entity(self, ctx: OrchestrationContext) -> OrchestrationContext:
        # Skip if resolved entity is a specific non-generic entity
        if ctx.resolved_entity_id and ctx.resolved_entity_id not in GENERIC_ENTITIES:
            return ctx
        if ctx.is_out_of_domain or ctx.is_ambiguous or ctx.is_general_catalog_query:
            return ctx

        q_lower = ctx.normalized_query.lower().strip()

        prefixes = ["tell me about ", "explain ", "what is ", "about "]
        for p in prefixes:
            if q_lower.startswith(p):
                candidate = q_lower[len(p):].strip().rstrip(".")
                if candidate and candidate not in KNOWN_TAXONOMY_TERMS:
                    ctx.is_unknown_entity = True
                    ctx.unknown_entity_name = candidate.title()
                    ctx.resolved_entity_id = None
                    ctx.add_trace(
                        stage="UnknownEntityHandler",
                        result=f"Unknown entity detected -> {candidate.title()}",
                        reason="Query references non-existent catalog offering"
                    )
                    return ctx

        return ctx

    def build_unknown_entity_response(self, ctx: OrchestrationContext) -> Dict[str, Any]:
        ent_name = ctx.unknown_entity_name or "The requested offering"
        
        response_text = (
            f"**{ent_name}** is not part of the current **CittaAI** catalog.\n\n"
            f"Here are the flagship enterprise solutions and services currently available:\n\n"
            f"• **Education OS**: Comprehensive campus management, automated admissions, and student lifecycle analytics.\n"
            f"• **Pharma OS**: Clinical trial data pipelines, compliance tracking, and supply chain intelligence.\n"
            f"• **Real Estate OS**: Automated lead scoring, tenant management, and property valuation engines.\n"
            f"• **Smart Cities OS**: Urban IoT telemetry, traffic optimization, and municipal resource allocation.\n"
            f"• **Enterprise AI OS**: Multi-agent orchestration, local LLM fine-tuning, and corporate knowledge management.\n"
            f"• **E-Commerce OS**: Personalized recommendations, dynamic pricing, and automated inventory sync."
        )

        return {
            "text": response_text,
            "source": "Catalog Taxonomy Guardrail",
            "verified": True,
            "confidence": 1.0,
            "suggestions": ["Tell me about Education OS", "Explain Pharma OS", "What products do you offer?"],
            "metrics": {
                "resolved_registry": "CATALOG_TAXONOMY",
                "resolved_entity": "NONE",
                "resolved_section": "NONE"
            }
        }

_unknown_handler_instance = None

def get_unknown_entity_handler() -> UnknownEntityHandler:
    global _unknown_handler_instance
    if _unknown_handler_instance is None:
        _unknown_handler_instance = UnknownEntityHandler()
    return _unknown_handler_instance
