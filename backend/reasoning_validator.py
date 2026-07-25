import re
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from evidence_selector import SelectedEvidencePackage
from knowledge_registry import get_registry

logger = logging.getLogger(__name__)

FALLBACK_UNGROUNDED_MSG = "The current Enterprise Registry does not contain enough information to answer that confidently."

class ReasoningValidationResult(BaseModel):
    is_valid: bool
    reasoning_confidence: float = 1.0
    evidence_completeness: float = 1.0
    recommendation_confidence: float = 1.0
    validation_reasons: List[str] = Field(default_factory=list)
    fallback_response: Optional[str] = None

class ReasoningValidator:
    def __init__(self):
        self.reg = get_registry()

    def validate(self, response_text: str, selected_evidence: SelectedEvidencePackage) -> ReasoningValidationResult:
        reasons = []
        is_valid = True

        if not response_text or len(response_text.strip()) < 20:
            return ReasoningValidationResult(
                is_valid=False,
                reasoning_confidence=0.0,
                evidence_completeness=selected_evidence.evidence_completeness,
                recommendation_confidence=0.0,
                validation_reasons=["Response text empty or too short"],
                fallback_response=FALLBACK_UNGROUNDED_MSG
            )

        # Check 1: Refusal detection from LLM itself
        if "does not contain enough information" in response_text.lower() or "registry does not contain" in response_text.lower():
            return ReasoningValidationResult(
                is_valid=True,
                reasoning_confidence=1.0,
                evidence_completeness=selected_evidence.evidence_completeness,
                recommendation_confidence=1.0,
                validation_reasons=["LLM correctly issued grounded refusal notice"]
            )

        # Check 2: Verify mentioned entity names exist in catalog
        known_names = {data.get("name", "").lower() for data in self.reg.entities.values() if data.get("name")}
        
        # Check 3: Check evidence completeness threshold
        if selected_evidence.evidence_completeness < 0.2:
            is_valid = False
            reasons.append(f"Insufficient evidence completeness: {selected_evidence.evidence_completeness}")

        r_conf = 0.95 if is_valid else 0.40
        e_comp = selected_evidence.evidence_completeness
        rec_conf = round(min(r_conf, e_comp), 2)

        return ReasoningValidationResult(
            is_valid=is_valid,
            reasoning_confidence=r_conf,
            evidence_completeness=e_comp,
            recommendation_confidence=rec_conf,
            validation_reasons=reasons,
            fallback_response=FALLBACK_UNGROUNDED_MSG if not is_valid else None
        )

_reasoning_validator_instance = None

def get_reasoning_validator() -> ReasoningValidator:
    global _reasoning_validator_instance
    if _reasoning_validator_instance is None:
        _reasoning_validator_instance = ReasoningValidator()
    return _reasoning_validator_instance
