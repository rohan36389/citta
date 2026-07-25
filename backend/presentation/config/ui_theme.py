"""
Configuration mapping for the Presentation Layer.
Defines icons, standard section titles, and action button routes.
"""

UI_THEME = {
    "ICONS": {
        "solution": "⚙️",
        "product": "⚙️",
        "service": "🚀",
        "technology": "🧠",
        "company": "🏢",
        "case_study": "📈",
        "recognition": "🏆",
        "contact": "📞",
        "location": "🏢",
        "comparison": "⚖️",
        "recommendation": "🎯",
        "default": "💡"
    },
    "SECTION_TITLES": {
        "overview": "Overview",
        "best_for": "Best For",
        "recommended_for": "Recommended For",
        "capabilities": "Capabilities",
        "features": "Key Features",
        "modules": "Core Modules",
        "services_included": "Services Included",
        "benefits": "Benefits",
        "advantages": "Advantages",
        "technology_stack": "Technology Stack",
        "integrations": "Integrations",
        "industries": "Industries",
        "deployment": "Deployment",
        "used_in": "Used In",
        "next_actions": "Next Actions",
        "how_it_works": "How It Works"
    },
    "BUTTONS": {
        "request_demo": {"label": "Request Demo", "route": "/contact"},
        "contact_sales": {"label": "Contact Sales", "route": "/contact"},
        "talk_to_expert": {"label": "Talk to Expert", "route": "/contact"},
        "how_it_works": {"label": "How it Works", "route": "#how-it-works"},
        "architecture": {"label": "Architecture", "route": "#architecture"},
        "pricing": {"label": "Pricing", "route": "/pricing"},
        "our_process": {"label": "Our Process", "route": "/services/ai-strategy"},
        "explore_products": {"label": "Explore Products", "route": "/products"},
        "contact_us": {"label": "Contact Us", "route": "/contact"},
        "ask_another": {"label": "Ask Another Question", "route": "#chat"}
    }
}
