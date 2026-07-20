import os
import time
import json
import asyncio
import logging
import inspect
from typing import Any, Dict, List, Optional, Tuple

import config
from execution_context import (
    RequestContext,
    UnderstandingResult,
    ExecutionPlan,
    PlanTask,
    RetrievalRequest,
    RetrievalResult,
    ResponsePlan,
    ValidationResult,
    ExecutionBudget,
    Event,
    ExecutionStep,
    CapabilityResult,
    ExecutionContext,
    UnderstandingIntent,
    OutputShape,
    HallucinationRisk,
    ValidationAction,
    ConfidenceObject,
    Entity,
    RetrievalChunk
)

logger = logging.getLogger(__name__)

# State Transitions Map
TRANSITIONS = {
    "UNDERSTAND": {
        "UNDERSTANDING_COMPLETE": "DECIDE",
        "CLARIFICATION_REQUIRED": "CLARIFY",
        "TIMEOUT": "CLARIFY",
    },
    "DECIDE": {
        "PLAN_COMPLETE": "PLAN",
        "CLARIFICATION_REQUIRED": "CLARIFY",
    },
    "PLAN": {
        "PLAN_COMPLETE": "RETRIEVE",
    },
    "RETRIEVE": {
        "RETRIEVAL_COMPLETE": "ENOUGH_CHECK",
        "BUDGET_EXCEEDED": "COMPOSE",
    },
    "ENOUGH_CHECK": {
        "MORE_EVIDENCE_REQUIRED": "RETRIEVE",
        "RETRIEVAL_COMPLETE": "COMPOSE",
        "BUDGET_EXCEEDED": "COMPOSE",
    },
    "COMPOSE": {
        "PLAN_COMPLETE": "VALIDATE",
    },
    "VALIDATE": {
        "VALIDATION_PASSED": "FINISH",
        "MORE_EVIDENCE_REQUIRED": "RETRIEVE",
        "RETRY_COMPOSE": "COMPOSE",
        "CLARIFICATION_REQUIRED": "CLARIFY",
        "VALIDATION_FAILED": "FINISH",
    },
    "CLARIFY": {},  # Terminal
    "FINISH": {},   # Terminal
}

def resolve_registry_topic(understanding) -> List[str]:
    # Returns normalized canonical topic identifiers matching registry keys
    if not understanding:
        return []
    
    raw_topics = understanding.constraints.get("topics", [])
    query_type = understanding.constraints.get("query_type")
    
    # Mapped list of topics to registry keys
    reg_map = {
        "PRODUCTS": "PRODUCTS",
        "SERVICES": "SERVICES",
        "SOLUTIONS": "SOLUTIONS",
        "CASE_STUDIES": "CASE_STUDIES",
        "LEADERSHIP": "LEADERSHIP",
        "RECOGNITION": "RECOGNITION",
        "AWARDS": "RECOGNITION",
        "ACHIEVEMENTS": "RECOGNITION",
        "CONTACT": "CONTACT",
        "CONTACT_INFO": "CONTACT",
        "COMPANY": "COMPANY_INFO",
        "COMPANY_INFO": "COMPANY_INFO",
        "ABOUT": "COMPANY_INFO",
        "FAQ": "FAQ",
        "HELP": "FAQ",
        "MENU": "FAQ"
    }
    
    resolved = []
    
    # Process topics constraint
    for t in raw_topics:
        t_upper = str(t).upper()
        if t_upper in reg_map:
            resolved.append(reg_map[t_upper])
            
    # Process query_type if present
    if query_type:
        qt_upper = str(query_type).upper()
        if qt_upper in reg_map:
            resolved.append(reg_map[qt_upper])
            
    # Also check if any entity has category/type that maps to a registry
    # (e.g. to preserve support if entity categorization was used)
    if not resolved:
        for ent in understanding.entities:
            ent_type = str(ent.type).upper()
            if ent_type in reg_map:
                resolved.append(reg_map[ent_type])
                
    # Unique values while preserving order
    seen = set()
    return [x for x in resolved if not (x in seen or seen.add(x))]

class IntelligenceEngine:
    def __init__(self):
        from knowledge_service import get_knowledge_service
        from deterministic_engine import get_deterministic_engine
        from conversation_memory import get_conversation_memory
        
        self.ks = get_knowledge_service()
        self.det_engine = get_deterministic_engine()
        self.memory = get_conversation_memory()
        
        self.embedding_model = None
        self.provider = None

    def get_embedding_model(self) -> Any:
        if self.embedding_model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Lazy loading local embedding model: {config.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        return self.embedding_model

    def get_llm_provider(self) -> Any:
        if self.provider is None:
            from llm_provider import get_llm_provider
            provider_name = config.LLM_PROVIDER
            config_dict = {
                "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", config.API_KEY),
                "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
                "CLAUDE_API_KEY": os.environ.get("CLAUDE_API_KEY", "")
            }
            self.provider = get_llm_provider(provider_name, config_dict)
        return self.provider

    # --- Capability Execution Wrapper with Built-in Retries ---

    async def run_capability(self, name: str, func, *args, **kwargs) -> CapabilityResult:
        """Runs a given capability function with execution timing and a single retry on Failure/Timeout."""
        status = "SUCCESS"
        result_data = None
        error_msg = None
        start_time = time.time()

        for attempt in range(2):
            try:
                if asyncio.iscoroutinefunction(func):
                    result_data = await func(*args, **kwargs)
                else:
                    result_data = func(*args, **kwargs)
                    if inspect.iscoroutine(result_data):
                        result_data = await result_data
                status = "SUCCESS"
                error_msg = None
                break
            except asyncio.TimeoutError as e:
                status = "TIMEOUT"
                error_msg = str(e)
            except Exception as e:
                status = "FAILURE"
                error_msg = str(e)
            
            if attempt == 0:
                logger.warning(f"Capability {name} failed with status {status}. Retrying once...")
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        confidence = None
        if isinstance(result_data, dict):
            confidence = result_data.get("confidence")
        elif hasattr(result_data, "confidence"):
            confidence = getattr(result_data, "confidence")

        next_event = "PLAN_COMPLETE"
        if status != "SUCCESS":
            result_data = error_msg
            next_event = "TIMEOUT" if status == "TIMEOUT" else "VALIDATION_FAILED"

        return CapabilityResult(
            status=status,
            duration_ms=duration_ms,
            confidence=confidence,
            next_event=next_event,
            data=result_data,
            name=name
        )

    # --- Specific Capability Wrappers ---

    async def cap_intent_analyze(self, query: str) -> CapabilityResult:
        from intent_analyzer import get_intent_analyzer
        analyzer = get_intent_analyzer()
        func = lambda: analyzer.analyze(query)
        res = await self.run_capability("intent_analyzer.analyze", func)
        if res.status == "SUCCESS":
            res.next_event = "UNDERSTANDING_COMPLETE"
        return res

    async def cap_find_entity(self, tenant_id: str, query: str) -> CapabilityResult:
        func = lambda: self.ks.find_entity(tenant_id, query)
        res = await self.run_capability("knowledge_service.find_entity", func)
        if res.status == "SUCCESS":
            res.next_event = "PLAN_COMPLETE"
        return res

    async def cap_generate_deterministic(
        self, tenant_id: str, intent: Any, topics: List[Any], query: str
    ) -> CapabilityResult:
        func = lambda: self.det_engine.generate_response(tenant_id, intent, topics, query)
        res = await self.run_capability("deterministic_engine.generate_response", func)
        if res.status == "SUCCESS":
            res.next_event = "PLAN_COMPLETE" if res.data is not None else "MORE_EVIDENCE_REQUIRED"
        return res

    async def cap_retrieve_hybrid(
        self, query: str, query_embedding: List[float], intent: str, top_k: int, domain: str
    ) -> CapabilityResult:
        from vector_store import VectorStore
        vstore = VectorStore()
        func = lambda: vstore.query_hybrid(
            query_text=query, query_embedding=query_embedding, intent=intent, top_k=top_k, domain=domain
        )
        res = await self.run_capability("vector_store.query_hybrid", func)
        if res.status == "SUCCESS":
            res.next_event = "RETRIEVAL_COMPLETE"
        return res

    async def cap_validate_response(
        self, response_text: str, resolved_entity: Optional[str], resolved_section: Optional[str], registry: Any
    ) -> CapabilityResult:
        from response_validator import validate_response
        func = lambda: validate_response(
            response_text,
            resolved_entity=resolved_entity,
            resolved_section=resolved_section,
            registry=registry,
            return_metrics=True
        )
        res = await self.run_capability("response_validator.validate_response", func)
        if res.status == "SUCCESS":
            valid_bool = res.data[0]
            res.next_event = "VALIDATION_PASSED" if valid_bool else "VALIDATION_FAILED"
        return res

    async def cap_call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.4) -> CapabilityResult:
        provider = self.get_llm_provider()
        model = config.MODEL_NAME
        func = lambda: provider.generate(messages, model, temperature=temperature)
        res = await self.run_capability("llm_provider.generate", func)
        if res.status == "SUCCESS":
            res.next_event = "PLAN_COMPLETE"
            if isinstance(res.data, tuple) and len(res.data) == 2:
                content, metrics = res.data
                res.data = content
                from execution_context import LLMMetrics
                res.llm_metrics = LLMMetrics(**metrics)
        return res

    # --- Telemetry Helpers ---

    def _record_step(self, context: ExecutionContext, state: str, duration_ms: int, result: str, notes: str = "", start_timestamp: Optional[float] = None, end_timestamp: Optional[float] = None, retry_count: int = 0, emitted_event: Optional[str] = None):
        context.history.append(ExecutionStep(
            state=state,
            duration_ms=duration_ms,
            result=result,
            notes=notes,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            retry_count=retry_count,
            emitted_event=emitted_event
        ))

    def _record_event(self, context: ExecutionContext, name: str, producer: str, payload: Optional[Dict[str, Any]] = None):
        context.events.append(Event(
            name=name,
            producer=producer,
            payload=payload
        ))

    # --- State Implementation Handlers ---

    async def state_understand(self, context: ExecutionContext) -> Event:
        query = context.request.query
        tenant_id = context.request.tenant_id

        # 1. Deterministic Pass using Local Rule-based Intent Analyzer and Entity Lookup
        intent_cap = await self.cap_intent_analyze(query)
        context.capability_results.append(intent_cap)

        entity_cap = await self.cap_find_entity(tenant_id, query)
        context.capability_results.append(entity_cap)

        intent_analysis = intent_cap.data if intent_cap.status == "SUCCESS" else None
        matched_entity = entity_cap.data if (entity_cap.status == "SUCCESS" and isinstance(entity_cap.data, dict)) else None

        # Determine if an entity is optional for this query's intent and topics
        is_entity_optional = False
        if intent_analysis:
            prim_intent = intent_analysis.primary_intent
            topics_list = [str(t).upper() for t in intent_analysis.topics]
            
            # Semantic exemptions where entities are genuinely not required
            if prim_intent in ["GREETING", "THANKS", "GOODBYE", "HELP", "MENU", "ABOUT", "CONTACT"]:
                is_entity_optional = True
            elif "COMPANY" in topics_list or "CONTACT_INFO" in topics_list or "AWARDS" in topics_list:
                is_entity_optional = True
            elif prim_intent in ["LIST", "COUNT"]:
                known_registries = {"PRODUCTS", "SERVICES", "SOLUTIONS", "CASE_STUDIES", "LEADERSHIP", "RECOGNITION", "CONTACT", "COMPANY_INFO"}
                if any(str(topic).upper() in known_registries for topic in intent_analysis.topics):
                    is_entity_optional = True

        # Determine confidence of deterministic pass
        intent_conf = 1.0 if (intent_analysis and intent_analysis.is_deterministic) else 0.70
        
        if matched_entity:
            entity_conf = 1.0
        elif is_entity_optional:
            entity_conf = 1.0
        else:
            entity_conf = 0.50

        conf = ConfidenceObject(intent_confidence=intent_conf, entity_confidence=entity_conf)

        if conf.overall_confidence >= 0.75:
            # Deterministic pass holds sufficient confidence
            entities_list = []
            if matched_entity:
                entities_list.append(Entity(
                    name=matched_entity.get("name") or matched_entity.get("title") or "Unknown",
                    type=matched_entity.get("category", "entity"),
                    value=matched_entity.get("id")
                ))

            # Store the original intent in constraints
            orig_intent = intent_analysis.primary_intent if intent_analysis else "ASK"
            constraints_dict = dict(topics=intent_analysis.topics) if intent_analysis else {}
            constraints_dict["original_intent"] = orig_intent
            
            # Map HELP, MENU, ABOUT to query_type constraint
            if orig_intent in ["HELP", "MENU", "ABOUT"]:
                constraints_dict["query_type"] = orig_intent

            # Map the intent to a valid enum value for validation safety
            mapped_intent = orig_intent
            if orig_intent in ["GREETING", "THANKS", "GOODBYE", "HELP", "MENU", "ABOUT", "CONTACT"]:
                mapped_intent = "ASK"

            context.understanding = UnderstandingResult(
                intent=mapped_intent,
                entities=entities_list,
                constraints=constraints_dict,
                resolved_deterministically=True,
                confidence=conf,
                requires_clarification=False,
                clarification_question=None
            )
            
            # Telemetry tracking: mark deterministic attempt
            context.request.metadata["deterministic_attempt"] = True
            
            return Event(name="UNDERSTANDING_COMPLETE", producer="UNDERSTAND")

        # 2. Escalate to LLM if deterministic confidence is low
        # Record reasons in metadata
        context.request.metadata["deterministic_attempt"] = False
        context.request.metadata["deterministic_success"] = False
        context.request.metadata["deterministic_failure_reason"] = "Low confidence in deterministic pass"
        context.request.metadata["llm_escalation_reason"] = f"Low confidence in deterministic pass (overall confidence: {conf.overall_confidence}); escalated to LLM for understanding"

        if context.budget.llm.remaining_calls <= 0:
            # Fall back to degraded deterministic path if no LLM calls left
            context.understanding = UnderstandingResult(
                intent="ASK",
                entities=[],
                constraints={},
                resolved_deterministically=True,
                confidence=conf,
                requires_clarification=False,
                clarification_question=None
            )
            return Event(name="UNDERSTANDING_COMPLETE", producer="UNDERSTAND")

        context.budget.llm.remaining_calls -= 1

        system_prompt = (
            "You are the query understanding module. Categorize user intent and extract entities.\n"
            "Respond ONLY with a JSON document matching this structure:\n"
            "{\n"
            "  \"intent\": \"ASK\" | \"LIST\" | \"COUNT\" | \"COMPARE\" | \"SEARCH\" | \"RECOMMEND\" | \"SUMMARIZE\",\n"
            "  \"entities\": [{\"name\": \"string\", \"type\": \"string\", \"value\": \"string\"}],\n"
            "  \"constraints\": {},\n"
            "  \"intent_confidence\": float,\n"
            "  \"entity_confidence\": float,\n"
            "  \"requires_clarification\": boolean,\n"
            "  \"clarification_question\": \"string or null\"\n"
            "}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        llm_cap = await self.cap_call_llm(messages)
        context.capability_results.append(llm_cap)

        if llm_cap.status == "SUCCESS":
            try:
                parsed = json.loads(llm_cap.data)
                conf = ConfidenceObject(
                    intent_confidence=parsed.get("intent_confidence", 0.7),
                    entity_confidence=parsed.get("entity_confidence", 0.7)
                )
                context.understanding = UnderstandingResult(
                    intent=parsed.get("intent", "ASK"),
                    entities=[Entity(**e) for e in parsed.get("entities", [])],
                    constraints=parsed.get("constraints", {}),
                    resolved_deterministically=False,
                    confidence=conf,
                    requires_clarification=parsed.get("requires_clarification", False),
                    clarification_question=parsed.get("clarification_question")
                )

                if context.understanding.requires_clarification:
                    return Event(name="CLARIFICATION_REQUIRED", producer="UNDERSTAND", payload={
                        "question": context.understanding.clarification_question
                    })
                return Event(name="UNDERSTANDING_COMPLETE", producer="UNDERSTAND")
            except Exception as e:
                logger.error(f"Failed to parse understanding LLM response JSON: {e}")

        # Final grace fallback if LLM understanding call failed
        context.understanding = UnderstandingResult(
            intent="ASK",
            entities=[],
            constraints={},
            resolved_deterministically=True,
            confidence=conf,
            requires_clarification=False,
            clarification_question=None
        )
        return Event(name="UNDERSTANDING_COMPLETE", producer="UNDERSTAND")

    async def state_decide(self, context: ExecutionContext) -> Event:
        # Determine if query can be executed deterministically end-to-end (GREETING, THANKS, etc.)
        intent = context.understanding.intent
        is_deterministic = context.understanding.resolved_deterministically
        requires_clarification = context.understanding.requires_clarification

        if requires_clarification:
            return Event(name="CLARIFICATION_REQUIRED", producer="DECIDE")

        # Set telemetry and workflow flags
        return Event(name="PLAN_COMPLETE", producer="DECIDE")

    async def state_plan(self, context: ExecutionContext) -> Event:
        intent = context.understanding.intent
        entities = [e.name for e in context.understanding.entities]
        is_det = context.understanding.resolved_deterministically

        tasks = []
        if is_det:
            tasks.append(PlanTask(id="1", description="Execute deterministic registry lookup", requires_llm=False))
        else:
            tasks.append(PlanTask(id="1", description="Execute hybrid vector RAG retrieval", requires_llm=False))
            tasks.append(PlanTask(id="2", description="Compose response via context builder and LLM", requires_llm=True))

        expected_shape = OutputShape.PARAGRAPH
        if intent == "LIST":
            expected_shape = OutputShape.LIST
        elif intent == "COUNT":
            expected_shape = OutputShape.COUNT_VALUE
        elif intent == "COMPARE":
            expected_shape = OutputShape.TABLE
        elif intent == "RECOMMEND":
            expected_shape = OutputShape.RECOMMENDATION

        context.execution_plan = ExecutionPlan(
            intent=intent,
            tasks=tasks,
            required_knowledge=entities,
            is_deterministic=is_det,
            expected_output_shape=expected_shape
        )
        return Event(name="PLAN_COMPLETE", producer="PLAN")

    async def state_retrieve(self, context: ExecutionContext) -> Event:
        # Determine pass number
        pass_num = 1
        if context.retrieval_request:
            pass_num = context.retrieval_request.retrieval_pass_number + 1

        context.retrieval_request = RetrievalRequest(
            topics=context.understanding.constraints.get("topics", []),
            entities=[e.name for e in context.understanding.entities],
            max_chunks=5,
            ranking_strategy="hybrid",
            retrieval_pass_number=pass_num,
            budget_remaining=context.budget
        )

        # Get local query embedding
        model = self.get_embedding_model()
        query_vector = model.encode(context.request.query, normalize_embeddings=True).tolist()

        search_domain = None
        if context.understanding.constraints.get("topics"):
            search_domain = context.understanding.constraints["topics"][0]

        cap_res = await self.cap_retrieve_hybrid(
            query=context.request.query,
            query_embedding=query_vector,
            intent=str(context.understanding.intent),
            top_k=5,
            domain=search_domain
        )
        context.capability_results.append(cap_res)

        if cap_res.status == "SUCCESS" and cap_res.data:
            chunks = [RetrievalChunk(
                content=c["content"],
                source=c["source"],
                score=c["score"]
            ) for c in cap_res.data]
            
            # Simple coverage metric based on average scores
            coverage = sum(c.score for c in chunks) / len(chunks) if chunks else 0.0
            sufficient = coverage >= 0.50

            context.retrieval_result = RetrievalResult(
                chunks=chunks,
                retrieval_coverage=coverage,
                sufficient=sufficient,
                suggested_next_query=None
            )
        else:
            context.retrieval_result = RetrievalResult(
                chunks=[],
                retrieval_coverage=0.0,
                sufficient=False,
                suggested_next_query=None
            )

        return Event(name="RETRIEVAL_COMPLETE", producer="RETRIEVE")

    async def state_enough_check(self, context: ExecutionContext) -> Event:
        if context.retrieval_result and context.retrieval_result.sufficient:
            return Event(name="RETRIEVAL_COMPLETE", producer="ENOUGH_CHECK")

        # Sufficiency test failed: check budget limits
        ret_made = context.retrieval_request.retrieval_pass_number
        if ret_made >= context.budget.retrieval.max_retrievals:
            context.budget.retrieval.remaining_retrievals = 0
            return Event(name="BUDGET_EXCEEDED", producer="ENOUGH_CHECK")

        context.budget.retrieval.remaining_retrievals = max(
            0, context.budget.retrieval.max_retrievals - ret_made
        )
        return Event(name="MORE_EVIDENCE_REQUIRED", producer="ENOUGH_CHECK")

    async def state_compose(self, context: ExecutionContext) -> Event:
        low_confidence = False
        if context.retrieval_result and not context.retrieval_result.sufficient:
            if context.budget.retrieval.remaining_retrievals == 0:
                low_confidence = True

        context.response_plan = ResponsePlan(
            structure=["Overview", "Citations"],
            sections=["overview"],
            tone="professional",
            low_confidence_flag=low_confidence
        )

        # 1. Zero-LLM Deterministic Registry Resolution
        if context.execution_plan.is_deterministic:
            topics = resolve_registry_topic(context.understanding)
            orig_intent = context.understanding.constraints.get("original_intent", context.understanding.intent)
            
            # Ensure deterministic attempt is marked True in telemetry
            context.request.metadata["deterministic_attempt"] = True
            
            det_cap = await self.cap_generate_deterministic(
                tenant_id=context.request.tenant_id,
                intent=orig_intent,
                topics=topics,
                query=context.request.query
            )
            context.capability_results.append(det_cap)
            
            if det_cap.status == "SUCCESS" and det_cap.data:
                if det_cap.data.get("response") is None:
                    err_reason = det_cap.data.get("error", "Deterministic engine returned empty response")
                    context.request.metadata["deterministic_success"] = False
                    context.request.metadata["deterministic_failure_reason"] = err_reason
                    context.request.metadata["fallback_reason"] = f"Deterministic lookup failed: {err_reason}"
                    context.request.metadata["llm_escalation_reason"] = f"Deterministic engine failed: {err_reason}; escalated to LLM for composition"
                    logger.warning(f"Deterministic resolution failed: {err_reason}. Falling back to RAG composition.")
                else:
                    context.response_plan.draft_response = det_cap.data.get("response")
                    context.request.metadata["deterministic_success"] = True
                    context.request.metadata["deterministic_failure_reason"] = None
                    context.request.metadata["fallback_reason"] = None
                    context.request.metadata["llm_escalation_reason"] = None
                    return Event(name="PLAN_COMPLETE", producer="COMPOSE")

        # 2. LLM-based RAG Composition
        # Ensure telemetry has LLM escalation reason
        if "llm_escalation_reason" not in context.request.metadata:
            context.request.metadata["llm_escalation_reason"] = "Non-deterministic path requires LLM response composition"
        if "deterministic_success" not in context.request.metadata:
            context.request.metadata["deterministic_success"] = False
        if "deterministic_attempt" not in context.request.metadata:
            context.request.metadata["deterministic_attempt"] = False

        if context.budget.llm.remaining_calls <= 0:
            context.response_plan.draft_response = "I found partial information but couldn't generate a full verified answer due to resource limits."
            return Event(name="PLAN_COMPLETE", producer="COMPOSE")

        context.budget.llm.remaining_calls -= 1

        # Format structured context via context builder
        from context_builder import build_structured_context
        evidence = []
        if context.retrieval_result:
            evidence = [{"content": c.content, "source": c.source, "score": c.score} for c in context.retrieval_result.chunks]

        active_ent = None
        if context.understanding.entities:
            active_ent = context.understanding.entities[0].value

        topics = context.understanding.constraints.get("topics", ["overview"])
        active_sec = topics[0] if topics else "overview"

        structured_ctx = build_structured_context(
            resolved_entity=active_ent,
            resolved_section=active_sec,
            registry=self.ks.reg,
            evidence_chunks=evidence
        )

        system_instructions = (
            "You are the CittaAI Enterprise AI Consultant. Keep answers factual and structured.\n"
            f"--- VERIFIED FACTS CONTEXT ---\n{structured_ctx}\n\n"
            "Format your answer professionally in markdown."
        )

        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": context.request.query}
        ]

        llm_cap = await self.cap_call_llm(messages)
        context.capability_results.append(llm_cap)

        if llm_cap.status == "SUCCESS":
            context.response_plan.draft_response = llm_cap.data
        else:
            context.response_plan.draft_response = "I encountered an issue composing a response. Here is partial information."
        
        return Event(name="PLAN_COMPLETE", producer="COMPOSE")

    async def state_validate(self, context: ExecutionContext) -> Event:
        active_ent = None
        if context.understanding.entities:
            active_ent = context.understanding.entities[0].value

        topics = context.understanding.constraints.get("topics", ["overview"])
        active_sec = topics[0] if topics else "overview"

        val_cap = await self.cap_validate_response(
            response_text=context.response_plan.draft_response or "",
            resolved_entity=active_ent,
            resolved_section=active_sec,
            registry=self.ks.reg
        )
        context.capability_results.append(val_cap)

        if val_cap.status == "SUCCESS":
            valid_bool, validated_text, metrics = val_cap.data
            context.response_plan.draft_response = validated_text
            
            risk = HallucinationRisk.LOW if valid_bool else HallucinationRisk.HIGH
            action = ValidationAction.SEND if valid_bool else ValidationAction.RETRY_COMPOSE
            
            # If no LLM calls left, force SEND to degrade gracefully instead of looping
            if not valid_bool and context.budget.llm.remaining_calls <= 0:
                action = ValidationAction.SEND

            context.validation_result = ValidationResult(
                is_complete=True,
                is_grounded=valid_bool,
                missing_aspects=metrics.get("reasons", []),
                hallucination_risk=risk,
                validation_confidence=1.0 if valid_bool else 0.3,
                action=action
            )

            if action == ValidationAction.SEND:
                return Event(name="VALIDATION_PASSED", producer="VALIDATE")
            elif action == ValidationAction.RETRY_COMPOSE:
                context.request.metadata["llm_escalation_reason"] = f"Response validation failed ({', '.join(metrics.get('reasons', []))}); retrying LLM composition"
                return Event(name="RETRY_COMPOSE", producer="VALIDATE")

        context.validation_result = ValidationResult(
            is_complete=True,
            is_grounded=False,
            missing_aspects=["Validation failed to execute"],
            hallucination_risk=HallucinationRisk.HIGH,
            validation_confidence=0.0,
            action=ValidationAction.SEND
        )
        return Event(name="VALIDATION_FAILED", producer="VALIDATE")

    async def state_clarify(self, context: ExecutionContext):
        if not context.response_plan:
            context.response_plan = ResponsePlan(
                structure=["Clarification"],
                sections=["clarification"],
                tone="professional",
                low_confidence_flag=False
            )
        if context.understanding and context.understanding.clarification_question:
            context.response_plan.draft_response = context.understanding.clarification_question
        else:
            context.response_plan.draft_response = "I need some clarification. Could you please specify which CittaAI product, solution, or service you are asking about?"

    async def state_finish(self, context: ExecutionContext):
        # State machine terminal completion routines
        pass

    # --- Core Runtime Execution Loop ---

    async def execute(self, query: str, tenant_id: str = "cittaai", session_id: str = "default_session") -> ExecutionContext:
        request = RequestContext(query=query, tenant_id=tenant_id, session_id=session_id)
        context = ExecutionContext(request=request)

        current_state = "UNDERSTAND"
        start_time = time.time()

        while current_state not in ["FINISH", "CLARIFY"]:
            # Evaluate global execution runtime timeout limits
            elapsed_ms = int((time.time() - start_time) * 1000)
            context.budget.global_budget.remaining_runtime_ms = max(
                0, context.budget.global_budget.max_runtime_ms - elapsed_ms
            )

            if context.budget.global_budget.remaining_runtime_ms <= 0:
                self._record_event(context, "BUDGET_EXCEEDED", producer="SystemRuntime", payload={"reason": "Global timeout reached"})
                if current_state in ["RETRIEVE", "ENOUGH_CHECK"]:
                    current_state = "COMPOSE"
                else:
                    current_state = "FINISH"
                    break

            step_start = time.time()
            notes = ""
            
            try:
                if current_state == "UNDERSTAND":
                    event = await self.state_understand(context)
                elif current_state == "DECIDE":
                    event = await self.state_decide(context)
                elif current_state == "PLAN":
                    event = await self.state_plan(context)
                elif current_state == "RETRIEVE":
                    event = await self.state_retrieve(context)
                elif current_state == "ENOUGH_CHECK":
                    event = await self.state_enough_check(context)
                elif current_state == "COMPOSE":
                    event = await self.state_compose(context)
                elif current_state == "VALIDATE":
                    event = await self.state_validate(context)
                else:
                    raise ValueError(f"Encountered unhandled execution state: {current_state}")

                step_end = time.time()
                duration_ms = int((step_end - step_start) * 1000)
                self._record_step(context, state=current_state, duration_ms=duration_ms, result="SUCCESS", start_timestamp=step_start, end_timestamp=step_end, emitted_event=event.name)
                self._record_event(context, event.name, producer=current_state, payload=event.payload)

                next_state = TRANSITIONS[current_state].get(event.name)
                if not next_state:
                    current_state = "FINISH"
                else:
                    current_state = next_state

            except Exception as e:
                step_end = time.time()
                duration_ms = int((step_end - step_start) * 1000)
                logger.exception(f"Exception encountered in state {current_state}")
                self._record_step(context, state=current_state, duration_ms=duration_ms, result="FAILURE", notes=str(e), start_timestamp=step_start, end_timestamp=step_end, emitted_event="TIMEOUT")
                self._record_event(context, "TIMEOUT", producer=current_state, payload={"exception": str(e)})

                if current_state in ["UNDERSTAND", "DECIDE"]:
                    current_state = "CLARIFY"
                else:
                    current_state = "FINISH"

        # Terminal state processing
        if current_state == "CLARIFY":
            step_start = time.time()
            await self.state_clarify(context)
            step_end = time.time()
            duration_ms = int((step_end - step_start) * 1000)
            self._record_step(context, state="CLARIFY", duration_ms=duration_ms, result="SUCCESS", start_timestamp=step_start, end_timestamp=step_end, emitted_event="CLARIFICATION_REQUIRED")
        elif current_state == "FINISH":
            step_start = time.time()
            await self.state_finish(context)
            step_end = time.time()
            duration_ms = int((step_end - step_start) * 1000)
            self._record_step(context, state="FINISH", duration_ms=duration_ms, result="SUCCESS", start_timestamp=step_start, end_timestamp=step_end)

        try:
            from telemetry_logger import log_execution
            await log_execution(context)
        except Exception as tel_err:
            logger.error(f"Failed to persist production telemetry: {tel_err}")

        return context
