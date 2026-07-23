import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import logging

try:
    from backend.conversation.interfaces import (
        IContextEngine,
        IUnderstandingEngine,
        IKnowledgeEngine,
        IStrategyEngine,
        IPromptEngine,
        IResponseEngine,
        IQualityEngine,
        IAnalyticsEngine,
        IMemoryStore
    )
    from backend.conversation.memory_store import get_memory_store
    from backend.conversation.context_engine import get_context_engine
    from backend.conversation.understanding_engine import get_understanding_engine
    from backend.conversation.knowledge_engine import get_knowledge_engine
    from backend.conversation.strategy_engine import get_strategy_engine
    from backend.conversation.prompt_engine import get_prompt_engine
    from backend.conversation.response_engine import get_response_engine
    from backend.conversation.quality_engine import get_quality_engine
    from backend.conversation.analytics_engine import get_analytics_engine
    from backend.conversation.manager import ConversationManager
except ImportError:
    from conversation.interfaces import (
        IContextEngine,
        IUnderstandingEngine,
        IKnowledgeEngine,
        IStrategyEngine,
        IPromptEngine,
        IResponseEngine,
        IQualityEngine,
        IAnalyticsEngine,
        IMemoryStore
    )
    from conversation.memory_store import get_memory_store
    from conversation.context_engine import get_context_engine
    from conversation.understanding_engine import get_understanding_engine
    from conversation.knowledge_engine import get_knowledge_engine
    from conversation.strategy_engine import get_strategy_engine
    from conversation.prompt_engine import get_prompt_engine
    from conversation.response_engine import get_response_engine
    from conversation.quality_engine import get_quality_engine
    from conversation.analytics_engine import get_analytics_engine
    from conversation.manager import ConversationManager

logger = logging.getLogger(__name__)

_manager_instance: ConversationManager = None

def get_conversation_manager() -> ConversationManager:
    """
    Singleton factory helper to retrieve or construct the fully cohesive ConversationManager.
    """
    global _manager_instance
    if _manager_instance is None:
        logger.info("Initializing Pre-Sales Conversation Platform Pipeline Orchestrator...")
        mem_store = get_memory_store()
        ctx_eng = get_context_engine(mem_store)
        und_eng = get_understanding_engine()
        kn_eng = get_knowledge_engine()
        strat_eng = get_strategy_engine()
        pr_eng = get_prompt_engine()
        resp_eng = get_response_engine()
        qual_eng = get_quality_engine()
        an_eng = get_analytics_engine()
        
        _manager_instance = ConversationManager(
            context_engine=ctx_eng,
            understanding_engine=und_eng,
            knowledge_engine=kn_eng,
            strategy_engine=strat_eng,
            prompt_engine=pr_eng,
            response_engine=resp_eng,
            quality_engine=qual_eng,
            analytics_engine=an_eng
        )
    return _manager_instance
