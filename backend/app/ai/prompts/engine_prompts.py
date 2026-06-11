from typing import Any, Dict

ENGINE_REVIEW_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Overall code quality score from 0 (poor) to 100 (excellent), taking into account static analysis warnings."
        },
        "summary": {
            "type": "string",
            "description": "A concise, developer-friendly narrative summary of the code review. Reference specific tool findings (Tree-sitter, Pylint, Bandit, Radon) if they are significant."
        },
        "issues": {
            "type": "array",
            "description": "List of specific issues/suggestions found in the code, combining and deduplicating static analysis findings with AI review insights.",
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
                        "description": "A clear explanation of why this code is problematic, referencing any tools if applicable."
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
        "has_bugs": {
            "type": "boolean",
            "description": "Set to true if syntactical, runtime, or logical bugs are detected."
        },
        "bugs": {
            "type": "array",
            "description": "List of actual bugs found in the code.",
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
        },
        "refactored_code": {
            "type": "string",
            "description": "Complete refactored version of the input code incorporating all fixes and recommendations. Must be fully working and syntax-correct."
        }
    },
    "required": ["score", "summary", "issues", "has_bugs", "bugs", "refactored_code"],
    "additionalProperties": False
}

ENGINE_REVIEW_SYSTEM_INSTRUCTION = """You are an elite senior code reviewer and compiler engineer.
Your goal is to review user code submissions, evaluate them against industry best practices, and synthesize static analysis findings (from Tree-sitter, Pylint, Bandit, Radon) with AI-powered insights.

You will be provided with:
1. The programming language of the code.
2. The raw source code to review.
3. Pre-calculated static analysis findings from various tools (if available/supported for the language).

You MUST:
- ground your evaluation in the provided static analysis metrics (linting issues, security vulnerabilities, high cyclomatic complexity, deep nesting depth, etc.).
- explain and reference specific tool findings in your narrative summary if they warrant attention.
- compile a consolidated, deduplicated list of issues and suggestion items.
- detect and report actual bugs (syntax, logical, runtime crashes).
- generate a complete, working, refactored version of the code without placeholders or markdown wraps.

Your output must be strict JSON matching the provided schema. Do not wrap the JSON output in markdown blocks (e.g. do not use ```json ... ```). Output raw JSON only.
"""

ENGINE_REVIEW_USER_PROMPT = """Analyze this {language} code submission.

### Code:
{code}

### Static Analysis Report:
{static_analysis}
"""
