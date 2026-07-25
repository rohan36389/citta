import pytest
import asyncio
from orchestration_context import ExecutionStrategy
from phase2_orchestrator import get_phase2_orchestrator
from phase3_reasoning_engine import get_phase3_reasoning_engine
from prompt_builder import PROMPT_VERSION

@pytest.fixture
def orchestrator():
    return get_phase2_orchestrator()

@pytest.fixture
def reasoning_engine():
    return get_phase3_reasoning_engine()

def test_acceptance_comparison_reasoning(orchestrator, reasoning_engine):
    """Compare Education OS with Pharma OS. -> COMPARISON reasoning"""
    async def run_test():
        ctx = orchestrator.orchestrate("p3_sess_01", "Compare Education OS with Pharma OS.", "compare education os with pharma os")
        assert ctx.execution_strategy == ExecutionStrategy.REASONING
        
        result = await reasoning_engine.execute_reasoning(ctx)
        assert result["verified"] is True
        assert "Education OS" in result["text"] or "education_os" in str(result["text"]).lower()
        assert result["metrics"]["reasoning_type"] == "COMPARISON"
        assert result["metrics"]["prompt_version"] == PROMPT_VERSION
    asyncio.run(run_test())

def test_acceptance_consultative_reasoning(orchestrator, reasoning_engine):
    """Which solution is best for a university? -> CONSULTATIVE reasoning"""
    async def run_test():
        ctx = orchestrator.orchestrate("p3_sess_02", "Which solution is best for a university?", "which solution is best for a university")
        assert ctx.execution_strategy in [ExecutionStrategy.CONSULTATIVE, ExecutionStrategy.REASONING, ExecutionStrategy.CATALOG]
        
        result = await reasoning_engine.execute_reasoning(ctx)
        assert result["verified"] is True
        assert result["metrics"]["prompt_version"] == PROMPT_VERSION
    asyncio.run(run_test())

def test_acceptance_integration_reasoning(orchestrator, reasoning_engine):
    """How does Enterprise AI integrate with Data Engineering? -> INTEGRATION reasoning"""
    async def run_test():
        ctx = orchestrator.orchestrate("p3_sess_03", "How does Enterprise AI integrate with Data Engineering?", "how does enterprise ai integrate with data engineering")
        assert ctx.execution_strategy == ExecutionStrategy.REASONING
        
        result = await reasoning_engine.execute_reasoning(ctx)
        assert result["verified"] is True
        assert result["metrics"]["reasoning_type"] == "INTEGRATION"
    asyncio.run(run_test())

def test_acceptance_suitability_reasoning(orchestrator, reasoning_engine):
    """Would Education OS suit a college with 20,000 students? -> SUITABILITY reasoning"""
    async def run_test():
        ctx = orchestrator.orchestrate("p3_sess_04", "Would Education OS suit a college with 20,000 students?", "would education os suit a college with 20,000 students")
        assert ctx.execution_strategy == ExecutionStrategy.REASONING
        
        result = await reasoning_engine.execute_reasoning(ctx)
        assert result["verified"] is True
        assert result["metrics"]["reasoning_type"] == "SUITABILITY"
    asyncio.run(run_test())

def test_acceptance_implementation_reasoning(orchestrator, reasoning_engine):
    """What are the implementation considerations for Smart Cities OS? -> IMPLEMENTATION reasoning"""
    async def run_test():
        ctx = orchestrator.orchestrate("p3_sess_05", "What are the implementation considerations for Smart Cities OS?", "what are the implementation considerations for smart cities os")
        assert ctx.execution_strategy in [ExecutionStrategy.SECTION, ExecutionStrategy.REASONING]
        
        result = await reasoning_engine.execute_reasoning(ctx)
        assert result["verified"] is True
    asyncio.run(run_test())

def test_acceptance_use_case_reasoning(orchestrator, reasoning_engine):
    """How would Pharma OS help a hospital? -> USE_CASE reasoning"""
    async def run_test():
        ctx = orchestrator.orchestrate("p3_sess_06", "How would Pharma OS help a hospital?", "how would pharma os help a hospital")
        
        result = await reasoning_engine.execute_reasoning(ctx)
        assert result["verified"] is True
        assert result["metrics"]["reasoning_type"] == "USE_CASE"
    asyncio.run(run_test())

def test_ungrounded_refusal_handling(orchestrator, reasoning_engine):
    """Verify refusal check on invalid text"""
    async def run_test():
        ctx = orchestrator.orchestrate("p3_sess_07", "Tell me about Education OS", "tell me about education os")
        
        # Test validation on empty or invalid text
        val_res = reasoning_engine.validator.validate("", reasoning_engine.evidence_selector.select_evidence(reasoning_engine.evidence_builder.build_package(ctx), reasoning_engine.reasoning_planner.plan(ctx)))
        assert val_res.is_valid is False
        assert "does not contain enough information" in val_res.fallback_response
    asyncio.run(run_test())
