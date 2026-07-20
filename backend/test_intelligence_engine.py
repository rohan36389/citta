import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

from intelligence_engine import IntelligenceEngine

async def run_test():
    engine = IntelligenceEngine()
    
    print("Test 1: Deterministic Query (GREETINGS)")
    print("=" * 60)
    ctx1 = await engine.execute("hello, who are you?", tenant_id="cittaai", session_id="test_session_1")
    print(f"Final State History: {[s.state for s in ctx1.history]}")
    print(f"Final Events List: {[e.name for e in ctx1.events]}")
    print(f"Resolved Deterministically: {ctx1.understanding.resolved_deterministically if ctx1.understanding else None}")
    print(f"Draft Response:\n{ctx1.response_plan.draft_response if ctx1.response_plan else None}")
    print("=" * 60)
    print()

    print("Test 2: General Query (RAG path)")
    print("=" * 60)
    ctx2 = await engine.execute("what is the WhatsApp Marketing Platform?", tenant_id="cittaai", session_id="test_session_2")
    print(f"Final State History: {[s.state for s in ctx2.history]}")
    print(f"Final Events List: {[e.name for e in ctx2.events]}")
    print(f"Resolved Deterministically: {ctx2.understanding.resolved_deterministically if ctx2.understanding else None}")
    print(f"Remaining LLM calls: {ctx2.budget.llm.remaining_calls}")
    print(f"Remaining Retrieval runs: {ctx2.budget.retrieval.remaining_retrievals}")
    print(f"Draft Response:\n{ctx2.response_plan.draft_response if ctx2.response_plan else None}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_test())
