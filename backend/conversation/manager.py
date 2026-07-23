import time
import logging
from typing import Dict, Any, Optional

from backend.conversation.models import (
    ConversationContext,
    ResponseComposition
)
from backend.conversation.interfaces import (
    IContextEngine,
    IUnderstandingEngine,
    IKnowledgeEngine,
    IStrategyEngine,
    IPromptEngine,
    IResponseEngine,
    IQualityEngine,
    IAnalyticsEngine
)

logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Orchestrates the entire Conversational Intelligence Pipeline, 
    transforming queries step-by-step through:
    Context -> Intent -> Discovery -> Strategy -> Tools -> Knowledge -> Compose -> Critic -> composition.
    """
    def __init__(
        self,
        context_engine: IContextEngine,
        understanding_engine: IUnderstandingEngine,
        knowledge_engine: IKnowledgeEngine,
        strategy_engine: IStrategyEngine,
        prompt_engine: IPromptEngine,
        response_engine: IResponseEngine,
        quality_engine: IQualityEngine,
        analytics_engine: IAnalyticsEngine
    ):
        self.context_engine = context_engine
        self.understanding_engine = understanding_engine
        self.knowledge_engine = knowledge_engine
        self.strategy_engine = strategy_engine
        self.prompt_engine = prompt_engine
        self.response_engine = response_engine
        self.quality_engine = quality_engine
        self.analytics_engine = analytics_engine

    def process_turn(self, query: str, session_id: str) -> ResponseComposition:
        """
        Executes the pre-sales dialog pipeline transformation.
        """
        timings: Dict[str, float] = {}
        
        # 1. Context Engine retrieves current context
        t_start = time.perf_counter()
        context = self.context_engine.get_or_create_context(session_id)
        timings["context_ms"] = (time.perf_counter() - t_start) * 1000.0

        # 2. Understanding Engine analyzes intent & discovery indicators
        t_now = time.perf_counter()
        intent = self.understanding_engine.analyze_intent(query, context)
        discovery = self.understanding_engine.run_discovery(query, intent, context)
        lead_qual = self.understanding_engine.qualify_lead(discovery)
        timings["understanding_ms"] = (time.perf_counter() - t_now) * 1000.0

        # 3. Context Engine evaluates stage transition
        t_now = time.perf_counter()
        p_intent = intent.primary_intent.lower()
        if p_intent in ["demo_scheduling", "demo request"]:
            self.context_engine.transition_stage(context, "Demo Scheduling")
        elif p_intent in ["pricing_inquiry", "pricing"]:
            self.context_engine.transition_stage(context, "Objection Handling")
        elif context.current_stage == "Greeting":
            self.context_engine.transition_stage(context, "Discovery")
        timings["stage_transition_ms"] = (time.perf_counter() - t_now) * 1000.0

        # 4. Knowledge Engine matches tools and orchestrates evidence
        t_now = time.perf_counter()
        tool_sel = self.knowledge_engine.select_tools(intent, context)
        retrieved_data = self.knowledge_engine.orchestrate_knowledge(tool_sel, query)
        is_gap = self.knowledge_engine.detect_knowledge_gap(retrieved_data, query)
        timings["knowledge_ms"] = (time.perf_counter() - t_now) * 1000.0

        # 5. Strategy Engine formulates response strategy
        t_now = time.perf_counter()
        strategy = self.strategy_engine.formulate_strategy(intent, discovery, context)
        plan = self.strategy_engine.plan_response(strategy, context)
        timings["strategy_ms"] = (time.perf_counter() - t_now) * 1000.0

        # 6. Prompt Engine prepares templates
        t_now = time.perf_counter()
        sys_prompt = self.prompt_engine.build_system_prompt(context, strategy)
        usr_prompt = self.prompt_engine.build_user_prompt(query, retrieved_data)
        timings["prompt_ms"] = (time.perf_counter() - t_now) * 1000.0

        # 7. Response Engine drafts responses & dynamically extracts suggestion chips
        t_now = time.perf_counter()
        draft = self.response_engine.compose_draft(sys_prompt, usr_prompt, strategy, context)
        suggestions = self.response_engine.generate_suggestions(draft, context)
        draft.suggestions = suggestions
        timings["response_ms"] = (time.perf_counter() - t_now) * 1000.0

        # 8. Quality Engine reviews draft, checks grounding, and writes explainability trace
        t_now = time.perf_counter()
        review = self.quality_engine.review_draft(draft, context)
        is_valid = self.quality_engine.validate_facts(draft, retrieved_data)
        
        explainability = self.quality_engine.create_explainability_record(
            context, intent, strategy, review, timings
        )
        timings["quality_ms"] = (time.perf_counter() - t_now) * 1000.0

        # 9. Formulate final response composition payload
        final_text = review.suggested_rewrite or draft.text
        
        # In Greeting state, if we want to suggest explorer redirects
        redirect_url: Optional[str] = None
        if intent.primary_intent == "demo_scheduling":
            redirect_url = "/contact"

        composition = ResponseComposition(
            text=final_text,
            suggestions=suggestions,
            redirect_url=redirect_url,
            explainability=explainability,
            metadata={
                "lead_score": lead_qual.score,
                "interest_level": lead_qual.interest_level,
                "next_best_action": lead_qual.next_best_action,
                "knowledge_gap": is_gap
            }
        )

        # 10. Update historical context
        context.history.append({"role": "user", "content": query})
        context.history.append({"role": "assistant", "content": final_text})
        self.context_engine.update_context(context, {"history": context.history})

        # 11. Analytics Engine logs telemetry metrics
        self.analytics_engine.track_turn(context, composition)

        return composition
