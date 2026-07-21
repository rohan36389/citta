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
        logger.error("❌ Vector database build failed.")
        sys.exit(1)
        
    vstore = VectorStore()
    chunk_count = vstore.get_chunk_count()
    if chunk_count == 0:
        logger.error("❌ Integrity Check Failed: vector database chunk count is 0.")
        sys.exit(1)
        
    meta = vstore.get_metadata()
    logger.info(f"✓ CI Integrity Verified: {chunk_count} chunks indexed successfully.")
    logger.info(f"✓ Metadata: {meta}")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
