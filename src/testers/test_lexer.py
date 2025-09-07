from src.lexer.lexer import Lexer


def test_correct_keywords():
    errors = []
    lx = Lexer(errors)
    lx.build()
    lx.data = "if else while return"
    lx.lex.input(lx.data)
    tokens = [lx.lex.token() for _ in range(4)]
    assert [t.type for t in tokens] == ["IF", "ELSE", "WHILE", "RETURN"]
    assert all(t.value in ["if", "else", "while", "return"] for t in tokens)
    assert not errors


def test_correct_numbers():
    errors = []
    lx = Lexer(errors)
    lx.build()
    lx.data = "123 45.67 0.001 1000 .6767676785894595"
    lx.lex.input(lx.data)
    tokens = [lx.lex.token() for _ in range(5)]
    assert [t.type for t in tokens] == [
        "NUMBER",
        "NUMBER",
        "NUMBER",
        "NUMBER",
        "NUMBER",
    ]
    assert [t.value for t in tokens] == [123, 45.67, 0.001, 1000, 0.6767676785894595]
    assert not errors


def test_number_dot_number():
    """Test lexer on incorrect input: number dot number without spaces. This is not a lexical error,
    but should be tokenized as three separate NUMBER TOKENS"""
    errors = []
    lx = Lexer(errors)
    lx.build()
    lx.data = "127.0.0.1"
    lx.lex.input(lx.data)
    tokens = []
    while True:
        tok = lx.lex.token()
        if not tok:
            break
        tokens.append(tok)
    assert len(tokens) == 3
    assert tokens[0].type == "NUMBER"
    assert abs(tokens[0].value - 127.0) < 1e-10
    assert tokens[1].type == "NUMBER"
    assert abs(tokens[1].value - 0.0) < 1e-10
    assert tokens[2].type == "NUMBER"
    assert abs(tokens[2].value - 0.1) < 1e-10

def test_negative_numbers():
    """Test that negative numbers are tokenized as separate MINUS and NUMBER tokens."""
    errors = []
    lx = Lexer(errors)
    lx.build()
    lx.data = "-42 -3.14 -.001 -0.5"
    lx.lex.input(lx.data)
    tokens = [lx.lex.token() for _ in range(8)]
    types = ["MINUS", "NUMBER", "MINUS", "NUMBER", "MINUS", "NUMBER", "MINUS", "NUMBER"]
    assert [t.type for t in tokens] == types
    assert [t.value for t in tokens] == ["-", 42, "-", 3.14, "-", 0.001, "-", 0.5]
    assert not errors

def test_leading_zeros():
    """Test lexer for numbers with leading zeros. This is not a lexical error,
    but the leading zeros should be ignored in the token value. This is a parser concern."""
    errors = []
    lx = Lexer(errors)
    lx.build()
    lx.data = "007 0.5 000123"
    lx.lex.input(lx.data)
    tokens = [lx.lex.token() for _ in range(3)]
    types = ["NUMBER", "NUMBER", "NUMBER"]
    values = [7, 0.5, 123]
    assert [t.type for t in tokens] == types
    assert [t.value for t in tokens] == values
    assert not errors


def test_numbers_with_operators():
    """Test lexer for numbers mixed with operators."""
    errors = []
    lx = Lexer(errors)
    lx.build()
    lx.data = "5-3 4.5+2.3"
    lx.lex.input(lx.data)
    tokens = [lx.lex.token() for _ in range(6)]
    assert [t.type for t in tokens] == ["NUMBER", "MINUS", "NUMBER", "NUMBER", "PLUS", "NUMBER"]
    assert [t.value for t in tokens] == [5, "-", 3, 4.5, "+", 2.3]
    assert not errors

def test_large_numbers():
    """Test lexer for very large numbers."""
    errors = []
    lx = Lexer(errors)
    lx.build()
    lx.data = "12345678901234567890 1.7976931348623157e+308"
    lx.lex.input(lx.data)
    tokens = [lx.lex.token() for _ in range(2)]
    types = ["NUMBER", "NUMBER"]
    values = [12345678901234567890, 1.7976931348623157e+308]
    assert [t.type for t in tokens] == types
    assert [t.value for t in tokens] == values
    assert not errors

def test_scientific_notation():
    """Test lexer for numbers in scientific notation."""
    errors = []
    lx = Lexer(errors)
    lx.build()
    lx.data = "1e10 3.14e-2 2E+5 -1.23e-4"
    lx.lex.input(lx.data)
    tokens = [lx.lex.token() for _ in range(5)]
    types = ["NUMBER", "NUMBER", "NUMBER", "MINUS", "NUMBER"]
    values = [1e10, 3.14e-2, 2e5, "-", 1.23e-4]
    assert [t.type for t in tokens] == types
    assert [t.value for t in tokens] == values
    assert not errors
