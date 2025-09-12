"""
A lexical analyzer for a Fangless Python language using PLY.
This class implements a lexer that tokenizes source code following Fangless Python syntax rules.
It handles keywords, operators, literals, identifiers, comments and indentation-based
block structure.
Key features:
- Tokenizes source code into language elements
- Tracks indentation levels for INDENT/DEDENT tokens
- Maintains symbol table for identifiers
- Collects lexical errors
- Supports debug output
    keywords (dict): Maps language keywords to their token types
    tokens (tuple): List of all valid token types
    t_ignore (str): Characters to skip during lexical analysis
    lex: PLY lexer instance
    data (str): Input source code being analyzed
    debug (bool): Enable debug output for indentation errors
    errors (list[Error]): Collection of lexical errors found
    symbol_table (SymbolTable): Symbol table tracking identifiers
    _indent_stack (list[int]): Stack of indentation levels in spaces
    _pending (list): Queue of pending INDENT/DEDENT tokens
    _at_line_start (bool): Flag for line start position
    _base_token: Original PLY token function
Regular expression rules defined for:
- Arithmetic operators (+, -, *, /, //, %, **)
- Comparison operators (==, !=, <, <=, >, >=)
- Assignment operators (=, +=, -=, *=, /=, //=, %=, **=)
- Delimiters ((, ), {, }, [, ], :, ,, .)
- Identifiers, numbers, strings, comments
- Whitespace and newlines for indentation
Example usage:
    lexer = Lexer(errors=[])
    lexer.build()
    lexer.input(source_code)
    for token in lexer:
        print(token)
"""

import re
from ply import lex

from ..core.utils import Error
from ..core.symbol_table import SymbolTable
from .tokens import TOKENS, KEYWORDS, TAB_WIDTH
from .indentation import process_newline_and_indent  # NUEVO

# Helper sets used by the lexer to track suites and delimiter nesting.
SUITE_COLON = {"COLON"}  # ':' fuera de delimitadores abre bloque
OPEN_DELIMS  = {"LPAREN", "LBRACKET", "LBRACE"}
CLOSE_DELIMS = {"RPAREN", "RBRACKET", "RBRACE"}


class Lexer:
    """
    Lexer for a Fangless Python language using PLY.

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
    t_MINUS = r"\-"
    t_TIMES = r"\*"
    t_DIVIDE = r"\/"
    t_FLOOR_DIVIDE = r"\/\/"
    t_MOD = r"\%"
    t_POWER = r"\*\*"
    t_EQUALS = r"\=\="
    t_NOT_EQUALS = r"\!\="
    t_LESS_THAN = r"\<"
    t_LESS_THAN_EQUALS = r"\<\="
    t_GREATER_THAN = r"\>"
    t_GREATER_THAN_EQUALS = r"\>\="
    t_ASSIGN = r"\="
    t_PLUS_ASSIGN = r"\+\="
    t_MINUS_ASSIGN = r"\-\="
    t_TIMES_ASSIGN = r"\*\="
    t_DIVIDE_ASSIGN = r"\/\="
    t_FLOOR_DIVIDE_ASSIGN = r"\/\/\="
    t_MOD_ASSIGN = r"\%\="
    t_POWER_ASSIGN = r"\*\*="
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_COLON = r"\:"
    t_COMMA = r"\,"
    t_DOT = r"\."

    t_ignore = "" # global ignore empty because the whitespace is handled by rules.

    #   Lifecycle
    def __init__(self, errors: list[Error], debug: bool = False):
        """
        Initialize a new lexer instance.

        Parameters:
        errors : list[Error]
            A list that will receive lexical errors discovered during scanning.
        debug : bool, optional
            When True, prints indentation diagnostics, by default False.   

        """
        self.lex = None
        self.data = None
        self.debug = debug
        self.errors = errors
        self.symbol_table = SymbolTable()

        # Indentation state
        self._indent_stack = [0]     # absolute columns (0, 4, 8, ...)
        self._pending = []           # queue of synthetic INDENT/DEDENT tokens
        self._expect_indent = False  # becomes True after ':' outside delimiters
        self._delim_depth = 0        # (), [], {} 


    def build(self):
        """
        Build and initialize the underlying PLY lexer.
        Creates the PLY lexer with `module=self` so PLY can discover the `t_...` rules.
        Captures the original `token` function.
        Installs `_next_token` as the token producer to interleave pending INDENT/DEDENT.

        """
        self.lex = lex.lex(module=self)
        self._base_token = self.lex.token
        self.lex.token = self._next_token  


    def input(self, data: str):
        """
        Feed source text to the lexer.
        A leading newline is prepended to ensure the first physical line passes through
        `t_NEWLINE`, which is where indentation is evaluated and the base indent (0)
        is asserted.

        """
        self.data = data
        if not data.startswith("\n"):
            data = "\n" + data  
        self.lex.input(data)
        

 
    def _next_token(self):
        """
        Token source that can also emit extra INDENT/DEDENT tokens.
        Returns lex.LexToken | None
        The next token to emit, or None when the input has truly ended (EOF).

        """
        while True:         
            if self._pending:
                return self._pending.pop(0)
           
            tok = self._base_token()
           
            if tok is None:            
                if self.lex.lexpos >= len(self.lex.lexdata):                    
                    return None               
                continue

            if tok.type in OPEN_DELIMS:
                self._delim_depth += 1
            elif tok.type in CLOSE_DELIMS:
                if self._delim_depth > 0:
                    self._delim_depth -= 1
            if tok.type in SUITE_COLON and self._delim_depth == 0:
                self._expect_indent = True

            if self._pending:
                self._pending.append(tok)
                return self._pending.pop(0)
            
            return tok

    # ---- Internal helpers (also used by `.indentation`) ----
    def _make_token(self, type_, value, lineno, lexpos):
        """
        Creates and returns a LexToken object with the specified attributes.
        Args:
            type_ (str): The type/category of the token
            value: The actual value/text of the token
            lineno (int): The line number where the token appears
            lexpos (int): The position/index where the token starts in the input
        Returns:
            lex.LexToken: A token object containing the specified type, value, line number and position
        """
        tok = lex.LexToken()
        tok.type = type_
        tok.value = value
        tok.lineno = lineno
        tok.lexpos = lexpos
        return tok

    def _indent_error(self, msg, lineno, lexpos):
        """
        Reports an indentation error during lexical analysis.
        This method adds the indentation error to the error collection and
        optionally prints debug information.
        Args:
            msg (str): The error message describing the indentation issue.
            lineno (int): The line number where the error occurred.
            lexpos (int): The position in the input where the error occurred.

        """
        self.errors.append(Error(msg, lineno, lexpos, "lexer", self.data))
        if self.debug:
            print(f"[INDENT-ERROR] {msg} @ line {lineno}")


    # ---- PLY rules (t_...) ----
    def t_ID(self, t):
        r"[A-Za-z_][A-Za-z0-9_]*"
        t.type = self.keywords.get(t.value, "ID")
        if t.type == "ID":
            # Optional: symbol table registration (kept as in your base)
            try:
                self.symbol_table.add(t.value, t.lexpos, t.lineno, "identifier")
            except Exception:
                pass
        return t
    
    def t_WS(self, t):
        r"[ \t]+"
        # NOTE: Inline spaces/tabs are ignored. Indentation at line start is handled in `t_NEWLINE`.
        return None

    # TODO: Fix (Not a one line comment)
    def t_COMMENT(self, t):
        r"\#.*"
        return None

    def t_STRING(self, t):
        # TODO(Andres): Multiline doesn't allow \n inside single/double quotes. Asks if this is correct.
        r"(?:\"\"\"(?:[^\"\\]|\\.|\"(?!\"\"))*\"\"\"|\'\'\'(?:[^\'\\]|\\.|\'(?!\'\'))*\'\'\'|\"(?:[^\"\\\n]|\\.)*\"|\'(?:[^\'\\\n]|\\.)*\')"
        if t.value.startswith('"""') or t.value.startswith("'''"):
            content = t.value[3:-3] # Triple quotes - multiline OK
        else:
            content = t.value[1:-1] # Single/double quotes

        # Process basic escapes    
        content = (
            content.replace(r"\\", "\\")
            .replace(r"\"", '"')
            .replace(r"\'", "'")
            .replace(r"\n", "\n")
            .replace(r"\t", "\t")
            .replace(r"\r", "\r")
        )
        t.value = content
        return t

    def t_error_unterminated_string(self, t):
        r'(?:"""|\'\'\'|["\']).+?(?=\n|$)'
        msg = "Unterminated string literal"
        self.errors.append(Error(msg, t.lineno, t.lexpos, "lexer", self.data))
        t.lexer.skip(len(t.value))
        return None

    def t_NEWLINE(self, t):
        r"(?:\r?\n[ \t]*)+"
        # NOTE: Delegates indentation logic to `.indentation.process_newline_and_indent`.
        #       This rule never returns a token; it only enqueues INDENT/DEDENT to `self._pending`.
        process_newline_and_indent(self, t, TAB_WIDTH)
        return None

    def t_NUMBER(self, t):
        r"((\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)"
        if "." in t.value or "e" in t.value or "E" in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    def t_error(self, t):
        """
        Default error handler for illegal/unrecognized characters.
        Parameters   
        t : lex.LexToken
            Token positioned at the offending character.

        """
        msg = f"Illegal character '{t.value[0]}'"
        self.errors.append(Error(msg, t.lineno, t.lexpos, "lexer", self.data))
        t.lexer.skip(1)

    def t_eof(self, t):
        """
        End-of-file used by PLY to finalize token emission.
        If there are pending INDENT/DEDENT tokens in `self._pending`, return them first.
        If `_indent_stack` holds more than the base level, pop one level and emit a DEDENT.
        PLY will call `t_eof` again until the stack is fully drained.
        If nothing remains, return None to signal end-of-input.
        Parameters:
        t : lex.LexToken
            The (unused) token object provided by PLY at EOF.

        """
        if self._pending:
            return self._pending.pop(0)

        if len(self._indent_stack) > 1:
            self._indent_stack.pop()
            return self._make_token("DEDENT", "", getattr(self.lex, "lineno", 1), getattr(self.lex, "lexpos", 0))
        return None    