import os
import sys


sys.path.insert(0, os.path.abspath("src"))

from transpyler.lexer import Lexer
from transpyler.utils import Error


def load_expected_tokens(filepath):
    """
    Load expected tokens from a .expect file.
    Each line should be: TOKEN VALUE
    For example:
        ID my_var
        IF if
    """
    expected = []
    if not os.path.exists(filepath):
        return expected

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                expected.append((parts[0], parts[1]))
            else:
                expected.append((parts[0], ""))
    return expected


def test_file(filepath, debug=False):
    """
    Test lexer against a single file.
    Compares tokens against a corresponding .expect file.
    """
    errors = []
    lx = Lexer(errors, debug=debug)
    lx.build()

    # Read test code
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    # Load expected tokens
    expect_file = filepath.replace(".txt", ".expect")
    expected_tokens = load_expected_tokens(expect_file)

    lx.lex.input(code)
    success = True

    print(f"\n--- Testing file: {filepath} ---")
    for idx, expected in enumerate(expected_tokens):
        tok = lx.lex.token()
        if not tok:
            print(f"Missing token at position {idx}, expected {expected}")
            success = False
            break
        if (tok.type, str(tok.value)) != expected:
            print(
                f"Token mismatch at index {idx}: got ({tok.type}, {tok.value}), expected {expected}"
            )
            success = False

    # Check for extra tokens
    extra_tok = lx.lex.token()
    if extra_tok:
        print(f"Extra token found: ({extra_tok.type}, {extra_tok.value})")
        success = False

    if errors:
        print("\nLexer Errors:")
        for e in errors:
            print(e)
        success = False

    if success:
        print("Test passed ✅")
    else:
        print("Test failed ❌")


def test_directory(directory, debug=False):
    """
    Test all .txt files in a directory with their corresponding .expect files.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            test_file(os.path.join(directory, filename), debug=debug)


if __name__ == "__main__":
    # Example usage: tests folder contains .txt and .expect pairs
    test_directory("tests", debug=True)
