# TransPYler

## 1. Overview

**TransPYler** is a compiler-like project designed to translate a simplified subset of Python, called **Fangless Python**, into another target programming language (to be defined).

The project is divided into multiple stages of compilation:

1. **Lexical Analysis (Lexer)** – ✅ _implemented in this version_
2. **Syntactic Analysis (Parser)** – 🚧 _to be implemented_
3. **Semantic Analysis** – 🚧 _future work_
4. **Transpilation/Code Generation** – 🚧 _future work_

At this stage, the project includes only the **Lexer**, which is capable of scanning Fangless Python source code and producing a stream of tokens.

---

## 2. Current Status

- **Implemented**: Lexer for Fangless Python using [PLY (Python Lex-Yacc)](https://www.dabeaz.com/ply/).
- **Pending**: Parser, AST construction, semantic checks, and transpilation to the target language.

This README will serve as a reference for the full transcompiler, but usage examples and tests are focused on the **Lexer** implementation.

---

## 3. Features

### Lexer Features

- Recognizes **keywords** (`if, else, while, for, def, return, class, True, False, and, or, not...`).
- Identifies **identifiers**, **numeric and string literals**, and **operators** (`+, -, *, /, //, %, **, ==, !=, <, >, <=, >=, =, += ...`).
- Supports **delimiters**: `( ) [ ] { } : , .`.
- Handles **comments** starting with `#`.
- Detects **indentation levels**, generating special tokens `INDENT` and `DEDENT`.
- Reports **lexical errors** (unknown characters, invalid escapes, indentation mistakes).

---

## 4. Installation

### 4.1 Requirements

- Python 3.x
- Git + GitHub
- PLY (Python Lex-Yacc)

### 4.2 Setup

```bash
# Clone the repository
git clone https://github.com/Andres-QG/TransPYler.git
cd TransPYler

# (Optional) virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 5. Usage (Current Lexer Stage)

### 5.1 Running the Lexer

```bash
python lexer.py input.fangpy
```

- **Input**: A `.fangpy` file containing Fangless Python code.
- **Output**: A sequence of tokens printed to the console or stored in an output file.

### 5.2 Example

**Input (`example.fangpy`):**

```python
def add(x, y):
    return x + y
```

**Output (tokens):**

```plain
DEF IDENTIFIER LPAREN IDENTIFIER COMMA IDENTIFIER RPAREN COLON NEWLINE INDENT RETURN IDENTIFIER PLUS IDENTIFIER DEDENT
```

---

## 6. Project Structure (TODO: Correct it to be the same as the real projects structure)

```plain
TransPYler/
│── lexer.py        # Main entry point for the Lexer
│── tokens.py       # Token definitions and regex rules
│── tests/          # Test cases for validation
│── docs/           # Documentation and design notes
│── README.md       # This file
```

---

## 7. Development Workflow

- Code and documentation are written in **English**.
- Git workflow:

  - Branch naming: `TASK_<#>_<BriefDescription>`
  - Contributions via **Pull Requests** only.

- Code must be clean, modular, and documented.

---

## 8. Testing

### 8.1 Strategy

- Unit tests for token recognition.
- Integration tests with Fangless Python snippets.
- Error cases: invalid characters, indentation, escape sequences.

### 8.2 Example Test

**Input:**

```python
while x < 10:
    x += 1
```

**Expected Tokens:**

```plain
WHILE IDENTIFIER LT NUMBER COLON NEWLINE INDENT IDENTIFIER PLUSEQ NUMBER NEWLINE DEDENT
```

### TODO: Add more usage examples

---

## 9. Roadmap

- **Phase 1 – Lexer**: ✅ Completed
- **Phase 2 – Parser**: Construction of AST (Abstract Syntax Tree)
- **Phase 3 – Semantic Analysis**: Type checking, symbol tables
- **Phase 4 – Code Generation**: Translate Fangless Python into the target language

---

## 10. References

- [PLY Documentation](https://www.dabeaz.com/ply/)
- [Python 3 Language Reference](https://docs.python.org/3/reference/)

## 11. Authors

| Name                    | Email                          | Role/Contribution                                                                |
| ----------------------- | ------------------------------ | -------------------------------------------------------------------------------- |
| Andrés Quesada-González | <andresquesadagon4@gmail.com>  | Operator and literal token definition, documentation, project structure, testing |
| David Obando-Cortés     | <david.obandocortes@ucr.ac.cr> | TODO                                                                             |
| Randy Agüero-Bermúdez   | <randy.aguero@ucr.ac.cr>       | TODO                                                                             |
