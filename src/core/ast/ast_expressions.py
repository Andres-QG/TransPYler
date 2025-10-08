from dataclasses import dataclass, field
from typing import Any, List, Tuple
from .ast_base import AstNode


# ---------- Atomic expressions ----------
@dataclass
class LiteralExpr(AstNode):
    value: Any = None  # numbers, strings, True/False/None (and basic collections after)


@dataclass
class Identifier(AstNode):
    name: str = ""  # variable / function


# ---------- Operators ----------
@dataclass
class UnaryExpr(AstNode):
    op: str = ""  # "+", "-", "not"
    operand: AstNode = None


@dataclass
class BinaryExpr(AstNode):
    left: AstNode = None
    op: str = ""  # "PLUS", "MINUS", "TIMES", "POWER", etc. (token o symbol)
    right: AstNode = None


@dataclass
class ComparisonExpr(AstNode):
    left: AstNode = None
    op: str = ""  # "EQUALS", "LESS_THAN", ...
    right: AstNode = None
    # Note: could be chained comparisons (a < b < c) but for simplicity, we keep it binary


# ---------- Calls ----------
@dataclass
class CallExpr(AstNode):
    callee: AstNode = None  # Identifier, but could be more complex (e.g., obj.method)
    args: List[AstNode] = field(default_factory=list)  # positional arguments


# ---------- Collections ----------
@dataclass
class TupleExpr(AstNode):
    """
    Represents a tuple literal, e.g. (1, 2, 3)
    Empty tuple: ()
    """
    elements: List[AstNode] = field(default_factory=list)


@dataclass
class ListExpr(AstNode):
    """
    Represents a list literal, e.g. [1, 2, 3]
    """
    elements: List[AstNode] = field(default_factory=list)


@dataclass
class DictExpr(AstNode):
    """
    Represents a dictionary literal, e.g. {"a": 1, "b": 2}
    Each pair is (key, value)
    """
    pairs: List[Tuple[AstNode, AstNode]] = field(default_factory=list)



