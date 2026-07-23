# Conversation Intelligence Layer Configuration

# Pre-sales conversation stages
CONVERSATION_STAGES = [
    "Greeting",
    "Discovery",
    "Education",
    "Solution Exploration",
    "Technical Validation",
    "Objection Handling",
    "Demo Scheduling",
    "Closing"
]

# Transition rules matrix (allowed next stages from current stage)
STAGE_TRANSITIONS = {
    "Greeting": ["Discovery", "Education", "Solution Exploration"],
    "Discovery": ["Education", "Solution Exploration", "Technical Validation", "Objection Handling"],
    "Education": ["Solution Exploration", "Technical Validation", "Objection Handling", "Demo Scheduling"],
    "Solution Exploration": ["Technical Validation", "Objection Handling", "Demo Scheduling"],
    "Technical Validation": ["Objection Handling", "Demo Scheduling", "Closing"],
    "Objection Handling": ["Solution Exploration", "Technical Validation", "Demo Scheduling", "Closing"],
    "Demo Scheduling": ["Closing"],
    "Closing": ["Greeting", "Discovery"]
}

# Lead qualification scoring weights
LEAD_QUALIFICATION_WEIGHTS = {
    "industry": 0.15,
    "company_size": 0.20,
    "urgency": 0.15,
    "timeline": 0.25,
    "budget": 0.25
}

# Objection responses mappings (default deterministic hooks/grounding triggers)
OBJECTION_TEMPLATES = {
    "pricing": "We tailor our solutions to your scale and ROI metrics. Let's schedule a brief call with our sales engineering team to model a customized commercial package.",
    "complexity": "CittaAI modules are designed for zero-friction deployment with unified data ingestion and out-of-the-box system integration protocols.",
    "timeline": "Our pre-built domain templates and platform tools enable staging setup in weeks, not months."
}

# Safety parameters
MAX_HISTORY_LEN = 10
GROUNDEDNESS_THRESHOLD = 0.85
PERSONA_STYLE = "CittaAI Pre-Sales Expert (Professional, Consultation-driven, Proactive Lead Qualification)"
