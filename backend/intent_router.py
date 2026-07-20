import re
from typing import Dict, Any, List

# Define intent categories and their keyword regexes
INTENT_RULES = {
    "LIST_PRODUCTS": [
        r"\bwhat\s+(?:products|platforms)\s+(?:does\s+cittaai\s+offer|do\s+you\s+offer|does\s+cittaai\s+provide|do\s+you\s+provide|are\s+there|have)\b",
        r"\b(?:list|show|what\s+are)\s+(?:your\s+)?products?\b",
        r"\bwhat\s+products\s+does\s+cittaai\s+have\b",
        r"\bwhat\s+are\s+your\s+products\b"
    ],
    "LIST_SOLUTIONS": [
        r"\bwhat\s+(?:solutions|os\s+platforms|industry\s+solutions)\s+(?:does\s+cittaai\s+offer|do\s+you\s+offer|does\s+cittaai\s+provide|do\s+you\s+provide|are\s+there|have)\b",
        r"\b(?:list|show|what\s+are)\s+(?:your\s+)?solutions\b",
        r"\bwhat\s+os\s+platforms\s+do\s+you\s+have\b",
        r"\bwhat\s+industry\s+solutions\s+do\s+you\s+offer\b"
    ],
    "LIST_SERVICES": [
        r"\bwhat\s+services\s+(?:does\s+cittaai\s+offer|do\s+you\s+offer|does\s+cittaai\s+provide|do\s+you\s+provide|are\s+there|have)\b",
        r"\b(?:list|show|what\s+are)\s+(?:your\s+)?services\b",
        r"\bwhat\s+services\s+do\s+you\s+provide\b"
    ],
    "SERVICE_DETAIL": [
        r"\bdata\s+engineering\s+(?:include|contain|offer|cover|mean|capabilities)\b",
        r"\benterprise\s+(?:&\s+)?agentic\s+ai\s+(?:include|contain|offer|cover|mean|capabilities)\b",
        r"\benterprise\s+ai\s+(?:include|contain|offer|cover|mean|capabilities)\b",
        r"\bai\s+strategy\s+(?:&\s+)?advisory\s+(?:include|contain|offer|cover|mean|capabilities)\b",
        r"\bai\s+strategy\s+(?:include|contain|offer|cover|mean|capabilities)\b",
        r"\bai\s+powered\s+marketing\s+(?:include|contain|offer|cover|mean|capabilities)\b",
        r"\bmartech\s+360\s+(?:include|contain|offer|cover|mean|capabilities)\b"
    ],
    "PRODUCT_DETAIL": [
        r"\bwhatsapp\s+marketing\s+platform\b",
        r"\bwhatsapp\s+marketing\b",
        r"\bwhatsapp\s+platform\b",
        r"\binfluencer\s+marketing\s+platform\b",
        r"\binfluencer\s+marketing\b"
    ],
    "SOLUTION_DETAIL": [
        r"\be-?commerce\s+os\b",
        r"\breal\s+estate\s+os\b",
        r"\bpharma\s+(?:&\s+)?healthcare\s+os\b",
        r"\bpharma\s+os\b",
        r"\bsmart\s+cities\s+os\b",
        r"\beducation\s+os\b",
        r"\blms\s+os\b",
        r"\benterprise\s+ai\s+os\b"
    ],
    "SERVICE_PRICING": [
        r"\b(?:price|pricing|cost|charges|rate|rates|quote|quotation|fee|fees|payment|charge)\b"
    ],
    "LOCATION": [
        r"\b(?:address|location|where\s+are\s+you|office|headquarters|hq|maps|map|hyderabad|located|place)\b"
    ],
    "BUSINESS HOURS": [
        r"\b(?:hours|business\s+hours|timing|timings|open|close|mon|fri|weekday|working\s+hours|days)\b"
    ],
    "SOCIAL LINKS": [
        r"\b(?:social|linkedin|instagram|twitter|facebook|youtube|social\s+links|x\.com)\b"
    ],
    "CONTACT": [
        r"\b(?:contact|email|phone|number|reach|support|say\s+hello|hello|get\s+in\s+touch|write\s+to|mail|talk\s+to|mobile)\b"
    ],
    "CAREERS": [
        r"\b(?:careers|job|jobs|hiring|work\s+at|join\s+us|career|apply|opening|openings)\b"
    ],
    "RECOGNITION": [
        r"\b(?:recognition|award|awards|msme|hybiz|excellence|victory|won|won\b|achievement|achievements|certifications|iso|startup\s+india)\b"
    ],
    "CASE STUDIES": [
        r"\b(?:case\s+studies|case\s+study|jewellery|fmcg|spices|results|roi|metric|metrics|success\s+story|success\s+stories)\b"
    ],
    "LEGAL": [
        r"\b(?:privacy|terms|condition|legal|policy|security|compliance|gdpr|soc2|hipaa)\b"
    ],
    "CONSULTATION": [
        r"\b(?:consultation|book|schedule|strategy\s+call|meeting|call|appointment|talk\s+to\s+expert)\b"
    ],
    "COMPARISON": [
        r"\b(?:compare|vs|versus|difference\s+between|alternative|differ|comparison)\b"
    ],
    "SERVICES": [
        r"\b(?:services|data\s+engineering|enterprise\s+ai|ai\s+strategy|martech\s+360|consulting|service)\b"
    ],
    "PRODUCTS": [
        r"\b(?:products|marktech\s+suite|whatsapp|whatsapp\s+marketing|influencer\s+marketing|agentic\s+ai|lms|education\s+os|pharma\s+os|smart\s+cities\s+os|product)\b"
    ],
    "ABOUT": [
        r"\b(?:about|who\s+are\s+you|what\s+is\s+cittaai|cittaai\s+details|tell\s+me\s+about|company\s+name|founded|history|vision|mission|values|philosophy|story|founder|leadership|ceo|cto|co-founder|team|leaders|executive|executives)\b"
    ],
    "GENERAL AI": [
        r"\b(?:agentic\s+ai|generative\s+ai|llm|rag|rag\s+routing|embedding|qwen|llama|machine\s+learning|deep\s+learning)\b"
    ]
}

def normalize_query(query: str) -> str:
    """Normalize the user query to build consistent cache keys and routing input."""
    q = query.lower().strip()
    # Remove punctuation
    q = re.sub(r"[^\w\s\-\/\.]", "", q)
    # Remove common filler words
    fillers = {"what", "is", "are", "your", "the", "a", "an", "how", "can", "i", "you", "tell", "me", "about", "please", "do", "we", "get", "in"}
    words = [w for w in q.split() if w not in fillers]
    # Sort to avoid word ordering differences affecting cache key
    words.sort()
    return " ".join(words)

def classify_intent(query: str) -> str:
    """Classify the user query into an intent using a rule-based engine in < 1ms."""
    query_clean = query.lower().strip()
    
    for intent, patterns in INTENT_RULES.items():
        for pattern in patterns:
            if re.search(pattern, query_clean):
                return intent
                
    return "UNKNOWN"

def detect_tool_call(query: str, intent: str) -> str:
    """Detect if the query qualifies for a direct tool calling response (e.g. lists)."""
    query_clean = query.lower().strip()
    
    # Core catalog / listing mappings
    if intent == "LIST_PRODUCTS":
        return "list_products"
    if intent == "LIST_SOLUTIONS":
        return "list_solutions"
    if intent == "LIST_SERVICES":
        return "list_services"
        
    if intent == "SERVICE_DETAIL":
        if "data engineering" in query_clean:
            return "service_detail:data_engineering"
        elif "agentic" in query_clean or "enterprise" in query_clean:
            return "service_detail:enterprise_agentic_ai"
        elif "strategy" in query_clean or "advisory" in query_clean:
            return "service_detail:ai_strategy"
        elif "marketing" in query_clean or "martech" in query_clean:
            return "service_detail:ai_powered_marketing"

    # Check for listing / searching service requests
    if intent == "SERVICES":
        if any(w in query_clean for w in ["list", "show all", "provide all"]) or \
           any(phrase in query_clean for phrase in ["what services", "which services", "what are the services", "what service", "what do you offer"]):
            return "list_services"
        
    # Check for listing / searching product requests
    if intent == "PRODUCTS":
        if any(w in query_clean for w in ["list", "show all", "platforms"]) or \
           any(phrase in query_clean for phrase in ["what products", "which products", "what are the products", "what product", "what do you offer"]):
            return "list_products"
        
    # Check for listing case studies
    if intent == "CASE STUDIES":
        if any(w in query_clean for w in ["list", "show all", "examples"]) or \
           any(phrase in query_clean for phrase in ["what case studies", "which case studies", "what are the case studies", "what success stories"]):
            return "list_case_studies"
        
    # Check for listing awards / recognition
    if intent == "RECOGNITION":
        if any(w in query_clean for w in ["list", "show all", "won", "get", "got"]) or \
           any(phrase in query_clean for phrase in ["what awards", "which awards", "what recognition", "what achievements"]):
            return "list_recognition"
        
    return ""
