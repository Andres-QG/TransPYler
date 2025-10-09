from ..core.ast import If


class ConditionalRules:
    """Rules for parsing conditional statements."""
    def p_if_stmt(self, p):
        """if_stmt : IF expr COLON suite elif_blocks else_block_opt"""
        p[0] = If(cond=p[2], body=p[4], elifs=p[5], orelse=p[6])
    def p_elif_blocks(self, p):
        """elif_blocks : ELIF expr COLON suite elif_blocks
        |"""
        if len(p) == 1:
            p[0] = []
        else:
            p[0] = [(p[2], p[4])] + p[5]

    def p_else_block_opt(self, p):
        """else_block_opt : ELSE COLON suite
        |"""
        p[0] = p[3] if len(p) > 1 else None
