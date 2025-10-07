from src.parser.parser import Parser
from src.core.ast import  LiteralExpr, Identifier, UnaryExpr, BinaryExpr,ComparisonExpr, CallExpr, Assign, Return, Block, If

def parse(code):
    parser = Parser(debug=False)
    return parser.parse(code)

# ======== PRUEBAS ========
if __name__ == "__main__":
    # Literal
    ast = parse("42")
    print(ast, type(ast))
    
    # Identificador
    ast = parse("x")
    print(ast, type(ast))
    
    # Unary
    ast = parse("-42")
    print(ast, type(ast), ast.op, ast.operand.value)
    
    # Binario
    ast = parse("2 + 3")
    print(ast, type(ast), ast.left.value, ast.op, ast.right.value)
    
    # Asignacion
    ast = parse("x = 10\n")
    print(ast, type(ast), ast.target.name, ast.value.value)
    
    # If simple
    code = """
if x > 0:
    y = 1
"""
    ast = parse(code)
    print(ast, type(ast))
    print("Body:", ast.body.statements[0].target.name, ast.body.statements[0].value.value)
