"""
Indent handling for a Python-like lexer (PLY)

This module centralizes the logic that converts leading whitespace after a newline
into Python-like INDENT/DEDENT tokens. It is invoked exclusively by the lexer rule
`t_NEWLINE` and communicates with the lexer through a small, explicit contract.

The lexer instance passed here (`lexer`) MUST provide:
lexer._indent_stack : list[int]
Stack of absolute indentation columns. Base level is 0.
lexer._pending : list[lex.LexToken]
    FIFO queue where synthesized INDENT/DEDENT tokens are enqueued.
lexer._expect_indent : bool
    True if the previous token was a ':' outside delimiters, and thus an indent is required.
lexer._delim_depth : int
    Nesting level of (), [], {}; indentation is disabled when > 0.

"""


def _expand_tabs_count(s: str, tab_width: int) -> int:
    col = 0
    for ch in s:
        if ch == "\t":
            col += tab_width - (col % tab_width)
        else:
            col += 1
    return col

# TODO(any): Refactor
def process_newline_and_indent(lexer, t, tab_width: int):
    """
    Handles a block of one or more line breaks followed by spaces/tabs.
    Concatenates INDENT/DEDENT as appropriate. Returns None (t_NEWLINE does not produce a token).
    `t.value` may contain multiple blank lines. We take the spaces that
    appear after the LAST "\n" to decide the indentation of the next line.
    """
    # 1. Update line number
    nl_count = t.value.count("\n")
    t.lexer.lineno += nl_count

    # 2. If we are inside ()/[]/{}, we ignore structural indentation.
    if getattr(lexer, "_delim_depth", 0) > 0:
        return None

    # 3. Take the spaces/tabs after the last \n (may be an empty string)
    after_last_nl = t.value.rsplit("\n", 1)[-1]

    # 4. Look at the following real char (without consuming it)
    data, pos = t.lexer.lexdata, t.lexer.lexpos
    nextch = data[pos] if pos < len(data) else ""

    # 5. If the “next line” is blank or a comment, do not decide on indentation.
    if nextch in ("\n", "#"):
        return None

    # 6. Calculate column (with tabs expanded correctly)
    spaces = _expand_tabs_count(after_last_nl, tab_width)
    top = lexer._indent_stack[-1]

    # 7. Same level
    if spaces == top:
        # If we came from “:”, I had to increase the indentation.
        if getattr(lexer, "_expect_indent", False):
            lexer._indent_error("Expected an indented block", t.lineno, t.lexpos)
            lexer._expect_indent = False
        return None

    # 8. Increased indent
    if spaces > top:
        if spaces % tab_width != 0:
            lexer._indent_error(
                "Indentation is not a multiple of 4", t.lineno, t.lexpos
            )

        # If we don't come from “:”, it's unexpected indentation.
        if not getattr(lexer, "_expect_indent", False):
            lexer._indent_error("Unexpected indent", t.lineno, t.lexpos)

        # (Optional) If they skip >1 level at once, report it.
        delta = spaces - top
        levels = delta // tab_width
        if getattr(lexer, "_strict_single_step_indent", False) and levels > 1:
            lexer._indent_error(
                f"Over-indented: increased by {levels} levels", t.lineno, t.lexpos
            )

        # Store the absolute column of the new level.
        lexer._indent_stack.append(spaces)
        lexer._pending.append(lexer._make_token("INDENT", "", t.lineno, t.lexpos))
        lexer._expect_indent = False
        return None

    # 9. Decreased indent: issue DEDENTs until reaching 'spaces'
    if spaces % tab_width != 0:
        lexer._indent_error("Indentation is not a multiple of 4", t.lineno, t.lexpos)

    while len(lexer._indent_stack) > 1 and lexer._indent_stack[-1] > spaces:
        lexer._indent_stack.pop()
        lexer._pending.append(lexer._make_token("DEDENT", "", t.lineno, t.lexpos))

    # If we did not fall exactly on a valid previous level
    if lexer._indent_stack and lexer._indent_stack[-1] != spaces:
        lexer._indent_error(
            "Unindent does not match any outer indentation level", t.lineno, t.lexpos
        )

    lexer._expect_indent = False
    return None
