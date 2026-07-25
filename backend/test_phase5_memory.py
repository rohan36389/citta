import time
import pytest
from phase5_memory_engine import get_phase5_memory_engine
from memory_manager import get_memory_manager
from memory_resolver import get_memory_resolver
from memory_store import get_memory_store, EnterpriseMemory, MemoryProvenance

@pytest.fixture
def memory_engine():
    return get_phase5_memory_engine()

@pytest.fixture
def memory_manager():
    return get_memory_manager()

@pytest.fixture
def memory_resolver():
    return get_memory_resolver()

def test_preference_memory_storage_and_provenance(memory_engine, memory_manager):
    """User: 'I always prefer PDF reports.' -> Preference stored with provenance"""
    mem = memory_engine.record_user_preference("I always prefer PDF reports.", user_id="user_john", organization_id="acme_corp")
    assert mem is not None
    assert mem.type == "PREFERENCE"
    assert "PDF" in mem.content
    assert mem.provenance.source_type == "MANUAL_USER_INPUT"

def test_preference_memory_retrieval(memory_engine, memory_resolver):
    """User: 'What report format do I prefer?' -> Memory retrieved"""
    # Prime memory
    memory_engine.record_user_preference("I always prefer PDF reports.", user_id="user_john", organization_id="acme_corp")
    
    resolved = memory_resolver.resolve_relevant_memories(user_id="user_john", organization_id="acme_corp", user_role="sales_agent")
    assert len(resolved) >= 1
    pref_mems = [m for m in resolved if m.type == "PREFERENCE"]
    assert len(pref_mems) >= 1
    assert "PDF" in str(pref_mems[0].content)

def test_memory_policy_filter_ephemeral(memory_manager):
    """Temporary ephemeral remark -> Discarded by MemoryPolicyEngine"""
    mem = memory_manager.create_memory(
        content="My meeting starts in 5 mins right now",
        owner_user_id="user_john",
        organization_id="acme_corp",
        memory_type="CONVERSATION"
    )
    assert mem is None  # Ephemeral policy filter discarded it

def test_memory_confidence_decay():
    """Decay calculation reduces confidence dynamically over time based on half-life formula"""
    prov = MemoryProvenance(source_type="CONVERSATION", source_id="src_decay")
    now_ms = time.time() * 1000.0
    ninety_days_ago_ms = now_ms - (90 * 86400.0 * 1000.0)

    mem = EnterpriseMemory(
        memory_id="mem_decay_test",
        type="WORKFLOW",
        owner_user_id="user_john",
        organization_id="acme_corp",
        content="Executed workflow 90 days ago",
        initial_confidence=1.0,
        half_life_days=180.0,
        provenance=prov,
        created_at_ms=ninety_days_ago_ms,
        updated_at_ms=ninety_days_ago_ms
    )

    decayed = mem.get_decayed_confidence(now_ms)
    assert 0.65 <= decayed <= 0.75  # ~0.71 after 90 days on 180-day half-life

def test_memory_version_history(memory_manager):
    """User updating preference (PDF -> Markdown) -> Old version saved in version_history"""
    # 1. Initial preference
    mem1 = memory_manager.create_memory("I prefer PDF report format.", owner_user_id="user_sarah", organization_id="acme_corp", memory_type="PREFERENCE")
    assert mem1 is not None

    # 2. Updated preference (conflicting)
    mem2 = memory_manager.create_memory("I prefer Markdown report format.", owner_user_id="user_sarah", organization_id="acme_corp", memory_type="PREFERENCE")
    assert mem2 is not None
    assert mem2.memory_id == mem1.memory_id  # Same memory record updated
    assert "Markdown" in mem2.content
    assert len(mem2.version_history) >= 1
    assert "PDF" in str(mem2.version_history[0].content)

def test_permission_engine_guard(memory_manager, memory_resolver):
    """Restricted employee requesting admin memory -> Permission denied"""
    admin_mem = memory_manager.create_memory(
        content="Sensitive Admin Security Protocol",
        owner_user_id="user_admin",
        organization_id="acme_corp",
        visibility="ADMIN_ONLY",
        memory_type="ORG"
    )
    assert admin_mem is not None

    # Restricted user attempts retrieval
    resolved = memory_resolver.resolve_relevant_memories(
        user_id="user_restricted",
        organization_id="acme_corp",
        user_role="restricted_user"
    )
    assert not any(m.memory_id == admin_mem.memory_id for m in resolved)

def test_phase4_workflow_outcome_persistence(memory_engine, memory_resolver):
    """Completed workflow outcome -> Recorded in enterprise memory"""
    mem = memory_engine.record_workflow_outcome("Schedule Demo", "Calendar Event Scheduled (evt_99) + CRM Lead Created (lead_12)", user_id="user_john", organization_id="acme_corp")
    assert mem is not None
    assert mem.type == "ACTION"
    assert "Schedule Demo" in mem.content
