import logging
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

class KnowledgeType(str, Enum):
    PRODUCT = "product"
    SERVICE = "service"
    SOLUTION = "solution"
    COMPANY = "company"
    CASE_STUDY = "case_study"
    AWARD = "award"
    FAQ = "faq"
    CONTACT = "contact"
    LEADERSHIP = "leadership"
    LOCATION = "location"
    PARTNERS = "partners"
    PRICING = "pricing"

class ClassificationSchema(BaseModel):
    category: str
    industry: str
    domain: str
    subdomain: Optional[str] = None

class MetadataSchema(BaseModel):
    schema_version: str
    content_version: str
    last_updated: str
    source: str
    confidence: float
    language: str

class FAQItemSchema(BaseModel):
    question: str
    answer: str

class WorkflowStepSchema(BaseModel):
    step: int
    title: str
    description: str

class FeatureSchema(BaseModel):
    id: str
    title: str
    description: str
    keywords: List[str] = Field(default_factory=list)

class RelationshipSchema(BaseModel):
    type: str  # e.g., "contains_capability", "recommended_with", "related_service", "belongs_to"
    target: str  # Target ID or slug of related object

class CapabilitySchema(BaseModel):
    id: str
    title: str
    subtitle: str
    description: str
    keywords: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)
    features: List[FeatureSchema] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    relationships: List[RelationshipSchema] = Field(default_factory=list)

class SearchBoostSchema(BaseModel):
    primary_keywords: List[str] = Field(default_factory=list)
    secondary_keywords: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)
    synonyms: List[str] = Field(default_factory=list)

class EnterpriseKnowledgeSchema(BaseModel):
    # Identity
    uuid: UUID
    id: str
    type: KnowledgeType
    slug: str
    name: str
    title: str

    # Presentation
    tagline: str
    overview: str
    description: str
    cta: str
    url: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None

    # Search (Boosting structure)
    search: SearchBoostSchema

    # Classification
    classification: ClassificationSchema

    # Audience
    target_users: List[str] = Field(default_factory=list)

    # Capabilities
    capabilities: List[CapabilitySchema] = Field(default_factory=list)

    # Workflows
    workflows: List[WorkflowStepSchema] = Field(default_factory=list)

    # Benefits
    benefits: List[str] = Field(default_factory=list)

    # Use Cases
    use_cases: List[str] = Field(default_factory=list)

    # FAQ
    faq: List[FAQItemSchema] = Field(default_factory=list)

    # Leadership Members
    members: List[Dict[str, Any]] = Field(default_factory=list)

    # Related / Graph Relationships
    relationships: List[RelationshipSchema] = Field(default_factory=list)

    # Metadata
    metadata: MetadataSchema

def validate_object(data: Dict[str, Any], filename: str = "Unknown") -> EnterpriseKnowledgeSchema:
    """Validates raw dict against Pydantic schema."""
    try:
        obj = EnterpriseKnowledgeSchema(**data)
        # Content Quality Check: duplicate keywords check
        all_kw = []
        all_kw.extend(obj.search.primary_keywords)
        all_kw.extend(obj.search.secondary_keywords)
        
        seen_kw = set()
        duplicates = [k for k in all_kw if k.lower() in seen_kw or seen_kw.add(k.lower())]
        if duplicates:
            logger.warning(f"Quality Check Warning in '{filename}': Duplicate keywords found: {duplicates}")
            
        return obj
    except ValidationError as e:
        logger.error(f"Schema validation failed for '{filename}':\n{e}")
        raise ValueError(f"File '{filename}' failed schema validation: {e}")

def validate_global_registry(objects: List[EnterpriseKnowledgeSchema]):
    """Enforces global referential integrity and uniqueness rules across all objects."""
    seen_ids = set()
    seen_slugs = set()
    seen_capabilities = set()
    
    # Pass 1: Collect IDs and Slugs
    for obj in objects:
        if obj.id in seen_ids:
            raise ValueError(f"Quality Check Failed: Duplicate global object ID found: '{obj.id}'")
        seen_ids.add(obj.id)
        
        if obj.slug in seen_slugs:
            raise ValueError(f"Quality Check Failed: Duplicate global slug found: '{obj.slug}'")
        seen_slugs.add(obj.slug)
        
        # Verify uniqueness of capabilities
        for cap in obj.capabilities:
            if cap.id in seen_capabilities:
                raise ValueError(f"Quality Check Failed: Duplicate capability ID found: '{cap.id}' (across multiple products/solutions)")
            seen_capabilities.add(cap.id)
            
    # Pass 2: Verify relationships and targets
    for obj in objects:
        # Check object relationship targets
        for rel in obj.relationships:
            if rel.target not in seen_ids and rel.target not in seen_slugs:
                raise ValueError(f"Quality Check Failed: Object '{obj.id}' references non-existent target: '{rel.target}' in relationships")
                
        # Check capability relationship targets
        for cap in obj.capabilities:
            for rel in cap.relationships:
                if rel.target not in seen_ids and rel.target not in seen_slugs and rel.target not in seen_capabilities:
                    raise ValueError(f"Quality Check Failed: Capability '{cap.id}' in '{obj.id}' references non-existent target: '{rel.target}'")
                    
    logger.info("Global registry quality validation completed successfully. All references verified.")
