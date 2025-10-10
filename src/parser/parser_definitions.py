from ..core.ast import FunctionDef, ClassDef, Block, Identifier
from .parser_utils import _pos


class DefinitionRules:
    """Rules for parsing function and class definitions."""

    def p_funcdef(self, p):
        "funcdef : DEF ID LPAREN param_list_opt RPAREN COLON suite"
        line, col = _pos(p, 1)
        # TODO(Andres): Suite already returns a Block, so this check is redundant.
        body = Block(statements=p[7]) if not isinstance(p[7], Block) else p[7]
        p[0] = FunctionDef(name=p[2], params=p[4], body=body, line=line, col=col)

    def p_classdef(self, p):
        "classdef : CLASS ID COLON suite"
        line, col = _pos(p, 1)
        # TODO(Andres): Suite already returns a Block, so this check is redundant.
        body = Block(statements=p[4]) if not isinstance(p[4], Block) else p[4]
        p[0] = ClassDef(name=p[2], body=body, line=line, col=col)

    def p_param_list_opt(self, p):
        """param_list_opt : param COMMA param_list_opt
        | param
        |"""
        if len(p) == 1:  # empty
            p[0] = []
        elif len(p) == 2:  # single param
            p[0] = [p[1]]
        else:  # param COMMA param_list_opt
            p[0] = [p[1]] + p[3]

    def p_param(self, p):
        """param : ID
        | ID ASSIGN expr"""
        line, col = _pos(p, 1)
        p[0] = Identifier(name=p[1], line=line, col=col)
