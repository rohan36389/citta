import sqlite3
import json
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "telemetry.db"))

# Pricing Model: NVIDIA Llama-3 (per 1M tokens)
INPUT_COST_PER_1M = 0.70 # $0.70 per 1M prompt tokens
OUTPUT_COST_PER_1M = 0.90 # $0.90 per 1M completion tokens

def analyze_costs():
    if not os.path.exists(DB_PATH):
        print("Telemetry database not found. Run the engine first.")
        return {}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT tenant_id, context_json FROM requests_telemetry")
    rows = cursor.fetchall()
    conn.close()

    total_requests = len(rows)
    total_cost = 0.0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    peak_tokens_single_request = 0
    
    tenant_costs = {}
    intent_costs = {}
    status_costs = {"SUCCESS": {"cost": 0.0, "count": 0}, "FAILURE": {"cost": 0.0, "count": 0}}

    for tenant_id, context_json in rows:
        try:
            ctx = json.loads(context_json)
        except Exception:
            continue

        # Extract tokens from all capability results
        req_prompt = 0
        req_completion = 0
        
        for cap in ctx.get("capability_results", []):
            lm = cap.get("llm_metrics")
            if lm:
                req_prompt += lm.get("prompt_tokens", 0)
                req_completion += lm.get("completion_tokens", 0)
        
        req_total_tokens = req_prompt + req_completion
        if req_total_tokens > peak_tokens_single_request:
            peak_tokens_single_request = req_total_tokens

        # Compute cost
        cost = (req_prompt * INPUT_COST_PER_1M / 1000000.0) + (req_completion * OUTPUT_COST_PER_1M / 1000000.0)
        
        total_cost += cost
        total_prompt_tokens += req_prompt
        total_completion_tokens += req_completion

        # Group by tenant
        if tenant_id not in tenant_costs:
            tenant_costs[tenant_id] = {"cost": 0.0, "count": 0}
        tenant_costs[tenant_id]["cost"] += cost
        tenant_costs[tenant_id]["count"] += 1

        # Group by intent
        intent = "UNKNOWN"
        und = ctx.get("understanding")
        if und:
            intent = und.get("intent", "UNKNOWN")
            
        if intent not in intent_costs:
            intent_costs[intent] = {"cost": 0.0, "count": 0}
        intent_costs[intent]["cost"] += cost
        intent_costs[intent]["count"] += 1

        # Group by status
        history = ctx.get("history", [])
        has_failure = any(h.get("result") == "FAILURE" for h in history)
        status = "FAILURE" if has_failure else "SUCCESS"
        status_costs[status]["cost"] += cost
        status_costs[status]["count"] += 1

    report = {
        "total_requests": total_requests,
        "total_cost": round(total_cost, 6),
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "avg_tokens_per_request": round((total_prompt_tokens + total_completion_tokens) / max(1, total_requests), 1),
        "peak_tokens_single_request": peak_tokens_single_request,
        "tenant_costs": tenant_costs,
        "intent_costs": intent_costs,
        "status_costs": status_costs
    }

    return report

def main():
    report = analyze_costs()
    if not report:
        return

    print("="*60)
    print("           PRODUCTION TELEMETRY COST ANALYSIS")
    print("="*60)
    print(f"Total Requests Evaluated: {report['total_requests']}")
    print(f"Total Combined Cost     : ${report['total_cost']:.6f}")
    print(f"Average Cost/Request    : ${report['total_cost'] / max(1, report['total_requests']):.6f}")
    print(f"Total Prompt Tokens     : {report['total_prompt_tokens']}")
    print(f"Total Completion Tokens : {report['total_completion_tokens']}")
    print(f"Average Request Tokens  : {report['avg_tokens_per_request']}")
    print(f"Peak Request Tokens     : {report['peak_tokens_single_request']}")
    
    print("-"*60)
    print("Cost breakdown by Tenant:")
    for tenant, data in report["tenant_costs"].items():
        print(f"  - {tenant:<15}: ${data['cost']:.6f} ({data['count']} reqs)")

    print("-"*60)
    print("Cost breakdown by Intent:")
    for intent, data in report["intent_costs"].items():
        print(f"  - {intent:<15}: ${data['cost']:.6f} ({data['count']} reqs)")

    print("-"*60)
    print("Cost breakdown by Status:")
    for status, data in report["status_costs"].items():
        print(f"  - {status:<15}: ${data['cost']:.6f} ({data['count']} reqs)")
    print("="*60)

if __name__ == "__main__":
    main()
