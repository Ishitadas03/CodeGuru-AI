import logging
import asyncio
from typing import Any, AsyncGenerator, Dict, Optional
from app.ai.providers.base import AbstractAIProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.core.config import settings

logger = logging.getLogger("codeguru.ai_router")


class AIRouter:
    """Dynamic model router targeting task complexity and handling retries/fallbacks."""

    def __init__(self) -> None:
        self.fast_model = settings.GEMINI_FAST_MODEL or "gemini-2.0-flash"
        self.primary_model = settings.GEMINI_PRIMARY_MODEL or "gemini-2.5-pro"
        self.fallback_model = settings.OPENAI_MODEL or "gpt-4o-mini"

    def get_provider(self, complexity: str = "simple", force_fallback: bool = False) -> AbstractAIProvider:
        """Resolve primary provider or fallback based on complexity and status."""
        if force_fallback:
            logger.warning(f"Routing task to fallback model: {self.fallback_model}")
            return OpenAIProvider(model=self.fallback_model)

        if complexity == "complex":
            model = self.primary_model
        else:
            model = self.fast_model

        return GeminiProvider(model=model)

    async def generate_with_fallback(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        complexity: str = "simple"
    ) -> tuple[str, str]:
        """Execute text generation with up to 3 retries and fallback to OpenAI.

        Returns:
            Tuple of (response_text, model_used)
        """
        provider = self.get_provider(complexity=complexity)
        model_used = getattr(provider, "model", self.fast_model)
        
        # In mock key mode, bypass actual external calls to avoid 401s
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "MOCK_KEY":
            res = await provider.generate(prompt, system_instruction, schema)
            return res, model_used

        retries = 3
        delay = 1.0  # Initial delay for exponential backoff

        for attempt in range(retries):
            try:
                # Call generate
                res = await provider.generate(prompt, system_instruction, schema)
                
                # Check if mock response was returned because of failure
                if "Failed to complete" in res or "System error" in res:
                    raise RuntimeError(f"Provider generate failed: {res}")
                
                return res, model_used
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{retries} failed for model {model_used}: {str(e)}"
                )
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2
                else:
                    logger.error(
                        f"Failed all {retries} attempts for model {model_used}. Falling back to OpenAI."
                    )

        # Trigger fallback to OpenAI
        fallback_provider = self.get_provider(complexity=complexity, force_fallback=True)
        model_used = fallback_provider.model
        
        try:
            res = await fallback_provider.generate(prompt, system_instruction, schema)
            return res, model_used
        except Exception as e:
            logger.critical(f"Fallback model {model_used} also failed: {str(e)}")
            raise e

    async def stream_with_fallback(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        complexity: str = "simple"
    ) -> AsyncGenerator[tuple[str, str], None]:
        """Stream chunks with fallback options."""
        provider = self.get_provider(complexity=complexity)
        model_used = getattr(provider, "model", self.fast_model)

        # In mock key mode, bypass actual external calls
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "MOCK_KEY":
            async for chunk in provider.stream(prompt, system_instruction):
                yield chunk, model_used
            return

        try:
            async for chunk in provider.stream(prompt, system_instruction):
                yield chunk, model_used
        except Exception as e:
            logger.warning(f"Streaming failed for model {model_used}, falling back to OpenAI: {str(e)}")
            fallback_provider = self.get_provider(complexity=complexity, force_fallback=True)
            model_used = fallback_provider.model
            async for chunk in fallback_provider.stream(prompt, system_instruction):
                yield chunk, model_used
