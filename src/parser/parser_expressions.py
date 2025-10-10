from ..core.ast import (
    LiteralExpr,
    Identifier,
    UnaryExpr,
    BinaryExpr,
    ComparisonExpr,
    CallExpr,
    TupleExpr,
    ListExpr,
    DictExpr,
    Attribute,
    Subscript,
)
from .parser_utils import _pos


class ExpressionRules:
    """Rules for parsing expressions."""

    # ---------------------- BASIC EXPRESSIONS ----------------------
    def p_expr_atom(self, p):
        "expr : atom"
        p[0] = p[1]

    def p_expr_group(self, p):
        "expr : LPAREN expr RPAREN"
        p[0] = p[2]

    def p_atom_attribute(self, p):
        "atom : atom DOT ID"
        line, col = _pos(p, 2)
        p[0] = Attribute(value=p[1], attr=p[3], line=line, col=col)

    # ---------------------- LITERALS ----------------------
    def p_atom_number(self, p):
        "atom : NUMBER"
        line, col = _pos(p, 1)
        p[0] = LiteralExpr(value=p[1], line=line, col=col)

    def p_atom_string(self, p):
        "atom : STRING"
        line, col = _pos(p, 1)
        p[0] = LiteralExpr(value=p[1], line=line, col=col)

    def p_atom_true(self, p):
        "atom : TRUE"
        line, col = _pos(p, 1)
        p[0] = LiteralExpr(value=True, line=line, col=col)

    def p_atom_false(self, p):
        "atom : FALSE"
        line, col = _pos(p, 1)
        p[0] = LiteralExpr(value=False, line=line, col=col)

    def p_atom_none(self, p):
        "atom : NONE"
        line, col = _pos(p, 1)
        p[0] = LiteralExpr(value=None, line=line, col=col)

    def p_atom_identifier(self, p):
        "atom : ID"
        line, col = _pos(p, 1)
        p[0] = Identifier(name=p[1], line=line, col=col)

    # ---------------------- DATA STRUCTURES ----------------------
    def p_atom_paren(self, p):
        """atom : LPAREN elements_opt RPAREN"""
        line, col = _pos(p, 1)
        elements = p[2]
        if len(elements) == 1:
            p[0] = elements[0]
        else:
            p[0] = TupleExpr(elements=elements, line=line, col=col)

    def p_atom_list(self, p):
        """atom : LBRACKET elements_opt RBRACKET"""
        line, col = _pos(p, 1)
        p[0] = ListExpr(elements=p[2], line=line, col=col)

    def p_atom_subscript(self, p):
        "atom : atom LBRACKET expr RBRACKET"
        line, col = _pos(p, 2)
        p[0] = Subscript(value=p[1], index=p[3], line=line, col=col)

    def p_atom_dict(self, p):
        """atom : LBRACE key_value_list_opt RBRACE"""
        line, col = _pos(p, 1)
        p[0] = DictExpr(pairs=p[2], line=line, col=col)

    # ---------------------- UNARY OPERATORS ----------------------
    def p_expr_unary_plus(self, p):
        "expr : PLUS expr %prec UPLUS"
        line, col = _pos(p, 1)
        p[0] = UnaryExpr(op="PLUS", operand=p[2], line=line, col=col)

    def p_expr_unary_minus(self, p):
        "expr : MINUS expr %prec UMINUS"
        line, col = _pos(p, 1)
        p[0] = UnaryExpr(op="MINUS", operand=p[2], line=line, col=col)

    def p_expr_unary_not(self, p):
        "expr : NOT expr"
        line, col = _pos(p, 1)
        p[0] = UnaryExpr(op="NOT", operand=p[2], line=line, col=col)

    # ---------------------- BINARY OPERATORS ----------------------
    def p_expr_power(self, p):
        "expr : expr POWER expr %prec POWER"
        line, col = _pos(p, 1)
        p[0] = BinaryExpr(left=p[1], op="**", right=p[3], line=line, col=col)

    def p_expr_multiplicative(self, p):
        """expr : expr TIMES expr
        | expr DIVIDE expr
        | expr FLOOR_DIVIDE expr
        | expr MOD expr"""
        line, col = _pos(p, 1)
        p[0] = BinaryExpr(left=p[1], op=p[2], right=p[3], line=line, col=col)

    def p_expr_additive(self, p):
        """expr : expr PLUS expr
        | expr MINUS expr"""
        line, col = _pos(p, 1)
        p[0] = BinaryExpr(left=p[1], op=p[2], right=p[3], line=line, col=col)

    # ---------------------- COMPARISONS ----------------------
    def p_expr_comparison(self, p):
        """expr : expr EQUALS expr
        | expr NOT_EQUALS expr
        | expr LESS_THAN expr
        | expr LESS_THAN_EQUALS expr
        | expr GREATER_THAN expr
        | expr GREATER_THAN_EQUALS expr"""
        line, col = _pos(p, 1)
        p[0] = ComparisonExpr(left=p[1], op=p[2], right=p[3], line=line, col=col)

    # ---------------------- LOGICAL OPERATORS ----------------------
    def p_expr_logical(self, p):
        """expr : expr AND expr
        | expr OR expr"""
        line, col = _pos(p, 1)
        p[0] = BinaryExpr(left=p[1], op=p[2], right=p[3], line=line, col=col)

    # ---------------------- FUNCTION CALLS ----------------------
    def p_expr_call(self, p):
        "expr : atom LPAREN arg_list_opt RPAREN"
        line, col = _pos(p, 2)
        p[0] = CallExpr(callee=p[1], args=p[3], line=line, col=col)

    # ---------------------- EXPRESSION LISTS ----------------------
    def p_arg_list_opt(self, p):
        """arg_list_opt : expr COMMA arg_list_opt
        | expr"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_arg_list_opt_empty(self, p):
        "arg_list_opt :"
        p[0] = []

    def p_key_value_list(self, p):
        """key_value_list : key_value
        | key_value COMMA key_value_list"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_key_value_list_opt(self, p):
        """key_value_list_opt : key_value_list
        | empty"""
        p[0] = p[1]

    def p_key_value(self, p):
        "key_value : expr COLON expr"
        p[0] = (p[1], p[3])

    def p_elements_opt(self, p):
        """elements_opt : elements
        | empty"""
        p[0] = p[1] if len(p) > 1 else []

    def p_elements(self, p):
        """elements : expr
        | elements COMMA expr"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_empty(self, p):
        "empty :"
        p[0] = []