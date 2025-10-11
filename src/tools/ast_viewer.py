from __future__ import annotations
import json
from typing import Iterable, List, TYPE_CHECKING, Any

from src.core.ast.ast_base import AstNode
from src.core.ast import (
    ExprStmt,
    If,
    While,
    For,
    Block,
    TupleExpr,
    ListExpr,
    DictExpr,
    Attribute,
    Subscript,
    FunctionDef,
    ClassDef,
    Assign,
    Return,
)


if TYPE_CHECKING:
    from rich.tree import Tree as RichTree
else:
    RichTree = Any

NODE_STYLE = "bold cyan"
FIELD_STYLE = "italic yellow"
SECTION_STYLE = "dim green"
VALUE_STYLE = "magenta"
PLAIN_DIM = "dim"


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
    data = dict(getattr(node, "__dict__", {}))
    if not verbose:
        for field_key in _HIDE_FIELDS:
            data.pop(field_key, None)
    return data


def _label(node: AstNode, title: str, verbose: bool) -> str:
    if not verbose:
        return f"[{NODE_STYLE}]{title}[/]"
    line = getattr(node, "line", None)
    col = getattr(node, "col", None)
    meta = (
        f" [dim](line={line}, col={col})[/dim]"
        if line is not None and col is not None
        else ""
    )
    return f"[{NODE_STYLE}]{title}[/]{meta}"


def _add_list(
    branch: RichTree, label: str, items: Iterable[AstNode], render_fn, verbose: bool
):
    items = list(items)
    lst = branch.add(f"[{SECTION_STYLE}]{label}[/] [dim][{len(items)}][/dim]")
    for it in items:
        render_fn(it, lst, verbose)


# TODO (Any): This one is never used, should it be removed?
def _render_elements_node(
    node: AstNode,
    parent: RichTree,
    verbose: bool,
    name: str,
    elements: List[AstNode],
    is_root: bool,
):
    b = parent if is_root else parent.add(_label(node, name, verbose))
    _add_list(b, "elements", elements or [], _render_node, verbose)


# ---------- RENDER (Rich, genérico) ----


def build_rich_tree_generic(
    node: AstNode, *, label: str | None = None, verbose: bool = False
):
    if not RICH_OK:
        raise RuntimeError("Rich is not available.")
    if node is None:
        return Tree("[dim]∅[/dim]")

    title = (
        node.__class__.__name__
        if label is None
        else f"{node.__class__.__name__} ({label})"
    )
    root = Tree(_label(node, title, verbose))
    _render_node(node, root, verbose, is_root=True)
    return root


def _render_node(node: AstNode, parent: RichTree, verbose: bool, is_root: bool = False):
    if isinstance(node, ExprStmt):
        _render_node(node.value, parent, verbose, is_root=is_root)
        return

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
        pairs = b.add(f"[{SECTION_STYLE}]pairs[/]")
        for k, v in node.pairs or []:
            kv = pairs.add(f"[{SECTION_STYLE}]pair[/]")
            _render_node(k, kv.add(f"[{FIELD_STYLE}]key[/]"), verbose)
            _render_node(v, kv.add(f"[{FIELD_STYLE}]value[/]"), verbose)
        return

    if isinstance(node, If):
        b = parent if is_root else parent.add(_label(node, "If", verbose))
        _render_node(node.cond, b.add("cond"), verbose)
        _render_node(node.body, b.add("body"), verbose)

        el = b.add("elifs")
        for c, blk in node.elifs or []:
            e = el.add("elif")
            _render_node(c, e.add("cond"), verbose)
            _render_node(blk, e.add("body"), verbose)

        o = b.add("orelse")
        _render_node(node.orelse, o, verbose) if node.orelse else o.add("None")
        return

    b = (
        parent
        if is_root
        else parent.add(_label(node, node.__class__.__name__, verbose))
    )
    data = _fields_for_print(node, verbose)

    for k, v in data.items():
        if isinstance(v, AstNode):
            _render_node(v, b.add(f"[{FIELD_STYLE}]{k}[/]"), verbose)

        elif isinstance(v, list):
            only_nodes = [x for x in v if isinstance(x, AstNode)]
            if only_nodes:
                _add_list(b, k, only_nodes, _render_node, verbose)
            else:
                b.add(f"[{FIELD_STYLE}]{k}[/] = {repr(v)}")

        else:
            if k not in ("statements", "elements", "pairs"):
                b.add(f"[{FIELD_STYLE}]{k}[/] = [{VALUE_STYLE}]{repr(v)}[/]")


# ======= EXPRESSION-ONLY VIEW (Rich) =======
def build_expr_tree(node: AstNode, *, verbose: bool = False):
    if not RICH_OK:
        raise RuntimeError("Rich is not available.")
    if node is None:
        return Tree("[dim]∅[/dim]")

    def _lbl(text: str) -> str:
        return f"[bold]{text}[/bold]"

    def _branch(name: str, child: AstNode):
        t = Tree(f"[dim]{name}[/dim]")
        t.add(build_expr_tree(child, verbose=verbose))
        return t

    # Binary
    if all(hasattr(node, a) for a in ("left", "right", "op")):
        root = Tree(_lbl(str(getattr(node, "op"))))
        root.add(_branch("left", node.left))
        root.add(_branch("right", node.right))
        return root

    # Unary
    if hasattr(node, "op") and hasattr(node, "operand"):
        root = Tree(_lbl(str(getattr(node, "op"))))
        root.add(_branch("operand", node.operand))
        return root

    # Identifier / Literal
    if hasattr(node, "name"):
        return Tree(f"[cyan]{getattr(node, 'name')}[/cyan]")
    if hasattr(node, "value"):
        return Tree(f"[magenta]{repr(getattr(node, 'value'))}[/magenta]")

    # Call
    if hasattr(node, "callee") and hasattr(node, "args"):
        root = Tree(_lbl("call"))
        root.add(_branch("callee", node.callee))
        args_t = Tree("[dim]args[/dim]")
        for a in node.args:
            args_t.add(build_expr_tree(a, verbose=verbose))
        root.add(args_t)
        return root

    # Subscript / Attribute / Collections
    if isinstance(node, Subscript):
        root = Tree(_lbl("[]"))
        root.add(_branch("value", node.value))
        root.add(_branch("index", node.index))
        return root

    if isinstance(node, Attribute):
        root = Tree(_lbl("."))  # attribute access
        root.add(_branch("value", node.value))
        root.add(Tree(f"[cyan]{node.attr}[/cyan]"))
        return root

    if isinstance(node, (TupleExpr, ListExpr)):
        root = Tree(_lbl("()" if isinstance(node, TupleExpr) else "[]"))
        for e in node.elements:
            root.add(build_expr_tree(e, verbose=verbose))
        return root

    if isinstance(node, DictExpr):
        root = Tree(_lbl("{}"))
        for k, v in node.pairs:
            pair = Tree(":")
            pair.add(build_expr_tree(k, verbose=verbose))
            pair.add(build_expr_tree(v, verbose=verbose))
            root.add(pair)
        return root

    return build_rich_tree_generic(node, verbose=verbose)


# --------------- ASCII ----------------
def _expr_label(node: AstNode) -> str:
    cls = node.__class__.__name__
    if cls in {
        "Module",
        "Block",
        "If",
        "While",
        "For",
        "Assign",
        "Pass",
        "Continue",
        "Break",
        "ExprStmt",
    }:
        return cls
    if hasattr(node, "op"):
        return str(node.op)
    if hasattr(node, "name"):
        return str(node.name)
    if hasattr(node, "value"):
        return repr(node.value)
    if hasattr(node, "callee"):
        return "call"
    return cls


def _expr_children(node: AstNode):
    # Block
    if isinstance(node, ExprStmt):
        return [node.value]

    # FunctionDef y ClassDef
    if isinstance(node, FunctionDef):
        children = []
        children.extend(node.params)
        if node.body:
            children.append(node.body)
        return children

    if isinstance(node, ClassDef):
        if node.body:
            return [node.body]
        return []

    # Return statement
    if isinstance(node, Return):
        if node.value:
            return [node.value]
        return []

    # Assign statement
    if isinstance(node, Assign):
        children = []
        if node.target:
            children.append(node.target)
        if node.value:
            children.append(node.value)
        return children

    if hasattr(node, "body") and isinstance(node.body, list):
        return node.body
    if hasattr(node, "statements") and isinstance(node.statements, list):
        return node.statements

    if isinstance(node, If):
        out = [node.cond, node.body]
        for cond, blk in node.elifs or []:
            out.extend([cond, blk])
        if node.orelse:
            out.append(node.orelse)
        return out
    if isinstance(node, While):
        return [node.cond, node.body]
    if isinstance(node, For):
        return [node.target, node.iterable, node.body]

    if all(hasattr(node, a) for a in ("left", "right", "op")):
        return [node.left, node.right]
    if hasattr(node, "op") and hasattr(node, "operand"):
        return [node.operand]
    if hasattr(node, "callee") and hasattr(node, "args"):
        return [node.callee] + list(node.args)
    if isinstance(node, Subscript):
        return [node.value, node.index]
    if isinstance(node, Attribute):
        return [node.value]
    if isinstance(node, (TupleExpr, ListExpr)):
        return list(node.elements)
    if isinstance(node, DictExpr):
        out = []
        for k, v in node.pairs:
            out.extend([k, v])
        return out
    return []


def _merge_ascii(children_lines, gap=4):

    if not children_lines:
        return [], 0, 0, []

    heights = [len(lines) for lines, _, _ in children_lines]
    max_h = max(heights)

    padded = []
    for lines, w, m in children_lines:
        pad = lines + [" " * w] * (max_h - len(lines))
        padded.append((pad, w, m))

    merged: List[str] = []
    total_w = sum(w for _, w, _ in padded) + gap * (len(padded) - 1)

    child_mids: List[int] = []
    x = 0
    for _, w, m in padded:
        child_mids.append(x + m)
        x += w + gap

    for r in range(max_h):
        line = ""
        for i, (lines, w, _) in enumerate(padded):
            line += lines[r]
            if i < len(padded) - 1:
                line += " " * gap
        merged.append(line)

    block_mid = sum(child_mids) // len(child_mids)
    return merged, total_w, block_mid, child_mids


def _render_ascii(node: AstNode):

    label = f"({_expr_label(node)})"
    children = [c for c in _expr_children(node) if c is not None]

    if not children:
        return [label], len(label), len(label) // 2

    rendered = [_render_ascii(c) for c in children]
    merged, block_w, block_mid, child_mids = _merge_ascii(rendered)

    root_w = len(label)
    root_mid = root_w // 2
    left_pad = max(0, block_mid - root_mid)

    first_line = " " * left_pad + label
    if len(first_line) < block_w:
        first_line += " " * (block_w - len(first_line))

    connector_vert = [" "] * block_w
    if 0 <= block_mid < block_w:
        connector_vert[block_mid] = "│"
    connector_vert = "".join(connector_vert)

    connector_h = [" "] * block_w
    if child_mids:
        lo, hi = min(child_mids), max(child_mids)
        for x in range(lo, hi + 1):
            connector_h[x] = "─"
        for mid in child_mids:
            connector_h[mid] = "┬"
        connector_h[block_mid] = "┼" if lo <= block_mid <= hi else "┴"
    connector_h = "".join(connector_h)

    lines = [first_line, connector_vert, connector_h] + merged
    return lines, block_w, block_mid


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
    return (
        label.replace('"', "'").replace("{", "(").replace("}", ")").replace("\n", " ")
    )


def ast_to_mermaid_lines(node: AstNode, node_id=None, counter=None):
    if counter is None:
        counter = {"n": 0}
    if node_id is None:
        node_id = f"N{counter['n']}"
        counter["n"] += 1

    label = node.__class__.__name__
    if hasattr(node, "name"):
        label += f": {node.name}"
    elif hasattr(node, "value") and not hasattr(node, "callee"):
        val_str = repr(node.value)
        # Truncate long strings
        if len(val_str) > 30:
            val_str = val_str[:27] + "..."
        label += f": {val_str}"
    elif hasattr(node, "op"):
        label += f" ({node.op})"

    lines = [f'{node_id}["{_sanitize(label)}"]']

    # Process children
    children = _expr_children(node)
    for child in children:
        if child is None:
            continue
        cid = f"N{counter['n']}"
        counter["n"] += 1
        lines.append(f"{node_id} --> {cid}")
        lines.extend(ast_to_mermaid_lines(child, cid, counter))

    return lines


def render_mermaid(ast_root: AstNode) -> str:
    if ast_root is None:
        return "graph TD\nEmptyAST"
    lines = ["graph TD"]
    lines.extend(ast_to_mermaid_lines(ast_root))
    return "\n".join(lines)
