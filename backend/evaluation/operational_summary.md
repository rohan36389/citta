# CittaAI Operational Metrics & Benchmark Summary

Generated on 2026-07-19 17:49:05
Total query scenarios run: 43 / 43

## Summary Metrics

- **Understand Deterministic Resolution Rate**: 76.7% (queries not needing LLM understanding)
- **End-to-End Deterministic Path Rate**: 25.6% (handled fully deterministically, zero-LLM/zero-RAG)
- **Clarification Escalation Rate**: 18.6% (queries routed to clarify)
- **Budget/Timeout Exceeded Rate**: 81.4% (exceeded limits before sufficiency)
- **Validation Retry Rate**: 0 total retry actions triggered
- **Average RAG Context Chunks Used**: 0.60 chunks per request

## Per-Intent Performance Metrics

| Intent Detected | Scenarios Run | Avg Retrieval Coverage | Avg Latency (ms) |
|---|---|---|---|
| UnderstandingIntent.SEARCH | 5 | 0.00 | 11654.4ms |
| UnderstandingIntent.LIST | 14 | 0.14 | 25084.8ms |
| UnderstandingIntent.ASK | 23 | 0.00 | 11397.1ms |
| UnderstandingIntent.COUNT | 1 | 0.00 | 9790.0ms |

## Capability Failures and Timeouts Breakdown

| Capability Worker | Failure/Timeout Count |
|---|---|
| None | 0 |

## Review Actions Needed

Please review the detailed log file in [operational_metrics.csv](file:///c:/Users/Rohan%20chilukuri/citta/backend/evaluation/operational_metrics.csv) and fill out the manual pass/fail column.