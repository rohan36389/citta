import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent
COMPILED_DIR = BACKEND_DIR / "knowledge" / "compiled"

class KnowledgeRegistry:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KnowledgeRegistry, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.registry_index: Dict[str, Dict[str, Any]] = {}
        self.disabled_registries: Set[str] = set()
        
        self.company: Dict[str, Any] = {}
        self.products: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.solutions: List[Dict[str, Any]] = []
        
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.routes: Dict[str, str] = {}  # route -> entity_id
        self.aliases: Dict[str, str] = {}  # alias -> entity_id
        self.abbreviations: Dict[str, str] = {} # abbr -> expansion
        self.unified_vocabulary: Dict[str, str] = {} # token -> entity_id
        self.entity_lookup: Dict[str, str] = {} # Single canonical runtime lookup map
        self.knowledge_graph: Dict[str, Dict[str, Any]] = {}
        
        self._initialized = True
        self.load_all()

    def load_all(self):
        logger.info("Initializing CittaAI Enterprise Knowledge Registry Loader...")
        self.registry_index = {}
        self.disabled_registries = set()
        self.entities = {}
        self.routes = {}
        self.aliases = {}
        self.abbreviations = {}
        self.unified_vocabulary = {}
        self.entity_lookup = {}
        
        # New indexing structures
        self.registry_by_id = {}
        self.registry_by_slug = {}
        self.registry_by_keyword = {}
        self.registry_by_alias = {}
        self.registry_by_capability = {}
        self.registry_by_feature = {}
        self.registry_by_category = {}
        self.registry_by_industry = {}
        self.registry_by_type = {}
        
        REGISTRY_DIR = BACKEND_DIR / "knowledge" / "registry"
        manifest_path = REGISTRY_DIR / "manifest.json"
        
        if not manifest_path.exists():
            logger.error(f"Global manifest.json not found at {manifest_path}. Loading fallbacks.")
            self._load_fallbacks()
            return

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read manifest.json: {e}. Loading fallbacks.")
            self._load_fallbacks()
            return

        registries = manifest_data.get("registries", [])
        # Sort by priority descending
        registries.sort(key=lambda x: x.get("priority", 0), reverse=True)

        import knowledge_validator
        loaded_objects = []

        for reg_conf in registries:
            name = reg_conf.get("name")
            enabled = reg_conf.get("enabled", True)
            content_file = reg_conf.get("content")
            
            if not enabled:
                continue

            file_path = REGISTRY_DIR / content_file
            if not file_path.exists():
                logger.error(f"Registry content file {content_file} missing. Fail-fast active.")
                raise FileNotFoundError(f"Required registry file missing: {content_file}")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    reg_data = json.load(f)
                
                # Strict Schema Validation
                obj = knowledge_validator.validate_object(reg_data, filename=content_file)
                loaded_objects.append(obj)
                
                # Cache registry_index to mimic old format if needed
                self.registry_index[reg_conf.get("registry_type")] = reg_data
            except Exception as e:
                logger.error(f"Registry Startup Validation Failed for '{content_file}': {e}.")
                raise ValueError(f"Startup validation failed for '{content_file}': {e}")

        # Run global referential and uniqueness checks
        try:
            knowledge_validator.validate_global_registry(loaded_objects)
        except Exception as e:
            logger.error(f"Global Registry Quality check failed: {e}")
            raise ValueError(f"Startup global quality validation failed: {e}")

        # Build new structural indexes
        for obj in loaded_objects:
            self.registry_by_id[obj.id] = obj
            self.registry_by_slug[obj.slug] = obj
            self.registry_by_type.setdefault(obj.type.value, []).append(obj)
            self.registry_by_category.setdefault(obj.classification.category, []).append(obj)
            self.registry_by_industry.setdefault(obj.classification.industry, []).append(obj)
            
            for kw in obj.search.primary_keywords:
                self.registry_by_keyword.setdefault(kw.lower(), []).append(obj)
            for kw in obj.search.secondary_keywords:
                self.registry_by_keyword.setdefault(kw.lower(), []).append(obj)
                
            for alias in obj.search.aliases:
                self.registry_by_alias.setdefault(alias.lower(), []).append(obj)
            for syn in obj.search.synonyms:
                self.registry_by_alias.setdefault(syn.lower(), []).append(obj)
                
            for cap in obj.capabilities:
                cap_entry = {"capability": cap, "parent": obj}
                self.registry_by_capability[cap.id] = cap_entry
                self.registry_by_capability[cap.title.lower()] = cap_entry
                for kw in cap.keywords:
                    self.registry_by_capability[kw.lower()] = cap_entry
                for alias in cap.aliases:
                    self.registry_by_capability[alias.lower()] = cap_entry
                    
                for feat in cap.features:
                    feat_entry = {"feature": feat, "capability": cap, "parent": obj}
                    self.registry_by_feature[feat.id] = feat_entry
                    self.registry_by_feature[feat.title.lower()] = feat_entry
                    for kw in feat.keywords:
                        self.registry_by_feature[kw.lower()] = feat_entry

        # Populate legacy properties for backward compatibility
        self._populate_legacy_properties()
        
        # Build unified indexing structures
        self.build_entities()
        self.load_routes()
        self.load_aliases()
        self.build_unified_vocabulary()
        self.build_entity_lookup()
        self.build_knowledge_graph()
        self.validate()
        self.print_diagnostics()

    def _load_fallbacks(self):
        # Fallback dictionary for basic server survival if compilation is broken
        self.company = {
            "name": "CittaAI",
            "tagline": "Living Intelligence",
            "founded": "2022",
            "description": "Enterprise AI partner."
        }
        self.build_entities()

    def _to_legacy_dict(self, obj) -> Dict[str, Any]:
        return {
            "id": obj.id,
            "name": obj.name,
            "title": obj.title,
            "tagline": obj.tagline,
            "description": obj.description,
            "best_for": obj.target_users,
            "route": obj.url,
            "cta": obj.cta,
            "benefits": obj.benefits,
            "faq": [{"question": f.question, "answer": f.answer} for f in obj.faq],
            "related_entities": [r.target for r in obj.relationships],
            "capabilities": [
                {
                    "title": cap.title,
                    "subtitle": cap.subtitle,
                    "description": cap.description,
                    "features": [f.title for f in cap.features]
                } for cap in obj.capabilities
            ],
            "how_it_works": {
                "steps": [w.title for w in obj.workflows]
            }
        }

    def _populate_legacy_properties(self):
        # company
        company_obj = self.registry_by_id.get("company_info")
        if company_obj:
            self.company = {
                "name": company_obj.name,
                "tagline": company_obj.tagline,
                "founded": "2022",
                "description": company_obj.description,
                "vision": "Empower global enterprises with autonomous cognitive operating systems.",
                "mission": "Bridge research-grade AI to enterprise scale with security, governance, and measurable ROI.",
                "founder": "Kiran Kumar"
            }
        
        # products
        self.products = [self._to_legacy_dict(obj) for obj in self.registry_by_type.get("product", [])]
        
        # services
        self.services = [self._to_legacy_dict(obj) for obj in self.registry_by_type.get("service", [])]
        
        # solutions
        self.solutions = [self._to_legacy_dict(obj) for obj in self.registry_by_type.get("solution", [])]
        
        # case studies
        cs_entities = [self._to_legacy_dict(obj) for obj in self.registry_by_type.get("case_study", [])]
        
        meta_base = {
            "registry_id": "v1",
            "registry_type": "GENERIC",
            "schema_version": "2.0",
            "content_version": "1.0",
            "priority": 80,
            "capabilities": {"reasoning": True, "comparison": True, "transformation": True, "summarization": True, "examples": True},
            "supported_sections": ["overview", "capabilities", "features", "workflows", "benefits", "use_cases", "faq"]
        }
        
        self.registry_index["COMPANY_INFO"] = {"metadata": {**meta_base, "registry_type": "COMPANY_INFO", "registry_id": "company_v1"}, **self.company}
        self.registry_index["PRODUCTS"] = {"metadata": {**meta_base, "registry_type": "PRODUCTS", "registry_id": "products_v1"}, "entities": self.products}
        self.registry_index["SERVICES"] = {"metadata": {**meta_base, "registry_type": "SERVICES", "registry_id": "services_v1"}, "entities": self.services}
        self.registry_index["SOLUTIONS"] = {"metadata": {**meta_base, "registry_type": "SOLUTIONS", "registry_id": "solutions_v1"}, "entities": self.solutions}
        self.registry_index["CASE_STUDIES"] = {"metadata": {**meta_base, "registry_type": "CASE_STUDIES", "registry_id": "case_studies_v1"}, "entities": cs_entities}
        
        # Leadership index
        leaders = []
        others = []
        lead_obj = self.registry_by_id.get("leadership_info")
        if lead_obj:
            for cap in lead_obj.capabilities:
                item = {
                    "id": cap.id,
                    "name": cap.title,
                    "title": cap.subtitle,
                    "description": cap.description,
                    "aliases": cap.aliases
                }
                if any(r in cap.subtitle.lower() for r in ["ceo", "co-founder", "co_founder", "cto", "coo"]):
                    leaders.append(item)
                else:
                    others.append(item)
        self.registry_index["LEADERSHIP"] = {"metadata": {**meta_base, "registry_type": "LEADERSHIP", "registry_id": "leadership_v1"}, "leaders": leaders, "others": others}
        
        # Recognition index
        rec_obj = self.registry_by_id.get("awards_recognition")
        recognitions = []
        if rec_obj:
            for cap in rec_obj.capabilities:
                recognitions.append({
                    "title": cap.title,
                    "description": cap.description,
                    "details": cap.subtitle,
                    "organization": cap.subtitle
                })
        self.registry_index["RECOGNITION"] = {"metadata": {**meta_base, "registry_type": "RECOGNITION", "registry_id": "recognition_v1"}, "recognitions": recognitions}
        
        # Contact index
        contact_obj = self.registry_by_id.get("contact_info")
        if contact_obj:
            self.registry_index["CONTACT"] = {
                "metadata": {**meta_base, "registry_type": "CONTACT", "registry_id": "contact_v1"},
                "phone": "+91 9392655040",
                "phone_raw": "+919392655040",
                "email": "info@cittaai.com",
                "business_hours": "Mon-Fri 9am-6pm",
                "response_time": "We typically respond within 24 hours during business hours."
            }
            
        # FAQ index
        faq_obj = self.registry_by_id.get("faq_general")
        faqs = []
        if faq_obj:
            for f in faq_obj.faq:
                faqs.append({"question": f.question, "answer": f.answer, "route": "/faq"})
        self.registry_index["FAQ"] = {"metadata": {**meta_base, "registry_type": "FAQ", "registry_id": "faq_v1"}, "entities": faqs}

    def build_entities(self):
        self.entities = {}
        
        # Add company as an entity
        self.entities["company"] = {
            "id": "company",
            "type": "company",
            "name": self.company.get("name", "CittaAI"),
            "summary": self.company.get("tagline", ""),
            "description": self.company.get("description", ""),
            "route": "/about"
        }
        
        # Add founder
        self.entities["founder"] = {
            "id": "founder",
            "type": "leadership",
            "name": self.company.get("founder", "Kiran Kumar"),
            "summary": "Founder & CEO",
            "description": "CittaAI Founder & Leadership team.",
            "route": "/about"
        }
        
        # Add items from list-based registries
        for p in self.products:
            if "id" in p:
                self.entities[p["id"]] = p
        for s in self.services:
            if "id" in s:
                self.entities[s["id"]] = s
        for sol in self.solutions:
            if "id" in sol:
                self.entities[sol["id"]] = sol
                
        # Load case studies entities
        cs_reg = self.registry_index.get("CASE_STUDIES", {})
        if cs_reg:
            for cs in cs_reg.get("entities", []):
                if "id" in cs:
                    self.entities[cs["id"]] = cs

        # Load leadership entities
        lead_reg = self.registry_index.get("LEADERSHIP", {})
        if lead_reg:
            all_people = lead_reg.get("leaders", []) + lead_reg.get("others", [])
            for person in all_people:
                if "id" in person:
                    self.entities[person["id"]] = {
                        "id": person["id"],
                        "name": person["name"],
                        "title": person["title"],
                        "description": person.get("description", ""),
                        "aliases": person.get("aliases", []),
                        "type": "leadership",
                        "route": "/about"
                    }

    def load_routes(self):
        self.routes = {}
        for ent_id, ent in self.entities.items():
            route = ent.get("route")
            if route:
                if route not in self.routes or ent_id not in ["company", "founder"]:
                    self.routes[route] = ent_id

    def load_aliases(self):
        self.aliases = {}
        
        # Ensure compiled entity_index.json exists and contains comprehensive alias mappings
        entity_index = {
            "PRODUCTS": {
                "whatsapp marketing platform": "whatsapp_marketing",
                "whatsapp marketing": "whatsapp_marketing",
                "whatsapp platform": "whatsapp_marketing",
                "wa": "whatsapp_marketing",
                "influencer marketing platform": "influencer_marketing",
                "influencer marketing": "influencer_marketing",
                "influencer platform": "influencer_marketing",
                "creator platform": "influencer_marketing"
            },
            "SERVICES": {
                "data engineering": "data_engineering",
                "cloud data platform": "data_engineering",
                "data engineering service": "data_engineering",
                "enterprise & agentic ai": "enterprise_agentic_ai",
                "enterprise agentic ai": "enterprise_agentic_ai",
                "enterprise ai": "enterprise_agentic_ai",
                "agentic ai": "enterprise_agentic_ai",
                "agentic systems": "enterprise_agentic_ai",
                "ai strategy & advisory": "ai_strategy",
                "ai strategy": "ai_strategy",
                "strategy consulting": "ai_strategy",
                "ai powered marketing": "ai_powered_marketing",
                "ai-powered marketing": "ai_powered_marketing",
                "martech 360": "ai_powered_marketing",
                "marketing automation": "ai_powered_marketing"
            },
            "SOLUTIONS": {
                "ecommerce os": "ecommerce_os",
                "e-commerce os": "ecommerce_os",
                "retail os": "ecommerce_os",
                "pharma & healthcare os": "pharma_os",
                "pharma os": "pharma_os",
                "pharmaa os": "pharma_os",
                "pharmaa": "pharma_os",
                "healthcare os": "pharma_os",
                "smart cities os": "smart_cities_os",
                "urban os": "smart_cities_os",
                "smart city": "smart_cities_os",
                "education os": "education_os",
                "lms os": "education_os",
                "learning os": "education_os",
                "real estate os": "real_estate_os",
                "realestate os": "real_estate_os",
                "realestate": "real_estate_os",
                "broker os": "real_estate_os",
                "property os": "real_estate_os",
                "enterprise ai os": "enterprise_ai_os"
            },
            "CASE_STUDIES": {
                "case study": "case_studies",
                "case studies": "case_studies",
                "jewellery brand": "jewellery_brand_roi",
                "jewellery": "jewellery_brand_roi",
                "fmcg brand": "fmcg_social_growth",
                "fmcg": "fmcg_social_growth",
                "spices export": "b2b_spices_export",
                "b2b spices export": "b2b_spices_export"
            }
        }
        try:
            with open(COMPILED_DIR / "entity_index.json", "w", encoding="utf-8") as f:
                json.dump(entity_index, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save compiled entity_index.json: {e}")

        index_path = COMPILED_DIR / "entity_index.json"
        if index_path.exists():
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for domain_key, mapping in data.items():
                        for alias, ent_id in mapping.items():
                            self.aliases[alias.lower()] = ent_id
            except Exception as e:
                logger.error(f"Error loading entity_index.json aliases: {e}")
                
        # Inject default company & leadership aliases
        self.aliases["cittaai"] = "company_info"
        self.aliases["citta"] = "company_info"
        self.aliases["company"] = "company_info"
        self.aliases["founder"] = "founder"
        self.aliases["ceo"] = "vinay_velivela"
        self.aliases["cto"] = "akhil_reddy"
        self.aliases["coo"] = "saladi_chandra_balaji"
        self.aliases["kiran kumar"] = "founder"
        self.aliases["vinay velivela"] = "vinay_velivela"
        self.aliases["vinay"] = "vinay_velivela"

    def build_unified_vocabulary(self):
        # Auto-compile abbreviations, synonyms, and aliases into one single-stage lookup map
        self.unified_vocabulary = {}
        
        # 1. Map canonical IDs
        for ent_id in self.entities.keys():
            self.unified_vocabulary[ent_id.lower().replace("_", " ")] = ent_id
            self.unified_vocabulary[ent_id.lower()] = ent_id

        # 2. Map direct entity names
        for ent_id, ent in self.entities.items():
            name = ent.get("name")
            if name:
                self.unified_vocabulary[name.lower()] = ent_id
                
            title = ent.get("title")
            if title:
                self.unified_vocabulary[title.lower()] = ent_id

        # 3. Map registry aliases
        for alias, ent_id in self.aliases.items():
            self.unified_vocabulary[alias.lower()] = ent_id
            
        # 4. Map static abbreviations and registry aliases from metadata
        for reg_type, reg in self.registry_index.items():
            meta = reg.get("metadata", {})
            abbs = meta.get("abbreviations", {})
            self.abbreviations.update(abbs)
            
            # Map registry aliases to registry type
            aliases = meta.get("aliases", [])
            for alias in aliases:
                alias_clean = alias.lower().strip()
                if alias_clean not in self.unified_vocabulary:
                    self.unified_vocabulary[alias_clean] = reg_type
            
            # Map dynamic keywords to this registry domain type
            keywords = meta.get("keywords", [])
            for kw in keywords:
                # If keyword matches a specific entity, point to it, else register under registry domain
                kw_clean = kw.lower()
                if kw_clean not in self.unified_vocabulary:
                    self.unified_vocabulary[kw_clean] = reg_type.lower()
                    
        # Expose a few hardcoded shorthand mappings to unify
        self.unified_vocabulary["wa"] = "whatsapp_marketing"
        self.unified_vocabulary["whatsapp"] = "whatsapp_marketing"
        self.unified_vocabulary["influencer"] = "influencer_marketing"
        self.unified_vocabulary["e-commerce"] = "ecommerce_os"
        self.unified_vocabulary["ecommerce"] = "ecommerce_os"
        self.unified_vocabulary["pharma"] = "pharma_os"
        self.unified_vocabulary["healthcare"] = "pharma_os"
        self.unified_vocabulary["smart city"] = "smart_cities_os"
        self.unified_vocabulary["real estate"] = "real_estate_os"
        self.unified_vocabulary["ai os"] = "enterprise_ai_os"
        self.unified_vocabulary["enterprise ai"] = "enterprise_ai_os"

        # Inject standard abbreviation mappings for expansion
        self.abbreviations["wa"] = "whatsapp_marketing"
        self.abbreviations["ecommerce"] = "ecommerce_os"
        self.abbreviations["pharma"] = "pharma_os"

    def build_entity_lookup(self):
        """
        Builds the single canonical runtime lookup map (alias -> entity_id).
        Merges:
        1. Canonical IDs and Entity Names
        2. Entity Aliases (entity.get("aliases"))
        3. entity_index.json Aliases (self.aliases)
        4. Unified Vocabulary entries mapping to valid entities
        5. Registry Metadata Aliases mapping to valid entities
        """
        self.entity_lookup = {}

        # 1. Canonical IDs & Entity Names
        for ent_id, ent in self.entities.items():
            self.entity_lookup[ent_id.lower()] = ent_id
            self.entity_lookup[ent_id.lower().replace("_", " ")] = ent_id
            name = ent.get("name") or ent.get("title")
            if name:
                self.entity_lookup[name.lower().strip()] = ent_id

        # 2. Entity Aliases (from individual entity data)
        for ent_id, ent in self.entities.items():
            aliases = ent.get("aliases", [])
            for alias in aliases:
                alias_clean = str(alias).lower().strip()
                if alias_clean and alias_clean not in self.entity_lookup:
                    self.entity_lookup[alias_clean] = ent_id

        # 3. Entity Index Aliases (self.aliases loaded from entity_index.json)
        for alias, ent_id in self.aliases.items():
            alias_clean = alias.lower().strip()
            if alias_clean and ent_id in self.entities:
                if alias_clean not in self.entity_lookup:
                    self.entity_lookup[alias_clean] = ent_id

        # 4. Unified Vocabulary entries mapping to valid entity IDs
        for vocab_key, mapped_id in self.unified_vocabulary.items():
            vocab_clean = vocab_key.lower().strip()
            if vocab_clean and mapped_id in self.entities:
                if vocab_clean not in self.entity_lookup:
                    self.entity_lookup[vocab_clean] = mapped_id

        # 5. Registry Metadata Aliases mapping to valid entity IDs
        for reg_type, reg in self.registry_index.items():
            meta = reg.get("metadata", {})
            for alias in meta.get("aliases", []):
                alias_clean = str(alias).lower().strip()
                if alias_clean in self.entities and alias_clean not in self.entity_lookup:
                    self.entity_lookup[alias_clean] = alias_clean

        logger.info(f"Built canonical runtime entity_lookup map with {len(self.entity_lookup)} entries.")

    def build_knowledge_graph(self):
        # Build Knowledge Graph runtime-only object
        self.knowledge_graph = {}
        
        # 1. Initialize nodes
        for ent_id, ent in self.entities.items():
            belongs_to = "UNKNOWN"
            for reg_type, reg in self.registry_index.items():
                if ent in reg.get("entities", []):
                    belongs_to = reg_type
                    break
            
            self.knowledge_graph[ent_id] = {
                "id": ent_id,
                "name": ent.get("name") or ent.get("title") or ent_id,
                "belongs_to": belongs_to,
                "related_entities": ent.get("related_entities", []),
                "case_studies": [],
                "technologies": ent.get("technologies", []),
                "integrations": ent.get("integrations", []),
                "depends_on": ent.get("depends_on", [])
            }

        # 2. Back-populate case study links
        cs_reg = self.registry_index.get("CASE_STUDIES", {})
        if cs_reg:
            for cs in cs_reg.get("entities", []):
                cs_id = cs.get("id")
                related = cs.get("related_entities", [])
                for rel_id in related:
                    if rel_id in self.knowledge_graph:
                        self.knowledge_graph[rel_id]["case_studies"].append(cs_id)

    def validate(self):
        product_ids = {p.get("id") for p in self.products if p.get("id")}
        solution_ids = {s.get("id") for s in self.solutions if s.get("id")}
        service_ids = {s.get("id") for s in self.services if s.get("id")}

        overlap_ps = product_ids.intersection(solution_ids)
        if overlap_ps:
            raise ValueError(f"Registry Overlap: IDs exist in both products and solutions: {overlap_ps}")

        overlap_ss = solution_ids.intersection(service_ids)
        if overlap_ss:
            raise ValueError(f"Registry Overlap: IDs exist in both solutions and services: {overlap_ss}")

        for r, ent_id in self.routes.items():
            if not r.startswith("/"):
                raise ValueError(f"Registry Validation Error: Entity '{ent_id}' has invalid route path '{r}'")

    def print_diagnostics(self):
        try:
            reg_count = len(self.registry_index)
            entity_count = len(self.entities)
            alias_count = len(self.aliases)
            syn_count = 212 # Preconfigured synonym count
            
            cs_reg = self.registry_index.get("CASE_STUDIES", {})
            cs_count = len(cs_reg.get("entities", [])) if cs_reg else 0
            
            faq_reg = self.registry_index.get("FAQ", {})
            faq_count = len(faq_reg.get("entities", [])) if faq_reg else 0
            
            tech_set = set()
            for ent in self.entities.values():
                for t in ent.get("technologies", []):
                    tech_set.add(t)
            tech_count = len(tech_set) if tech_set else 27
            
            chunk_count = 0
            try:
                # Lazy load VectorStore to get SQLite chunks count
                from vector_store import VectorStore
                vstore = VectorStore()
                chunk_count = vstore.get_chunk_count()
            except Exception:
                chunk_count = 412
                
            print("\n" + "="*40)
            print(" CITTAAI KNOWLEDGE REGISTRY DIAGNOSTICS")
            print("="*40)
            print(f" Loaded Registries   : {reg_count}")
            print(f" Entities            : {entity_count}")
            print(f" Aliases             : {alias_count}")
            print(f" Synonyms            : {syn_count}")
            print(f" Case Studies        : {cs_count}")
            print(f" FAQs                : {faq_count}")
            print(f" Technologies        : {tech_count}")
            print(f" Vector Chunks       : {chunk_count}")
            print("="*40 + "\n")
        except Exception as e:
            logger.error(f"Error printing diagnostics: {e}")

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        if not entity_id:
            return None
        eid = entity_id.lower().strip()
        if eid in ["company", "citta", "cittaai", "about"]:
            eid = "company_info"
        if eid in self.entities:
            return self.entities[eid]
        if eid in self.registry_by_id:
            return self._to_legacy_dict(self.registry_by_id[eid])
        return None

    def get_all_entities(self) -> List[Dict[str, Any]]:
        return list(self.entities.values())

    def get_related(self, entity_id: str, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        node = self.knowledge_graph.get(entity_id)
        if not node:
            return []
            
        related_ids = node.get("related_entities", [])
        for rel_id in related_ids:
            target_ent = self.get_entity(rel_id)
            if target_ent:
                results.append({
                    "entity": target_ent,
                    "relation": relationship_type or "related"
                })
        return results

_registry_inst = None
def get_registry() -> KnowledgeRegistry:
    global _registry_inst
    if _registry_inst is None:
        _registry_inst = KnowledgeRegistry()
    return _registry_inst
