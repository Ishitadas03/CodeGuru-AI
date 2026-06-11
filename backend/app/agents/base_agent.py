import uuid
import logging
import json
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.base import AbstractAIProvider
from app.core.config import SubscriptionTier
from app.services.usage_service import UsageService
from app.services.prompt_service import PromptService
from app.ai.router import AIRouter

logger = logging.getLogger("codeguru.base_agent")


class BaseAgent:
    """Base Agent wrapper coordinating LLM interaction protocols with cost control, routing, and logging."""

    def __init__(
        self,
        provider: AbstractAIProvider,
        db: Optional[AsyncSession] = None,
        user_id: Optional[uuid.UUID] = None,
        tier: SubscriptionTier = SubscriptionTier.FREE
    ) -> None:
        self.provider = provider
        self.db = db
        self.user_id = user_id
        self.tier = tier
        self.usage_service = UsageService()
        self.prompt_service = PromptService()
        self.router = AIRouter()

    async def _call_llm(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        complexity: str = "simple"
    ) -> str:
        """Execute the LLM call, checking budgets, routing by complexity, validating JSON structure, and logging costs."""
        # 1. Pre-call budget verification (if db & user_id are set)
        if self.db and self.user_id:
            prompt_tokens = self.usage_service.count_tokens(prompt)
            system_tokens = self.usage_service.count_tokens(system_instruction or "")
            await self.usage_service.verify_budgets(
                db=self.db,
                user_id=self.user_id,
                tier=self.tier,
                estimated_input_tokens=prompt_tokens + system_tokens
            )

        # 2. Self-correcting validation loop
        attempts = 3
        current_prompt = prompt
        response_text = ""
        model_used = "unknown"

        for attempt in range(attempts):
            try:
                response_text, model_used = await self.router.generate_with_fallback(
                    prompt=current_prompt,
                    system_instruction=system_instruction,
                    schema=schema,
                    complexity=complexity
                )

                # Validate JSON/schema compliance if expected
                is_json_expected = schema or (system_instruction and "json" in system_instruction.lower())
                if is_json_expected:
                    cleaned = response_text.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    cleaned = cleaned.strip()

                    parsed = json.loads(cleaned)

                    # Validate required keys if schema dictates them
                    if schema and "required" in schema:
                        for req_key in schema["required"]:
                            if req_key not in parsed:
                                raise KeyError(f"Required key '{req_key}' was missing from AI output.")
                
                # If we reached here without raising, validation passed
                break
            except (json.JSONDecodeError, KeyError, Exception) as e:
                logger.warning(
                    f"LLM output validation failed on attempt {attempt + 1}/{attempts}: {str(e)}"
                )
                if attempt == attempts - 1:
                    # Final attempt failed, propagate error or return fallback message
                    raise e
                
                # Feedback loop: append error to prompt
                current_prompt = (
                    f"{prompt}\n\n"
                    f"--- SCHEMATIC VALIDATION ERROR ---\n"
                    f"Your previous response was malformed or missing required keys.\n"
                    f"Error Details: {str(e)}\n"
                    f"Provide a valid JSON response conforming to the schema and requirements."
                )

        # 3. Post-call usage logging
        if self.db and self.user_id:
            input_tokens = self.usage_service.count_tokens(prompt) + self.usage_service.count_tokens(system_instruction or "")
            output_tokens = self.usage_service.count_tokens(response_text)
            await self.usage_service.record_usage(
                db=self.db,
                user_id=self.user_id,
                model=model_used,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

        return response_text
