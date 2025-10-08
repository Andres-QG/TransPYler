"""AST nodes for definitions like functions, classes, and modules."""

from dataclasses import dataclass, field
from typing import List
from .ast_base import AstNode


@dataclass
class FunctionDef(AstNode):
    """Function definition: def name(params): body"""

    name: str = ""
    params: List[str] = field(default_factory=list)  # parameter names
    body: List[AstNode] = field(default_factory=list)  # statements in function


@dataclass
class ClassDef(AstNode):
    """Class definition: class name: body"""

    name: str = ""
    body: List[AstNode] = field(default_factory=list)  # methods and statements


@dataclass
class Subscript(AstNode):
    """
    Represents a subscript operation, such as accessing an element of a list or dictionary.
    """

    def __init__(self, value, index, line=None, col=None):
        self.value = value
        self.index = index
        self.line = line
        self.col = col


@dataclass
class Attribute(AstNode):
    """
    Represents an attribute access operation, such as accessing a property of an object.
    """

    def __init__(self, value, attr, line=None, col=None):
        self.value = value
        self.attr = attr
        self.line = line
        self.col = col
