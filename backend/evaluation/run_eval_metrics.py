import os
import sys
import json
import time
import csv
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Setup paths
EVAL_DIR = Path(__file__).resolve().parent
BACKEND_DIR = EVAL_DIR.parent
sys.path.append(str(BACKEND_DIR))

from intelligence_engine import IntelligenceEngine

async def evaluate_query(engine: IntelligenceEngine, case_id: int, query: str, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
    async with semaphore:
        start_time = time.time()
        try:
            # Execute query through state machine
            context = await engine.execute(query, tenant_id="cittaai", session_id=f"eval_session_{case_id}")
            runtime_ms = int((time.time() - start_time) * 1000)

            # Extract metrics from context
            intent_detected = context.understanding.intent if context.understanding else "UNKNOWN"
            understand_llm_escalated = "LLM" if (context.understanding and not context.understanding.resolved_deterministically) else "DETERMINISTIC"

            # Check Decide Route from history
            decide_route = "clarification"
            if context.execution_plan:
                if context.execution_plan.is_deterministic:
                    decide_route = "deterministic"
                else:
                    decide_route = "retrieval-based"
            
            # Count retrieval passes
            retrieval_passes = context.retrieval_request.retrieval_pass_number if context.retrieval_request else 0
            retrieval_coverage = context.retrieval_result.retrieval_coverage if context.retrieval_result else 0.0

            # Validation details
            val_action = context.validation_result.action.value if context.validation_result else "NONE"
            val_confidence = context.validation_result.validation_confidence if context.validation_result else 0.0

            # LLM calls count: starts with default max remaining (2), decrement by remaining
            llm_calls_made = 2 - context.budget.llm.remaining_calls
            budget_cap_hit = "YES" if "BUDGET_EXCEEDED" in [e.name for e in context.events] else "NO"

            # Format full execution step history
            history_str = " -> ".join([f"{step.state}({step.result}:{step.duration_ms}ms)" for step in context.history])

            # Chunks count
            chunks_used = len(context.retrieval_result.chunks) if context.retrieval_result else 0

            return {
                "Query ID": case_id,
                "Query": query,
                "Intent Detected": intent_detected,
                "Understand LLM Escalated": understand_llm_escalated,
                "Decide Route": decide_route,
                "Retrieval Passes": retrieval_passes,
                "Final Retrieval Coverage": f"{retrieval_coverage:.2f}",
                "Validation Action": val_action,
                "Validation Confidence": f"{val_confidence:.2f}",
                "Total Runtime MS": runtime_ms,
                "Total LLM Calls": llm_calls_made,
                "Budget Cap Hit": budget_cap_hit,
                "Chunks Used": chunks_used,
                "History": history_str,
                "Manual Pass/Fail": "",  # To be filled in by reviewer
                "context": context  # Hold context reference for aggregates
            }
        except Exception as e:
            runtime_ms = int((time.time() - start_time) * 1000)
            return {
                "Query ID": case_id,
                "Query": query,
                "Intent Detected": "ERROR",
                "Understand LLM Escalated": "ERROR",
                "Decide Route": "ERROR",
                "Retrieval Passes": 0,
                "Final Retrieval Coverage": "0.00",
                "Validation Action": "ERROR",
                "Validation Confidence": "0.00",
                "Total Runtime MS": runtime_ms,
                "Total LLM Calls": 0,
                "Budget Cap Hit": "NO",
                "Chunks Used": 0,
                "History": f"ERROR: {str(e)}",
                "Manual Pass/Fail": "FAIL",
                "context": None
            }

async def run_evaluation():
    print("================ CITTAAI OPERATIONAL METRICS BENCHMARK ================")
    
    questions_file = EVAL_DIR / "golden_questions.json"
    if not questions_file.exists():
        print(f"Golden questions file not found at {questions_file}")
        return

    with open(questions_file, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    # Run first 30 scenarios + last 13 new regression scenarios (total 43 scenarios)
    test_cases = test_cases[:30] + test_cases[-13:]
    total_cases = len(test_cases)
    print(f"Running evaluation against {total_cases} test scenarios...")

    engine = IntelligenceEngine()
    
    # Warmup provider and database
    print("Warming up models...")
    engine.get_embedding_model()
    engine.get_llm_provider()

    # Semaphore to run up to 5 concurrent queries
    sem = asyncio.Semaphore(5)
    
    start_eval = time.time()
    tasks = [evaluate_query(engine, idx + 1, case["question"], sem) for idx, case in enumerate(test_cases)]
    results = await asyncio.gather(*tasks)
    total_eval_time = time.time() - start_eval

    # Write CSV output
    csv_file = EVAL_DIR / "operational_metrics.csv"
    csv_headers = [
        "Query ID", "Query", "Intent Detected", "Understand LLM Escalated",
        "Decide Route", "Retrieval Passes", "Final Retrieval Coverage",
        "Validation Action", "Validation Confidence", "Total Runtime MS",
        "Total LLM Calls", "Budget Cap Hit", "Chunks Used", "History", "Manual Pass/Fail"
    ]
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
        for r in results:
            row_to_write = {k: v for k, v in r.items() if k != "context"}
            writer.writerow(row_to_write)

    # Compute Aggregates
    valid_results = [r for r in results if r["context"] is not None]
    total_valid = len(valid_results)

    if total_valid > 0:
        understand_det_pct = (sum(1 for r in valid_results if r["Understand LLM Escalated"] == "DETERMINISTIC") / total_valid) * 100.0
        decide_det_pct = (sum(1 for r in valid_results if r["Decide Route"] == "deterministic") / total_valid) * 100.0
        clarify_pct = (sum(1 for r in valid_results if "CLARIFY" in [step.state for step in r["context"].history]) / total_valid) * 100.0
        budget_exceeded_pct = (sum(1 for r in valid_results if r["Budget Cap Hit"] == "YES") / total_valid) * 100.0

        # Avg coverage and runtime by intent
        intent_stats = {}
        for r in valid_results:
            intent = r["Intent Detected"]
            coverage = float(r["Final Retrieval Coverage"])
            runtime = r["Total Runtime MS"]
            
            if intent not in intent_stats:
                intent_stats[intent] = {"coverage_sum": 0.0, "runtime_sum": 0, "count": 0}
            
            intent_stats[intent]["coverage_sum"] += coverage
            intent_stats[intent]["runtime_sum"] += runtime
            intent_stats[intent]["count"] += 1

        # Capability failures and timeouts
        cap_failures = {}
        total_caps_run = 0
        for r in valid_results:
            for cap in r["context"].capability_results:
                total_caps_run += 1
                worker = cap.next_event # or custom identifier
                # Group by worker
                worker_name = worker.replace("_COMPLETE", "").replace("_PASSED", "").replace("_FAILED", "").lower()
                if cap.status in ["FAILURE", "TIMEOUT"]:
                    if worker_name not in cap_failures:
                        cap_failures[worker_name] = 0
                    cap_failures[worker_name] += 1

        # Validation retry rate
        total_retries = 0
        for r in valid_results:
            # Check validation result retries
            for step in r["context"].history:
                if step.state == "VALIDATE" and step.result == "SUCCESS":
                    val_res = r["context"].validation_result
                    if val_res and val_res.action in [ValidationAction.RETRY_COMPOSE, ValidationAction.RETRY_RETRIEVAL]:
                        total_retries += 1

        avg_chunks = sum(r["Chunks Used"] for r in valid_results) / total_valid
    else:
        understand_det_pct = decide_det_pct = clarify_pct = budget_exceeded_pct = 0.0
        intent_stats = {}
        cap_failures = {}
        total_retries = 0
        avg_chunks = 0.0

    # Write Markdown Summary report
    summary_file = EVAL_DIR / "operational_summary.md"
    summary_content = [
        "# CittaAI Operational Metrics & Benchmark Summary\n",
        f"Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total query scenarios run: {total_valid} / {total_cases}\n",
        "## Summary Metrics\n",
        f"- **Understand Deterministic Resolution Rate**: {understand_det_pct:.1f}% (queries not needing LLM understanding)",
        f"- **End-to-End Deterministic Path Rate**: {decide_det_pct:.1f}% (handled fully deterministically, zero-LLM/zero-RAG)",
        f"- **Clarification Escalation Rate**: {clarify_pct:.1f}% (queries routed to clarify)",
        f"- **Budget/Timeout Exceeded Rate**: {budget_exceeded_pct:.1f}% (exceeded limits before sufficiency)",
        f"- **Validation Retry Rate**: {total_retries} total retry actions triggered",
        f"- **Average RAG Context Chunks Used**: {avg_chunks:.2f} chunks per request\n",
        "## Per-Intent Performance Metrics\n",
        "| Intent Detected | Scenarios Run | Avg Retrieval Coverage | Avg Latency (ms) |",
        "|---|---|---|---|"
    ]
    for intent, stat in intent_stats.items():
        avg_cov = stat["coverage_sum"] / stat["count"]
        avg_run = stat["runtime_sum"] / stat["count"]
        summary_content.append(f"| {intent} | {stat['count']} | {avg_cov:.2f} | {avg_run:.1f}ms |")

    summary_content.extend([
        "\n## Capability Failures and Timeouts Breakdown\n",
        "| Capability Worker | Failure/Timeout Count |",
        "|---|---|"
    ])
    if cap_failures:
        for worker, count in cap_failures.items():
            summary_content.append(f"| {worker} | {count} |")
    else:
        summary_content.append("| None | 0 |")

    summary_content.extend([
        "\n## Review Actions Needed\n",
        "Please review the detailed log file in [operational_metrics.csv](file:///c:/Users/Rohan%20chilukuri/citta/backend/evaluation/operational_metrics.csv) and fill out the manual pass/fail column."
    ])

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_content))

    print(f"\nOperational metrics saved to: {csv_file}")
    print(f"Operational summary report saved to: {summary_file}")
    print(f"Total benchmark run took {total_eval_time:.1f} seconds.")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
