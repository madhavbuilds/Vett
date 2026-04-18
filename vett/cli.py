import os
import platform
import sys
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

ENV_KEY_BY_PROVIDER = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


def choose_ai_mode() -> str:
    """Return 'ai' or 'no_ai' based on an interactive prompt."""
    try:
        import questionary
    except Exception:
        return "ai" if click.confirm("Use AI analysis?", default=False) else "no_ai"

    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return "ai" if click.confirm("Use AI analysis?", default=False) else "no_ai"

    choice = questionary.select(
        "No API key found. Choose scan mode:",
        choices=[
            questionary.Choice("Use AI analysis (enter API key)", value="ai"),
            questionary.Choice("Continue without AI", value="no_ai"),
        ],
        default="no_ai",
        qmark="?",
    ).ask()
    return choice or "no_ai"


def resolve_api_key(provider: str, explicit_api_key: Optional[str]) -> Optional[str]:
    if explicit_api_key:
        return explicit_api_key
    env_name = ENV_KEY_BY_PROVIDER.get(provider, "ANTHROPIC_API_KEY")
    return os.getenv(env_name)


@click.group(context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 100})
def main():
    """🩺 Vett — AI-powered codebase health scanner.

    Scan projects for common security issues, code complexity, TODO debt,
    and optionally run AI analysis.

    Common commands:
      vett scan . --no-ai
      vett scan . --api-key YOUR_KEY
      vett version
    """
    pass


@main.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option(
    "--api-key",
    help="API key for selected provider. If omitted, provider-specific env var is used.",
)
@click.option(
    "--provider",
    type=click.Choice(["anthropic", "openai", "gemini", "openrouter"], case_sensitive=False),
    default="anthropic",
    show_default=True,
    help="AI provider to use.",
)
@click.option("--model", default=None, help="Model name override for selected provider.")
@click.option(
    "--max-files",
    default=50,
    show_default=True,
    help="Maximum number of source files to scan.",
)
@click.option("--no-ai", is_flag=True, help="Skip AI analysis and run local checks only.")
def scan(path, api_key, provider, model, max_files, no_ai):
    """Scan a codebase and generate a health report.

    \b
    Examples:
      vett scan .
      vett scan ./my-project
      vett scan ./my-project --no-ai
      vett scan . --provider openrouter
    """
    from vett.reporter import print_report, save_markdown_report
    from vett.scanner import scan_complexity, scan_large_files, scan_security, scan_todos
    from vett.utils import collect_files

    console.print()
    console.print("[bold cyan]🩺 Vett[/bold cyan] [dim]— AI Codebase Health Scanner[/dim]")
    console.print()

    provider = provider.lower()
    api_key = resolve_api_key(provider, api_key)

    if not no_ai and not api_key:
        env_name = ENV_KEY_BY_PROVIDER.get(provider, "API_KEY")
        console.print(f"[yellow]⚠️  No API key found for provider '{provider}'.[/yellow]")
        console.print(f"[dim]Set {env_name} or pass --api-key.[/dim]")
        mode = choose_ai_mode()
        if mode == "ai":
            api_key = click.prompt(f"Enter {provider} API key", hide_input=True).strip()
            if not api_key:
                console.print("[red]API key cannot be empty.[/red]")
                sys.exit(1)
        else:
            no_ai = True
            console.print("[cyan]Continuing in no-AI mode.[/cyan]")
        console.print()

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
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
            progress.update(task, description=f"[cyan]Running AI analysis ({provider})...[/cyan]")
            from vett.analyzer import analyze_with_ai

            ai_result = analyze_with_ai(
                files,
                security,
                todos,
                large,
                complex_fns,
                provider=provider,
                api_key=api_key,
                model=model,
            )
        else:
            ai_result = {
                "project_summary": "AI analysis skipped (--no-ai flag used).",
                "overall_score": 0,
                "grade": "N/A",
                "strengths": [],
                "critical_issues": [],
                "suggestions": [],
                "estimated_tech_debt": "Unknown",
                "one_line_roast": "",
            }

        progress.update(task, description="Generating report...")
        save_markdown_report(path, ai_result, security, todos, large, complex_fns, files)

    print_report(path, ai_result, security, todos, large, complex_fns, files)


@main.command()
@click.option("--short", is_flag=True, help="Print version only.")
def version(short):
    """Show Vett version and environment info."""
    from vett import __version__

    if short:
        console.print(__version__)
        return

    table = Table(show_header=False)
    table.add_row("Version", f"v{__version__}")
    table.add_row("Python", platform.python_version())
    table.add_row("Platform", platform.platform())
    table.add_row("Providers", "anthropic, openai, gemini, openrouter")
    table.add_row("Command", "vett scan . --provider openai")
    console.print("[bold cyan]Vett[/bold cyan] [dim]version info[/dim]")
    console.print(table)


if __name__ == "__main__":
    main()
