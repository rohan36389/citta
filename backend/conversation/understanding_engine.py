import logging
from typing import Dict, Any, List
from backend.conversation.models import ConversationContext, IntentAnalysis, DiscoveryState, LeadQualification
from backend.conversation.interfaces import IUnderstandingEngine
from backend.conversation.config import LEAD_QUALIFICATION_WEIGHTS

logger = logging.getLogger(__name__)

class UnderstandingEngine(IUnderstandingEngine):
    """
    Decodes user intent (multi-intent), customer discovery indicators, 
    and applies lead qualification rules.
    """
    def __init__(self):
        pass

    def analyze_intent(self, query: str, context: ConversationContext) -> IntentAnalysis:
        """
        Extracts primary and secondary user intents dynamically.
        """
        q = query.lower()
        primary = "general_inquiry"
        secondary: List[str] = []
        
        # Simple rule-based classification stubs
        if "compare" in q or "vs" in q or "difference" in q:
            primary = "comparison"
        elif "price" in q or "cost" in q or "budget" in q or "quote" in q:
            primary = "pricing_inquiry"
        elif "how to" in q or "api" in q or "integrate" in q or "architecture" in q or "setup" in q:
            primary = "technical_validation"
        elif "demo" in q or "schedule" in q or "talk to sales" in q or "meeting" in q:
            primary = "demo_scheduling"
        elif "who" in q or "founder" in q or "ceo" in q or "team" in q:
            primary = "leadership_lookup"
            
        # Detect secondary indicators
        if "manufacturing" in q or "retail" in q or "healthcare" in q or "finance" in q:
            secondary.append("industry_filtering")
            
        return IntentAnalysis(primary_intent=primary, secondary_intents=secondary)

    def run_discovery(self, query: str, intent: IntentAnalysis, context: ConversationContext) -> DiscoveryState:
        """
        Discovers pre-sales indicators in conversation history & query text.
        """
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
