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
        """
        converts the node into a dictionary, which helps it to be saved in a 
        serializable format (such as JSON)
        """
        dictionary: Dict[str, Any] = {"_type": self.__class__.__name__}
        for key, value in self.__dict__.items():
            # If the key is "line" or "col", we skip it for now and add it later if it's not None
            if key in ("line", "col"):
                continue
            # If the value is another AstNode
            if isinstance(value, AstNode):
                dictionary[key] = value.to_dict()
            # If the value is a list of AstNodes
            elif isinstance(value, list):
                # Build a list converting AstNode elements to dicts, leaving others unchanged
                dictionary[key] = [
                    x.to_dict() if isinstance(x, AstNode) else x for x in value
                ]
            else:
                dictionary[key] = value
        if self.line is not None:
            dictionary["line"] = self.line
        if self.col is not None:
            dictionary["col"] = self.col
        return dictionary
    
@dataclass    
class Module(AstNode):
    """Top-level AST node representing a complete module or file."""
    body: List[AstNode] = field(default_factory=list)