import ply.lex as lex

from .utils import Error
from .symbol_table import SymbolTable


#   Configuration / Constants
TAB_WIDTH = 4  # one tab counts as 4 spaces for indentation

RESERVED = {
    # Flow control
    'if': 'IF', 
    'else': 'ELSE', 
    'elif': 'ELIF', 
    'while': 'WHILE',
    'for': 'FOR', 
    'break': 'BREAK', 
    'continue': 'CONTINUE', 
    'pass': 'PASS',
    # Definitions
    'def': 'DEF', 
    'return': 'RETURN', 
    'class': 'CLASS',
    # Booleans (case-sensitive like Python)
    'True': 'TRUE', 
    'False': 'FALSE',
    # Logical operators
    'and': 'AND', 
    'or': 'OR', 
    'not': 'NOT',
}

TOKENS = tuple(set(RESERVED.values())) + ('ID', 'INDENT', 'DEDENT')

class Lexer:
    reserved = RESERVED
    tokens = TOKENS

    t_ignore = ''

 
    #   Lifecycle
    def __init__(self, errors: list[Error], debug: bool = False):
        self.lex = None
        self.data = None
        self.debug = debug
        self.errors = errors
        self.symbol_table = SymbolTable()

        # Indentation state
        self._indent_stack = [0]    # indentation levels in spaces (0, 4, 8, ...)
        self._pending = []          # queue of INDENT/DEDENT tokens to return
        self._at_line_start = True  # true when the next char is at start of a line

    def build(self):
        self.lex = lex.lex(module=self)
        self._base_token = self.lex.token
        self.lex.token = self._wrapped_token

    #   Private helpers
    def _make_token(self, type_, value, lineno, lexpos):
        tok = lex.LexToken()
        tok.type = type_
        tok.value = value
        tok.lineno = lineno
        tok.lexpos = lexpos
        return tok

    def _indent_error(self, msg, lineno, lexpos):
        self.errors.append(Error(msg, lineno, lexpos, 'lexer', self.data))
        if self.debug:
            print(f"[INDENT-ERROR] {msg} @ line {lineno}")


    #   PLY rules (t_...)
    def t_ID(self, t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        t.type = self.reserved.get(t.value, 'ID')
        if t.type == 'ID':
            # Optional: symbol table registration (kept as in your base)
            try:
                self.symbol_table.add(t.value, t.lexpos, t.lineno, 'identifier')
            except Exception:
                pass
        self._at_line_start = False
        return t

    def t_COMMENT(self, t):
        r'\#.*'
        return None

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        self._at_line_start = True
        return None

    def t_INDENT_DEDENT(self, t):
        r'[ \t]+'
        if not self._at_line_start:
            return None  # internal whitespace is ignored

        # 1) Count indentation (tab == TAB_WIDTH)
        spaces = sum(TAB_WIDTH if ch == '\t' else 1 for ch in t.value)

        # 2) Peek next character without consuming it
        pos, data = t.lexer.lexpos, t.lexer.lexdata
        nextch = data[pos] if pos < len(data) else ''
        # blank line or comment-only
        if nextch in ('\n', '#'):
            return None

        # 3) Compare with current top
        top = self._indent_stack[-1]

        if spaces == top:
            self._at_line_start = False
            return None

        if spaces > top:
            # INDENT
            delta = spaces - top
            if delta % TAB_WIDTH != 0:
                self._indent_error("Indentation is not a multiple of 4", t.lineno, t.lexpos)
                self._at_line_start = False
                return None
            for _ in range(delta // TAB_WIDTH):
                top += TAB_WIDTH
                self._indent_stack.append(top)
                self._pending.append(self._make_token('INDENT', '', t.lineno, t.lexpos))

            self._at_line_start = False
            return self._pending.pop(0) if self._pending else None

        # spaces < top DEDENT
        if spaces % TAB_WIDTH != 0:
            self._indent_error("Indentation is not a multiple of 4", t.lineno, t.lexpos)

        while self._indent_stack and self._indent_stack[-1] > spaces:
            self._indent_stack.pop()
            self._pending.append(self._make_token('DEDENT', '', t.lineno, t.lexpos))

        if self._indent_stack and self._indent_stack[-1] != spaces:
            self._indent_error("Invalid dedent level", t.lineno, t.lexpos)

        self._at_line_start = False
        return self._pending.pop(0) if self._pending else None

    def t_error(self, t):
        msg = f"Illegal character '{t.value[0]}'"
        self.errors.append(Error(msg, t.lineno, t.lexpos, 'lexer', self.data))
        t.lexer.skip(1)


    #   token() wrapper
    def _wrapped_token(self):
        # Dedent at start-of-line (column 0)
        if self._at_line_start and not self._pending:
            pos, data = self.lex.lexpos, self.lex.lexdata
            ch = data[pos] if pos < len(data) else ''
            if ch not in (' ', '\t', '\n', '#'):
                while len(self._indent_stack) > 1:
                    self._indent_stack.pop()
                    self._pending.append(self._make_token('DEDENT', '', self.lex.lineno, self.lex.lexpos))

        # Return any queued INDENT/DEDENT first
        if self._pending:
            return self._pending.pop(0)

        # Ask PLY for the next real token
        tok = self._base_token()

        # At EOF, close remaining indentation levels
        if tok is None and len(self._indent_stack) > 1:
            self._indent_stack.pop()
            return self._make_token('DEDENT', '', self.lex.lineno, self.lex.lexpos)

        return tok
