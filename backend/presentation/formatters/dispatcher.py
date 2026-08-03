from presentation.models.response_object import ResponseObject
from presentation.validators.response_validator import ResponseValidator
from presentation.config.formatter_registry import FORMATTERS

class ResponseFormatterDispatcher:
    
    @staticmethod
    def dispatch(response_obj: ResponseObject) -> str:
        """
        Validates the ResponseObject, routes it to the appropriate formatter based on intent type, 
        and returns the final rendered markdown.
        """
        # Validate and sanitize data
        validated_obj = ResponseValidator.validate(response_obj)
        
        # Get formatter based on type
        intent_type = validated_obj.type.lower()
        formatter_cls = FORMATTERS.get(intent_type, FORMATTERS["overview"])
        
        # Render
        return formatter_cls.render(validated_obj)
