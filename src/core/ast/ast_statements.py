"""
AST nodes for statements and blocks.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from .ast_base import AstNode

@dataclass
class Block(AstNode):
    """
    Represents a block of statements, such as the body of a function,
    if/elif/else, while, or for loop.

    Attributes:
        statements (List[AstNode]): A list of statements contained in the block.
    """

    statements: List[AstNode] = field(default_factory=list)


@dataclass
class ExprStmt(AstNode):
    """
    Represents an expression used as a statement.
    Typically used for function calls or standalone expressions.

    Attributes:
        value (AstNode): The expression being executed as a statement.
    """

    value: Optional[AstNode] = None


@dataclass
class Assign(AstNode):
    """
    Represents an assignment statement.

    Examples:
        x = 5
        total += 3

    Attributes:
        target (AstNode): The variable or target receiving the value.
        op (str): The assignment operator, e.g., '=', '+=', '-='.
        value (AstNode): The expression assigned to the target.
    """

    target: Optional[AstNode] = None
    op: str = "="
    value: Optional[AstNode] = None


@dataclass
class Return(AstNode):
    """
    Represents a return statement in a function.

    Example:
        return x + y

    Attributes:
        value (Optional[AstNode]): The expression being returned,
        or None for bare 'return'.
    """

    value: Optional[AstNode] = None


@dataclass
class Break(AstNode):
    """
    Represents a 'break' statement inside a loop.

    Usage:
        Used to exit the nearest enclosing while or for loop immediately.
    """

@dataclass
class Continue(AstNode):
    """
    Represents a 'continue' statement inside a loop.

    Usage:
        Skips the remaining statements in the current iteration
        and continues with the next iteration of the loop.
    """

@dataclass
class Pass(AstNode):
    """
    Represents a no-op statement.

    Usage:
        'pass' is used as a placeholder where a statement is syntactically required.
    """

@dataclass
class If(AstNode):
    """
    Represents an if/elif/else conditional statement.

    Example:
        if cond:
            ...
        elif cond2:
            ...
        else:
            ...

    Attributes:
        cond (AstNode): The condition for the 'if' block.
        body (Block): The block executed if 'cond' is True.
        elifs (List[Tuple[AstNode, Block]]): Optional list of (condition, block) for 'elif' clauses.
        orelse (Optional[Block]): Optional block executed if all conditions are False.
    """

    cond: Optional[AstNode] = None
    body: Optional[Block] = None
    elifs: List[Tuple[AstNode, Block]] = field(default_factory=list)
    orelse: Optional[Block] = None


@dataclass
class While(AstNode):
    """
    Represents a 'while' loop statement.

    Attributes:
        cond (AstNode): The loop condition expression.
        body (Block): The block of statements executed as long as 'cond' is True.
    """

    cond: Optional[AstNode] = None
    body: Optional[Block] = None


@dataclass
class For(AstNode):
    """
    Represents a 'for' loop statement.

    Example:
        for target in iterable:
            ...

    Attributes:
        target (AstNode): The loop variable.
        iterable (AstNode): The expression being iterated over.
        body (Block): The block of statements executed in each iteration.
    """

    target: Optional[AstNode] = None
    iterable: Optional[AstNode] = None
    body: Optional[Block] = None
