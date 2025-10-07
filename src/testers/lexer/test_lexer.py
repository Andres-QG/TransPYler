'''Unit tests for the Lexer component of the TransPYler project.'''

from src.lexer.lexer import Lexer


def _lex_all(src):
    """Helper function to lex all tokens from a source string.
    Returns list of tokens and any lexical errors."""
    errors = []
    lx = Lexer(errors)
    lx.build()
    lx.data = src
    lx.lex.input(lx.data)
    tokens = []
    while True:
        t = lx.lex.token()
        if not t:
            break
        tokens.append(t)
    return tokens, errors


def test_correct_keywords():
    """
    Test if lexer correctly identifies and tokenizes Python keywords.
    Raises:
        AssertionError: If token types or values don't match expected keywords,
        or if lexical errors are found
    """
    tokens, errors = _lex_all("if else while return")
    assert [t.type for t in tokens] == ["IF", "ELSE", "WHILE", "RETURN"]
    assert all(t.value in ["if", "else", "while", "return"] for t in tokens)
    assert not errors


def test_correct_numbers():
    """Test lexer on various correct number formats."""
    tokens, errors = _lex_all("123 45.67 0.001 1000 .6767676785894595")
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
    tokens, errors = _lex_all("127.0 .0 .1")
    assert len(tokens) == 3
    assert tokens[0].type == "NUMBER"
    assert abs(tokens[0].value - 127.0) < 1e-10
    assert tokens[1].type == "NUMBER"
    assert abs(tokens[1].value - 0.0) < 1e-10
    assert tokens[2].type == "NUMBER"
    assert abs(tokens[2].value - 0.1) < 1e-10
    assert not errors


def test_negative_numbers():
    """Test that negative numbers are tokenized as separate MINUS and NUMBER tokens."""
    tokens, errors = _lex_all("-42 -3.14 -.001 -0.5")
    types = ["MINUS", "NUMBER", "MINUS", "NUMBER", "MINUS", "NUMBER", "MINUS", "NUMBER"]
    assert [t.type for t in tokens] == types
    assert [t.value for t in tokens] == ["-", 42, "-", 3.14, "-", 0.001, "-", 0.5]
    assert not errors


def test_leading_zeros():
    """Test lexer for numbers with leading zeros. This is not a lexical error,
    but the leading zeros should be ignored in the token value. This is a parser concern.
    """
    tokens, errors = _lex_all("007 000.5 0123")
    types = ["NUMBER", "NUMBER", "NUMBER"]
    values = [7, 0.5, 123]
    assert [t.type for t in tokens] == types
    assert [t.value for t in tokens] == values
    assert not errors


def test_numbers_with_operators():
    """Test lexer for numbers mixed with operators."""
    tokens, errors = _lex_all("5-3 4.5+2.3")
    assert [t.type for t in tokens] == [
        "NUMBER",
        "MINUS",
        "NUMBER",
        "NUMBER",
        "PLUS",
        "NUMBER",
    ]
    assert [t.value for t in tokens] == [5, "-", 3, 4.5, "+", 2.3]
    assert not errors


def test_large_numbers():
    """Test lexer for very large numbers."""
    tokens, errors = _lex_all("12345678901234567890 1.7976931348623157e+308")
    types = ["NUMBER", "NUMBER"]
    values = [12345678901234567890, 1.7976931348623157e308]
    assert [t.type for t in tokens] == types
    assert [t.value for t in tokens] == values
    assert not errors


def test_scientific_notation():
    """Test lexer for numbers in scientific notation."""
    tokens, errors = _lex_all("1e10 3.14e-2 2E+5 -1.23e-4")
    types = ["NUMBER", "NUMBER", "NUMBER", "MINUS", "NUMBER"]
    values = [1e10, 3.14e-2, 2e5, "-", 1.23e-4]
    assert [t.type for t in tokens] == types
    assert [t.value for t in tokens] == values
    assert not errors


def test_basic_strings():
    """Test lexer on basic string formats with single and double quotes."""
    tokens, errors = _lex_all("\"Hello\" 'World' \"Python\" 'Testing'")
    assert [t.type for t in tokens] == ["STRING", "STRING", "STRING", "STRING"]
    assert [t.value for t in tokens] == ["Hello", "World", "Python", "Testing"]
    assert not errors


def test_empty_strings():
    """Test lexer on empty strings."""
    tokens, errors = _lex_all("\"\" '' \"\" ''")
    assert [t.type for t in tokens] == ["STRING", "STRING", "STRING", "STRING"]
    assert [t.value for t in tokens] == ["", "", "", ""]
    assert not errors


def test_strings_with_spaces():
    """Test lexer on strings containing spaces and special characters."""
    tokens, errors = _lex_all('"Hello World" "  spaces  " "!@#$%^&*()"')
    assert [t.type for t in tokens] == ["STRING", "STRING", "STRING"]
    assert [t.value for t in tokens] == ["Hello World", "  spaces  ", "!@#$%^&*()"]
    assert not errors


def test_mixed_quotes():
    """Test lexer on strings with mixed quote types."""
    tokens, errors = _lex_all("\"Contains 'single' quotes\" 'Contains \"double\" quotes'")
    assert [t.type for t in tokens] == ["STRING", "STRING"]
    assert [t.value for t in tokens] == [
        "Contains 'single' quotes",
        'Contains "double" quotes',
    ]
    assert not errors


def test_strings_with_numbers():
    """Test lexer on strings containing numbers and mixed content."""
    tokens, errors = _lex_all('"123" "num 456" "0.123" "1e10"')
    assert [t.type for t in tokens] == ["STRING", "STRING", "STRING", "STRING"]
    assert [t.value for t in tokens] == ["123", "num 456", "0.123", "1e10"]
    assert not errors


def test_unterminated_string():
    """Test lexer on an unterminated string to ensure it raises a lexical error."""
    tokens, errors = _lex_all('"Unfinished string')
    assert len(tokens) == 0
    assert len(errors) == 1
    assert errors[0].message == "Unterminated string literal"


def test_multiline_strings():
    """Test lexer on multiline strings using line continuation."""
    tokens, errors = \
    _lex_all("'''Triple quotation string\n continues here''' 'But single quotation ones\n do not'")
    assert tokens[0].type == "STRING"
    assert len(errors) == 1
    assert errors[0].message == "Unterminated string literal"


def test_strings_with_escapes():
    """Test lexer on strings containing escape sequences."""
    tokens, errors = _lex_all(r""""Tab\there" "Quote\"mark" 'Back\\slash' ''""")
    assert not errors
    assert [t.type for t in tokens] == ["STRING", "STRING", "STRING", "STRING"]
    assert [t.value for t in tokens] == [
        "Tab\there",
        'Quote"mark',
        "Back\\slash",
        "",
    ]

def test_unknown_escapes_are_preserved():
    '''Test lexer on strings with unknown escape sequences to ensure they are preserved as-is.'''
    s = r'"foo\qbar\xZZ"'
    tokens, errors = _lex_all(s)
    assert tokens[0].type == "STRING"
    assert tokens[0].value == r"foo\qbar\xZZ"
    assert not errors
