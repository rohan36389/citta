from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ResponseObject(BaseModel):
    """
    Structured representation of a response before formatting.
    This ensures that the UI layer only renders structured objects, 
    making it agnostic to the source (Deterministic, RAG, LLM).
    """
    type: str = Field(description="The intent or type of response (e.g., overview, workflow, comparison, recommendation)")
    domain: str = Field(description="The business domain (e.g., solution, product, service, technology, company)")
    title: str = Field(description="The primary title of the entity")
    tagline: Optional[str] = Field(default=None, description="A one-line subtitle or tagline")
    
    # Generic sections stored as lists of strings (bullets) or dictionaries
    overview: Optional[List[str]] = Field(default=None)
    best_for: Optional[List[str]] = Field(default=None)
    capabilities: Optional[List[str]] = Field(default=None)
    features: Optional[List[str]] = Field(default=None)
    modules: Optional[List[str]] = Field(default=None)
    services_included: Optional[List[str]] = Field(default=None)
    benefits: Optional[List[str]] = Field(default=None)
    advantages: Optional[List[str]] = Field(default=None)
    technology_stack: Optional[List[str]] = Field(default=None)
    integrations: Optional[List[str]] = Field(default=None)
    industries: Optional[List[str]] = Field(default=None)
    deployment: Optional[List[str]] = Field(default=None)
    used_in: Optional[List[str]] = Field(default=None)
    workflows: Optional[List[Dict[str, Any]]] = Field(default=None)
    faq: Optional[List[Dict[str, Any]]] = Field(default=None)
    contact_info: Optional[Dict[str, str]] = Field(default=None)
    comparison_data: Optional[Dict[str, Any]] = Field(default=None)
    recommendation_data: Optional[Dict[str, Any]] = Field(default=None)
    
    actions: List[str] = Field(default_factory=list, description="List of action button keys (e.g., 'request_demo', 'how_it_works')")
