import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from backend.conversation.models import (
    RolePersona,
    RelationshipPersona,
    PersonaSignal,
    CommunicationPreferences,
    PersonaProfile,
    ConversationContext
)

logger = logging.getLogger(__name__)

# Terminology & Keyword Dictionary Patterns
ROLE_TERMINOLOGY_PATTERNS: Dict[RolePersona, List[Tuple[str, float]]] = {
    RolePersona.DEVELOPER: [
        (r"\bapi(s)?\b", 0.90),
        (r"\bsdk(s)?\b", 0.90),
        (r"\bcode\b", 0.85),
        (r"\bwebhook(s)?\b", 0.90),
        (r"\boauth\b", 0.90),
        (r"\bendpoint(s)?\b", 0.90),
        (r"\bjson\b", 0.80),
        (r"\bpython\b", 0.80),
        (r"\bscript\b", 0.75),
        (r"\btoken(s)?\b", 0.75)
    ],
    RolePersona.TECHNICAL_ARCHITECT: [
        (r"\barchitectur(e|al)\b", 0.95),
        (r"\bcto\b", 0.90),
        (r"\btech\s+stack\b", 0.90),
        (r"\binfrastructure\b", 0.85),
        (r"\bscalabilit(y|ies)\b", 0.90),
        (r"\bkubernetes\b", 0.85),
        (r"\bcontainer(s)?\b", 0.85),
        (r"\bsecurity\b", 0.75),
        (r"\blatency\b", 0.85),
        (r"\bthroughput\b", 0.85)
    ],
    RolePersona.EXECUTIVE_DECISION_MAKER: [
        (r"\broi\b", 0.95),
        (r"\bceo\b", 0.90),
        (r"\bcio\b", 0.90),
        (r"\barr\b", 0.90),
        (r"\brevenue\b", 0.90),
        (r"\bstrategic\b", 0.85),
        (r"\bbusiness\s+impact\b", 0.90),
        (r"\bcost\s+reduction\b", 0.85),
        (r"\bcommercial\b", 0.80),
        (r"\bexpansion\b", 0.75)
    ],
    RolePersona.BUSINESS_FUNCTIONAL: [
        (r"\bfunctional\b", 0.85),
        (r"\brequirement(s)?\b", 0.85),
        (r"\banalyst\b", 0.90),
        (r"\bproduct\s+manager\b", 0.90),
        (r"\bfeature\s+matrix\b", 0.85),
        (r"\bdashboard(s)?\b", 0.80),
        (r"\breporting\b", 0.80)
    ],
    RolePersona.OPERATIONS: [
        (r"\boperation(s)?\b", 0.90),
        (r"\bcoo\b", 0.90),
        (r"\bprocess(es)?\b", 0.80),
        (r"\befficiency\b", 0.85),
        (r"\bfriction\b", 0.80),
        (r"\blogistics\b", 0.85),
        (r"\bsupply\s+chain\b", 0.85)
    ],
    RolePersona.MARKETING: [
        (r"\bmarketing\b", 0.90),
        (r"\bcmo\b", 0.90),
        (r"\bcampaign(s)?\b", 0.90),
        (r"\bcac\b", 0.90),
        (r"\bconversion\s+rate\b", 0.90),
        (r"\b retention\b", 0.85),
        (r"\bacquisition\b", 0.85)
    ],
    RolePersona.ACADEMIC_STUDENT: [
        (r"\bstudent\b", 0.95),
        (r"\buniversity\b", 0.90),
        (r"\bschool\b", 0.85),
        (r"\bproject\b", 0.70),
        (r"\bexplain\s+simply\b", 0.85),
        (r"\bbeginner\b", 0.85),
        (r"\bnew\s+to\s+ai\b", 0.85)
    ],
    RolePersona.RECRUITER: [
        (r"\brecruiter\b", 0.95),
        (r"\bhiring\b", 0.90),
        (r"\bcareers\b", 0.90),
        (r"\bjob\s+opening(s)?\b", 0.95),
        (r"\bteam\s+culture\b", 0.85)
    ],
    RolePersona.INVESTOR: [
        (r"\binvestor\b", 0.95),
        (r"\bvc\b", 0.90),
        (r"\bfunding\b", 0.90),
        (r"\bvaluation\b", 0.90),
        (r"\bmarket\s+size\b", 0.85)
    ]
}

# Negative Signal Patterns
NEGATIVE_ROLE_PATTERNS: Dict[RolePersona, List[Tuple[str, float]]] = {
    RolePersona.DEVELOPER: [
        (r"\bi\s+don'?t\s+know\s+programming\b", -0.90),
        (r"\bnon-technical\b", -0.85),
        (r"\bexplain\s+simply\b", -0.60),
        (r"\bno\s+code\b", -0.70)
    ],
    RolePersona.TECHNICAL_ARCHITECT: [
        (r"\bnon-technical\b", -0.90),
        (r"\bi\s+don'?t\s+know\s+programming\b", -0.85),
        (r"\bbeginner\b", -0.70)
    ],
    RolePersona.EXECUTIVE_DECISION_MAKER: [
        (r"\bi\s+am\s+a\s+student\b", -0.95),
        (r"\bbeginner\b", -0.60)
    ]
}

# Relationship Persona Patterns
RELATIONSHIP_PATTERNS: Dict[RelationshipPersona, List[Tuple[str, float]]] = {
    RelationshipPersona.EXISTING_CUSTOMER: [
        (r"\balready\s+use(d|s|ing)?\b", 0.95),
        (r"\bour\s+account\b", 0.90),
        (r"\bour\s+deployment\b", 0.90),
        (r"\bcurrent\s+customer\b", 0.95),
        (r"\bsupport\s+ticket\b", 0.90),
        (r"\bupgrade\s+our\b", 0.85)
    ],
    RelationshipPersona.PROSPECTIVE_CUSTOMER: [
        (r"\bevaluat(e|ing)\b", 0.85),
        (r"\blooking\s+for\b", 0.80),
        (r"\bconsidering\b", 0.80),
        (r"\bpricing\b", 0.70),
        (r"\bdemo\b", 0.75)
    ],
    RelationshipPersona.PARTNER: [
        (r"\bpartner(ship)?\b", 0.90),
        (r"\breseller\b", 0.90),
        (r"\bintegration\s+partner\b", 0.90)
    ]
}


class TerminologyProvider:
    """Extracts positive and negative terminology signals from user queries."""
    def extract_signals(self, query: str, turn: int) -> List[PersonaSignal]:
        signals: List[PersonaSignal] = []
        q = query.lower()
        
        # Positive role signals
        for role, patterns in ROLE_TERMINOLOGY_PATTERNS.items():
            for pat, weight in patterns:
                if re.search(pat, q):
                    m = re.search(pat, q)
                    matched_text = m.group(0) if m else pat
                    signals.append(PersonaSignal(
                        provider="TerminologyProvider",
                        feature=f"Matched term '{matched_text}' for {role.value}",
                        weight=weight,
                        source_turn=turn
                    ))

        # Negative role signals
        for role, neg_patterns in NEGATIVE_ROLE_PATTERNS.items():
            for pat, weight in neg_patterns:
                if re.search(pat, q):
                    m = re.search(pat, q)
                    matched_text = m.group(0) if m else pat
                    signals.append(PersonaSignal(
                        provider="TerminologyProvider",
                        feature=f"Contradictory phrase '{matched_text}' against {role.value}",
                        weight=weight, # negative float
                        source_turn=turn
                    ))
                    
        return signals


class RelationshipProvider:
    """Extracts relationship persona signals (Existing Customer vs Prospective Customer)."""
    def extract_signals(self, query: str, turn: int) -> List[Tuple[RelationshipPersona, PersonaSignal]]:
        results: List[Tuple[RelationshipPersona, PersonaSignal]] = []
        q = query.lower()
        
        for rel, patterns in RELATIONSHIP_PATTERNS.items():
            for pat, weight in patterns:
                if re.search(pat, q):
                    m = re.search(pat, q)
                    matched_text = m.group(0) if m else pat
                    sig = PersonaSignal(
                        provider="RelationshipProvider",
                        feature=f"Matched relationship phrase '{matched_text}' for {rel.value}",
                        weight=weight,
                        source_turn=turn
                    )
                    results.append((rel, sig))
                    
        return results


class CustomerPersonaEngine:
    """
    Enterprise Customer Persona Detection Engine.
    Infers RolePersona, RelationshipPersona, CommunicationPreferences, and profile_stability
    through Bayesian accumulation of positive/negative evidence with turn decay.
    """
    def __init__(self):
        self.term_provider = TerminologyProvider()
        self.rel_provider = RelationshipProvider()

    def process(self, query: str, context: Optional[ConversationContext] = None) -> PersonaProfile:
        """
        Executes turn signal extraction, score accumulation, stability evaluation,
        and preference mapping.
        """
        turn = context.turn_count if context else 1
        
        # Load state from context variables
        state = {}
        if context and "persona_state" in context.variables:
            state = context.variables["persona_state"]
            
        role_scores: Dict[str, float] = state.get("role_scores", {r.value: 0.1 for r in RolePersona if r != RolePersona.UNKNOWN})
        rel_scores: Dict[str, float] = state.get("rel_scores", {r.value: 0.1 for r in RelationshipPersona if r != RelationshipPersona.UNKNOWN})
        history_signals: List[Dict[str, Any]] = state.get("history_signals", [])
        turn_history_log: List[Dict[str, Any]] = state.get("turn_history_log", [])

        # Apply Turn Decay (0.85 per turn) to historical scores
        decay_factor = 0.85
        for r_key in role_scores:
            role_scores[r_key] = max(0.05, role_scores[r_key] * decay_factor)
        for rel_key in rel_scores:
            rel_scores[rel_key] = max(0.05, rel_scores[rel_key] * decay_factor)

        # Extract New Turn Signals
        new_signals = self.term_provider.extract_signals(query, turn)
        new_rel_signals = self.rel_provider.extract_signals(query, turn)

        # Accumulate Role Signals
        for sig in new_signals:
            for role in RolePersona:
                if role.value in sig.feature:
                    curr = role_scores.get(role.value, 0.1)
                    role_scores[role.value] = max(0.0, curr + sig.weight)

        # Accumulate Relationship Signals
        for rel, sig in new_rel_signals:
            curr = rel_scores.get(rel.value, 0.1)
            rel_scores[rel.value] = max(0.0, curr + sig.weight)

        # Explicit direct phrase overrides (e.g., "I'm the CTO", "I am a developer")
        q_lower = query.lower()
        if "i'm the cto" in q_lower or "i am the cto" in q_lower or "i'm cto" in q_lower:
            role_scores[RolePersona.TECHNICAL_ARCHITECT.value] += 1.5
            role_scores[RolePersona.DEVELOPER.value] += 1.0
        elif "i am a developer" in q_lower or "i'm a developer" in q_lower:
            role_scores[RolePersona.DEVELOPER.value] += 1.5

        # Normalize role probabilities
        total_role_score = sum(role_scores.values()) or 1.0
        role_probs: Dict[RolePersona, float] = {}
        for role in RolePersona:
            if role == RolePersona.UNKNOWN:
                continue
            raw_sc = role_scores.get(role.value, 0.05)
            role_probs[role] = round(raw_sc / total_role_score, 2)

        # Determine Primary Role
        sorted_roles = sorted(role_probs.items(), key=lambda item: item[1], reverse=True)
        top_role, top_prob = sorted_roles[0] if sorted_roles else (RolePersona.UNKNOWN, 0.0)
        
        # If top probability is very low (< 0.25), mark primary_role as UNKNOWN
        if top_prob < 0.25:
            primary_role = RolePersona.UNKNOWN
        else:
            primary_role = top_role

        # Normalize relationship probabilities
        total_rel_score = sum(rel_scores.values()) or 1.0
        rel_probs: Dict[RelationshipPersona, float] = {}
        for rel in RelationshipPersona:
            if rel == RelationshipPersona.UNKNOWN:
                continue
            raw_sc = rel_scores.get(rel.value, 0.05)
            rel_probs[rel] = round(raw_sc / total_rel_score, 2)

        sorted_rels = sorted(rel_probs.items(), key=lambda item: item[1], reverse=True)
        top_rel, top_rel_prob = sorted_rels[0] if sorted_rels else (RelationshipPersona.UNKNOWN, 0.0)
        
        if top_rel_prob < 0.35:
            primary_rel = RelationshipPersona.UNKNOWN
            rel_conf = 0.0
        else:
            primary_rel = top_rel
            rel_conf = top_rel_prob

        # Calculate Profile Stability Metric
        # Stability measures consistency of top role dominance over turn progression
        turn_history_log.append({"turn": turn, "primary_role": primary_role.value, "top_prob": top_prob})
        if len(turn_history_log) >= 2:
            recent_roles = [t["primary_role"] for t in turn_history_log[-3:]]
            matching = recent_roles.count(primary_role.value)
            stability = round(matching / len(recent_roles), 2)
        else:
            stability = 0.50 if primary_role != RolePersona.UNKNOWN else 0.20

        # Map Communication Preferences
        tech_depth = "Executive"
        exec_focus = 0.5
        density = "Balanced"
        prefer_code = False
        prefer_cases = False

        if primary_role in [RolePersona.DEVELOPER, RolePersona.TECHNICAL_ARCHITECT]:
            tech_depth = "Deep Technical"
            exec_focus = 0.1
            prefer_code = True
            density = "Detailed"
        elif primary_role in [RolePersona.EXECUTIVE_DECISION_MAKER, RolePersona.INVESTOR]:
            tech_depth = "Executive"
            exec_focus = 0.95
            prefer_cases = True
            density = "Concise"
        elif primary_role in [RolePersona.BUSINESS_FUNCTIONAL, RolePersona.OPERATIONS]:
            tech_depth = "Functional"
            exec_focus = 0.60
            density = "Balanced"
        elif primary_role == RolePersona.ACADEMIC_STUDENT:
            tech_depth = "Introductory"
            exec_focus = 0.1
            density = "Detailed"

        comm_prefs = CommunicationPreferences(
            technical_depth=tech_depth,
            executive_focus=exec_focus,
            detail_density=density,
            prefer_code_snippets=prefer_code,
            prefer_case_studies=prefer_cases
        )

        # Construct Human-Readable Reasoning Trace String
        if new_signals or new_rel_signals:
            sig_strings = [s.feature for s in new_signals] + [s.feature for _, s in new_rel_signals]
            reasoning = f"Inferred primary interaction role '{primary_role.value}' (prob: {top_prob}, stability: {stability}) based on signals: " + "; ".join(sig_strings)
        elif primary_role != RolePersona.UNKNOWN:
            reasoning = f"Maintained primary interaction role '{primary_role.value}' (prob: {top_prob}, stability: {stability}) from historical turn accumulation."
        else:
            reasoning = "Insufficient specific terminology or style signals; defaulting to Unknown / General interaction role."

        profile = PersonaProfile(
            role_probabilities=role_probs,
            primary_role=primary_role,
            relationship=primary_rel,
            relationship_confidence=rel_conf,
            communication_preferences=comm_prefs,
            profile_stability=stability,
            reasoning=reasoning,
            detected_signals=new_signals + [s for _, s in new_rel_signals],
            turn_history=turn_history_log
        )

        # Save updated state to context variables
        if context:
            context.variables["persona_state"] = {
                "role_scores": role_scores,
                "rel_scores": rel_scores,
                "turn_history_log": turn_history_log
            }

        logger.info(
            f"CustomerPersonaEngine: Session {context.session_id if context else 'N/A'} Turn {turn} -> "
            f"Role: {primary_role.value} (prob: {top_prob}), Rel: {primary_rel.value}, Stability: {stability}"
        )

        return profile


_persona_engine_instance: Optional[CustomerPersonaEngine] = None

def get_customer_persona_engine() -> CustomerPersonaEngine:
    global _persona_engine_instance
    if _persona_engine_instance is None:
        _persona_engine_instance = CustomerPersonaEngine()
    return _persona_engine_instance
