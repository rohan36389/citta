from backend.presentation.formatters.overview import OverviewFormatter
from backend.presentation.formatters.workflow import WorkflowFormatter
from backend.presentation.formatters.comparison import ComparisonFormatter
from backend.presentation.formatters.recommendation import RecommendationFormatter
from backend.presentation.formatters.faq import FAQFormatter
from backend.presentation.formatters.contact import ContactFormatter

# Optional: You can import placeholder formatters if they have a basic render() method,
# otherwise route them to OverviewFormatter for now until they are implemented.

FORMATTERS = {
    "overview": OverviewFormatter,
    "workflow": WorkflowFormatter,
    "comparison": ComparisonFormatter,
    "recommendation": RecommendationFormatter,
    "faq": FAQFormatter,
    "contact": ContactFormatter,
    # Aliases
    "how_it_works": WorkflowFormatter,
    "workflows": WorkflowFormatter,
    "process": WorkflowFormatter,
    "features": OverviewFormatter,
    "capabilities": OverviewFormatter,
    "benefits": OverviewFormatter,
    "best_for": OverviewFormatter,
    
    # Placeholders map to OverviewFormatter temporarily
    "pricing": OverviewFormatter,
    "architecture": OverviewFormatter,
    "deployment": OverviewFormatter,
    "case_study": OverviewFormatter,
    "timeline": OverviewFormatter,
}
