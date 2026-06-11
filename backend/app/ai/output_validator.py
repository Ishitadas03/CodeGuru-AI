import json
import logging
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError
from app.ai.router import AIRouter

logger = logging.getLogger("codeguru.output_validator")

T = TypeVar("T", bound=BaseModel)


class AIOutputValidator:
    """Validates LLM outputs against Pydantic models, retrying on failure with error feedback."""

    def __init__(self, router: Optional[AIRouter] = None) -> None:
        self.router = router or AIRouter()

    async def generate_and_validate(
        self,
        pydantic_model: Type[T],
        prompt: str,
        system_instruction: Optional[str] = None,
        complexity: str = "simple",
        max_validation_attempts: int = 3
    ) -> tuple[T, str]:
        """Generate content from LLM and validate it against the Pydantic schema.

        If validation fails, retries up to max_validation_attempts - 1 times,
        incorporating the error feedback into the prompt.

        Returns:
            Tuple of (validated_pydantic_model_instance, model_used)
        """
        schema = pydantic_model.model_json_schema()
        current_prompt = prompt
        model_used = "unknown"

        for attempt in range(max_validation_attempts):
            try:
                # Call generator
                raw_response, model_used = await self.router.generate_with_fallback(
                    prompt=current_prompt,
                    system_instruction=system_instruction,
                    schema=schema,
                    complexity=complexity
                )

                # Standardize JSON cleanups
                cleaned = raw_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()

                # Parse JSON
                parsed_json = json.loads(cleaned)

                # Validate against Pydantic
                validated_obj = pydantic_model.model_validate(parsed_json)
                return validated_obj, model_used

            except (json.JSONDecodeError, ValidationError, KeyError) as e:
                logger.warning(
                    f"Validation attempt {attempt + 1}/{max_validation_attempts} failed: {str(e)}"
                )
                if attempt == max_validation_attempts - 1:
                    logger.error("All validation attempts failed. Raising exception.")
                    raise e

                # Augment prompt with feedback
                error_msg = str(e)
                current_prompt = (
                    f"{prompt}\n\n"
                    f"--- ATTEMPT ERROR ---\n"
                    f"Your previous response failed validation against the schema.\n"
                    f"Error details: {error_msg}\n"
                    f"Please fix the schema conformances and output valid JSON only."
                )
