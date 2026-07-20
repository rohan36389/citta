import logging
from typing import Dict, Any, List, Optional
from taxonomy import (
    get_products, get_solutions, get_services, get_navigation,
    get_product, get_solution, get_service, find_route
)

logger = logging.getLogger(__name__)

def list_products() -> Dict[str, Any]:
    """Return catalog list of all products."""
    products = get_products()
    lines = ["CittaAI currently offers two flagship products:", ""]
    for p in products:
        lines.append(f"• {p['name']}")
    lines.append("")
    lines.append("I can explain either product in detail.")
    
    return {
        "type": "products_list",
        "text": "\n".join(lines),
        "redirect": "/products/whatsapp-marketing",
        "section": "hero",
        "highlight": True,
        "suggested_questions": [
            "What is the WhatsApp Marketing Platform?",
            "Tell me about the Influencer Marketing Platform."
        ]
    }

def list_solutions() -> Dict[str, Any]:
    """Return catalog list of all industry solutions."""
    solutions = get_solutions()
    lines = ["CittaAI provides the following AI industry solutions:", ""]
    for s in solutions:
        lines.append(f"• {s['name']}")
        
    return {
        "type": "solutions_list",
        "text": "\n".join(lines),
        "redirect": "/solutions/ecommerce-os",
        "section": "hero",
        "highlight": True,
        "suggested_questions": [
            "Tell me about the E-Commerce OS.",
            "What is the Enterprise AI OS?",
            "How does Pharma & Healthcare OS work?"
        ]
    }

def list_services() -> Dict[str, Any]:
    """Return catalog list of services and their capabilities."""
    services = get_services()
    lines = ["CittaAI offers four professional service areas:", ""]
    for serv in services:
        caps_str = ", ".join(serv["capabilities"])
        lines.append(f"• **{serv['name']}**")
        lines.append(f"  Capabilities: {caps_str}")
        lines.append("")
        
    return {
        "type": "services_list",
        "text": "\n".join(lines).strip(),
        "redirect": "/services",
        "section": "hero",
        "highlight": True,
        "suggested_questions": [
            "What does Data Engineering include?",
            "What does Enterprise & Agentic AI include?",
            "Tell me about AI Strategy & Advisory."
        ]
    }

def service_detail(service_id: str) -> Dict[str, Any]:
    """Return specific service capabilities directly from taxonomy without RAG/LLM."""
    serv = get_service(service_id)
    if not serv:
        return {}
        
    lines = [f"**{serv['name']}** capabilities include:", ""]
    for cap in serv["capabilities"]:
        lines.append(f"• {cap}")
        
    return {
        "type": "service_detail",
        "text": "\n".join(lines),
        "redirect": serv["route"],
        "section": "hero",
        "highlight": True,
        "suggested_questions": build_suggestions(serv)
    }

def build_suggestions(item: Dict[str, Any]) -> List[str]:
    """Generate smart contextually aligned suggestions from related taxonomy items."""
    category = item.get("category", "").lower()
    item_id = item.get("id")
    
    suggestions = []
    if category == "product":
        for p in get_products():
            if p["id"] != item_id:
                suggestions.append(f"Tell me about the {p['name']}.")
        # Fallback suggestion
        suggestions.append("What solutions do you provide?")
    elif category == "solution":
        for s in get_solutions():
            if s["id"] != item_id and len(suggestions) < 2:
                suggestions.append(f"Explain {s['name']}.")
        suggestions.append("What products do you offer?")
    elif category == "service":
        for s in get_services():
            if s["id"] != item_id and len(suggestions) < 2:
                suggestions.append(f"What does {s['name']} include?")
        suggestions.append("What solutions do you provide?")
        
    return suggestions[:3]

def generate_catalog_response(tool_handle: str) -> Dict[str, Any]:
    """Helper method to routing catalog tools directly to responses."""
    if tool_handle == "list_products":
        return list_products()
    elif tool_handle == "list_solutions":
        return list_solutions()
    elif tool_handle == "list_services":
        return list_services()
    elif tool_handle.startswith("service_detail:"):
        service_id = tool_handle.split(":", 1)[1]
        return service_detail(service_id)
    return {}
