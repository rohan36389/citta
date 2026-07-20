import os
import json
import logging
import asyncio
import httpx
from typing import AsyncGenerator, Dict, Any, List
import config

logger = logging.getLogger(__name__)

class NvidiaClient:
    def __init__(self):
        self.api_key = config.NVIDIA_API_KEY
        self.base_url = config.NVIDIA_BASE_URL
        self.model = config.NVIDIA_MODEL
        self.timeout = config.TIMEOUT
        
    def _get_headers(self) -> Dict[str, str]:
        # Fetch dynamically if it updates
        api_key = config.NVIDIA_API_KEY or os.environ.get("NVIDIA_API_KEY", "")
        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    async def stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.4
    ) -> AsyncGenerator[str, None]:
        """Streams completion chunks from the NVIDIA API with exponential backoff and rate limit handling."""
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": config.MAX_TOKENS,
            "top_p": config.TOP_P
        }

        max_retries = 3
        backoff = 1.0
        success = False
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream("POST", url, headers=self._get_headers(), json=payload) as response:
                        if response.status_code == 200:
                            success = True
                            async for line in response.aiter_lines():
                                if line.startswith("data: "):
                                    data_str = line[6:].strip()
                                    if data_str == "[DONE]":
                                        break
                                    try:
                                        data = json.loads(data_str)
                                        chunk = data["choices"][0]["delta"].get("content", "")
                                        if chunk:
                                            yield chunk
                                    except (json.JSONDecodeError, KeyError, IndexError):
                                        continue
                            break  # Exit retry loop on success
                        
                        elif response.status_code == 429:
                            logger.warning(f"Rate limited (429) on chat stream, retrying in {backoff}s...")
                            await asyncio.sleep(backoff)
                            backoff *= 2
                        else:
                            err_text = await response.aread()
                            logger.error(f"NVIDIA API error {response.status_code}: {err_text.decode('utf-8', errors='ignore')}")
                            raise httpx.HTTPStatusError(
                                message=f"NVIDIA API Error {response.status_code}",
                                request=None,
                                response=response
                            )
                            
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == max_retries - 1:
                    logger.exception("NVIDIA API connection failed after maximum retries")
                    yield "The CittaAI Enterprise AI Consultant is temporarily unavailable. Please try again shortly."
                    return
                logger.warning(f"NVIDIA API request failed on attempt {attempt+1}: {e}. Retrying in {backoff}s...")
                await asyncio.sleep(backoff)
                backoff *= 2

    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.4
    ) -> str:
        """Retrieves a complete chat completion response from the NVIDIA API with error handling and retries."""
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": temperature,
            "max_tokens": config.MAX_TOKENS,
            "top_p": config.TOP_P
        }

        max_retries = 3
        backoff = 1.0
        
        import time
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    req_start = time.time()
                    async with client.stream("POST", url, headers=self._get_headers(), json=payload) as response:
                        ttfb = time.time() - req_start
                        if response.status_code == 200:
                            body = await response.aread()
                            download_time = time.time() - (req_start + ttfb)
                            data = json.loads(body)
                            content = data["choices"][0]["message"]["content"]
                            usage = data.get("usage", {})
                            
                            metrics = {
                                "provider": "NVIDIA",
                                "model": self.model,
                                "prompt_tokens": usage.get("prompt_tokens", 0),
                                "completion_tokens": usage.get("completion_tokens", 0),
                                "total_tokens": usage.get("total_tokens", 0),
                                "request_upload_ms": 0,
                                "network_wait_ms": int(ttfb * 1000),
                                "estimated_inference_time_ms": 0,
                                "response_download_ms": int(download_time * 1000),
                                "total_llm_duration_ms": int((time.time() - start_time) * 1000)
                            }
                            return content, metrics
                        elif response.status_code == 429:
                            logger.warning(f"Rate limited (429) on chat completions, retrying in {backoff}s...")
                            await asyncio.sleep(backoff)
                            backoff *= 2
                        else:
                            err_text = await response.aread()
                            logger.error(f"NVIDIA API error {response.status_code}: {err_text.decode('utf-8', errors='ignore')}")
                            raise httpx.HTTPStatusError(
                                message=f"NVIDIA API Error {response.status_code}",
                                request=None,
                                response=response
                            )
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == max_retries - 1:
                    logger.exception("NVIDIA API generate failed after maximum retries")
                    return "The CittaAI Enterprise AI Consultant is temporarily unavailable. Please try again shortly."
                logger.warning(f"NVIDIA API request failed on attempt {attempt+1}: {e}. Retrying in {backoff}s...")
                await asyncio.sleep(backoff)
                backoff *= 2
        
        return "The CittaAI Enterprise AI Consultant is temporarily unavailable. Please try again shortly."
