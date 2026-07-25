from backend.presentation.models.response_object import ResponseObject
from backend.presentation.renderers.section_renderer import SectionRenderer

class OverviewFormatter:
    
    @staticmethod
    def render(response: ResponseObject) -> str:
        """
        Renders an overview response based on the domain (Product, Service, Technology).
        """
        md = SectionRenderer.render_header(response.title, response.domain, response.tagline)
        
        # Determine the sections to render based on domain
        domain = response.domain.lower()
        
        if domain in ["product", "solution"]:
            sections = [
                ("overview", response.overview),
                ("best_for", response.best_for),
                ("modules", response.modules),
                ("features", response.features),
                ("capabilities", response.capabilities),
                ("benefits", response.benefits),
                ("technology_stack", response.technology_stack),
                ("integrations", response.integrations),
                ("deployment", response.deployment)
            ]
        elif domain == "service":
            sections = [
                ("overview", response.overview),
                ("services_included", response.services_included),
                ("benefits", response.benefits),
                ("technology_stack", response.technology_stack)
            ]
        elif domain == "technology":
            sections = [
                ("overview", response.overview),
                ("capabilities", response.capabilities),
                ("used_in", response.used_in),
                ("advantages", response.advantages)
            ]
        elif domain == "company":
            sections = [
                ("overview", response.overview),
                ("capabilities", response.capabilities),
                ("industries", response.industries)
            ]
        else:
            # Generic fallback
            sections = [
                ("overview", response.overview),
                ("features", response.features),
                ("benefits", response.benefits)
            ]
            
        for key, items in sections:
            if items:
                md += SectionRenderer.render_section(key, items)
                
        return md.strip()
