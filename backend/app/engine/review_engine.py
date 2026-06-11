"""Code Review Engine — Orchestrator combining static code analysis with Gemini synthesis."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from app.engine.treesitter_analyzer import TreeSitterAnalyzer
from app.engine.pylint_analyzer import PylintAnalyzer
from app.engine.bandit_analyzer import BanditAnalyzer
from app.engine.radon_analyzer import RadonAnalyzer
from app.engine.gemini_synthesizer import GeminiReviewSynthesizer

logger = logging.getLogger("codeguru.engine.orchestrator")


class CodeReviewEngine:
    """Orchestrates the static analysis pipeline and synthesizes results via LLM."""

    def __init__(self) -> None:
        self.analyzers = [
            TreeSitterAnalyzer(),
            PylintAnalyzer(),
            BanditAnalyzer(),
            RadonAnalyzer(),
        ]
        self.synthesizer = GeminiReviewSynthesizer()

    async def analyze(self, code: str, language: str) -> Dict[str, Any]:
        """Execute parallel static analysis, aggregate the reports, and generate the synthesized AI review.

        Args:
            code: Source code content.
            language: Programming language name (e.g. 'python', 'javascript').

        Returns:
            A combined dictionary containing both the full static analysis reports
            and the synthesized review (score, summary, issues, bugs, refactored_code).
        """
        logger.info(f"Starting code review pipeline for language: {language}")

        # Run all static analyzers concurrently
        tasks = [analyzer.analyze(code, language) for analyzer in self.analyzers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        static_report = {
            "language": language,
        }

        # Build aggregated static analysis report
        for analyzer, res in zip(self.analyzers, results):
            if isinstance(res, Exception):
                logger.error(f"Analyzer '{analyzer.name}' crashed: {res}", exc_info=True)
                static_report[analyzer.name] = {
                    "analyzer": analyzer.name,
                    "supported": True,
                    "results": {"error": str(res)},
                }
            else:
                static_report[analyzer.name] = res

        # Run synthesis via LLM (Gemini) using static analysis as context
        synthesized_review = await self.synthesizer.synthesize(code, language, static_report)

        # Merge synthesized results with static analysis reports
        return {
            "score": synthesized_review.get("score", 0),
            "summary": synthesized_review.get("summary", "No summary could be generated."),
            "issues": synthesized_review.get("issues", []),
            "refactored_code": synthesized_review.get("refactored_code", code),
            "has_bugs": synthesized_review.get("has_bugs", False),
            "bugs": synthesized_review.get("bugs", []),
            "static_analysis": static_report,
        }
