"""Radon complexity analyzer — measures complexity, maintainability, and raw metrics of Python code."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from app.engine.base_analyzer import BaseAnalyzer

logger = logging.getLogger("codeguru.engine.radon")


class RadonAnalyzer(BaseAnalyzer):
    """Computes Radon metrics (Cyclomatic Complexity, Maintainability Index, Raw metrics) for Python."""

    @property
    def name(self) -> str:
        return "radon"

    def _supports_language(self, language: str) -> bool:
        return language.lower() in {"python", "py"}

    async def analyze(self, code: str, language: str) -> Dict[str, Any]:
        """Execute Radon analysis on the submitted code."""
        if not self._supports_language(language):
            result = self._empty_result()
            result["results"] = {
                "note": f"Radon only supports Python. Skipping for '{language}'."
            }
            return result

        return await asyncio.to_thread(self._run_radon, code)

    def _run_radon(self, code: str) -> Dict[str, Any]:
        """Synchronously compute Radon metrics."""
        try:
            from radon.complexity import cc_visit, cc_rank, average_complexity
            from radon.metrics import mi_visit, mi_rank
            from radon.raw import analyze as raw_analyze

            # 1. Raw metrics
            raw_res = raw_analyze(code)
            raw_metrics = {
                "loc": raw_res.loc,
                "lloc": raw_res.lloc,
                "sloc": raw_res.sloc,
                "comments": raw_res.comments,
                "multi": raw_res.multi,
                "blank": raw_res.blank,
            }

            # 2. Cyclomatic Complexity
            blocks = cc_visit(code)
            cc_blocks = []
            for b in blocks:
                b_type = "class" if type(b).__name__ == "Class" else ("method" if getattr(b, "is_method", False) else "function")
                cc_blocks.append({
                    "name": getattr(b, "name", ""),
                    "complexity": getattr(b, "complexity", 1),
                    "line_number": getattr(b, "lineno", 1),
                    "column_offset": getattr(b, "col_offset", 0),
                    "type": b_type,
                    "rank": getattr(b, "letter", "A"),
                })
            
            avg_cc = average_complexity(blocks) if blocks else 1.0

            # 3. Maintainability Index
            try:
                mi_score = mi_visit(code, multi=True)
                mi_letter = mi_rank(mi_score)
            except Exception as e:
                logger.warning(f"Failed to calculate MI: {e}")
                mi_score = 100.0
                mi_letter = "A"

            return {
                "analyzer": self.name,
                "supported": True,
                "results": {
                    "raw_metrics": raw_metrics,
                    "complexity": {
                        "blocks": cc_blocks,
                        "average_complexity": avg_cc,
                        "overall_rank": cc_rank(avg_cc),
                    },
                    "maintainability": {
                        "score": mi_score,
                        "rank": mi_letter,
                    }
                }
            }

        except Exception as e:
            logger.error(f"Radon analysis failed: {e}", exc_info=True)
            return {
                "analyzer": self.name,
                "supported": True,
                "results": {
                    "error": str(e),
                    "complexity": {"blocks": [], "average_complexity": 1.0, "overall_rank": "A"},
                    "maintainability": {"score": 100.0, "rank": "A"}
                },
            }
