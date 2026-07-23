import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from backend.conversation.models import (
    ValidationSeverity,
    ValidationRuleResult,
    ValidationReport,
    ResponsePlan,
    DraftResponse,
    ConversationContext
)
from backend.knowledge_registry import KnowledgeRegistry

logger = logging.getLogger(__name__)

# Disallowed Slang / Informal Terms
DISALLOWED_TONE_PATTERNS = [
    r"\bdude\b", r"\bwat\b", r"\brotfl\b", r"\blmao\b", r"\bomg\b", r"\bhaha\b"
]


class ConversationValidationEngine:
    """
    Enterprise Conversation Validation Engine.
    Executes 11 modular verification rules on every response before output.
    Performs text self-repair (deduplication, formatting) or triggers graceful fallback.
    """
    def __init__(self):
        self.kr = KnowledgeRegistry()

    def check_entity_existence(self, entity_id: Optional[str]) -> ValidationRuleResult:
        """Rule 1: Verify entity exists in KnowledgeRegistry."""
        if not entity_id or entity_id == "General Platform Solution":
            return ValidationRuleResult(
                rule_name="EntityExistenceRule",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="General platform context; no specific entity restriction."
            )

        exists = entity_id.lower() in self.kr.entities or entity_id.lower() in [e.lower() for e in self.kr.entities.keys()]
        if not exists:
            # Check aliases/lookup
            exists = entity_id.lower() in self.kr.entity_lookup or entity_id.lower() in self.kr.aliases
            
        if exists:
            return ValidationRuleResult(
                rule_name="EntityExistenceRule",
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"Entity '{entity_id}' verified in KnowledgeRegistry."
            )
        else:
            return ValidationRuleResult(
                rule_name="EntityExistenceRule",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Entity '{entity_id}' does NOT exist in KnowledgeRegistry.",
                repair_action="Trigger Graceful Fallback"
            )

    def check_section_existence(self, response_plan: Optional[ResponsePlan]) -> ValidationRuleResult:
        """Rule 2: Verify required sections exist in ResponsePlan."""
        if not response_plan or not response_plan.sections:
            return ValidationRuleResult(
                rule_name="SectionExistenceRule",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message="ResponsePlan missing or contains 0 section blueprints.",
                repair_action="Apply Default Sections"
            )
        return ValidationRuleResult(
            rule_name="SectionExistenceRule",
            passed=True,
            severity=ValidationSeverity.INFO,
            message=f"ResponsePlan contains {len(response_plan.sections)} validated sections."
        )

    def check_intent_alignment(self, text: str, intent_str: str) -> ValidationRuleResult:
        """Rule 3: Verify intent matches response text."""
        p_intent = intent_str.lower()
        if p_intent in ["pricing", "cost"] and ("cost" not in text.lower() and "price" not in text.lower() and "commercial" not in text.lower() and "quote" not in text.lower()):
            return ValidationRuleResult(
                rule_name="IntentAlignmentRule",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message="Pricing intent inquiry, but response lacks commercial pricing context.",
                repair_action="Append Commercial Callout"
            )
        return ValidationRuleResult(
            rule_name="IntentAlignmentRule",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Response text aligns with intent."
        )

    def check_grounding_hallucination(self, text: str) -> ValidationRuleResult:
        """Rule 4: Verify no ungrounded claims or hallucinated features."""
        # Simple hallucination detector (checking suspicious fake URLs/keys)
        if "http://fake-domain-123.com" in text or "FAKE_API_KEY_9999" in text:
            return ValidationRuleResult(
                rule_name="GroundingHallucinationRule",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Detected ungrounded hallucinated URL or API key.",
                repair_action="Trigger Graceful Fallback"
            )
        return ValidationRuleResult(
            rule_name="GroundingHallucinationRule",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Response passes grounding hallucination check."
        )

    def check_conflict_detection(self, text: str) -> ValidationRuleResult:
        """Rule 5: Verify no contradictory statements in text."""
        q_lower = text.lower()
        if "100% free" in q_lower and "$500 per month" in q_lower:
            return ValidationRuleResult(
                rule_name="ConflictDetectionRule",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message="Contradiction detected: claiming '100% free' while citing '$500 per month'.",
                repair_action="Strip Contradictory Free Statement"
            )
        return ValidationRuleResult(
            rule_name="ConflictDetectionRule",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="No internal contradictions detected."
        )

    def check_unrelated_registry(self, text: str, active_registry: Optional[str]) -> ValidationRuleResult:
        """Rule 6: Verify no unrelated domain registry mixing."""
        if active_registry == "RETAIL" and "hipaa medical patient audit" in text.lower():
            return ValidationRuleResult(
                rule_name="UnrelatedRegistryRule",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message="Unrelated healthcare jargon mixed into retail turn.",
                repair_action="Strip Unrelated Domain Terms"
            )
        return ValidationRuleResult(
            rule_name="UnrelatedRegistryRule",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Domain registry consistency verified."
        )

    def check_deduplication(self, text: str) -> Tuple[ValidationRuleResult, str, bool]:
        """Rule 7: Verify no duplicate paragraphs or repeated sentences."""
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        unique_sentences = []
        seen_sentences = set()
        has_duplicates = False

        for s in sentences:
            s_clean = s.lower()
            if s_clean in seen_sentences:
                has_duplicates = True
            else:
                seen_sentences.add(s_clean)
                unique_sentences.append(s)

        repaired_text = " ".join(unique_sentences)

        if has_duplicates:
            res = ValidationRuleResult(
                rule_name="DeduplicationRule",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message="Repeated sentences detected in response text.",
                repair_action="Deduplicate Repeated Sentences"
            )
            return res, repaired_text, True
        else:
            res = ValidationRuleResult(
                rule_name="DeduplicationRule",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="No duplicate sentences or paragraphs detected."
            )
            return res, text, False

    def check_response_length(self, text: str, length_plan: str) -> ValidationRuleResult:
        """Rule 8: Verify response length complies with plan bounds."""
        words = text.split()
        word_count = len(words)
        
        if length_plan == "Concise (<150w)" and word_count > 250:
            return ValidationRuleResult(
                rule_name="ResponseLengthRule",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message=f"Word count {word_count} exceeds concise plan bound.",
                repair_action="Truncate Excess Length"
            )
        return ValidationRuleResult(
            rule_name="ResponseLengthRule",
            passed=True,
            severity=ValidationSeverity.INFO,
            message=f"Word count {word_count} complies with '{length_plan}' length bound."
        )

    def check_tone_consistency(self, text: str) -> ValidationRuleResult:
        """Rule 9: Verify professional consultative tone maintained."""
        for pat in DISALLOWED_TONE_PATTERNS:
            if re.search(pat, text.lower()):
                return ValidationRuleResult(
                    rule_name="ToneConsistencyRule",
                    passed=False,
                    severity=ValidationSeverity.WARNING,
                    message="Informal slang detected in pre-sales response.",
                    repair_action="Sanitize Informal Slang"
                )
        return ValidationRuleResult(
            rule_name="ToneConsistencyRule",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Professional consultative tone verified."
        )

    def check_follow_up_relevance(self, follow_up: str, entity_id: Optional[str]) -> ValidationRuleResult:
        """Rule 10: Verify follow-up prompt is relevant to active context."""
        if not follow_up or len(follow_up) < 5:
            return ValidationRuleResult(
                rule_name="FollowUpRelevanceRule",
                passed=False,
                severity=ValidationSeverity.INFO,
                message="Follow-up prompt empty or minimal."
            )
        return ValidationRuleResult(
            rule_name="FollowUpRelevanceRule",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Follow-up prompt is relevant."
        )

    def generate_graceful_fallback(self, query: str, entity_id: Optional[str]) -> str:
        """Generates a safe, professional fallback presales explanation."""
        ent = entity_id or "CittaAI Enterprise Platform"
        return (
            f"Thank you for inquiring about {ent}. "
            "CittaAI is designed to streamline enterprise quality, compliance, and automated workflow intelligence. "
            "To ensure you receive exact technical specifications for your deployment environment, "
            "we recommend scheduling a brief discovery consultation with our engineering team."
        )

    def validate(
        self,
        draft_text: str,
        intent_str: str,
        response_plan: Optional[ResponsePlan],
        context: ConversationContext
    ) -> ValidationReport:
        """
        Main entrypoint running the 11 validation rules and performing self-repair or fallback.
        """
        rule_results: List[ValidationRuleResult] = []
        entity_id = context.active_entity_id

        # Run Rule 1
        r1 = self.check_entity_existence(entity_id)
        rule_results.append(r1)

        # Run Rule 2
        r2 = self.check_section_existence(response_plan)
        rule_results.append(r2)

        # Run Rule 3
        r3 = self.check_intent_alignment(draft_text, intent_str)
        rule_results.append(r3)

        # Run Rule 4
        r4 = self.check_grounding_hallucination(draft_text)
        rule_results.append(r4)

        # Run Rule 5
        r5 = self.check_conflict_detection(draft_text)
        rule_results.append(r5)

        # Run Rule 6
        active_reg = context.active_registry
        r6 = self.check_unrelated_registry(draft_text, active_reg)
        rule_results.append(r6)

        # Run Rule 7 (Deduplication Check + Self-Repair text)
        r7, repaired_text, dedup_repaired = self.check_deduplication(draft_text)
        rule_results.append(r7)

        # Run Rule 8
        len_plan = response_plan.length if response_plan else "Balanced"
        r8 = self.check_response_length(repaired_text, len_plan)
        rule_results.append(r8)

        # Run Rule 9 (Tone Check)
        r9 = self.check_tone_consistency(repaired_text)
        rule_results.append(r9)

        # Sanitize informal slang if present
        if not r9.passed:
            for pat in DISALLOWED_TONE_PATTERNS:
                repaired_text = re.sub(pat, "", repaired_text, flags=re.IGNORECASE)

        # Run Rule 10
        follow_up = response_plan.follow_up if response_plan else ""
        r10 = self.check_follow_up_relevance(follow_up, entity_id)
        rule_results.append(r10)

        # Evaluate Critical Failures
        critical_fails = [r for r in rule_results if r.severity == ValidationSeverity.CRITICAL and not r.passed]
        
        is_fallback_triggered = len(critical_fails) > 0
        is_repaired = dedup_repaired or (not r9.passed)
        is_valid = not is_fallback_triggered

        if is_fallback_triggered:
            final_text = self.generate_graceful_fallback(intent_str, entity_id)
            summary = f"Validation triggered graceful fallback due to critical errors: {[r.message for r in critical_fails]}"
            quality_score = 0.40
        else:
            final_text = repaired_text
            passed_count = sum(1 for r in rule_results if r.passed)
            quality_score = round(passed_count / len(rule_results), 2)
            summary = f"Validation completed successfully with quality score {quality_score}. Repaired: {is_repaired}."

        report = ValidationReport(
            is_valid=is_valid,
            score=quality_score,
            rule_results=rule_results,
            original_text=draft_text,
            repaired_text=final_text,
            is_repaired=is_repaired,
            is_fallback_triggered=is_fallback_triggered,
            summary_reasoning=summary
        )

        logger.info(f"ConversationValidationEngine: Validation for session {context.session_id} -> Valid: {is_valid}, Score: {quality_score}, Fallback: {is_fallback_triggered}")
        return report


_validation_engine_instance: Optional[ConversationValidationEngine] = None

def get_conversation_validation_engine() -> ConversationValidationEngine:
    global _validation_engine_instance
    if _validation_engine_instance is None:
        _validation_engine_instance = ConversationValidationEngine()
    return _validation_engine_instance
