"""
Tests for parsing valid Python-like structures (assignments, lists, dicts, loops, conditionals).
"""

import pytest
from src.parser.parser import Parser


class TestValidAssignments:
    """Test parsing of assignment expressions"""

    def test_basic_assignments(self):
        code = """
a = 1
b = 2
c = 3
x = a + b
"""
        parser = Parser(debug=False)
        ast = parser.parse(code)
        assert ast is not None
        assert len(parser.errors) == 0

    def test_mixed_assignment_structures(self):
        code = """
nums = [1, 2, 3, 4]
empty_list = []
coords = (10,20)
nested_tuple = ((1, 2), (3, 4))
person = {"name": "Alice", "age": 30}
empty_dict = {}
data = {"sum": 1 + 2, "nested": {"ok": True, "list": [1, 2, 3]}}
mixed = [1, (2, 3), {"a": 4, "b": [5, 6]}]
"""
        parser = Parser(debug=False)
        ast = parser.parse(code)
        assert ast is not None
        assert len(parser.errors) == 0, parser.errors


class TestValidConditionals:
    """Test correct parsing of if/elif/else structures"""

    def test_if_elif_else(self):
        code = """
a = 1
b = 2
x = a + b

if x > 5:
    result = x * 2
    pass
elif x == 3:
    result = x / 2
else:
    result = 0
"""
        parser = Parser(debug=False)
        ast = parser.parse(code)
        assert ast is not None
        assert len(parser.errors) == 0


class TestValidLoops:
    """Test parsing of while and for loops"""

    def test_while_loop(self):
        code = """
counter = 0
while counter < 3:
    counter += 1
    if counter == 2:
        continue
    if counter == 3:
        break
"""
        parser = Parser(debug=False)
        ast = parser.parse(code)
        assert ast is not None
        assert len(parser.errors) == 0

    def test_for_loop(self):
        code = """
for i in range(2):
    print(i)
"""
        parser = Parser(debug=False)
        ast = parser.parse(code)
        assert ast is not None
        assert len(parser.errors) == 0


class TestNestedStructures:
    """Test nested lists, tuples, and dicts."""

    def test_nested_data_structures(self):
        code = """
nested_list = [1, [2, [3, [4, [5]]]]]
nested_tuple = (1, (2, (3, (4, 5))))
nested_dict = {
    "level1": {
        "level2": {
            "level3": {
                "numbers": [1, 2, 3],
                "letters": ("a", "b", "c"),
                "flag": True
            }
        }
    }
}
"""
        parser = Parser(debug=False)
        ast = parser.parse(code)
        assert ast is not None
        assert len(parser.errors) == 0


class TestMixedControlFlow:
    """Test mixing if, for, and while inside valid nested scopes."""

    def test_if_for_while_mix(self):
        code = """
a = 1
b = 2
c = 3
nested_list = [1, [2, [3, [4, [5]]]]]

if a < 5:
    for i in range(2):
        while b < 4:
            c = c + 1
            if c == 5:
                nested_list.append(c)
            else:
                b += 1
else:
    nested_list = []

final_structure = [
    nested_list,
    (1, (2, (3, (4, 5)))),
    {
        "level1": {
            "level2": {
                "level3": {
                    "numbers": [1, 2, 3],
                    "letters": ("a", "b", "c"),
                    "flag": True
                }
            }
        }
    },
    [{"inner_list": [0, 1, {"deep": [10, 20]}]}]
]
"""
        parser = Parser(debug=False)
        ast = parser.parse(code)
        assert ast is not None
        assert len(parser.errors) == 0, f"Unexpected parser errors: {parser.errors}"


class TestParserNoCrashes:
    """Ensure parser handles complex code without exceptions."""

    @pytest.mark.parametrize(
        "code",
        [
            "a = 1",
            "nums = [1, 2, 3]",
            "if True:\n    pass",
            "while False:\n    break",
            "for i in range(3):\n    print(i)",
        ],
    )
    def test_no_crash_on_valid_code(self, code):
        parser = Parser(debug=False)
        try:
            parser.parse(code)
        except Exception as e:
            pytest.fail(f"Parser crashed on valid code: {e}")

        assert len(parser.errors) == 0, f"Errors found in valid code: {parser.errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
