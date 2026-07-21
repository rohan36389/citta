import re
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class IntentCategory:
    GREETING = "GREETING"
    COMPANY_OVERVIEW = "COMPANY_OVERVIEW"
    PRODUCTS = "PRODUCTS"
    SOLUTIONS = "SOLUTIONS"
    SERVICES = "SERVICES"
    INDUSTRIES = "INDUSTRIES"
    LEADERSHIP = "LEADERSHIP"
    CAREERS = "CAREERS"
    CONTACT = "CONTACT"
    LOCATION = "LOCATION"
    PRICING = "PRICING"
    TECHNOLOGY = "TECHNOLOGY"
    AI_MODELS = "AI_MODELS"
    PARTNERSHIPS = "PARTNERSHIPS"
    CASE_STUDIES = "CASE_STUDIES"
    DEMO_REQUESTS = "DEMO_REQUESTS"
    SUPPORT = "SUPPORT"
    SMALL_TALK = "SMALL_TALK"
    UNKNOWN = "UNKNOWN"

INTENT_RULES: Dict[str, List[str]] = {
    IntentCategory.GREETING: [
        r"^(hi|hello|hey|greetings|good\s+morning|good\s+afternoon|good\s+evening)\b",
        r"\bhow\s+are\s+you\b"
    ],
    IntentCategory.COMPANY_OVERVIEW: [
        r"\bwho\s+are\s+you\b", r"\btell\s+me\s+about\s+cittaai\b", r"\bwhat\s+is\s+cittaai\b",
        r"\bintroduce\s+your\s+company\b", r"\bwhat\s+does\s+your\b", r"\babout\s+cittaai\b",
        r"\bcompany\s+overview\b", r"\bdescribe\s+cittaai\b", r"\borganization\b", r"\bwho\s+is\s+cittaai\b"
    ],
    IntentCategory.PRODUCTS: [
        r"\bproducts?\b", r"\bplatforms?\b", r"\bwhatsapp\s+marketing\b", r"\binfluencer\s+marketing\b",
        r"\bwhat\s+products\b", r"\bproduct\s+list\b"
    ],
    IntentCategory.SOLUTIONS: [
        r"\bsolutions?\b", r"\be-?commerce\s+os\b", r"\bpharma\s+os\b", r"\breal\s+estate\s+os\b",
        r"\beducation\s+os\b", r"\bsmart\s+cities\s+os\b", r"\benterprise\s+ai\s+os\b", r"\boperating\s+system\b"
    ],
    IntentCategory.SERVICES: [
        r"\bservices?\b", r"\bconsulting\b", r"\bdata\s+engineering\b", r"\bagentic\s+ai\b",
        r"\bai\s+strategy\b", r"\bmartech\s+360\b", r"\badvisory\b"
    ],
    IntentCategory.INDUSTRIES: [
        r"\bhealthcare\b", r"\bhospitals?\b", r"\bmedical\b", r"\bretail\b", r"\be-?commerce\b",
        r"\bpharma\b", r"\beducation\b", r"\bschools?\b", r"\buniversities?\b", r"\breal\s+estate\b",
        r"\bindustry\b", r"\bindustries\b", r"\bverticals?\b"
    ],
    IntentCategory.LEADERSHIP: [
        r"\bceo\b", r"\bcto\b", r"\bcoo\b", r"\bfounder\b", r"\bleadership\b", r"\bleaders\b",
        r"\bwho\s+leads\b", r"\bwho\s+manages\b", r"\bexecutives?\b", r"\bmanagement\b", r"\bteam\b"
    ],
    IntentCategory.CAREERS: [
        r"\bcareers?\b", r"\bjobs?\b", r"\bhiring\b", r"\bopenings?\b", r"\bapply\b", r"\binternship\b"
    ],
    IntentCategory.CONTACT: [
        r"\bcontact\b", r"\bphone\b", r"\bemail\b", r"\breach\s+sales\b", r"\btalk\s+to\s+team\b", r"\bget\s+in\s+touch\b"
    ],
    IntentCategory.LOCATION: [
        r"\blocation\b", r"\baddress\b", r"\boffice\b", r"\bwhere\s+are\s+you\b", r"\bheadquarters\b", r"\bhyderabad\b", r"\bmadhapur\b"
    ],
    IntentCategory.PRICING: [
        r"\bpricing\b", r"\bcost\b", r"\bprice\b", r"\bquote\b", r"\bplans\b", r"\bcharge\b"
    ],
    IntentCategory.TECHNOLOGY: [
        r"\btech\s+stack\b", r"\btechnology\b", r"\btechnologies\b", r"\bframework\b", r"\barchitecture\b"
    ],
    IntentCategory.AI_MODELS: [
        r"\bllm\b", r"\brag\b", r"\bgraphrag\b", r"\bgenerative\s+ai\b", r"\bmachine\s+learning\b",
        r"\bai\s+models?\b", r"\bdeep\s+learning\b"
    ],
    IntentCategory.PARTNERSHIPS: [
        r"\bpartner\b", r"\bpartnerships?\b", r"\bcollaboration\b", r"\bcollaborate\b"
    ],
    IntentCategory.CASE_STUDIES: [
        r"\bcase\s+stud(y|ies)\b", r"\bsuccess\s+stor(y|ies)\b", r"\bresults\b", r"\bmetrics\b"
    ],
    IntentCategory.DEMO_REQUESTS: [
        r"\bbook\s+a?\s*demo\b", r"\bschedule\s+a?\s*demo\b", r"\bdemo\b", r"\btrial\b"
    ],
    IntentCategory.SUPPORT: [
        r"\bhelp\b", r"\bsupport\b", r"\bassistance\b", r"\bissue\b"
    ],
    IntentCategory.SMALL_TALK: [
        r"\bthanks?\b", r"\bthank\s+you\b", r"\bbye\b", r"\bgoodbye\b", r"\bcool\b", r"\bgreat\b"
    ]
}

ANCHOR_TEXTS: Dict[str, str] = {
    IntentCategory.GREETING: "hello hi hey greetings good morning",
    IntentCategory.COMPANY_OVERVIEW: "tell me about cittaai company overview background vision mission history",
    IntentCategory.PRODUCTS: "software products platforms whatsapp marketing influencer marketing tools",
    IntentCategory.SOLUTIONS: "enterprise industry solutions ecommerce os pharma os real estate os education os smart cities os enterprise ai os",
    IntentCategory.SERVICES: "consulting services data engineering enterprise agentic ai strategy advisory martech 360",
    IntentCategory.INDUSTRIES: "healthcare medical pharma retail ecommerce education real estate verticals",
    IntentCategory.LEADERSHIP: "ceo cto coo founder leadership executive team management leaders",
    IntentCategory.CAREERS: "careers job openings hiring employment internship join team",
    IntentCategory.CONTACT: "contact us phone email reach sales inquiry talk to us",
    IntentCategory.LOCATION: "office location address headquarters hyderabad madhapur location",
    IntentCategory.PRICING: "pricing cost subscription price quotes plan charges",
    IntentCategory.TECHNOLOGY: "technology tech stack architecture framework development infrastructure",
    IntentCategory.AI_MODELS: "artificial intelligence llm rag graphrag generative ai machine learning models",
    IntentCategory.PARTNERSHIPS: "partners partner program strategic alliances collaboration",
    IntentCategory.CASE_STUDIES: "case studies client success stories customer results roi impact",
    IntentCategory.DEMO_REQUESTS: "schedule a demo request product trial book a demo",
    IntentCategory.SUPPORT: "customer support help center tech support assistance troubleshooting",
    IntentCategory.SMALL_TALK: "thank you cool great awesome goodbye chat"
}

@dataclass
class IntentResult:
    primary_intent: str
    confidence: float
    is_deterministic: bool
    secondary_intents: List[str]

class IntentClassifier:
    def __init__(self, embedding_model=None):
        self.embedding_model = embedding_model
        self.anchor_embeddings: Dict[str, np.ndarray] = {}
        if self.embedding_model:
            self._init_anchors()

    def _init_anchors(self):
        try:
            for cat, text in ANCHOR_TEXTS.items():
                emb = self.embedding_model.encode(text, normalize_embeddings=True)
                self.anchor_embeddings[cat] = np.array(emb)
        except Exception as e:
            logger.warning(f"Failed to encode anchor embeddings for IntentClassifier: {e}")

    def _calculate_similarity(self, query: str) -> Dict[str, float]:
        if not self.embedding_model or not self.anchor_embeddings:
            return {}
        try:
            q_emb = np.array(self.embedding_model.encode(query, normalize_embeddings=True))
            sims = {}
            for cat, anchor_emb in self.anchor_embeddings.items():
                sim = float(np.dot(q_emb, anchor_emb))
                sims[cat] = sim
            return sims
        except Exception as e:
            logger.warning(f"Similarity calculation failed: {e}")
            return {}

    def classify(self, query: str) -> IntentResult:
        q_lower = query.lower().strip()
        matched_intents: List[str] = []

        # 1. Regex rule checking
        for category, patterns in INTENT_RULES.items():
            for p in patterns:
                if re.search(p, q_lower):
                    if category not in matched_intents:
                        matched_intents.append(category)
                    break

        if matched_intents:
            primary = matched_intents[0]
            is_det = primary in [
                IntentCategory.GREETING, IntentCategory.SMALL_TALK,
                IntentCategory.LOCATION, IntentCategory.CONTACT, IntentCategory.LEADERSHIP
            ]
            return IntentResult(
                primary_intent=primary,
                confidence=1.0 if is_det else 0.92,
                is_deterministic=is_det,
                secondary_intents=matched_intents[1:]
            )

        # 2. Semantic Embedding Cosine Similarity (if available)
        sims = self._calculate_similarity(query)
        if sims:
            sorted_cats = sorted(sims.items(), key=lambda x: x[1], reverse=True)
            top_cat, top_sim = sorted_cats[0]
            if top_sim >= 0.55:
                sec = [cat for cat, sim in sorted_cats[1:3] if sim >= 0.45]
                return IntentResult(
                    primary_intent=top_cat,
                    confidence=round(float(top_sim), 3),
                    is_deterministic=False,
                    secondary_intents=sec
                )

        return IntentResult(
            primary_intent=IntentCategory.COMPANY_OVERVIEW if "citta" in q_lower else IntentCategory.UNKNOWN,
            confidence=0.5,
            is_deterministic=False,
            secondary_intents=[]
        )

_classifier_instance = None

def get_intent_classifier(embedding_model=None) -> IntentClassifier:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = IntentClassifier(embedding_model=embedding_model)
    return _classifier_instance

