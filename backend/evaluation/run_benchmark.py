import os
import sys
import json
import time
from pathlib import Path

# Setup paths
EVAL_DIR = Path(__file__).resolve().parent
BACKEND_DIR = EVAL_DIR.parent
sys.path.append(str(BACKEND_DIR))

# Import planning & resolution logic
try:
    from query_planner import classify_query
except ImportError:
    from backend.query_planner import classify_query

def run_evaluation():
    print("================ RUNNING CITTAAI V3.4 ACCURACY BENCHMARK ================")
    
    questions_file = EVAL_DIR / "golden_questions.json"
    if not questions_file.exists():
        print(f"Golden questions file not found at {questions_file}")
        return

    with open(questions_file, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    total_tests = len(test_cases)
    passed_type = 0
    passed_domain = 0
    passed_entity = 0
    
    report_rows = []

    for idx, case in enumerate(test_cases):
        q = case["question"]
        exp_type = case["expected_query_type"]
        exp_domain = case["expected_domain"]
        exp_entity = case.get("expected_entity")
        
        start_time = time.time()
        
        # Call Classifier
        cls_res = classify_query(q)
        act_type = cls_res["query_type"]
        act_domain = cls_res["domain"]
        act_entity = cls_res["matched_entity"]
        
        type_ok = (act_type == exp_type)
        domain_ok = (act_domain == exp_domain)
        entity_ok = (act_entity == exp_entity)
        
        if type_ok: passed_type += 1
        if domain_ok: passed_domain += 1
        if entity_ok: passed_entity += 1
            
        latency = (time.time() - start_time) * 1000.0 # ms
        
        status = "PASS" if (type_ok and domain_ok and entity_ok) else "FAIL"
        report_rows.append({
            "id": idx + 1,
            "question": q,
            "expected_query_type": exp_type,
            "actual_query_type": act_type,
            "expected_domain": exp_domain,
            "actual_domain": act_domain,
            "expected_entity": exp_entity or "None",
            "actual_entity": act_entity or "None",
            "latency": f"{latency:.2f}ms",
            "status": status
        })

    # Calculations
    type_acc = (passed_type / total_tests) * 100.0
    domain_acc = (passed_domain / total_tests) * 100.0
    entity_acc = (passed_entity / total_tests) * 100.0
    overall_acc = (type_acc + domain_acc + entity_acc) / 3.0

    print(f"\nBenchmark results:")
    print(f"  Total tests             : {total_tests}")
    print(f"  Query Type Accuracy     : {passed_type}/{total_tests} ({type_acc:.1f}%)")
    print(f"  Domain Detection Acc    : {passed_domain}/{total_tests} ({domain_acc:.1f}%)")
    print(f"  Entity Mapping Accuracy : {passed_entity}/{total_tests} ({entity_acc:.1f}%)")
    print(f"  Overall Score           : {overall_acc:.1f}%")

    # Generate Markdown Report
    report_file = EVAL_DIR / "benchmark_report.md"
    report_content = [
        "# CittaAI V3.4 Demo-Freeze Accuracy Report\n",
        f"Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## Summary Statistics\n",
        f"- **Total Scenarios Evaluated**: {total_tests}",
        f"- **Query Type Accuracy**: {type_acc:.1f}% ({passed_type}/{total_tests})",
        f"- **Domain Detection Accuracy**: {domain_acc:.1f}% ({passed_domain}/{total_tests})",
        f"- **Entity Mapping Accuracy**: {entity_acc:.1f}% ({passed_entity}/{total_tests})",
        f"- **Overall Core Score**: **{overall_acc:.1f}%**\n",
        "## Detail Log Matrix\n",
        "| # | Question | Expected Type | Actual Type | Expected Domain | Actual Domain | Expected Entity | Resolved Entity | Latency | Status |",
        "|---|---|---|---|---|---|---|---|---|---|"
    ]
    
    for row in report_rows:
        report_content.append(
            f"| {row['id']} | {row['question']} | {row['expected_query_type']} | {row['actual_query_type']} | "
            f"{row['expected_domain']} | {row['actual_domain']} | {row['expected_entity']} | {row['actual_entity']} | "
            f"{row['latency']} | {row['status']} |"
        )
        
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))
    print(f"\nFull validation report saved to: {report_file}")

if __name__ == "__main__":
    run_evaluation()
