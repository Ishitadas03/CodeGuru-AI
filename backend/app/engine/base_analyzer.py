"""Abstract base class defining the contract for all static code analyzers."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger("codeguru.engine")


class BaseAnalyzer(ABC):
    """Abstract analyzer interface.

    Every static analysis tool (Tree-sitter, Pylint, Bandit, Radon) implements
    this contract so the engine can run them uniformly and in parallel.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the analyzer (e.g. 'pylint', 'bandit')."""
        ...

    @abstractmethod
    async def analyze(self, code: str, language: str) -> Dict[str, Any]:
        """Run analysis on the given source code.

        Args:
            code: The raw source code string to analyze.
            language: Programming language identifier (e.g. 'python', 'javascript').

        Returns:
            A structured dictionary of analysis results specific to the tool.
            Must include at minimum an 'analyzer' key with the tool name.
        """
        ...

    def _supports_language(self, language: str) -> bool:
        """Check if this analyzer supports the given language. Override per-tool."""
        return True

    def _empty_result(self) -> Dict[str, Any]:
        """Return an empty result skeleton when language is unsupported or analysis fails."""
        return {"analyzer": self.name, "supported": False, "results": {}}
