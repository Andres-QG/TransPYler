"""
Tests for parsing invalid Python-like statements and structures.
"""

import pytest
from src.parser.parser import Parser


@pytest.fixture
def parser():
    return Parser(debug=False)


class TestInvalidAssignments:
    """Test invalid assignment syntax."""

    def test_assignment_to_literal(self, parser):
        code = "1 = a"
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Parser should report error for '1 = a'"

    def test_assignment_to_expression(self, parser):
        code = "(a + b) = 5"
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Parser should not allow '(a + b) = 5'"


class TestInvalidIndentation:
    def test_bad_indentation_in_if(self, parser):
        code = """
if True:
print("bad indent")
"""
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Parser should detect bad indentation"

class TestInvalidLoops:
    def test_missing_colon_in_for(self, parser):
        code = """
for i in range(3)
    print(i)
"""
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Missing ':' should trigger a syntax error"

    def test_missing_colon_in_while(self, parser):
        code = """
while x < 5
    x += 1
"""
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Parser should detect missing ':' in while loop"


class TestInvalidPrints:
    """Test invalid print statement syntax."""

    def test_print_with_missing_expression(self, parser):
        code = "print(,1,2)"
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Parser should flag 'print(,1,2)' as invalid"

    def test_print_with_missing_comma(self, parser):
        code = "print(1 2)"
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Parser should detect missing comma in print()"


class TestInvalidDataStructures:
    """Test malformed lists, tuples, and dictionaries."""

    def test_extra_comma_in_list(self, parser):
        code = "nums = [1, 2,, 3]"
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Parser should reject list with extra comma"

    def test_dict_with_missing_value(self, parser):
        code = 'data = {"key": 1, "value"}'
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Missing value should cause a syntax error"

    def test_tuple_with_extra_comma(self, parser):
        code = "coords = (10, 20,,)"
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Parser should detect extra comma in tuple"

    def test_unbalanced_brackets(self, parser):
        code = "broken = [1, [2, [3, 4]]"
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Parser should report unbalanced brackets"

    def test_unclosed_dict(self, parser):
        code = 'weird_dict = {"a": 1, "b": 2'
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Parser should detect unclosed dict"

class TestInvalidOperators:
    """Test invalid operator usage."""

    def test_invalid_operator_combination(self, parser):
        code = "x = 5 @ 3"
        ast = parser.parse(code)
        assert ast is None or parser.errors, "Parser should reject unsupported operator '@'"


class TestParserResilience:
    """Ensure parser does not crash on invalid input."""

    @pytest.mark.parametrize(
        "code",
        [
            "1 = a",
            "(a + b) = 5",
            "for i in range(3)",
            "while x < 5",
            "nums = [1, 2,, 3]",
            'data = {"key": 1, "value"}',
            "broken = [1, [2, [3, 4]]",
            'weird_dict = {"a": 1, "b": 2',
        ],
    )
    def test_parser_does_not_crash_on_invalid_code(self, parser, code):
        try:
            parser.parse(code)
        except Exception as e:
            pytest.fail(f"Parser crashed unexpectedly: {e}")

        assert parser.errors, f"Invalid code should produce errors: {code!r}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
