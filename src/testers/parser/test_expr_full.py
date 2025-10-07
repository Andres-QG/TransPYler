from src.parser.parser import Parser
from src.core.ast import LiteralExpr, UnaryExpr, BinaryExpr, ComparisonExpr, CallExpr, Identifier

def parse(s: str):
    return Parser().parse(s)

# ============================ NUMEROS Y LITERALS ============================

def test_expr_number():
    ast = parse("42")
    assert isinstance(ast, LiteralExpr)
    assert ast.value == 42

def test_expr_string():
    ast = parse('"hello"')
    assert isinstance(ast, LiteralExpr)
    assert ast.value == "hello"

def test_expr_true():
    ast = parse("True")
    assert isinstance(ast, LiteralExpr)
    assert ast.value is True

def test_expr_false():
    ast = parse("False")
    assert isinstance(ast, LiteralExpr)
    assert ast.value is False

def test_expr_none():
    ast = parse("None")
    assert isinstance(ast, LiteralExpr)
    assert ast.value is None

def test_expr_identifier():
    ast = parse("x")
    assert isinstance(ast, Identifier)
    assert ast.name == "x"

# ============================ UNARIOS ============================

def test_expr_unary_plus():
    ast = parse("+42")
    assert isinstance(ast, UnaryExpr)
    assert ast.op == "PLUS"
    assert isinstance(ast.operand, LiteralExpr)
    assert ast.operand.value == 42

def test_expr_unary_minus():
    ast = parse("-42")
    assert isinstance(ast, UnaryExpr)
    assert ast.op == "MINUS"
    assert isinstance(ast.operand, LiteralExpr)
    assert ast.operand.value == 42

def test_expr_unary_not():
    ast = parse("not True")
    assert isinstance(ast, UnaryExpr)
    assert ast.op == "NOT"
    assert isinstance(ast.operand, LiteralExpr)
    assert ast.operand.value is True

# ============================ BINARIOS ============================

def test_expr_power():
    ast = parse("2 ** 3")
    assert isinstance(ast, BinaryExpr)
    assert ast.op == "**"
    assert ast.left.value == 2
    assert ast.right.value == 3

def test_expr_multiplicative():
    ast = parse("4 * 5")
    assert isinstance(ast, BinaryExpr)
    assert ast.op == "*"
    assert ast.left.value == 4
    assert ast.right.value == 5

def test_expr_additive():
    ast = parse("7 + 8")
    assert isinstance(ast, BinaryExpr)
    assert ast.op == "+"
    assert ast.left.value == 7
    assert ast.right.value == 8

def test_expr_comparison():
    ast = parse("5 == 6")
    assert isinstance(ast, ComparisonExpr)
    assert ast.op == "=="
    assert ast.left.value == 5
    assert ast.right.value == 6

def test_expr_logical():
    ast = parse("True and False")
    assert isinstance(ast, BinaryExpr)
    assert ast.op == "and"
    assert ast.left.value is True
    assert ast.right.value is False

# ============================ LLAMADAS A FUNCIONES ============================

def test_expr_call():
    ast = parse("func(1, 2, 3)")
    assert isinstance(ast, CallExpr)
    assert ast.callee.name == "func"
    assert len(ast.args) == 3
    assert ast.args[0].value == 1
    assert ast.args[1].value == 2
    assert ast.args[2].value == 3
