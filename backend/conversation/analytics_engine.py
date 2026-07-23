import logging
from backend.conversation.models import ConversationContext, ResponseComposition
from backend.conversation.interfaces import IAnalyticsEngine

logger = logging.getLogger(__name__)

class AnalyticsEngine(IAnalyticsEngine):
    """
    Logs pre-sales funnel performance statistics, knowledge gaps, and interaction dropoffs.
    """
    def __init__(self):
        pass

    def track_turn(self, context: ConversationContext, composition: ResponseComposition) -> None:
        """
        Logs successful turn completion.
        """
        logger.info(
            f"Analytics: Session {context.session_id} Turn {context.turn_count} completed. "
            f"Current Stage: {context.current_stage}"
        )

    def track_dropoff(self, session_id: str, stage: str) -> None:
        """
        Logs pre-sales funnel dropoffs.
        """
        logger.warning(f"Analytics Dropoff: Session {session_id} ended at stage {stage}")

def get_analytics_engine() -> IAnalyticsEngine:
    return AnalyticsEngine()
