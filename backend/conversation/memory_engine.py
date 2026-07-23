import hashlib
import logging
from typing import Dict, Any, List, Optional
from backend.conversation.models import (
    EntityNode,
    WorkingMemory,
    CustomerFacts,
    BusinessMemory,
    QuestionSignature,
    FollowUpOpportunity,
    MemoryEvent,
    ConversationContext
)

logger = logging.getLogger(__name__)

class ConversationMemoryManager:
    """
    Manages session-level WorkingMemory, BusinessMemory, Entity Graph,
    and handles structured event-driven memory updates (apply_event).
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.working_memory = WorkingMemory()
        self.business_memory = BusinessMemory()
        self.entity_graph: Dict[str, EntityNode] = {}

    def apply_event(self, event: MemoryEvent) -> None:
        """
        Single-source-of-truth event dispatcher updating Working & Business memory state.
        """
        e_type = event.event_type
        payload = event.payload
        turn = event.turn

        if e_type == "ENTITY_DETECTED":
            ent_id = payload.get("entity_id")
            name = payload.get("name", ent_id)
            registry = payload.get("registry", "UNKNOWN")

            if not ent_id:
                return

            # Update or create EntityNode in Entity Graph
            if ent_id in self.entity_graph:
                node = self.entity_graph[ent_id]
                node.mention_count += 1
                node.last_turn = turn
            else:
                node = EntityNode(
                    entity_id=ent_id,
                    name=name,
                    registry=registry,
                    mention_count=1,
                    first_turn=turn,
                    last_turn=turn
                )
                self.entity_graph[ent_id] = node

            # If active current_entity is changing, push old to recent_entities stack
            curr = self.working_memory.current_entity
            if curr and curr.entity_id != ent_id:
                # Add to recent_entities if not already present
                if not any(n.entity_id == curr.entity_id for n in self.working_memory.recent_entities):
                    self.working_memory.recent_entities.insert(0, curr)
                    # Limit stack to 10 entities
                    if len(self.working_memory.recent_entities) > 10:
                        self.working_memory.recent_entities.pop()

            self.working_memory.current_entity = node
            self.working_memory.active_registry = registry

        elif e_type == "GOAL_IDENTIFIED":
            goal = payload.get("goal")
            if goal and goal not in self.business_memory.customer_facts.goals:
                self.business_memory.customer_facts.goals.append(goal)

        elif e_type == "OBJECTION_RAISED":
            objection = payload.get("objection")
            if objection and objection not in self.business_memory.objections_raised:
                self.business_memory.objections_raised.append(objection)

        elif e_type == "RECOMMENDATION_GIVEN":
            rec = payload.get("recommendation")
            if rec and rec not in self.business_memory.recommendations_given:
                self.business_memory.recommendations_given.append(rec)

        elif e_type == "QUESTION_ANSWERED":
            ent_id = payload.get("entity_id", "general")
            intent = payload.get("intent", "general")
            sig_raw = f"{ent_id}:{intent}".lower()
            sig_hash = hashlib.md5(sig_raw.encode("utf-8")).hexdigest()

            q_sig = QuestionSignature(
                entity_id=ent_id,
                intent=intent,
                signature_hash=sig_hash,
                answered_turn=turn
            )
            if not any(q.signature_hash == sig_hash for q in self.business_memory.questions_answered):
                self.business_memory.questions_answered.append(q_sig)

        logger.info(f"MemoryManager[{self.session_id}]: Applied event '{e_type}' on turn {turn}")

    def is_question_already_answered(self, entity_id: str, intent: str) -> bool:
        """
        Checks if a question with given entity and intent signature was answered.
        """
        sig_raw = f"{entity_id}:{intent}".lower()
        sig_hash = hashlib.md5(sig_raw.encode("utf-8")).hexdigest()
        return any(q.signature_hash == sig_hash for q in self.business_memory.questions_answered)

    def add_follow_up_opportunity(self, topic: str, priority: float, reason: str, turn: int) -> None:
        """Adds structured follow-up opportunity to queue."""
        opp = FollowUpOpportunity(topic=topic, priority=priority, reason=reason, suggested_turn=turn)
        self.business_memory.follow_up_opportunities.append(opp)
        self.business_memory.follow_up_opportunities.sort(key=lambda o: o.priority, reverse=True)


_managers: Dict[str, ConversationMemoryManager] = {}

def get_memory_manager(session_id: str) -> ConversationMemoryManager:
    global _managers
    if session_id not in _managers:
        _managers[session_id] = ConversationMemoryManager(session_id)
    return _managers[session_id]
