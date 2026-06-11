"""Tree-sitter AST analyzer — extracts structural metrics from source code.

Uses tree-sitter grammars to parse code into ASTs and compute metrics like
function count, class count, nesting depth, import count, and average function length.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

from app.engine.base_analyzer import BaseAnalyzer

logger = logging.getLogger("codeguru.engine.treesitter")

# Language → tree-sitter module mapping (lazy-loaded)
_LANGUAGE_MODULES = {
    "python": "tree_sitter_python",
    "javascript": "tree_sitter_javascript",
    "js": "tree_sitter_javascript",
}

# Node types per language for structural extraction
_FUNCTION_NODE_TYPES = {
    "python": {"function_definition"},
    "javascript": {"function_declaration", "arrow_function", "method_definition", "function_expression"},
}

_CLASS_NODE_TYPES = {
    "python": {"class_definition"},
    "javascript": {"class_declaration"},
}

_IMPORT_NODE_TYPES = {
    "python": {"import_statement", "import_from_statement"},
    "javascript": {"import_statement"},
}


class TreeSitterAnalyzer(BaseAnalyzer):
    """Parses source code via tree-sitter grammars and extracts structural AST metrics."""

    @property
    def name(self) -> str:
        return "treesitter"

    def _supports_language(self, language: str) -> bool:
        return language.lower() in _LANGUAGE_MODULES

    async def analyze(self, code: str, language: str) -> Dict[str, Any]:
        """Parse code into an AST and compute structural metrics."""
        lang_key = language.lower()
        if not self._supports_language(lang_key):
            result = self._empty_result()
            result["results"] = {
                "note": f"Tree-sitter grammar not available for '{language}'. Skipping AST analysis."
            }
            return result

        # Run CPU-bound parsing in a thread pool
        return await asyncio.to_thread(self._parse_and_extract, code, lang_key)

    def _parse_and_extract(self, code: str, lang_key: str) -> Dict[str, Any]:
        """Synchronous parsing and metric extraction."""
        try:
            import tree_sitter as ts

            # Dynamically import the language module
            mod_name = _LANGUAGE_MODULES[lang_key]
            lang_mod = __import__(mod_name)
            language = ts.Language(lang_mod.language())

            parser = ts.Parser(language)
            tree = parser.parse(bytes(code, "utf-8"))
            root = tree.root_node

            # Extract metrics by walking the AST
            func_nodes = self._collect_nodes_by_type(
                root, _FUNCTION_NODE_TYPES.get(lang_key, set())
            )
            class_nodes = self._collect_nodes_by_type(
                root, _CLASS_NODE_TYPES.get(lang_key, set())
            )
            import_nodes = self._collect_nodes_by_type(
                root, _IMPORT_NODE_TYPES.get(lang_key, set())
            )

            # Compute function lengths (line span)
            func_lengths = []
            for fn in func_nodes:
                start_line = fn.start_point[0]
                end_line = fn.end_point[0]
                func_lengths.append(end_line - start_line + 1)

            # Compute max nesting depth
            max_depth = self._compute_max_depth(root)

            # Detect issues
            issues = self._detect_structural_issues(
                func_lengths, max_depth, len(class_nodes), lang_key
            )

            lines = code.split("\n")
            loc = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())
            comment_lines = self._count_comment_lines(root, lang_key)

            return {
                "analyzer": self.name,
                "supported": True,
                "results": {
                    "function_count": len(func_nodes),
                    "class_count": len(class_nodes),
                    "import_count": len(import_nodes),
                    "loc": loc,
                    "blank_lines": blank_lines,
                    "comment_lines": comment_lines,
                    "max_nesting_depth": max_depth,
                    "average_function_length": (
                        round(sum(func_lengths) / len(func_lengths), 1)
                        if func_lengths else 0
                    ),
                    "function_lengths": func_lengths,
                    "has_syntax_errors": root.has_error,
                    "issues": issues,
                },
            }
        except Exception as e:
            logger.error(f"Tree-sitter analysis failed: {e}", exc_info=True)
            return {
                "analyzer": self.name,
                "supported": True,
                "results": {"error": str(e)},
            }

    def _collect_nodes_by_type(self, node: Any, type_names: set) -> List[Any]:
        """Recursively collect all descendant nodes matching the given type names."""
        found: List[Any] = []
        if node.type in type_names:
            found.append(node)
        for child in node.children:
            found.extend(self._collect_nodes_by_type(child, type_names))
        return found

    def _compute_max_depth(self, node: Any, current_depth: int = 0) -> int:
        """Compute maximum nesting depth of block-level constructs."""
        _BLOCK_TYPES = {
            "if_statement", "for_statement", "while_statement", "try_statement",
            "with_statement", "elif_clause", "else_clause", "except_clause",
            "for_in_statement", "if_statement", "switch_statement",
        }
        max_d = current_depth
        for child in node.children:
            child_depth = current_depth
            if child.type in _BLOCK_TYPES:
                child_depth = current_depth + 1
            max_d = max(max_d, self._compute_max_depth(child, child_depth))
        return max_d

    def _count_comment_lines(self, root: Any, lang_key: str) -> int:
        """Count comment nodes in the AST."""
        comment_types = {"comment"}
        if lang_key == "python":
            comment_types.add("string")  # docstrings are string nodes at statement level
        comments = self._collect_nodes_by_type(root, {"comment"})
        return len(comments)

    def _detect_structural_issues(
        self,
        func_lengths: List[int],
        max_depth: int,
        class_count: int,
        lang_key: str,
    ) -> List[Dict[str, str]]:
        """Detect common structural anti-patterns from AST metrics."""
        issues: List[Dict[str, str]] = []

        # Long functions (> 50 lines)
        for i, length in enumerate(func_lengths):
            if length > 50:
                issues.append({
                    "type": "long_function",
                    "severity": "warning",
                    "message": f"Function #{i + 1} is {length} lines long. Consider refactoring into smaller functions.",
                })

        # Deep nesting (> 4 levels)
        if max_depth > 4:
            issues.append({
                "type": "deep_nesting",
                "severity": "warning",
                "message": f"Maximum nesting depth is {max_depth}. Consider using early returns or extracting helper functions.",
            })

        # God class detection (> 10 methods would need deeper analysis, just flag many classes)
        if class_count > 5:
            issues.append({
                "type": "many_classes",
                "severity": "info",
                "message": f"File contains {class_count} classes. Consider splitting into separate modules.",
            })

        return issues
