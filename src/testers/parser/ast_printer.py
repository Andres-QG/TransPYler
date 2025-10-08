# src/testers/ast_printer.py
import argparse, json, sys
from pathlib import Path

# Parser and AST types
from ...parser.parser import Parser
from ...core.ast.ast_statements import If, While, For, Assign, Block, Pass, Continue, Break, ExprStmt
from ...core.ast.ast_base import AstNode, Module



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
    """Etiqueta simple para el nodo en el diagrama ASCII."""
    cls_name = node.__class__.__name__

    # Manejamos bloques y declaraciones compuestas
    if cls_name == "Module":
        return "Module"
    if cls_name == "Block":
        return "Block"
    if cls_name == "If":
        return "If"
    if cls_name == "While":
        return "While"
    if cls_name == "For":
        return "For"
    if cls_name == "Assign":
        return "Assign"
    if cls_name == "Pass":
        return "Pass"
    if cls_name == "ExprStmt":
        return "ExprStmt"

    # Expresiones
    if hasattr(node, "op"):
        return str(node.op)
    if hasattr(node, "name"):
        return str(node.name)
    if hasattr(node, "value"):
        return repr(node.value)
    if hasattr(node, "callee") or hasattr(node, "func"):
        return "call"

    return cls_name
def _expr_children(node):
    # Bloques y módulos
    if hasattr(node, "body") and isinstance(node.body, list):
        return node.body
    if hasattr(node, "statements") and isinstance(node.statements, list):
        return node.statements

    # If / While / For
    if isinstance(node, If):
        children = [node.cond, node.body]
        for cond, blk in node.elifs or []:
            children.extend([cond, blk])
        if node.orelse:
            children.append(node.orelse)
        return children

    if isinstance(node, While):
        return [node.cond, node.body]

    if isinstance(node, For):
        return [node.target, node.iterable, node.body]

    # Expresiones binarias/unarias
    if all(hasattr(node, a) for a in ("left", "right", "op")):
        return [node.left, node.right]
    if hasattr(node, "op") and hasattr(node, "operand"):
        return [node.operand]

    # Expresiones agrupadas
    if hasattr(node, "expression"):
        return [node.expression]
    if hasattr(node, "expr"):
        return [node.expr]

    # Call
    if hasattr(node, "callee") and hasattr(node, "args"):
        return [node.callee] + list(node.args)
    if hasattr(node, "func") and hasattr(node, "args"):
        return [node.func] + list(node.args)

    # Index / Attribute
    if hasattr(node, "obj") and hasattr(node, "index"):
        return [node.obj, node.index]
    if hasattr(node, "obj") and hasattr(node, "attr"):
        return [node.obj]

    # List / Dict
    if hasattr(node, "elements"):
        return list(node.elements)
    if hasattr(node, "keys") and hasattr(node, "values"):
        out = []
        for k, v in zip(node.keys, node.values):
            out.extend([k, v])
        return out

    return []

def _merge_ascii_multiple(children_lines, gap=4):
    """
    Merge multiple ASCII blocks horizontally with a gap.
    children_lines: list of tuples (lines, width, mid)
    Returns: merged_lines, total_width, root_mid
    """
    if not children_lines:
        return [], 0, 0

    heights = [len(lines) for lines, _, _ in children_lines]
    max_height = max(heights)

    # Pad all children to max_height
    padded = []
    for lines, w, m in children_lines:
        padded_lines = lines + [" " * w] * (max_height - len(lines))
        padded.append((padded_lines, w, m))

    # Merge lines horizontally
    merged_lines = []
    total_width = sum(w for _, w, _ in padded) + gap * (len(padded) - 1)
    positions = []
    x = 0
    for lines, w, m in padded:
        positions.append(x + m)
        x += w + gap

    for row in range(max_height):
        line = ""
        for i, (lines, w, m) in enumerate(padded):
            line += lines[row]
            if i < len(padded) - 1:
                line += " " * gap
        merged_lines.append(line)

    root_mid = sum(positions) // len(positions)
    return merged_lines, total_width, root_mid


def _render_ascii(node: AstNode):
    label = f"({_expr_label(node)})"
    children = [c for c in _expr_children(node) if c is not None]

    if not children:
        line = label
        return [line], len(line), len(line) // 2

    # Render all children recursively
    rendered_children = [_render_ascii(c) for c in children]
    merged_children, merged_width, merged_mid = _merge_ascii_multiple(rendered_children)

    root_width = len(label)
    root_mid = root_width // 2
    total_width = max(root_width, merged_width)
    left_padding = merged_mid - root_mid
    first_line = " " * max(0, left_padding) + label
    second_line = [" "] * total_width

    # Conecta el nodo raíz con los hijos
    for child_mid in [mid for _, _, mid in rendered_children]:
        if 0 <= child_mid < total_width:
            second_line[child_mid] = "│"
    second_line = "".join(second_line)

    return [first_line, second_line] + merged_children, total_width, merged_mid


def render_expression_diagram(ast_root: AstNode) -> str:
    """ASCII diagram compatible con cualquier AST (no Rich)."""
    if ast_root is None:
        return "<< empty AST >>"
    lines, _, _ = _render_ascii(ast_root)
    title = "Expression"
    top = " " * max(0, (len(lines[0]) - len(title)) // 2) + title
    arrow = " " * (len(lines[0]) // 2) + "↓"
    return "\n".join([top, arrow] + lines)

def ast_to_mermaid(node: AstNode, node_id=None, counter=None):
    """Convierte un AST a líneas Mermaid (graph TD)"""
    if counter is None:
        counter = {"count": 0}

    if node_id is None:
        node_id = f"N{counter['count']}"
        counter['count'] += 1

    label = node.__class__.__name__
    if hasattr(node, "name"):
        label += f": {node.name}"
    elif hasattr(node, "value"):
        label += f": {repr(node.value)}"

    label = sanitize_label(label)
    lines = [f'{node_id}["{label}"]']

    for child in _expr_children(node):
        child_id = f"N{counter['count']}"
        counter['count'] += 1
        lines.append(f"{node_id} --> {child_id}")
        lines.extend(ast_to_mermaid(child, child_id, counter))

    return lines

def sanitize_label(label: str) -> str:
    """Sanitiza texto para Mermaid (quita {} y comillas problemáticas)"""
    replacements = {
        '"': "'", '{': '(', '}': ')', '\n': ' '
    }
    for k, v in replacements.items():
        label = label.replace(k, v)
    return label

def render_mermaid(ast_root: AstNode) -> str:
    """Genera el diagrama Mermaid a partir del AST"""
    if ast_root is None:
        return "graph TD\nEmptyAST"
    lines = ["graph TD"]
    lines.extend(ast_to_mermaid(ast_root))
    return "\n".join(lines)

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
        choices=["expr", "generic", "diagram", "mermaid"], 
        default="expr",
        help="expr: expression tree (Rich). generic: all fields (Rich). diagram: ASCII 'circles' diagram. mermaid: generate Mermaid diagram.",
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
    #print("DEBUG: ast_root.to_dict() output:")
    #import pprint
   # pprint.pprint(ast_root.to_dict())
    out_path.write_text(to_json(ast_root), encoding="utf-8")

   # 5) Print according to the selected view
    if args.view == "diagram":
        # Simple header + ASCII diagram
        print(f"[TransPyler] AST generated\nSource: {src_label}\nJSON:   {out_path}\n")
        print(render_expression_diagram(ast_root))
    elif args.view == "mermaid":

        mermaid_code = render_mermaid(ast_root)

        mermaid_out_path = out_path.with_suffix(".mmd")  # si JSON es ast.json -> ast.mmd
        mermaid_out_path.parent.mkdir(parents=True, exist_ok=True)
        mermaid_out_path.write_text(mermaid_code, encoding="utf-8")

        print(f"[TransPyler] AST Mermaid diagram saved to {mermaid_out_path}")

    else:
        # Rich
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


