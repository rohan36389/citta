import sqlite3
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import config

logger = logging.getLogger(__name__)

DB_PATH = config.TELEMETRY_DB_PATH

def init_knowledge_gap_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                query TEXT,
                intent TEXT,
                entity TEXT,
                confidence REAL,
                retrieval_score REAL,
                reason TEXT,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Failed to initialize knowledge_gaps table in {DB_PATH}: {e}")

# Initialize on module import
init_knowledge_gap_db()

def log_knowledge_gap(
    query: str,
    intent: Optional[str] = None,
    entity: Optional[str] = None,
    confidence: float = 0.0,
    retrieval_score: float = 0.0,
    reason: str = "Low Confidence",
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Logs low confidence or unhandled questions to telemetry.db silently.
    NEVER exposes this info to the user.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now_str = datetime.utcnow().isoformat()
        meta_str = json.dumps(metadata or {})
        
        cursor.execute("""
            INSERT INTO knowledge_gaps (timestamp, query, intent, entity, confidence, retrieval_score, reason, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (now_str, query, intent or "UNKNOWN", entity or "NONE", confidence, retrieval_score, reason, meta_str))
        
        conn.commit()
        conn.close()
        logger.info(f"Logged Knowledge Gap: '{query}' ({reason})")
    except Exception as e:
        logger.warning(f"Failed to log knowledge gap: {e}")
