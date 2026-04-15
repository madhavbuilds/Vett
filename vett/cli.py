import sys
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@click.group()
def main():
    """🩺 Vett — AI-powered codebase health scanner."""
    pass

@main.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--api-key", envvar="ANTHROPIC_API_KEY", help="Anthropic API key")
@click.option("--max-files", default=50, help="Max files to scan (default: 50)")
@click.option("--no-ai", is_flag=True, help="Skip AI analysis (local checks only)")
def scan(path, api_key, max_files, no_ai):
    """Scan a codebase and generate a health report.

    \b
    Examples:
      vett scan .
      vett scan ./my-project
      vett scan ./my-project --no-ai
    """
    from vett.utils import collect_files
    from vett.scanner import scan_security, scan_todos, scan_large_files, scan_complexity
    from vett.reporter import print_report, save_markdown_report

    console.print()
    console.print("[bold cyan]🩺 Vett[/bold cyan] [dim]— AI Codebase Health Scanner[/dim]")
    console.print()

    if not no_ai and not api_key:
        console.print("[yellow]⚠️  No API key found.[/yellow]")
        console.print("  Set it: [cyan]export ANTHROPIC_API_KEY=your-key[/cyan]")
        console.print("  Or run without AI: [cyan]vett scan . --no-ai[/cyan]")
        console.print()
        sys.exit(1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Collecting files...", total=None)
        files = collect_files(path, max_files=max_files)
        progress.update(task, description=f"Found [bold]{len(files)}[/bold] source files")

        if not files:
            console.print("[red]No source files found.[/red]")
            sys.exit(1)

        progress.update(task, description="Running security scan...")
        security = scan_security(files)

        progress.update(task, description="Scanning TODO/FIXME...")
        todos = scan_todos(files)

        progress.update(task, description="Checking file sizes...")
        large = scan_large_files(files)

        progress.update(task, description="Analyzing complexity...")
        complex_fns = scan_complexity(files)

        if not no_ai:
            progress.update(task, description="[cyan]Asking Claude for AI analysis...[/cyan]")
            from vett.analyzer import analyze_with_claude
            ai_result = analyze_with_claude(files, security, todos, large, complex_fns, api_key)
        else:
            ai_result = {
                "project_summary": "AI analysis skipped (--no-ai flag used).",
                "overall_score": 0, "grade": "N/A",
                "strengths": [], "critical_issues": [],
                "suggestions": [], "estimated_tech_debt": "Unknown",
                "one_line_roast": "",
            }

        progress.update(task, description="Generating report...")
        save_markdown_report(path, ai_result, security, todos, large, complex_fns, files)

    print_report(path, ai_result, security, todos, large, complex_fns, files)

@main.command()
def version():
    """Show Vett version."""
    from vett import __version__
    console.print(f"Vett v{__version__}")

if __name__ == "__main__":
    main()
