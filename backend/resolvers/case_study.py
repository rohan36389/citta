import logging
from typing import Dict, Any, List, Optional
from knowledge_registry import get_registry

logger = logging.getLogger(__name__)

class CaseStudyResolver:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CaseStudyResolver, cls).__new__(cls)
            cls._instance.reg = get_registry()
        return cls._instance

    def resolve_case_study(self, query: str, entity_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Resolves case study details and returns dynamic section components."""
        target_id = entity_id
        q_lower = query.lower().strip()
        
        if not target_id:
            if "jewellery" in q_lower:
                target_id = "jewellery_brand_roi"
            elif "fmcg" in q_lower:
                target_id = "fmcg_social_growth"
            elif "spices" in q_lower or "b2b" in q_lower:
                target_id = "b2b_spices_export"
                
        obj = self.reg.registry_by_id.get(target_id) if target_id else None
        
        if not obj:
            # Check legacy case studies list
            cs_list = self.reg.registry_index.get("CASE_STUDIES", {}).get("entities", [])
            for cs in cs_list:
                c_id = cs.get("id", "").lower()
                c_title = cs.get("title", "").lower()
                c_name = cs.get("name", "").lower()
                if (target_id and target_id.lower() in c_id) or ("jewellery" in q_lower and "jewellery" in c_title) or ("fmcg" in q_lower and "fmcg" in c_title) or ("spices" in q_lower and "spices" in c_title):
                    return {
                        "id": cs.get("id"),
                        "title": cs.get("title") or cs.get("name"),
                        "overview": cs.get("overview") or cs.get("summary", ""),
                        "problem": cs.get("challenge") or cs.get("problem", ""),
                        "solution": cs.get("solution") or cs.get("approach", ""),
                        "technologies": cs.get("technologies") or cs.get("tech_stack", []),
                        "outcome": cs.get("results") or cs.get("outcome", ""),
                        "benefits": cs.get("benefits", []),
                        "metrics": {"resolved_entity": cs.get("id"), "resolved_registry": "CASE_STUDIES"}
                    }
            return None

        # Extract sections from EnterpriseKnowledgeObject
        overview = obj.overview or obj.description
        problem = ""
        solution_desc = ""
        tech_used = []
        outcome = ""
        benefits = obj.benefits or []
        
        if obj.capabilities:
            for cap in obj.capabilities:
                if "problem" in cap.title.lower() or "challenge" in cap.title.lower():
                    problem = cap.description
                elif "solution" in cap.title.lower() or "implementation" in cap.title.lower():
                    solution_desc = cap.description
                elif "results" in cap.title.lower() or "outcome" in cap.title.lower() or "impact" in cap.title.lower():
                    outcome = cap.description
                tech_used.extend(cap.keywords)
                
        if not problem and obj.use_cases:
            problem = ", ".join(obj.use_cases)
        if not outcome and obj.tagline:
            outcome = obj.tagline
            
        return {
            "id": obj.id,
            "title": obj.title,
            "overview": overview,
            "problem": problem or "Enterprise scale operations and operational efficiency bottleneck.",
            "solution": solution_desc or "Deployed CittaAI Enterprise Platform with custom AI workflows.",
            "technologies": list(set(tech_used)) if tech_used else ["Enterprise AI OS", "NLP", "Predictive Analytics"],
            "outcome": outcome or obj.tagline or "Significant ROI boost and operational transformation.",
            "benefits": benefits,
            "url": obj.url,
            "metrics": {"resolved_entity": obj.id, "resolved_registry": "CASE_STUDIES"}
        }

def get_case_study_resolver() -> CaseStudyResolver:
    return CaseStudyResolver()
