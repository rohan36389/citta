import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.conversation.models import (
    RolePersona,
    PersonaProfile,
    CommunicationPreferences,
    IntentAnalysis,
    ConversationContext
)
from backend.conversation.suggestion_engine import get_suggestion_engine

class TestSuggestionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = get_suggestion_engine()

    def test_dynamic_suggestion_generation_for_ecommerce(self):
        ctx = ConversationContext(session_id="sug_test_1", active_entity_id="Ecommerce OS")
        intent = IntentAnalysis(primary_intent="overview")

        res = self.engine.generate(intent, None, ctx)

        self.assertGreater(len(res.suggestions), 0)
        labels = [s.label for s in res.suggestions]
        # Check presence of dynamic questions
        self.assertTrue(any("How does Ecommerce OS work?" in l for l in labels))
        self.assertTrue(any("integrations" in l.lower() for l in labels))
        self.assertIsNotNone(res.top_suggestion)
        self.assertGreater(res.top_suggestion.confidence, 0.70)
        self.assertIsNotNone(res.top_suggestion.reasoning)

    def test_registry_comparison_suggestions(self):
        ctx = ConversationContext(session_id="sug_comp_test", active_entity_id="Ecommerce OS")
        intent = IntentAnalysis(primary_intent="overview")

        res = self.engine.generate(intent, None, ctx)

        labels = [s.label for s in res.suggestions]
        # Check that registry lookup generated comparison chips with sibling entities
        self.assertTrue(any("Compare Ecommerce OS with" in l for l in labels))

    def test_persona_adapted_developer_suggestions(self):
        ctx = ConversationContext(session_id="sug_dev_test", active_entity_id="Ecommerce OS")
        intent = IntentAnalysis(primary_intent="integration")
        persona = PersonaProfile(
            role_probabilities={RolePersona.DEVELOPER: 0.90},
            primary_role=RolePersona.DEVELOPER,
            relationship=None,
            relationship_confidence=0.0,
            communication_preferences=CommunicationPreferences(technical_depth="Deep Technical", executive_focus=0.1, detail_density="Detailed", prefer_code_snippets=True),
            profile_stability=0.9,
            reasoning="Developer persona detected"
        )

        res = self.engine.generate(intent, persona, ctx)

        labels = [s.label for s in res.suggestions]
        self.assertTrue(any("APIs and webhooks" in l for l in labels))

    def test_persona_adapted_executive_suggestions(self):
        ctx = ConversationContext(session_id="sug_exec_test", active_entity_id="Ecommerce OS")
        intent = IntentAnalysis(primary_intent="pricing")
        persona = PersonaProfile(
            role_probabilities={RolePersona.EXECUTIVE_DECISION_MAKER: 0.90},
            primary_role=RolePersona.EXECUTIVE_DECISION_MAKER,
            relationship=None,
            relationship_confidence=0.0,
            communication_preferences=CommunicationPreferences(technical_depth="Executive", executive_focus=0.95, detail_density="Concise"),
            profile_stability=0.9,
            reasoning="Executive persona detected"
        )

        res = self.engine.generate(intent, persona, ctx)

        labels = [s.label for s in res.suggestions]
        self.assertTrue(any("ROI" in l or "demo" in l.lower() for l in labels))

    def test_deduplication_filters_past_user_queries(self):
        ctx = ConversationContext(session_id="sug_dedup_test", active_entity_id="Ecommerce OS")
        ctx.history.append({"role": "user", "content": "How does Ecommerce OS work?"})
        intent = IntentAnalysis(primary_intent="overview")

        res = self.engine.generate(intent, None, ctx)

        labels = [s.label for s in res.suggestions]
        self.assertNotIn("How does Ecommerce OS work?", labels)

if __name__ == "__main__":
    unittest.main()
