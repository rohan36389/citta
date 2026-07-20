import re
import json
import logging
import time
from collections import OrderedDict
from typing import AsyncGenerator, Dict, Any, List, Tuple, Optional
import httpx
import config

try:
    from llm_provider import LLMProvider
    from vector_store import VectorStore
    from intent_router import classify_intent, normalize_query, detect_tool_call
    from static_data import get_static_response, execute_tool
    from response_decision import make_response_decision
    from knowledge_registry import get_registry
    from query_planner import classify_query, init_anchor_embeddings, rewrite_query
    from response_validator import validate_response
    from response_builder import build_deterministic_response, load_registry_file, load_templates, validate_response_source, ResponsePersonalizer, STATIC_SUGGESTIONS
    from response_transformer import ResponseTransformer
    from query_normalizer import normalize_query_pipeline
    from registry_resolver import resolve_registry
    from entity_resolver import resolve_entity_dynamic, contains_pronouns
    from section_resolver import resolve_section_dynamic
    from knowledge_router import route_query
    from greeting_detector import detect_greeting
    from context_builder import build_structured_context
    from explainability_logger import create_explainability_log, log_explainability
except ImportError:
    from backend.llm_provider import LLMProvider
    from backend.vector_store import VectorStore
    from backend.intent_router import classify_intent, normalize_query, detect_tool_call
    from backend.static_data import get_static_response, execute_tool
    from backend.response_decision import make_response_decision
    from backend.knowledge_registry import get_registry
    from backend.query_planner import classify_query, init_anchor_embeddings, rewrite_query
    from backend.response_validator import validate_response
    from backend.response_builder import build_deterministic_response, load_registry_file, load_templates, validate_response_source, ResponsePersonalizer, STATIC_SUGGESTIONS
    from backend.response_transformer import ResponseTransformer
    from backend.query_normalizer import normalize_query_pipeline
    from backend.registry_resolver import resolve_registry
    from backend.entity_resolver import resolve_entity_dynamic, contains_pronouns
    from backend.section_resolver import resolve_section_dynamic
    from backend.knowledge_router import route_query
    from backend.greeting_detector import detect_greeting

logger = logging.getLogger(__name__)

INJECTION_KEYWORDS = [
    r"ignore\s+previous\s+instruction",
    r"reveal\s+system\s+prompt",
    r"tell\s+me\s+your\s+prompt",
    r"system\s+instructions",
    r"ignore\s+company\s+info",
    r"developer\s+mode",
    r"override\s+instructions",
    r"you\s+must\s+ignore"
]

FOLLOW_UP_TRIGGERS = [
    "tell me more", "how does it work", "benefits", "features", "examples", "explain simply", "why", 
    "tell me how it works", "working", "integrations", "details"
]

class LRUCacheWithTTL:
    def __init__(self, capacity: int = 100, ttl_seconds: float = 1800):
        self.capacity = capacity
        self.ttl = ttl_seconds
        self.cache = OrderedDict()

    def get(self, key: str) -> Any:
        if key not in self.cache:
            return None
        value, expiry = self.cache[key]
        if time.time() > expiry:
            del self.cache[key]
            return None
        self.cache.move_to_end(key)
        return value

    def set(self, key: str, value: Any):
        if key in self.cache:
            del self.cache[key]
        elif len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        expiry = time.time() + self.ttl
        self.cache[key] = (value, expiry)

def get_domain_from_category(category: str) -> str:
    cat = str(category).lower().strip()
    if cat in ["product", "whatsapp_marketing", "influencer_marketing", "products"]:
        return "PRODUCTS"
    elif cat in ["solution", "ecommerce_os", "pharma_os", "real_estate_os", "smart_cities_os", "education_os", "enterprise_ai_os", "solutions"]:
        return "SOLUTIONS"
    elif cat in ["service", "data_engineering", "enterprise_agentic_ai", "ai_strategy", "ai_powered_marketing", "services"]:
        return "SERVICES"
    elif cat in ["leadership", "founder", "team"]:
        return "LEADERSHIP"
    elif cat in ["recognition", "awards"]:
        return "RECOGNITION"
    elif cat in ["casestudies", "case_studies"]:
        return "CASE_STUDIES"
    elif cat in ["contact"]:
        return "CONTACT"
    elif cat in ["location", "address"]:
        return "LOCATION"
    return "COMPANY_INFO"

class RAGService:
    def __init__(self, provider: LLMProvider, vector_store: VectorStore):
        self.provider = provider
        self.vector_store = vector_store
        
        self.session_memory: Dict[str, List[Dict[str, str]]] = {}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.session_summaries: Dict[str, str] = {}
        
        self.active_entities: Dict[str, str] = {}
        self.cache = LRUCacheWithTTL(capacity=100, ttl_seconds=1800)
        self.conversation_states: Dict[str, Dict[str, Any]] = {}
        self.transform_cache = LRUCacheWithTTL(capacity=200, ttl_seconds=1800)
        self.transformer = ResponseTransformer(self.provider)
        
        logger.info(f"Loading local embedding model: {config.EMBEDDING_MODEL}")
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        init_anchor_embeddings(self.embedding_model)
        self.unindexed_routes: Dict[str, str] = {}
        self._build_unindexed_routes_registry()

    def _build_unindexed_routes_registry(self):
        try:
            reg = get_registry()
            routes = list(reg.routes.keys())
            for route in routes:
                if not route or route == "/":
                    continue
                count = self.vector_store.get_chunk_count_for_page(route)
                if count == 0:
                    slug = route.split("/")[-1]
                    label = slug.replace("-", " ").title()
                    if "os" in label.lower():
                        label = label.replace("Os", "OS").replace("os", "OS")
                    self.unindexed_routes[route] = label
            logger.info(f"Registered unindexed routes: {self.unindexed_routes}")
        except Exception as e:
            logger.warning(f"Failed to build unindexed routes registry: {e}")

    def clear_session(self, session_id: str):
        if session_id in self.session_memory:
            del self.session_memory[session_id]
        if session_id in self.user_preferences:
            del self.user_preferences[session_id]
        if session_id in self.session_summaries:
            del self.session_summaries[session_id]
        if session_id in self.active_entities:
            del self.active_entities[session_id]
        if session_id in self.conversation_states:
            del self.conversation_states[session_id]

    def is_prompt_injection(self, text: str) -> bool:
        text_lower = text.lower()
        for pattern in INJECTION_KEYWORDS:
            if re.search(pattern, text_lower):
                return True
        return False

    async def get_embedding(self, text: str, input_type: str = "query") -> List[float]:
        if not text:
            return [0.0] * 768
            
        processed_text = text
        if "bge" in config.EMBEDDING_MODEL.lower() and input_type == "query":
            processed_text = f"Represent this sentence for searching relevant passages: {text}"
            
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.embedding_model.encode(processed_text, normalize_embeddings=True).tolist()
            )
            return embedding
        except Exception:
            logger.exception("Failed to get embeddings locally")
            return [0.0] * 768

    async def warmup(self, model: str):
        try:
            self.vector_store.warmup()
        except Exception as e:
            logger.warning(f"Vector store warmup failed: {e}")
        try:
            _ = await self.get_embedding("warmup query", input_type="query")
        except Exception as e:
            logger.warning(f"Embedding model warmup failed: {e}")

    async def chat_stream(
        self, 
        session_id: str, 
        message: str, 
        model: str,
        tenant_id: str = "cittaai"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        start_time = time.time()
        
        # 1. Injection Protection
        if self.is_prompt_injection(message):
            injection_text = "I can only assist with verified information regarding CittaAI company details, products, services, achievements, and operations. How else can I help you?"
            yield {"text": injection_text, "done": False}
            yield {
                "done": True,
                "citations": [],
                "suggested_questions": ["What services do you offer?", "Tell me about CittaAI products.", "How can I contact support?"],
                "preferences": self.user_preferences.get(session_id, {}),
                "redirect": None,
                "source": "Injection Guardrail",
                "verified": True,
                "confidence": 1.0,
                "attribution": {
                    "source": "Injection Guardrail",
                    "knowledge_file": "injection_filter.json",
                    "entity": "None",
                    "confidence": 1.0,
                    "verified": True
                },
                "metrics": {
                    "intent_time": 0.0,
                    "cache_hit": 0,
                    "cache_time": 0.0,
                    "embedding_time": 0.0,
                    "retrieval_time": 0.0,
                    "llm_time": 0.0,
                    "streaming_time": 0.0,
                    "total_time": time.time() - start_time,
                    "prompt_tokens": 0,
                    "completion_tokens": len(injection_text) // 4
                }
            }
            return
 
        # Initialize memory structures
        if session_id not in self.session_memory:
            self.session_memory[session_id] = []
        if session_id not in self.user_preferences:
            self.user_preferences[session_id] = {}
        if session_id not in self.conversation_states:
            self.conversation_states[session_id] = {
                "active_registry": None,
                "active_entity": None,
                "active_section": None,
                "active_intent": None,
                "last_query": None,
                "last_response": None,
                "last_source": None,
                "confidence": 0.0,
                "turn_count": 0
            }

        state = self.conversation_states[session_id]
        reg = get_registry()
        # 2. Query Normalizer (Clean -> Typo autocorrect -> Abbreviation/Synonym Expansion)
        start_norm = time.time()
        norm_res = normalize_query_pipeline(message, reg.unified_vocabulary, reg.abbreviations)
        normalized_q = norm_res["normalized_query"]
        spell_corrections = norm_res["spell_corrections"]
        norm_time = time.time() - start_norm
        
        # 3. Early Intercept Greeting Detector
        greeting_res = detect_greeting(message) or detect_greeting(normalized_q)
        if greeting_res:
            resp_text = greeting_res["response"]
            self.session_memory[session_id].append({"role": "user", "content": message})
            self.session_memory[session_id].append({"role": "assistant", "content": resp_text})
            
            state["turn_count"] = state.get("turn_count", 0) + 1
            state["last_query"] = message
            state["last_response"] = resp_text
            state["last_source"] = "Greeting Detector"
            state["confidence"] = 1.0
            
            exp_log = create_explainability_log(
                query=message,
                normalized_query=normalized_q,
                registry="GREETINGS",
                entity=None,
                section=None,
                intent="GREETING",
                confidence=1.0,
                retrieved_sources=["greeting_detector.py"],
                llm_used=False,
                validator_result={"valid": True, "reasons": []},
                latency=time.time() - start_time
            )
            log_explainability(exp_log)

            yield {"text": resp_text, "done": False}
            yield {
                "done": True,
                "citations": [],
                "suggested_questions": greeting_res["suggestions"],
                "redirect": None,
                "source": "Greeting Detector",
                "verified": True,
                "confidence": 1.0,
                "attribution": {
                    "source": "Greeting Detector",
                    "knowledge_file": "greeting_detector.py",
                    "entity": "None",
                    "confidence": 1.0,
                    "verified": True
                },
                "metrics": {
                    "intent_time": norm_time,
                    "cache_hit": 0,
                    "cache_time": 0.0,
                    "embedding_time": 0.0,
                    "retrieval_time": 0.0,
                    "llm_time": 0.0,
                    "streaming_time": 0.0,
                    "total_time": time.time() - start_time,
                    "prompt_tokens": 0,
                    "completion_tokens": len(resp_text) // 4,
                    "normalized_query": normalized_q,
                    "spell_corrections": json.dumps(spell_corrections),
                    "resolved_registry": "GREETINGS",
                    "resolved_entity": "NONE",
                    "resolved_section": "NONE",
                    "routing_path": "greeting_detector",
                    "explainability": json.dumps(exp_log),
                    "normalizer_ms": norm_time * 1000.0,
                    "resolver_ms": 0.0,
                    "router_ms": 0.0,
                    "builder_ms": 0.0,
                    "rag_ms": 0.0
                }
            }
            return

        # 4. Deterministic Intercept Engine Check (Zero-LLM latency, strictly grounded in leadership_info.json)
        from intent_analyzer import get_intent_analyzer
        from deterministic_engine import get_deterministic_engine
        from structured_renderers import sanitize_conversational_text

        intent_analysis = get_intent_analyzer().analyze(message)
        det_response = get_deterministic_engine().generate_response(
            tenant_id=tenant_id,
            intent=intent_analysis.primary_intent,
            topics=intent_analysis.topics,
            query=message
        )
        if det_response:
            clean_text = sanitize_conversational_text(det_response["response"])
            det_metrics = det_response.get("metrics", {})
            res_ent = det_metrics.get("resolved_entity", "NONE")
            res_reg = det_metrics.get("resolved_registry", "NONE")
            if res_ent and res_ent != "NONE":
                state["active_entity"] = res_ent
            if res_reg and res_reg != "NONE":
                state["active_registry"] = res_reg

            self.session_memory[session_id].append({"role": "user", "content": message})
            self.session_memory[session_id].append({"role": "assistant", "content": clean_text})
            state["turn_count"] = state.get("turn_count", 0) + 1
            state["last_query"] = message
            state["last_response"] = clean_text

            exp_log = {
                "query": message,
                "normalized_query": normalized_q,
                "registry": det_response.get("metrics", {}).get("resolved_registry", "GENERAL"),
                "entity": det_response.get("metrics", {}).get("resolved_entity", "NONE"),
                "section": "overview",
                "intent": str(intent_analysis.primary_intent),
                "confidence": 1.0,
                "retrieved_sources": ["Deterministic Engine"],
                "llm_used": "NONE (Deterministic)",
                "validator_result": "PASS",
                "latency": (time.time() - start_time) * 1000.0
            }
            log_explainability(exp_log)

            yield {"text": clean_text, "done": False}
            yield {
                "done": True,
                "source": det_response.get("source", "Deterministic Engine"),
                "redirect": det_response.get("navigation"),
                "suggested_questions": det_response.get("suggestions", []),
                "action_choices": det_response.get("action_choices", []),
                "metrics": {
                    "normalizer_time": norm_time,
                    "intent_time": time.time() - start_time,
                    "cache_hit": 0,
                    "cache_time": 0.0,
                    "embedding_time": 0.0,
                    "retrieval_time": 0.0,
                    "llm_time": 0.0,
                    "streaming_time": 0.0,
                    "total_time": time.time() - start_time,
                    "prompt_tokens": 0,
                    "completion_tokens": len(clean_text) // 4,
                    "normalized_query": normalized_q,
                    "resolved_registry": det_response.get("metrics", {}).get("resolved_registry", "GENERAL"),
                    "resolved_entity": det_response.get("metrics", {}).get("resolved_entity", "NONE"),
                    "resolved_section": det_response.get("metrics", {}).get("resolved_section", "overview"),
                    "routing_path": "deterministic_engine",
                    "explainability": json.dumps(exp_log)
                }
            }
            return

        # Fast Exact Query Cache Lookup (< 5ms hit latency)
        cache_query_key = f"exact_query:{message.strip().lower()}"
        cached_entry = self.cache.get(cache_query_key)
        if cached_entry:
            resp_text = cached_entry["response"]
            self.session_memory[session_id].append({"role": "user", "content": message})
            self.session_memory[session_id].append({"role": "assistant", "content": resp_text})
            
            state["turn_count"] = state.get("turn_count", 0) + 1
            state["last_query"] = message
            state["last_response"] = resp_text
            state["last_source"] = cached_entry.get("source", "Cache Hit")
            
            exp_log = create_explainability_log(
                query=message,
                normalized_query=message.strip().lower(),
                registry=cached_entry.get("registry", "CACHE"),
                entity=cached_entry.get("entity", "CACHE"),
                section=cached_entry.get("section", "CACHE"),
                intent=cached_entry.get("intent", "CACHE"),
                confidence=1.0,
                retrieved_sources=["cache_hit"],
                llm_used=False,
                validator_result={"valid": True, "reasons": []},
                latency=time.time() - start_time
            )
            log_explainability(exp_log)

            yield {"text": resp_text, "done": False}
            yield {
                "done": True,
                "citations": cached_entry.get("citations", []),
                "suggested_questions": cached_entry.get("suggested_questions", []),
                "redirect": cached_entry.get("redirect"),
                "source": "Cache Hit",
                "verified": True,
                "confidence": 1.0,
                "attribution": cached_entry.get("attribution", {"source": "Cache Hit"}),
                "metrics": {
                    "intent_time": 0.0,
                    "cache_hit": 1,
                    "cache_time": time.time() - start_time,
                    "embedding_time": 0.0,
                    "retrieval_time": 0.0,
                    "llm_time": 0.0,
                    "streaming_time": 0.0,
                    "total_time": time.time() - start_time,
                    "prompt_tokens": 0,
                    "completion_tokens": len(resp_text) // 4,
                    "normalized_query": message.strip().lower(),
                    "spell_corrections": "{}",
                    "resolved_registry": cached_entry.get("registry", "CACHE"),
                    "resolved_entity": cached_entry.get("entity", "CACHE"),
                    "resolved_section": cached_entry.get("section", "CACHE"),
                    "routing_path": "cache_hit",
                    "explainability": json.dumps(exp_log),
                    "normalizer_ms": 0.0,
                    "resolver_ms": 0.0,
                    "router_ms": 0.0,
                    "builder_ms": 0.0,
                    "rag_ms": 0.0
                }
            }
            return
        
        # 5. Intent Classification Check
        cls_res = classify_query(message, self.embedding_model)
        query_type = cls_res["query_type"]
        state["active_intent"] = query_type

        # 5. Active Context Memory check for follow-up requests
        state["turn_count"] = state.get("turn_count", 0) + 1
        
        # Check if query explicitly refers to a DIFFERENT entity or registry FIRST
        explicit_change = False
        section_words = {"how", "it", "works", "work", "benefits", "features", "case", "studies", "faq", "examples", "integrations", "best", "for", "overview", "about"}
        for word in normalized_q.split():
            if word in section_words:
                continue
            mapped_id = reg.unified_vocabulary.get(word)
            if mapped_id:
                if mapped_id in reg.entities and mapped_id != state.get("active_entity"):
                    explicit_change = True
                    break
                elif mapped_id.upper() in reg.registry_index and mapped_id.upper() != state.get("active_registry"):
                    explicit_change = True
                    break
                    
        if explicit_change:
            logger.info("Context explicitly changed. Clearing context.")
            state["active_registry"] = None
            state["active_entity"] = None
            state["active_section"] = None
            state["turn_count"] = 1
            
        # Determine if it is a follow-up query (only if no explicit change occurred!)
        is_follow_up = (
            not explicit_change and
            state.get("active_entity") is not None and (
                contains_pronouns(normalized_q) or 
                normalized_q.strip().lower() in FOLLOW_UP_TRIGGERS or
                (len(normalized_q.split()) <= 3 and any(trig in normalized_q.strip().lower() for trig in FOLLOW_UP_TRIGGERS))
            )
        )
        
        res_entity = None
        res_registry = None
        res_section = None
        clarification_data = None
        
        if is_follow_up:
            # Re-use context! Skip entity search, resolve section dynamically
            res_entity = state.get("active_entity")
            res_registry = state.get("active_registry")
            logger.info(f"Context memory match: follow-up query inherits active entity '{res_entity}'")
            
            start_resolve = time.time()
            res_section, sec_score, sec_clar = resolve_section_dynamic(
                query=normalized_q,
                entity_data=reg.get_entity(res_entity),
                registry_meta=reg.registry_index.get(res_registry, {}).get("metadata") if res_registry else None,
                active_section=state.get("active_section"),
                intent=query_type
            )
            clarification_data = sec_clar
            resolver_time = time.time() - start_resolve
            confidence = 1.0
            ent_score = 1.0
            
        else:
            # Perform entity resolution first
            start_resolve = time.time()
            res_entity, ent_score, ent_alias, ent_clar = resolve_entity_dynamic(
                query=normalized_q,
                registry_entities=reg.entities,
                entity_lookup=reg.entity_lookup,
                alias_index=reg.aliases,
                unified_vocabulary=reg.unified_vocabulary,
                active_entity=state.get("active_entity")
            )
            
            # Resolve registry dynamically from entity.belongs_to
            res_registry, reg_score = resolve_registry(
                query=normalized_q,
                resolved_entity_id=res_entity,
                registry_index=reg.registry_index,
                knowledge_graph=reg.knowledge_graph,
                disabled_registries=reg.disabled_registries
            )
            
            # Resolve section dynamically
            res_section, sec_score, sec_clar = resolve_section_dynamic(
                query=normalized_q,
                entity_data=reg.get_entity(res_entity) if res_entity else None,
                registry_meta=reg.registry_index.get(res_registry, {}).get("metadata") if res_registry else None,
                active_section=state.get("active_section"),
                intent=query_type
            )
            
            resolver_time = time.time() - start_resolve
            confidence = reg_score if reg_score > 0.0 else 1.0
            clarification_data = ent_clar or sec_clar

        # 6. Knowledge Router Execution
        start_route = time.time()
        router_res = route_query(
            query_text=message,
            normalized_query=normalized_q,
            registry_type=res_registry,
            registry_score=confidence,
            entity_id=res_entity,
            entity_score=ent_score if res_entity else 0.0,
            section=res_section,
            section_score=sec_score if 'sec_score' in locals() else 1.0,
            clarification_data=clarification_data,
            conversation_state=state,
            registry_index=reg.registry_index
        )
        router_time = time.time() - start_route
        
        # Save context attributes on successful resolution
        if res_registry and not clarification_data:
            state["active_registry"] = res_registry
            if res_entity:
                state["active_entity"] = res_entity
                self.active_entities[session_id] = res_entity
            if res_section:
                state["active_section"] = res_section

        route_path = router_res["explainability"]["route"]
        
        # If routed to cache, golden answers, registries, or clarification pages
        if route_path != "fallback" and "hybrid_rag" not in route_path:
            resp_text = router_res["response"]
            self.session_memory[session_id].append({"role": "user", "content": message})
            self.session_memory[session_id].append({"role": "assistant", "content": resp_text})
            
            state["last_query"] = message
            state["last_response"] = resp_text
            state["last_source"] = route_path
            state["confidence"] = confidence
            
            cache_key = f"{query_type}_{res_registry or 'SYS'}_{res_entity or 'NONE'}_{res_section or 'NONE'}"
            attribution = {
                "source": router_res["source"],
                "knowledge_file": f"{res_registry.lower() if res_registry else 'system'}.json",
                "entity": res_entity or "None",
                "confidence": confidence,
                "verified": router_res["verified"]
            }
            
            payload = {
                "response": resp_text,
                "citations": [],
                "suggested_questions": router_res.get("suggestions") or [],
                "redirect": router_res.get("redirect"),
                "source": router_res["source"],
                "verified": router_res["verified"],
                "confidence": confidence,
                "attribution": attribution,
                "registry": res_registry,
                "entity": res_entity,
                "section": res_section,
                "intent": query_type
            }
            self.cache.set(cache_key, payload)
            self.cache.set(f"exact_query:{message.strip().lower()}", payload)
            
            exp_log = create_explainability_log(
                query=message,
                normalized_query=normalized_q,
                registry=res_registry,
                entity=res_entity,
                section=res_section,
                intent=query_type,
                confidence=confidence,
                retrieved_sources=[router_res.get("source", "knowledge_router")],
                llm_used=False,
                validator_result={"valid": True, "reasons": []},
                latency=time.time() - start_time
            )
            log_explainability(exp_log)

            yield {"text": resp_text, "done": False}
            yield {
                "done": True,
                "citations": [],
                "suggested_questions": router_res.get("suggestions") or [],
                "redirect": router_res.get("redirect"),
                "source": router_res["source"],
                "verified": router_res["verified"],
                "confidence": confidence,
                "attribution": attribution,
                "metrics": {
                    "intent_time": norm_time + resolver_time,
                    "cache_hit": 0,
                    "cache_time": 0.0,
                    "embedding_time": 0.0,
                    "retrieval_time": 0.0,
                    "llm_time": 0.0,
                    "streaming_time": 0.0,
                    "total_time": time.time() - start_time,
                    "prompt_tokens": 0,
                    "completion_tokens": len(resp_text) // 4,
                    "normalized_query": normalized_q,
                    "spell_corrections": json.dumps(spell_corrections),
                    "resolved_registry": res_registry,
                    "resolved_entity": res_entity,
                    "resolved_section": res_section,
                    "routing_path": route_path,
                    "explainability": json.dumps(exp_log),
                    "normalizer_ms": norm_time * 1000.0,
                    "resolver_ms": resolver_time * 1000.0,
                    "router_ms": router_time * 1000.0,
                    "builder_ms": 0.0,
                    "rag_ms": 0.0
                }
            }
            return

        # 7. Fallthrough to Hybrid RAG pathway (Only for reasoning/comparisons)
        emb_start = time.time()
        query_vector = await self.get_embedding(message, input_type="query")
        embedding_time = time.time() - emb_start
        
        retrieval_start = time.time()
        search_domain = res_registry if res_registry else None
        
        top_chunks = self.vector_store.query_hybrid(
            query_text=message,
            query_embedding=query_vector,
            intent=None,
            top_k=config.TOP_K,
            domain=search_domain
        )
        
        unique_chunks = []
        seen_contents = set()
        for chunk in top_chunks:
            norm_content = chunk["content"].strip().lower()
            if norm_content not in seen_contents:
                seen_contents.add(norm_content)
                unique_chunks.append(chunk)
                if len(unique_chunks) == config.RERANK_TOP_K:
                    break
                    
        retrieval_time = time.time() - retrieval_start
        max_score = unique_chunks[0]["score"] if unique_chunks else 0.0

        if max_score < 0.30 or not unique_chunks:
            logger.warning(f"RAG search confidence {max_score:.4f} below absolute threshold (0.30).")
            unavail_msg = "I couldn't find verified information about this topic in the current knowledge base."
            yield {"text": unavail_msg, "done": False}
            yield {
                "done": True,
                "citations": [],
                "suggested_questions": ["Show Products", "Show Services", "Show Solutions"],
                "redirect": None,
                "source": "Hybrid RAG + LLM",
                "verified": False,
                "confidence": max_score,
                "attribution": {
                    "source": "Hybrid RAG + LLM",
                    "knowledge_file": "vector_store.db",
                    "entity": "None",
                    "confidence": max_score,
                    "verified": False
                },
                "metrics": {
                    "intent_time": norm_time + resolver_time,
                    "cache_hit": 0,
                    "cache_time": 0.0,
                    "embedding_time": embedding_time,
                    "retrieval_time": retrieval_time,
                    "llm_time": 0.0,
                    "streaming_time": 0.0,
                    "total_time": time.time() - start_time,
                    "prompt_tokens": 0,
                    "completion_tokens": len(unavail_msg) // 4,
                    "normalized_query": normalized_q,
                    "spell_corrections": json.dumps(spell_corrections),
                    "resolved_registry": res_registry,
                    "resolved_entity": res_entity,
                    "resolved_section": res_section,
                    "routing_path": "hybrid_rag_unauthorized",
                    "explainability": json.dumps({"reason": "Max score below 0.30 threshold"}),
                    "normalizer_ms": norm_time * 1000.0,
                    "resolver_ms": resolver_time * 1000.0,
                    "router_ms": router_time * 1000.0,
                    "builder_ms": 0.0,
                    "rag_ms": retrieval_time * 1000.0
                }
            }
            return

        citations = []
        for chunk in unique_chunks:
            meta = chunk["metadata"]
            source_title = meta.get("title", meta.get("source", "Website Core"))
            if source_title not in citations:
                citations.append(source_title)
        
        # Build canonical structured context via ContextBuilder
        structured_context = build_structured_context(
            resolved_entity=res_entity,
            resolved_section=res_section,
            registry=reg,
            conversation_state=state,
            evidence_chunks=unique_chunks
        )

        mode = "REASON"
        if query_type in ["SIMPLIFY", "ELABORATE", "SUMMARIZE", "EXAMPLE", "COMPARE"]:
            mode = query_type

        system_instructions = (
            f"You are the CittaAI Enterprise AI Consultant, a professional advisor representing CittaAI.\n"
            f"Active Mode: {mode}\n"
            "Answer the query professionally. Your response must be entirely factual, structured, and grounded in context.\n"
            "STRICT CATEGORY BOUNDS CONSTRAINTS:\n"
            "- You must NOT mix Products with Solutions or Services.\n"
            "- WhatsApp Marketing and Influencer Marketing are Products.\n"
            "- Operating Systems (e.g. ecommerce-os, pharma-os) are Solutions.\n"
            "- Consulting fields (e.g. Data Engineering, Strategy) are Services.\n"
            "- Never display routing or navigation links other than the exact verified routes in the context.\n"
        )
        
        full_system_prompt = (
            f"{system_instructions}\n\n"
            f"--- FACTUAL STRUCTURED CONTEXT ---\n{structured_context}\n\n"
            "Answer the query professionally. Stream only raw markdown text."
        )
        
        llm_messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": message}
        ]
        
        prompt_tokens = len(json.dumps(llm_messages)) // 4
        llm_start = time.time()
        complete_response = ""
        first_token_latency = 0.0
        first_token_received = False
        streaming_start = 0.0
        
        try:
            async for chunk in self.provider.generate_stream(
                messages=llm_messages,
                model=model,
                temperature=0.4
            ):
                if not first_token_received:
                    first_token_received = True
                    first_token_latency = time.time() - llm_start
                    streaming_start = time.time()
                text_part = chunk.get("text", "") if isinstance(chunk, dict) else chunk
                complete_response += text_part
                yield {"text": text_part, "done": False}
        except Exception:
            logger.exception("Error during LLM stream generation")
            complete_response = "The AI consultant assistant is temporarily offline. Please try again later."
            yield {"text": complete_response, "done": False}

        streaming_time = (time.time() - streaming_start) if first_token_received else 0.0
        completion_tokens = len(complete_response) // 4
        tokens_per_second = completion_tokens / streaming_time if streaming_time > 0 else 0.0
        llm_time = time.time() - llm_start

        # Post-generation Category Guardrail (Mixing check)
        from query_planner import _entity_index
        if res_registry and query_type != "COMPARE":
            other_domains = [d for d in _entity_index.keys() if d.upper() != res_registry.upper()]
            has_mixed_content = False
            for od in other_domains:
                for alias in _entity_index[od].keys():
                    if re.search(r"\b" + re.escape(alias) + r"\b", complete_response.lower()):
                        has_mixed_content = True
                        break
                if has_mixed_content:
                    break
            
            if has_mixed_content:
                logger.warning("Guardrail detected cross-domain categories mixing in RAG output. Triggering strict regeneration.")
                strict_prompt = (
                    f"{system_instructions}\n"
                    f"--- STRICT GUARDRAIL RULES ---\n"
                    f"You must ONLY discuss entities belonging to the {res_registry} category. "
                    f"Do not mention any entities from other domains under any circumstance.\n\n"
                    f"--- KNOWLEDGE REGISTRY CONTEXT ---\n{company_ctx}\n"
                    f"--- STRUCTURED ENTITY DB ---\n{entity_ctx}\n"
                    f"--- RAG EVIDENCE CHUNKS ---\n{retrieved_evidence}\n"
                )
                llm_messages[0]["content"] = strict_prompt
                
                regenerated_response = ""
                try:
                    async for chunk in self.provider.generate_stream(
                        messages=llm_messages,
                        model=model,
                        temperature=0.2
                    ):
                        text_part = chunk.get("text", "") if isinstance(chunk, dict) else chunk
                        regenerated_response += text_part
                    
                    has_mixed_content = False
                    for od in other_domains:
                        for alias in _entity_index[od].keys():
                            if re.search(r"\b" + re.escape(alias) + r"\b", regenerated_response.lower()):
                                has_mixed_content = True
                                break
                        if has_mixed_content:
                            break
                            
                    if not has_mixed_content:
                        complete_response = regenerated_response
                    else:
                        logger.warning("Regeneration still contained category mix. Falling back to default templates.")
                        complete_response = "I couldn't find verified information about this topic in the current knowledge base."
                except Exception:
                    logger.exception("Failed to run guardrail regeneration.")

        # Apply soft confidence disclaimer brackets
        if 0.30 <= max_score < 0.60:
            disclaimer_prefix = "Based on the available CittaAI information, "
            if not complete_response.startswith(disclaimer_prefix):
                complete_response = disclaimer_prefix + complete_response
                yield {"text": "\n\n*Applied disclaimer:* " + complete_response, "done": False}
                    
        # Apply output validation with grounding & facts verification
        val_ok, verified_text, val_metrics = validate_response(
            complete_response,
            resolved_entity=res_entity,
            resolved_section=res_section,
            registry=reg,
            retry_count=0,
            return_metrics=True
        )
        if not val_ok:
            # Single retry check on initial validation failure
            val_ok_retry, verified_text_retry, val_metrics_retry = validate_response(
                verified_text,
                resolved_entity=res_entity,
                resolved_section=res_section,
                registry=reg,
                retry_count=1,
                return_metrics=True
            )
            complete_response = verified_text_retry
            yield {"text": "\n\n*Validation checks applied:* " + complete_response, "done": False}

        self.session_memory[session_id].append({"role": "user", "content": message})
        self.session_memory[session_id].append({"role": "assistant", "content": complete_response})
        
        state["last_query"] = message
        state["last_response"] = complete_response
        state["last_source"] = "hybrid_rag"
        state["confidence"] = max_score
        
        sugs = STATIC_SUGGESTIONS.get(res_registry or "COMPANY_INFO", ["How do I contact support?"])
        nav_link = None
        if res_entity:
            ent = reg.get_entity(res_entity)
            if ent:
                nav_link = ent.get("route")
                
        attribution = {
            "source": "Hybrid RAG + LLM",
            "knowledge_file": "vector_store.db",
            "entity": res_entity or "None",
            "confidence": max_score,
            "verified": False
        }
        
        # Cache response
        cache_key = f"{query_type}_{res_registry or 'SYS'}_{res_entity or 'NONE'}_{res_section or 'NONE'}"
        self.cache.set(cache_key, {
            "response": complete_response,
            "citations": unique_chunks,
            "suggested_questions": sugs,
            "redirect": nav_link,
            "source": "Hybrid RAG + LLM",
            "verified": False,
            "confidence": max_score,
            "attribution": attribution
        })

        exp_log = create_explainability_log(
            query=message,
            normalized_query=normalized_q,
            registry=res_registry,
            entity=res_entity,
            section=res_section,
            intent=query_type,
            confidence=max_score,
            retrieved_sources=citations,
            llm_used=True,
            validator_result=val_metrics if 'val_metrics' in locals() else {"valid": True, "reasons": []},
            latency=time.time() - start_time
        )
        log_explainability(exp_log)

        yield {
            "done": True,
            "citations": citations,
            "suggested_questions": sugs,
            "redirect": nav_link,
            "source": "Hybrid RAG + LLM",
            "verified": False,
            "confidence": max_score,
            "attribution": attribution,
            "metrics": {
                "intent_time": norm_time + resolver_time,
                "cache_hit": 0,
                "cache_time": 0.0,
                "embedding_time": embedding_time,
                "retrieval_time": retrieval_time,
                "llm_time": llm_time,
                "streaming_time": streaming_time,
                "total_time": time.time() - start_time,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "first_token_latency": first_token_latency,
                "tokens_per_second": tokens_per_second,
                "normalized_query": normalized_q,
                "spell_corrections": json.dumps(spell_corrections),
                "resolved_registry": res_registry,
                "resolved_entity": res_entity,
                "resolved_section": res_section,
                "routing_path": "hybrid_rag",
                "explainability": json.dumps(exp_log),
                "explainability_log": exp_log,
                "normalizer_ms": norm_time * 1000.0,
                "resolver_ms": resolver_time * 1000.0,
                "router_ms": router_time * 1000.0,
                "builder_ms": 0.0,
                "rag_ms": retrieval_time * 1000.0
            }
        }

    async def extract_preferences(self, query: str, response: str, session_id: str, model: str):
        pass

    async def generate_summary(self, session_id: str, model: str):
        pass
