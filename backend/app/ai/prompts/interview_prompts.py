from typing import Any, Dict

INTERVIEW_CHAT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "response": {
            "type": "string",
            "description": "The mock interviewer's response. Ask follow-up questions, challenge assumptions, or request code details without giving the solution."
        },
        "focus_area": {
            "type": "string",
            "description": "The category of this turn (e.g., 'System Design', 'Algorithms', 'Coding', 'Behavioral', 'Testing', 'Optimizations')."
        }
    },
    "required": ["response", "focus_area"],
    "additionalProperties": False
}

INTERVIEW_EVALUATION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "score": {
            "type": "integer",
            "description": "Candidate's final score out of 100."
        },
        "summary": {
            "type": "string",
            "description": "A high-level summary of the candidate's performance."
        },
        "strengths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of key strengths shown during the session."
        },
        "weakness_areas": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of technical or behavioral weakness areas observed."
        },
        "correct_code_suggestions": {
            "type": "string",
            "description": "Markdown formatted code snippet or architecture design showing the optimal solution for the problems discussed."
        },
        "improvement_tips": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Actionable steps or study topics to focus on next."
        }
    },
    "required": [
        "score",
        "summary",
        "strengths",
        "weakness_areas",
        "correct_code_suggestions",
        "improvement_tips"
    ],
    "additionalProperties": False
}

INTERVIEW_SYSTEM_INSTRUCTION = """You are an expert technical interviewer at a tier-1 tech company.
Your goal is to conduct a mock technical interview with the user.
Topic: {topic}
Difficulty: {difficulty}

Follow these instructions strictly:
1. Stay in character as a professional, polite, but challenging interviewer.
2. Ask one question at a time.
3. Start with an opening question or problem statement related to the topic and difficulty, then ask follow-up questions, challenge their trade-offs, and probe for optimizations based on their responses.
4. Do NOT give away the full solution or write the code for them during the interview chat. Keep them thinking and coding.
5. If the candidate makes a mistake, guide them gently with hints or ask about edge cases.
6. Provide your response strictly in the requested JSON format containing the 'response' and 'focus_area'. Do not include any formatting blocks outside the JSON.
"""

INTERVIEW_EVAL_SYSTEM_INSTRUCTION = """You are an expert technical interviewer evaluating a completed mock interview session.
You will be provided with the complete chat history of the interview.
Your task is to analyze the candidate's performance across communication, technical correctness, problem-solving, and trade-off decisions.
Rate the candidate on a scale of 0 to 100, list their strengths, areas for improvement, provide the optimal code/design suggestions, and list actionable tips.
Provide your response strictly in the requested JSON format matching the schema.
"""

INTERVIEW_CHAT_PROMPT = """Below is the current chat history of the interview session.
Review the history and generate the interviewer's next response:

{chat_history_str}
"""

INTERVIEW_EVAL_PROMPT = """Analyze the following interview history for a session on topic '{topic}' with difficulty '{difficulty}'.
Calculate their score out of 100 and compile the final feedback report:

{chat_history_str}
"""
