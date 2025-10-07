'''Unit tests for the Indentation component of the TransPYler project.'''

from src.lexer.lexer import Lexer

def _lex_all(src: str):
    """Consume the entire input and return (tokens, errors)."""
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

def _indent_types(tokens):
    """Return only indentation token types."""
    return [t.type for t in tokens if t.type in ("INDENT", "DEDENT")]

def test_simple_block_indent_and_dedent():
    src = (
        "def f():\n"
        "    x = 1\n"
        "    return x\n"
    )  # At EOF, the closing DEDENT must be emitted
    tokens, errors = _lex_all(src)
    inds = _indent_types(tokens)
    assert not errors
    # Exactly 1 INDENT when entering the block and 1 DEDENT when closing it
    assert inds == ["INDENT", "DEDENT"]

def test_nested_blocks_sequence_counts():
    src = (
        "def f():\n"
        "    if x:\n"
        "        y = 1\n"
        "    else:\n"
        "        y = 2\n"
        "    z = 3\n"
    )
    tokens, errors = _lex_all(src)
    inds = _indent_types(tokens)
    assert not errors
    # Levels: def(INDENT), if(INDENT), close if(DEDENT),
    # else(INDENT), close else(DEDENT), close def(DEDENT)
    assert inds.count("INDENT") == 3
    assert inds.count("DEDENT") == 3

def test_multiple_dedents_at_eof():
    src = (
        "def a():\n"
        "    def b():\n"
        "        x = 1\n"
        "        y = 2\n"
    )  # At EOF, DEDENTs must be emitted to close b and a
    tokens, errors = _lex_all(src)
    inds = _indent_types(tokens)
    assert not errors
    assert inds.count("INDENT") == 2
    assert inds.count("DEDENT") == 2

def test_blank_lines_and_comments_do_not_change_indentation():
    src = (
        "def f():\n"
        "    x = 1\n"
        "    # comment\n"
        "\n"
        "    y = 2\n"
        "pass\n"
    )  # 'pass' at level 0 forces the DEDENT of f's block
    tokens, errors = _lex_all(src)
    inds = _indent_types(tokens)
    assert not errors
    assert inds == ["INDENT", "DEDENT"]

def test_inconsistent_tabs_and_spaces_reports_error():
    src = (
        "def f():\n"
        "\t x = 1\n"    # tab
        "    y = 2\n"   # spaces
    )
    tokens, errors = _lex_all(src)
    # There must be at least one indentation error for mixing tabs and spaces
    assert any("indent" in e.message.lower() for e in errors)

def test_unindent_not_matching_any_level_reports_error():
    # First line indented with 6 spaces; next line with 4 spaces (not in the stack)
    src = (
        "def f():\n"
        "      x = 1\n"   # 6 spaces
        "    y = 2\n"     # 4 spaces -> does not match 0 or 6
    )
    tokens, errors = _lex_all(src)
    assert errors, "An error must be reported for a misaligned dedent"
    assert any("unindent" in e.message.lower() or "indentation" in e.message.lower() for e in errors)
