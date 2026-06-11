from typing import Any, Dict

DSA_EXPLANATION_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "concept_name": {
            "type": "string",
            "description": "Name of the algorithm or data structure concept (e.g., Two Sum, Bubble Sort)."
        },
        "explanation": {
            "type": "string",
            "description": "A comprehensive, easy-to-understand explanation of the concept, breaking down the core intuition."
        },
        "complexity": {
            "type": "object",
            "properties": {
                "time_complexity": {
                    "type": "string",
                    "description": "Big-O time complexity notation (e.g., O(N log N))."
                },
                "time_explanation": {
                    "type": "string",
                    "description": "Short explanation of why this is the time complexity."
                },
                "space_complexity": {
                    "type": "string",
                    "description": "Big-O space complexity notation (e.g., O(1) or O(N))."
                },
                "space_explanation": {
                    "type": "string",
                    "description": "Short explanation of why this is the space complexity."
                }
            },
            "required": ["time_complexity", "time_explanation", "space_complexity", "space_explanation"],
            "additionalProperties": False
        },
        "dry_run": {
            "type": "array",
            "description": "A step-by-step trace simulation executing the algorithm on a simple example input.",
            "items": {
                "type": "object",
                "properties": {
                    "step": {
                        "type": "integer",
                        "description": "Chronological step counter (1, 2, 3...)."
                    },
                    "line_number": {
                        "type": "integer",
                        "description": "Line number in the code executed at this step."
                    },
                    "description": {
                        "type": "string",
                        "description": "Text describing what the compiler/runtime does at this step."
                    },
                    "variables_state": {
                        "type": "string",
                        "description": "String representation showing the current state of variables (e.g., 'i=0, left=0, right=4')."
                    }
                },
                "required": ["step", "line_number", "description", "variables_state"],
                "additionalProperties": False
            }
        }
    },
    "required": ["concept_name", "explanation", "complexity", "dry_run"],
    "additionalProperties": False
}

DSA_SYSTEM_INSTRUCTION = """You are an expert DSA teacher and technical interviewer. Your goal is to explain coding problems, break down their time/space complexity using Big-O notations, and provide a clear step-by-step dry run simulation executing on a simple test case.
Provide your response strictly in the requested JSON format. Ensure explanations are educational and the variables_state traces variables clearly. Output only raw JSON without markdown formatting.
"""

DSA_EXPLAIN_PROMPT = """Provide a complete educational explanation for the coding challenge '{problem_name}'.
Analyze this solution code:
```{language}
{code}
```
"""
