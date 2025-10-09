# src/tools/ast_cli.py
from __future__ import annotations
import argparse, sys
from pathlib import Path
from src.parser.parser import Parser
from src.core.ast import Module, ExprStmt
from src.tools.ast_viewer import (
    ast_to_json, build_rich_tree_generic, build_expr_tree,
    render_ascii, render_mermaid
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
    if isinstance(tree, Module) and len(tree.body) == 1 and isinstance(tree.body[0], ExprStmt):
        return tree.body[0].value
    return tree

def main():
    ap = argparse.ArgumentParser(
        description="Parse source, save AST JSON, and print (Rich/ASCII/Mermaid)."
    )
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--expr", help="Inline expression to parse")
    g.add_argument("--file", help="Path to a source file (.py/.flpy)")
    ap.add_argument("--out", help="JSON output path (default: repo_root/ast.json)")
    ap.add_argument("--view", choices=["expr","generic","diagram","mermaid"], default="expr")
    ap.add_argument("--unwrap-expr", action="store_true",
                    help="Return bare expr when input is a single expression")
    args = ap.parse_args()

    # 1) Source
    if args.expr is not None:
        source = args.expr
        src_label = "[inline expr]"
    else:
        path = Path(args.file)
        source = path.read_text(encoding="utf-8")
        src_label = str(path)

    # 2) Default JSON output
    repo_root = Path(__file__).resolve().parents[2]  # .../src/tools/ -> repo root
    out_path = Path(args.out) if args.out else (repo_root / "ast.json")

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

    if args.unwrap_expr:
        ast_root = _maybe_unwrap_expr(ast_root)

    # 4) Save JSON
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(ast_to_json(ast_root), encoding="utf-8")

    # 5) Print selected view
    if args.view == "diagram":
        print(f"[TransPyler] AST generated\nSource: {src_label}\nJSON:   {out_path}\n")
        print(render_ascii(ast_root))
    elif args.view == "mermaid":
        mmd = out_path.with_suffix(".mmd")
        mmd.write_text(render_mermaid(ast_root), encoding="utf-8")
        print(f"[TransPyler] AST Mermaid diagram saved to {mmd}")
    else:
        if not RICH_OK:
            print(f"[TransPyler] AST generated\nSource: {src_label}\nJSON:   {out_path}\n")
            print("(Rich not installed) Use --view diagram or --view mermaid.")
            return
        header = Panel.fit(
            f"[bold green]AST generated[/bold green]\n"
            f"Source: {src_label}\n"
            f"JSON:   {out_path}",
            title="[white]TransPyler[/white]",
        )
        console.print(header)
        tree = build_expr_tree(ast_root) if args.view == "expr" else build_rich_tree_generic(ast_root)
        console.print(tree)

if __name__ == "__main__":
    main()
