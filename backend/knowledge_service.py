import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from knowledge_registry import get_registry
from tenant_registry import get_tenant_registry

logger = logging.getLogger(__name__)

class KnowledgeService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KnowledgeService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.reg = get_registry()
        self.tenant_reg = get_tenant_registry()

    def search_registry(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Applies priority-based deterministic search ranking to find the best matching
        knowledge object, capability, or feature.
        Order: Normalize query -> Typo correction -> Alias lookup -> Exact match -> Fuzzy match -> Registry lookup.
        """
        import re
        raw_q = query.lower().strip()
        if not raw_q:
            return None

        # Typo correction stage
        q = raw_q
        from query_normalizer import COMMON_TYPO_MAP
        for typo, fix in COMMON_TYPO_MAP.items():
            q = re.sub(rf"\b{re.escape(typo)}\b", fix, q, flags=re.IGNORECASE)

        candidates = []  # List of tuples: (score, obj_dict_or_entry, match_metadata)

        # 1. ID Match (Score 100)
        if q in self.reg.registry_by_id or raw_q in self.reg.registry_by_id:
            target_id = q if q in self.reg.registry_by_id else raw_q
            candidates.append((100, self.reg.registry_by_id[target_id], {"match_type": "id"}))

        # 2. Slug Match (Score 95)
        if q in self.reg.registry_by_slug or raw_q in self.reg.registry_by_slug:
            target_slug = q if q in self.reg.registry_by_slug else raw_q
            candidates.append((95, self.reg.registry_by_slug[target_slug], {"match_type": "slug"}))

        # 3. Exact Primary Keyword Match (Score 90)
        for obj in self.reg.registry_by_id.values():
            if obj.id == "company_info" and not any(k in q for k in ["citta", "company", "mission", "vision", "founded", "about us", "who are you", "what is cittaai"]):
                continue
            if any(q == pk.lower() or raw_q == pk.lower() for pk in obj.search.primary_keywords):
                candidates.append((90, obj, {"match_type": "primary_keyword"}))

        # 4. Alias Match (Score 80)
        for obj in self.reg.registry_by_id.values():
            if obj.id == "company_info" and not any(k in q for k in ["citta", "company", "mission", "vision", "founded", "about us", "who are you", "what is cittaai"]):
                continue
            if any(q == al.lower() or raw_q == al.lower() for al in obj.search.aliases):
                candidates.append((80, obj, {"match_type": "alias"}))

        # 4.5 Substring / Phrase Boundary Match (Score 80)
        import re
        for obj in self.reg.registry_by_id.values():
            if obj.id == "company_info" and not any(k in q for k in ["citta", "company", "mission", "vision", "founded", "about us", "who are you", "what is cittaai"]):
                continue
            all_aliases = set(obj.search.aliases + obj.search.primary_keywords + [obj.id, obj.slug, obj.title.lower(), obj.name.lower()])
            for al in all_aliases:
                al_clean = al.lower().strip()
                if len(al_clean) > 3 and (re.search(rf"\b{re.escape(al_clean)}\b", q) or re.search(rf"\b{re.escape(al_clean)}\b", raw_q)):
                    candidates.append((80, obj, {"match_type": "phrase_match"}))

        # 5. Fuzzy String Similarity Matching (Score 75-79)
        try:
            from rapidfuzz import fuzz
            for obj in self.reg.registry_by_id.values():
                if obj.id == "company_info" and not any(k in q for k in ["citta", "company", "mission", "vision", "founded", "about us", "who are you", "what is cittaai"]):
                    continue
                all_aliases = set(obj.search.aliases + obj.search.primary_keywords + [obj.id, obj.slug, obj.title.lower(), obj.name.lower()])
                for al in all_aliases:
                    al_clean = al.lower().strip()
                    if len(al_clean) > 3:
                        ratio = max(fuzz.token_set_ratio(q, al_clean), fuzz.partial_ratio(q, al_clean))
                        if ratio >= 80:
                            candidates.append((78, obj, {"match_type": "fuzzy_match", "similarity": ratio}))
        except ImportError:
            pass

        # 6. Capability Title Match (Score 75)
        for cap_key, cap_entry in self.reg.registry_by_capability.items():
            cap_title = cap_entry["capability"].title.lower().strip()
            if cap_title not in ["services", "products", "solutions", "managed services"]:
                if q == cap_key.lower() or q == cap_title or (len(cap_title) > 4 and re.search(rf"\b{re.escape(cap_title)}\b", q)):
                    candidates.append((75, cap_entry, {"match_type": "capability"}))

        # 7. Feature Title Match (Score 70)
        for feat_key, feat_entry in self.reg.registry_by_feature.items():
            feat_title = feat_entry["feature"].title.lower().strip()
            if feat_title not in ["services", "products", "solutions", "managed services"]:
                if q == feat_key.lower() or q == feat_title or (len(feat_title) > 4 and re.search(rf"\b{re.escape(feat_title)}\b", q)):
                    candidates.append((70, feat_entry, {"match_type": "feature"}))

        # 8. Synonym / Secondary Keyword Match (Score 65)
        for obj in self.reg.registry_by_id.values():
            if obj.id == "company_info" and not any(k in q for k in ["citta", "company", "mission", "vision", "founded", "about us", "who are you", "what is cittaai"]):
                continue
            if any(q == sk.lower() for sk in obj.search.secondary_keywords) or any(q == syn.lower() for syn in obj.search.synonyms):
                candidates.append((65, obj, {"match_type": "secondary_keyword_synonym"}))

        # 9. Partial Match (Score 50)
        for obj in self.reg.registry_by_id.values():
            if obj.id == "company_info" and not any(k in q for k in ["citta", "company", "mission", "vision", "founded", "about us", "who are you", "what is cittaai"]):
                continue
            if q in obj.id or q in obj.slug or q in obj.title.lower() or any(q in pk.lower() for pk in obj.search.primary_keywords):
                candidates.append((50, obj, {"match_type": "partial"}))
        for cap_key, cap_entry in self.reg.registry_by_capability.items():
            if q in cap_key.lower() or q in cap_entry["capability"].title.lower():
                candidates.append((50, cap_entry, {"match_type": "partial_capability"}))

        if not candidates:
            return None

        # Sort candidates: highest score wins
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_match, meta = candidates[0]
        
        if isinstance(best_match, dict) and ("capability" in best_match or "feature" in best_match):
            return {
                "type": "nested_match",
                "match": best_match,
                "score": best_score,
                "metadata": meta
            }
        else:
            return {
                "type": "object_match",
                "match": best_match,
                "score": best_score,
                "metadata": meta
            }

    def find_entity(self, tenant_id: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Generic tenant-aware entity lookup utilizing priority search.
        """
        res = self.search_registry(query)
        if not res:
            return None

        if res["type"] == "nested_match":
            parent_obj = res["match"]["parent"]
            legacy_dict = self.reg._to_legacy_dict(parent_obj)
            if "capability" in res["match"]:
                legacy_dict["matched_capability"] = res["match"]["capability"]
            elif "feature" in res["match"]:
                legacy_dict["matched_feature"] = res["match"]["feature"]
            return legacy_dict
        else:
            return self.reg._to_legacy_dict(res["match"])

    def find_people(self, tenant_id: str, role_or_name: str) -> Optional[Dict[str, Any]]:
        """
        Generic person lookup. Resolves individual executive profiles based on role or name.
        """
        role_clean = role_or_name.lower().strip()
        
        # Role synonym expansion
        role_syns = [role_clean]
        if "ceo" in role_clean or "chief executive officer" in role_clean:
            role_syns.extend(["ceo", "chief executive officer"])
        elif "cto" in role_clean or "chief technology officer" in role_clean:
            role_syns.extend(["cto", "chief technology officer"])
        elif "coo" in role_clean or "chief operating officer" in role_clean:
            role_syns.extend(["coo", "chief operating officer"])
        elif "cmo" in role_clean or "chief marketing officer" in role_clean:
            role_syns.extend(["cmo", "chief marketing officer"])
        elif "founder" in role_clean:
            role_syns.extend(["founder"])

        lead_data = self.reg.registry_index.get("LEADERSHIP", {})
        leaders = lead_data.get("leaders", [])
        others = lead_data.get("others", [])
        all_people = leaders + others

        for person in all_people:
            p_name = person.get("name", "").lower()
            p_title = person.get("title", "").lower()
            p_aliases = [str(a).lower() for a in person.get("aliases", [])]
            
            for r in role_syns:
                if (r in p_title or r in p_name or any(r == a for a in p_aliases)):
                    return {
                        "id": person.get("id"),
                        "name": person.get("name"),
                        "title": person.get("title"),
                        "role": r.upper(),
                        "tenant_id": tenant_id
                    }
        return None

    def list_entities(self, tenant_id: str, entity_type: str) -> List[Dict[str, Any]]:
        """
        Returns complete catalog listings for PRODUCTS, SERVICES, SOLUTIONS, CASE_STUDIES, LEADERSHIP.
        """
        etype = entity_type.upper().strip()
        if etype in ["PRODUCTS", "PRODUCT"]:
            return self.reg.products
        elif etype in ["SERVICES", "SERVICE"]:
            return self.reg.services
        elif etype in ["SOLUTIONS", "SOLUTION"]:
            return self.reg.solutions
        elif etype in ["CASE_STUDIES", "CASE_STUDY"]:
            cs_data = self.reg.registry_index.get("CASE_STUDIES", {})
            return cs_data.get("entities", [])
        elif etype in ["LEADERSHIP", "TEAM"]:
            lead_data = self.reg.registry_index.get("LEADERSHIP", {})
            return lead_data.get("leaders", []) + lead_data.get("others", [])
        return []

    def count_entities(self, tenant_id: str, entity_type: str) -> Dict[str, Any]:
        """
        Returns count breakdown for specified category.
        """
        items = self.list_entities(tenant_id, entity_type)
        etype = entity_type.upper().strip()
        return {
            "tenant_id": tenant_id,
            "entity_type": etype,
            "count": len(items),
            "items": items
        }

    def find_sections(self, tenant_id: str, entity_id: str, topics: List[str]) -> Dict[str, Any]:
        """
        Retrieves section content for entity based on requested topics.
        """
        ent = self.reg.get_entity(entity_id)
        if not ent:
            return {}

        results = {}
        for topic in topics:
            t_clean = topic.lower()
            if t_clean in ["overview", "company"]:
                results["overview"] = ent.get("overview") or ent.get("description") or ent.get("summary")
            elif t_clean in ["how_it_works", "workflow"]:
                results["how_it_works"] = ent.get("how_it_works")
            elif t_clean in ["features", "modules"]:
                results["features"] = ent.get("features") or ent.get("capabilities")
            elif t_clean in ["benefits", "advantages"]:
                results["benefits"] = ent.get("benefits")
            elif t_clean in ["case_studies", "results"]:
                results["case_studies"] = ent.get("case_studies") or ent.get("results")
            elif t_clean in ["technologies", "tech"]:
                results["technologies"] = ent.get("technologies") or ent.get("tech_stack")
        return results

    def find_related(self, tenant_id: str, entity_id: str) -> List[Dict[str, Any]]:
        ent = self.reg.get_entity(entity_id)
        if not ent:
            return []
        rel_ids = ent.get("related_entities", [])
        return [self.reg.get_entity(r_id) for r_id in rel_ids if self.reg.get_entity(r_id)]

def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService()
