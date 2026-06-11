import json
import logging
import uuid
import asyncio
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.agents.debugger_agent import DebuggerAgent
from app.agents.teacher_agent import TeacherAgent
from app.agents.interviewer_agent import InterviewerAgent
from app.ai.prompts.coordinator_prompts import (
    COORDINATOR_JSON_SCHEMA,
    COORDINATOR_SYSTEM_INSTRUCTION,
    COORDINATOR_USER_PROMPT,
)

logger = logging.getLogger("codeguru")


class CoordinatorAgent(BaseAgent):
    """Coordinator Agent responsible for identifying developer intent and routing requests to specialized agents."""

    async def route_request(self, user_input: str) -> Dict[str, Any]:
        """Use LLM to categorize the incoming user request into review, dsa, or general intents."""
        prompt = COORDINATOR_USER_PROMPT.format(user_input=user_input)
        
        try:
            raw_response = await self._call_llm(
                prompt=prompt,
                system_instruction=COORDINATOR_SYSTEM_INSTRUCTION,
                schema=COORDINATOR_JSON_SCHEMA
            )

            # Clean markdown wrappers if returned by LLM fallbacks
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            
            # Assert keys exist
            required = ["intent", "confidence", "reasoning", "parameters"]
            for key in required:
                if key not in parsed:
                    raise KeyError(f"Missing required key: {key}")

            return parsed
        except Exception as e:
            logger.error(f"CoordinatorAgent failed to process or parse: {str(e)}", exc_info=True)
            return {
                "intent": "general",
                "confidence": 1.0,
                "reasoning": f"Default fallback routing due to error: {str(e)}",
                "parameters": {}
            }

    async def route_and_execute(
        self,
        user_input: str,
        user_id: uuid.UUID,
        db: AsyncSession,
        session_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Classify user intent, route request, execute specialized agents, and package response."""
        routing_info = await self.route_request(user_input)
        intent = routing_info.get("intent", "general")
        params = routing_info.get("parameters", {})
        
        logger.info(f"Coordinator routing user query. Intent={intent}, params={params}")

        # 1. AI Code Review routing
        if intent == "review":
            code = params.get("code") or user_input
            language = params.get("language") or "python"
            
            reviewer = ReviewerAgent(self.provider)
            debugger = DebuggerAgent(self.provider)
            
            try:
                review_task = reviewer.review_code(code, language)
                debug_task = debugger.debug_code(code, language)
                
                review_res, debug_res = await asyncio.gather(review_task, debug_task)
                
                return {
                    "intent": "review",
                    "reasoning": routing_info.get("reasoning"),
                    "response": f"I have analyzed your {language} code and compiled a review scorecard.",
                    "data": {
                        "score": review_res.get("score", 70),
                        "summary": review_res.get("summary", ""),
                        "issues": review_res.get("issues", []),
                        "refactored_code": review_res.get("refactored_code", code),
                        "has_bugs": debug_res.get("has_bugs", False),
                        "bugs": debug_res.get("bugs", [])
                    }
                }
            except Exception as e:
                logger.error(f"Failed during concurrent code review routing: {str(e)}", exc_info=True)
                return {
                    "intent": "review",
                    "reasoning": f"Error during review routing: {str(e)}",
                    "response": "An error occurred while compiling your code review.",
                    "data": {}
                }

        # 2. DSA Mentor routing
        elif intent == "dsa":
            problem_id = params.get("problem_id") or "two-sum"
            code = params.get("code") or ""
            language = params.get("language") or "python"
            
            teacher = TeacherAgent(self.provider)
            try:
                # If code is supplied, run the concept stepper/dry-run analysis
                if code:
                    explanation = await teacher.explain_concept(
                        problem_name=problem_id.replace("-", " ").title(),
                        code=code,
                        language=language
                    )
                    return {
                        "intent": "dsa",
                        "reasoning": routing_info.get("reasoning"),
                        "response": f"I've compiled a trace report and Big-O analysis for your {problem_id} solution.",
                        "data": explanation
                    }
                else:
                    # Generic algorithm chat explanation fallback
                    prompt = f"Explain the concept of {problem_id} in algorithms, detailing standard approaches and optimal Big-O complexity."
                    response_text = await self._call_llm(
                        prompt=prompt,
                        system_instruction="You are a senior computer science professor guiding a student in DSA topics."
                    )
                    return {
                        "intent": "dsa",
                        "reasoning": routing_info.get("reasoning"),
                        "response": response_text,
                        "data": {}
                    }
            except Exception as e:
                logger.error(f"Failed during DSA mentor routing: {str(e)}", exc_info=True)
                return {
                    "intent": "dsa",
                    "reasoning": f"Error during DSA routing: {str(e)}",
                    "response": "An error occurred while generating the DSA guide.",
                    "data": {}
                }

        # 3. Technical Mock Interview routing
        elif intent == "interview":
            interviewer = InterviewerAgent(self.provider)
            try:
                # If an active session is in play, we process inside the session flow
                if session_id:
                    # In a real API flow, we fetch messages from DB first.
                    # This fallback mock response simulates the next interview turn.
                    next_resp = await interviewer.generate_next_response(
                        topic=params.get("topic") or "Coding",
                        difficulty=params.get("difficulty") or "Medium",
                        messages=[{"role": "user", "content": user_input}]
                    )
                    return {
                        "intent": "interview",
                        "reasoning": routing_info.get("reasoning"),
                        "response": next_resp.get("response", "Could you elaborate on that approach?"),
                        "data": {
                            "session_id": str(session_id),
                            "focus_area": next_resp.get("focus_area", "Algorithms")
                        }
                    }
                else:
                    # Inform the user how to initiate a structured session
                    return {
                        "intent": "interview",
                        "reasoning": routing_info.get("reasoning"),
                        "response": "I see you're asking about mock interviews! To start a structured mock coding or system design interview session, navigate to the Interview Simulator lobby and click 'Start Session'.",
                        "data": {}
                    }
            except Exception as e:
                logger.error(f"Failed during interview routing: {str(e)}", exc_info=True)
                return {
                    "intent": "interview",
                    "reasoning": f"Error during interview routing: {str(e)}",
                    "response": "An error occurred while routing to the interviewer agent.",
                    "data": {}
                }

        # 4. General fallback chat Q&A
        else:
            try:
                system_instr = "You are CodeGuru AI, a senior staff software engineer and programming mentor. Help the user answer their questions."
                response_text = await self._call_llm(
                    prompt=user_input,
                    system_instruction=system_instr
                )
                return {
                    "intent": "general",
                    "reasoning": routing_info.get("reasoning", "Conversational fallback"),
                    "response": response_text,
                    "data": {}
                }
            except Exception as e:
                logger.error(f"Failed general fallback routing: {str(e)}", exc_info=True)
                return {
                    "intent": "general",
                    "reasoning": "Fallback due to exception",
                    "response": "Hello! I am CodeGuru AI. Let me know if you need code reviews, DSA step traces, or mock interview prep.",
                    "data": {}
                }
