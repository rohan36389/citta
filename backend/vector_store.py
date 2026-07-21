import os
import sqlite3
import json
import re
import numpy as np
from typing import List, Dict, Any, Tuple

import config

DB_PATH = config.VECTOR_DB_PATH

def atomic_replace_database(tmp_db_path: str, target_db_path: str):
    if not os.path.exists(tmp_db_path):
        raise FileNotFoundError(f"Temporary database file {tmp_db_path} does not exist")
    os.replace(tmp_db_path, target_db_path)

class VectorStore:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                embedding BLOB NOT NULL,
                metadata TEXT NOT NULL,
                source TEXT NOT NULL
            )
        """)
        # Create metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vector_db_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def rebuild_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS chunks")
        cursor.execute("DROP TABLE IF EXISTS vector_db_metadata")
        conn.commit()
        conn.close()
        self._init_db()

    def get_metadata(self) -> Dict[str, str]:
        if not os.path.exists(self.db_path):
            return {}
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT key, value FROM vector_db_metadata")
            rows = cursor.fetchall()
            return {row[0]: row[1] for row in rows}
        except Exception:
            return {}
        finally:
            conn.close()

    def write_metadata(self, metadata: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            for k, v in metadata.items():
                cursor.execute(
                    "INSERT OR REPLACE INTO vector_db_metadata (key, value) VALUES (?, ?)",
                    (str(k), str(v))
                )
            conn.commit()
        finally:
            conn.close()

    def validate_database_integrity(self) -> Dict[str, Any]:
        if not os.path.exists(self.db_path):
            return {"valid": False, "reason": "Database file missing"}
        try:
            count = self.get_chunk_count()
            if count == 0:
                return {"valid": False, "reason": "Database has 0 chunks"}
            meta = self.get_metadata()
            return {"valid": True, "count": count, "metadata": meta}
        except Exception as e:
            return {"valid": False, "reason": f"Database error: {e}"}

    def warmup(self):
        """Execute a dummy query to warm up the SQLite vector database."""
        dummy_vector = [0.0] * 768
        try:
            _ = self.query_hybrid("warmup", dummy_vector, top_k=1)
        except Exception:
            pass

    def add_chunk(self, chunk_id: str, content: str, embedding: List[float], metadata: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        emb_blob = np.array(embedding, dtype=np.float32).tobytes()
        metadata_str = json.dumps(metadata)
        source = metadata.get("source", "unknown")
        
        cursor.execute(
            "INSERT OR REPLACE INTO chunks (id, content, embedding, metadata, source) VALUES (?, ?, ?, ?, ?)",
            (chunk_id, content, emb_blob, metadata_str, source)
        )
        conn.commit()
        conn.close()

    def delete_document(self, source_name: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chunks WHERE source = ?", (source_name,))
        rows_deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_deleted

    def get_all_documents(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT source, COUNT(*), MAX(metadata) FROM chunks GROUP BY source")
        rows = cursor.fetchall()
        conn.close()
        
        docs = []
        for row in rows:
            source, count, sample_meta = row
            meta = {}
            try:
                meta = json.loads(sample_meta)
            except Exception:
                pass
            docs.append({
                "source": source,
                "chunk_count": count,
                "document_type": meta.get("doc_type", "unknown"),
                "last_updated": meta.get("last_updated", "")
            })
        return docs

    def get_chunk_count(self) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chunks")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_chunk_count_for_page(self, page_url: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM chunks WHERE json_extract(metadata, '$.page') = ? OR json_extract(metadata, '$.url') = ?",
            (page_url, page_url)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, content, metadata, source FROM chunks")
        rows = cursor.fetchall()
        conn.close()
        
        chunks = []
        for row in rows:
            chunk_id, content, metadata_str, source = row
            try:
                metadata = json.loads(metadata_str)
            except Exception:
                metadata = {}
            chunks.append({
                "id": chunk_id,
                "content": content,
                "metadata": metadata,
                "source": source
            })
        return chunks

    def query_hybrid(
        self, 
        query_text: str, 
        query_embedding: List[float], 
        intent: str = None, 
        top_k: int = 5,
        domain: str = None
    ) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, content, embedding, metadata, source FROM chunks")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        query_vector = np.array(query_embedding, dtype=np.float32)
        query_terms = set(re.findall(r"\w+", query_text.lower()))

        results = []
        for row in rows:
            chunk_id, content, emb_bytes, metadata_str, source = row
            try:
                metadata = json.loads(metadata_str)
            except Exception:
                metadata = {}

            # 0. Domain Filter
            if domain:
                chunk_domain = metadata.get("domain", "").upper()
                if chunk_domain != domain.upper():
                    continue

            # 1. Intent Category Filtering
            # If intent classification is specific, we prioritize relevant sections
            if intent and intent.lower() != "generalai":
                chunk_category = metadata.get("category", "").lower()
                # Skip chunks that don't match intent category if it's a specific intent search
                # e.g., if intent is 'legal', search only legal category
                if intent.lower() == "legal" and chunk_category != "legal":
                    continue
                if intent.lower() == "products" and chunk_category not in ["product", "solution"]:
                    continue
                if intent.lower() == "services" and chunk_category not in ["service", "solution"]:
                    continue
                if intent.lower() == "service_pricing" and chunk_category not in ["product", "service", "solution"]:
                    continue
                if intent.lower() == "recognition" and chunk_category != "recognition":
                    continue
                if intent.lower() == "casestudies" and chunk_category != "casestudies":
                    continue
                if intent.lower() == "contact" and chunk_category != "contact":
                    continue

            # 2. Semantic Score (Cosine Similarity)
            chunk_vector = np.frombuffer(emb_bytes, dtype=np.float32)
            dot_product = np.dot(query_vector, chunk_vector)
            query_norm = np.linalg.norm(query_vector)
            chunk_norm = np.linalg.norm(chunk_vector)
            
            semantic_score = 0.0
            if query_norm > 0 and chunk_norm > 0:
                # Cosine similarity range from -1 to 1, normalized to 0 to 1
                cosine_sim = dot_product / (query_norm * chunk_norm)
                semantic_score = float((cosine_sim + 1.0) / 2.0)

            # 3. Keyword Match Score (Simple TF-IDF overlap)
            content_lower = content.lower()
            content_terms = re.findall(r"\w+", content_lower)
            term_count = len(content_terms)
            
            keyword_score = 0.0
            if term_count > 0 and query_terms:
                matched_terms = [t for t in query_terms if t in content_lower]
                # Give higher weight to longer matches, normalize by query size and content size log
                overlap = sum(len(t) for t in matched_terms)
                total_query_len = sum(len(t) for t in query_terms)
                if total_query_len > 0:
                    keyword_score = overlap / total_query_len
                    # Adjust for length normalization to avoid penalizing medium docs
                    keyword_score = keyword_score * (1.0 / (1.0 + np.log1p(term_count / 100.0)))

            # 4. Score Fusion (40% Semantic + 20% Keyword + 40% Simulated Cross-Encoder Sequence Matcher)
            from difflib import SequenceMatcher
            cross_encoder_score = SequenceMatcher(None, query_text.lower(), content.lower()).ratio()
            
            fusion_score = (0.4 * semantic_score) + (0.2 * keyword_score) + (0.4 * cross_encoder_score)

            results.append({
                "id": chunk_id,
                "content": content,
                "metadata": metadata,
                "source": source,
                "score": fusion_score,
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "cross_encoder_score": cross_encoder_score
            })

        # Sort by hybrid score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


# --- Ingestion Parser for content.js ---

def clean_js_comments(text: str) -> str:
    # Remove single line comments
    text = re.sub(r"//.*", "", text)
    # Remove block comments
    text = re.sub(r"/\*[\s\S]*?\*/", "", text)
    return text

def parse_javascript_object(js_code: str, var_name: str) -> Dict[str, Any]:
    """Helper to extract a variable declaration as dict if simple, or return chunks of key text."""
    # Find the object block: export const VAR_NAME = { ... };
    pattern = rf"export\s+const\s+{var_name}\s*=\s*([\s\S]*?);"
    match = re.search(pattern, js_code)
    if not match:
        return {}
    
    obj_body = match.group(1).strip()
    
    # We will return key lines as a list of strings for granular chunking
    # This is safer than eval() or simple JSON parse since content.js contains JS templates
    lines = [line.strip() for line in obj_body.split("\n") if line.strip()]
    return {"raw_lines": lines}

def parse_content_js(file_path: str) -> List[Dict[str, Any]]:
    """Parse content.js into highly structured semantic chunks for embedding."""
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = clean_js_comments(content)
    chunks = []
    timestamp = str(os.path.getmtime(file_path))

    # Define the objects we want to parse
    # Products & Solutions
    sections_to_parse = [
        ("WHATSAPP", "product", "/products/whatsapp-marketing"),
        ("INFLUENCER", "product", "/products/influencer-marketing"),
        ("ECOMMERCE", "solution", "/solutions/ecommerce-os"),
        ("REALESTATE", "solution", "/solutions/real-estate-os"),
        ("PHARMA", "solution", "/solutions/pharma-os"),
        ("SMARTCITIES", "solution", "/solutions/smart-cities-os"),
        ("EDUCATION", "solution", "/solutions/education-os"),
        ("ENTERPRISEAI", "solution", "/solutions/enterprise-ai-os"),
    ]

    for var_name, kind, url in sections_to_parse:
        # Extract variables from content
        pattern = rf"export\s+const\s+{var_name}\s*=\s*\{{([\s\S]*?)\}};"
        match = re.search(pattern, content)
        if match:
            body = match.group(1)
            # Find name/eyebrow/hero/subtitle
            name_m = re.search(r"name:\s*\"([^\"]+)\"", body)
            hero_m = re.search(r"hero:\s*\"([^\"]+)\"", body)
            subtitle_m = re.search(r"subtitle:\s*\"([^\"]+)\"", body)
            
            name = name_m.group(1) if name_m else var_name.capitalize()
            hero = hero_m.group(1) if hero_m else ""
            subtitle = subtitle_m.group(1) if subtitle_m else ""

            # Core chunk for the product/solution main details
            main_text = f"CittaAI {kind.capitalize()} - {name}: {hero} {subtitle}"
            chunks.append({
                "content": main_text,
                "metadata": {
                    "source": "content.js",
                    "page": url,
                    "section": "hero",
                    "title": name,
                    "category": kind,
                    "url": url,
                    "last_updated": timestamp,
                    "doc_type": "web_copy"
                }
            })

            # Extract capabilities array: capabilities: [ { t: "Title", d: "Desc" } ]
            cap_pattern = r"\{\s*t:\s*\"([^\"]+)\"\s*,\s*d:\s*\"([^\"]+)\"\s*\}"
            capabilities = re.findall(cap_pattern, body)
            for title, desc in capabilities:
                chunks.append({
                    "content": f"CittaAI {name} Capability: {title} - {desc}",
                    "metadata": {
                        "source": "content.js",
                        "page": url,
                        "section": "capabilities",
                        "title": f"{name} - {title}",
                        "category": kind,
                        "url": url,
                        "last_updated": timestamp,
                        "doc_type": "web_copy"
                    }
                })

    # Ingest RECOGNITION (Awards)
    rec_pattern = r"export\s+const\s+RECOGNITION\s*=\s*\{([\s\S]*?)\};"
    rec_match = re.search(rec_pattern, content)
    if rec_match:
        body = rec_match.group(1)
        # Find award objects: { name: "...", subtitle: "...", body: "...", org: "..." }
        award_blocks = re.findall(r"\{\s*name:\s*\"([^\"]+)\"\s*,\s*subtitle:\s*\"([^\"]+)\"\s*,\s*body:\s*\"([^\"]+)\"\s*,\s*org:\s*\"([^\"]+)\"", body)
        for name, subtitle, award_body, org in award_blocks:
            chunks.append({
                "content": f"CittaAI Award & Recognition: {name} ({subtitle}) - {award_body}. Organized by {org}.",
                "metadata": {
                    "source": "content.js",
                    "page": "/recognition",
                    "section": "awards",
                    "title": name,
                    "category": "recognition",
                    "url": "/recognition",
                    "last_updated": timestamp,
                    "doc_type": "web_copy"
                }
            })

    # Ingest CASESTUDIES
    case_pattern = r"export\s+const\s+CASESTUDIES\s*=\s*\{([\s\S]*?)\};"
    case_match = re.search(case_pattern, content)
    if case_match:
        body = case_match.group(1)
        cases = re.findall(r"\{\s*brand:\s*\"([^\"]+)\"\s*,\s*metric:\s*\"([^\"]+)\"\s*,\s*label:\s*\"([^\"]+)\"\s*,\s*desc:\s*\"([^\"]+)\"", body)
        for brand, metric, label, desc in cases:
            chunks.append({
                "content": f"CittaAI Case Study - {brand}: Achieved {metric} ({label}) - {desc}",
                "metadata": {
                    "source": "content.js",
                    "page": "/case-studies",
                    "section": "cases",
                    "title": f"Case Study: {brand}",
                    "category": "casestudies",
                    "url": "/case-studies",
                    "last_updated": timestamp,
                    "doc_type": "web_copy"
                }
            })

    # Ingest ABOUT
    about_pattern = r"export\s+const\s+ABOUT\s*=\s*\{([\s\S]*?)\};"
    about_match = re.search(about_pattern, content)
    if about_match:
        body = about_match.group(1)
        lead_m = re.search(r"lead:\s*\"([^\"]+)\"", body)
        story_m = re.search(r"story:\s*\"([^\"]+)\"", body)
        
        if lead_m:
            chunks.append({
                "content": f"About CittaAI: {lead_m.group(1)}",
                "metadata": {
                    "source": "content.js",
                    "page": "/about",
                    "section": "about_lead",
                    "title": "About CittaAI",
                    "category": "about",
                    "url": "/about",
                    "last_updated": timestamp,
                    "doc_type": "web_copy"
                }
            })
            
        if story_m:
            chunks.append({
                "content": f"CittaAI History & Story: {story_m.group(1)}",
                "metadata": {
                    "source": "content.js",
                    "page": "/about",
                    "section": "about_story",
                    "title": "Our Story",
                    "category": "about",
                    "url": "/about",
                    "last_updated": timestamp,
                    "doc_type": "web_copy"
                }
            })
            
        # Ingest why CittaAI
        why_items = re.findall(r"\{\s*t:\s*\"([^\"]+)\"\s*,\s*d:\s*\"([^\"]+)\"\s*\}", body)
        for title, desc in why_items:
            chunks.append({
                "content": f"Why choose CittaAI: {title} - {desc}",
                "metadata": {
                    "source": "content.js",
                    "page": "/about",
                    "section": "why_us",
                    "title": f"Why Choose Us: {title}",
                    "category": "about",
                    "url": "/about",
                    "last_updated": timestamp,
                    "doc_type": "web_copy"
                }
            })

    # Ingest BRAND constants (Vision, driven by Fixity)
    brand_pattern = r"export\s+const\s+BRAND\s*=\s*\{([\s\S]*?)\};"
    brand_match = re.search(brand_pattern, content)
    if brand_match:
        body = brand_match.group(1)
        tag_m = re.search(r"tagline:\s*\"([^\"]+)\"", body)
        driven_m = re.search(r"drivenBy:\s*\"([^\"]+)\"", body)
        pos_m = re.search(r"positioning:\s*\"([^\"]+)\"", body)
        
        brand_info = []
        if tag_m: brand_info.append(f"Tagline: {tag_m.group(1)}.")
        if driven_m: brand_info.append(f"Philosophy: {driven_m.group(1)}.")
        if pos_m: brand_info.append(f"Positioning: {pos_m.group(1)}.")
        
        chunks.append({
            "content": f"CittaAI Brand Core Info: " + " ".join(brand_info),
            "metadata": {
                "source": "content.js",
                "page": "/",
                "section": "brand",
                "title": "CittaAI Brand Info",
                "category": "company",
                "url": "/",
                "last_updated": timestamp,
                "doc_type": "web_copy"
            }
        })

    # Ingest CONTACT Info
    contact_pattern = r"export\s+const\s+CONTACT\s*=\s*\{([\s\S]*?)\};"
    contact_match = re.search(contact_pattern, content)
    if contact_match:
        body = contact_match.group(1)
        phone_m = re.search(r"phone:\s*\"([^\"]+)\"", body)
        email_m = re.search(r"email:\s*\"([^\"]+)\"", body)
        address_m = re.search(r"address:\s*\"([^\"]+)\"", body)
        
        contact_info = []
        if phone_m: contact_info.append(f"Phone: {phone_m.group(1)}.")
        if email_m: contact_info.append(f"Email: {email_m.group(1)}.")
        if address_m: contact_info.append(f"Office Address: {address_m.group(1)}.")
        
        chunks.append({
            "content": f"CittaAI Contact Details: " + " ".join(contact_info),
            "metadata": {
                "source": "content.js",
                "page": "/contact",
                "section": "contact_info",
                "title": "Contact Information",
                "category": "contact",
                "url": "/contact",
                "last_updated": timestamp,
                "doc_type": "web_copy"
            }
        })

    return chunks
