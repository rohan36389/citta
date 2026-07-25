import os
import sys
import json
import logging
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = BACKEND_DIR / "evaluation" / "corpus"
CORPUS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("corpus_generator")

CATEGORIES_DISTRIBUTION = {
    "01_products": {"prefix": "PROD", "count": 50},
    "02_solutions": {"prefix": "SOL", "count": 50},
    "03_services": {"prefix": "SERV", "count": 50},
    "04_company": {"prefix": "COMP", "count": 20},
    "05_leadership": {"prefix": "LEAD", "count": 20},
    "06_technologies": {"prefix": "TECH", "count": 20},
    "07_security": {"prefix": "SEC", "count": 20},
    "08_integrations": {"prefix": "INT", "count": 20},
    "09_pricing": {"prefix": "PRIC", "count": 20},
    "10_comparisons": {"prefix": "COMP", "count": 20},
    "11_demo_sales": {"prefix": "DEMO", "count": 20},
    "12_unknown_queries": {"prefix": "UNK", "count": 20},
    "13_memory": {"prefix": "MEM", "count": 30},
    "14_coreference": {"prefix": "CORE", "count": 30},
    "15_clarifications": {"prefix": "CLAR", "count": 20},
    "16_small_talk": {"prefix": "TALK", "count": 20},
    "17_objections": {"prefix": "OBJ", "count": 20},
    "18_competitors": {"prefix": "COMPET", "count": 20},
    "19_recovery": {"prefix": "REC", "count": 20},
    "20_stress_tests": {"prefix": "STRESS", "count": 20}
}

TEMPLATE_DATA = {
    "01_products": [
        ("solution_ecommerce_os", "E-Commerce OS", "SOLUTIONS", ["E-Commerce OS", "retail"], ["Smart Cities"]),
        ("solution_pharma_os", "Pharma OS", "SOLUTIONS", ["Pharma OS", "clinical"], ["E-Commerce OS"]),
        ("solution_smart_cities_os", "Smart Cities OS", "SOLUTIONS", ["Smart Cities OS", "urban"], ["Pharma OS"]),
        ("product_whatsapp_marketing", "WhatsApp Marketing Platform", "PRODUCTS", ["WhatsApp Marketing", "broadcast"], ["Pharma OS"]),
        ("product_influencer_marketing", "Influencer Marketing Platform", "PRODUCTS", ["Influencer Marketing", "creator"], ["Smart Cities"])
    ],
    "09_pricing": [
        ("solution_ecommerce_os", "E-Commerce OS", "PRICING", ["Contact page", "sales team"], ["$10", "₹50,000", "per month"])
    ],
    "12_unknown_queries": [
        ("unknown_agriculture", "Smart Agriculture OS", "UNKNOWN", ["couldn't find", "Contact page"], ["Smart Agriculture OS"])
    ]
}

def generate_scenario_content(cat_key: str, idx: int, prefix: str) -> str:
    """Generates valid multi-turn scenario markdown string with YAML frontmatter."""
    sc_id = f"{prefix}_{idx:03d}"
    cat_short = cat_key.split("_", 1)[1] if "_" in cat_key else cat_key
    
    # Rotate through primary canonical entities
    entities = [
        ("solution_ecommerce_os", "Ecommerce OS"),
        ("solution_pharma_os", "Pharma OS"),
        ("solution_smart_cities_os", "Smart Cities OS"),
        ("product_whatsapp_marketing", "WhatsApp Marketing Platform"),
        ("product_influencer_marketing", "Influencer Marketing Platform")
    ]
    ent_id, ent_name = entities[(idx - 1) % len(entities)]

    if cat_short == "pricing":
        user_q = f"How much does {ent_name} cost for module deployment {idx}?"
        must_inc = ["Contact page", "sales team"]
        must_not_inc = ["$100", "₹50,000", "per month"]
        exp_ent_line = f"      active_entity: {ent_id}"
    elif cat_short == "unknown_queries":
        ent_id = "NONE"
        user_q = f"Do you provide Quantum Agriculture Solution {idx}?"
        must_inc = ["couldn't find", "Contact page"]
        must_not_inc = [f"Quantum Agriculture Solution {idx}"]
        exp_ent_line = "      active_entity: null"
    elif cat_short == "coreference":
        user_q = f"Tell me about {ent_name}."
        must_inc = [ent_name.split()[0]]
        must_not_inc = ["Agriculture"]
        exp_ent_line = f"      active_entity: {ent_id}"
    elif cat_short == "recovery":
        user_q = f"Tell me about {ent_name}."
        must_inc = [ent_name.split()[0]]
        must_not_inc = ["Agriculture"]
        exp_ent_line = f"      active_entity: {ent_id}"
    else:
        user_q = f"Tell me about {ent_name} capabilities for {cat_short} scenario {idx}."
        must_inc = ["CittaAI", ent_name.split()[0]]
        must_not_inc = ["Smart Agriculture"]
        exp_ent_line = f"      active_entity: {ent_id}"

    content = f"""---
id: {sc_id}
category: {cat_short}
difficulty: medium
scenario_name: {cat_short.title()} Scenario {idx}
expected_outcomes:
  initial_entity: {ent_id}
  pricing_speculation_allowed: false
  hallucination_allowed: false
  auto_redirect_allowed: false

turns:
  - turn: 1
    user: "{user_q}"
    expected_state:
{exp_ent_line}
    expected_response:
      must_include: {json.dumps(must_inc)}
      must_not_include: {json.dumps(must_not_inc)}
---

Customer:
{user_q}

Assistant:
Thank you for inquiring about {ent_name if ent_id != 'NONE' else 'CittaAI'}. CittaAI provides verified enterprise platforms tailored for digital operations and intelligence.
"""
    return content

def generate_full_corpus():
    """Generates scenario files across all 20 categories."""
    total_generated = 0
    cat_counts = {}

    for cat_dir, meta in CATEGORIES_DISTRIBUTION.items():
        cat_path = CORPUS_DIR / cat_dir
        cat_path.mkdir(parents=True, exist_ok=True)
        prefix = meta["prefix"]
        target_count = meta["count"]
        
        gen_count = 0
        for i in range(1, target_count + 1):
            file_name = f"{prefix}_{i:03d}_scenario.md"
            file_path = cat_path / file_name
            # Preserve existing handcrafted scenarios if present
            if not file_path.exists():
                text = generate_scenario_content(cat_dir, i, prefix)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
            gen_count += 1
            total_generated += 1
            
        cat_counts[cat_dir] = gen_count

    # Update manifest.json
    manifest = {
        "version": "1.0",
        "corpus_name": "CittaAI Golden Enterprise Conversation Corpus",
        "description": "Multi-turn enterprise scenario dataset across 20 categories.",
        "total_categories": len(CATEGORIES_DISTRIBUTION),
        "total_scenarios": total_generated,
        "category_distribution": cat_counts
    }
    with open(CORPUS_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {total_generated} scenarios across {len(cat_counts)} categories.")

if __name__ == "__main__":
    generate_full_corpus()
