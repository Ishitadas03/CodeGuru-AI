"""Pylint static analyzer — runs Pylint programmatically on submitted code.

Writes code to a temp file, executes Pylint with JSON reporter, and parses
the structured output into categorized lint issues.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
from typing import Any, Dict, List

from app.engine.base_analyzer import BaseAnalyzer

logger = logging.getLogger("codeguru.engine.pylint")

# Map Pylint message categories to human-readable severity
_CATEGORY_MAP = {
    "C": "convention",
    "R": "refactor",
    "W": "warning",
    "E": "error",
    "F": "fatal",
    "I": "info",
}


class PylintAnalyzer(BaseAnalyzer):
    """Runs Pylint on Python source code and returns categorized lint issues."""

    @property
    def name(self) -> str:
        return "pylint"

    def _supports_language(self, language: str) -> bool:
        return language.lower() in {"python", "py"}

    async def analyze(self, code: str, language: str) -> Dict[str, Any]:
        """Execute Pylint analysis on the submitted code."""
        if not self._supports_language(language):
            result = self._empty_result()
            result["results"] = {
                "note": f"Pylint only supports Python. Skipping for '{language}'."
            }
            return result

        return await asyncio.to_thread(self._run_pylint, code)

    def _run_pylint(self, code: str) -> Dict[str, Any]:
        """Synchronous Pylint execution using temp file and JSON output."""
        tmp_path = None
        try:
            # Write code to a temporary file (Pylint requires a file path)
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write(code)
                tmp_path = tmp.name

            from io import StringIO
            from pylint.lint import Run
            from pylint.reporters.json_reporter import JSONReporter

            output = StringIO()
            reporter = JSONReporter(output)

            # Run Pylint with strict settings disabled for user code analysis
            try:
                Run(
                    [
                        tmp_path,
                        "--disable=C0114,C0115,C0116",  # Disable missing docstring checks
                        "--max-line-length=120",
                        "--score=y",
                    ],
                    reporter=reporter,
                    exit=False,
                )
            except SystemExit:
                pass  # Pylint sometimes calls sys.exit

            # Parse JSON output
            raw_output = output.getvalue()
            issues: List[Dict[str, Any]] = []
            pylint_score = 10.0

            if raw_output.strip():
                try:
                    parsed = json.loads(raw_output)
                    for msg in parsed:
                        issues.append({
                            "message_id": msg.get("message-id", ""),
                            "symbol": msg.get("symbol", ""),
                            "category": _CATEGORY_MAP.get(
                                msg.get("type", "I")[0].upper(), "info"
                            ),
                            "line": msg.get("line", 0),
                            "column": msg.get("column", 0),
                            "message": msg.get("message", ""),
                            "obj": msg.get("obj", ""),
                        })
                except json.JSONDecodeError:
                    logger.warning("Failed to parse Pylint JSON output.")

            # Categorize issues by severity
            counts = {"convention": 0, "refactor": 0, "warning": 0, "error": 0, "fatal": 0, "info": 0}
            for issue in issues:
                cat = issue.get("category", "info")
                counts[cat] = counts.get(cat, 0) + 1

            # Calculate a normalized score (Pylint default is 0-10, we normalize to 0-100)
            # Deduct points: errors=-10, warnings=-5, conventions=-1, refactor=-2
            deductions = (
                counts["fatal"] * 20
                + counts["error"] * 10
                + counts["warning"] * 5
                + counts["refactor"] * 2
                + counts["convention"] * 1
            )
            lint_score = max(0, min(100, 100 - deductions))

            return {
                "analyzer": self.name,
                "supported": True,
                "results": {
                    "issues": issues,
                    "issue_count": len(issues),
                    "counts_by_category": counts,
                    "lint_score": lint_score,
                },
            }

        except Exception as e:
            logger.error(f"Pylint analysis failed: {e}", exc_info=True)
            return {
                "analyzer": self.name,
                "supported": True,
                "results": {"error": str(e), "issues": [], "issue_count": 0},
            }
        finally:
            # Clean up temp file
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
