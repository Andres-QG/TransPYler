try:
    from rich.console import Console
    from rich.tree import Tree
    console = Console()
    tree = Tree("[bold green]Root[/bold green]")
    tree.add("[cyan]Child 1[/cyan]")
    tree.add("[magenta]Child 2[/magenta]")
    console.print(tree)
    print("✅ Rich está funcionando")
except Exception as e:
    print("❌ Rich NO está funcionando:", e)