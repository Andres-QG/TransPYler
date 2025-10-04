from dataclasses import dataclass, field
from typing import Any, List
from .ast_base import AstNode

# ---------- Atomic expressions ----------
@dataclass
class LiteralExpr(AstNode):
    value: Any = None   # numbers, strings, True/False/None (y luego colecciones básicas)

@dataclass
class Identifier(AstNode):
    name: str = ""      # variable / función

# ---------- Operators ----------
@dataclass
class UnaryExpr(AstNode):
    op: str = ""        # "+", "-", "not"
    operand: AstNode = None

@dataclass
class BinaryExpr(AstNode):
    left: AstNode = None
    op: str = ""        # "PLUS", "MINUS", "TIMES", "POWER", etc. (token o símbolo)
    right: AstNode = None

@dataclass
class ComparisonExpr(AstNode):
    left: AstNode = None
    op: str = ""        # "EQUALS", "LESS_THAN", ...
    right: AstNode = None
    # Nota: si luego quieren comparaciones encadenadas (a < b < c), se puede extender a listas.

# ---------- Calls ----------
@dataclass
class CallExpr(AstNode):
    callee: AstNode = None                   # normalmente Identifier, pero puede ser otra expresión
    args: List[AstNode] = field(default_factory=list)  # argumentos posicionales
