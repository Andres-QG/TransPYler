from ..core.ast import Block


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
            statement = p[1]
            p[0] = Block(
                statements=[statement],
                line=getattr(statement, "line", None),
                col=getattr(statement, "col", None),
            )
        else:
            statements = p[2]
            if statements:
                p[0] = Block(
                    statements=statements,
                    line=getattr(statements[0], "line", None),
                    col=getattr(statements[0], "col", None),
                )
            else:
                p[0] = Block(statements=[])
