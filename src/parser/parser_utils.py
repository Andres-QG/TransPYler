def _pos(p, i) -> tuple[int, int]:
    """Returns approximate (line, col) for the i-th symbol of the production."""
    return p.lineno(i), p.lexpos(i)
