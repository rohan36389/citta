import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.conversation import get_conversation_manager
from backend.conversation.models import ResponseComposition

class TestConversationalIntelligence(unittest.TestCase):
    def test_singleton_initialization(self):
        manager = get_conversation_manager()
        self.assertIsNotNone(manager)
        
        # Test second call returns the same instance
        manager2 = get_conversation_manager()
        self.assertIs(manager, manager2)

    def test_pipeline_greeting_turn(self):
        manager = get_conversation_manager()
        res = manager.process_turn("Hello!", "session_greet")
        
        self.assertIsInstance(res, ResponseComposition)
        self.assertIsNotNone(res.text)
        self.assertGreater(len(res.suggestions), 0)
        self.assertIsNotNone(res.explainability)
        self.assertEqual(res.explainability.intent, "general_inquiry")
        self.assertEqual(res.explainability.stage, "Discovery")
        
        # Discovery variables should have been modified/prepared
        ctx = manager.context_engine.get_or_create_context("session_greet")
        self.assertIn("discovery_state", ctx.variables)

    def test_pipeline_pricing_turn(self):
        manager = get_conversation_manager()
        # Initialize session to Discovery stage first
        manager.process_turn("Hello!", "session_price")
        res = manager.process_turn("How much does CittaAI cost?", "session_price")
        
        self.assertIsInstance(res, ResponseComposition)
        self.assertIn("objection", res.explainability.strategy.lower())
        self.assertEqual(res.metadata.get("interest_level"), "LOW")
        self.assertEqual(res.explainability.stage, "Objection Handling")

    def test_pipeline_technical_validation_turn(self):
        manager = get_conversation_manager()
        res = manager.process_turn("Can CittaAI integrate with our custom CRM APIs?", "session_tech")
        
        self.assertIsInstance(res, ResponseComposition)
        self.assertEqual(res.explainability.intent, "technical_validation")
        self.assertEqual(res.explainability.strategy, "Educational")

if __name__ == "__main__":
    unittest.main()
