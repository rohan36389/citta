import sqlite3
import json
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "telemetry.db"))

def classify_failures():
    if not os.path.exists(DB_PATH):
        print("Telemetry database not found. Run the engine first.")
        return {}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, query, context_json FROM requests_telemetry")
    rows = cursor.fetchall()
    conn.close()

    total = len(rows)
    success_count = 0
    categories = {
        "Intent classification": 0,
        "Entity extraction": 0,
        "Retrieval failure": 0,
        "Missing knowledge": 0,
        "LLM hallucination": 0,
        "Validation issue": 0,
        "Timeout": 0,
        "User ambiguity": 0,
        "Other failure": 0
    }

    for id_, query, context_json in rows:
        try:
            ctx = json.loads(context_json)
        except Exception:
            categories["Other failure"] += 1
            continue

        # Look for explicit errors in history
        history = ctx.get("history", [])
        events = ctx.get("events", [])
        
        # Check if the execution ended in clarification fallback
        has_clarify = any(h.get("state") == "CLARIFY" for h in history)
        
        # Check for budget timeouts or other timeouts
        has_timeout = any(e.get("name") == "TIMEOUT" or e.get("name") == "BUDGET_EXCEEDED" for e in events)

        failed_step = None
        for step in history:
            if step.get("result") == "FAILURE":
                failed_step = step
                break

        if failed_step:
            state = failed_step.get("state")
            notes = failed_step.get("notes", "")
            
            if has_timeout or "timeout" in notes.lower():
                categories["Timeout"] += 1
            elif state == "UNDERSTAND":
                # Understand failures could be extraction or classification
                if "intent" in notes.lower():
                    categories["Intent classification"] += 1
                else:
                    categories["Entity extraction"] += 1
            elif state in ["RETRIEVE", "ENOUGH_CHECK"]:
                if "knowledge" in notes.lower() or "chunk" in notes.lower():
                    categories["Missing knowledge"] += 1
                else:
                    categories["Retrieval failure"] += 1
            elif state == "VALIDATE":
                validation_res = ctx.get("validation_result", {})
                if validation_res and validation_res.get("hallucination_risk") == "HIGH":
                    categories["LLM hallucination"] += 1
                else:
                    categories["Validation issue"] += 1
            else:
                categories["Other failure"] += 1
        elif has_clarify:
            categories["User ambiguity"] += 1
        else:
            success_count += 1

    report = {
        "total": total,
        "success": success_count,
        "failed": total - success_count,
        "breakdown": categories
    }

    return report

def main():
    report = classify_failures()
    if not report:
        return
        
    print("="*60)
    print("           PRODUCTION ERROR TAXONOMY REPORT")
    print("="*60)
    print(f"Total Requests Evaluated: {report['total']}")
    print(f"Successful Requests     : {report['success']}")
    print(f"Failed/Clarified Requests: {report['failed']}")
    print("-"*60)
    print("Failure Category Breakdown:")
    
    failed = report["failed"] or 1
    for category, count in report["breakdown"].items():
        pct = (count / failed) * 100 if report["failed"] > 0 else 0
        print(f"  - {category:<25}: {count:<4} ({pct:.1f}% of failures)")
    print("="*60)

if __name__ == "__main__":
    main()
