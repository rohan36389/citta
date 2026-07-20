import sys
import os
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure backend folder is in path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

import config
import vector_store
import rag_service
from llm_provider import NvidiaProvider

async def main():
    logger.info("Initializing RAG database builder...")
    
    # 1. Check/create vector database
    vstore = vector_store.VectorStore()
    
    # 2. Rebuild database (clean schema)
    logger.info("Rebuilding vector database schema...")
    vstore.rebuild_db()
    
    # 3. Initialize RAG Service with Nvidia provider to load local embedding model
    provider = NvidiaProvider()
    rag = rag_service.RAGService(provider=provider, vector_store=vstore)
    
    # 4. Parse content.js
    content_js_path = os.path.join(ROOT_DIR, "..", "frontend", "src", "data", "content.js")
    logger.info(f"Parsing website content from {content_js_path}...")
    chunks = vector_store.parse_content_js(content_js_path)
    
    if not chunks:
        logger.error("No chunks found in content.js. Check file path.")
        return
        
    logger.info(f"Generating embeddings for {len(chunks)} chunks using {config.EMBEDDING_MODEL}...")
    
    # Process sequentially
    for i, chunk in enumerate(chunks):
        chunk_id = f"content_js_{i}"
        # Fetch embedding using 'passage' input type for documentation indexing
        emb = await rag.get_embedding(chunk["content"], input_type="passage")
        
        vstore.add_chunk(
            chunk_id=chunk_id,
            content=chunk["content"],
            embedding=emb,
            metadata=chunk["metadata"]
        )
        if (i + 1) % 10 == 0 or (i + 1) == len(chunks):
            logger.info(f"Indexed {i + 1}/{len(chunks)} chunks...")
            
    logger.info("Explicit indexing complete! Vector store has been populated.")

if __name__ == "__main__":
    asyncio.run(main())
