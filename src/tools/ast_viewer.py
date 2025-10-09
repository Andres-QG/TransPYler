# src/tools/ast_viewer.py
from __future__ import annotations
import json
from typing import List, Tuple
from src.core.ast.ast_base import AstNode
from src.core.ast import (
    Module, ExprStmt, If, While, For, Assign, Block, Pass, Continue, Break,
    TupleExpr, ListExpr, DictExpr, Attribute, Subscript
)

# ---------------- JSON ----------------
def ast_to_json(node: AstNode) -> str:
    return json.dumps(node.to_dict(), indent=2, ensure_ascii=False)

# --------------- Rich -----------------
try:
    from rich.tree import Tree
    RICH_OK = True
except Exception:
    RICH_OK = False
    Tree = None  # type: ignore

def build_rich_tree_generic(node: AstNode, *, label: str | None = None):
    if not RICH_OK:
        raise RuntimeError("Rich is not available.")
    if node is None:
        return Tree("[dim]∅[/dim]")

    cls = node.__class__.__name__
    title = f"[bold]{cls}[/bold]" if label is None else f"[bold]{cls}[/bold] [dim]({label})[/dim]"
    tree = Tree(title)

    for k, v in node.__dict__.items():
        if k in ("line", "col"):
            continue
        if isinstance(v, AstNode):
            tree.add(build_rich_tree_generic(v, label=k))
        elif isinstance(v, list):
            lst = tree.add(f"[italic]{k}[/italic] [dim](list, {len(v)})[/dim]")
            for i, it in enumerate(v):
                if isinstance(it, AstNode):
                    lst.add(build_rich_tree_generic(it, label=f"{k}[{i}]"))
                else:
                    lst.add(f"{k}[{i}] = {repr(it)}")
        else:
            tree.add(f"[italic]{k}[/italic] = {repr(v)}")
    return tree

def build_expr_tree(node: AstNode):
    if not RICH_OK:
        raise RuntimeError("Rich is not available.")
    if node is None:
        return Tree("[dim]∅[/dim]")

    def _label(text: str) -> str:
        return f"[bold]{text}[/bold]"

    def _branch(name: str, child: AstNode):
        t = Tree(f"[dim]{name}[/dim]")
        t.add(build_expr_tree(child))
        return t

    # Binary: left op right
    if all(hasattr(node, a) for a in ("left", "right", "op")):
        root = Tree(_label(str(getattr(node, "op"))))
        root.add(_branch("left", node.left))
        root.add(_branch("right", node.right))
        return root

    # Unary: op operand
    if hasattr(node, "op") and hasattr(node, "operand"):
        root = Tree(_label(str(getattr(node, "op"))))
        root.add(_branch("operand", node.operand))
        return root

    # Identifier
    if hasattr(node, "name"):
        return Tree(f"[cyan]{getattr(node, 'name')}[/cyan]")

    # Literal
    if hasattr(node, "value"):
        return Tree(f"[magenta]{repr(getattr(node, 'value'))}[/magenta]")

    # Call
    if hasattr(node, "callee") and hasattr(node, "args"):
        root = Tree(_label("call"))
        root.add(_branch("callee", node.callee))
        args_t = Tree("[dim]args[/dim]")
        for a in node.args:
            args_t.add(build_expr_tree(a))
        root.add(args_t)
        return root

    # Subscript / Attribute / Collections
    if isinstance(node, Subscript):
        root = Tree(_label("[]"))
        root.add(_branch("value", node.value))
        root.add(_branch("index", node.index))
        return root

    if isinstance(node, Attribute):
        root = Tree(_label("."))  # attribute access
        root.add(_branch("value", node.value))
        root.add(Tree(f"[cyan]{node.attr}[/cyan]"))
        return root

    if isinstance(node, TupleExpr) or isinstance(node, ListExpr):
        root = Tree(_label("()" if isinstance(node, TupleExpr) else "[]"))
        for e in node.elements:
            root.add(build_expr_tree(e))
        return root

    if isinstance(node, DictExpr):
        root = Tree(_label("{}"))
        for k, v in node.pairs:
            pair = Tree(":")
            pair.add(build_expr_tree(k))
            pair.add(build_expr_tree(v))
            root.add(pair)
        return root

    # Fallback
    return build_rich_tree_generic(node)

# --------------- ASCII ----------------
def _expr_label(node: AstNode) -> str:
    cls_name = node.__class__.__name__
    if cls_name in {"Module","Block","If","While","For","Assign","Pass","Continue","Break","ExprStmt"}:
        return cls_name
    if hasattr(node, "op"):
        return str(node.op)
    if hasattr(node, "name"):
        return str(node.name)
    if hasattr(node, "value"):
        return repr(node.value)
    if hasattr(node, "callee"):
        return "call"
    return cls_name

def _expr_children(node: AstNode):
    if hasattr(node, "body") and isinstance(node.body, list):
        return node.body
    if hasattr(node, "statements") and isinstance(node.statements, list):
        return node.statements

    if isinstance(node, If):
        children = [node.cond, node.body]
        for cond, blk in (node.elifs or []):
            children.extend([cond, blk])
        if node.orelse:
            children.append(node.orelse)
        return children

    if isinstance(node, While):
        return [node.cond, node.body]

    if isinstance(node, For):
        return [node.target, node.iterable, node.body]

    if all(hasattr(node, a) for a in ("left","right","op")):
        return [node.left, node.right]
    if hasattr(node, "op") and hasattr(node, "operand"):
        return [node.operand]

    if hasattr(node, "callee") and hasattr(node, "args"):
        return [node.callee] + list(node.args)

    if isinstance(node, Subscript):
        return [node.value, node.index]
    if isinstance(node, Attribute):
        return [node.value]

    if isinstance(node, TupleExpr) or isinstance(node, ListExpr):
        return list(node.elements)

    if isinstance(node, DictExpr):
        out = []
        for k, v in node.pairs:
            out.extend([k, v])
        return out

    return []

def _merge_ascii(children_lines, gap=4):
    if not children_lines:
        return [], 0, 0
    heights = [len(lines) for lines, _, _ in children_lines]
    max_h = max(heights)
    padded = []
    for lines, w, m in children_lines:
        padded.append((lines + [" " * w] * (max_h - len(lines)), w, m))
    merged = []
    total_w = sum(w for _, w, _ in padded) + gap * (len(padded) - 1)
    positions = []
    x = 0
    for _, w, m in padded:
        positions.append(x + m)
        x += w + gap
    for r in range(max_h):
        line = ""
        for i, (lines, w, m) in enumerate(padded):
            line += lines[r]
            if i < len(padded) - 1:
                line += " " * gap
        merged.append(line)
    root_mid = sum(positions) // len(positions)
    return merged, total_w, root_mid

def _render_ascii(node: AstNode):
    label = f"({_expr_label(node)})"
    children = [c for c in _expr_children(node) if c is not None]
    if not children:
        return [label], len(label), len(label)//2
    rendered = [_render_ascii(c) for c in children]
    merged, m_w, m_mid = _merge_ascii(rendered)
    root_w = len(label); root_mid = root_w//2
    total_w = max(root_w, m_w)
    left_pad = m_mid - root_mid
    first = " " * max(0, left_pad) + label
    second = [" "] * total_w
    for _, _, mid in rendered:
        if 0 <= mid < total_w:
            second[mid] = "│"
    return [first, "".join(second)] + merged, total_w, m_mid

def render_ascii(ast_root: AstNode) -> str:
    if ast_root is None:
        return "<< empty AST >>"
    lines, _, _ = _render_ascii(ast_root)
    title = "Expression"
    top = " " * max(0, (len(lines[0]) - len(title)) // 2) + title
    arrow = " " * (len(lines[0]) // 2) + "↓"
    return "\n".join([top, arrow] + lines)

# ------------- Mermaid ---------------
def _sanitize(label: str) -> str:
    return label.replace('"', "'").replace("{","(").replace("}",")").replace("\n"," ")

def ast_to_mermaid_lines(node: AstNode, node_id=None, counter=None):
    if counter is None:
        counter = {"n": 0}
    if node_id is None:
        node_id = f"N{counter['n']}"; counter["n"] += 1

    label = node.__class__.__name__
    if hasattr(node, "name"):
        label += f": {node.name}"
    elif hasattr(node, "value"):
        label += f": {repr(node.value)}"
    lines = [f'{node_id}["{_sanitize(label)}"]']

    for child in _expr_children(node):
        cid = f"N{counter['n']}"; counter["n"] += 1
        lines.append(f"{node_id} --> {cid}")
        lines.extend(ast_to_mermaid_lines(child, cid, counter))
    return lines

def render_mermaid(ast_root: AstNode) -> str:
    if ast_root is None:
        return "graph TD\nEmptyAST"
    lines = ["graph TD"]
    lines.extend(ast_to_mermaid_lines(ast_root))
    return "\n".join(lines)
