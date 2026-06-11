from typing import Any, Dict

COORDINATOR_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": ["review", "dsa", "interview", "general"],
            "description": "Route classification for the query: 'review' (code reviews), 'dsa' (DSA tutorials/concept traces/puzzles), 'interview' (technical mock interviews/behavioral chat), or 'general' (chat Q&A)."
        },
        "confidence": {
            "type": "number",
            "description": "Confidence of the classification from 0.0 to 1.0."
        },
        "reasoning": {
            "type": "string",
            "description": "Explanation of the routing classification decision."
        },
        "parameters": {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "The programming language detected, or null if none."
                },
                "problem_id": {
                    "type": "string",
                    "description": "The coding challenge ID/slug if referenced."
                }
            },
            "additionalProperties": True
        }
    },
    "required": ["intent", "confidence", "reasoning", "parameters"],
    "additionalProperties": False
}

COORDINATOR_SYSTEM_INSTRUCTION = """You are the CodeGuru AI routing coordinator. Your job is to analyze the user's prompt and classify it into one of these intents:
1. 'review': Submitting code blocks for review, feedback, rating, style checking, debugging, or optimization.
2. 'dsa': Asking DSA concepts, big-O, data structure explanations, trees, hash maps, complexity analysis, or standard problems (like two-sum).
3. 'interview': Inquiring about mock technical interviews, STAR behavioral practice, interview simulator workspace, or starting a practice session.
4. 'general': Standard software questions, greetings, setup issues, syntax clarifications, general chat, or generic coding support.

Output must be strict JSON matching the provided schema. Output raw JSON only.
"""

COORDINATOR_USER_PROMPT = """Determine the intent for:
{user_input}
"""
