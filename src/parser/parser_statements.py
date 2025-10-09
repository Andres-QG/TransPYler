from ..core.ast import (
    ExprStmt,
    Assign,
    Return,
    Break,
    Continue,
    Pass,
    Identifier,
    TupleExpr,
    ListExpr,
    Attribute,
    Subscript,
)
from .parser_utils import _pos


class StatementRules:
    """Rules for parsing statements."""

    def p_statement(self, p):
        """statement : simple_statement
        | compound_statement"""
        p[0] = p[1]
    # TODO(Randy): Simple and small statements are currently the same.
    # Consider merging them or differentiating them more clearly.
    def p_simple_statement(self, p):
        """simple_statement : small_stmt"""
        p[0] = p[1]

    def p_small_stmt(self, p):
        """small_stmt : assignment
        | return_stmt
        | break_stmt
        | continue_stmt
        | pass_stmt
        | expr"""
        if len(p) == 2:
            if not isinstance(p[1], (Assign, Return, Break, Continue, Pass)):
                line, col = _pos(p, 1)
                p[0] = ExprStmt(value=p[1], line=line, col=col)
            else:
                p[0] = p[1]

    # ---------------------- ASSIGNMENTS ----------------------
    def p_assignment(self, p):
        """assignment : assign_targets ASSIGN expr
        | assign_targets PLUS_ASSIGN expr
        | assign_targets MINUS_ASSIGN expr
        | assign_targets TIMES_ASSIGN expr
        | assign_targets DIVIDE_ASSIGN expr
        | assign_targets FLOOR_DIVIDE_ASSIGN expr
        | assign_targets MOD_ASSIGN expr
        | assign_targets POWER_ASSIGN expr"""
        value = p[3]
        line, col = _pos(p, 1)
        for target in reversed(p[1]):
            if not isinstance(
                target, (Identifier, TupleExpr, ListExpr, Attribute, Subscript)
            ):
                raise SyntaxError(
                    f"Invalid assignment target at line {line}, col {col}"
                )
            value = Assign(target=target, op=p[2], value=value, line=line, col=col)
        p[0] = value

    def p_assign_targets(self, p):
        """assign_targets : assign_targets ASSIGN target
        | target"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_target(self, p):
        """target : ID
        | LPAREN elements_opt RPAREN
        | LBRACKET elements_opt RBRACKET
        | target LBRACKET expr RBRACKET
        | target DOT ID"""
        line, col = _pos(p, 1)
        if len(p) == 2:
            # Single Id
            p[0] = Identifier(name=p[1], line=line, col=col)
        elif len(p) == 4 and p[1] == "(":
            # Tuple
            p[0] = TupleExpr(elements=p[2], line=line, col=col)
        elif len(p) == 4 and p[1] == "[":
            # List
            p[0] = ListExpr(elements=p[2], line=line, col=col)
        elif len(p) == 4 and p[2] == ".":
            # Attribute
            p[0] = Attribute(value=p[1], attr=p[3], line=line, col=col)
        elif len(p) == 5 and p[2] == "[":
            # Subscript
            p[0] = Subscript(value=p[1], index=p[3], line=line, col=col)

    # ---------------------- CONTROL FLOW STATEMENTS ----------------------
    def p_return_stmt(self, p):
        """return_stmt : RETURN expr
        | RETURN"""
        if len(p) == 3:
            p[0] = Return(value=p[2])
        else:
            p[0] = Return(value=None)

    def p_break_stmt(self, p):
        "break_stmt : BREAK"
        p[0] = Break()

    def p_continue_stmt(self, p):
        "continue_stmt : CONTINUE"
        p[0] = Continue()

    def p_pass_stmt(self, p):
        "pass_stmt : PASS"
        p[0] = Pass()
