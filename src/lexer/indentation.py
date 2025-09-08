
"""
Indentation utilities for a Python-like lexer PLY.

Provides the minimal logic for indentation outside the main lexer.
At start of line, counts spaces/tabs (with a fixed tab width of 4), emits
INDENT/DEDENT tokens when the level changes, ignores blank/comment-only lines,
and closes any open blocks with DEDENT at EOF.

Functions:
    process_indent_dedent(lexer, t, tab_width):
        Body of the t_INDENT_DEDENT rule; returns an INDENT/DEDENT token or None.
    wrapped_token(lexer, base_token):
        Token wrapper that returns queued INDENT/DEDENT first and flushes
        pending DEDENTs at SOL/EOF.

Lexer must provide:
    _indent_stack, _pending, _at_line_start, _make_token, _indent_error and lex.
"""

def process_indent_dedent(lexer, t, tab_width):
    """
    Process indentation and dedentation at the start of a line.

    This function is intended to be called from the `t_INDENT_DEDENT` rule
    in a PLY lexer. It compares the current indentation level (measured in
    spaces, with tabs expanded to multiples of `tab_width`) with the last
    recorded level in `lexer._indent_stack`.

    Behavior:
        - If the indentation is unchanged, nothing is emitted.
        - If the indentation increases, one or more `INDENT` tokens are queued.
        - If the indentation decreases, one or more `DEDENT` tokens are queued.
        - If indentation is not a multiple of `tab_width`, `_indent_error`
          is invoked.
        - Blank lines or comment-only lines are ignored.

    Args:
        lexer: The lexer instance managing indentation state.
        t: The PLY token containing leading whitespace.
        tab_width (int): Number of spaces per tab (default 4).

    Returns:
        A single queued `INDENT`/`DEDENT` token if available, or `None`.
    """

    if not lexer._at_line_start:
        return None  # whitespace interno se ignora

    # 1. Count indentation (tab == tab_width)
    spaces = sum(tab_width if ch == "\t" else 1 for ch in t.value)

    # 2. Look at the following char without consuming it
    pos, data = t.lexer.lexpos, t.lexer.lexdata
    nextch = data[pos] if pos < len(data) else ""
    # blank line or comment only, ignore indentation
    if nextch in ("\n", "#"):
        return None

    # 3. Compare with current top
    top = lexer._indent_stack[-1]

    if spaces == top:
        lexer._at_line_start = False
        return None

    if spaces > top:
        # INDENT
        delta = spaces - top
        if delta % tab_width != 0:
            lexer._indent_error("Indentation is not a multiple of 4", t.lineno, t.lexpos)
            lexer._at_line_start = False
            return None
        for _ in range(delta // tab_width):
            top += tab_width
            lexer._indent_stack.append(top)
            lexer._pending.append(lexer._make_token("INDENT", "", t.lineno, t.lexpos))
        lexer._at_line_start = False
        return lexer._pending.pop(0) if lexer._pending else None

    # spaces < top -> DEDENT
    if spaces % tab_width != 0:
        lexer._indent_error("Indentation is not a multiple of 4", t.lineno, t.lexpos)

    while lexer._indent_stack and lexer._indent_stack[-1] > spaces:
        lexer._indent_stack.pop()
        lexer._pending.append(lexer._make_token("DEDENT", "", t.lineno, t.lexpos))

    if lexer._indent_stack and lexer._indent_stack[-1] != spaces:
        lexer._indent_error("Invalid dedent level", t.lineno, t.lexpos)

    lexer._at_line_start = False
    return lexer._pending.pop(0) if lexer._pending else None


def wrapped_token(lexer, base_token_callable):
    """
    Token wrapper that handles queued indentation/dedentation tokens.

    This function wraps the base lexer token generator and ensures that
    `INDENT`/`DEDENT` tokens are returned in the correct order. It also
    injects final `DEDENT` tokens at end-of-file (EOF) to close any open
    indentation levels.

    Behavior:
        - At the start of a line, if no whitespace token is present, checks
          whether outstanding `DEDENT`s should be generated.
        - If `_pending` tokens exist, returns them before requesting a new
          token from PLY.
        - If EOF is reached but the indentation stack is not back to the
          base level, emits one `DEDENT` per open block.

    Args:
        lexer: The lexer instance managing indentation state.
        base_token_callable (callable): Function that retrieves the next
            token from the underlying PLY lexer.

    Returns:
        The next token (real or synthetic `INDENT`/`DEDENT`), or `None`
        when no more tokens are available.
    """
     
    # DEDENT at the beginning of the line if applicable
    if lexer._at_line_start and not lexer._pending:
        pos, data = lexer.lex.lexpos, lexer.lex.lexdata
        ch = data[pos] if pos < len(data) else ""
        if ch not in (" ", "\t", "\n", "#"):
            while len(lexer._indent_stack) > 1:
                lexer._indent_stack.pop()
                lexer._pending.append(
                    lexer._make_token("DEDENT", "", lexer.lex.lineno, lexer.lex.lexpos)
                )

    # Return pending INDENT/DEDENT orders first
    if lexer._pending:
        return lexer._pending.pop(0)

    # Ask PLY for the next real token
    tok = base_token_callable()

    # At EOF, close open indentations
    if tok is None and len(lexer._indent_stack) > 1:
        lexer._indent_stack.pop()
        return lexer._make_token("DEDENT", "", lexer.lex.lineno, lexer.lex.lexpos)

    return tok