from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from .ast_base import AstNode

# Ast Nodes for statments and blocks

@dataclass
class Block(AstNode):
    """
    Represents a block of statements, as in:
        if condition:
            stmt1
            stmt2
    """
    statements: List[AstNode] = field(default_factory=list)


@dataclass
class ExprStmt(AstNode):
    """
    Represents an expression used as a statement (e.g., a function call or bare expression).
    Example:
        some_call(1, 2)
        1 + 2   # as top-level statement
    """
    value: AstNode = None


@dataclass
class Assign(AstNode):
    """
    Represents simple or compound assignment.
    Example:
        x = 5
        total += 3
    """
    target: AstNode = None
    op: str = "="
    value: AstNode = None


@dataclass
class Return(AstNode):
    """
    Represents a 'return' statement.
    Example:
        return x + y
    """
    value: Optional[AstNode] = None


@dataclass
class Break(AstNode):
    """Represents a 'break' statement inside a loop."""
    pass

@dataclass
class Pass(AstNode):
    """Represents a 'pass' statement (no-op)."""
    pass


@dataclass
class Continue(AstNode):
    """Represents a 'continue' statement inside a loop."""
    pass


@dataclass
class If(AstNode):
    """
    Represents an if/elif/else structure.
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
    # elifs: list of tuples (cond, block)
    elifs: List[Tuple[AstNode, Block]] = field(default_factory=list)
    orelse: Optional[Block] = None


@dataclass
class While(AstNode):
    """
    Represents a 'while' loop.
    Example:
        while cond:
            ...
    """
    cond: AstNode = None
    body: Block = None


@dataclass
class For(AstNode):
    """
    Represents a 'for' loop.
    Example:
        for x in iterable:
            ...
    """
    target: AstNode = None
    iterable: AstNode = None
    body: Block = None