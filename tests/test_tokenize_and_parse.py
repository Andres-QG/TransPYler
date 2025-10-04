import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


import json
from src.parser.parser import Parser
from src.lexer.lexer import Lexer

def test_tokenize_and_parse(code: str):
    # 1. Tokenizar el código con el Lexer
    lexer = Lexer(errors=[])
    lexer.build()
    lexer.input(code)  # Pasamos el código al lexer

    # 2. Crear el parser
    parser = Parser(debug=False)

    # 3. Parsear el código con el lexer tokenizado
    ast = parser.parse(code)

    # 4. Convertir el AST a formato JSON
    ast_json = ast.to_dict()

    # 5. Imprimir el AST en la consola (ver en formato JSON)
    print("AST generado:")
    print(json.dumps(ast_json, indent=4))  # Imprime el AST como JSON en la consola

# Código de ejemplo para probar
code_example = """
def suma(a, b):
    return a + b

x = suma(3, 5)
"""

# Ejecutar la prueba
test_tokenize_and_parse(code_example)
