import asyncio
import time
import httpx
import json

async def run_benchmark():
    url = "http://localhost:8000/api/chat"
    payload = {
        "session_id": "benchmark_session_999",
        "message": "What is CittaAI's official products and solutions?"
    }
    
    print("="*60)
    print("STARTING CITTAAI STREAMING BENCHMARK")
    print("="*60)
    
    # Run first query (Cache Miss / RAG Cold Start test)
    print("\n[Test 1] Executing Cache Miss RAG Query...")
    start_time = time.time()
    first_token_time = None
    total_tokens = 0
    full_text = ""
    citations = []
    suggested_questions = []
    redirect = None
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            if response.status_code != 200:
                print(f"Error: Server returned status code {response.status_code}")
                return
                
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        if data.get("done") is True:
                            citations = data.get("citations", [])
                            suggested_questions = data.get("suggested_questions", [])
                            redirect = data.get("redirect")
                        elif "text" in data:
                            if not first_token_time:
                                first_token_time = time.time() - start_time
                            text = data["text"]
                            full_text += text
                            # Estimate token count (roughly 4 characters per token)
                            total_tokens += len(text) // 4 if len(text) >= 4 else 1
                    except json.JSONDecodeError:
                        pass
                        
    total_time = time.time() - start_time
    streaming_time = (total_time - first_token_time) if first_token_time else 0.0
    tokens_per_second = total_tokens / streaming_time if streaming_time > 0 else 0.0
    
    print("\n--- RESULTS (Cache Miss) ---")
    print(f"First Token Latency : {first_token_time:.4f} seconds (Target: < 1.0s)")
    print(f"Total Response Time : {total_time:.4f} seconds")
    print(f"Streaming Duration  : {streaming_time:.4f} seconds")
    print(f"Estimated Tokens    : {total_tokens} tokens")
    print(f"Tokens/Second       : {tokens_per_second:.2f} t/s")
    print(f"Citations Retrieved : {citations}")
    print(f"Suggested Questions : {suggested_questions}")
    print(f"Redirect Target     : {redirect}")
    print(f"Answer Sample       : {full_text[:120]}...")
    
    # Wait a brief moment to allow background tasks to complete cache write
    print("\nWaiting 1 second for background tasks to commit...")
    await asyncio.sleep(1.0)
    
    # Run second query (Cache Hit test)
    print("\n[Test 2] Executing Cache Hit Query...")
    start_time = time.time()
    first_token_time_hit = None
    total_tokens_hit = 0
    full_text_hit = ""
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        if not data.get("done") and "text" in data:
                            if not first_token_time_hit:
                                first_token_time_hit = time.time() - start_time
                            text = data["text"]
                            full_text_hit += text
                            total_tokens_hit += len(text) // 4 if len(text) >= 4 else 1
                    except json.JSONDecodeError:
                        pass
                        
    total_time_hit = time.time() - start_time
    print("\n--- RESULTS (Cache Hit) ---")
    print(f"First Token Latency : {first_token_time_hit:.4f} seconds (Target: < 0.05s)")
    print(f"Total Response Time : {total_time_hit:.4f} seconds (Target: < 0.1s)")
    print(f"Estimated Tokens    : {total_tokens_hit} tokens")
    print(f"Answer Sample       : {full_text_hit[:120]}...")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
