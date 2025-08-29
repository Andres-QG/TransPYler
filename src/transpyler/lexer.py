import ply.lex as lex

from .utils import Error
from .symbol_table import SymbolTable


class Lexer:
    def __init__(self, errors: list[Error], debug=False):
        self.lex = None
        self.data = None
        self.debug = debug
        self.symbol_table = SymbolTable()
        #self.reserved_map = {}
        self.errors = errors  # to use the same list of errors that the parser uses
        #for r in self.reserved:
        #    self.reserved_map[r.lower()] = r

    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'then': 'THEN',
        'while': 'WHILE',
        'for': 'FOR',
        'do': 'DO',
        'to': 'TO',
        'read': 'READ',
        'write': 'WRITE',
        'program': 'PROGRAM',
        'declare': 'DECLARE',
        'integer': 'INTEGER',
        'decimal': 'DECIMAL',
        'begin': 'BEGIN',
        'end': 'END',
        'and': 'AND',
        'or': 'OR',
        'not': 'NOT',
        'mod': 'MOD',
    }

    tokens = tuple(reserved.values()) + (
        # Literals (identifier, integer constant, float constant, string constant, char const)'ID',
        'ID', 'NUMBER', 'SCONST',

        # Operators (+,-,*,/,%,<,>,<=,>=,==,!=,&&,||,!,=)
        'PLUS', 'MINUS', 'MULTI', 'DIVIDE', 'LPAREN', 'RPAREN', 'COMMA', 'SEMICOLON', 'COLON', 'EQUAL', 'LESS',
        'LESSEQUAL', 'GREATER', 'GREATEREQUAL', 'ASSIGN', 'DOT', 'DOUBLEGREATER', 'DOUBLELESS', 'TRIPLELESS',
        'TRIPLEGREATER', 'LESSGREATER', 'TERNAL', 'LITERAL'
    )

    # Regular expression rules for simple tokens

    # Operators
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MULTI = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COMMA = r','
    t_SEMICOLON = r';'
    t_COLON = r':'
    t_EQUAL = r'='
    t_LESS = r'<'
    t_GREATER = r'>'
    t_ASSIGN = r':='
    t_DOT = r'\.'
    t_DOUBLEGREATER = r'>>'
    t_DOUBLELESS = r'<<'
    t_TRIPLELESS = r'<<<'
    t_TRIPLEGREATER = r'>>>'
    t_LESSGREATER = r'<>'
    t_TERNAL = r'\?'
    
    t_LESSEQUAL = r'<='
    t_GREATEREQUAL = r'>='


    # String literal
    t_SCONST = r'\"([^\\\n]|(\\.))*?\"'

    t_ignore = ' \t'

    def log(self, msg: str):
        if self.debug:
            print(f"DEBUG(LEXER): {msg}")

    # This rules matches identifiers that start with a letter or underscore, and may contain letters, digits, underscores.
    # If the value is in "self.reserve", it is classified as a keyword. Otherwise it remains an 'ID'.
    # Errors are logged without stopping the lexer. In debud mode, token details are printed.

    def t_ID(self, t):
       

        r'[a-zA-Z_][a-zA-Z0-9_]*'
        
       # Check if the token is a reserved word
        t.type = self.reserved.get(t.value.lower(), 'ID')

        # Register in symbol table, redeclarations allowed by design
        if t.type == 'ID':
            try:
                self.symbol_table.add(t.value, t.lexpos, t.lineno, 'identifier')
            except Exception as e:
                self.log(f"Redeclaration ignored: {t.value} at line {t.lineno}, pos {t.lexpos}")  # Comment about design choice

        self.log(f"Token {t.type}={t.value} at line {t.lineno}, pos {t.lexpos}")
        return t

    # TODO: Podría ser un sólo token t_NUMBER y t_DECIMAL?
    def t_NUMBER(self, t):
        r"""\d+"""
        t.value = int(t.value)
        return t

    def t_DECIMAL(self, t):
        r"""\d+\.\d+"""
        t.value = float(t.value)
        return t

    def t_LITERAL(self, t):
        r"""\"[^"]*\\"""
        return t

    def t_NEWLINE(self, t):
        r"""\n+"""
        t.lexer.lineno += len(t.value)

    def t_COMMENT(self, t):
        r'\#.*'
        self.log(f"Comment ignored at line {t.lineno}")
        return None  # Ignore comments

    def t_error(self, t):
        error_msg = f"Illegal character '{t.value[0]}'"
        self.errors.append(Error(error_msg, t.lineno, t.lexpos, 'lexer', self.data))
        self.log(error_msg)
        t.lexer.skip(1)

    def build(self, ):
        self.lex = lex.lex(module=self)
