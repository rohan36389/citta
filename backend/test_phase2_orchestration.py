import pytest
from orchestration_context import ExecutionStrategy, EnterpriseIntent
from phase2_orchestrator import get_phase2_orchestrator

@pytest.fixture
def orchestrator():
    return get_phase2_orchestrator()

def test_acceptance_catalog_strategy(orchestrator):
    """Tell me about Education OS -> CATALOG"""
    ctx = orchestrator.orchestrate("sess_01", "Tell me about Education OS.", "tell me about education os")
    assert ctx.execution_strategy == ExecutionStrategy.CATALOG
    assert ctx.resolved_entity_id == "education_os"
    assert ctx.requires_llm is False
    assert any(trace["stage"] == "ExecutionStrategySelector" for trace in ctx.decision_trace)

def test_acceptance_section_workflow_strategy(orchestrator):
    """How does Education OS work? -> SECTION (workflow)"""
    ctx = orchestrator.orchestrate("sess_02", "How does Education OS work?", "how does education os work")
    assert ctx.execution_strategy == ExecutionStrategy.SECTION
    assert ctx.resolved_entity_id == "education_os"
    assert ctx.intent == EnterpriseIntent.WORKFLOW.value
    assert ctx.requires_llm is False

def test_acceptance_section_benefits_strategy(orchestrator):
    """Benefits of Education OS. -> SECTION (benefits)"""
    ctx = orchestrator.orchestrate("sess_03", "Benefits of Education OS.", "benefits of education os")
    assert ctx.execution_strategy == ExecutionStrategy.SECTION
    assert ctx.resolved_entity_id == "education_os"
    assert ctx.intent == EnterpriseIntent.BENEFITS.value
    assert ctx.requires_llm is False

def test_acceptance_section_pricing_strategy(orchestrator):
    """Pricing. -> SECTION (pricing)"""
    # Prime active context
    orchestrator.orchestrate("sess_04", "Tell me about Education OS.", "tell me about education os")
    # Follow-up standalone pricing query
    ctx = orchestrator.orchestrate("sess_04", "Pricing.", "pricing")
    assert ctx.execution_strategy == ExecutionStrategy.SECTION
    assert ctx.resolved_entity_id == "education_os"
    assert ctx.intent == EnterpriseIntent.PRICING.value
    assert ctx.requires_llm is False

def test_acceptance_reasoning_comparison_strategy(orchestrator):
    """Compare Education OS with Pharma OS. -> REASONING"""
    ctx = orchestrator.orchestrate("sess_05", "Compare Education OS with Pharma OS.", "compare education os with pharma os")
    assert ctx.execution_strategy == ExecutionStrategy.REASONING
    assert ctx.intent == EnterpriseIntent.COMPARISON.value
    assert ctx.requires_llm is True

def test_acceptance_reasoning_suitability_strategy(orchestrator):
    """Why is Education OS better than traditional LMS? -> REASONING"""
    ctx = orchestrator.orchestrate("sess_06", "Why is Education OS better than traditional LMS?", "why is education os better than traditional lms")
    assert ctx.execution_strategy == ExecutionStrategy.REASONING
    assert ctx.requires_llm is True

def test_acceptance_consultative_recommendation_strategy(orchestrator):
    """We're a university with 10,000 students. Which solution should we choose? -> CONSULTATIVE"""
    query = "We're a university with 10,000 students. Which solution should we choose?"
    ctx = orchestrator.orchestrate("sess_07", query, query.lower())
    assert ctx.execution_strategy == ExecutionStrategy.CONSULTATIVE
    assert ctx.requires_llm is True

def test_acceptance_out_of_domain(orchestrator):
    """Who won yesterday's cricket match? -> OUT_OF_DOMAIN"""
    ctx = orchestrator.orchestrate("sess_08", "Who won yesterday's cricket match?", "who won yesterday's cricket match")
    assert ctx.execution_strategy == ExecutionStrategy.OUT_OF_DOMAIN
    assert ctx.is_out_of_domain is True
    assert ctx.requires_llm is False

def test_general_catalog_query_routing(orchestrator):
    """What solutions do you offer? -> CATALOG (General in-domain catalog list)"""
    ctx = orchestrator.orchestrate("sess_09", "What solutions do you offer?", "what solutions do you offer")
    assert ctx.execution_strategy == ExecutionStrategy.CATALOG
    assert ctx.is_general_catalog_query is True
    assert ctx.is_out_of_domain is False

def test_ambiguity_detection(orchestrator):
    """Tell me about marketing -> AMBIGUOUS"""
    ctx = orchestrator.orchestrate("sess_10", "Tell me about marketing", "tell me about marketing")
    assert ctx.is_ambiguous is True
    assert len(ctx.matched_entity_ids) > 1

def test_unknown_entity_handling(orchestrator):
    """Tell me about Finance OS -> UNKNOWN ENTITY"""
    ctx = orchestrator.orchestrate("sess_11", "Tell me about Finance OS", "tell me about finance os")
    assert ctx.is_unknown_entity is True
    assert ctx.unknown_entity_name == "Finance Os"
