import logging
from typing import Dict, Any, List, Optional
from reasoning_planner import ReasoningType
from evidence_selector import SelectedEvidencePackage

logger = logging.getLogger(__name__)

class StructuredFormatter:
    def __init__(self):
        pass

    def format_deterministic_fallback(self, selected_evidence: SelectedEvidencePackage, reasoning_type: str) -> str:
        entities = selected_evidence.selected_entities
        if not entities:
            return "The current Enterprise Registry does not contain enough information to answer that confidently."

        lines = [f"### Enterprise {reasoning_type.title()} Analysis\n"]

        if reasoning_type == ReasoningType.COMPARISON.value:
            lines.append("#### Executive Summary\nBelow is a side-by-side comparison compiled directly from verified Enterprise Registry data:\n")
            lines.append("| Feature / Specification | " + " | ".join([e.get("name", eid) for eid, e in entities.items()]) + " |")
            lines.append("| :--- | " + " | ".join([":---" for _ in entities]) + " |")
            
            lines.append("| **Category** | " + " | ".join([str(e.get("category", "N/A")) for eid, e in entities.items()]) + " |")
            lines.append("| **Overview** | " + " | ".join([str(e.get("overview", "N/A"))[:80] + "..." for eid, e in entities.items()]) + " |")
            lines.append("| **Target Audience** | " + " | ".join([", ".join(e.get("best_for", ["N/A"])) if isinstance(e.get("best_for"), list) else str(e.get("best_for", "N/A")) for eid, e in entities.items()]) + " |")
            
            lines.append("\n#### Key Strengths & Differences")
            for eid, e in entities.items():
                name = e.get("name", eid)
                lines.append(f"\n- **{name}**:")
                if e.get("benefits"):
                    b_list = e.get("benefits")
                    if isinstance(b_list, list):
                        for b in b_list[:3]:
                            if isinstance(b, dict):
                                lines.append(f"  • **{b.get('title', 'Benefit')}**: {b.get('description', '')}")
                            else:
                                lines.append(f"  • {b}")

            lines.append("\n#### Recommendation\nAdvanced consultative reasoning is temporarily offline. For custom architectural advisory, please reach out to our team at sales@citta.ai.")

        elif reasoning_type == ReasoningType.SUITABILITY.value:
            lines.append("#### Requirements & Evaluation\n")
            for eid, e in entities.items():
                name = e.get("name", eid)
                lines.append(f"**Target Offering**: {name}\n")
                lines.append(f"• **Designed For**: {', '.join(e.get('best_for', ['Enterprise'])) if isinstance(e.get('best_for'), list) else e.get('best_for')}\n")
                lines.append(f"• **Overview**: {e.get('overview')}\n")

            lines.append("#### Recommendation\nBased on verified catalog taxonomy, the selected offering aligns with the specified operational requirements.")

        else:
            for eid, e in entities.items():
                name = e.get("name", eid)
                lines.append(f"### {name}\n")
                lines.append(f"**Overview**: {e.get('overview', 'Verified Enterprise Offering')}\n")
                if e.get("features"):
                    lines.append("**Key Features**:")
                    for f in e.get("features")[:4]:
                        if isinstance(f, dict):
                            lines.append(f"- **{f.get('title', 'Feature')}**: {f.get('description', '')}")
                        else:
                            lines.append(f"- {f}")

        return "\n".join(lines)

_structured_formatter_instance = None

def get_structured_formatter() -> StructuredFormatter:
    global _structured_formatter_instance
    if _structured_formatter_instance is None:
        _structured_formatter_instance = StructuredFormatter()
    return _structured_formatter_instance
