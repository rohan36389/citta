import json
import sqlite3
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import config

logger = logging.getLogger(__name__)

DB_PATH = Path(config.SQLITE_DB_PATH)

# In-memory buffer for fast debugging inspection
_explainability_buffer: List[Dict[str, Any]] = []
MAX_BUFFER_SIZE = 500

def init_explainability_db():
    """Ensures explainability_analytics table exists in SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS explainability_analytics (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                normalized_query TEXT NOT NULL,
                registry TEXT,
                entity TEXT,
                section TEXT,
                intent TEXT,
                confidence REAL,
                retrieved_sources TEXT,
                llm_used INTEGER,
                validator_result TEXT,
                latency REAL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to initialize explainability_analytics table: {e}")

init_explainability_db()

def create_explainability_log(
    query: str,
    normalized_query: str,
    registry: Optional[str] = None,
    entity: Optional[str] = None,
    section: Optional[str] = None,
    intent: Optional[str] = None,
    confidence: float = 1.0,
    retrieved_sources: Optional[List[str]] = None,
    llm_used: Union[bool, str] = False,
    validator_result: Optional[Union[Dict[str, Any], bool]] = None,
    latency: float = 0.0
) -> Dict[str, Any]:
    """
    Constructs standard explainability log object for production monitoring and debugging.
    
    Structure:
    {
        "query": str,
        "normalized_query": str,
        "registry": str,
        "entity": str,
        "section": str,
        "intent": str,
        "confidence": float,
        "retrieved_sources": List[str],
        "llm_used": bool,
        "validator_result": Dict[str, Any],
        "latency": float
    }
    """
    retrieved_sources = retrieved_sources or []
    
    if validator_result is None:
        val_res = {"valid": True, "reasons": []}
    elif isinstance(validator_result, bool):
        val_res = {"valid": validator_result, "reasons": []}
    else:
        val_res = validator_result

    log_obj = {
        "query": query,
        "normalized_query": normalized_query,
        "registry": registry or "NONE",
        "entity": entity or "NONE",
        "section": section or "NONE",
        "intent": intent or "UNKNOWN",
        "confidence": float(confidence),
        "retrieved_sources": retrieved_sources,
        "llm_used": bool(llm_used),
        "validator_result": val_res,
        "latency": float(latency)
    }
    return log_obj

def log_explainability(log_obj: Dict[str, Any]) -> None:
    """
    Logs explainability data internally:
    1. Appends to in-memory debugging buffer
    2. Writes structured record into analytics.db SQLite table
    3. Emits logger info string
    Never exposes log data directly to user interface text.
    """
    try:
        # 1. In-memory buffer
        _explainability_buffer.append(log_obj)
        if len(_explainability_buffer) > MAX_BUFFER_SIZE:
            _explainability_buffer.pop(0)

        # 2. SQLite storage
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        sources_str = json.dumps(log_obj["retrieved_sources"])
        val_str = json.dumps(log_obj["validator_result"])
        
        cursor.execute("""
            INSERT INTO explainability_analytics (
                id, timestamp, query, normalized_query, registry, entity, section,
                intent, confidence, retrieved_sources, llm_used, validator_result, latency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            log_obj["query"],
            log_obj["normalized_query"],
            log_obj["registry"],
            log_obj["entity"],
            log_obj["section"],
            log_obj["intent"],
            log_obj["confidence"],
            sources_str,
            1 if log_obj["llm_used"] else 0,
            val_str,
            log_obj["latency"]
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"EXPLAINABILITY_LOG: {json.dumps(log_obj)}")
    except Exception as e:
        logger.error(f"Failed to log explainability record: {e}")

def get_recent_explainability_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Returns recent explainability logs for administrative monitoring and debugging."""
    return _explainability_buffer[-limit:]
