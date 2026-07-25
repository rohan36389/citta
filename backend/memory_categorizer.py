import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

PREFERENCE_PATTERNS = [
    r"\bprefer(s|red)?\b", r"\balways\s+use\b", r"\blike\s+to\s+have\b", r"\bformat\b", r"\breport\s+style\b"
]

ACTION_PATTERNS = [
    r"\bbooked\b", r"\bscheduled\b", r"\bcreated\s+ticket\b", r"\bsent\s+proposal\b", r"\bworkflow\s+executed\b"
]

WORKFLOW_PATTERNS = [
    r"\bworkflow\b", r"\bpending\s+step\b", r"\bexecution\s+summary\b"
]

ORG_PATTERNS = [
    r"\bcompany\s+policy\b", r"\binternal\s+term\b", r"\bdepartment\b", r"\borganization\b"
]

class MemoryCategorizer:
    def __init__(self):
        pass

    def categorize(self, content_str: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        c_lower = str(content_str).lower().strip()
        meta = metadata or {}

        if meta.get("category"):
            return meta["category"].upper()

        if any(re.search(p, c_lower) for p in PREFERENCE_PATTERNS):
            return "PREFERENCE"

        if any(re.search(p, c_lower) for p in ACTION_PATTERNS):
            return "ACTION"

        if any(re.search(p, c_lower) for p in WORKFLOW_PATTERNS):
            return "WORKFLOW"

        if any(re.search(p, c_lower) for p in ORG_PATTERNS):
            return "ORG"

        return "CONVERSATION"

_memory_categorizer_instance = None

def get_memory_categorizer() -> MemoryCategorizer:
    global _memory_categorizer_instance
    if _memory_categorizer_instance is None:
        _memory_categorizer_instance = MemoryCategorizer()
    return _memory_categorizer_instance
