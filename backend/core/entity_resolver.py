import re
import time
import logging
from functools import lru_cache
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class EntityResolver:
    def __init__(self, registry):
        self.registry = registry

    def resolve(self, query: str, debug: bool = False) -> Dict[str, Any]:
        t_start = time.perf_counter()
        
        trace = []
        timings = {}
        
        # 1. Clean / Normalize base text
        t_norm_start = time.perf_counter()
        q_clean = query.lower().strip()
        # strip punctuation except hyphens/slashes
        q_clean = re.sub(r"[^\w\s\-\/]", "", q_clean)
        q_clean = re.sub(r"\s+", " ", q_clean).strip()
        timings["normalization_ms"] = (time.perf_counter() - t_norm_start) * 1000.0
        
        trace.append(f"normalized_query='{q_clean}'")

        if not q_clean:
            return {
                "entity_id": None,
                "registry": None,
                "entity_confidence": 0.0,
                "routing_confidence": 0.0,
                "confidence_level": "NONE",
                "matched_alias": None,
                "normalized_query": q_clean,
                "source": None,
                "trace": trace,
                "timings": timings
            }

        t_lookup_start = time.perf_counter()

        # Step 1: Exact Canonical ID or Name Match
        if q_clean in self.registry.entity_lookup:
            ent_id = self.registry.entity_lookup[q_clean]
            belongs_to = self.registry.knowledge_graph.get(ent_id, {}).get("belongs_to", "UNKNOWN")
            trace.append(f"canonical_exact_match='{q_clean}' -> {ent_id}")
            timings["lookup_ms"] = (time.perf_counter() - t_lookup_start) * 1000.0
            return {
                "entity_id": ent_id,
                "registry": belongs_to,
                "entity_confidence": 1.0,
                "routing_confidence": 1.0,
                "confidence_level": "EXACT",
                "matched_alias": q_clean,
                "normalized_query": q_clean,
                "source": "canonical",
                "trace": trace,
                "timings": timings
            }

        # Step 2: Exact Alias Match
        if q_clean in self.registry.alias_lookup:
            ent_id = self.registry.alias_lookup[q_clean]
            belongs_to = self.registry.knowledge_graph.get(ent_id, {}).get("belongs_to", "UNKNOWN")
            trace.append(f"alias_exact_match='{q_clean}' -> {ent_id}")
            timings["lookup_ms"] = (time.perf_counter() - t_lookup_start) * 1000.0
            return {
                "entity_id": ent_id,
                "registry": belongs_to,
                "entity_confidence": 1.0,
                "routing_confidence": 0.95,
                "confidence_level": "EXACT",
                "matched_alias": q_clean,
                "normalized_query": q_clean,
                "source": "alias",
                "trace": trace,
                "timings": timings
            }

        # Step 3: Exact Slug Match
        if q_clean in self.registry.slug_lookup:
            ent_id = self.registry.slug_lookup[q_clean]
            belongs_to = self.registry.knowledge_graph.get(ent_id, {}).get("belongs_to", "UNKNOWN")
            trace.append(f"slug_exact_match='{q_clean}' -> {ent_id}")
            timings["lookup_ms"] = (time.perf_counter() - t_lookup_start) * 1000.0
            return {
                "entity_id": ent_id,
                "registry": belongs_to,
                "entity_confidence": 1.0,
                "routing_confidence": 0.95,
                "confidence_level": "EXACT",
                "matched_alias": q_clean,
                "normalized_query": q_clean,
                "source": "slug",
                "trace": trace,
                "timings": timings
            }

        # Step 4: Exact Keyword Match
        if q_clean in self.registry.keyword_lookup:
            ent_id = self.registry.keyword_lookup[q_clean]
            belongs_to = self.registry.knowledge_graph.get(ent_id, {}).get("belongs_to", "UNKNOWN")
            trace.append(f"keyword_exact_match='{q_clean}' -> {ent_id}")
            timings["lookup_ms"] = (time.perf_counter() - t_lookup_start) * 1000.0
            return {
                "entity_id": ent_id,
                "registry": belongs_to,
                "entity_confidence": 0.90,
                "routing_confidence": 0.85,
                "confidence_level": "MEDIUM",
                "matched_alias": q_clean,
                "normalized_query": q_clean,
                "source": "keyword",
                "trace": trace,
                "timings": timings
            }

        # Step 5: Substring phrase lookup (Word boundary searches)
        GENERIC_WORDS = {"marketing", "platform", "system", "os", "service", "solution", "engineering", "ai", "team", "leaders", "about", "contact"}
        
        # Check canonicals
        for key in sorted(self.registry.entity_lookup.keys(), key=len, reverse=True):
            if key in GENERIC_WORDS:
                continue
            if len(key) > 3 and re.search(r"\b" + re.escape(key) + r"\b", q_clean):
                ent_id = self.registry.entity_lookup[key]
                belongs_to = self.registry.knowledge_graph.get(ent_id, {}).get("belongs_to", "UNKNOWN")
                trace.append(f"canonical_substring_match='{key}' -> {ent_id}")
                timings["lookup_ms"] = (time.perf_counter() - t_lookup_start) * 1000.0
                return {
                    "entity_id": ent_id,
                    "registry": belongs_to,
                    "entity_confidence": 0.95,
                    "routing_confidence": 0.90,
                    "confidence_level": "HIGH",
                    "matched_alias": key,
                    "normalized_query": q_clean,
                    "source": "canonical",
                    "trace": trace,
                    "timings": timings
                }

        # Check aliases
        for key in sorted(self.registry.alias_lookup.keys(), key=len, reverse=True):
            if key in GENERIC_WORDS:
                continue
            if len(key) > 3 and re.search(r"\b" + re.escape(key) + r"\b", q_clean):
                ent_id = self.registry.alias_lookup[key]
                belongs_to = self.registry.knowledge_graph.get(ent_id, {}).get("belongs_to", "UNKNOWN")
                trace.append(f"alias_substring_match='{key}' -> {ent_id}")
                timings["lookup_ms"] = (time.perf_counter() - t_lookup_start) * 1000.0
                return {
                    "entity_id": ent_id,
                    "registry": belongs_to,
                    "entity_confidence": 0.90,
                    "routing_confidence": 0.85,
                    "confidence_level": "HIGH",
                    "matched_alias": key,
                    "normalized_query": q_clean,
                    "source": "alias",
                    "trace": trace,
                    "timings": timings
                }

        # Check slugs
        for key in sorted(self.registry.slug_lookup.keys(), key=len, reverse=True):
            if key in GENERIC_WORDS:
                continue
            if len(key) > 3 and re.search(r"\b" + re.escape(key) + r"\b", q_clean):
                ent_id = self.registry.slug_lookup[key]
                belongs_to = self.registry.knowledge_graph.get(ent_id, {}).get("belongs_to", "UNKNOWN")
                trace.append(f"slug_substring_match='{key}' -> {ent_id}")
                timings["lookup_ms"] = (time.perf_counter() - t_lookup_start) * 1000.0
                return {
                    "entity_id": ent_id,
                    "registry": belongs_to,
                    "entity_confidence": 0.90,
                    "routing_confidence": 0.85,
                    "confidence_level": "HIGH",
                    "matched_alias": key,
                    "normalized_query": q_clean,
                    "source": "slug",
                    "trace": trace,
                    "timings": timings
                }

        # Check keywords
        for key in sorted(self.registry.keyword_lookup.keys(), key=len, reverse=True):
            if key in GENERIC_WORDS:
                continue
            if len(key) > 3 and re.search(r"\b" + re.escape(key) + r"\b", q_clean):
                ent_id = self.registry.keyword_lookup[key]
                belongs_to = self.registry.knowledge_graph.get(ent_id, {}).get("belongs_to", "UNKNOWN")
                trace.append(f"keyword_substring_match='{key}' -> {ent_id}")
                timings["lookup_ms"] = (time.perf_counter() - t_lookup_start) * 1000.0
                return {
                    "entity_id": ent_id,
                    "registry": belongs_to,
                    "entity_confidence": 0.80,
                    "routing_confidence": 0.75,
                    "confidence_level": "MEDIUM",
                    "matched_alias": key,
                    "normalized_query": q_clean,
                    "source": "keyword",
                    "trace": trace,
                    "timings": timings
                }

        timings["lookup_ms"] = (time.perf_counter() - t_lookup_start) * 1000.0

        # Step 6: Fuzzy Match (WRatio >= 90%)
        t_fuzzy_start = time.perf_counter()
        try:
            from rapidfuzz import process, fuzz
            candidates = list(self.registry.entity_lookup.keys()) + list(self.registry.alias_lookup.keys()) + list(self.registry.slug_lookup.keys())
            match = process.extractOne(q_clean, candidates, scorer=fuzz.WRatio)
            if match and match[1] >= 90.0:
                best_str = match[0]
                ent_id = self.registry.entity_lookup.get(best_str) or self.registry.alias_lookup.get(best_str) or self.registry.slug_lookup.get(best_str)
                if ent_id:
                    belongs_to = self.registry.knowledge_graph.get(ent_id, {}).get("belongs_to", "UNKNOWN")
                    trace.append(f"fuzzy_match='{best_str}' (score={match[1]:.1f}) -> {ent_id}")
                    timings["fuzzy_ms"] = (time.perf_counter() - t_fuzzy_start) * 1000.0
                    return {
                        "entity_id": ent_id,
                        "registry": belongs_to,
                        "entity_confidence": float(match[1] / 100.0),
                        "routing_confidence": float(match[1] / 100.0 * 0.90),
                        "confidence_level": "FUZZY",
                        "matched_alias": best_str,
                        "normalized_query": q_clean,
                        "source": "alias",
                        "trace": trace,
                        "timings": timings
                    }
        except Exception as e:
            logger.warning(f"Fuzzy matching failed in core/entity_resolver: {e}")

        timings["fuzzy_ms"] = (time.perf_counter() - t_fuzzy_start) * 1000.0

        trace.append("resolution_failed")
        return {
            "entity_id": None,
            "registry": None,
            "entity_confidence": 0.0,
            "routing_confidence": 0.0,
            "confidence_level": "NONE",
            "matched_alias": None,
            "normalized_query": q_clean,
            "source": None,
            "trace": trace,
            "timings": timings
        }

@lru_cache(maxsize=2048)
def _resolve_cached(query: str) -> Dict[str, Any]:
    from knowledge_registry import get_registry
    registry = get_registry()
    resolver = EntityResolver(registry)
    return resolver.resolve(query)

def resolve(query: str, debug: bool = False) -> Dict[str, Any]:
    """Expose simple public resolve API using cached resolver."""
    if debug:
        from knowledge_registry import get_registry
        return EntityResolver(get_registry()).resolve(query, debug=True)
    return _resolve_cached(query)
