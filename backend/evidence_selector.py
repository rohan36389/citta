import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from evidence_builder import EvidencePackage, EntityEvidence
from reasoning_planner import ReasoningPlan

logger = logging.getLogger(__name__)

class SelectedEvidencePackage(BaseModel):
    session_id: str
    query: str
    reasoning_type: str
    selected_entities: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    included_sections: List[str] = Field(default_factory=list)
    evidence_completeness: float = 1.0

class EvidenceSelector:
    def __init__(self):
        pass

    def select_evidence(self, raw_package: EvidencePackage, plan: ReasoningPlan) -> SelectedEvidencePackage:
        required_secs = set(plan.required_sections)
        selected_entities = {}
        total_requested = len(plan.target_entity_ids) * len(required_secs)
        found_count = 0

        for ent_id, ent_evidence in raw_package.entities.items():
            if plan.target_entity_ids and ent_id not in plan.target_entity_ids:
                continue

            filtered_data = {
                "entity_id": ent_evidence.entity_id,
                "name": ent_evidence.name,
                "category": ent_evidence.category,
                "tagline": ent_evidence.tagline
            }

            for sec in required_secs:
                val = getattr(ent_evidence, sec, None)
                if val:
                    filtered_data[sec] = val
                    found_count += 1

            selected_entities[ent_id] = filtered_data

        completeness = round(found_count / max(total_requested, 1), 2) if total_requested > 0 else 1.0
        # Bound completeness between 0.0 and 1.0
        completeness = max(0.0, min(1.0, completeness))

        return SelectedEvidencePackage(
            session_id=raw_package.session_id,
            query=raw_package.query,
            reasoning_type=plan.reasoning_type.value,
            selected_entities=selected_entities,
            included_sections=list(required_secs),
            evidence_completeness=completeness
        )

_evidence_selector_instance = None

def get_evidence_selector() -> EvidenceSelector:
    global _evidence_selector_instance
    if _evidence_selector_instance is None:
        _evidence_selector_instance = EvidenceSelector()
    return _evidence_selector_instance
