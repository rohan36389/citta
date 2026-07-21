import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class HybridRetrievalReranker:
    def __init__(self, vector_store=None):
        self.vector_store = vector_store

    def rerank(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_n: int = 5,
        domain_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not chunks:
            return []

        q_terms = set(query.lower().split())
        scored_chunks = []

        for idx, chunk in enumerate(chunks):
            content = chunk.get("content", "").lower()
            dense_score = chunk.get("score", 0.5)

            # BM25-style keyword overlap score
            term_overlap = sum(1 for term in q_terms if len(term) > 3 and term in content)
            bm25_bonus = min(term_overlap * 0.08, 0.3)

            # Domain metadata filter match bonus
            meta = chunk.get("metadata", {})
            meta_domain = meta.get("domain", meta.get("category", "")).upper()
            domain_bonus = 0.1 if (domain_filter and domain_filter.upper() in meta_domain) else 0.0

            final_score = min(dense_score + bm25_bonus + domain_bonus, 1.0)
            chunk_copy = chunk.copy()
            chunk_copy["final_rerank_score"] = final_score
            scored_chunks.append(chunk_copy)

        # Sort by final rerank score descending
        scored_chunks.sort(key=lambda x: x["final_rerank_score"], reverse=True)

        # Select Top-N unique chunks
        unique_results = []
        seen_texts = set()
        for item in scored_chunks:
            norm_t = item["content"].strip().lower()
            if norm_t not in seen_texts:
                seen_texts.add(norm_t)
                unique_results.append(item)
                if len(unique_results) == top_n:
                    break

        logger.info(f"Hybrid Reranker: {len(chunks)} candidate chunks -> {len(unique_results)} reranked top chunks.")
        return unique_results

_reranker_instance = None

def get_retrieval_reranker(vector_store=None) -> HybridRetrievalReranker:
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = HybridRetrievalReranker(vector_store=vector_store)
    return _reranker_instance
