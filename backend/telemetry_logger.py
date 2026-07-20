import sqlite3
import json
import logging
from datetime import datetime, timezone
import os

logger = logging.getLogger(__name__)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "telemetry.db"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Persistent request telemetry
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests_telemetry (
        id TEXT PRIMARY KEY,
        timestamp TEXT,
        query TEXT,
        tenant_id TEXT,
        session_id TEXT,
        context_json TEXT
    )
    """)
    
    # Persistent human evaluation scoring table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS human_evaluations (
        request_id TEXT PRIMARY KEY,
        correctness INTEGER,
        completeness INTEGER,
        groundedness INTEGER,
        hallucination INTEGER,
        citation_quality INTEGER,
        user_satisfaction INTEGER,
        comments TEXT,
        FOREIGN KEY(request_id) REFERENCES requests_telemetry(id)
    )
    """)
    
    conn.commit()
    conn.close()

async def log_execution(context) -> None:
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        request_id = str(context.request.session_id) + "_" + str(datetime.now(timezone.utc).timestamp())
        # If request has unique ID or similar, use it. Otherwise construct session key
        # ExecutionContext usually has unique session identifiers
        request_id = f"{context.request.session_id}_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        
        cursor.execute("""
        INSERT OR REPLACE INTO requests_telemetry (id, timestamp, query, tenant_id, session_id, context_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            request_id,
            datetime.now(timezone.utc).isoformat(),
            context.request.query,
            context.request.tenant_id,
            context.request.session_id,
            context.model_dump_json()
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.exception(f"Failed to log execution context to persistent telemetry: {e}")
