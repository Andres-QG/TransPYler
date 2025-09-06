import sys
from src.lexer.lexer import Lexer

# TODO(Andres): Fix output formatting for comparison


def read_file(file_path):
    """Read contents of a file"""
    try:
        with open(file=file_path, mode="r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        sys.exit(1)


def format_token(token):
    if token.type in ("INDENT", "DEDENT", "NEWLINE"):
        return f"{token.type}"
    return f'{token.type} "{token.value}"'


def compare_results(lexer_output, expected_output):
    """Compare lexer output with expected output"""
    lexer_tokens = [format_token(token) for token in lexer_output]
    expected_lines = [
        line.strip() for line in expected_output.strip().split("\n") if line.strip()
    ]

    if len(lexer_tokens) != len(expected_lines):
        print("❌ Test failed: Number of tokens doesn't match")
        print(f"Expected {len(expected_lines)} tokens, got {len(lexer_tokens)}")
        print("\nActual tokens:")
        for token in lexer_tokens:
            print(token)
        print("\nExpected tokens:")
        for token in expected_lines:
            print(token)
        return False

    for i, (actual, expected) in enumerate(zip(lexer_tokens, expected_lines)):
        if actual.strip() != expected.strip():
            print(f"❌ Mismatch at token {i+1}:")
            print(f"Expected: {expected}")
            print(f"Got: {actual}")
            return False

    return True


def main():
    if len(sys.argv) != 3:
        print("Usage: python manual_tester.py <test_file> <expected_file>")
        sys.exit(1)

    test_file = sys.argv[1]
    expected_file = sys.argv[2]

    # Read input files
    test_content = read_file(test_file)
    expected_content = read_file(expected_file)

    # Initialize lexer and get tokens
    errors = []
    lexer = Lexer(errors)
    lexer.build()
    lexer.data = test_content
    lexer.lex.input(test_content)

    # Collect all tokens
    tokens = []
    while True:
        tok = lexer.lex.token()
        if not tok:
            break
        tokens.append(tok)

    # Compare results
    if compare_results(tokens, expected_content):
        print("✅ Test passed: All tokens match expected output")
    else:
        print("❌ Test failed: Tokens don't match expected output")

    # Print any lexical errors
    if errors:
        print("\nLexical Errors:")
        for error in errors:
            print(f"Line {error.line}: {error.message}")


if __name__ == "__main__":
    main()
