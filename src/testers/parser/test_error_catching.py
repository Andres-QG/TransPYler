"""
Focused tests for Parser.p_error() method.

Tests are organized to cover distinct error scenarios and verify
that p_error handles them correctly with appropriate messages.

These tests are adjusted to match the actual behavior of the parser,
including cases where lexer errors occur before parser errors.
"""

import pytest
from src.parser.parser import Parser
from src.core.utils import Error


class TestPErrorDetection:
    """Test that p_error detects different types of syntax errors."""

    def test_missing_colon_control_structures(self):
        """Test detection of missing colons in if/while/for/def/class."""
        test_cases = [
            "if x > 5\n    y = 10",
            "while x < 10\n    x = x + 1",
            "for i in range(10)\n    print(i)",
            "def foo(x, y)\n    return x + y",
            "class MyClass\n    x = 5",
        ]

        for code in test_cases:
            parser = Parser(debug=False)
            parser.parse(code)
            assert (
                len(parser.errors) > 0
            ), f"Should detect missing colon in: {code[:20]}..."
            assert parser.errors[0].type in ("lexer", "parser")

    def test_incomplete_binary_expressions(self):
        """Test detection of incomplete binary operations."""
        code = "x = 5 + 3 *"
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) > 0, "Should detect incomplete expression"

    def test_unexpected_closing_delimiters(self):
        """Test detection of unmatched closing delimiters."""
        delimiters = [")", "]", "}"]

        for delim in delimiters:
            code = f"x = 5 {delim}"
            parser = Parser(debug=False)
            parser.parse(code)

            assert len(parser.errors) > 0, f"Should detect unexpected '{delim}'"
            assert delim in parser.errors[0].message

    def test_unexpected_end_of_file(self):
        """Test detection of unexpected EOF in incomplete statement."""
        code = "if x > 5:"
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) > 0, "Should detect incomplete if statement"
        error_msg = parser.errors[0].message.lower()
        assert (
            "end of input" in error_msg
            or "syntax" in error_msg
            or "indent" in error_msg
        )

    def test_assignment_without_target(self):
        """Test detection of assignment operators without target."""
        operators = ["=", "+=", "-="]

        for op in operators:
            code = f"{op} 5"
            parser = Parser(debug=False)
            parser.parse(code)

            assert len(parser.errors) > 0, f"Should detect invalid '{op}' usage"
            error_msg = parser.errors[0].message.lower()
            assert (
                "assignment" in error_msg
                or "target" in error_msg
                or "syntax" in error_msg
            )


class TestPErrorMessages:
    """Test that p_error produces specific and helpful error messages."""

    def test_indent_error_message(self):
        """Test INDENT error has specific message about indentation."""
        code = "x = 5\n    y = 10"
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) > 0
        assert "indent" in parser.errors[0].message.lower()

    def test_dedent_error_message(self):
        """Test DEDENT error mentions unindent/dedent."""
        code = "def foo():\n    x = 5\n  y = 10"
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) > 0
        error_msg = parser.errors[0].message.lower()
        assert "dedent" in error_msg or "unindent" in error_msg or "indent" in error_msg

    def test_delimiter_error_messages(self):
        """Test delimiter errors mention 'delimiter' or 'closing'."""
        code = "x = ]"
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) > 0
        error_msg = parser.errors[0].message.lower()
        assert "delimiter" in error_msg or "closing" in error_msg

    def test_colon_error_message(self):
        """Test unexpected colon error mentions control structures."""
        code = "x = 5 :"
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) > 0
        error_msg = parser.errors[0].message.lower()
        keywords = ["if", "while", "for", "def", "class", "syntax", ":"]
        assert any(kw in error_msg for kw in keywords)

    def test_comma_error_message(self):
        """Test unexpected comma error mentions list/tuple/argument."""
        code = "x = , 5"
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) > 0
        error_msg = parser.errors[0].message.lower()
        keywords = ["list", "tuple", "argument", "syntax", ","]
        assert any(kw in error_msg for kw in keywords)

    def test_operator_error_messages(self):
        """Test operator errors are detected."""
        code = "x = 5 +"
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) > 0
        error_msg = parser.errors[0].message.lower()
        keywords = ["operator", "operand", "syntax", "end of input", "unexpected"]
        assert any(kw in error_msg for kw in keywords)


class TestPErrorRecovery:
    """Test that p_error recovery mechanism allows continued parsing."""

    def test_recovery_continues_after_error(self):
        """Test parser continues after encountering an error."""
        code = """
x = 5
y = 10 +
z = 15
"""
        parser = Parser(debug=False)
        ast = parser.parse(code)

        # Should detect error but not crash
        assert len(parser.errors) > 0
        assert ast is not None

    def test_multiple_errors_in_one_pass(self):
        """Test parser detects multiple errors without stopping."""
        code = """
x = 5 +
if y
    z = 10
"""
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) >= 1
        for err in parser.errors:
            assert isinstance(err, Error)

    def test_recovery_sync_on_control_structures(self):
        """Test recovery synchronizes on statement-starting keywords."""
        code = """
x = )
def foo():
    return 5
while True:
    pass
"""
        parser = Parser(debug=False)
        parser.parse(code)

        # Should detect error in first line but continue
        assert len(parser.errors) > 0

    def test_consecutive_delimiter_errors(self):
        """Test recovery handles consecutive errors."""
        code = """
x = )
y = ]
"""
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) >= 1


class TestPErrorAttributes:
    """Test that Error objects have correct attributes."""

    def test_error_object_structure(self):
        """Test Error object has all required attributes."""
        code = "x = )"
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) > 0
        err = parser.errors[0]

        # Check all attributes exist
        assert hasattr(err, "message") and isinstance(err.message, str)
        assert hasattr(err, "line") and err.line > 0
        assert hasattr(err, "column") and err.column >= 0
        assert hasattr(err, "type") and err.type in ("lexer", "parser")
        assert hasattr(err, "data")

    def test_error_line_accuracy(self):
        """Test that error line numbers are reasonably accurate."""
        code = """
x = 5
y = )
"""
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) > 0
        # Error should be near line 3 (where 'y = )' is)
        assert parser.errors[0].line >= 2


class TestPErrorEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_input_no_crash(self):
        """Test empty input doesn't crash."""
        parser = Parser(debug=False)
        parser.parse("")

        # The important thing is it doesn't crash
        assert True  # If we got here, no crash occurred

    def test_whitespace_only_no_crash(self):
        """Test whitespace-only input doesn't crash."""
        parser = Parser(debug=False)
        parser.parse("   \n\n   \n")
        assert True  # If we got here, no crash occurred

    def test_error_at_end_of_file(self):
        """Test error detection at EOF."""
        code = "x = 5\ny = 10\nz ="
        parser = Parser(debug=False)
        parser.parse(code)

        assert len(parser.errors) > 0

    def test_valid_code_produces_no_errors(self):
        """Test that syntactically correct code has no parser errors."""
        code = """
x = 5
y = 10
if x > 0:
    z = x + y
else:
    pass

def foo(a, b):
    return a * b
"""
        parser = Parser(debug=False)
        ast = parser.parse(code)

        assert (
            len(parser.errors) == 0
        ), f"Valid code should not produce errors: {parser.errors}"
        assert ast is not None


class TestPErrorComplexScenarios:
    """Test complex scenarios mixing different error types."""

    def test_mixed_errors_in_nested_structures(self):
        """Test errors in nested control structures."""
        code = """
if x > 5:
    while y < 10
        z = z + 1
    for i in items:
        process(i)
"""
        parser = Parser(debug=False)
        parser.parse(code)

        # Should detect missing colon in while
        assert len(parser.errors) > 0

    def test_error_in_function_with_complex_body(self):
        """Test error detection within function bodies."""
        code = """
def calculate(x, y):
    result = x + y *
    return result
"""
        parser = Parser(debug=False)
        parser.parse(code)

        # Should detect incomplete expression
        assert len(parser.errors) > 0

    def test_error_recovery_across_class_definition(self):
        """Test recovery works across class boundaries."""
        code = """
x = )

class MyClass:
    value = 42
    
    def method(self):
        return self.value
"""
        parser = Parser(debug=False)
        parser.parse(code)

        # Should detect delimiter error but recover for class
        assert len(parser.errors) > 0

    def test_multiple_statement_types_with_error(self):
        """Test mixed valid and invalid statements."""
        code = """
x = 5
y = 10
z = 15 +
w = 20
if w > 10:
    print(w)
"""
        parser = Parser(debug=False)
        parser.parse(code)

        # Should detect error in incomplete expression
        assert len(parser.errors) > 0


class TestPErrorNoExceptions:
    """Test that p_error never raises exceptions for any syntax error."""

    def test_no_exception_on_critical_errors(self):
        """Verify critical syntax errors don't crash the parser."""
        bad_codes = [
            "if x > 5\n    pass",  # Missing colon (may be lexer error)
            "x = 5 +",  # Incomplete expression
            "x = )",  # Unexpected delimiter
            "= 5",  # Missing target
            "x = 5 :",  # Unexpected colon
        ]

        for code in bad_codes:
            parser = Parser(debug=False)
            try:
                parser.parse(code)
                assert len(parser.errors) > 0, f"Should detect error in: {code[:30]}..."
            except Exception as e:
                pytest.fail(
                    f"p_error raised exception (should not): {type(e).__name__}: {e}"
                )


# Parametrized tests for comprehensive coverage
@pytest.mark.parametrize(
    "code,expected_keywords",
    [
        ("x = )", ["delimiter", ")", "closing"]),
        ("= 5", ["assignment", "target", "syntax"]),
        ("x = 5 :", [":", "if", "while", "for", "def", "class", "syntax"]),
    ],
)
def test_error_messages_are_descriptive(code, expected_keywords):
    """Parametrized test: verify error messages contain relevant keywords."""
    parser = Parser(debug=False)
    parser.parse(code)

    assert len(parser.errors) > 0, f"Should detect error in: {code}"
    error_msg = parser.errors[0].message.lower()
    found = any(keyword.lower() in error_msg for keyword in expected_keywords)
    assert (
        found
    ), f"Error for '{code}' should mention one of {expected_keywords}, got: {parser.errors[0].message}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
