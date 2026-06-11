from typing import Any, Dict

# ------------------------------------------------------------------------------
# REVIEWER AGENT SCHEMAS & PROMPTS
# ------------------------------------------------------------------------------

REVIEWER_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Overall code quality score from 0 (poor) to 100 (excellent)."
        },
        "summary": {
            "type": "string",
            "description": "A concise, developer-friendly summary of the code review."
        },
        "issues": {
            "type": "array",
            "description": "List of specific issues found in the code.",
            "items": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["security", "readability", "performance", "style"],
                        "description": "The category classification of the issue."
                    },
                    "line": {
                        "type": "integer",
                        "description": "The 1-indexed line number where the issue occurs. If generic, set to 1."
                    },
                    "description": {
                        "type": "string",
                        "description": "A clear explanation of why this code is problematic."
                    },
                    "suggestion": {
                        "type": "string",
                        "description": "The suggested change or best practice recommendation."
                    }
                },
                "required": ["category", "line", "description", "suggestion"],
                "additionalProperties": False
            }
        },
        "refactored_code": {
            "type": "string",
            "description": "Complete refactored version of the input code incorporating all suggestions. Must be fully working and syntax-correct."
        }
    },
    "required": ["score", "summary", "issues", "refactored_code"],
    "additionalProperties": False
}

REVIEWER_SYSTEM_INSTRUCTION = """You are an elite senior code reviewer. Your goal is to review user code submissions, evaluate them against industry best practices, score them, and provide concrete refactoring recommendations.
You MUST analyze the code across 4 categories:
1. Security (vulnerabilities, injection, credentials exposure)
2. Readability (naming, structure, docstrings, flow)
3. Performance (complexity, unnecessary loops, allocations)
4. Style (formatting, conventions like PEP-8 or lint guidelines)

Your output must be strict JSON matching the provided schema. Do not write any markdown wrappers (like ```json) in your raw response; output raw JSON only. Ensure the refactored code is functional and does not contain placeholders.
"""

REVIEWER_USER_PROMPT = """Analyze this {language} code submission.

### Code:
{code}
"""


# ------------------------------------------------------------------------------
# DEBUGGER AGENT SCHEMAS & PROMPTS
# ------------------------------------------------------------------------------

DEBUGGER_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "has_bugs": {
            "type": "boolean",
            "description": "Set to true if syntactical or logical bugs are detected."
        },
        "bugs": {
            "type": "array",
            "description": "List of bugs found in the code.",
            "items": {
                "type": "object",
                "properties": {
                    "line": {
                        "type": "integer",
                        "description": "The 1-indexed line number of the bug."
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["error", "warning"],
                        "description": "Error means it will crash or fail. Warning means it is logical/risky code."
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed explanation of what the bug is and why it fails."
                    },
                    "fix": {
                        "type": "string",
                        "description": "Concrete code snippet or description showing how to fix this specific line."
                    }
                },
                "required": ["line", "severity", "description", "fix"],
                "additionalProperties": False
            }
        }
    },
    "required": ["has_bugs", "bugs"],
    "additionalProperties": False
}

DEBUGGER_SYSTEM_INSTRUCTION = """You are a compiler engineer and expert debugger agent. Your sole purpose is to parse the user's code, detect syntax errors, runtime crashes, logical bugs, and resource leaks, and report them with line numbers.
Your output must be strict JSON matching the provided schema. Do not write any markdown wrappers; output raw JSON only.
"""

DEBUGGER_USER_PROMPT = """Find all bugs in this {language} code.

### Code:
{code}
"""
