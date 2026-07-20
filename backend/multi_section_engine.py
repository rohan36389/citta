import logging
from typing import Dict, Any, List, Optional

from knowledge_service import get_knowledge_service
from tenant_registry import get_tenant_registry
from intent_analyzer import TopicType

logger = logging.getLogger(__name__)

class MultiSectionEngine:
    def __init__(self):
        self.ks = get_knowledge_service()
        self.tenant_reg = get_tenant_registry()

    def merge_sections(self, tenant_id: str, topics: List[str], entity_id: Optional[str] = None) -> Dict[str, Any]:
        tenant = self.tenant_reg.get_tenant(tenant_id)
        comp_data = self.ks.reg.registry_index.get("COMPANY_INFO", {})
        
        md_sections = []
        name = comp_data.get("name") or tenant.name

        # If it's a multi-topic company request
        if TopicType.COMPANY in topics or TopicType.MISSION in topics or TopicType.VISION in topics or TopicType.VALUES in topics:
            md_sections.append(f"### {name} — Corporate Overview\n\n**Overview**: {comp_data.get('description', '')}")
            
            if TopicType.MISSION in topics and comp_data.get("mission"):
                md_sections.append(f"**Mission**: {comp_data.get('mission')}")
            if TopicType.VISION in topics and comp_data.get("vision"):
                md_sections.append(f"**Vision**: {comp_data.get('vision')}")
            if TopicType.VALUES in topics and comp_data.get("values"):
                md_sections.append(f"**Values**: {comp_data.get('values')}")

        if TopicType.LEADERSHIP in topics:
            leaders = self.ks.list_entities(tenant_id, "LEADERSHIP")
            lead_str = "\n".join([f"- **{person['name']}**: {person['title']}" for person in leaders[:4]])
            md_sections.append(f"### Executive Leadership\n\n{lead_str}")

        if TopicType.AWARDS in topics or TopicType.CERTIFICATIONS in topics:
            rec_data = self.ks.reg.registry_index.get("RECOGNITION", {})
            recognitions = rec_data.get("recognitions", [])
            if recognitions:
                rec_str = "\n".join([f"- **{r['title']}**: {r.get('organization', '')}" for r in recognitions])
                md_sections.append(f"### Awards & Certifications\n\n{rec_str}")

        combined_text = "\n\n".join(md_sections)
        combined_text += f"\n\nExplore more on our [About page]({tenant.routes.get('about', '/about')}) or reach out via [Contact page]({tenant.routes.get('contact', '/contact')})."

        return {
            "response": combined_text,
            "source": "Platform Knowledge Service",
            "verified": True,
            "confidence": 1.0,
            "navigation": tenant.routes.get("about", "/about"),
            "suggestions": ["Who is CEO?", "What products do you offer?", "Contact Us"]
        }

def get_multi_section_engine() -> MultiSectionEngine:
    return MultiSectionEngine()
