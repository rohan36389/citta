import asyncio
from vector_store import VectorStore
from rag_service import RAGService
from llm_provider import NvidiaProvider

async def test():
    vstore = VectorStore()
    provider = NvidiaProvider()
    rag = RAGService(provider, vstore)
    
    query = "What is the Pharma OS solution offered by CittaAI?"
    emb = await rag.get_embedding(query, input_type="query")
    
    print("Embedding vector length:", len(emb))
    print("Top retrieved chunks:")
    print("="*60)
    
    results = vstore.query_hybrid(query, emb, intent=None, top_k=5)
    for r in results:
        print(f"Content: {r['content']}")
        print(f"Source: {r['source']} | Page: {r['metadata'].get('page')}")
        print(f"Hybrid Score: {r['score']:.4f} (Semantic: {r['semantic_score']:.4f}, Keyword: {r['keyword_score']:.4f})")
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test())
