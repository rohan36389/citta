import logging
from typing import Dict, Any, Optional, List, Union, Tuple

logger = logging.getLogger(__name__)

def _format_section_value(val: Any) -> str:
    """Formats a section value (dict, list, or str) into structured human-readable markdown text."""
    if not val:
        return ""
    if isinstance(val, str):
        return val.strip()
    elif isinstance(val, list):
        items = []
        for item in val:
            if isinstance(item, dict):
                q = item.get("question") or item.get("title") or item.get("name")
                a = item.get("answer") or item.get("description") or item.get("summary")
                if q and a:
                    items.append(f"- Question: {q}\n  Answer: {a}")
                elif q:
                    items.append(f"- {q}")
            else:
                items.append(f"- {str(item)}")
        return "\n".join(items)
    elif isinstance(val, dict):
        lines = []
        for k, v in val.items():
            k_title = k.replace("_", " ").title()
            if isinstance(v, list):
                lines.append(f"{k_title}:")
                lines.extend(f"  - {str(item)}" for item in v)
            elif isinstance(v, dict):
                lines.append(f"{k_title}:")
                for sub_k, sub_v in v.items():
                    lines.append(f"  - {sub_k.replace('_', ' ').title()}: {sub_v}")
            else:
                lines.append(f"{k_title}: {v}")
        return "\n".join(lines)
    return str(val)

_CONTEXT_CACHE: Dict[Tuple[str, str], str] = {}

class ContextBuilder:
    """
    ContextBuilder:
    The single canonical component responsible for building factual context for the LLM.
    
    Guarantees:
    - Never sends raw JSON to the LLM.
    - Never sends unrelated sections or entities.
    - Single source of truth for LLM context assembly.
    - The LLM receives pre-filtered, structured factual context and only writes natural language.
    """

    def __init__(self, registry=None):
        self.registry = registry

    def build_context(
        self,
        resolved_entity: Optional[Union[str, Dict[str, Any]]] = None,
        resolved_section: Optional[str] = None,
        registry: Optional[Any] = None,
        conversation_state: Optional[Dict[str, Any]] = None,
        evidence_chunks: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Builds structured context for the LLM from resolved entity, section, registry, and state.
        Uses in-memory context cache for static entity-section pairs when state is clear.
        """
        conversation_state = conversation_state or {}
        history = conversation_state.get("history", [])
        
        # Check cache for static entity-section pairs
        entity_id_str = resolved_entity if isinstance(resolved_entity, str) else (resolved_entity.get("id") if isinstance(resolved_entity, dict) else "")
        section_str = resolved_section or "overview"
        cache_key = (str(entity_id_str), str(section_str))
        
        if not history and not evidence_chunks and cache_key in _CONTEXT_CACHE:
            return _CONTEXT_CACHE[cache_key]
        reg = registry or self.registry
        conversation_state = conversation_state or {}
        
        # Resolve entity dict if string ID was passed
        entity_id = None
        entity_data = None
        if isinstance(resolved_entity, str):
            entity_id = resolved_entity
            if reg and hasattr(reg, "get_entity"):
                entity_data = reg.get_entity(entity_id)
        elif isinstance(resolved_entity, dict):
            entity_data = resolved_entity
            entity_id = entity_data.get("id")

        context_parts = []
        
        # 1. Company Metadata Header
        if reg and hasattr(reg, "company") and reg.company:
            comp_name = reg.company.get("name", "CittaAI")
            comp_desc = reg.company.get("description", "")
            context_parts.append(f"COMPANY OVERVIEW:\n- Name: {comp_name}\n- Description: {comp_desc}")

        # 2. Entity & Section Core Context
        if entity_data:
            ent_name = entity_data.get("name") or entity_data.get("title") or entity_id
            ent_summary = entity_data.get("summary") or entity_data.get("description") or ""
            
            ent_lines = [f"ENTITY: {ent_name}"]
            if ent_summary:
                ent_lines.append(f"Overview: {ent_summary}")
            
            # Check sections dictionary OR top-level keys in entity_data
            sections_data = entity_data.get("sections") if isinstance(entity_data.get("sections"), dict) else {}
            sec_name = resolved_section.lower().strip() if resolved_section else "overview"
            
            # Primary Requested Section Content
            primary_content = ""
            if sec_name in sections_data:
                primary_content = _format_section_value(sections_data[sec_name])
            elif sec_name in entity_data:
                primary_content = _format_section_value(entity_data[sec_name])
            elif sec_name != "overview":
                # Fallback check top-level overview
                if "overview" in entity_data:
                    primary_content = _format_section_value(entity_data["overview"])
                elif "description" in entity_data:
                    primary_content = entity_data["description"]
                    
            if primary_content:
                ent_lines.append(f"\nPRIMARY SECTION ({sec_name.replace('_', ' ').title()}):\n{primary_content}")

            # Relevant Features / Capabilities
            features_val = entity_data.get("features") or entity_data.get("capabilities") or entity_data.get("modules")
            if features_val and sec_name != "features":
                formatted_feat = _format_section_value(features_val)
                if formatted_feat:
                    ent_lines.append(f"\nRELEVANT FEATURES & CAPABILITIES:\n{formatted_feat}")

            # Related Technologies
            tech_val = entity_data.get("technologies")
            if tech_val and sec_name != "technologies":
                formatted_tech = _format_section_value(tech_val)
                if formatted_tech:
                    ent_lines.append(f"\nRELATED TECHNOLOGIES:\n{formatted_tech}")

            # Related Integrations
            integ_val = entity_data.get("integrations")
            if integ_val and sec_name != "integrations":
                formatted_integ = _format_section_value(integ_val)
                if formatted_integ:
                    ent_lines.append(f"\nSUPPORTED INTEGRATIONS:\n{formatted_integ}")

            # Knowledge Graph & Entity FAQs & Case Studies
            faq_val = entity_data.get("faq") or entity_data.get("faqs")
            if faq_val and sec_name != "faq":
                formatted_faq = _format_section_value(faq_val)
                if formatted_faq:
                    ent_lines.append(f"\nRELATED FAQs:\n{formatted_faq}")

            cs_val = entity_data.get("case_studies")
            if cs_val and sec_name != "case_studies":
                formatted_cs = _format_section_value(cs_val)
                if formatted_cs:
                    ent_lines.append(f"\nRELEVANT CASE STUDIES:\n{formatted_cs}")

            context_parts.append("\n".join(ent_lines))

        # 3. Evidence Chunks (RAG retrieved passages with Context Compressor)
        if evidence_chunks:
            try:
                from context_compressor import get_context_compressor
                compressed = get_context_compressor().compress(evidence_chunks)
            except Exception:
                compressed = evidence_chunks
            retrieved_text = []
            for chunk in compressed:
                content = chunk.get("content") if isinstance(chunk, dict) else str(chunk)
                if content:
                    retrieved_text.append(content)
            if retrieved_text:
                context_parts.append("RETRIEVED FACTUAL EVIDENCE:\n" + "\n---\n".join(retrieved_text))

        # 4. Conversation History (if present in state)
        history = conversation_state.get("history", [])
        if history:
            hist_lines = ["CONVERSATION HISTORY:"]
            for turn in history[-3:]:
                role = turn.get("role", "user").capitalize()
                content = turn.get("content", "")
                hist_lines.append(f"{role}: {content}")
            context_parts.append("\n".join(hist_lines))

        full_structured_context = "\n\n".join(context_parts)
        if not history and not evidence_chunks and cache_key[0]:
            _CONTEXT_CACHE[cache_key] = full_structured_context
        return full_structured_context

def build_structured_context(
    resolved_entity: Optional[Union[str, Dict[str, Any]]] = None,
    resolved_section: Optional[str] = None,
    registry: Optional[Any] = None,
    conversation_state: Optional[Dict[str, Any]] = None,
    evidence_chunks: Optional[List[Dict[str, Any]]] = None
) -> str:
    """Convenience helper function to construct structured context."""
    builder = ContextBuilder(registry=registry)
    return builder.build_context(
        resolved_entity=resolved_entity,
        resolved_section=resolved_section,
        registry=registry,
        conversation_state=conversation_state,
        evidence_chunks=evidence_chunks
    )
