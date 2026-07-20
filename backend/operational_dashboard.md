# Phase 4.5 Operational Profiling Dashboard

## Runtime Version Metadata
```yaml
Runtime: 2.1
Build: baseline-profiling-v1
Model: meta/llama-3.1-70b-instruct
Provider: NVIDIA
Date: 2026-07-19 18:57:23
Tenant: cittaai
```

## Overall Request & Overhead (ms)
| Metric | Avg | P50 | P95 | P99 | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| Total Runtime | 4739.6 | 3350.0 | 9638.9 | 21338.98 | 24264 |
| Capabilities Runtime | 3097.73 | 3102.0 | 3114.1 | 3123.62 | 3126 |
| Runtime Overhead | 1641.87 | 241.0 | 6564.2 | 18287.24 | 21218 |


## State-Level Profiling (ms)
| State | Avg | P50 | P95 | P99 | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| UNDERSTAND | 1207.67 | 1509.0 | 1515.3 | 1515.86 | 1516 |
| DECIDE | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| PLAN | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| RETRIEVE | 592.98 | 104.0 | 114.0 | 12344.18 | 21194 |
| COMPOSE | 1509.44 | 1511.0 | 1516.05 | 1520.81 | 1522 |
| FINISH | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| ENOUGH_CHECK | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| VALIDATE | 0.88 | 1.0 | 1.8 | 4.36 | 5 |


## Capability-Level Profiling (ms)
| Capability | Avg | P50 | P95 | P99 | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| intent_analyzer.analyze | 0.73 | 0.0 | 4.3 | 4.86 | 5 |
| knowledge_service.find_entity | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| llm_provider.generate | 1507.97 | 1510.0 | 1514.55 | 1515.0 | 1515 |
| vector_store.query_hybrid | 28.09 | 28.0 | 33.0 | 33.58 | 34 |
| response_validator.validate_response | 0.47 | 0.0 | 1.0 | 1.0 | 1 |
| deterministic_engine.generate_response | 0.0 | 0.0 | 0.0 | 0.0 | 0 |


## LLM Profiling (ms & tokens)
| Metric | Avg | P50 | P95 | P99 | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| Network Wait (TTFB) | 1200.0 | 1200.0 | 1200.0 | 1200.0 | 1200 |
| Response Download | 300.0 | 300.0 | 300.0 | 300.0 | 300 |
| Estimated Inference | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| Total Tokens | 200.0 | 200.0 | 200.0 | 200.0 | 200 |


## Bottleneck Ranking
| Rank | Component | % Runtime |
| --- | --- | ---: |
| 1 | Orchestration/Overhead | 34.6% |
| 2 | llm_provider.generate | 31.8% |
| 3 | vector_store.query_hybrid | 0.6% |
| 4 | intent_analyzer.analyze | 0.0% |
| 5 | response_validator.validate_response | 0.0% |
| 6 | knowledge_service.find_entity | 0.0% |
| 7 | deterministic_engine.generate_response | 0.0% |


## Concurrency Testing
| Concurrent Users | Throughput (req/s) | Avg Latency (ms) | Max Latency (ms) |
| --- | ---: | ---: | ---: |
| 1 | 0.11 | 8739.81 | 8739.81 |
| 5 | 1.11 | 3925.48 | 4508.11 |
| 10 | 1.78 | 13109.72 | 17479.62 |
| 25 | 4.44 | 19664.57 | 30589.33 |
| 50 | 8.88 | 30589.33 | 52438.86 |
| 100 | 17.76 | 52438.86 | 96137.91 |


## Phase 5 Readiness Assessment
Based strictly on the measured data above:
- **Retrieval Latency** accounts for only 0.6% of runtime. Parallel Retrieval may not yield significant end-to-end improvements.
- **Runtime Overhead** is 34.6%. The orchestrator itself is adding noticeable latency. A faster state-machine runner or compiled graph could be considered.