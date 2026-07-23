import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.conversation.models import (
    BusinessIntent,
    RolePersona,
    ResponseStrategyType,
    IntentAnalysis,
    PersonaProfile,
    CommunicationPreferences,
    ConversationContext
)
from backend.conversation.planning_engine import get_response_planning_engine

class TestResponsePlanningEngine(unittest.TestCase):
    def setUp(self):
        self.engine = get_response_planning_engine()

    def test_executive_summary_strategy(self):
        intent = IntentAnalysis(primary_intent="pricing")
        persona = PersonaProfile(
            role_probabilities={RolePersona.EXECUTIVE_DECISION_MAKER: 0.90},
            primary_role=RolePersona.EXECUTIVE_DECISION_MAKER,
            relationship=None,
            relationship_confidence=0.0,
            communication_preferences=CommunicationPreferences(technical_depth="Executive", executive_focus=0.9, detail_density="Concise"),
            profile_stability=0.9,
            reasoning="Executive persona detected"
        )
        ctx = ConversationContext(session_id="exec_test", active_entity_id="enterprise_ai_os")

        plan = self.engine.plan(intent, persona, ctx)

        self.assertEqual(plan.strategy_type, ResponseStrategyType.EXECUTIVE_SUMMARY)
        self.assertIn("Strategic", plan.tone)
        self.assertGreater(len(plan.sections), 0)
        self.assertIsNotNone(plan.cta)
        self.assertIn("executive persona", plan.selection_reasoning)

    def test_technical_deep_dive_strategy(self):
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
        ctx = ConversationContext(session_id="tech_test", active_entity_id="ecommerce_os")

        plan = self.engine.plan(intent, persona, ctx)

        self.assertEqual(plan.strategy_type, ResponseStrategyType.TECHNICAL_DEEP_DIVE)
        self.assertEqual(plan.depth, "Deep Technical Specs")
        self.assertGreater(len(plan.sections), 0)

    def test_comparison_strategy(self):
        intent = IntentAnalysis(primary_intent="comparison")
        ctx = ConversationContext(session_id="comp_test")

        plan = self.engine.plan(intent, None, ctx)

        self.assertEqual(plan.strategy_type, ResponseStrategyType.COMPARISON)
        self.assertEqual(plan.sections[0].title, "Comparative Overview")

    def test_case_study_strategy(self):
        intent = IntentAnalysis(primary_intent="case_studies")
        ctx = ConversationContext(session_id="cs_test")

        plan = self.engine.plan(intent, None, ctx)

        self.assertEqual(plan.strategy_type, ResponseStrategyType.CASE_STUDY)
        self.assertIn("Client", plan.sections[0].title)

    def test_troubleshooting_strategy(self):
        intent = IntentAnalysis(primary_intent="support")
        ctx = ConversationContext(session_id="trouble_test")

        plan = self.engine.plan(intent, None, ctx)

        self.assertEqual(plan.strategy_type, ResponseStrategyType.TROUBLESHOOTING)
        self.assertIn("Symptom", plan.sections[0].title)

    def test_all_13_strategies_defined(self):
        from backend.conversation.planning_engine import STRATEGY_TEMPLATES
        for strat in ResponseStrategyType:
            self.assertIn(strat, STRATEGY_TEMPLATES)
            t = STRATEGY_TEMPLATES[strat]
            self.assertIn("tone", t)
            self.assertIn("depth", t)
            self.assertIn("sections", t)
            self.assertIn("follow_up", t)
            self.assertIn("cta", t)

if __name__ == "__main__":
    unittest.main()
