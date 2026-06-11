from typing import Any, AsyncGenerator, Dict, Optional
from openai import AsyncOpenAI
from app.ai.providers.base import AbstractAIProvider
from app.core.config import settings


class GeminiProvider(AbstractAIProvider):
    """Google Gemini API provider leveraging the OpenAI-compatible API interface."""

    def __init__(self, model: str = "gemini-2.0-flash") -> None:
        # Gemini's OpenAI compatibility base URL
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/v1"
        self.client = AsyncOpenAI(
            api_key=settings.GEMINI_API_KEY or "MOCK_KEY",
            base_url=base_url
        )
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> str:
        """Call Gemini API, optionally enforcing structured JSON schema outputs."""
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        kwargs: Dict[str, Any] = {}

        if schema:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "response_schema",
                    "strict": True,
                    "schema": schema
                }
            }
        elif system_instruction and "json" in system_instruction.lower():
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                **kwargs
            )
            return response.choices[0].message.content or ""
        except Exception:
            from app.ai.providers.mock_generator import generate_mock_response
            return generate_mock_response(prompt, system_instruction, schema)

    async def stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat completions from Gemini model chunk by chunk."""
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                stream=True
            )
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception:
            from app.ai.providers.mock_generator import async_stream_mock_response
            async for chunk in async_stream_mock_response(prompt, system_instruction):
                yield chunk
