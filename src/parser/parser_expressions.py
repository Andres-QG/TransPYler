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
    SetExpr,
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
        # Situation like x = a[b] is handled in assignment rules

    def p_atom_dict(self, p):
        """atom : LBRACE key_value_list_opt RBRACE"""
        line, col = _pos(p, 1)
        p[0] = DictExpr(pairs=p[2], line=line, col=col)

    # ------------------------slicing ------------------------------  
    # atom [ subscript_item ]
    def p_atom_subscript_slice(self, p):
        "atom : atom LBRACKET subscript_item RBRACKET"
        line, col = _pos(p, 2)
        p[0] = Subscript(value=p[1], index=p[3], line=line, col=col)

    def p_subscript_item_index(self, p):
        "subscript_item : expr"
        p[0] = p[1]

    def p_subscript_item_slice_2(self, p):
        "subscript_item : opt_expr COLON opt_expr"
        # (lower, upper, None)
        line, col = _pos(p, 2)
        p[0] = TupleExpr(elements=[p[1], p[3], None], line=line, col=col)

    def p_subscript_item_slice_3(self, p):
        "subscript_item : opt_expr COLON opt_expr COLON opt_expr"
        # (lower, upper, step)
        line, col = _pos(p, 2)
        p[0] = TupleExpr(elements=[p[1], p[3], p[5]], line=line, col=col)

    def p_subscript_item_slice_head(self, p):
        "subscript_item : COLON opt_expr"
        line, col = _pos(p, 1)
        p[0] = TupleExpr(elements=[None, p[2], None], line=line, col=col)

    def p_subscript_item_slice_tail(self, p):
        "subscript_item : opt_expr COLON"
        line, col = _pos(p, 2)
        p[0] = TupleExpr(elements=[p[1], None, None], line=line, col=col)

    def p_subscript_item_slice_all(self, p):
        "subscript_item : COLON"
        line, col = _pos(p, 1)
        p[0] = TupleExpr(elements=[None, None, None], line=line, col=col)

    def p_subscript_item_slice_step_only(self, p):
        "subscript_item : COLON COLON opt_expr"
        line, col = _pos(p, 1)
        p[0] = TupleExpr(elements=[None, None, p[3]], line=line, col=col)

    def p_opt_expr_empty(self, p):
        "opt_expr :"
        p[0] = None

    def p_opt_expr_expr(self, p):
        "opt_expr : expr"
        p[0] = p[1]

    # ------------ set literal ---------------------
    def p_atom_set(self, p):
        "atom : LBRACE set_elements RBRACE"
        line, col = _pos(p, 1)
        p[0] = SetExpr(elements=p[2], line=line, col=col)

    def p_set_elements_single(self, p):
        "set_elements : expr"
        p[0] = [p[1]]

    def p_set_elements_multi(self, p):
        "set_elements : set_elements COMMA expr"
        p[1].append(p[3])
        p[0] = p[1]

    def p_set_elements_trailing(self, p):
        "set_elements : set_elements COMMA"
        p[0] = p[1]

    # ---------------------- UNARY OPERATORS ----------------------
    # TODO(Any): UPLUS is not a Token on our lexer, should we change it?
    def p_expr_unary_plus(self, p):
        "expr : PLUS expr %prec UPLUS"
        line, col = _pos(p, 1)
        p[0] = UnaryExpr(op="PLUS", operand=p[2], line=line, col=col)

    # TODO(Any): UMINUS is not a Token on our lexer, should we change it?
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
        | expr GREATER_THAN_EQUALS expr
        | expr IN expr"""
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
