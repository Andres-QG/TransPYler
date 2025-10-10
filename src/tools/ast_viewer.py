from __future__ import annotations
import json
from typing import List
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

# ---------- helpers (Rich) ------------

_HIDE_FIELDS = {"line", "col"}

def _fields_for_print(node: AstNode, verbose: bool) -> dict:
    """Copia de campos del nodo; oculta metadatos si verbose=False."""
    d = dict(getattr(node, "__dict__", {}))
    if not verbose:
        for k in _HIDE_FIELDS:
            d.pop(k, None)
    return d

def _label(node: AstNode, title: str, verbose: bool) -> str:
    if not verbose:
        return f"[bold]{title}[/bold]"
    line = getattr(node, "line", None)
    col = getattr(node, "col", None)
    if line is not None and col is not None:
        return f"[bold]{title}[/bold] [dim](line={line}, col={col})[/dim]"
    return f"[bold]{title}[/bold]"

def _add_list(branch: Tree, label: str, items: List[AstNode], render_fn, verbose: bool):
    lst = branch.add(f"[italic]{label}[/italic] [dim][{len(items)}][/dim]")
    for it in items:
        render_fn(it, lst, verbose)

# ---------- RENDER (Rich, genérico) ----

def build_rich_tree_generic(node: AstNode, *, label: str | None = None, verbose: bool = False):
    """
    Árbol genérico (para --view generic) con impresión limpia:
    - listas como 'elements [N]' (sin índices)
    - DictExpr como pares key/value
    - If con cond/body/elifs/orelse estructurados
    - ExprStmt colapsado a su 'value'
    """
    if not RICH_OK:
        raise RuntimeError("Rich is not available.")
    if node is None:
        return Tree("[dim]∅[/dim]")

    title = node.__class__.__name__ if label is None else f"{node.__class__.__name__} ({label})"
    root = Tree(_label(node, title, verbose))
    _render_node(node, root, verbose, is_root=True)
    return root

def _render_node(node: AstNode, parent: Tree, verbose: bool, is_root: bool = False):
    # Tipos con render específico (más limpio)
    if isinstance(node, Block):
        b = parent if is_root else parent.add(_label(node, "Block", verbose))
        _add_list(b, "statements", node.statements or [], _render_node, verbose)
        return

    if isinstance(node, ListExpr):
        b = parent if is_root else parent.add(_label(node, "ListExpr", verbose))
        _add_list(b, "elements", node.elements or [], _render_node, verbose)
        return

    if isinstance(node, TupleExpr):
        b = parent if is_root else parent.add(_label(node, "TupleExpr", verbose))
        _add_list(b, "elements", node.elements or [], _render_node, verbose)
        return

    if isinstance(node, DictExpr):
        b = parent if is_root else parent.add(_label(node, "DictExpr", verbose))
        pairs = b.add("pairs")
        for (k, v) in (node.pairs or []):
            kv = pairs.add("pair")
            kk = kv.add("key")
            _render_node(k, kk, verbose)
            vv = kv.add("value")
            _render_node(v, vv, verbose)
        return

    if isinstance(node, If):
        b = parent if is_root else parent.add(_label(node, "If", verbose))
        cond = b.add("cond")
        _render_node(node.cond, cond, verbose)

        body = b.add("body")
        _render_node(node.body, body, verbose)

        el = b.add("elifs")
        for (c, blk) in (node.elifs or []):
            e = el.add("elif")
            ec = e.add("cond")
            _render_node(c, ec, verbose)
            eb = e.add("body")
            _render_node(blk, eb, verbose)

        o = b.add("orelse")
        if node.orelse:
            _render_node(node.orelse, o, verbose)
        else:
            o.add("None")
        return

    if isinstance(node, ExprStmt):
        # Colapsamos el envoltorio: mostramos directamente el valor
        _render_node(node.value, parent, verbose, is_root=is_root)
        return

    # Fallback genérico: nodos no cubiertos arriba
    title = node.__class__.__name__
    b = parent if is_root else parent.add(_label(node, title, verbose))
    data = _fields_for_print(node, verbose)
    for k, v in list(data.items()):
        if isinstance(v, AstNode):
            br = b.add(f"[italic]{k}[/italic]")
            _render_node(v, br, verbose)
        elif isinstance(v, list):
            # Si es una lista de nodos, imprímela como bloque de hijos
            only_nodes = [x for x in v if isinstance(x, AstNode)]
            if only_nodes:
                _add_list(b, k, only_nodes, _render_node, verbose)
            # Si hay elementos no-AstNode (raro), muéstralos planos
            for x in v:
                if not isinstance(x, AstNode):
                    b.add(f"{k} = {repr(x)}")
        else:
            if k not in ("statements", "elements", "pairs"):  # ya renderizados arriba
                b.add(f"[italic]{k}[/italic] = {repr(v)}")

# ======= EXPRESSION-ONLY VIEW (Rich) =======
def build_expr_tree(node: AstNode, *, verbose: bool = False):
    """
    Árbol compacto especializado para una sola expresión (vista --view expr),
    compatible con la versión anterior. El parámetro 'verbose' se acepta pero
    no altera la salida (esta vista es minimalista por diseño).
    """
    if not RICH_OK:
        raise RuntimeError("Rich is not available.")
    if node is None:
        return Tree("[dim]∅[/dim]")

    def _label(text: str) -> str:
        return f"[bold]{text}[/bold]"

    def _branch(name: str, child: AstNode):
        t = Tree(f"[dim]{name}[/dim]")
        t.add(build_expr_tree(child, verbose=verbose))
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
            args_t.add(build_expr_tree(a, verbose=verbose))
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
            root.add(build_expr_tree(e, verbose=verbose))
        return root

    if isinstance(node, DictExpr):
        root = Tree(_label("{}"))
        for k, v in node.pairs:
            pair = Tree(":")
            pair.add(build_expr_tree(k, verbose=verbose))
            pair.add(build_expr_tree(v, verbose=verbose))
            root.add(pair)
        return root

    # Fallback: usa el generador genérico
    return build_rich_tree_generic(node, verbose=verbose)

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


