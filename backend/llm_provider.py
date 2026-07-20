import abc
import json
import logging
from typing import AsyncGenerator, Dict, Any, List
import httpx

logger = logging.getLogger(__name__)

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    async def generate_stream(
        self, 
        messages: List[Dict[str, str]], 
        model: str, 
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion chunks."""
        pass

    @abc.abstractmethod
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        model: str, 
        temperature: float = 0.7
    ) -> str:
        """Get complete chat completion response."""
        pass

    async def warmup(self, model: str) -> None:
        """Warm up the provider by pre-loading models if applicable."""
        pass


class NvidiaProvider(LLMProvider):
    def __init__(self):
        from nvidia_client import NvidiaClient
        self.client = NvidiaClient()

    async def generate_stream(
        self, 
        messages: List[Dict[str, str]], 
        model: str, 
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        async for chunk in self.client.stream_chat(messages, temperature=temperature):
            yield chunk

    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        model: str, 
        temperature: float = 0.7
    ) -> str:
        return await self.client.generate(messages, temperature=temperature)



class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def generate_stream(
        self, messages: List[Dict[str, str]], model: str, temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": temperature
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        logger.error(f"OpenAI error: {err_text}")
                        yield "Error contacting OpenAI API."
                        return
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
            except Exception as e:
                yield f"Error connecting to OpenAI: {str(e)}"

    async def generate(
        self, messages: List[Dict[str, str]], model: str, temperature: float = 0.7
    ) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "temperature": temperature
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code != 200:
                    return f"Error contacting OpenAI API: {response.text}"
                return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                return f"Error connecting to OpenAI: {str(e)}"


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def generate_stream(
        self, messages: List[Dict[str, str]], model: str, temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        # Google Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={self.api_key}"
        # Convert standard OpenAI/Ollama messages to Gemini structure
        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": m["content"]}]
            })
            
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature
            }
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        yield "Error contacting Gemini API."
                        return
                    async for line in response.aiter_lines():
                        if line:
                            # Gemini stream returns array elements
                            cleaned_line = line.strip().lstrip("[").rstrip(",").rstrip("]")
                            if not cleaned_line:
                                continue
                            try:
                                data = json.loads(cleaned_line)
                                text = data["candidates"][0]["content"]["parts"][0]["text"]
                                if text:
                                    yield text
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue
            except Exception as e:
                yield f"Error connecting to Gemini: {str(e)}"

    async def generate(
        self, messages: List[Dict[str, str]], model: str, temperature: float = 0.7
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": m["content"]}]
            })
            
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature
            }
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    return f"Error contacting Gemini API: {response.text}"
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                return f"Error connecting to Gemini: {str(e)}"


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def generate_stream(
        self, messages: List[Dict[str, str]], model: str, temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        # Format system prompt separate for Claude
        system_text = ""
        user_messages = []
        for m in messages:
            if m["role"] == "system":
                system_text = m["content"]
            else:
                user_messages.append(m)
                
        payload = {
            "model": model,
            "messages": user_messages,
            "system": system_text,
            "stream": True,
            "max_tokens": 4096,
            "temperature": temperature
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        yield "Error contacting Anthropic API."
                        return
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            try:
                                data = json.loads(data_str)
                                if data.get("type") == "content_block_delta":
                                    chunk = data["delta"].get("text", "")
                                    if chunk:
                                        yield chunk
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                yield f"Error connecting to Anthropic: {str(e)}"

    async def generate(
        self, messages: List[Dict[str, str]], model: str, temperature: float = 0.7
    ) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        system_text = ""
        user_messages = []
        for m in messages:
            if m["role"] == "system":
                system_text = m["content"]
            else:
                user_messages.append(m)
                
        payload = {
            "model": model,
            "messages": user_messages,
            "system": system_text,
            "stream": False,
            "max_tokens": 4096,
            "temperature": temperature
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code != 200:
                    return f"Error contacting Anthropic API: {response.text}"
                return response.json()["content"][0]["text"]
            except Exception as e:
                return f"Error connecting to Anthropic: {str(e)}"


def get_llm_provider(provider_name: str, config: Dict[str, Any]) -> LLMProvider:
    provider_name = provider_name.lower()
    if provider_name == "nvidia":
        return NvidiaProvider()
    elif provider_name == "openai":
        return OpenAIProvider(api_key=config.get("OPENAI_API_KEY", ""))
    elif provider_name == "gemini":
        return GeminiProvider(api_key=config.get("GEMINI_API_KEY", ""))
    elif provider_name == "claude":
        return ClaudeProvider(api_key=config.get("CLAUDE_API_KEY", ""))
    else:
        # Default fallback
        return NvidiaProvider()
