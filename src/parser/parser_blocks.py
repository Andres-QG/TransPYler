# parser/parser_blocks.py
from ..core.ast import Block
from .parser_utils import _pos


class BlockRules:
    """Rules for parsing code blocks and compound statements."""
    
    def p_compound_statement(self, p):
        """compound_statement : if_stmt
                          | while_stmt
                          | for_stmt
                          | funcdef
                          | classdef"""
        p[0] = p[1]

    def p_suite(self, p):
        """suite : simple_statement
                 | INDENT statement_list DEDENT"""
        if len(p) == 2:
            stmt = p[1]
            p[0] = Block(statements=[stmt], line=getattr(stmt, "line", None), col=getattr(stmt, "col", None))
        else:
            stmts = p[2]
            if stmts:
                p[0] = Block(statements=stmts, line=getattr(stmts[0], "line", None), col=getattr(stmts[0], "col", None))
            else:
                p[0] = Block(statements=[])