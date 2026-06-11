"""Bandit security analyzer — scans Python code for common security vulnerabilities.

Runs Bandit programmatically via its manager API, extracting security findings
with CWE IDs, severity levels, and confidence ratings.
"""
from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from typing import Any, Dict, List

from app.engine.base_analyzer import BaseAnalyzer

logger = logging.getLogger("codeguru.engine.bandit")


class BanditAnalyzer(BaseAnalyzer):
    """Scans Python code for security vulnerabilities using Bandit."""

    @property
    def name(self) -> str:
        return "bandit"

    def _supports_language(self, language: str) -> bool:
        return language.lower() in {"python", "py"}

    async def analyze(self, code: str, language: str) -> Dict[str, Any]:
        """Execute Bandit security scan on the submitted code."""
        if not self._supports_language(language):
            result = self._empty_result()
            result["results"] = {
                "note": f"Bandit only supports Python. Skipping for '{language}'."
            }
            return result

        return await asyncio.to_thread(self._run_bandit, code)

    def _run_bandit(self, code: str) -> Dict[str, Any]:
        """Synchronous Bandit execution via its manager API."""
        tmp_path = None
        try:
            # Write code to a temp file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write(code)
                tmp_path = tmp.name

            from bandit.core import manager as bandit_manager
            from bandit.core import config as bandit_config

            # Create Bandit manager with default config
            conf = bandit_config.BanditConfig()
            mgr = bandit_manager.BanditManager(conf, "file")

            # Discover and run tests on the temp file
            mgr.discover_files([tmp_path])
            mgr.run_tests()

            # Extract findings
            findings: List[Dict[str, Any]] = []
            for issue in mgr.get_issue_list():
                findings.append({
                    "test_id": issue.test_id,
                    "test_name": issue.test,
                    "severity": issue.severity,
                    "confidence": issue.confidence,
                    "description": issue.text,
                    "line_number": issue.lineno,
                    "line_range": list(issue.linerange),
                    "cwe": getattr(issue, "cwe", None),
                })

            # Categorize by severity
            counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
            for f in findings:
                sev = f.get("severity", "LOW")
                counts[sev] = counts.get(sev, 0) + 1

            # Security score: start at 100, deduct per finding
            deductions = counts["HIGH"] * 25 + counts["MEDIUM"] * 10 + counts["LOW"] * 3
            security_score = max(0, min(100, 100 - deductions))

            return {
                "analyzer": self.name,
                "supported": True,
                "results": {
                    "findings": findings,
                    "finding_count": len(findings),
                    "counts_by_severity": counts,
                    "security_score": security_score,
                },
            }

        except Exception as e:
            logger.error(f"Bandit analysis failed: {e}", exc_info=True)
            return {
                "analyzer": self.name,
                "supported": True,
                "results": {"error": str(e), "findings": [], "finding_count": 0},
            }
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
