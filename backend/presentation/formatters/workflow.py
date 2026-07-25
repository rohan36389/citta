from backend.presentation.models.response_object import ResponseObject
from backend.presentation.renderers.section_renderer import SectionRenderer

class WorkflowFormatter:
    
    @staticmethod
    def render(response: ResponseObject) -> str:
        """
        Renders a sequential workflow using step indicators and arrows.
        """
        md = SectionRenderer.render_header(response.title, response.domain, response.tagline)
        
        if not response.workflows:
            md += "**How It Works**\n\n"
            md += "Workflow details are not available for this entity.\n\n"
        else:
            is_synthesized = any(w.get("synthesized") for w in response.workflows)
            
            if is_synthesized:
                md += "**Operational Workflow**\n\n"
            else:
                md += "**How It Works**\n\n"
                
            for i, step in enumerate(response.workflows):
                step_num = step.get("step", i + 1)
                title = step.get("title", f"Step {step_num}")
                desc = step.get("description", "")
                
                if is_synthesized:
                    md += f"{step_num}. {title}\n"
                    if desc:
                        md += f"• {desc}\n"
                else:
                    md += f"Step {step_num}\n"
                    if title and desc:
                        md += f"• **{title}**: {desc}\n"
                    elif title:
                        md += f"• {title}\n"
                    elif desc:
                        md += f"• {desc}\n"
                    
                if i < len(response.workflows) - 1:
                    md += "\n\n"
                else:
                    md += "\n"
                    
        return md.strip()
