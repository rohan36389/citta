import os
import sys
import json
import logging
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BACKEND_DIR / "evaluation" / "reports"
HISTORY_FILE = BACKEND_DIR / "evaluation" / "benchmark_history.json"
DASHBOARD_FILE = REPORTS_DIR / "ecqf_dashboard.html"

def generate_html_dashboard():
    """Generates an interactive visual HTML dashboard for ECQF quality reporting."""
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
            
    latest = history[-1] if history else {
        "timestamp": "N/A",
        "version": "1.0",
        "overall_quality_score": 100.0,
        "conv_quality_score": 100.0,
        "pipeline_quality_score": 100.0,
        "release_gate_status": "PASSED"
    }

    gate_color = "#10B981" if latest.get("release_gate_status") == "PASSED" else "#EF4444"
    gate_badge = f"<span style='background-color: {gate_color}; color: white; padding: 4px 12px; border-radius: 9999px; font-weight: bold; font-size: 14px;'>{latest.get('release_gate_status')}</span>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECQF v1.0 Quality Dashboard - CittaAI</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0F172A;
            color: #F8FAFC;
            margin: 0;
            padding: 24px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .title {{
            font-size: 24px;
            font-weight: bold;
            color: #38BDF8;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        .card {{
            background-color: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
        }}
        .card-label {{
            font-size: 14px;
            color: #94A3B8;
            margin-bottom: 8px;
        }}
        .card-value {{
            font-size: 32px;
            font-weight: bold;
            color: #F8FAFC;
        }}
        .card-subtext {{
            font-size: 12px;
            color: #64748B;
            margin-top: 4px;
        }}
        .table-container {{
            background-color: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 32px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}
        th, td {{
            padding: 12px;
            border-bottom: 1px solid #334155;
        }}
        th {{
            color: #94A3B8;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <div class="title">CittaAI Enterprise Conversation Quality Framework (ECQF v1.0)</div>
                <div style="color: #94A3B8; font-size: 14px; margin-top: 4px;">Last Run: {latest.get('timestamp')}</div>
            </div>
            <div>
                Release Status: {gate_badge}
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-label">Overall Quality Score</div>
                <div class="card-value" style="color: #38BDF8;">{latest.get('overall_quality_score', 0):.1f}%</div>
                <div class="card-subtext">Combined Dual Scorecard Score</div>
            </div>
            <div class="card">
                <div class="card-label">Conversation Quality</div>
                <div class="card-value" style="color: #34D399;">{latest.get('conv_quality_score', 0):.1f}%</div>
                <div class="card-subtext">Retention, Coreference & Memory</div>
            </div>
            <div class="card">
                <div class="card-label">Pipeline Quality</div>
                <div class="card-value" style="color: #A78BFA;">{latest.get('pipeline_quality_score', 0):.1f}%</div>
                <div class="card-subtext">Routing, Provenance & Guardrails</div>
            </div>
            <div class="card">
                <div class="card-label">Scenarios Passed</div>
                <div class="card-value">{latest.get('passed_scenarios', 0)} / {latest.get('total_scenarios', 0)}</div>
                <div class="card-subtext">Scenario Pass Rate: {latest.get('scenario_pass_rate', 0):.1f}%</div>
            </div>
        </div>

        <div class="table-container">
            <h3 style="color: #38BDF8; margin-top: 0;">Historical Quality Trend</h3>
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Version</th>
                        <th>Overall Score</th>
                        <th>Conv Quality</th>
                        <th>Pipeline Quality</th>
                        <th>Gate Decision</th>
                    </tr>
                </thead>
                <tbody>
"""
    for entry in reversed(history[-10:]):
        html_content += f"""
                    <tr>
                        <td>{entry.get('timestamp')}</td>
                        <td>{entry.get('version')}</td>
                        <td><strong>{entry.get('overall_quality_score', 0):.1f}%</strong></td>
                        <td>{entry.get('conv_quality_score', 0):.1f}%</td>
                        <td>{entry.get('pipeline_quality_score', 0):.1f}%</td>
                        <td><span style="color: {'#10B981' if entry.get('release_gate_status')=='PASSED' else '#EF4444'}; font-weight: bold;">{entry.get('release_gate_status')}</span></td>
                    </tr>
"""

    html_content += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
    with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Generated HTML Dashboard at: {DASHBOARD_FILE}")

if __name__ == "__main__":
    generate_html_dashboard()
