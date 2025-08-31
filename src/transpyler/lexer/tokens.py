#   Configuration / Constants
TAB_WIDTH = 4  # one tab counts as 4 spaces for indentation

KEYWORDS = {
    # Flow control
    "if": "IF",
    "else": "ELSE",
    "elif": "ELIF",
    "while": "WHILE",
    "for": "FOR",
    "break": "BREAK",
    "continue": "CONTINUE",
    "pass": "PASS",
    # Definitions
    "def": "DEF",
    "return": "RETURN",
    "class": "CLASS",
    # Booleans (case-sensitive like Python)
    "True": "TRUE",
    "False": "FALSE",
    # Logical operators
    "and": "AND",
    "or": "OR",
    "not": "NOT",
}

TOKENS = (
    tuple(set(KEYWORDS.values()))
    + ("ID", "INDENT", "DEDENT")
    + (  # * Are this token names to long?
        # Literals
        "NUMBER",
        "STRING",
        # Operators
        ## Arithmetic
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "FLOOR_DIVIDE",
        "MOD",
        "POWER",
        ## Relational
        "EQUALS",
        "NOT_EQUALS",
        "LESS_THAN",
        "LESS_THAN_EQUALS",
        "GREATER_THAN",
        "GREATER_THAN_EQUALS",
        ## Assignment
        "ASSIGN",
        "PLUS_ASSIGN",
        "MINUS_ASSIGN",
        "TIMES_ASSIGN",
        "DIVIDE_ASSIGN",
        "FLOOR_DIVIDE_ASSIGN",
        "MOD_ASSIGN",
        "POWER_ASSIGN",
        # Delimiters
        "LPAREN",
        "RPAREN",
        "LBRACE",
        "RBRACE",
        "LBRACKET",
        "RBRACKET",
        "COLON",
        "COMMA",
        "DOT",
        # Special
        "NEWLINE",
    )
)
