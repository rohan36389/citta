import re
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class IntentType:
    ASK = "ASK"
    LIST = "LIST"
    COUNT = "COUNT"
    COMPARE = "COMPARE"
    CONTACT = "CONTACT"
    RECOMMEND = "RECOMMEND"
    SEARCH = "SEARCH"
    SUMMARIZE = "SUMMARIZE"
    GREETING = "GREETING"
    THANKS = "THANKS"
    GOODBYE = "GOODBYE"
    SMALL_TALK = "SMALL_TALK"
    OUT_OF_DOMAIN = "OUT_OF_DOMAIN"
    HELP = "HELP"
    MENU = "MENU"
    ABOUT = "ABOUT"

class TopicType:
    COMPANY = "COMPANY"
    PRODUCTS = "PRODUCTS"
    SERVICES = "SERVICES"
    SOLUTIONS = "SOLUTIONS"
    MISSION = "MISSION"
    VISION = "VISION"
    VALUES = "VALUES"
    LEADERSHIP = "LEADERSHIP"
    PERSON_LOOKUP = "PERSON_LOOKUP"
    AWARDS = "AWARDS"
    CERTIFICATIONS = "CERTIFICATIONS"
    TECHNOLOGIES = "TECHNOLOGIES"
    CASE_STUDIES = "CASE_STUDIES"
    PRICING = "PRICING"
    LOCATION = "LOCATION"
    CONTACT_INFO = "CONTACT_INFO"
    FAQS = "FAQS"

TOPIC_PATTERNS = {
    TopicType.COMPANY: [r"\babout\b", r"\boverview\b", r"\bcompany\b", r"\bwho\s+are\s+we\b", r"\bwho\s+is\b", r"\bdescribe\b", r"\bintroduction\b"],
    TopicType.MISSION: [r"\bmission\b", r"\bour\s+mission\b", r"\bcompany\s+mission\b"],
    TopicType.VISION: [r"\bvision\b", r"\bour\s+vision\b", r"\bcompany\s+vision\b"],
    TopicType.VALUES: [r"\bvalues\b", r"\bcore\s+values\b", r"\bour\s+values\b"],
    TopicType.LEADERSHIP: [r"\bleadership\b", r"\bleaders\b", r"\bexecutives\b", r"\bteam\b", r"\bmanagement\b", r"\bdirectors\b"],
    TopicType.PERSON_LOOKUP: [r"\bceo\b", r"\bcto\b", r"\bcoo\b", r"\bcmo\b", r"\bfounder\b", r"\bpresident\b", r"\bhead\s+of\b"],
    TopicType.PRODUCTS: [r"\bproducts\b", r"\bproduct\b", r"\bplatform\b", r"\bplatforms\b", r"\bsoftware\b", r"\bwhatsapp\b", r"\binfluencer\b"],
    TopicType.SERVICES: [r"\bservices\b", r"\bservice\b", r"\bconsulting\b", r"\badvisory\b", r"\bengineering\b"],
    TopicType.SOLUTIONS: [r"\bsolutions\b", r"\bsolution\b", r"\becommerce\s+os\b", r"\breal\s+estate\s+os\b", r"\bpharma\s+os\b", r"\beducation\s+os\b", r"\bsmart\s+cities\s+os\b"],
    TopicType.CASE_STUDIES: [r"\bcase\s+study\b", r"\bcase\s+studies\b", r"\bsuccess\s+story\b", r"\bsuccess\s+stories\b", r"\bresults\b", r"\bmetrics\b"],
    TopicType.AWARDS: [r"\bawards\b", r"\baward\b", r"\brecognition\b", r"\baccolades\b", r"\bmsme\b", r"\bachievements\b", r"\bachievement\b"],
    TopicType.CERTIFICATIONS: [r"\bcertification\b", r"\bcertifications\b", r"\bcompliance\b", r"\baccreditation\b", r"\baccreditations\b"],
    TopicType.TECHNOLOGIES: [r"\btechnology\b", r"\btechnologies\b", r"\btech\s+stack\b", r"\bframework\b", r"\bllm\b", r"\brag\b", r"\bagents\b"],
    TopicType.PRICING: [r"\bpricing\b", r"\bcost\b", r"\bprice\b", r"\bquote\b", r"\bplans\b", r"\bsubscription\b"],
    TopicType.LOCATION: [r"\blocation\b", r"\baddress\b", r"\boffice\b", r"\bwhere\s+is\b", r"\bheadquarters\b"],
    TopicType.CONTACT_INFO: [r"\bcontact\b", r"\bphone\b", r"\bemail\b", r"\breach\b", r"\bsales\b", r"\bapply\b", r"\bjob\b", r"\bcareers\b"]
}

INTENT_PATTERNS = {
    IntentType.GREETING: [r"^(hi|hello|hey|greetings|good\s+morning|good\s+afternoon)\b"],
    IntentType.THANKS: [r"^(thanks|thank\s+you|thx|cheers)\b"],
    IntentType.GOODBYE: [r"^(bye|goodbye|see\s+you|farewell)\b"],
    IntentType.COUNT: [r"\bhow\s+many\b", r"\bnumber\s+of\b", r"\bcount\s+of\b", r"\btotal\b"],
    IntentType.LIST: [r"\blist\b", r"\bshow\s+all\b", r"\bshow\s+products\b", r"\bshow\s+services\b", r"\bshow\s+solutions\b", r"\bshow\s+case\s+studies\b", r"^(products|services|solutions|case\s+studies|leadership)$"],
    IntentType.COMPARE: [r"\bcompare\b", r"\bdifference\b", r"\bversus\b", r"\bvs\b"],
    IntentType.RECOMMEND: [r"\brecommend\b", r"\bsuggest\b", r"\bbest\s+option\b", r"\bwhich\s+one\b"],
    IntentType.CONTACT: [r"\bcontact\b", r"\bbook\s+a\s+demo\b", r"\bhire\b", r"\bapply\b", r"\bquote\b"],
    IntentType.HELP: [r"^(help|info|support|guide)\b"],
    IntentType.MENU: [r"^(menu|options|nav|navigation)\b"],
    IntentType.ABOUT: [r"^(about|overview)\b"]
}

@dataclass
class IntentAnalysisResult:
    primary_intent: str
    topics: List[str]
    is_multi_topic: bool
    is_deterministic: bool
    confidence: float

class IntentAnalyzer:
    def analyze(self, query: str) -> IntentAnalysisResult:
        q_lower = query.lower().strip()

        # 1. Check Primary Intent
        detected_intent = IntentType.ASK
        for intent, patterns in INTENT_PATTERNS.items():
            for p in patterns:
                if re.search(p, q_lower):
                    detected_intent = intent
                    break
            if detected_intent != IntentType.ASK:
                break

        # 2. Extract All Topics
        detected_topics: List[str] = []
        for topic, patterns in TOPIC_PATTERNS.items():
            for p in patterns:
                if re.search(p, q_lower):
                    if topic not in detected_topics:
                        detected_topics.append(topic)
                    break

        if not detected_topics and detected_intent == IntentType.ASK:
            detected_topics = [TopicType.COMPANY]

        is_multi = len(detected_topics) > 1
        
        is_deterministic = (
            detected_intent in [
                IntentType.GREETING, IntentType.THANKS, IntentType.GOODBYE, 
                IntentType.COUNT, IntentType.HELP, IntentType.MENU, 
                IntentType.ABOUT, IntentType.CONTACT
            ] 
            or (detected_intent == IntentType.LIST and len(query.split()) <= 4)
            or (detected_intent == IntentType.ASK and any(t in detected_topics for t in [TopicType.AWARDS, TopicType.CONTACT_INFO, TopicType.COMPANY]))
        )

        return IntentAnalysisResult(
            primary_intent=detected_intent,
            topics=detected_topics,
            is_multi_topic=is_multi,
            is_deterministic=is_deterministic,
            confidence=1.0 if is_deterministic else 0.9
        )

def get_intent_analyzer() -> IntentAnalyzer:
    return IntentAnalyzer()
