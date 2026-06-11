"""Gemini synthesizer — synthesizes static analysis results into an AI-powered review."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict

from app.ai.router import AIRouter
from app.ai.prompts.engine_prompts import (
    ENGINE_REVIEW_JSON_SCHEMA,
    ENGINE_REVIEW_SYSTEM_INSTRUCTION,
    ENGINE_REVIEW_USER_PROMPT,
)

logger = logging.getLogger("codeguru.engine.synthesizer")


class GeminiReviewSynthesizer:
    """Synthesizes static analysis findings with Gemini reasoning to create code reviews."""

    def __init__(self) -> None:
        self.router = AIRouter()

    async def synthesize(self, code: str, language: str, static_analysis_report: Dict[str, Any]) -> Dict[str, Any]:
        """Call Gemini to synthesize static analysis findings and generate a structured review.

        Falls back to a deterministic scoring and issues list if the LLM fails.
        """
        # Serialize the static analysis report for inclusion in the user prompt
        try:
            serialized_report = json.dumps(static_analysis_report, indent=2)
        except Exception as e:
            logger.warning(f"Failed to serialize static analysis report: {e}")
            serialized_report = str(static_analysis_report)

        prompt = ENGINE_REVIEW_USER_PROMPT.format(
            language=language,
            code=code,
            static_analysis=serialized_report
        )

        try:
            response_text, model_used = await self.router.generate_with_fallback(
                prompt=prompt,
                system_instruction=ENGINE_REVIEW_SYSTEM_INSTRUCTION,
                schema=ENGINE_REVIEW_JSON_SCHEMA,
                complexity="complex"
            )

            # Parse JSON response
            result = json.loads(response_text)
            logger.info(f"Synthesized review successfully using model: {model_used}")
            return result

        except Exception as e:
            logger.error(f"AI synthesis failed: {e}. Using deterministic fallback.", exc_info=True)
            return self._deterministic_fallback(code, static_analysis_report)

    def _deterministic_fallback(self, code: str, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a basic structured review using static analysis data if LLM is down."""
        issues = []
        bugs = []
        has_bugs = False

        # Gather Tree-sitter issues
        ts_res = report.get("treesitter", {}).get("results", {})
        for issue in ts_res.get("issues", []):
            issues.append({
                "category": "readability" if issue.get("type") != "long_method" else "performance",
                "line": 1,
                "description": issue.get("message", "Tree-sitter structural issue."),
                "suggestion": "Refactor the code structure."
            })

        # Gather Pylint issues
        pylint_res = report.get("pylint", {}).get("results", {})
        pylint_score = pylint_res.get("lint_score", 100.0)
        for issue in pylint_res.get("issues", []):
            cat = issue.get("category", "style")
            # Map Pylint warning/error/fatal to schema categories
            mapped_cat = "style"
            if cat in ("warning", "error", "fatal"):
                mapped_cat = "readability"
            
            issues.append({
                "category": mapped_cat,
                "line": issue.get("line", 1),
                "description": f"Pylint ({issue.get('symbol', 'lint')}): {issue.get('message', '')}",
                "suggestion": "Fix lint warning."
            })

        # Gather Bandit findings
        bandit_res = report.get("bandit", {}).get("results", {})
        bandit_score = bandit_res.get("security_score", 100.0)
        for finding in bandit_res.get("findings", []):
            issues.append({
                "category": "security",
                "line": finding.get("line_number", 1),
                "description": f"Bandit security risk: {finding.get('description', '')}",
                "suggestion": "Avoid using insecure functions or values."
            })
            # Bandit issues are also bugs if high severity
            if finding.get("severity") == "HIGH":
                has_bugs = True
                bugs.append({
                    "line": finding.get("line_number", 1),
                    "severity": "error",
                    "description": f"Security Vulnerability: {finding.get('description', '')}",
                    "fix": "Rewrite statement to use secure equivalents."
                })

        # Calculate a deterministic base score
        # Start at 100, deduct based on static scores if available
        base_score = 100.0
        active_scores = []
        if report.get("pylint", {}).get("supported"):
            active_scores.append(pylint_score)
        if report.get("bandit", {}).get("supported"):
            active_scores.append(bandit_score)
        
        # Radon maintainability score
        radon_res = report.get("radon", {}).get("results", {})
        if report.get("radon", {}).get("supported"):
            mi_score = radon_res.get("maintainability", {}).get("score", 100.0)
            active_scores.append(mi_score)

        if active_scores:
            base_score = sum(active_scores) / len(active_scores)
        
        # Final rounding
        final_score = max(0, min(100, int(base_score)))

        summary = (
            f"Static Analysis Summary: Parsed code in {report.get('language', 'unknown')}. "
            f"Found {len(issues)} issues across styling, complexity, and security."
        )

        return {
            "score": final_score,
            "summary": summary,
            "issues": issues,
            "has_bugs": has_bugs,
            "bugs": bugs,
            "refactored_code": code
        }
