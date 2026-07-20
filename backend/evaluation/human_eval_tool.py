import sqlite3
import json
import os
import sys

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "telemetry.db"))

def get_int_input(prompt, min_val, max_val):
    while True:
        try:
            val = int(input(prompt))
            if min_val <= val <= max_val:
                return val
            print(f"Error: Value must be between {min_val} and {max_val}.")
        except ValueError:
            print("Error: Invalid integer input.")

def main():
    if not os.path.exists(DB_PATH):
        print(f"Telemetry database not found at {DB_PATH}. Please execute the engine first to populate logs.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query un-scored telemetry items
    cursor.execute("""
    SELECT t.id, t.timestamp, t.query, t.context_json 
    FROM requests_telemetry t
    LEFT JOIN human_evaluations e ON t.id = e.request_id
    WHERE e.request_id IS NULL
    ORDER BY t.timestamp DESC
    """)
    
    rows = cursor.fetchall()
    if not rows:
        print("All request logs have been human-evaluated! Nothing to review.")
        conn.close()
        return

    print(f"Found {len(rows)} un-reviewed requests in staging pilot telemetry.")
    print("Starting human evaluation. Enter 'q' at any score prompt to quit.\n")

    for id_, timestamp, query, context_json in rows:
        try:
            ctx = json.loads(context_json)
            # Fetch the actual output response drafted by the COMPOSE state
            draft_resp = ctx.get("response_plan", {}).get("draft_response", "No draft response produced.")
        except Exception:
            draft_resp = "Error deserializing execution context JSON."

        print("="*60)
        print(f"Query Time : {timestamp}")
        print(f"Query ID   : {id_}")
        print(f"User Query : {query}")
        print("-"*60)
        print(f"Response:\n{draft_resp}")
        print("="*60)

        try:
            correctness = get_int_input("Correctness Score (1-5): ", 1, 5)
            completeness = get_int_input("Completeness Score (1-5): ", 1, 5)
            groundedness = get_int_input("Groundedness Score (1-5): ", 1, 5)
            hallucination = get_int_input("Did the response hallucinate? (1 = Yes, 0 = No): ", 0, 1)
            citation_quality = get_int_input("Citation/Reference Quality Score (1-5): ", 1, 5)
            user_satisfaction = get_int_input("Estimated User Satisfaction (1-5): ", 1, 5)
            comments = input("Comments (optional): ").strip()
            
            cursor.execute("""
            INSERT OR REPLACE INTO human_evaluations 
            (request_id, correctness, completeness, groundedness, hallucination, citation_quality, user_satisfaction, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_, correctness, completeness, groundedness, hallucination, citation_quality, user_satisfaction, comments))
            conn.commit()
            print("Evaluation saved successfully!\n")
            
        except KeyboardInterrupt:
            print("\nExiting evaluator.")
            break
        except Exception as e:
            # Check for quit signal
            print(f"Error saving evaluation: {e}")
            break

    conn.close()

if __name__ == "__main__":
    main()
