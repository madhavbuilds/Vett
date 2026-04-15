from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich import box

console = Console()

def get_score_color(score):
    if score >= 80: return "bright_green"
    if score >= 60: return "yellow"
    if score >= 40: return "orange3"
    return "bright_red"

def get_grade_emoji(grade):
    return {"A": "🏆", "B": "👍", "C": "⚠️", "D": "🔴", "F": "💀"}.get(grade, "❓")

def print_report(root_path, ai_result, security, todos, large, complex_fns, files):
    score = ai_result.get("overall_score", 0)
    grade = ai_result.get("grade", "?")
    color = get_score_color(score)
    emoji = get_grade_emoji(grade)

    console.print()
    console.print(Rule("[bold cyan]🩺 Vett — Codebase Health Report[/bold cyan]"))
    console.print()

    console.print(Panel(
        f"[bold]{ai_result.get('project_summary', 'N/A')}[/bold]",
        title="[cyan]Project Summary[/cyan]", border_style="cyan",
    ))
    console.print()

    score_text = Text()
    score_text.append(f"  {emoji} Grade: {grade}   ", style=f"bold {color}")
    score_text.append(f"Score: {score}/100   ", style=f"bold {color}")
    score_text.append(f"Tech Debt: {ai_result.get('estimated_tech_debt', 'Unknown')}  ", style="bold white")
    console.print(Panel(score_text, title="[cyan]Overall Health[/cyan]", border_style=color))
    console.print()

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Status", justify="center")
    table.add_row("Files scanned", str(len(files)), "✅")
    table.add_row("Security issues", str(len(security)), "🔴" if security else "✅")
    table.add_row("TODO / FIXME", str(len(todos)), "⚠️" if todos else "✅")
    table.add_row("Large files (>300 lines)", str(len(large)), "⚠️" if large else "✅")
    table.add_row("Complex functions (>50 lines)", str(len(complex_fns)), "⚠️" if complex_fns else "✅")
    console.print(table)
    console.print()

    if security:
        console.print(Rule("[bold red]🔐 Security Issues[/bold red]"))
        for s in security[:10]:
            sev_color = "bright_red" if s["severity"] == "CRITICAL" else "yellow"
            console.print(f"  [{sev_color}]{s['severity']}[/{sev_color}] {s['file']}:{s['line']} — {s['issue']}")
            console.print(f"    [dim]{s['snippet']}[/dim]")
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

    if ai_result.get("suggestions"):
        console.print(Rule("[bold yellow]💡 AI Suggestions[/bold yellow]"))
        for i, s in enumerate(ai_result["suggestions"], 1):
            console.print(f"  [yellow]{i}.[/yellow] [bold]{s['title']}[/bold]")
            console.print(f"     [dim]{s['detail']}[/dim]")
            console.print()

    roast = ai_result.get("one_line_roast", "")
    if roast:
        console.print(Panel(f"[italic]{roast}[/italic]", title="[magenta]🎤 Vett's Take[/magenta]", border_style="magenta"))
        console.print()

    console.print(Rule("[dim]Report saved → vett_report.md[/dim]"))
    console.print()

def save_markdown_report(root_path, ai_result, security, todos, large, complex_fns, files):
    score = ai_result.get("overall_score", 0)
    grade = ai_result.get("grade", "?")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# 🩺 Vett Health Report",
        f"", f"**Scanned:** `{root_path}`  ",
        f"**Date:** {now}  ",
        f"**Grade:** {grade} | **Score:** {score}/100 | **Tech Debt:** {ai_result.get('estimated_tech_debt', 'Unknown')}",
        f"", f"---", f"",
        f"## 📋 Project Summary", f"",
        f"{ai_result.get('project_summary', 'N/A')}", f"",
        f"## 📊 Stats", f"",
        f"| Metric | Count |", f"|--------|-------|",
        f"| Files scanned | {len(files)} |",
        f"| Security issues | {len(security)} |",
        f"| TODO/FIXME | {len(todos)} |",
        f"| Large files | {len(large)} |",
        f"| Complex functions | {len(complex_fns)} |", f"",
    ]

    if security:
        lines += ["## 🔐 Security Issues", ""]
        for s in security:
            lines.append(f"- **{s['severity']}** `{s['file']}:{s['line']}` — {s['issue']}")
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

    if ai_result.get("suggestions"):
        lines += ["## 💡 AI Suggestions", ""]
        for s in ai_result["suggestions"]:
            lines.append(f"### {s['title']}")
            lines.append(s["detail"])
            lines.append("")

    if ai_result.get("one_line_roast"):
        lines += ["---", f"", f"> 🎤 *{ai_result['one_line_roast']}*", ""]

    report_path = Path(root_path) / "vett_report.md"
    report_path.write_text("\n".join(lines))
    return str(report_path)
