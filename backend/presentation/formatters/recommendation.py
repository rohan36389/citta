from presentation.models.response_object import ResponseObject
from presentation.renderers.section_renderer import SectionRenderer

class RecommendationFormatter:
    
    @staticmethod
    def render(response: ResponseObject) -> str:
        """
        Renders a targeted recommendation (e.g. 'I am a hospital' -> Healthcare AI Platform).
        """
        md = SectionRenderer.render_header("Recommended Solution", "recommendation")
        
        md += f"**{response.title}**\n\n"
        
        rec = response.recommendation_data
        if rec and rec.get("why_this_fits"):
            md += "**Why This Fits**\n\n"
            for reason in rec["why_this_fits"]:
                md += f"• {reason}\n"
            md += "\n"
            
        if response.capabilities:
            md += SectionRenderer.render_section("capabilities", response.capabilities)
            
        return md.strip()
