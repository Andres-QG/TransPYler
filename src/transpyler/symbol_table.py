class SymbolTable:
    """
    Manages a symbol table for identifiers in source code.

    Stores symbol names, their positions, and types. Provides methods to add, check, retrieve, and remove symbols.
    """

    def __init__(self):
        self.table = {}

    def __str__(self):
        return str(self.table)

    def add(self, symbol, pos, line, tk_type=None):
        """
        Adds a symbol to the table.

        Args:
            symbol (str): The identifier name.
            pos (int): Position in the source code.
            line (int): Line number.
            tk_type (str, optional): Type of the symbol.

        Raises:
            Exception: If the symbol is already declared.
        """
        if symbol not in self.table:
            self.table[symbol] = {
                "Position": {"line": line, "pos": pos},
                "Type": tk_type,
            }
        else:
            raise Exception(f"{symbol} has already been declared")

    def exists(self, symbol):
        """
        Checks if a symbol exists in the table.

        Args:
            symbol (str): The identifier name.

        Returns:
            bool: True if symbol exists, False otherwise.
        """
        return symbol in self.table

    def get(self, symbol):
        """
        Retrieves information about a symbol.

        Args:
            symbol (str): The identifier name.

        Returns:
            dict: Symbol information.

        Raises:
            Exception: If the symbol is not declared.
        """
        if symbol in self.table:
            return self.table[symbol]

        raise Exception(f"{symbol} has not been declared")

    def remove(self, symbol):
        """
        Removes a symbol from the table.

        Args:
            symbol (str): The identifier name.
        """
        del self.table[symbol]
