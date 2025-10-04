import json
from src.parser.parser import Parser
from src.lexer.lexer import Lexer
import os

def tokenize_and_parse(file_path: str):
    # 1. Leer el archivo de entrada
    with open(file_path, 'r') as f:
        code = f.read()

    # 2. Tokenizar el código con el Lexer
    lexer = Lexer(errors=[])
    lexer.build()
    lexer.input(code)  # Pasamos el código al lexer

    # 3. Crear el parser
    parser = Parser(debug=False)  # Crear una instancia del parser

    # 4. Parsear el código con el lexer tokenizado
    ast = parser.parse(code)

    # 5. Convertir el AST a formato JSON
    ast_json = ast.to_dict()

    # 6. Definir la ruta para guardar el archivo JSON
    output_path = 'ast_output.json'  # En la raíz del proyecto

    # 7. Guardar el resultado en un archivo JSON
    try:
        with open(output_path, 'w') as f:
            json.dump(ast_json, f, indent=4)  # Guardamos el árbol en formato legible
        print(f"AST generado y guardado como '{output_path}'.")
    except Exception as e:
        print(f"Error al guardar el archivo JSON: {e}")
    
    # 8. Imprimir el AST en la consola para verlo
    print(json.dumps(ast_json, indent=4))  # Imprime el AST como JSON en la consola

# Llamada a la función con la ruta del archivo de prueba
tokenize_and_parse("tests/lexer/Integration_test_4.flpy")


