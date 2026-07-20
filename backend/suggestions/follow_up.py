import logging
from typing import Dict, Any, List, Optional
from knowledge_registry import get_registry

logger = logging.getLogger(__name__)

ROLE_FOLLOWUPS = {
    "vinay_velivela": [
        "Show Leadership Team",
        "Tell me about the CTO",
        "Learn about CittaAI"
    ],
    "akhil_reddy": [
        "What technologies does CittaAI use?",
        "Tell me about Enterprise AI OS",
        "Show AI Products"
    ],
    "saladi_chandra_balaji": [
        "Tell me about company operations",
        "Show Services",
        "Learn about CittaAI"
    ],
    "ganesh_gandhi_vadalani": [
        "Show Products",
        "Tell me about WhatsApp Marketing Platform",
        "Show Leadership Team"
    ],
    "harish_nerati": [
        "Show Services",
        "Contact Team",
        "Show Leadership Team"
    ],
    "aravind_reddy": [
        "Explain E-Commerce OS",
        "Show Products",
        "Show Leadership Team"
    ],
    "parvatha_mohan": [
        "Contact Team",
        "Show Services",
        "Show Leadership Team"
    ]
}

DEFAULT_REGISTRY_SUGGESTIONS = {
    "SOLUTIONS": ["Explain E-Commerce OS", "Explain Education OS", "Explain Real Estate OS"],
    "PRODUCTS": ["Explain WhatsApp Marketing Platform", "Explain Influencer Marketing Platform"],
    "SERVICES": ["What does Data Engineering include?", "Explain Enterprise & Agentic AI service"],
    "CASE_STUDIES": ["Show Jewellery Brand case study", "Show FMCG Brand case study", "Show Spices Export case study"],
    "LEADERSHIP": ["Who is the CEO?", "Tell me about Akhil Reddy.", "Who leads Technology?"],
    "RECOGNITION": ["What certifications does CittaAI hold?", "Show company awards"],
    "CONTACT": ["What are your office hours?", "Where is your office located?"]
}

class FollowUpEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FollowUpEngine, cls).__new__(cls)
            cls._instance.reg = get_registry()
        return cls._instance

    def generate_suggestions(
        self,
        entity_id: Optional[str] = None,
        registry_type: Optional[str] = None,
        query_intent: Optional[str] = None,
        target_person_id: Optional[str] = None
    ) -> List[str]:
        """Deterministically generates 2–4 relationship-driven follow-up suggestions."""
        if target_person_id and target_person_id in ROLE_FOLLOWUPS:
            return ROLE_FOLLOWUPS[target_person_id]

        if entity_id:
            if entity_id in ROLE_FOLLOWUPS:
                return ROLE_FOLLOWUPS[entity_id]
                
            obj = self.reg.registry_by_id.get(entity_id)
            if obj:
                title = obj.title or obj.name
                sugs = [
                    f"How does {title} work?",
                    f"What features are included in {title}?",
                    f"Who is {title} designed for?"
                ]
                if hasattr(obj, "relationships") and obj.relationships:
                    for rel in obj.relationships:
                        target_obj = self.reg.registry_by_id.get(rel.target) or self.reg.registry_by_slug.get(rel.target)
                        if target_obj:
                            sugs.append(f"Compare {title} with {target_obj.title}")
                            break
                return sugs[:4]
                
        if registry_type and registry_type.upper() in DEFAULT_REGISTRY_SUGGESTIONS:
            return DEFAULT_REGISTRY_SUGGESTIONS[registry_type.upper()][:4]

        if query_intent == "leadership_lookup":
            return ["Who is the CEO?", "Who is the CTO?", "Show Executive Leadership Team"]
            
        return ["Show Solutions", "Show Products", "Show Services", "Contact Info"]

def get_follow_up_engine() -> FollowUpEngine:
    return FollowUpEngine()
