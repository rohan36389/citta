import os
import json
import sqlite3
from datetime import date
from pathlib import Path
from static_data import get_raw_content

# Setup paths
BACKEND_DIR = Path(__file__).resolve().parent
TAXONOMY_DIR = BACKEND_DIR / "knowledge" / "taxonomy"
TAXONOMY_DIR.mkdir(parents=True, exist_ok=True)

def get_chunk_counts():
    """Retrieve chunk count per route dynamically from the vector database."""
    counts = {}
    db_path = BACKEND_DIR / "vector_store.db"
    if not db_path.exists():
        return counts
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT metadata FROM chunks")
        for row in cursor.fetchall():
            try:
                meta = json.loads(row[0])
                page = meta.get("page") or meta.get("url")
                if page:
                    counts[page] = counts.get(page, 0) + 1
            except Exception:
                pass
        conn.close()
    except Exception as e:
        print(f"Error querying vector DB: {e}")
    return counts

def generate():
    raw_content = get_raw_content()
    if not raw_content:
        print("Failed to load content.js")
        return
        
    chunk_counts = get_chunk_counts()
    
    # 1. Company Taxonomy
    brand = raw_content.get("BRAND", {})
    company_data = {
        "name": brand.get("name", "CittaAI"),
        "description": brand.get("tagline", "") or brand.get("positioning", "Enterprise AI company.")
    }
    with open(TAXONOMY_DIR / "company.json", "w", encoding="utf-8") as f:
        json.dump(company_data, f, indent=2)
        
    # 2. Navigation Taxonomy
    nav = raw_content.get("NAV", {})
    nav_routes = []
    for item in nav.get("primary", []):
        if "to" in item:
            nav_routes.append({"name": item["label"], "route": item["to"]})
        if "children" in item:
            for child in item["children"]:
                # skip listing categorized pages in generic navigation
                if "to" in child and not any(p in child["to"] for p in ["/products/", "/solutions/", "/services/"]):
                    nav_routes.append({"name": child["label"], "route": child["to"]})
    
    # Add other hardcoded items if missing
    if not any(n["route"] == "/contact" for n in nav_routes):
        nav_routes.append({"name": "Contact", "route": "/contact"})
    
    with open(TAXONOMY_DIR / "navigation.json", "w", encoding="utf-8") as f:
        json.dump(nav_routes, f, indent=2)

    # 3. Products Taxonomy
    products = []
    product_configs = [
        ("whatsapp-marketing", "whatsapp_marketing", ["influencer_marketing"], ["ai_powered_marketing"], ["ecommerce_os"]),
        ("influencer-marketing", "influencer_marketing", ["whatsapp_marketing"], ["ai_powered_marketing"], ["ecommerce_os"])
    ]
    
    for slug, p_id, rel_p, rel_serv, rel_sol in product_configs:
        config = raw_content.get("PAGE_CONFIGS", {}).get(slug, {})
        
        route = f"/products/{slug}"
        c_count = chunk_counts.get(route, 0)
        
        p_name = config.get("name", slug.replace("-", " ").title())
        keywords = [w.strip(",.()").lower() for w in p_name.split() if len(w) > 2]
        for cap in config.get("capabilities", []):
            if cap.get("t"):
                keywords.extend([w.strip(",.()").lower() for w in cap.get("t").split() if len(w) > 2])
        keywords = sorted(list(set(keywords)))

        p_data = {
            "id": p_id,
            "name": p_name,
            "category": "product",
            "route": route,
            "summary": config.get("hero", "Enterprise product platform."),
            "description": config.get("subtitle", "AI-powered enterprise business product."),
            "keywords": keywords,
            "related_products": rel_p,
            "related_services": rel_serv,
            "related_solutions": rel_sol,
            "capabilities": [cap.get("t") for cap in config.get("capabilities", []) if cap.get("t")],
            "indexed": c_count > 0,
            "chunk_count": c_count,
            "last_updated": str(date.today())
        }
        products.append(p_data)
        
    with open(TAXONOMY_DIR / "products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)

    # 4. Solutions Taxonomy
    solutions = []
    sol_configs = [
        ("ecommerce-os", "ecommerce_os", ["whatsapp_marketing", "influencer_marketing"], ["ai_powered_marketing"], []),
        ("real-estate-os", "real_estate_os", [], ["data_engineering"], []),
        ("pharma-os", "pharma_os", [], ["data_engineering"], []),
        ("smart-cities-os", "smart_cities_os", [], ["data_engineering"], []),
        ("education-os", "education_os", [], ["data_engineering"], []),
        ("enterprise-ai-os", "enterprise_ai_os", [], ["enterprise_agentic_ai"], [])
    ]
    
    for slug, s_id, rel_p, rel_serv, rel_sol in sol_configs:
        config = raw_content.get("PAGE_CONFIGS", {}).get(slug, {})
        route = f"/solutions/{slug}"
        c_count = chunk_counts.get(route, 0)
        
        s_name = config.get("name", slug.replace("-", " ").title())
        keywords = [w.strip(",.()").lower() for w in s_name.split() if len(w) > 2]
        for cap in config.get("capabilities", []):
            if cap.get("t"):
                keywords.extend([w.strip(",.()").lower() for w in cap.get("t").split() if len(w) > 2])
        keywords = sorted(list(set(keywords)))

        s_data = {
            "id": s_id,
            "name": s_name,
            "category": "solution",
            "route": route,
            "summary": config.get("hero", "Enterprise solution platform."),
            "description": config.get("subtitle", "AI-powered industry vertical solution."),
            "keywords": keywords,
            "related_products": rel_p,
            "related_services": rel_serv,
            "related_solutions": rel_sol,
            "capabilities": [cap.get("t") for cap in config.get("capabilities", []) if cap.get("t")],
            "indexed": c_count > 0,
            "chunk_count": c_count,
            "last_updated": str(date.today())
        }
        solutions.append(s_data)
        
    with open(TAXONOMY_DIR / "solutions.json", "w", encoding="utf-8") as f:
        json.dump(solutions, f, indent=2)

    # 5. Services Taxonomy
    services = []
    serv_configs = [
        ("data-engineering", "data_engineering", "Data Engineering", ["Real-time data pipelines", "Cloud data warehouse", "Data lake architecture", "Master data management"], [], ["enterprise_agentic_ai"], ["enterprise_ai_os"]),
        ("enterprise-ai", "enterprise_agentic_ai", "Enterprise & Agentic AI", ["Custom LLM fine-tuning", "Multi-agent systems", "RAG solutions", "Conversational AI"], [], ["data_engineering", "ai_strategy"], ["enterprise_ai_os"]),
        ("ai-strategy", "ai_strategy", "AI Strategy & Advisory", ["AI readiness assessment", "Strategic roadmap", "Use case prioritization", "AI governance"], [], ["enterprise_agentic_ai"], []),
        ("martech-360", "ai_powered_marketing", "AI-Powered Marketing", ["Branding & Strategy", "Social Media Marketing", "Content & Design", "SEO", "PPC Advertising", "E-commerce Growth", "WhatsApp Marketing Automation"], ["whatsapp_marketing", "influencer_marketing"], [], ["ecommerce_os"])
    ]
    
    for slug, serv_id, display_name, caps, rel_p, rel_serv, rel_sol in serv_configs:
        route = f"/services/{slug}"
        c_count = chunk_counts.get(route, 0)
        
        homepage_services = raw_content.get("HOMEPAGE", {}).get("services", {}).get("items", [])
        desc = "AI-powered professional service."
        for item in homepage_services:
            if item.get("to") == route:
                desc = item.get("desc", desc)
                
        serv_data = {
            "id": serv_id,
            "name": display_name,
            "category": "service",
            "route": route,
            "summary": f"Professional CittaAI service for {display_name}.",
            "description": desc,
            "keywords": [w.strip(",.()").lower() for w in display_name.split() if len(w) > 2],
            "related_products": rel_p,
            "related_services": rel_serv,
            "related_solutions": rel_sol,
            "capabilities": caps,
            "indexed": c_count > 0,
            "chunk_count": c_count,
            "last_updated": str(date.today())
        }
        services.append(serv_data)
        
    with open(TAXONOMY_DIR / "services.json", "w", encoding="utf-8") as f:
        json.dump(services, f, indent=2)
        
    print(f"Taxonomy files written successfully in {TAXONOMY_DIR}")

if __name__ == "__main__":
    generate()
