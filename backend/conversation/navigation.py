import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

class NavigationController:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NavigationController, cls).__new__(cls)
        return cls._instance

    def process_navigation(
        self,
        navigation_intent: bool,
        target_url: Optional[str],
        entity_name: Optional[str] = None,
        entity_type: Optional[str] = None,
        is_public: bool = True
    ) -> Tuple[Optional[str], List[Dict[str, str]]]:
        """
        Enforces strict UX Navigation rule:
        - `redirect` URL is set ONLY if navigation_intent is True AND target_url exists AND is_public is True.
        - Otherwise returns redirect = None and returns contextual action choices for the user.
        """
        if navigation_intent and target_url and is_public:
            logger.info(f"Explicit navigation requested for '{entity_name or target_url}'. Populating redirect.")
            return target_url, []
            
        # Contextual Action Suggestions (when non-redirecting)
        action_choices = []
        etype = (entity_type or "").upper()
        
        if etype in ["PRODUCT", "PRODUCTS"]:
            action_choices = [
                {"label": "Learn More", "action": "learn_more"},
                {"label": f"Visit {entity_name or 'Product'} Page", "action": "visit_page", "url": target_url or "/products"},
                {"label": "Contact Sales", "action": "contact_sales", "url": "/contact"}
            ]
        elif etype in ["SOLUTION", "SOLUTIONS"]:
            action_choices = [
                {"label": "Learn More", "action": "learn_more"},
                {"label": f"View {entity_name or 'Solution'}", "action": "visit_page", "url": target_url or "/solutions"},
                {"label": "Request Demo", "action": "request_demo", "url": "/contact"}
            ]
        elif etype in ["CASE_STUDY", "CASE_STUDIES"]:
            action_choices = [
                {"label": "Business Outcome", "action": "view_outcome"},
                {"label": "Technologies Used", "action": "view_tech"},
                {"label": "Visit Full Case Study", "action": "visit_page", "url": target_url or "/case-studies"}
            ]
        elif etype in ["COMPANY", "COMPANY_INFO", "LEADERSHIP", "RECOGNITION"]:
            action_choices = [
                {"label": "Leadership Team", "action": "view_leadership"},
                {"label": "Awards & Recognitions", "action": "view_awards"},
                {"label": "Contact Us", "action": "contact_sales", "url": "/contact"}
            ]
        else:
            if entity_name:
                action_choices.append({"label": "Learn More", "action": "learn_more"})
                if target_url:
                    action_choices.append({"label": f"Visit {entity_name} Page", "action": "visit_page", "url": target_url})
            action_choices.append({"label": "Contact Sales", "action": "contact_sales", "url": "/contact"})
        
        return None, action_choices

def get_navigation_controller() -> NavigationController:
    return NavigationController()
