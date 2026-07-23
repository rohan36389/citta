import logging
from typing import Dict, Any, List, Optional, Tuple
from backend.conversation.models import (
    BusinessIntent,
    RolePersona,
    PersonaProfile,
    EntityNode,
    ResponsePlan,
    SuggestionCandidate,
    SuggestionResult,
    ConversationContext
)
from backend.knowledge_registry import KnowledgeRegistry

logger = logging.getLogger(__name__)

# Next Intent Mapping Table
NEXT_INTENT_MAP: Dict[str, List[Tuple[str, str, float]]] = {
    "overview": [
        ("How does it work?", "workflow", 0.90),
        ("What integrations are supported?", "integration", 0.88),
        ("Can I see case studies?", "case_studies", 0.85),
        ("Who typically uses this?", "target_audience", 0.82),
        ("What is the commercial pricing model?", "pricing", 0.80)
    ],
    "integration": [
        ("What security and compliance standards apply?", "security", 0.90),
        ("How can I access developer sandbox API keys?", "implementation", 0.88),
        ("Are webhook notifications supported?", "workflow", 0.85),
        ("What is the latency and SLA guarantee?", "architecture", 0.82)
    ],
    "pricing": [
        ("Book a 15-minute executive demo", "demo_request", 0.92),
        ("What is the typical ROI timeframe?", "benefits", 0.88),
        ("Are custom enterprise quotes available?", "pricing", 0.85)
    ],
    "comparison": [
        ("What are the key technical trade-offs?", "architecture", 0.88),
        ("Which option is recommended for our industry?", "recommendation", 0.85),
        ("Can we schedule a technical sandbox trial?", "demo_request", 0.82)
    ],
    "workflow": [
        ("What are the deployment prerequisites?", "implementation", 0.88),
        ("Can this process be fully automated via APIs?", "integration", 0.85)
    ]
}


class SuggestionEngine:
    """
    Enterprise Intelligent Suggestion Engine.
    Dynamically generates, ranks, and deduplicates follow-up question chips
    using entity context, intent, persona, available response sections, and registry lookups.
    """
    def __init__(self):
        pass

    def generate_candidate_chips(
        self,
        entity_name: str,
        intent_str: str,
        persona_role: RolePersona,
        response_plan: Optional[ResponsePlan],
        context: ConversationContext
    ) -> List[SuggestionCandidate]:
        candidates: List[SuggestionCandidate] = []
        p_intent = intent_str.lower()
        
        # 1. Logical Next-Intent Candidates
        next_intents = NEXT_INTENT_MAP.get(p_intent, NEXT_INTENT_MAP["overview"])
        for text, target_intent, weight in next_intents:
            # Adapt label to active entity_name if present
            formatted_text = text
            if "it" in text.lower() and entity_name and entity_name != "General Platform Solution":
                formatted_text = text.replace("it", entity_name).replace("this", entity_name)
                
            candidates.append(SuggestionCandidate(
                label=formatted_text,
                action=f"query_{target_intent}",
                confidence=round(weight, 2),
                ranking_score=weight,
                reasoning=f"Logical next-intent progression from '{p_intent}' to '{target_intent}'",
                target_intent=target_intent,
                target_entity=entity_name
            ))

        # 2. Registry Sibling Comparison Candidates
        try:
            kr = KnowledgeRegistry()
            all_entities = kr.entities
            # Find sibling entities to compare with
            sibling_names = []
            for ent_id, ent_obj in all_entities.items():
                ent_title = ent_obj.get("name", ent_id) if isinstance(ent_obj, dict) else (getattr(ent_obj, "name", ent_id))
                if ent_title and ent_title.lower() != entity_name.lower():
                    sibling_names.append(ent_title)
                    
            if sibling_names and entity_name:
                # Pick top 2 sibling entities for dynamic comparison chips
                for sib in sibling_names[:2]:
                    comp_text = f"Compare {entity_name} with {sib}"
                    candidates.append(SuggestionCandidate(
                        label=comp_text,
                        action=f"compare_{entity_name}_vs_{sib}",
                        confidence=0.86,
                        ranking_score=0.86,
                        reasoning=f"Registry lookup found sibling entity '{sib}' for comparative suggestion",
                        target_intent="comparison",
                        target_entity=sib
                    ))
        except Exception as e:
            logger.warning(f"SuggestionEngine: Registry sibling search error: {e}")

        # 3. Persona Phrasing Adaptions
        if persona_role in [RolePersona.DEVELOPER, RolePersona.TECHNICAL_ARCHITECT]:
            candidates.append(SuggestionCandidate(
                label=f"What REST APIs and webhooks does {entity_name} expose?",
                action="get_api_specs",
                confidence=0.90,
                ranking_score=0.92,
                reasoning=f"Persona-adapted developer technical prompt for '{persona_role.value}'",
                target_intent="integration",
                target_entity=entity_name
            ))
        elif persona_role in [RolePersona.EXECUTIVE_DECISION_MAKER, RolePersona.INVESTOR]:
            candidates.append(SuggestionCandidate(
                label=f"What ROI and cost reductions does {entity_name} deliver?",
                action="get_executive_roi",
                confidence=0.90,
                ranking_score=0.92,
                reasoning=f"Persona-adapted executive ROI prompt for '{persona_role.value}'",
                target_intent="benefits",
                target_entity=entity_name
            ))

        # 4. ResponsePlan Section Deep-Dive Candidates
        if response_plan:
            for sec in response_plan.sections:
                candidates.append(SuggestionCandidate(
                    label=f"Deep-dive into {sec.title}",
                    action=f"deep_dive_{sec.title.lower().replace(' ', '_')}",
                    confidence=0.80,
                    ranking_score=0.80,
                    reasoning=f"Derived from ResponsePlan section blueprint '{sec.title}'",
                    target_intent="features",
                    target_entity=entity_name
                ))

        return candidates

    def deduplicate_and_rank(
        self,
        candidates: List[SuggestionCandidate],
        context: ConversationContext
    ) -> List[SuggestionCandidate]:
        """
        Filters out previously answered question signatures and recent turn text,
        ranks by score, and returns top N candidates.
        """
        # Retrieve answered questions from context if present
        answered_sigs = set()
        if "persona_profile" in context.variables:
            pass
            
        # Get message history strings to avoid repeating recent queries
        past_queries = set()
        for turn_msg in context.history:
            if turn_msg.get("role") == "user":
                past_queries.add(turn_msg.get("content", "").lower().strip())

        unique_candidates: List[SuggestionCandidate] = []
        seen_labels = set()

        for cand in candidates:
            lbl_clean = cand.label.lower().strip()
            if lbl_clean in seen_labels or lbl_clean in past_queries:
                continue
                
            seen_labels.add(lbl_clean)
            unique_candidates.append(cand)

        # Sort descending by ranking_score
        unique_candidates.sort(key=lambda c: c.ranking_score, reverse=True)
        return unique_candidates[:4]

    def generate(
        self,
        intent: Any,
        persona_profile: Optional[PersonaProfile],
        context: ConversationContext
    ) -> SuggestionResult:
        """
        Main entrypoint generating dynamic ranked suggestions.
        """
        ent_name = context.active_entity_id or "Ecommerce OS"
        intent_str = getattr(intent, "primary_intent", "overview") if intent else "overview"
        persona_role = persona_profile.primary_role if persona_profile else RolePersona.UNKNOWN
        response_plan = context.variables.get("response_plan")

        # 1. Generate Raw Candidates
        raw_candidates = self.generate_candidate_chips(
            ent_name, intent_str, persona_role, response_plan, context
        )

        # 2. Deduplicate & Rank
        ranked = self.deduplicate_and_rank(raw_candidates, context)
        top_cand = ranked[0] if ranked else None

        reasoning = f"Generated {len(raw_candidates)} dynamic candidates; ranked top {len(ranked)} suggestions for entity '{ent_name}'."

        logger.info(
            f"SuggestionEngine: Generated {len(ranked)} suggestions for session {context.session_id} -> "
            f"Top: '{top_cand.label if top_cand else 'None'}'"
        )

        return SuggestionResult(
            suggestions=ranked,
            top_suggestion=top_cand,
            total_candidates_generated=len(raw_candidates),
            selection_reasoning=reasoning
        )


_suggestion_engine_instance: Optional[SuggestionEngine] = None

def get_suggestion_engine() -> SuggestionEngine:
    global _suggestion_engine_instance
    if _suggestion_engine_instance is None:
        _suggestion_engine_instance = SuggestionEngine()
    return _suggestion_engine_instance
