import re
import time
import logging
import json
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Any, List, Optional

from llm_provider import LLMProvider
from response_validator import validate_response
from knowledge_registry import get_registry

logger = logging.getLogger(__name__)

def extract_target_language(query: str) -> str:
    q = query.lower()
    match = re.search(r"\b(?:translate\s+(?:this\s+)?(?:to|into)|in)\s+([a-zA-Z]+)\b", q)
    if match:
        return match.group(1).capitalize()
    return "the requested language"

class ResponseTransformer:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def transform_stream(
        self,
        session_id: str,
        intent: str,
        query: str,
        model: str,
        conversation_states: Dict[str, Dict[str, Any]],
        transform_cache: Any
    ) -> AsyncGenerator[Dict[str, Any], None]:
        start_time = time.time()
        
        # 1. Fetch previous turn state
        state = conversation_states.get(session_id)
        if not state or not state.get("last_response"):
            logger.warning(f"No previous state found for session {session_id}. Transformation cannot proceed.")
            yield {"text": "I don't have a previous answer in this session to transform. Please ask me a question first.", "done": True}
            return
            
        last_response = state["last_response"]
        active_entity = state.get("active_entity") or "None"
        last_domain = state.get("last_domain") or "COMPANY_INFO"
        last_source = state.get("last_source") or "nvidia"
        last_citations = state.get("last_citations") or []
        last_redirect = state.get("last_redirect")
        
        # 2. Check transformation cache
        # Key: conversation_id + transformation_type + entity
        # Normalize the entity to avoid cache key mismatches
        norm_entity = str(active_entity).lower().strip()
        cache_key = f"transform_{session_id}_{intent}_{norm_entity}"
        
        cached = transform_cache.get(cache_key)
        if cached:
            logger.info(f"Transformation cache hit for key: {cache_key}")
            # Stream the cached answer
            yield {"text": cached["response"], "done": False}
            yield {
                "done": True,
                "citations": cached.get("citations") or [],
                "suggested_questions": cached.get("suggested_questions") or [],
                "redirect": cached.get("redirect"),
                "source": cached.get("source", f"Transformed ({intent})"),
                "verified": cached.get("verified", True),
                "confidence": cached.get("confidence", 1.0),
                "attribution": cached.get("attribution") or {
                    "source": f"Transformed ({intent})",
                    "knowledge_file": "transform_cache",
                    "entity": active_entity,
                    "confidence": 1.0,
                    "verified": True
                },
                "metrics": {
                    "intent_time": time.time() - start_time,
                    "cache_hit": 1,
                    "cache_time": time.time() - start_time,
                    "embedding_time": 0.0,
                    "retrieval_time": 0.0,
                    "llm_time": 0.0,
                    "streaming_time": 0.0,
                    "total_time": time.time() - start_time,
                    "prompt_tokens": 0,
                    "completion_tokens": len(cached["response"]) // 4
                }
            }
            # Update state with this query & response (per rules: "Update this after every successfully validated answer")
            state["last_query"] = query
            state["last_intent"] = intent
            state["last_response"] = cached["response"]
            state["last_source"] = "nvidia"
            state["timestamp"] = datetime.now(timezone.utc).isoformat()
            return

        # 3. Determine prompt & messages
        system_prompt = ""
        if intent == "SIMPLIFY":
            system_prompt = (
                "You are the CittaAI Enterprise AI Consultant. "
                "Rewrite the following previous response using very simple English. "
                "Do not change facts, do not remove important information, do not add new information. "
                "Keep product names unchanged. Return only the rewritten answer.\n\n"
                "--- PREVIOUS RESPONSE ---\n"
                f"{last_response}"
            )
        elif intent == "ELABORATE":
            system_prompt = (
                "You are the CittaAI Enterprise AI Consultant. "
                "Expand the following previous response and explain concepts more clearly. "
                "Do not hallucinate. Only use information already contained in the previous answer.\n\n"
                "--- PREVIOUS RESPONSE ---\n"
                f"{last_response}"
            )
        elif intent == "SUMMARIZE":
            system_prompt = (
                "You are the CittaAI Enterprise AI Consultant. "
                "Summarize the following previous response in under 80 words, preserving key facts.\n\n"
                "--- PREVIOUS RESPONSE ---\n"
                f"{last_response}"
            )
        elif intent == "EXAMPLE":
            system_prompt = (
                "You are the CittaAI Enterprise AI Consultant. "
                "Provide a practical business example based only on the following previous response. "
                "Do not invent products.\n\n"
                "--- PREVIOUS RESPONSE ---\n"
                f"{last_response}"
            )
        elif intent == "REPHRASE":
            system_prompt = (
                "You are the CittaAI Enterprise AI Consultant. "
                "Rewrite the following previous response professionally, keeping the meaning identical.\n\n"
                "--- PREVIOUS RESPONSE ---\n"
                f"{last_response}"
            )
        elif intent == "TRANSLATE":
            lang = extract_target_language(query)
            system_prompt = (
                "You are the CittaAI Enterprise AI Consultant. "
                f"Translate the following previous response into {lang}. "
                "Keep CittaAI product/service/solution names in English (e.g. WhatsApp Marketing Platform, Enterprise AI OS, AI Strategy, etc.). "
                "Return only the translated response.\n\n"
                "--- PREVIOUS RESPONSE ---\n"
                f"{last_response}"
            )
        elif intent == "FOLLOW_UP":
            system_prompt = (
                "You are the CittaAI Enterprise AI Consultant. "
                f"Given the active entity '{active_entity}' and the previous answer, generate a natural follow-up explanation "
                f"answering the new question about that same entity: '{query}'. "
                "Use the previous answer as the ground truth context. Do not hallucinate or invent new details. "
                "Ground your response in the previous answer. Keep CittaAI product, service, and solution names exactly as they are.\n\n"
                "--- PREVIOUS ANSWER ---\n"
                f"{last_response}"
            )
        else:
            logger.error(f"Unsupported transformation intent: {intent}")
            yield {"text": "I encountered an unsupported operation.", "done": True}
            return

        llm_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        prompt_tokens = len(json.dumps(llm_messages)) // 4
        llm_start = time.time()
        complete_response = ""
        first_token_latency = 0.0
        first_token_received = False
        streaming_start = 0.0
        
        # 4. Stream response from provider
        try:
            async for chunk in self.provider.generate_stream(
                messages=llm_messages,
                model=model,
                temperature=0.3
            ):
                if not first_token_received:
                    first_token_received = True
                    first_token_latency = time.time() - llm_start
                    streaming_start = time.time()
                text_part = chunk.get("text", "") if isinstance(chunk, dict) else chunk
                complete_response += text_part
                yield {"text": text_part, "done": False}
        except Exception:
            logger.exception("Error during transformed LLM stream generation")
            complete_response = "I encountered an error trying to process this transformation."
            yield {"text": complete_response, "done": False}
            
        streaming_time = (time.time() - streaming_start) if first_token_received else 0.0
        completion_tokens = len(complete_response) // 4
        tokens_per_second = completion_tokens / streaming_time if streaming_time > 0 else 0.0
        
        # 5. Run Response Validator
        val_ok, verified_text = validate_response(complete_response)
        if not val_ok:
            logger.warning(f"Transformation response failed validation check. Applying correction.")
            complete_response = verified_text
            yield {"text": "\n\n*Validation checks applied:* " + complete_response, "done": False}
            
        # 6. Cache & Update state
        sugs = ["Show Products", "Show Services", "Show Solutions"]
        attribution = {
            "source": f"Transformed ({intent})",
            "knowledge_file": "llm_transformer",
            "entity": active_entity,
            "confidence": 1.0,
            "verified": val_ok
        }
        
        transform_cache.set(cache_key, {
            "response": complete_response,
            "citations": last_citations,
            "suggested_questions": sugs,
            "redirect": last_redirect,
            "source": f"Transformed ({intent})",
            "verified": val_ok,
            "confidence": 1.0,
            "attribution": attribution
        })
        
        # Update active turn state
        state["last_query"] = query
        state["last_intent"] = intent
        state["last_response"] = complete_response
        state["last_source"] = "nvidia"
        state["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # 7. Final done packet
        yield {
            "done": True,
            "citations": last_citations,
            "suggested_questions": sugs,
            "redirect": last_redirect,
            "source": f"Transformed ({intent})",
            "verified": val_ok,
            "confidence": 1.0,
            "attribution": attribution,
            "metrics": {
                "intent_time": time.time() - start_time,
                "cache_hit": 0,
                "cache_time": 0.0,
                "embedding_time": 0.0,
                "retrieval_time": 0.0,
                "llm_time": time.time() - llm_start,
                "streaming_time": streaming_time,
                "total_time": time.time() - start_time,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "first_token_latency": first_token_latency,
                "tokens_per_second": tokens_per_second
            }
        }
