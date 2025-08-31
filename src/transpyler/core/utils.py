from typing import Literal


class Error:
    """
    Represents a compilation error with context information.

    Attributes:
        message (str): Description of the error.
        line (int): Line number where the error occurred.
        column (int): Column number where the error occurred.
        type (str): Type of error ('lexer', 'parser', or 'semantic').
        data (str, optional): Source code data for context.
    """

    def __init__(
        self,
        message,
        line,
        column,
        _type: Literal["lexer", "parser", "semantic"],
        data=None,
    ):
        self.message = message
        self.line = line
        self.column = column
        self.type = _type
        self.data = data

    def __repr__(self):
        return (
            f"ERROR({self.type.upper()}): {self.message} at line {self.line}, column {self.column}"
            + (
                f". On:\n{get_context(self.data, self.line, self.column)}"
                if self.data
                else ""
            )
        )

    def exact(self):
        """
        Returns a concise string representation of the error.
        """
        return f"Error({self.message}, line={self.line}, column={self.column}, _type={self.type})"

    def __eq__(self, other):
        return (
            self.message == other.message
            and self.line == other.line
            and self.column == other.column
            and self.type == other.type
        )


def get_context(data, lineno, lexpos):
    """
    Returns a string showing the line and position of an error in the source code.

    Args:
        data (str): Source code.
        lineno (int): Line number of the error.
        lexpos (int): Position in the source code.

    Returns:
        str: Context string with a caret (^) marking the error position.
    """
    error_line = data.split("\n")[lineno - 1]
    where = (
        error_line.lstrip()
        + "\n"
        + " "
        * (
            (lexpos - len("\n".join(data.split("\n")[: lineno - 1])))
            - ((len(error_line) - len(error_line.lstrip())) + 1)
        )
        + "^"
    )
    return where
