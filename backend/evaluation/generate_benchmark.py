import sqlite3
import json
import os
import sys
from datetime import datetime

# Add parent directory to sys.path so we can import helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from error_classifier import classify_failures
from cost_analyzer import analyze_costs

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "telemetry.db"))

def calculate_percentiles(data):
    if not data:
        return {"Avg": 0, "P50": 0, "P95": 0, "P99": 0, "Max": 0}
    data = sorted(data)
    n = len(data)
    
    def get_percentile(p):
        k = (n - 1) * p
        f = int(k)
        c = int(k) + 1 if int(k) + 1 < n else f
        if f == c:
            return data[f]
        d0 = data[f] * (c - k)
        d1 = data[c] * (k - f)
        return d0 + d1

    return {
        "Avg": round(sum(data) / n, 2),
        "P50": round(get_percentile(0.50), 2),
        "P95": round(get_percentile(0.95), 2),
        "P99": round(get_percentile(0.99), 2),
        "Max": round(data[-1], 2)
    }

def main():
    if not os.path.exists(DB_PATH):
        print(f"Telemetry database not found at {DB_PATH}. Running staging benchmark generation aborted.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Latencies
    cursor.execute("SELECT context_json FROM requests_telemetry")
    rows = cursor.fetchall()
    
    latencies = []
    deterministic_routing = 0
    llm_routing = 0
    clarification_rate = 0
    coverage_arr = []
    
    for (context_json,) in rows:
        try:
            ctx = json.loads(context_json)
        except Exception:
            continue
            
        history = ctx.get("history", [])
        if history:
            tot_dur = sum(h.get("duration_ms", 0) for h in history)
            latencies.append(tot_dur)
            
        und = ctx.get("understanding", {})
        if und:
            if und.get("resolved_deterministically", False):
                deterministic_routing += 1
            else:
                llm_routing += 1
                
        # Check if query fell back to Clarify
        if any(h.get("state") == "CLARIFY" for h in history):
            clarification_rate += 1
            
        ret_res = ctx.get("retrieval_result", {})
        if ret_res:
            coverage_arr.append(ret_res.get("retrieval_coverage", 0.0))

    latency_percentiles = calculate_percentiles(latencies)

    # Human Evaluations
    cursor.execute("""
    SELECT AVG(correctness), AVG(completeness), AVG(groundedness), 
           AVG(hallucination), AVG(citation_quality), AVG(user_satisfaction), COUNT(*)
    FROM human_evaluations
    """)
    eval_row = cursor.fetchone()
    
    avg_correctness = eval_row[0] or 0.0
    avg_completeness = eval_row[1] or 0.0
    avg_groundedness = eval_row[2] or 0.0
    hallucination_rate = (eval_row[3] or 0.0) * 100 # stored as 0 or 1
    avg_citation = eval_row[4] or 0.0
    avg_satisfaction = eval_row[5] or 0.0
    total_evals = eval_row[6] or 0

    conn.close()

    # Heuristics/Reports from other modules
    errors = classify_failures()
    costs = analyze_costs()

    # Generate Markdown Report
    md = []
    md.append("# Phase 5: Production Pilot Baseline Benchmark\n")
    md.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
    
    md.append("## 1. Request Performance & Reliability")
    md.append(f"- **Total Requests Logged**: {len(rows)}")
    md.append(f"- **Understand Deterministic Rate**: {deterministic_routing / max(1, deterministic_routing+llm_routing)*100:.1f}%")
    md.append(f"- **Understand Escalated LLM Rate**: {llm_routing / max(1, deterministic_routing+llm_routing)*100:.1f}%")
    md.append(f"- **Clarification Escalation Rate**: {clarification_rate / max(1, len(rows))*100:.1f}%")
    md.append(f"- **Average Retrieval Coverage**: {sum(coverage_arr)/max(1, len(coverage_arr))*100:.1f}%\n")

    md.append("## 2. Latency Percentiles (ms)")
    md.append("| Metric | Avg | P50 | P95 | P99 | Max |")
    md.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    md.append(f"| Request Latency | {latency_percentiles['Avg']} | {latency_percentiles['P50']} | {latency_percentiles['P95']} | {latency_percentiles['P99']} | {latency_percentiles['Max']} |\n")

    md.append("## 3. Human Evaluation Quality Metrics")
    md.append(f"- **Total Manual Evaluated Sample**: {total_evals}")
    md.append(f"- **Average Correctness (1-5)**: {avg_correctness:.2f}")
    md.append(f"- **Average Completeness (1-5)**: {avg_completeness:.2f}")
    md.append(f"- **Average Groundedness (1-5)**: {avg_groundedness:.2f}")
    md.append(f"- **Hallucination Rate (%)**: {hallucination_rate:.1f}%")
    md.append(f"- **Citation Quality Score (1-5)**: {avg_citation:.2f}")
    md.append(f"- **User Satisfaction Score (1-5)**: {avg_satisfaction:.2f}\n")

    md.append("## 4. Operational Cost Metrics")
    md.append(f"- **Total Staging Spend**: ${costs.get('total_cost', 0.0):.6f}")
    md.append(f"- **Avg Cost Per Request**: ${costs.get('total_cost', 0.0)/max(1, len(rows)):.6f}")
    md.append(f"- **Avg Tokens/Request**: {costs.get('avg_tokens_per_request', 0.0)}")
    md.append(f"- **Peak Single Request Tokens**: {costs.get('peak_tokens_single_request', 0.0)}\n")

    md.append("## 5. Failure Categorization Taxonomy")
    md.append("| Failure Category | Count | % of Failures |")
    md.append("| --- | --- | ---: |")
    failed = errors.get("failed", 0) or 1
    for category, count in errors.get("breakdown", {}).items():
        pct = (count / failed) * 100 if errors.get("failed", 0) > 0 else 0
        md.append(f"| {category} | {count} | {pct:.1f}% |")

    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "citta_production_benchmark.md"))
    with open(report_path, "w") as f:
        f.write("\n".join(md))

    print(f"Production Benchmark generated successfully and written to {report_path}")

if __name__ == "__main__":
    main()
