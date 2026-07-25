import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AdaptiveResponseGenerator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AdaptiveResponseGenerator, cls).__new__(cls)
        return cls._instance

    def generate_leadership_response(self, lead_data: Dict[str, Any], detail_level: str = "compact") -> str:
        """Formats leadership profiles strictly grounded in leadership_info.json."""
        if lead_data.get("type") == "not_found":
            return "I couldn't find that person in CittaAI's leadership team."

        if lead_data.get("type") == "individual":
            m = lead_data["member"]
            name = m.get("name")
            title = m.get("designation") or m.get("title")
            bio = m.get("bio") or m.get("description", "")
            dept = m.get("department", "")
            responsibilities = m.get("responsibilities", [])
            
            resp = f"👤 **{name}**\n*{title} — {dept}*\n\n" if dept else f"👤 **{name}**\n*{title}*\n\n"
            if bio:
                resp += f"{bio}\n\n"
            if responsibilities:
                resp += "**Key Responsibilities**:\n" + "\n".join([f"• {r}" for r in responsibilities]) + "\n"
            return resp.strip()

        # Leadership Team Overview Query Mode
        members = lead_data.get("members", [])
        exec_bullets = [
            f"• **{m['name']}** — {m.get('designation')}" 
            for m in members
        ]
        return (
            "👥 **Leadership Team**\n\n"
            "Meet the experienced leaders driving innovation at CittaAI.\n\n"
            + "\n".join(exec_bullets)
        ).strip()

    def generate_case_study_response(self, cs_data: Dict[str, Any], detail_level: str = "compact") -> str:
        """Formats case study details using AI Consultant persona."""
        title = cs_data.get("title")
        overview = cs_data.get("overview", "")
        problem = cs_data.get("problem", "")
        solution = cs_data.get("solution", "")
        tech = cs_data.get("technologies", [])
        outcome = cs_data.get("outcome", "")
        benefits = cs_data.get("benefits", [])
        
        if detail_level == "compact":
            res = f"Here is a summary of our client success story for **{title}**:\n\n"
            if overview:
                res += f"{overview}\n\n"
            res += "**Key Highlights & Impact**:\n"
            if outcome:
                res += f"• **Business Outcome**: {outcome}\n"
            if problem:
                res += f"• **Challenge Addressed**: {problem}\n"
            if tech:
                res += f"• **Tech Stack**: {', '.join(tech[:4])}\n"
            if benefits:
                res += f"• **Primary Benefit**: {benefits[0]}\n"
            return res.strip()
        else:
            res = f"### Case Study: {title}\n\n"
            if overview:
                res += f"**Overview**: {overview}\n\n"
            if problem:
                res += f"**The Challenge**: {problem}\n\n"
            if solution:
                res += f"**The Solution**: {solution}\n\n"
            if tech:
                res += f"**Technologies Applied**: {', '.join(tech)}\n\n"
            if outcome:
                res += f"**Business Outcome & ROI**: {outcome}\n\n"
            if benefits:
                res += "**Client Benefits**:\n" + "\n".join([f"- {b}" for b in benefits]) + "\n\n"
            return res.strip()

    def generate_entity_response(self, obj: Any, detail_level: str = "compact", section: str = "overview") -> str:
        """Formats EnterpriseKnowledgeObject by Information Density."""
        title = getattr(obj, "title", getattr(obj, "name", "CittaAI Solution"))
        tagline = getattr(obj, "tagline", "")
        overview = getattr(obj, "overview", getattr(obj, "description", ""))
        capabilities = getattr(obj, "capabilities", [])
        benefits = getattr(obj, "benefits", [])
        workflows = getattr(obj, "workflows", [])
        
        if detail_level == "compact":
            res = f"**{title}**"
            if tagline:
                res += f" is an {tagline.lower()}" if not tagline.lower().startswith("ai") else f" is an {tagline}"
            res += ".\n\n"
            if overview:
                res += f"{overview}\n\n"
                
            if capabilities:
                res += "**Key Capabilities & Modules**:\n"
                for cap in capabilities[:5]:
                    cap_title = getattr(cap, "title", str(cap))
                    cap_desc = getattr(cap, "description", "")
                    res += f"• **{cap_title}**: {cap_desc}\n" if cap_desc else f"• **{cap_title}**\n"
            elif benefits:
                res += "**Core Benefits**:\n"
                for b in benefits[:4]:
                    res += f"• {b}\n"
                    
            return res.strip()
            
        elif detail_level == "standard":
            res = f"### {title}\n"
            if tagline:
                res += f"*{tagline}*\n\n"
            if overview:
                res += f"**Overview**: {overview}\n\n"
            if capabilities:
                res += "**Key Capabilities**:\n"
                for cap in capabilities:
                    cap_title = getattr(cap, "title", str(cap))
                    cap_desc = getattr(cap, "description", "")
                    res += f"- **{cap_title}**: {cap_desc}\n"
                res += "\n"
            if benefits:
                res += "**Platform Benefits**:\n" + "\n".join([f"- {b}" for b in benefits]) + "\n\n"
            return res.strip()
            
        else: # Detailed
            import structured_renderers
            return structured_renderers.render_by_type(obj)

    def generate_workflow_response(self, title: str, steps: List[Any]) -> str:
        """Explains sequential operational workflows for 'HOW' inquiries."""
        res = f"⚙️ **How {title} Works (Operational Workflow)**\n\n"
        res += f"{title} operates through a structured, multi-step pipeline:\n\n"
        for idx, step in enumerate(steps, 1):
            s_title = getattr(step, "title", str(step))
            s_desc = getattr(step, "description", "")
            res += f"**Step {idx} — {s_title}**: {s_desc}\n" if s_desc else f"**Step {idx}**: {s_title}\n"
        res += "\nThis unified workflow eliminates operational friction and manual handoffs."
        return res.strip()

    def generate_grouped_benefits_response(self, title: str, benefits: List[str]) -> str:
        """Groups benefits logically into Business, Operational, and Technical categories."""
        res = f"🎯 **Key Value & Benefits of {title}**\n\n"
        
        biz_bens = []
        op_bens = []
        tech_bens = []
        
        for b in benefits:
            b_str = str(b)
            if any(k in b_str.lower() for k in ["cost", "roi", "revenue", "growth", "commercial", "time-to-market"]):
                biz_bens.append(b_str)
            elif any(k in b_str.lower() for k in ["api", "security", "cloud", "integration", "compliance", "scale"]):
                tech_bens.append(b_str)
            else:
                op_bens.append(b_str)

        if biz_bens:
            res += "**Business & Financial Benefits**:\n" + "\n".join([f"• {b}" for b in biz_bens]) + "\n\n"
        if op_bens:
            res += "**Operational & Efficiency Benefits**:\n" + "\n".join([f"• {b}" for b in op_bens]) + "\n\n"
        if tech_bens:
            res += "**Technical & Architecture Benefits**:\n" + "\n".join([f"• {b}" for b in tech_bens]) + "\n\n"
            
        if not (biz_bens or op_bens or tech_bens):
            res += "\n".join([f"• {b}" for b in benefits])

        return res.strip()

    def generate_comparative_response(self, entity_a: Dict[str, Any], entity_b: Dict[str, Any]) -> str:
        """Renders an objective comparative matrix table for retrieved entities."""
        name_a = entity_a.get("name", "Solution A")
        name_b = entity_b.get("name", "Solution B")
        
        res = f"📊 **Comparative Evaluation: {name_a} vs. {name_b}**\n\n"
        res += f"| Dimension | **{name_a}** | **{name_b}** |\n"
        res += "| :--- | :--- | :--- |\n"
        res += f"| **Core Focus** | {entity_a.get('tagline', 'Enterprise Operating System')} | {entity_b.get('tagline', 'Enterprise Operating System')} |\n"
        res += f"| **Target Vertical** | {entity_a.get('domain', 'Enterprise Operations')} | {entity_b.get('domain', 'Enterprise Operations')} |\n"
        res += f"| **Primary Capability** | {entity_a.get('capabilities', ['Unified Desk'])[0]} | {entity_b.get('capabilities', ['Unified Desk'])[0]} |\n\n"
        res += f"Both solutions leverage CittaAI's shared enterprise data engine and security architecture."
        return res.strip()

def get_response_generator() -> AdaptiveResponseGenerator:
    return AdaptiveResponseGenerator()
