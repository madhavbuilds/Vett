[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

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

## Release process (PyPI)

1. Update version in `vett/__init__.py` (`__version__`).
2. Add release notes in `CHANGELOG.md` (move items from `Unreleased` to the new version).
3. Commit and push to `main`.
4. Create a GitHub Release (or tag) for that version.
5. GitHub Actions publishes to PyPI via `.github/workflows/publish-pypi.yml`.

### One-time PyPI setup

- In PyPI, create a trusted publisher for this GitHub repository/workflow.
- Recommended: restrict publishing to releases from `main`.

### Manual local publish (fallback)

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```
