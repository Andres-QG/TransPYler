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
