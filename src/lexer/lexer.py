import ply.lex as lex
import re

from ..core.utils import Error
from ..core.symbol_table import SymbolTable
from .tokens import TOKENS, KEYWORDS, TAB_WIDTH
from .indentation import wrapped_token, process_indent_dedent


class Lexer:  # TODO: Too much instance attributes?
    """
    Lexer for a Python-like language using PLY.

    Handles tokenization, keyword recognition, indentation-based block structure,
    string and number literals, operators, identifiers and one line comments.
    Tracks indentation levels to emit INDENT and DEDENT tokens, similar to Python's syntax.
    Registers identifiers in a symbol table and collects lexical errors.
    Supports debug output for indentation errors.

    Attributes:
        keywords (dict): Mapping of language keywords to token types.
        tokens (tuple): List of token types recognized by the lexer.
        t_ignore (str): Characters to ignore during lexing.
        errors (list[Error]): List to collect lexical errors.
        symbol_table (SymbolTable): Symbol table for identifiers.
        debug (bool): Enables debug output for indentation errors.
    """

    keywords = KEYWORDS
    tokens = TOKENS

    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_TIMES = r"\*"
    t_DIVIDE = r"/"
    t_FLOOR_DIVIDE = r"//"
    t_MOD = r"%"
    t_POWER = r"\*\*"
    t_EQUALS = r"=="
    t_NOT_EQUALS = r"!="
    t_LESS_THAN = r"<"
    t_LESS_THAN_EQUALS = r"<="
    t_GREATER_THAN = r">"
    t_GREATER_THAN_EQUALS = r">="
    t_ASSIGN = r"="
    t_PLUS_ASSIGN = r"\+="
    t_MINUS_ASSIGN = r"-="
    t_TIMES_ASSIGN = r"\*="
    t_DIVIDE_ASSIGN = r"/="
    t_FLOOR_DIVIDE_ASSIGN = r"//="
    t_MOD_ASSIGN = r"%="
    t_POWER_ASSIGN = r"\*\*="
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_COLON = r":"
    t_COMMA = r","
    t_DOT = r"\."

    t_ignore = ""

    #   Lifecycle
    def __init__(self, errors: list[Error], debug: bool = False):
        self.lex = None
        self.data = None
        self.debug = debug
        self.errors = errors
        self.symbol_table = SymbolTable()

        # Indentation state
        self._indent_stack = [0]  # indentation levels in spaces (0, 4, 8, ...)
        self._pending = []  # queue of INDENT/DEDENT tokens to return
        self._at_line_start = True  # true when the next char is at start of a line

    def build(self):
        self.lex = lex.lex(module=self)
        self._base_token = self.lex.token
        self.lex.token = lambda: wrapped_token(self, self._base_token)

    #   Private helpers
    def _make_token(self, type_, value, lineno, lexpos):
        tok = lex.LexToken()
        tok.type = type_
        tok.value = value
        tok.lineno = lineno
        tok.lexpos = lexpos
        return tok

    def _indent_error(self, msg, lineno, lexpos):
        self.errors.append(Error(msg, lineno, lexpos, "lexer", self.data))
        if self.debug:
            print(f"[INDENT-ERROR] {msg} @ line {lineno}")

    #   PLY rules (t_...)
    def t_ID(self, t):
        r"[A-Za-z_][A-Za-z0-9_]*"
        t.type = self.keywords.get(t.value, "ID")
        if t.type == "ID":
            # Optional: symbol table registration (kept as in your base)
            try:
                self.symbol_table.add(t.value, t.lexpos, t.lineno, "identifier")
            except Exception:
                pass
        self._at_line_start = False
        return t

    # TODO: Fix (Not a one line comment)
    def t_COMMENT(self, t):
        r"\#.*"
        return None

    def t_STRING(self, t):
        (
            r'(?:'  # Start of non-capturing group for first quote
            r'\"(?:\\.|[^\"\\\n])*\"|'  # Double quoted string
            r'\'(?:\\.|[^\'\\\n])*\''    # Single quoted string
            r')'
            r'(?:'  # Start of non-capturing group for continuation
            r'\\[ \t]*\n[ \t]*'  # Line continuation
            r'(?:'  # Start of non-capturing group for additional quotes
            r'\"(?:\\.|[^\"\\\n])*\"|'  # Double quoted string
            r'\'(?:\\.|[^\'\\\n])*\''    # Single quoted string
            r')'
            r')*'  # Zero or more continuations
        )
        # Extract everything between the quotes, handling multiple parts
        parts = re.findall(r'"((?:\\.|[^"\\\n])*)"|\'((?:\\.|[^\'\\\n])*)\'', t.value)
        raw = "".join(p1 if p1 else p2 for (p1, p2) in parts)
        # Handle escape sequences
        raw = (
            raw.replace(r"\\", "\\")
            .replace(r"\"", '"')
            .replace(r"\'", "'")
            .replace(r"\n", "\n")
            .replace(r"\t", "\t")
        )

        t.value = raw
        self._at_line_start = False
        return t

    # Note: This is a PLY special rule, not a token
    def t_NEWLINE(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)
        self._at_line_start = True
        return None

    def t_INDENT_DEDENT(self, t):
        r"[ \t]+"
        return process_indent_dedent(self, t, TAB_WIDTH)

    def t_error(self, t):
        msg = f"Illegal character '{t.value[0]}'"
        self.errors.append(Error(msg, t.lineno, t.lexpos, "lexer", self.data))
        t.lexer.skip(1)

    def t_NUMBER(self, t):
        r"(\d+(\.\d*)?|\.\d+)"
        t.value = float(t.value) if "." in t.value else int(t.value)
        self._at_line_start = False
        return t
