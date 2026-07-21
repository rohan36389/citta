import os
import sys
import hashlib
import logging
import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import config
from vector_store import VectorStore, parse_content_js, atomic_replace_database

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent

def compute_file_sha256(file_path: str) -> str:
    """Computes SHA-256 hash of a file for deterministic rebuild verification."""
    if not os.path.exists(file_path):
        return ""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

async def build_vector_database(
    content_js_path: Optional[str] = None,
    db_path: Optional[str] = None,
    force: bool = False
) -> bool:
    """
    Idempotently builds vector_store.db using atomic temporary database replacement.
    Reads content.js, generates embeddings, validates integrity, and writes metadata.
    """
    if not content_js_path:
        candidates = [
            os.path.join(ROOT_DIR, "..", "frontend", "src", "data", "content.js"),
            os.path.join(ROOT_DIR, "data", "content.js"),
            os.path.join(ROOT_DIR, "content.js"),
            "/app/frontend/src/data/content.js",
            "/app/data/content.js",
            "/app/content.js",
        ]
        for c in candidates:
            if os.path.exists(c):
                content_js_path = c
                break
        else:
            content_js_path = os.path.join(ROOT_DIR, "..", "frontend", "src", "data", "content.js")
    content_js_path = os.path.abspath(content_js_path)

    if not db_path:
        db_path = config.VECTOR_DB_PATH
    db_path = os.path.abspath(db_path)

    if not os.path.exists(content_js_path):
        logger.error(f"content.js not found at {content_js_path}")
        return False

    current_hash = compute_file_sha256(content_js_path)

    # 1. Deterministic Content Hash Check
    if not force and os.path.exists(db_path):
        target_store = VectorStore(db_path)
        existing_meta = target_store.get_metadata()
        stored_hash = existing_meta.get("content_hash", "")
        if stored_hash and stored_hash == current_hash and target_store.get_chunk_count() > 0:
            logger.info(f"✓ Content hash match ({current_hash[:8]}...). Vector database is up to date. Skipping build.")
            return True

    # 2. Build inside temporary database for atomic replacement
    tmp_db_path = db_path + ".tmp.db"
    if os.path.exists(tmp_db_path):
        try:
            os.remove(tmp_db_path)
        except Exception:
            pass

    logger.info(f"Building vector database in temporary file: {tmp_db_path}")
    tmp_store = VectorStore(tmp_db_path)
    tmp_store.rebuild_db()

    # 3. Parse content.js
    chunks = parse_content_js(content_js_path)
    if not chunks:
        logger.error("No chunks parsed from content.js. Build aborted.")
        if os.path.exists(tmp_db_path):
            os.remove(tmp_db_path)
        return False

    # 4. Generate passage embeddings
    logger.info(f"Loading local embedding model: {config.EMBEDDING_MODEL}")
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)

    logger.info(f"Generating passage embeddings for {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks):
        chunk_id = f"content_js_{i}"
        content_text = chunk["content"]
        processed_text = content_text
        if "bge" in config.EMBEDDING_MODEL.lower():
            processed_text = f"Represent this sentence for searching relevant passages: {content_text}"

        emb = embedding_model.encode(processed_text, normalize_embeddings=True).tolist()
        tmp_store.add_chunk(
            chunk_id=chunk_id,
            content=content_text,
            embedding=emb,
            metadata=chunk["metadata"]
        )

    # 5. Write extended version metadata
    chunk_count = tmp_store.get_chunk_count()
    metadata: Dict[str, Any] = {
        "version": "1.0.0",
        "schema_version": "1.0.0",
        "parser_version": "1.0.0",
        "application_version": "1.0.0",
        "embedding_model": config.EMBEDDING_MODEL,
        "content_hash": current_hash,
        "chunk_count": str(chunk_count),
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    tmp_store.write_metadata(metadata)

    # 6. Integrity Verification
    if chunk_count == 0:
        logger.error("Integrity assertion failed: chunk count is 0. Build aborted.")
        if os.path.exists(tmp_db_path):
            os.remove(tmp_db_path)
        return False

    # 7. Atomic Replacement
    logger.info(f"Atomically replacing {db_path} with newly built database...")
    atomic_replace_database(tmp_db_path, db_path)

    db_size_mb = round(os.path.getsize(db_path) / (1024 * 1024), 2)
    logger.info(f"✓ Indexed {chunk_count} chunks | ✓ Database size: {db_size_mb} MB | ✓ Content hash: {current_hash[:8]}... | ✓ Completed successfully")
    return True
