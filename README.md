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

### 5.1 Running tests from files

```bash
python -m src.testers.manual_tester <test> <expect>
```

- **test**: Path of the file that contains a fangless python (.flpy) code for testing.
- **expect**: Path of the file that contains the sequence of tokens to expect when testing `test`.

### 5.2 Example

**Test (`strings_and_indent.flpy`):**

```python
# Function
def f():
    s1 = "Quote\"mark"
    s2 = 'Back\\slash'
    s3 = ''
    return s1
```

**Expected Tokens (`strings_and_indent.expect`):**

```plain
DEF "def"
ID "f"
LPAREN "("
RPAREN ")"
COLON ":"
INDENT
ID "s1"
ASSIGN "="
STRING "Quote"mark"
ID "s2"
ASSIGN "="
STRING "Back\slash"
ID "s3"
ASSIGN "="
STRING ""
RETURN "return"
ID "s1"
DEDENT
```

**Input (terminal)**

```bash
python -m src.testers.manual_tester strings_and_indent.flpy strings_and_indent.expect
```

**Output (from `manual_tester.py`)**

```plain
✅ Test passed: All tokens match expected output
```

---

## 6. Project Design

### 6.1 File structure

```plain
TransPYler/
│── src/
│   │── core/
│   │   │── __init__.py
│   │   │── symbol_table.py
│   │   │── utils.py
│   │
│   │── lexer/
│   │   │── __init__.py
│   │   │── indentation.py
│   │   │── lexer.py
│   │   │── tokens.py
│   │
│   │── testers/
│   |   │── __init__.py
│   |   │── manual_tester.py
│   |   │── test_lexer.py
|   |
|   |── __init__.py
│
│── tests/
│   │── lexer/
│   │── parser/
│
│── .gitignore
│── pytest.ini
│── README.md
│── requirements.txt
```

### 6.2 Lexer Design

[Read about TransPYler's lexer design here](doc/lexer_design.md)

---

## 7. Development Workflow

- Code and documentation are written in **English**.
- Git workflow:

  - Branch naming: `TASK_<#>_<BriefDescription>`
  - Contributions via **Pull Requests** only.

- Code must be clean, modular, and documented.

---

## 8. Automatic Testing

### 8.1 Strategy

- Unit tests for token recognition.
- Integration tests with Fangless Python snippets.
- Error cases: invalid characters, indentation, escape sequences.

### 8.2 Run tests

This project uses [pytest](https://docs.pytest.org/) for testing.

1. **Install dependencies**  
   Make sure you have installed all requirements first:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the full test suite**
   From the project root, run:

   ```bash
   pytest
   ```

   By default, pytest will automatically discover all tests with `test_` on their name.

3. **Run tests with more detailed output**

   ```bash
   pytest -v
   ```

   The -v (verbose) flag shows each test name and its result.

4. **Run a specific test file**

   ```bash
   pytest src/testers/test_lexer.py
   ```

5. **Stop at the first failure**

   ```bash
   pytest -x
   ```

---

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

| Name                    | Email                          | Role/Contribution                                                                                 |
| ----------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------- |
| Andrés Quesada-González | <andresquesadagon4@gmail.com>  | Operator and literal token definition, documentation, project structure, test scripts, test cases |
| David Obando-Cortés     | <david.obandocortes@ucr.ac.cr> | Indentation Handling, Keywords definition                                                                                              |
| Randy Agüero-Bermúdez   | <randy.aguero@ucr.ac.cr>       | Testing, comment handling, Identifier token definition recognition                                                                                             |
