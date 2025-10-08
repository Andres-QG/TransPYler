from ..core.ast import While, For, Identifier
from .parser_utils import _pos


class LoopRules:
    """Rules for parsing loop statements."""

    def p_while_stmt(self, p):
        """while_stmt : WHILE expr COLON suite"""
        p[0] = While(cond=p[2], body=p[4])

    def p_for_stmt(self, p):
        """for_stmt : FOR ID IN expr COLON suite"""
        line, col = _pos(p, 2)
        p[0] = For(
            target=Identifier(name=p[2], line=line, col=col),
            iterable=p[4],
            body=p[6],
        )
