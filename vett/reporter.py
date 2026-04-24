from collections.abc import Iterable, Mapping
from datetime import datetime
from pathlib import Path
from typing import Any, Tuple

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

console = Console()


def _normalize_suggestions(raw: Any) -> Iterable[Tuple[str, str]]:
    """Turn model output into (title, detail) pairs without assuming dict shape."""
    if not isinstance(raw, list):
        return
    for item in raw:
        if isinstance(item, Mapping):
            title = str(item.get("title") or "Suggestion").strip() or "Suggestion"
            detail = str(item.get("detail") or "").strip()
            yield title, detail
        elif isinstance(item, str) and item.strip():
            yield "Suggestion", item.strip()


def get_score_color(score):
    if score >= 80:
        return "bright_green"
    if score >= 60:
        return "yellow"
    if score >= 40:
        return "orange3"
    return "bright_red"


def get_grade_emoji(grade):
    return {"A": "🏆", "B": "👍", "C": "⚠️", "D": "🔴", "F": "💀"}.get(grade, "❓")


def status_and_color(count, bad_color="red", ok_label="✅", bad_label="🔴"):
    return (ok_label, "green") if count == 0 else (bad_label, bad_color)


def print_report(root_path, ai_result, security, todos, large, complex_fns, files):
    from vett.utils import has_readme

    score = ai_result.get("overall_score", 0)
    grade = ai_result.get("grade", "?")
    color = get_score_color(score)
    emoji = get_grade_emoji(grade)

    console.print()
    console.print(Rule("[bold cyan]🩺 Vett — Codebase Health Report[/bold cyan]"))
    console.print()

    console.print(
        Panel(
            f"[bold]{ai_result.get('project_summary', 'N/A')}[/bold]",
            title="[cyan]Project Summary[/cyan]",
            border_style="cyan",
        )
    )
    console.print()

    score_text = Text()
    score_text.append(f"  {emoji} Grade: {grade}   ", style=f"bold {color}")
    score_text.append(f"Score: {score}/100   ", style=f"bold {color}")
    score_text.append(
        f"Tech Debt: {ai_result.get('estimated_tech_debt', 'Unknown')}  ", style="bold white"
    )
    console.print(Panel(score_text, title="[cyan]Overall Health[/cyan]", border_style=color))
    console.print()

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Status", justify="center")
    table.add_row("Files scanned", f"[cyan]{len(files)}[/cyan]", "✅")

    sec_icon, sec_color = status_and_color(len(security))
    table.add_row("Security issues", f"[{sec_color}]{len(security)}[/{sec_color}]", sec_icon)

    todo_icon, todo_color = status_and_color(
        len(todos), bad_color="yellow", bad_label="⚠️"
    )
    table.add_row("TODO / FIXME", f"[{todo_color}]{len(todos)}[/{todo_color}]", todo_icon)

    large_icon, large_color = status_and_color(
        len(large), bad_color="yellow", bad_label="⚠️"
    )
    table.add_row(
        "Large files (>300 lines)", f"[{large_color}]{len(large)}[/{large_color}]", large_icon
    )
    table.add_row(
        "Complex functions (>50 lines)",
        f"[{'yellow' if complex_fns else 'green'}]{len(complex_fns)}[/{'yellow' if complex_fns else 'green'}]",
        "⚠️" if complex_fns else "✅",
    )
    readme_ok = has_readme(root_path)
    table.add_row("README present", "yes" if readme_ok else "no", "✅" if readme_ok else "⚠️")
    console.print(table)
    console.print()

    if security:
        console.print(Rule("[bold red]🔐 Security Issues[/bold red]"))
        for s in security[:10]:
            sev_color = "bright_red" if s["severity"] == "CRITICAL" else "yellow"
            console.print(
                f"  [{sev_color}]{s['severity']}[/{sev_color}] {s['file']}:{s['line']} — {s['issue']}"
            )
            console.print(f"    [dim]{s['snippet']}[/dim]")
        console.print()

    if todos:
        console.print(Rule("[bold yellow]📝 TODO / FIXME / HACK[/bold yellow]"))
        for t in todos[:15]:
            console.print(f"  [yellow]{t['issue']}[/yellow] {t['file']}:{t['line']}")
            console.print(f"    [dim]{t['snippet']}[/dim]")
        if len(todos) > 15:
            console.print(f"  [dim]... and {len(todos) - 15} more[/dim]")
        console.print()

    if large:
        console.print(Rule("[bold yellow]📦 Large Files[/bold yellow]"))
        for f in large:
            console.print(f"  [yellow]{f['file']}[/yellow] — {f['lines']} lines ({f['language']})")
        console.print()

    if complex_fns:
        console.print(Rule("[bold orange3]🔀 Complex Functions[/bold orange3]"))
        for c in complex_fns:
            reason = c.get("reason", "Too long")
            nesting = c.get("max_nesting", "?")
            console.print(
                f"  [orange3]{c['function']}()[/orange3] in {c['file']}:{c['line']} "
                f"— {c['length']} lines, nesting depth {nesting} ({reason})"
            )
        console.print()

    if ai_result.get("strengths"):
        console.print(Rule("[bold green]✅ Strengths[/bold green]"))
        for s in ai_result["strengths"]:
            console.print(f"  [green]•[/green] {s}")
        console.print()

    if ai_result.get("critical_issues"):
        console.print(Rule("[bold red]❗ Critical Issues[/bold red]"))
        for i in ai_result["critical_issues"]:
            console.print(f"  [red]•[/red] {i}")
        console.print()

    suggestions = list(_normalize_suggestions(ai_result.get("suggestions")))
    if suggestions:
        console.print(Rule("[bold yellow]💡 AI Suggestions[/bold yellow]"))
        for i, (title, detail) in enumerate(suggestions, 1):
            console.print(f"  [yellow]{i}.[/yellow] [bold]{title}[/bold]")
            if detail:
                console.print(f"     [dim]{detail}[/dim]")
            console.print()

    roast = ai_result.get("one_line_roast", "")
    if roast:
        console.print(
            Panel(
                f"[italic]{roast}[/italic]",
                title="[magenta]🎤 Vett's Take[/magenta]",
                border_style="magenta",
            )
        )
        console.print()

    footer_lines = [f"[dim]Report saved →[/dim] [cyan]vett_report.md[/cyan]"]
    if security:
        footer_lines.append(f"[red]Fix {len(security)} security issue(s) first[/red]")
    elif score >= 80:
        footer_lines.append("[green]Looking clean! Keep it up.[/green]")

    console.print(Panel("\n".join(footer_lines), border_style="dim"))
    console.print()


def save_markdown_report(root_path, ai_result, security, todos, large, complex_fns, files):
    from vett.utils import has_readme

    score = ai_result.get("overall_score", 0)
    grade = ai_result.get("grade", "?")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# 🩺 Vett Health Report",
        "",
        f"**Scanned:** `{root_path}`  ",
        f"**Date:** {now}  ",
        f"**Grade:** {grade} | **Score:** {score}/100 | **Tech Debt:** {ai_result.get('estimated_tech_debt', 'Unknown')}",
        "",
        "---",
        "",
        "## 📋 Project Summary",
        "",
        f"{ai_result.get('project_summary', 'N/A')}",
        "",
        "## 📊 Stats",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Files scanned | {len(files)} |",
        f"| Security issues | {len(security)} |",
        f"| TODO/FIXME | {len(todos)} |",
        f"| Large files | {len(large)} |",
        f"| Complex functions | {len(complex_fns)} |",
        f"| README present | {'yes' if has_readme(root_path) else 'no'} |",
        "",
    ]

    if security:
        lines += ["## 🔐 Security Issues", ""]
        for s in security:
            lines.append(f"- **{s['severity']}** `{s['file']}:{s['line']}` — {s['issue']}")
        lines.append("")

    if todos:
        lines += ["## 📝 TODO / FIXME / HACK", ""]
        for t in todos:
            lines.append(f"- **{t['issue']}** `{t['file']}:{t['line']}` — `{t['snippet']}`")
        lines.append("")

    if ai_result.get("strengths"):
        lines += ["## ✅ Strengths", ""]
        for s in ai_result["strengths"]:
            lines.append(f"- {s}")
        lines.append("")

    if ai_result.get("critical_issues"):
        lines += ["## ❗ Critical Issues", ""]
        for i in ai_result["critical_issues"]:
            lines.append(f"- {i}")
        lines.append("")

    suggestions = list(_normalize_suggestions(ai_result.get("suggestions")))
    if suggestions:
        lines += ["## 💡 AI Suggestions", ""]
        for title, detail in suggestions:
            lines.append(f"### {title}")
            if detail:
                lines.append(detail)
            lines.append("")

    if ai_result.get("one_line_roast"):
        lines += ["---", "", f"> 🎤 *{ai_result['one_line_roast']}*", ""]

    report_path = Path(root_path) / "vett_report.md"
    # Force UTF-8 so emoji and symbols work on Windows default cp1252 terminals.
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return str(report_path)
