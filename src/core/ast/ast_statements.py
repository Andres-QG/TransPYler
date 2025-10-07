from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from .ast_base import AstNode

# Ast Nodes for statments and blocks

@dataclass
class Block(AstNode):
    """
    Represents a block of statements, e.g.,
        if condition:
            stmt1
            stmt2
    """
    statements: List[AstNode] = field(default_factory=list)


@dataclass
class ExprStmt(AstNode):
    """Expression used as a statement (function call or bare expression)."""
    value: AstNode = None


@dataclass
class Assign(AstNode):
    """Simple or compound assignment, e.g., x = 5, total += 3."""
    target: AstNode = None
    op: str = "="
    value: AstNode = None


@dataclass
class Return(AstNode):
    """Return statement, e.g., return x + y."""
    value: Optional[AstNode] = None


@dataclass
class Break(AstNode):
    """Break statement inside a loop."""
    pass


@dataclass
class Continue(AstNode):
    """Continue statement inside a loop."""
    pass


@dataclass
class Pass(AstNode):
    """No-op statement."""
    pass


@dataclass
class If(AstNode):
    """
    If / Elif / Else statement.
    Example:
        if cond:
            ...
        elif cond2:
            ...
        else:
            ...
    """
    cond: AstNode = None
    body: Block = None
    elifs: List[Tuple[AstNode, Block]] = field(default_factory=list)
    orelse: Optional[Block] = None


@dataclass
class While(AstNode):
    """While loop."""
    cond: AstNode = None
    body: Block = None


@dataclass
class For(AstNode):
    """For loop."""
    target: AstNode = None
    iterable: AstNode = None
    body: Block = None