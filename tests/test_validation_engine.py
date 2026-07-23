import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.conversation.models import (
    ValidationSeverity,
    ResponsePlan,
    ResponseStrategyType,
    ConversationContext
)
from backend.conversation.validation_engine import get_conversation_validation_engine

class TestConversationValidationEngine(unittest.TestCase):
    def setUp(self):
        self.validator = get_conversation_validation_engine()

    def test_entity_existence_rule_pass(self):
        ctx = ConversationContext(session_id="val_test_1", active_entity_id="ecommerce_os")
        report = self.validator.validate("CittaAI Ecommerce OS is scalable.", "overview", None, ctx)

        self.assertTrue(report.is_valid)
        self.assertFalse(report.is_fallback_triggered)
        r1 = [r for r in report.rule_results if r.rule_name == "EntityExistenceRule"][0]
        self.assertTrue(r1.passed)

    def test_nonexistent_entity_triggers_fallback(self):
        ctx = ConversationContext(session_id="val_test_2", active_entity_id="fake_nonexistent_entity_xyz")
        report = self.validator.validate("Fake entity response.", "overview", None, ctx)

        self.assertFalse(report.is_valid)
        self.assertTrue(report.is_fallback_triggered)
        self.assertIn("Thank you for inquiring about fake_nonexistent_entity_xyz", report.repaired_text)

    def test_deduplication_rule_self_repairs_repeated_sentences(self):
        ctx = ConversationContext(session_id="val_test_3", active_entity_id="ecommerce_os")
        text_with_dups = "CittaAI features REST API connections. CittaAI features REST API connections. Microservices architecture is supported."

        report = self.validator.validate(text_with_dups, "overview", None, ctx)

        self.assertTrue(report.is_valid)
        self.assertTrue(report.is_repaired)
        self.assertEqual(
            report.repaired_text,
            "CittaAI features REST API connections. Microservices architecture is supported."
        )

    def test_hallucination_check_triggers_fallback(self):
        ctx = ConversationContext(session_id="val_test_4", active_entity_id="ecommerce_os")
        fake_text = "Check out our secret features at http://fake-domain-123.com for FAKE_API_KEY_9999."

        report = self.validator.validate(fake_text, "overview", None, ctx)

        self.assertFalse(report.is_valid)
        self.assertTrue(report.is_fallback_triggered)
        r4 = [r for r in report.rule_results if r.rule_name == "GroundingHallucinationRule"][0]
        self.assertFalse(r4.passed)
        self.assertEqual(r4.severity, ValidationSeverity.CRITICAL)

    def test_conflict_detection_warning(self):
        ctx = ConversationContext(session_id="val_test_5", active_entity_id="ecommerce_os")
        conflict_text = "The platform is 100% free for all users, but costs $500 per month."

        report = self.validator.validate(conflict_text, "pricing", None, ctx)

        r5 = [r for r in report.rule_results if r.rule_name == "ConflictDetectionRule"][0]
        self.assertFalse(r5.passed)
        self.assertEqual(r5.severity, ValidationSeverity.WARNING)

    def test_tone_sanitization_repair(self):
        ctx = ConversationContext(session_id="val_test_6", active_entity_id="ecommerce_os")
        informal_text = "Dude, CittaAI Ecommerce OS is awesome."

        report = self.validator.validate(informal_text, "overview", None, ctx)

        self.assertTrue(report.is_repaired)
        self.assertNotIn("dude", report.repaired_text.lower())

if __name__ == "__main__":
    unittest.main()
