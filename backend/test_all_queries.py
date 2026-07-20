import httpx
import json
import sys

queries = [
    # Company
    "Tell me about CittaAI.",
    "What is CittaAI's mission?",
    "What is CittaAI's vision?",
    "When was CittaAI founded?",
    "Where is CittaAI located?",
    # Leadership
    "Who is the CEO?",
    "Show me the leadership team.",
    "Tell me about Akhil Reddy.",
    "Who leads Technology?",
    "Who is the COO?",
    # Products
    "Tell me about the WhatsApp Marketing Platform.",
    "Explain the Influencer Marketing Platform.",
    "What products does CittaAI offer?",
    # Services
    "Tell me about AI Strategy & Advisory.",
    "Explain Data Engineering services.",
    "What is Martech 360?",
    "Tell me about Enterprise & Agentic AI.",
    # Solutions
    "Explain Pharma OS.",
    "How does Education OS work?",
    "Tell me about Enterprise AI OS.",
    "What is Smart Cities OS?",
    "Explain Real Estate OS.",
    # Case Studies
    "Show me all case studies.",
    "Explain the Jewellery Brand case study.",
    "Tell me about the FMCG case study.",
    "Explain the B2B Spices Export case study.",
    # Awards
    "What awards has CittaAI won?",
    "Tell me about the HYBIZ award.",
    "Explain the AP MSME Digital Empowerment Challenge.",
    # Contact
    "How can I contact CittaAI?",
    "What is CittaAI's email?",
    "Where is your office?",
    # Fallback / Negative
    "Tell me about RAG Solutions.",
    "Tell me about Martech.",
    "Who are CittaAI's clients?",
    "Explain Quantum OS.",
    "Tell me about Blockchain services."
]

results = []
for q in queries:
    try:
        r = httpx.post("http://127.0.0.1:8000/api/chat", json={"session_id": "reg_test", "message": q}, timeout=15)
        lines = [line[6:] for line in r.text.splitlines() if line.startswith("data:")]
        text_data = ""
        meta_data = {}
        for line in lines:
            try:
                d = json.loads(line)
                if "text" in d:
                    text_data += d["text"]
                if d.get("done"):
                    meta_data = d
            except:
                pass
        metrics = meta_data.get("metrics", {})
        results.append({
            "query": q,
            "source": meta_data.get("source"),
            "redirect": meta_data.get("redirect"),
            "resolved_registry": metrics.get("resolved_registry"),
            "resolved_entity": metrics.get("resolved_entity"),
            "preview": text_data[:100].replace("\n", " ").encode("ascii", "ignore").decode("ascii")
        })
    except Exception as e:
        results.append({
            "query": q,
            "error": str(e)
        })

print("=" * 80)
print(f"AUTOMATED REGISTRY VERIFICATION SUITE ({len(results)} QUERIES)")
print("=" * 80)
for idx, res in enumerate(results, 1):
    reg = res.get('resolved_registry') or 'N/A'
    ent = res.get('resolved_entity') or 'NONE'
    redir = res.get('redirect') or 'None'
    src = res.get('source') or 'Unknown'
    prev = res.get('preview', '')
    print(f"{idx:02d}. Query: '{res['query']}'")
    print(f"    -> Registry: {reg} | Entity: {ent} | Redirect: {redir} | Source: {src}")
    print(f"    -> Preview: {prev}...")
    print("-" * 80)

with open("test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
