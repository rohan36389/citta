import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.conversation.models import (
    RolePersona,
    RelationshipPersona,
    ConversationContext
)
from backend.conversation.persona_engine import get_customer_persona_engine

class TestCustomerPersonaEngine(unittest.TestCase):
    def setUp(self):
        self.engine = get_customer_persona_engine()

    def test_mixed_persona_cto_and_developer(self):
        query = "I'm the CTO but I also write our backend services in Python."
        profile = self.engine.process(query)
        
        # Verify both CTO and Developer have top scores in distribution
        probs = profile.role_probabilities
        self.assertGreater(probs[RolePersona.TECHNICAL_ARCHITECT], 0.20)
        self.assertGreater(probs[RolePersona.DEVELOPER], 0.20)
        self.assertIn(profile.primary_role, [RolePersona.TECHNICAL_ARCHITECT, RolePersona.DEVELOPER])
        self.assertTrue(profile.communication_preferences.prefer_code_snippets)

    def test_existing_customer_relationship(self):
        query = "We are already using Enterprise AI and need to upgrade our account."
        profile = self.engine.process(query)
        
        self.assertEqual(profile.relationship, RelationshipPersona.EXISTING_CUSTOMER)
        self.assertGreater(profile.relationship_confidence, 0.70)

    def test_negative_evidence_subtraction(self):
        query = "I don't know programming, non-technical background. Show me business ROI."
        profile = self.engine.process(query)
        
        probs = profile.role_probabilities
        # Developer and Architect probabilities should be suppressed due to negative signals
        self.assertLess(probs[RolePersona.DEVELOPER], 0.15)
        self.assertEqual(profile.primary_role, RolePersona.EXECUTIVE_DECISION_MAKER)
        self.assertGreater(profile.communication_preferences.executive_focus, 0.80)

    def test_persona_shift_over_turns(self):
        ctx = ConversationContext(session_id="shift_test")
        
        # Turn 1: Academic / Student
        t1_profile = self.engine.process("I am a student doing a project, explain simply.", ctx)
        ctx.turn_count += 1
        self.assertEqual(t1_profile.primary_role, RolePersona.ACADEMIC_STUDENT)
        
        # Turn 2: Developer technical turn
        t2_profile = self.engine.process("Actually, how do I configure OAuth scopes, API tokens and webhooks?", ctx)
        ctx.turn_count += 1
        self.assertEqual(t2_profile.primary_role, RolePersona.DEVELOPER)
        self.assertTrue(t2_profile.communication_preferences.prefer_code_snippets)

    def test_ambiguous_query_stays_unknown(self):
        query = "Tell me more"
        profile = self.engine.process(query)
        
        self.assertEqual(profile.primary_role, RolePersona.UNKNOWN)
        self.assertLessEqual(profile.profile_stability, 0.50)

if __name__ == "__main__":
    unittest.main()
