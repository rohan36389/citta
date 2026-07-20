import re
from typing import Optional, Dict, Any

GREETING_RESPONSES = {
    "hi": "Hello 👋\nWelcome to CittaAI! How can I help you explore our enterprise solutions today?",
    "hello": "Hello 👋\nWelcome to CittaAI! How can I help you explore our enterprise solutions today?",
    "hey": "Hello 👋\nWelcome to CittaAI! How can I help you explore our enterprise solutions today?",
    "good morning": "Good morning ☀️\nWelcome to CittaAI! How can I assist you with our products and services today?",
    "good afternoon": "Good afternoon 🌤️\nWelcome to CittaAI! How can I assist you with our products and services today?",
    "good evening": "Good evening 🌆\nWelcome to CittaAI! How can I assist you with our products and services today?",
    "how are you": "I am doing well, thank you for asking! I'm ready to help you explore CittaAI's AI systems and capabilities. What's on your mind?",
    "thanks": "You're very welcome! Let me know if there's anything else I can help you with.",
    "thank you": "You're very welcome! Let me know if there's anything else I can help you with.",
    "bye": "Goodbye! Have a great day ahead, and feel free to reach out to CittaAI anytime.",
    "goodbye": "Goodbye! Have a great day ahead, and feel free to reach out to CittaAI anytime."
}

def detect_greeting(query: str) -> Optional[Dict[str, Any]]:
    """
    Checks if a query matches standard greetings, bypassing resolvers and RAG.
    """
    q_clean = query.strip().lower()
    # Strip basic punctuation
    q_clean = re.sub(r"[^\w\s]", "", q_clean).strip()
    
    if q_clean in GREETING_RESPONSES:
        return {
            "response": GREETING_RESPONSES[q_clean],
            "source": "Greeting Detector",
            "verified": True,
            "confidence": 1.0,
            "suggestions": ["Show Products", "Show Services", "Show Solutions"]
        }
        
    for trigger, resp in GREETING_RESPONSES.items():
        # Match trigger as whole sentence
        if re.match(rf"^\s*{re.escape(trigger)}\s*$", q_clean):
            return {
                "response": resp,
                "source": "Greeting Detector",
                "verified": True,
                "confidence": 1.0,
                "suggestions": ["Show Products", "Show Services", "Show Solutions"]
            }
            
    return None
