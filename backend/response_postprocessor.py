import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

PRODUCT_NAME_MAPPINGS = {
    r"\bwhatsapp\s+marketing(?!\s+platform)\b": "WhatsApp Marketing Platform",
    r"\binfluencer\s+marketing(?!\s+platform)\b": "Influencer Marketing Platform",
    r"\becommerce\s+os\b": "E-Commerce OS",
    r"\be-commerce\s+os\b": "E-Commerce OS",
    r"\bpharma\s+os\b": "Pharma & Healthcare OS",
    r"\breal\s+estate\s+os\b": "Real Estate OS",
    r"\beducation\s+os\b": "Education OS",
    r"\bsmart\s+cities\s+os\b": "Smart Cities OS",
    r"\benterprise\s+ai\s+os\b": "Enterprise AI OS",
}

class ResponsePostprocessor:
    def process(self, text: str) -> str:
        if not text or not text.strip():
            return text

        processed = text

        # 1. Product Naming Standardization
        for pattern, replacement in PRODUCT_NAME_MAPPINGS.items():
            processed = re.sub(pattern, replacement, processed, flags=re.IGNORECASE)

        # 2. Sentence Deduplication
        lines = processed.splitlines()
        cleaned_lines: List[str] = []
        seen_sentences = set()

        for line in lines:
            line_str = line.strip()
            if not line_str:
                cleaned_lines.append("")
                continue

            # Check sentence duplication for paragraph lines
            norm_line = re.sub(r"[^\w\s]", "", line_str.lower())
            if len(norm_line) > 25 and norm_line in seen_sentences:
                continue

            if len(norm_line) > 25:
                seen_sentences.add(norm_line)

            cleaned_lines.append(line_str)

        processed = "\n".join(cleaned_lines)

        # 3. Clean Markdown Bullet Formatting
        processed = re.sub(r"\n{3,}", "\n\n", processed)
        processed = re.sub(r"•\s*•", "•", processed)
        processed = re.sub(r"\*\*\s*\*\*", "", processed)

        return processed.strip()

_postprocessor_instance = None

def get_response_postprocessor() -> ResponsePostprocessor:
    global _postprocessor_instance
    if _postprocessor_instance is None:
        _postprocessor_instance = ResponsePostprocessor()
    return _postprocessor_instance
