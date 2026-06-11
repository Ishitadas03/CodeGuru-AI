import json
from typing import Any, AsyncGenerator, Dict, Optional
from openai import AsyncOpenAI
from app.ai.providers.base import AbstractAIProvider
from app.core.config import settings


class OpenAIProvider(AbstractAIProvider):
    """OpenAI API provider implementation managing chat completion runs and streaming."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "MOCK_KEY")
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> str:
        """Call OpenAI chat completion API, optionally enforcing structured JSON schema outputs."""
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        kwargs: Dict[str, Any] = {}
        
        # Leverage OpenAI strict structured outputs if schema is supplied
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
            # Standard JSON mode fallback
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
        """Stream chat completions from OpenAI model chunk by chunk."""
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
