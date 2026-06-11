import json
import logging
from typing import Any, Dict, List
from app.agents.base_agent import BaseAgent
from app.ai.prompts.interview_prompts import (
    INTERVIEW_CHAT_SCHEMA,
    INTERVIEW_EVALUATION_SCHEMA,
    INTERVIEW_SYSTEM_INSTRUCTION,
    INTERVIEW_EVAL_SYSTEM_INSTRUCTION,
    INTERVIEW_CHAT_PROMPT,
    INTERVIEW_EVAL_PROMPT,
)

logger = logging.getLogger("codeguru")


class InterviewerAgent(BaseAgent):
    """AI Agent acting as a technical interviewer and evaluator."""

    def _format_chat_history(self, messages: List[Dict[str, str]]) -> str:
        """Helper to format the session messages list into a readable chat log string."""
        formatted = []
        for msg in messages:
            role = "Interviewer" if msg.get("role") == "interviewer" else "Candidate"
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)

    async def generate_next_response(
        self,
        topic: str,
        difficulty: str,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Generate the interviewer's next response based on chat history."""
        system_instruction_tpl, _ = await self.prompt_service.get_prompt(self.db, "interview_system")
        system_instruction = system_instruction_tpl.format(
            topic=topic,
            difficulty=difficulty
        )

        chat_history_str = self._format_chat_history(messages)
        user_prompt_tpl, _ = await self.prompt_service.get_prompt(self.db, "interview_chat")
        prompt = user_prompt_tpl.format(chat_history_str=chat_history_str)

        try:
            raw_response = await self._call_llm(
                prompt=prompt,
                system_instruction=system_instruction,
                schema=INTERVIEW_CHAT_SCHEMA,
                complexity="simple"
            )

            # Clean potential markdown JSON wrapping
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            # Ensure required schema keys exist
            if "response" not in parsed:
                parsed["response"] = "Let's proceed. Could you explain your approach in more detail?"
            if "focus_area" not in parsed:
                parsed["focus_area"] = "Algorithms"

            return parsed
        except Exception as e:
            logger.error(f"InterviewerAgent failed to generate chat response: {str(e)}", exc_info=True)
            # Fallback interviewer response
            return {
                "response": "Could you tell me more about how you would optimize your solution or handle potential edge cases?",
                "focus_area": "Optimizations"
            }

    async def evaluate_session(
        self,
        topic: str,
        difficulty: str,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Compile a complete feedback report and score at the end of the session."""
        chat_history_str = self._format_chat_history(messages)
        user_prompt_tpl, _ = await self.prompt_service.get_prompt(self.db, "interview_eval")
        prompt = user_prompt_tpl.format(
            topic=topic,
            difficulty=difficulty,
            chat_history_str=chat_history_str
        )
        system_instruction, _ = await self.prompt_service.get_prompt(self.db, "interview_eval_system")

        try:
            raw_response = await self._call_llm(
                prompt=prompt,
                system_instruction=system_instruction,
                schema=INTERVIEW_EVALUATION_SCHEMA,
                complexity="complex"
            )

            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            required_keys = [
                "score",
                "summary",
                "strengths",
                "weakness_areas",
                "correct_code_suggestions",
                "improvement_tips"
            ]
            for key in required_keys:
                if key not in parsed:
                    raise KeyError(f"Missing required evaluation field: {key}")

            return parsed
        except Exception as e:
            logger.error(f"InterviewerAgent failed to evaluate interview session: {str(e)}", exc_info=True)
            # Safe default fallback evaluation structure
            return {
                "score": 50,
                "summary": "The interview session was completed, but automated evaluation failed.",
                "strengths": ["Completed the mock interview session."],
                "weakness_areas": ["Could not extract detailed weakness analysis."],
                "correct_code_suggestions": "// Automated evaluation error. Please review your session manually.",
                "improvement_tips": ["Retry with a fresh interview session or check provider logs."]
            }
