import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Standard Out-of-Domain Topic Patterns
OUT_OF_DOMAIN_PATTERNS = [
    r"\bcricket\b", r"\bfootball\b", r"\bbasketball\b", r"\bbaseball\b", r"\bsports?\b", r"\bmatch\b", r"\bscore\b",
    r"\bweather\b", r"\brain\b", r"\btemperature\b", r"\bforecast\b", r"\bsunny\b",
    r"\bpolitics?\b", r"\belection\b", r"\bminister\b", r"\bpresident\b", r"\bdemocrat\b", r"\brepublican\b",
    r"\bmovie\b", r"\bcinema\b", r"\bactor\b", r"\bactress\b", r"\bsong\b", r"\bmusic\b", r"\bcelebrity\b",
    r"\bmedical\s+advice\b", r"\bdoctor\b", r"\bsymptom\b", r"\bdisease\b", r"\bmedicine\b",
    r"\brecipe\b", r"\bcooking\b", r"\bhoroscope\b", r"\bastrology\b", r"\bjoke\b", r"\bpython\s+code\b", r"\bjava\s+code\b"
]

# Explicit CittaAI / Enterprise AI In-Domain Keywords
IN_DOMAIN_PATTERNS = [
    r"\bcittaai\b", r"\bcitta\b", r"\bproduct\b", r"\bservice\b", r"\bsolution\b", r"\bplatform\b",
    r"\b[a-z0-9\s\-]+\s+(os|platform|service|solution|solutions)\b",
    r"\beducation\s+os\b", r"\bpharma\s+os\b", r"\breal\s+estate\s+os\b", r"\bsmart\s+cities\s+os\b",
    r"\benterprise\s+ai\s+os\b", r"\be-?commerce\s+os\b", r"\bwhatsapp\s+marketing\b", r"\binfluencer\s+marketing\b",
    r"\bdata\s+engineering\b", r"\bagentic\s+ai\b", r"\bmartech\s+360\b", r"\bai\s+strategy\b",
    r"\bpricing\b", r"\bcase\s+stud(y|ies)\b", r"\bleadership\b", r"\bceo\b", r"\bcto\b", r"\bcoo\b",
    r"\bcontact\b", r"\boffice\b", r"\bhyderabad\b", r"\baward\b", r"\brecognition\b"
]

DEFAULT_OOD_RESPONSE = (
    "I specialize in CittaAI's enterprise AI products, solutions, services, and software catalog. "
    "I don't have information on general topics like sports, weather, or politics. "
    "Feel free to ask me about our offerings such as Education OS, Pharma OS, Data Engineering, or WhatsApp Marketing!"
)

class OutOfDomainDetector:
    def __init__(self):
        pass

    def is_out_of_domain(self, query: str) -> Tuple[bool, str]:
        q_lower = query.lower().strip()

        # Check explicit in-domain matches first
        for p in IN_DOMAIN_PATTERNS:
            if re.search(p, q_lower):
                return False, ""

        # Check explicit out-of-domain patterns
        for p in OUT_OF_DOMAIN_PATTERNS:
            if re.search(p, q_lower):
                return True, DEFAULT_OOD_RESPONSE

        # If query has no in-domain keywords and no out-of-domain keywords, default to false (let orchestrator check general catalog)
        return False, ""

_ood_detector_instance = None

def get_out_of_domain_detector() -> OutOfDomainDetector:
    global _ood_detector_instance
    if _ood_detector_instance is None:
        _ood_detector_instance = OutOfDomainDetector()
    return _ood_detector_instance
