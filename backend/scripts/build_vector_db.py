import sys
import os
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure backend folder is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from vector_indexer import build_vector_database
from vector_store import VectorStore

async def main():
    logger.info("Initializing offline vector database build script...")
    
    force_build = "--force" in sys.argv
    success = await build_vector_database(force=force_build)
    
    if not success:
        raise RuntimeError("Vector database build failed during ingestion or model encoding.")
        
    vstore = VectorStore()
    if not os.path.exists(vstore.db_path):
        raise RuntimeError(f"Vector database build failed: database file '{vstore.db_path}' was not created.")

    val = vstore.validate_database_integrity()
    if not val.get("valid"):
        raise RuntimeError(f"Vector database build failed: integrity check failed ({val.get('reason')}).")

    chunk_count = vstore.get_chunk_count()
    if chunk_count <= 0:
        raise RuntimeError("Vector database build failed: 0 chunks were indexed.")

    meta = vstore.get_metadata()
    if not meta.get("content_hash"):
        raise RuntimeError("Vector database build failed: metadata content_hash is missing.")

    logger.info(f"✓ Build & Integrity Verified: {chunk_count} chunks indexed successfully.")
    logger.info(f"✓ Metadata: {meta}")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
