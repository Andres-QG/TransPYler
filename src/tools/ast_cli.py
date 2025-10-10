from __future__ import annotations
import argparse
import sys
from pathlib import Path

from src.parser.parser import Parser
from src.core.ast import Module, ExprStmt
from src.tools.ast_viewer import (
    ast_to_json,
    build_rich_tree_generic,
    build_expr_tree,
    render_ascii,
    render_mermaid,
)

try:
    from rich.console import Console
    from rich.panel import Panel

    RICH_OK = True
    console = Console()
except Exception:
    RICH_OK = False
    console = None
    Panel = None


def _maybe_unwrap_expr(tree):
    if (
        isinstance(tree, Module)
        and len(tree.body) == 1
        and isinstance(tree.body[0], ExprStmt)
    ):
        return tree.body[0].value
    return tree


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Parse source, save AST JSON, and print (Rich/ASCII/Mermaid)."
    )
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--expr", help="Inline expression to parse")
    g.add_argument("--file", help="Path to a source file (.py/.flpy)")
    ap.add_argument("--out", help="JSON output path (default: repo_root/ast.json)")
    ap.add_argument(
        "--view", choices=["expr", "generic", "diagram", "mermaid"], default="expr"
    )
    ap.add_argument(
        "--unwrap-expr",
        action="store_true",
        help="Return bare expr when input is a single expression",
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Show internal fields (line/col) in the printed tree",
    )
    return ap.parse_args()


def _read_source(args: argparse.Namespace) -> tuple[str, str]:
    """Devuelve (source_text, src_label)."""
    if args.expr is not None:
        return args.expr, "[inline expr]"
    try:
        path = Path(args.file)
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[TransPyler] Error reading file: {args.file}\n{e}", file=sys.stderr)
        sys.exit(2)
    return text, str(path)


def _default_json_path() -> Path:
    return Path(__file__).resolve().parents[2] / "ast.json"


def _print_header(src_label: str, out_path: Path):
    if not RICH_OK:
        print(f"[TransPyler] AST generated\nSource: {src_label}\nJSON:   {out_path}\n")
        return
    header = Panel.fit(
        f"[bold green]AST generated[/bold green]\n"
        f"Source: {src_label}\n"
        f"JSON:   {out_path}",
        title="[white]TransPyler[/white]",
    )
    console.print(header)


def main():
    args = _parse_args()

    # 1) Source
    source, src_label = _read_source(args)

    # 2) JSON output path
    out_path = Path(args.out) if args.out else _default_json_path()

    # 3) Parse
    parser = Parser(debug=False)
    ast_root = parser.parse(source)

    if parser.errors:
        msg = "\n".join(e.exact() for e in parser.errors)
        if RICH_OK:
            console.print(f"\n[bold red][PARSE ERROR][/bold red]\n{msg}")
        else:
            print("\n[PARSE ERROR]\n" + msg)
        sys.exit(1)

    # 4) Unwrap expr:
    if args.expr is not None or args.unwrap_expr:
        ast_root = _maybe_unwrap_expr(ast_root)

    # 5) Save JSON
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(ast_to_json(ast_root), encoding="utf-8")

    # 6) Print selected view
    if args.view == "diagram":
        _print_header(src_label, out_path)
        print(render_ascii(ast_root))
        return

    if args.view == "mermaid":
        mmd = out_path.with_suffix(".mmd")
        mmd.write_text(render_mermaid(ast_root), encoding="utf-8")
        print(f"[TransPyler] AST Mermaid diagram saved to {mmd}")
        return

    # Rich: expr / generic
    if not RICH_OK:
        _print_header(src_label, out_path)
        print("(Rich not installed) Use --view diagram or --view mermaid.")
        return

    _print_header(src_label, out_path)
    tree = (
        build_expr_tree(ast_root, verbose=args.verbose)
        if args.view == "expr"
        else build_rich_tree_generic(ast_root, verbose=args.verbose)
    )
    console.print(tree)


if __name__ == "__main__":
    main()
