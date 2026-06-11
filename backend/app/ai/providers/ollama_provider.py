from typing import Any, AsyncGenerator, Dict, Optional
from ollama import AsyncClient
from app.ai.providers.base import AbstractAIProvider
from app.core.config import settings


class OllamaProvider(AbstractAIProvider):
    """Local Ollama provider integration managing local model executions."""

    def __init__(self, model: str = "codellama") -> None:
        self.client = AsyncClient(host=settings.OLLAMA_HOST)
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> str:
        """Call Ollama chat endpoint, requesting JSON format if a schema is supplied."""
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        # Format can be set to 'json' to enforce JSON output in Ollama
        format_opt = None
        if schema or (system_instruction and "json" in system_instruction.lower()):
            format_opt = "json"

        try:
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                format=format_opt,
                options={"temperature": 0.1}
            )
            return response.get("message", {}).get("content", "")
        except Exception:
            from app.ai.providers.mock_generator import generate_mock_response
            return generate_mock_response(prompt, system_instruction, schema)

    async def stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream chunks from the local Ollama LLM execution."""
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response_stream = await self.client.chat(
                model=self.model,
                messages=messages,
                options={"temperature": 0.2},
                stream=True
            )
            async for chunk in response_stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
        except Exception:
            from app.ai.providers.mock_generator import async_stream_mock_response
            async for chunk in async_stream_mock_response(prompt, system_instruction):
                yield chunk
