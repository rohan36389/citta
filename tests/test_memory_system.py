import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.conversation.models import (
    EntityNode,
    WorkingMemory,
    MemoryEvent
)
from backend.conversation.memory_engine import get_memory_manager
from backend.conversation.coreference_engine import get_coreference_engine

class TestConversationMemorySystem(unittest.TestCase):
    def setUp(self):
        self.session_id = "mem_test_session"
        self.mem_mgr = get_memory_manager(self.session_id)
        self.coref_engine = get_coreference_engine()

    def test_pronoun_resolution_high_confidence(self):
        # 1. Simulate Turn 1: Entity detected (Ecommerce OS)
        event = MemoryEvent(
            event_type="ENTITY_DETECTED",
            payload={"entity_id": "ecommerce_os", "name": "Ecommerce OS", "registry": "SOLUTIONS"},
            turn=1
        )
        self.mem_mgr.apply_event(event)

        # 2. Turn 2: User asks "How scalable is it?"
        res = self.coref_engine.resolve("How scalable is it?", self.mem_mgr.working_memory, turn=2)

        self.assertFalse(res.requires_clarification)
        self.assertGreaterEqual(res.confidence, 0.75)
        self.assertEqual(res.selected_entity.entity_id, "ecommerce_os")
        self.assertEqual(res.resolved_query, "How scalable is Ecommerce OS?")

    def test_low_confidence_clarification(self):
        # Empty working memory (no active entities)
        empty_wm = WorkingMemory()
        res = self.coref_engine.resolve("How scalable is it?", empty_wm, turn=1)

        self.assertTrue(res.requires_clarification)
        self.assertLess(res.confidence, 0.45)
        self.assertIsNone(res.selected_entity)

    def test_entity_graph_and_stack(self):
        # Add first entity
        self.mem_mgr.apply_event(MemoryEvent(
            event_type="ENTITY_DETECTED",
            payload={"entity_id": "enterprise_ai_os", "name": "Enterprise AI OS", "registry": "SOLUTIONS"},
            turn=1
        ))
        
        # Add second entity
        self.mem_mgr.apply_event(MemoryEvent(
            event_type="ENTITY_DETECTED",
            payload={"entity_id": "pharma_os", "name": "Pharma OS", "registry": "SOLUTIONS"},
            turn=2
        ))

        wm = self.mem_mgr.working_memory
        self.assertEqual(wm.current_entity.entity_id, "pharma_os")
        self.assertEqual(len(wm.recent_entities), 1)
        self.assertEqual(wm.recent_entities[0].entity_id, "enterprise_ai_os")

    def test_semantic_question_signatures(self):
        # Mark question answered
        self.mem_mgr.apply_event(MemoryEvent(
            event_type="QUESTION_ANSWERED",
            payload={"entity_id": "ecommerce_os", "intent": "overview"},
            turn=1
        ))

        self.assertTrue(self.mem_mgr.is_question_already_answered("ecommerce_os", "overview"))
        self.assertFalse(self.mem_mgr.is_question_already_answered("ecommerce_os", "pricing"))

    def test_business_memory_events(self):
        self.mem_mgr.apply_event(MemoryEvent(
            event_type="GOAL_IDENTIFIED",
            payload={"goal": "Automate inventory processing"},
            turn=1
        ))
        self.mem_mgr.apply_event(MemoryEvent(
            event_type="OBJECTION_RAISED",
            payload={"objection": "Custom integration timeline"},
            turn=2
        ))

        bm = self.mem_mgr.business_memory
        self.assertIn("Automate inventory processing", bm.customer_facts.goals)
        self.assertIn("Custom integration timeline", bm.objections_raised)

if __name__ == "__main__":
    unittest.main()
