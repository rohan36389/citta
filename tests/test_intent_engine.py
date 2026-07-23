import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.conversation.models import (
    BusinessIntent,
    ConversationalIntent,
    IntentSource,
    ConversationContext
)
from backend.conversation.intent_engine import get_enterprise_intent_engine

class TestEnterpriseIntentEngine(unittest.TestCase):
    def setUp(self):
        self.engine = get_enterprise_intent_engine()

    def test_multi_intent_query(self):
        query = "Can Ecommerce integrate with SAP and what are the benefits?"
        res = self.engine.analyze(query)
        
        self.assertEqual(res.primary_intent.intent, BusinessIntent.INTEGRATION)
        self.assertGreater(len(res.secondary_intents), 0)
        secondary_intents = [s.intent for s in res.secondary_intents]
        self.assertIn(BusinessIntent.BENEFITS, secondary_intents)
        self.assertIn("KeywordSignal 'integrate'", res.primary_intent.reasoning)

    def test_misspellings_and_typos(self):
        query = "Tell me about the intrgration options and priceing for archtecture"
        res = self.engine.analyze(query)
        
        detected_intents = [res.primary_intent.intent] + [s.intent for s in res.secondary_intents]
        self.assertIn(BusinessIntent.INTEGRATION, detected_intents)
        self.assertIn(BusinessIntent.PRICING, detected_intents)
        self.assertIn(BusinessIntent.ARCHITECTURE, detected_intents)

    def test_context_dependent_pricing(self):
        ctx = ConversationContext(session_id="s123", active_entity_id="enterprise_ai_os")
        query = "What about pricing?"
        res = self.engine.analyze(query, context=ctx)
        
        self.assertEqual(res.primary_intent.intent, BusinessIntent.PRICING)
        # Verify MemorySignal provenance
        memory_signals = [s for s in res.primary_intent.signals if s.source == IntentSource.MEMORY]
        self.assertGreater(len(memory_signals), 0)
        self.assertIn("active_entity=enterprise_ai_os", memory_signals[0].value)

    def test_comparison_with_industry(self):
        query = "Compare Enterprise AI and WhatsApp Marketing for healthcare."
        res = self.engine.analyze(query)
        
        self.assertEqual(res.primary_intent.intent, BusinessIntent.COMPARISON)
        secondary_intents = [s.intent for s in res.secondary_intents]
        self.assertIn(BusinessIntent.INDUSTRIES, secondary_intents)

    def test_conflicting_intents(self):
        query = "Book a demo but first compare with Salesforce"
        res = self.engine.analyze(query)
        
        detected_intents = [res.primary_intent.intent] + [s.intent for s in res.secondary_intents]
        self.assertIn(BusinessIntent.DEMO_REQUEST, detected_intents)
        self.assertIn(BusinessIntent.COMPARISON, detected_intents)

    def test_conversational_greeting(self):
        query = "Good morning!"
        res = self.engine.analyze(query)
        
        self.assertEqual(res.primary_intent.intent, BusinessIntent.UNKNOWN)
        self.assertIsNotNone(res.conversational_intent)
        self.assertEqual(res.conversational_intent.intent, ConversationalIntent.GREETING)

    def test_ambiguous_tell_me_more(self):
        ctx = ConversationContext(session_id="s456", active_entity_id="pharma_os")
        query = "Tell me more"
        res = self.engine.analyze(query, context=ctx)
        
        self.assertIsNotNone(res.conversational_intent)
        self.assertEqual(res.conversational_intent.intent, ConversationalIntent.CONTINUE_TOPIC)
        conv_signals = [s for s in res.conversational_intent.signals if s.source == IntentSource.CONVERSATION_CONTEXT]
        self.assertGreater(len(conv_signals), 0)

if __name__ == "__main__":
    unittest.main()
