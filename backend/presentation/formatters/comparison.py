from backend.presentation.models.response_object import ResponseObject
from backend.presentation.renderers.section_renderer import SectionRenderer

class ComparisonFormatter:
    
    @staticmethod
    def render(response: ResponseObject) -> str:
        """
        Renders a side-by-side product or entity comparison.
        Expects response.comparison_data to contain 'left', 'right', 'recommendation', 'reason'.
        """
        md = SectionRenderer.render_header("Product Comparison", "comparison", response.tagline)
        
        comp = response.comparison_data
        if not comp:
            md += "Comparison data is not available.\n\n"
            return md.strip()
            
        left = comp.get("left", {})
        right = comp.get("right", {})
        
        if left:
            md += f"**{left.get('name', 'Product A')}**\n\n"
            for f in left.get("features", []):
                md += f"✔ {f}\n"
            md += "\n"
            
        if right:
            md += f"**{right.get('name', 'Product B')}**\n\n"
            for f in right.get("features", []):
                md += f"✔ {f}\n"
            md += "\n"
            
        if comp.get("recommendation") or comp.get("reason"):
            md += "**Recommendation**\n\n"
            if comp.get("recommendation"):
                md += f"{comp.get('recommendation')}\n\n"
            if comp.get("reason"):
                md += f"{comp.get('reason')}\n\n"
                
        return md.strip()
