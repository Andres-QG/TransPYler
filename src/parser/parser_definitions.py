# parser/parser_definitions.py
from ..core.ast import FunctionDef, ClassDef, Block, Identifier
from .parser_utils import _pos


class DefinitionRules:
    """Rules for parsing function and class definitions."""
    
    def p_funcdef(self, p):
        "funcdef : DEF ID LPAREN param_list_opt RPAREN COLON statement_list"
        line, col = _pos(p, 1)
        body = Block(statements=p[7]) if not isinstance(p[7], Block) else p[7]
        p[0] = FunctionDef(name=p[2], params=p[4], body=body, line=line, col=col)

    def p_classdef(self, p):
        "classdef : CLASS ID COLON statement_list"
        line, col = _pos(p, 1)
        body = Block(statements=p[3]) if not isinstance(p[3], Block) else p[3]
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
        """param : ID"""
        line, col = _pos(p, 1)
        p[0] = Identifier(name=p[1], line=line, col=col)