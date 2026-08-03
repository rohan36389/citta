from presentation.models.response_object import ResponseObject
from presentation.renderers.section_renderer import SectionRenderer

class ContactFormatter:
    
    @staticmethod
    def render(response: ResponseObject) -> str:
        """
        Renders the contact / location formatting.
        """
        md = SectionRenderer.render_header("Contact Sales & Advisory", "contact")
        
        c = response.contact_info
        if c:
            if c.get("phone"):
                md += f"**Phone**: {c.get('phone')}\n\n"
            if c.get("email"):
                md += f"**Email**: {c.get('email')}\n\n"
            if c.get("address"):
                md += f"**Location**: {c.get('address')}\n\n"
            if c.get("business_hours"):
                md += f"**Business Hours**: {c.get('business_hours')}\n\n"
                
        return md.strip()
