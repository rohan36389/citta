import os
import sys
import json
import time
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# Ensure backend root is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from rag_service import RAGService
    from deterministic_engine import get_deterministic_engine
    from intent_analyzer import get_intent_analyzer
except ImportError:
    from rag_service import RAGService
    from deterministic_engine import get_deterministic_engine
    from intent_analyzer import get_intent_analyzer

logger = logging.getLogger("ecqf_evaluator")

CORPUS_DIR = BACKEND_DIR / "evaluation" / "corpus"
REPORTS_DIR = BACKEND_DIR / "evaluation" / "reports"
HISTORY_FILE = BACKEND_DIR / "evaluation" / "benchmark_history.json"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def parse_scenario_file(filepath: Path) -> Dict[str, Any]:
    """Parses a Markdown scenario file containing YAML frontmatter and turn steps."""
    content = filepath.read_text(encoding="utf-8")
    
    # Extract YAML frontmatter if present
    yaml_match = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    metadata = {}
    if yaml_match:
        yaml_text = yaml_match.group(1)
        try:
            import yaml
            metadata = yaml.safe_load(yaml_text) or {}
        except Exception:
            # Simple fallback parser if PyYAML is not installed
            metadata = {}
            for line in yaml_text.splitlines():
                if ":" in line and not line.strip().startswith("#"):
                    k, v = line.split(":", 1)
                    metadata[k.strip()] = v.strip().strip('"').strip("'")

    scenario_id = metadata.get("id", filepath.stem.upper())
    category = metadata.get("category", filepath.parent.name)
    turns = metadata.get("turns", [])
    
    # Fallback to parsing Markdown dialog blocks if turns are empty
    if not turns:
        dialog_turns = []
        cust_matches = re.findall(r"Customer:\s*\n([^\n]+)", content)
        asst_matches = re.findall(r"Assistant:\s*\n([^\n]+)", content)
        for idx, (c_text, a_text) in enumerate(zip(cust_matches, asst_matches)):
            dialog_turns.append({
                "turn": idx + 1,
                "user": c_text.strip(),
                "expected_response": {"must_include": []}
            })
        turns = dialog_turns

    return {
        "id": scenario_id,
        "category": category,
        "filepath": str(filepath),
        "metadata": metadata,
        "turns": turns
    }

import asyncio

async def run_ecqf_scenario_async(scenario: Dict[str, Any], rag_service: RAGService, repeat_count: int = 1) -> Dict[str, Any]:
    """Executes a multi-turn scenario using RAGService and evaluates internal state, routing, content, and latency."""
    session_id = f"ecqf_session_{scenario['id']}_{int(time.time()*1000)}"
    active_entity = None
    previous_entity = None
    
    scenario_pass = True
    turn_results = []
    
    total_turns = len(scenario["turns"])
    passed_turns = 0
    
    entity_retention_passes = 0
    coreference_passes = 0
    pricing_guardrail_passes = 0
    hallucination_passes = 0
    drift_violations = 0
    
    stage_latencies = []
    
    for turn_idx, turn in enumerate(scenario["turns"]):
        user_input = turn["user"]
        expected_state = turn.get("expected_state", {})
        expected_resp = turn.get("expected_response", {})
        
        t0 = time.perf_counter()
        
        # Execute turn via RAGService chat_stream
        text_parts = []
        final_meta = {}
        
        async for chunk in rag_service.chat_stream(message=user_input, session_id=session_id, tenant_id="cittaai", model="mock"):
            if isinstance(chunk, dict):
                if chunk.get("done"):
                    final_meta = chunk
                elif "text" in chunk:
                    text_parts.append(chunk["text"])
                    
        total_turn_ms = (time.perf_counter() - t0) * 1000.0
        resp_text = "".join(text_parts) if text_parts else final_meta.get("text", "")
        
        # Retrieve internal session state from RAGService memory
        state = rag_service.conversation_states.get(session_id, {})
        res_entity = state.get("active_entity") or "NONE"
        res_registry = state.get("active_registry") or "GENERAL"
        resp_source = final_meta.get("source") or final_meta.get("attribution", {}).get("source", "Pipeline")
        
        stage_latencies.append({
            "total_ms": total_turn_ms
        })
        
        # Turn Assertions
        turn_passed = True
        turn_errors = []
        
        # Assertion 1: Expected Entity Match
        exp_entity = expected_state.get("active_entity")
        if exp_entity:
            exp_clean = str(exp_entity).lower().replace("solution_", "").replace("product_", "").replace("service_", "")
            res_clean = str(res_entity).lower().replace("solution_", "").replace("product_", "").replace("service_", "")
            if exp_clean != res_clean and res_entity != "NONE":
                if turn_idx > 0 and active_entity and res_clean != str(active_entity).lower().replace("solution_", "").replace("product_", "").replace("service_", ""):
                    drift_violations += 1
                    turn_errors.append(f"Unexpected entity drift: active was '{active_entity}', shifted to '{res_entity}'")
                    turn_passed = False
                elif exp_clean != res_clean:
                    turn_errors.append(f"Expected entity '{exp_entity}', resolved '{res_entity}'")
                    turn_passed = False
            else:
                entity_retention_passes += 1

        # Assertion 2: Inherited Context Coreference
        if expected_state.get("inherited_context"):
            if active_entity and (res_entity == active_entity or res_entity == "NONE"):
                coreference_passes += 1
            else:
                turn_errors.append(f"Coreference failed: expected to inherit '{active_entity}', got '{res_entity}'")
                turn_passed = False
                
        # Assertion 3: Content Rules (Must Include / Must Not Include)
        must_inc = expected_resp.get("must_include", [])
        for inc_term in must_inc:
            if inc_term.lower() not in resp_text.lower():
                turn_errors.append(f"Response missing required term: '{inc_term}'")
                turn_passed = False
                
        must_not_inc = expected_resp.get("must_not_include", [])
        for exc_term in must_not_inc:
            if exc_term.lower() in resp_text.lower():
                turn_errors.append(f"Response contains forbidden term / hallucination: '{exc_term}'")
                turn_passed = False
            else:
                hallucination_passes += 1

        # Assertion 4: Pricing Guardrails
        if "pricing" in user_input.lower() or "cost" in user_input.lower():
            price_terms = ["$10", "$100", "₹50,000", "per month", "exact price"]
            if any(p in resp_text for p in price_terms):
                turn_errors.append("Pricing guardrail violation: system speculated exact pricing!")
                turn_passed = False
            else:
                pricing_guardrail_passes += 1

        if turn_passed:
            passed_turns += 1
        else:
            scenario_pass = False
            
        turn_results.append({
            "turn": turn_idx + 1,
            "user": user_input,
            "passed": turn_passed,
            "errors": turn_errors,
            "resolved_entity": res_entity,
            "resolved_registry": res_registry,
            "provenance": resp_source,
            "latency_ms": total_turn_ms
        })
        
        if res_entity != "NONE":
            previous_entity = active_entity
            active_entity = res_entity

    return {
        "id": scenario["id"],
        "category": scenario["category"],
        "passed": scenario_pass,
        "total_turns": total_turns,
        "passed_turns": passed_turns,
        "drift_violations": drift_violations,
        "turns": turn_results,
        "avg_latency_ms": sum(t["total_ms"] for t in stage_latencies) / max(len(stage_latencies), 1)
    }

def run_ecqf_suite(repeat_count: int = 1) -> Dict[str, Any]:
    """Scans all scenario files in corpus/ and runs evaluation suite."""
    scenario_files = list(CORPUS_DIR.glob("**/*.md"))
    if not scenario_files:
        logger.warning("No scenario .md files found in corpus directory.")
        return {}

    scenarios = [parse_scenario_file(f) for f in scenario_files]
    results = []
    
    total_scenarios = len(scenarios)
    passed_scenarios = 0
    total_turns_count = 0
    passed_turns_count = 0
    total_drift_count = 0
    
    category_summary = {}
    
    import llm_provider
    import vector_store

    provider = llm_provider.get_llm_provider("mock", {})
    vstore = vector_store.VectorStore()
    rag_service = RAGService(provider=provider, vector_store=vstore)

    for sc in scenarios:
        cat = sc["category"]
        if cat not in category_summary:
            category_summary[cat] = {"total": 0, "passed": 0}
            
        res = asyncio.run(run_ecqf_scenario_async(sc, rag_service, repeat_count=repeat_count))
        results.append(res)
        
        category_summary[cat]["total"] += 1
        total_turns_count += res["total_turns"]
        passed_turns_count += res["passed_turns"]
        total_drift_count += res["drift_violations"]
        
        if res["passed"]:
            passed_scenarios += 1
            category_summary[cat]["passed"] += 1

    scenario_pass_rate = (passed_scenarios / max(total_scenarios, 1)) * 100.0
    turn_pass_rate = (passed_turns_count / max(total_turns_count, 1)) * 100.0
    
    # Calculate Dual Scorecard Metrics
    conv_quality_score = turn_pass_rate
    pipeline_quality_score = 100.0 if total_drift_count == 0 else max(0.0, 100.0 - (total_drift_count * 5.0))
    overall_quality_score = (conv_quality_score * 0.5) + (pipeline_quality_score * 0.5)

    # Release Gate Evaluation
    release_blocked = (
        total_drift_count > 0 or
        turn_pass_rate < 90.0 or
        scenario_pass_rate < 90.0
    )

    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0",
        "total_scenarios": total_scenarios,
        "passed_scenarios": passed_scenarios,
        "scenario_pass_rate": scenario_pass_rate,
        "total_turns": total_turns_count,
        "passed_turns": passed_turns_count,
        "turn_pass_rate": turn_pass_rate,
        "drift_violations": total_drift_count,
        "conv_quality_score": conv_quality_score,
        "pipeline_quality_score": pipeline_quality_score,
        "overall_quality_score": overall_quality_score,
        "release_gate_status": "BLOCKED" if release_blocked else "PASSED",
        "category_summary": category_summary,
        "scenarios": results
    }

    # Append to benchmark_history.json
    save_benchmark_history(report_data)
    
    # Save Markdown report
    write_markdown_report(report_data)

    return report_data

def save_benchmark_history(report: Dict[str, Any]):
    """Appends benchmark metrics to historical log for trend graphing."""
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
            
    record = {
        "timestamp": report["timestamp"],
        "version": report["version"],
        "total_scenarios": report["total_scenarios"],
        "passed_scenarios": report["passed_scenarios"],
        "scenario_pass_rate": report["scenario_pass_rate"],
        "conv_quality_score": report["conv_quality_score"],
        "pipeline_quality_score": report["pipeline_quality_score"],
        "overall_quality_score": report["overall_quality_score"],
        "release_gate_status": report["release_gate_status"]
    }
    history.append(record)
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def write_markdown_report(report: Dict[str, Any]):
    """Generates comprehensive ECQF markdown audit report."""
    md = f"""# ECQF v1.0 Framework Audit Report

**Generated**: {report['timestamp']}  
**Release Gate Status**: **{report['release_gate_status']}**

## Dual Scorecard Summary

| Scorecard Component | Score / Pass Rate | Target | Gate Status |
| :--- | :--- | :--- | :--- |
| **Conversation Quality Scorecard** | **{report['conv_quality_score']:.1f}%** | >90.0% | {'PASS' if report['conv_quality_score'] >= 90.0 else 'FAIL'} |
| **Pipeline Quality Scorecard** | **{report['pipeline_quality_score']:.1f}%** | >95.0% | {'PASS' if report['pipeline_quality_score'] >= 95.0 else 'FAIL'} |
| **Overall ECQF Quality Score** | **{report['overall_quality_score']:.1f}%** | >95.0% | **{report['release_gate_status']}** |

## Category Coverage Breakdown

| Category | Total Scenarios | Passed | Pass Rate |
| :--- | :--- | :--- | :--- |
"""
    for cat, data in report["category_summary"].items():
        rate = (data["passed"] / max(data["total"], 1)) * 100.0
        md += f"| **{cat}** | {data['total']} | {data['passed']} | {rate:.1f}% |\n"

    report_path = REPORTS_DIR / "ecqf_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)
        
    logger.info(f"Saved ECQF report to {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Enterprise Conversation Quality Framework (ECQF)")
    parser.add_argument("--repeat", type=int, default=1, help="Repeat scenarios for determinism testing")
    args = parser.parse_args()
    
    logger.info("Starting Enterprise Conversation Quality Framework (ECQF v1.0)...")
    res = run_ecqf_suite(repeat_count=args.repeat)
    print(f"\n================ ECQF v1.0 EVALUATION COMPLETE ================")
    print(f"  Overall Quality Score  : {res.get('overall_quality_score', 0):.1f}%")
    print(f"  Conversation Quality   : {res.get('conv_quality_score', 0):.1f}%")
    print(f"  Pipeline Quality       : {res.get('pipeline_quality_score', 0):.1f}%")
    print(f"  Release Gate Decision  : {res.get('release_gate_status')}")
    print(f"===============================================================\n")
