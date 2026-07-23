import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.conversation import get_conversation_manager
from backend.conversation.models import (
    ResponseComposition,
    RolePersona,
    BusinessIntent,
    ValidationReport
)

class TestFullPipelineIntegration(unittest.TestCase):
    def test_full_conversation_intelligence_pipeline_turn_1(self):
        manager = get_conversation_manager()
        session_id = "full_integration_s1"
        
        # Turn 1: User asks about Ecommerce OS as a developer
        query1 = "Tell me about Ecommerce OS and what REST APIs and webhooks are supported."
        res1 = manager.process_turn(query1, session_id)

        self.assertIsInstance(res1, ResponseComposition)
        self.assertIsNotNone(res1.text)
        self.assertGreater(len(res1.suggestions), 0)
        self.assertIsNotNone(res1.explainability)
        
        # Verify Persona Detection (Developer)
        ctx = manager.context_engine.get_or_create_context(session_id)
        persona = ctx.variables.get("persona_profile")
        self.assertIsNotNone(persona)
        self.assertEqual(persona.primary_role, RolePersona.DEVELOPER)

        # Verify Response Plan (Technical Deep Dive / Educational)
        plan = ctx.variables.get("response_plan")
        self.assertIsNotNone(plan)
        self.assertEqual(plan.depth, "Deep Technical Specs")

        # Verify Validation Report
        val_report = ctx.variables.get("validation_report")
        self.assertIsInstance(val_report, ValidationReport)
        self.assertTrue(val_report.is_valid)

    def test_coreference_pronoun_resolution_turn_2(self):
        manager = get_conversation_manager()
        session_id = "full_integration_s2"

        # Turn 1: Establish active entity (Ecommerce OS)
        manager.process_turn("Tell me about Ecommerce OS.", session_id)

        # Turn 2: Follow-up query using pronoun "it"
        res2 = manager.process_turn("How scalable is it?", session_id)

        self.assertIsInstance(res2, ResponseComposition)
        ctx = manager.context_engine.get_or_create_context(session_id)
        
        # Verify active entity remains Ecommerce OS
        self.assertEqual(ctx.active_entity_id, "ecommerce_os")
        
        # Verify suggestions generated dynamically
        self.assertGreater(len(res2.suggestions), 0)

    def test_deterministic_engine_fallback_behavior(self):
        manager = get_conversation_manager()
        session_id = "full_integration_s3"

        # Query about leadership (handled deterministically)
        res = manager.process_turn("Who is the CEO of CittaAI?", session_id)

        self.assertIsInstance(res, ResponseComposition)
        self.assertIsNotNone(res.text)

if __name__ == "__main__":
    unittest.main()
