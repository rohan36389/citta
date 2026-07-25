import sqlite3
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect('backend/telemetry.db')
c = conn.cursor()

# Find rows containing test_session
c.execute("SELECT session_id, query, timestamp, context_json FROM requests_telemetry WHERE session_id LIKE 'test_session%' ORDER BY timestamp DESC LIMIT 2")
rows = c.fetchall()
print(f"Found {len(rows)} test session rows.")

for session_id, query, timestamp, context_json in rows:
    print(f"\n==================== {session_id} ====================")
    print("TIMESTAMP:", timestamp)
    print("QUERY:", query)
    try:
        ctx = json.loads(context_json)
        history = ctx.get("history", [])
        states = [h.get("state") for h in history]
        print("STATES:", " -> ".join(states))
        
        events = ctx.get("events", [])
        print("EVENTS:", ", ".join([f"{e.get('name')} ({e.get('producer')})" for e in events]))
        
        caps = ctx.get("capability_results", [])
        print("CAPABILITIES:")
        llm_calls = 0
        for cap in caps:
            name = cap.get("name")
            status = cap.get("status")
            dur = cap.get("duration_ms")
            next_ev = cap.get("next_event")
            data = cap.get("data")
            if "llm_provider" in name or "call_llm" in name:
                llm_calls += 1
            if isinstance(data, str):
                data_str = data[:150]
            else:
                data_str = json.dumps(data, ensure_ascii=False)[:150]
            print(f"  - {name} | {status} | {dur}ms | Next: {next_ev} | Data: {data_str}")
            
        print("LLM CALLS IN HISTORY:", llm_calls)
        print("METADATA:", json.dumps(ctx.get("request", {}).get("metadata", {}), ensure_ascii=False))
        und = ctx.get("understanding", {})
        print("UNDERSTANDING:", json.dumps(und, ensure_ascii=False))
    except Exception as e:
        print("Error parsing json:", e)
    print("=" * 60)

conn.close()
