import logging
from typing import Dict, Any, List
from backend.conversation.models import ConversationContext, IntentAnalysis, DiscoveryState, LeadQualification
from backend.conversation.interfaces import IUnderstandingEngine
from backend.conversation.config import LEAD_QUALIFICATION_WEIGHTS

logger = logging.getLogger(__name__)

from backend.conversation.intent_engine import get_enterprise_intent_engine
from backend.conversation.persona_engine import get_customer_persona_engine

class UnderstandingEngine(IUnderstandingEngine):
    """
    Decodes user intent (multi-intent), customer discovery indicators, 
    persona detection, and applies lead qualification rules.
    """
    def __init__(self):
        self.intent_engine = get_enterprise_intent_engine()
        self.persona_engine = get_customer_persona_engine()

    def analyze_intent(self, query: str, context: ConversationContext) -> IntentAnalysis:
        """
        Extracts primary and secondary user intents dynamically via EnterpriseIntentEngine.
        """
        rich_res = self.intent_engine.analyze(query, context)
        
        primary_str = rich_res.primary_intent.intent.value.lower()
        secondary_strs = [s.intent.value.lower() for s in rich_res.secondary_intents]
        
        return IntentAnalysis(
            primary_intent=primary_str,
            secondary_intents=secondary_strs,
            confidence=rich_res.primary_intent.overall_confidence,
            rich_result=rich_res
        )

    def run_discovery(self, query: str, intent: IntentAnalysis, context: ConversationContext) -> DiscoveryState:
        """
        Discovers pre-sales indicators in conversation history, query text, and runs Persona Engine.
        """
        # Run Customer Persona Engine
        persona_profile = self.persona_engine.process(query, context)
        context.variables["persona_profile"] = persona_profile

        # Read existing variables from context
        variables = context.variables
        disc_data = variables.get("discovery_state", {})
        
        q = query.lower()
        
        # Basic heuristic parsing
        if "employee" in q or "people" in q:
            disc_data["company_size"] = "Enterprise" if "500" in q or "1000" in q else "Medium"
        if "healthcare" in q or "hospital" in q:
            disc_data["industry"] = "Healthcare"
        elif "retail" in q or "store" in q:
            disc_data["industry"] = "Retail"
            
        if "urgent" in q or "asap" in q or "weeks" in q:
            disc_data["urgency"] = "High"
            disc_data["timeline"] = "1-3 months"
            
        if "budget" in q or "pricing" in q:
            disc_data["budget"] = "Inquired"
            
        # Missing fields identification
        required = ["industry", "company_size", "urgency", "timeline", "budget"]
        missing = [f for f in required if f not in disc_data]
        
        # Calculate lead qualification progress
        score = 0.0
        for f, weight in LEAD_QUALIFICATION_WEIGHTS.items():
            if f in disc_data:
                score += weight
                
        disc_state = DiscoveryState(
            company_name=disc_data.get("company_name"),
            industry=disc_data.get("industry"),
            company_size=disc_data.get("company_size"),
            urgency=disc_data.get("urgency"),
            timeline=disc_data.get("timeline"),
            budget=disc_data.get("budget"),
            missing_fields=missing,
            lead_score=score
        )
        
        # Update context
        variables["discovery_state"] = disc_data
        
        return disc_state

    def qualify_lead(self, discovery: DiscoveryState) -> LeadQualification:
        """
        Scores lead status, evaluating pre-sales readiness and next-best actions.
        """
        score = discovery.lead_score * 100.0
        
        if score >= 75.0:
            interest = "HOT"
            readiness = "READY"
            nba = "Generate custom proposal and route to enterprise account executive."
        elif score >= 40.0:
            interest = "HIGH"
            readiness = "EVALUATING"
            nba = "Suggest scheduling a technical demonstration session."
        else:
            interest = "MEDIUM" if score > 0 else "LOW"
            readiness = "EXPLORATORY"
            nba = "Conduct discovery and qualify client industry vertical."
            
        return LeadQualification(
            score=score,
            interest_level=interest,
            readiness_tier=readiness,
            next_best_action=nba
        )

def get_understanding_engine() -> IUnderstandingEngine:
    return UnderstandingEngine()
