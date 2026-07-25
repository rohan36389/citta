import pytest
import asyncio
from phase2_orchestrator import get_phase2_orchestrator
from phase6_collaboration_engine import get_phase6_collaboration_engine

@pytest.fixture
def orchestrator():
    return get_phase2_orchestrator()

@pytest.fixture
def collaboration_engine():
    return get_phase6_collaboration_engine()

def test_acceptance_hospital_solution_multi_agent(orchestrator, collaboration_engine):
    """Recommend the best AI solution for a hospital and explain implementation."""
    async def run_test():
        ctx = orchestrator.orchestrate("p6_sess_01", "Recommend the best AI solution for a hospital and explain implementation.", "recommend the best ai solution for a hospital and explain implementation")
        
        result = await collaboration_engine.execute_collaboration_pipeline(ctx)
        assert result["verified"] is True
        assert result["consensus_score"] >= 0.90
        assert "BusinessSolutionsAgent" in result["participating_agents"]
        assert "TechnicalArchitectureAgent" in result["participating_agents"]
        assert "ReviewerAgent" in result["participating_agents"]
    asyncio.run(run_test())

def test_acceptance_comparison_deployment_multi_agent(orchestrator, collaboration_engine):
    """Compare Education OS and Pharma OS with deployment strategy."""
    async def run_test():
        ctx = orchestrator.orchestrate("p6_sess_02", "Compare Education OS and Pharma OS with deployment strategy.", "compare education os and pharma os with deployment strategy")
        
        result = await collaboration_engine.execute_collaboration_pipeline(ctx)
        assert result["verified"] is True
        assert "ResearchAgent" in result["participating_agents"]
        assert "TechnicalArchitectureAgent" in result["participating_agents"]
    asyncio.run(run_test())

def test_acceptance_history_continuation_multi_agent(orchestrator, collaboration_engine):
    """Continue last week's implementation discussion."""
    async def run_test():
        ctx = orchestrator.orchestrate("p6_sess_03", "Continue last week's implementation discussion.", "continue last week's implementation discussion")
        
        result = await collaboration_engine.execute_collaboration_pipeline(ctx)
        assert result["verified"] is True
        assert "MemoryAgent" in result["participating_agents"]
    asyncio.run(run_test())

def test_acceptance_reviewer_conflict_interception(orchestrator, collaboration_engine):
    """Reviewer agent validates findings and produces verified consensus output."""
    async def run_test():
        ctx = orchestrator.orchestrate("p6_sess_04", "Recommend the best AI solution for a hospital and explain implementation.", "recommend the best ai solution for a hospital and explain implementation")
        
        result = await collaboration_engine.execute_collaboration_pipeline(ctx)
        assert result["verified"] is True
        assert "ReviewerAgent" in result["participating_agents"]
        assert len(result["recommendations"]) > 0
    asyncio.run(run_test())

def test_acceptance_agent_timeout_and_failure_isolation(orchestrator, collaboration_engine):
    """Simulated timeout on TechnicalArchitectureAgent -> Fallback executed, remaining agents continue"""
    async def run_test():
        ctx = orchestrator.orchestrate("p6_sess_05", "Recommend the best AI solution for a hospital and explain implementation.", "recommend the best ai solution for a hospital and explain implementation")
        
        result = await collaboration_engine.execute_collaboration_pipeline(ctx, simulate_failure_agent_id="TechnicalArchitectureAgent")
        assert result["verified"] is True
        assert "TechnicalArchitectureAgent" in result["participating_agents"]
        assert result["consensus_score"] > 0.0
    asyncio.run(run_test())
