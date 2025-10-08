from dataclasses import dataclass, field
from typing import List
from .ast_base import AstNode


@dataclass
class Module(AstNode):
    """Root node representing an entire module/file"""

    body: List[AstNode] = field(default_factory=list)  # list of statements/definitions


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
    def __init__(self, value, index, line=None, col=None):
        self.value = value
        self.index = index
        self.line = line
        self.col = col

@dataclass
class Attribute(AstNode):
    def __init__(self, value, attr, line=None, col=None):
        self.value = value
        self.attr = attr
        self.line = line
        self.col = col