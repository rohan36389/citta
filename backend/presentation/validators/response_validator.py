from typing import List, Dict, Any, Optional
from presentation.models.response_object import ResponseObject

class ResponseValidator:
    """
    Validates and sanitizes a ResponseObject before it is passed to the renderer.
    Enforces presentation rules like max bullets, deduplication, and removing empty sections.
    """
    
    @staticmethod
    def validate(response_obj: ResponseObject) -> ResponseObject:
        """
        Validates all fields in the ResponseObject and returns the sanitized object.
        """
        # We need to sanitize any list of strings field
        list_fields = [
            'overview', 'best_for', 'capabilities', 'features', 'modules', 
            'services_included', 'benefits', 'advantages', 'technology_stack', 
            'integrations', 'industries', 'deployment', 'used_in'
        ]
        
        for field in list_fields:
            val = getattr(response_obj, field)
            if val is not None:
                sanitized_val = ResponseValidator._sanitize_list(val)
                setattr(response_obj, field, sanitized_val)
                
        # Validate actions
        if response_obj.actions:
            # deduplicate while maintaining order
            seen = set()
            new_actions = []
            for action in response_obj.actions:
                if action not in seen:
                    new_actions.append(action)
                    seen.add(action)
            response_obj.actions = new_actions
            
        return response_obj
        
    @staticmethod
    def _sanitize_list(items: List[str], max_items: int = 5) -> Optional[List[str]]:
        if not items:
            return None
            
        sanitized = []
        seen = set()
        for item in items:
            if not isinstance(item, str):
                item = str(item)
            item = item.strip()
            
            # Skip empty, "None", or null-like values
            if not item or item.lower() in ["none", "null", "n/a", "-"]:
                continue
                
            # Deduplicate
            lower_val = item.lower()
            if lower_val not in seen:
                sanitized.append(item)
                seen.add(lower_val)
                
            if len(sanitized) >= max_items:
                break
                
        return sanitized if sanitized else None
