import pytest
from unittest.mock import AsyncMock, patch
from app.engine.treesitter_analyzer import TreeSitterAnalyzer
from app.engine.pylint_analyzer import PylintAnalyzer
from app.engine.bandit_analyzer import BanditAnalyzer
from app.engine.radon_analyzer import RadonAnalyzer
from app.engine.gemini_synthesizer import GeminiReviewSynthesizer
from app.engine.review_engine import CodeReviewEngine

@pytest.mark.asyncio
async def test_treesitter_analyzer_python() -> None:
    analyzer = TreeSitterAnalyzer()
    code = """
import os
import sys

class User:
    def __init__(self, name: str):
        self.name = name

    def greet(self) -> str:
        if self.name:
            if True:
                if True:
                    if True:
                        if True:
                            return f"Hello, {self.name}"
        return "Hello"
"""
    result = await analyzer.analyze(code, "python")
    assert result["analyzer"] == "treesitter"
    assert result["supported"] is True
    res = result["results"]
    assert res["function_count"] == 2
    assert res["class_count"] == 1
    assert res["import_count"] == 2
    assert res["max_nesting_depth"] >= 4
    assert any(issue["type"] == "deep_nesting" for issue in res["issues"])


@pytest.mark.asyncio
async def test_treesitter_analyzer_javascript() -> None:
    analyzer = TreeSitterAnalyzer()
    code = """
import { helper } from './utils';

class Calculator {
    add(a, b) {
        return a + b;
    }
}
function greet(name) {
    console.log("Hello " + name);
}
"""
    result = await analyzer.analyze(code, "javascript")
    assert result["analyzer"] == "treesitter"
    assert result["supported"] is True
    res = result["results"]
    assert res["function_count"] == 2
    assert res["class_count"] == 1
    assert res["import_count"] == 1


@pytest.mark.asyncio
async def test_pylint_analyzer() -> None:
    analyzer = PylintAnalyzer()
    code = """
def foo():
    x = 10
    return 5
"""
    result = await analyzer.analyze(code, "python")
    assert result["analyzer"] == "pylint"
    assert result["supported"] is True
    res = result["results"]
    assert "issues" in res
    assert res["issue_count"] > 0
    assert any("unused-variable" in issue["symbol"] or "W0612" in issue["message_id"] for issue in res["issues"])


@pytest.mark.asyncio
async def test_bandit_analyzer() -> None:
    analyzer = BanditAnalyzer()
    code = """
import subprocess

def run_cmd(user_input):
    subprocess.call(user_input, shell=True)
"""
    result = await analyzer.analyze(code, "python")
    assert result["analyzer"] == "bandit"
    assert result["supported"] is True
    res = result["results"]
    assert res["finding_count"] > 0
    assert any("B602" in finding["test_id"] for finding in res["findings"])
    assert res["security_score"] < 100


@pytest.mark.asyncio
async def test_radon_analyzer() -> None:
    analyzer = RadonAnalyzer()
    code = """
def complex_func(x):
    if x > 10:
        if x < 20:
            return 1
        else:
            return 2
    else:
        return 3
"""
    result = await analyzer.analyze(code, "python")
    assert result["analyzer"] == "radon"
    assert result["supported"] is True
    res = result["results"]
    assert res["complexity"]["average_complexity"] >= 3.0
    assert len(res["complexity"]["blocks"]) == 1
    assert res["complexity"]["blocks"][0]["name"] == "complex_func"
    assert "maintainability" in res
    assert res["maintainability"]["score"] > 0


@pytest.mark.asyncio
async def test_non_python_graceful_degradation() -> None:
    pylint = PylintAnalyzer()
    bandit = BanditAnalyzer()
    
    pylint_res = await pylint.analyze("console.log('hello')", "javascript")
    bandit_res = await bandit.analyze("console.log('hello')", "javascript")
    
    assert pylint_res["supported"] is False
    assert bandit_res["supported"] is False


@pytest.mark.asyncio
async def test_gemini_synthesizer_mock() -> None:
    synthesizer = GeminiReviewSynthesizer()
    code = "def foo(): pass"
    report = {
        "language": "python",
        "treesitter": {"analyzer": "treesitter", "supported": True, "results": {}},
        "pylint": {"analyzer": "pylint", "supported": True, "results": {"lint_score": 100.0, "issues": []}},
        "bandit": {"analyzer": "bandit", "supported": True, "results": {"security_score": 100.0, "findings": []}},
        "radon": {"analyzer": "radon", "supported": True, "results": {"maintainability": {"score": 100.0}}},
    }
    
    result = await synthesizer.synthesize(code, "python", report)
    assert "score" in result
    assert "summary" in result
    assert "issues" in result
    assert "has_bugs" in result
    assert "bugs" in result
    assert "refactored_code" in result


@pytest.mark.asyncio
async def test_review_engine_pipeline() -> None:
    engine = CodeReviewEngine()
    code = "def bubble_sort(arr):\n    pass"
    result = await engine.analyze(code, "python")
    
    assert "score" in result
    assert "summary" in result
    assert "issues" in result
    assert "has_bugs" in result
    assert "bugs" in result
    assert "refactored_code" in result
    assert "static_analysis" in result
    assert "treesitter" in result["static_analysis"]
    assert "pylint" in result["static_analysis"]
    assert "bandit" in result["static_analysis"]
    assert "radon" in result["static_analysis"]
