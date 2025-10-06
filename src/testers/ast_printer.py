# src/testers/ast_printer.py
import argparse, json, sys
from pathlib import Path

# Parser and AST types
from ..parser.parser import Parser
from ..core.ast.ast_base import AstNode  # type: ignore

# ---- Rich (pretty console view) ----
try:
    from rich.console import Console
    from rich.tree import Tree
    from rich.panel import Panel
    RICH_OK = True
except Exception:
    # Minimal fallback if Rich is not installed (still saves JSON and shows ASCII)
    RICH_OK = False
    Console = None
    Tree = None
    Panel = None

console = Console() if RICH_OK else None


# =========================================================
# JSON helpers
# =========================================================
def to_json(node: AstNode) -> str:
    """Serialize AST node to pretty JSON (using node.to_dict())."""
    return json.dumps(node.to_dict(), indent=2, ensure_ascii=False)


# =========================================================
# Generic Rich builder (shows all fields)
# =========================================================
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
                    lst.add(f"{k}[{i}] = [cyan]{repr(it)}[/cyan]")
        else:
            tree.add(f"[italic]{k}[/italic] = [cyan]{repr(v)}[/cyan]")
    return tree


# =========================================================
# Expression tree (Rich) – operators as roots, operands as children
# =========================================================
def _label(text: str) -> str:
    return f"[bold]{text}[/bold]"

def _leaf(text: str):
    if not RICH_OK:
        raise RuntimeError("Rich is not available.")
    return Tree(text)

def _branch(name: str, child: AstNode):
    if not RICH_OK:
        raise RuntimeError("Rich is not available.")
    t = Tree(f"[dim]{name}[/dim]")
    t.add(build_expr_tree(child))
    return t

def build_expr_tree(node: AstNode):
    """Pretty expression view: binary/unary ops, grouping, calls, literals, names."""
    if not RICH_OK:
        raise RuntimeError("Rich is not available.")
    if node is None:
        return Tree("[dim]∅[/dim]")

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

    # Grouping
    if hasattr(node, "expression") or hasattr(node, "expr"):
        inside = getattr(node, "expression", None) or getattr(node, "expr", None)
        root = Tree(_label("()"))
        root.add(build_expr_tree(inside))
        return root

    # Identifier
    if hasattr(node, "name"):
        return _leaf(f"[cyan]{getattr(node, 'name')}[/cyan]")

    # Literal
    if hasattr(node, "value"):
        return _leaf(f"[magenta]{repr(getattr(node, 'value'))}[/magenta]")

    # Call
    if (hasattr(node, "callee") and hasattr(node, "args")) or (hasattr(node, "func") and hasattr(node, "args")):
        callee = getattr(node, "callee", None) or getattr(node, "func", None)
        args = list(getattr(node, "args", []))
        root = Tree(_label("call"))
        root.add(_branch("callee", callee))
        ab = Tree("[dim]args[/dim]")
        for a in args:
            ab.add(build_expr_tree(a))
        root.add(ab)
        return root

    # Index / attribute / list-like / dict-like
    if hasattr(node, "obj") and hasattr(node, "index"):
        root = Tree(_label("[]"))
        root.add(_branch("obj", node.obj))
        root.add(_branch("index", node.index))
        return root
    if hasattr(node, "obj") and hasattr(node, "attr"):
        root = Tree(_label("."))  # attribute access
        root.add(_branch("obj", node.obj))
        root.add(_leaf(f"[cyan]{getattr(node, 'attr')}[/cyan]"))
        return root
    if hasattr(node, "elements"):
        root = Tree(_label("[]" if getattr(node, "is_list", True) else "()"))
        for e in node.elements:
            root.add(build_expr_tree(e))
        return root
    if hasattr(node, "keys") and hasattr(node, "values"):
        root = Tree(_label("{}"))
        for k, v in zip(node.keys, node.values):
            pair = Tree(":")
            pair.add(build_expr_tree(k))
            pair.add(build_expr_tree(v))
            root.add(pair)
        return root

    # Fallback
    return build_rich_tree_generic(node)


# =========================================================
# ASCII "circles" diagram (no Rich required)
# =========================================================
def _expr_label(node):
    if all(hasattr(node, a) for a in ("left", "right", "op")):
        return str(getattr(node, "op"))
    if hasattr(node, "op") and hasattr(node, "operand"):
        return str(getattr(node, "op"))
    if hasattr(node, "expression") or hasattr(node, "expr"):
        return "Expr"
    if hasattr(node, "name"):
        return str(getattr(node, "name"))
    if hasattr(node, "value"):
        return repr(getattr(node, "value"))
    if (hasattr(node, "callee") and hasattr(node, "args")) or (hasattr(node, "func") and hasattr(node, "args")):
        return "call"
    if hasattr(node, "obj") and hasattr(node, "index"):
        return "[]"
    if hasattr(node, "obj") and hasattr(node, "attr"):
        return "."
    if hasattr(node, "elements"):
        return "[]" if getattr(node, "is_list", True) else "()"
    if hasattr(node, "keys") and hasattr(node, "values"):
        return "{}"
    return node.__class__.__name__

def _expr_children(node):
    if all(hasattr(node, a) for a in ("left", "right", "op")):
        return [node.left, node.right]
    if hasattr(node, "op") and hasattr(node, "operand"):
        return [node.operand]
    if hasattr(node, "expression"):
        return [node.expression]
    if hasattr(node, "expr"):
        return [node.expr]
    if hasattr(node, "callee") and hasattr(node, "args"):
        return [node.callee] + list(node.args)
    if hasattr(node, "func") and hasattr(node, "args"):
        return [node.func] + list(node.args)
    if hasattr(node, "obj") and hasattr(node, "index"):
        return [node.obj, node.index]
    if hasattr(node, "obj") and hasattr(node, "attr"):
        return [node.obj]
    if hasattr(node, "elements"):
        return list(node.elements)
    if hasattr(node, "keys") and hasattr(node, "values"):
        out = []
        for k, v in zip(node.keys, node.values):
            out.extend([k, v])
        return out
    return []

def _merge_ascii(left, right):
    w1, w2 = (len(left[0]) if left else 0), (len(right[0]) if right else 0)
    h1, h2 = len(left), len(right)
    height = max(h1, h2)
    left += [" " * w1] * (height - h1)
    right += [" " * w2] * (height - h2)
    return [l + r for l, r in zip(left, right)]

def _render_ascii(node):
    label = f"({ _expr_label(node) })"
    children = [c for c in _expr_children(node) if c is not None]

    if not children:
        line = label
        return [line], len(line), len(line) // 2

    if len(children) == 1:
        child_lines, child_w, child_m = _render_ascii(children[0])
        root_w = max(len(label), child_w)
        first = " " * child_m + label + " " * max(0, root_w - (child_m + len(label)))
        second = " " * (child_m + len(label)//2) + "│"
        pad_left = child_m + len(label)//2
        child_lines = [(" " * pad_left) + ln for ln in child_lines]
        return [first, second] + child_lines, max(root_w, len(first)), (child_m + len(label)//2)

    left_lines, lw, lm = _render_ascii(children[0])
    right_lines, rw, rm = _render_ascii(children[1])
    gap = 4
    root_center = lw + gap // 2
    root = " " * (root_center - len(label)//2) + label
    root_w = max(len(root), lw + gap + rw)
    root = root.ljust(root_w)

    # Connectors
    conn_v = [" "] * root_w
    conn_v[root_center] = "│"
    conn_d = [" "] * root_w
    # left
    li = lm
    for i in range(li + 1, root_center):
        conn_d[i] = "─"
    if li + 1 < root_center:
        conn_d[li + 1] = "┌"
    if root_center - 1 >= 0:
        conn_d[root_center - 1] = "┘"
    # right
    ri = lw + gap + rm
    for i in range(root_center + 1, ri):
        conn_d[i] = "─"
    if root_center + 1 < root_w:
        conn_d[root_center + 1] = "└"
    if ri - 1 >= 0:
        conn_d[ri - 1] = "┐"

    h = max(len(left_lines), len(right_lines))
    left_lines += [" " * lw] * (h - len(left_lines))
    right_lines += [" " * rw] * (h - len(right_lines))
    merged_children = _merge_ascii(left_lines, [" " * gap + ln for ln in right_lines])

    return [root, "".join(conn_v), "".join(conn_d)] + merged_children, root_w, root_center

def render_expression_diagram(ast_root: AstNode) -> str:
    """ASCII diagram similar to the reference image (no Rich required)."""
    if ast_root is None:
        return "<< empty AST >>"
    lines, _, _ = _render_ascii(ast_root)
    title = "Expression"
    top = " " * max(0, (len(lines[0]) - len(title)) // 2) + title
    arrow = " " * (len(lines[0]) // 2) + "↓"
    return "\n".join([top, arrow] + lines)


# =========================================================
# CLI
# =========================================================
def main():
    ap = argparse.ArgumentParser(
        description="Parse source, save AST as JSON at repo root (ast.json), and print it (Rich or ASCII diagram)."
    )
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--expr", help="Inline expression to parse")
    g.add_argument("--file", help="Path to a source file (.flpy or .py)")
    ap.add_argument("--out", help="Custom JSON output path (default is repo_root/ast.json)")
    ap.add_argument(
        "--view",
        choices=["expr", "generic", "diagram"],
        default="expr",
        help="expr: expression tree (Rich). generic: all fields (Rich). diagram: ASCII 'circles' diagram.",
    )
    args = ap.parse_args()

    # 1) Source
    if args.expr is not None:
        source = args.expr
        src_label = "[inline expr]"
    else:
        path = Path(args.file)
        source = path.read_text(encoding="utf-8")
        src_label = str(path)

    # 2) Default JSON path: always repo_root/ast.json (overwrite if exists)
    #    .../src/testers/ast_printer.py -> repo root is parents[2]
    repo_root = Path(__file__).resolve().parents[2]
    default_out = repo_root / "ast.json"
    out_path = Path(args.out) if args.out else default_out

    # 3) Parse
    parser = Parser(debug=False)
    try:
        ast_root = parser.parse(source)
    except Exception as e:
        if RICH_OK:
            console.print("\n[bold red][PARSE ERROR][/bold red]")
            for err in parser.errors:
                console.print(err.exact())
            console.print(str(e))
        else:
            print("\n[PARSE ERROR]")
            for err in parser.errors:
                print(err.exact())
            print(str(e))
        sys.exit(1)

    if ast_root is None:
        print("<< empty AST >>")
        sys.exit(0)

    # 4) Save JSON (overwrite)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(to_json(ast_root), encoding="utf-8")

    # 5) Print according to the selected view
    if args.view == "diagram":
        # Simple header + ASCII diagram
        print(f"[TransPyler] AST generated\nSource: {src_label}\nJSON:   {out_path}\n")
        print(render_expression_diagram(ast_root))
    else:
        if not RICH_OK:
            print(f"[TransPyler] AST generated\nSource: {src_label}\nJSON:   {out_path}\n")
            print("(Rich is not installed) Use --view diagram for the ASCII diagram.")
            return
        header = Panel.fit(
            f"[bold green]AST generated[/bold green]\n"
            f"Source: [cyan]{src_label}[/cyan]\n"
            f"JSON:   [cyan]{out_path}[/cyan]",
            title="[white]TransPyler[/white]",
        )
        console.print(header)
        tree = build_expr_tree(ast_root) if args.view == "expr" else build_rich_tree_generic(ast_root)
        console.print(tree)


if __name__ == "__main__":
    main()


