from backend.presentation.models.response_object import ResponseObject
from backend.presentation.renderers.section_renderer import SectionRenderer

class FAQFormatter:
    
    @staticmethod
    def render(response: ResponseObject) -> str:
        """
        Renders a Frequently Asked Questions list.
        """
        md = SectionRenderer.render_header(response.title, response.domain, response.tagline)
        
        md += "**Frequently Asked Questions**\n\n"
        
        if not response.faq:
            md += "No FAQs available for this item.\n\n"
        else:
            for item in response.faq:
                q = item.get("question")
                a = item.get("answer")
                if q and a:
                    md += f"**Q: {q}**\n*{a}*\n\n"
                    
        return md.strip()
