from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class AstNode:
    """
    Base class for all AST nodes.
    It functions as a general class from which other nodes inherit. 
    """
    line: Optional[int] = None # Tell us in which line and column of the source code the AST node is located.
    col: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        converts the node into a dictionary, which helps it to be saved in a serializable format (such as JSON)
        """    
        d: Dict[str, Any] = {"_type": self.__class__.__name__}
        for k, v in self.__dict__.items():
            if k in ("line", "col"):
                continue
            if isinstance(v, AstNode):
                d[k] = v.to_dict()
            elif isinstance(v, list):
                d[k] = [x.to_dict() if isinstance(x, AstNode) else x for x in v]
            else:
                d[k] = v
        if self.line is not None: d["line"] = self.line
        if self.col  is not None: d["col"]  = self.col
        return d
