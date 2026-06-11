import json
import logging
from typing import Any, Dict
from app.agents.base_agent import BaseAgent
from app.ai.prompts.dsa_prompts import (
    DSA_EXPLANATION_JSON_SCHEMA,
    DSA_SYSTEM_INSTRUCTION,
    DSA_EXPLAIN_PROMPT,
)

logger = logging.getLogger("codeguru")


class TeacherAgent(BaseAgent):
    """Agent that explains computer science algorithms, complexities, and provides code dry-runs."""

    async def explain_concept(
        self,
        problem_name: str,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """Call LLM with DSA schemas and return structured teaching reports."""
        system_instruction, _ = await self.prompt_service.get_prompt(self.db, "dsa_system")
        user_prompt_tpl, _ = await self.prompt_service.get_prompt(self.db, "dsa_explain")
        prompt = user_prompt_tpl.format(
            problem_name=problem_name,
            code=code,
            language=language
        )

        try:
            raw_response = await self._call_llm(
                prompt=prompt,
                system_instruction=system_instruction,
                schema=DSA_EXPLANATION_JSON_SCHEMA,
                complexity="simple"
            )

            # Clean markdown JSON block wrappers if present
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            parsed = json.loads(cleaned_response)

            # Assert key schema fields exist
            required_keys = ["concept_name", "explanation", "complexity", "dry_run"]
            for key in required_keys:
                if key not in parsed:
                    raise KeyError(f"Missing required key in DSA explanation report: {key}")

            return parsed
        except Exception as e:
            logger.error(f"TeacherAgent failed to process or parse response: {str(e)}", exc_info=True)
            return {
                "concept_name": problem_name,
                "explanation": f"Failed to retrieve automated DSA explanation: {str(e)}",
                "complexity": {
                    "time_complexity": "N/A",
                    "time_explanation": "Error during complexity analysis.",
                    "space_complexity": "N/A",
                    "space_explanation": "Error during complexity analysis."
                },
                "dry_run": []
            }
