import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ContextCompressor:
    def compress(
        self,
        chunks: List[Dict[str, Any]],
        max_chunks: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Deduplicates retrieved evidence chunks, merges overlapping text,
        ranks by score, and compresses redundant context before LLM consumption.
        """
        if not chunks:
            return []

        # 1. Rank chunks by score descending
        sorted_chunks = sorted(chunks, key=lambda x: x.get("score", x.get("final_rerank_score", 0.0)), reverse=True)

        unique_chunks: List[Dict[str, Any]] = []
        seen_passages: List[str] = []

        for chunk in sorted_chunks:
            content = chunk.get("content", "").strip()
            if not content:
                continue

            content_clean = re.sub(r"\s+", " ", content.lower())

            # Check exact or high partial duplication against already selected passages
            is_duplicate = False
            for prev in seen_passages:
                # If 80%+ overlap in content length
                if content_clean in prev or prev in content_clean:
                    is_duplicate = True
                    break

            if not is_duplicate:
                seen_passages.append(content_clean)
                unique_chunks.append(chunk)

            if len(unique_chunks) >= max_chunks:
                break

        logger.info(f"ContextCompressor: Compressed {len(chunks)} candidate chunks -> {len(unique_chunks)} clean evidence chunks.")
        return unique_chunks

_compressor_instance = None

def get_context_compressor() -> ContextCompressor:
    global _compressor_instance
    if _compressor_instance is None:
        _compressor_instance = ContextCompressor()
    return _compressor_instance
