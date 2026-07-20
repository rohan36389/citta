import json
import httpx
import asyncio

async def test_chat():
    url = "http://localhost:8001/api/chat"
    payload = {
        "session_id": "test_verification_session",
        "message": "What is the Pharma OS solution offered by CittaAI?"
    }
    
    print("Sending message to CittaAI Consultant backend...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    print(f"Error: Status code {response.status_code}")
                    return
                
                print("\nStreaming response chunks:")
                print("="*60)
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        try:
                            data = json.loads(data_str)
                            if data.get("done"):
                                print("\n" + "="*60)
                                print("Citations:", data.get("citations"))
                                print("Suggested Questions:", data.get("suggested_questions"))
                                print("Redirect:", data.get("redirect"))
                                print("Preferences:", data.get("preferences"))
                            elif "text" in data:
                                print(data["text"], end="", flush=True)
                        except Exception as e:
                            print(f"\nError parsing line: {line} ({e})")
        except Exception as e:
            print(f"\nConnection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
