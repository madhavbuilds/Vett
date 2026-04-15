# 🩺 Vett — AI-Powered Codebase Health Scanner

> Free alternative to SonarQube. Runs locally. Uses Claude AI.

## Install

```bash
pip install anthropic click rich
pip install -e .
```

## Usage

```bash
# Optional but recommended on Windows (prevents UnicodeEncodeError)
set PYTHONUTF8=1                              # Windows CMD
$env:PYTHONUTF8=1                             # PowerShell

# Step 1 — Set your API key (free at console.anthropic.com)
export ANTHROPIC_API_KEY=your-key-here        # Mac/Linux
set ANTHROPIC_API_KEY=your-key-here           # Windows CMD
$env:ANTHROPIC_API_KEY="your-key-here"        # PowerShell

# Step 2 — Scan any project
vett scan .                    # scan current folder
vett scan ./my-project         # scan a specific folder
vett scan . --no-ai            # no API key needed, local checks only
python -m vett.cli scan .      # fallback if `vett` is not in PATH
```

## What it checks

| Check | Description |
|-------|-------------|
| 🔐 Security | Hardcoded secrets, unsafe eval/exec, SQL injection |
| 📏 Complexity | Functions longer than 50 lines |
| 📦 Large files | Files over 300 lines |
| 📝 TODOs | Unresolved TODO/FIXME/HACK comments |
| 🤖 AI Analysis | Project summary, grade, strengths, suggestions |

## Output

- Beautiful terminal report
- `vett_report.md` saved in your project folder

## Troubleshooting

- `vett: command not found` -> run `python -m vett.cli scan . --no-ai`
- `UnicodeEncodeError` on Windows -> set `PYTHONUTF8=1` and run again
- `No API key found` -> set `ANTHROPIC_API_KEY` or use `--no-ai`
- `No source files found` -> verify the target path includes supported code files (`.py`, `.js`, `.ts`, etc.)

## Requirements

- Python 3.9+
- Anthropic API key (free tier available at console.anthropic.com)

## Open Source

- License: MIT (`LICENSE`)
- Contributing guide: `CONTRIBUTING.md`
- Security policy: `SECURITY.md`

## Quick start for contributors

```bash
pip install anthropic click rich
pip install -e .
python -m vett.cli scan . --no-ai
```
