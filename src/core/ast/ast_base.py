"""
This module defines the foundational classes for Abstract Syntax Tree (AST) nodes
used in the TransPYler compiler.

The module provides:
- AstNode: Base class for all AST nodes with common functionality
- Module: Top-level container representing a complete source file
- Utility functions for AST manipulation and serialization

Each AST node tracks its source code position (line, column) and can be
converted to a dictionary representation for debugging and processing.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List


@dataclass
class AstNode:
    """
    Base class for all AST nodes.
    It functions as a general class from which other nodes inherit.
    """

    line: Optional[int] = (
        None  # Tell us in which line and column of the source code the AST node is located.
    )
    col: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        dictionary = {"_type": self.__class__.__name__}
        for key, value in self.__dict__.items():
            if key in ("line", "col"):
                continue
            dictionary[key] = _convert(value)
        if self.line is not None:
            dictionary["line"] = self.line
        if self.col is not None:
            dictionary["col"] = self.col
        return dictionary


@dataclass
class Module(AstNode):
    """Top-level AST node representing a complete module or file."""

    body: List[AstNode] = field(default_factory=list)


def _convert(value):
    if isinstance(value, AstNode):
        return value.to_dict()
    if isinstance(value, (list, tuple)):
        return [_convert(x) for x in value]
    if isinstance(value, dict):
        return {k: _convert(v) for k, v in value.items()}
    return value  # str, int, float, bool, None
