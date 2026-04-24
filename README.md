[![PyPI](https://img.shields.io/pypi/v/vett)](https://pypi.org/project/vett/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

# 🩺 Vett — AI-Powered Codebase Health Scanner

> Fast codebase health checks with optional AI analysis. Local-first, open source, and developer-friendly.

## ✨ Features

- 🔐 Security pattern detection (secrets, risky APIs)
- 📏 Complexity and maintainability checks
- 📝 TODO/FIXME/HACK discovery
- 🤖 Optional AI project analysis (Anthropic, OpenAI, Gemini, OpenRouter)
- 📄 Markdown report output (`vett_report.md`)

## 📦 Install

```bash
pip install -U vett
```

If you are developing locally:

```bash
pip install -e .
```

## 🚀 Quick Start

```bash
# Scan current project (interactive mode if no API key is set)
vett scan .

# Scan without AI
vett scan . --no-ai

# Scan a specific folder
vett scan ./my-project
```

## 📋 Quick Copy Commands

```powershell
# Check latest live version on PyPI
python -c "import json,urllib.request;print(json.load(urllib.request.urlopen('https://pypi.org/pypi/vett/json'))['info']['version'])"
```

```powershell
# Install/upgrade to latest
python -m pip install -U vett
```

```powershell
# Verify installed CLI version
vett version
```

```powershell
# Scan without AI
vett scan . --no-ai
```

```powershell
# Scan with Anthropic + explicit model
vett scan . --provider anthropic --model claude-3-5-sonnet-latest
```

API key setup (optional):

```bash
# Anthropic
export ANTHROPIC_API_KEY=your-key-here        # Mac/Linux
set ANTHROPIC_API_KEY=your-key-here           # Windows CMD
$env:ANTHROPIC_API_KEY="your-key-here"        # PowerShell

# OpenAI
export OPENAI_API_KEY=your-key-here

# Gemini
export GEMINI_API_KEY=your-key-here

# OpenRouter (great for free/open models)
export OPENROUTER_API_KEY=your-key-here
```

Pick provider with:

```bash
vett scan . --provider anthropic
vett scan . --provider openai
vett scan . --provider gemini
vett scan . --provider openrouter
```

## 🧭 CLI Reference

```bash
vett --help
vett scan --help
vett scan . --provider openrouter
vett scan . --provider openai --model gpt-4o-mini
vett version
vett version --short
```

## 📊 What Vett Checks

| Check | Description |
|-------|-------------|
| 🔐 Security | Hardcoded secrets, unsafe eval/exec, SQL injection patterns |
| 📏 Complexity | Functions longer than 50 lines |
| 📦 Large files | Files over 300 lines |
| 📝 TODOs | Unresolved TODO/FIXME/HACK comments |
| 🤖 AI Analysis | Project summary, grade, strengths, suggestions |

## 📁 Output

- Colorful terminal report
- `vett_report.md` saved in your target folder

## 🛠️ Troubleshooting

- `vett: command not found` -> reinstall with `pip install -U vett` and restart terminal
- `UnicodeEncodeError` on Windows -> set `PYTHONUTF8=1` before running
- `No source files found` -> verify the target has code files (`.py`, `.js`, `.ts`, ...)

## 🤝 Open Source

- License: MIT (`LICENSE`)
- Contributing guide: `CONTRIBUTING.md`
- Security policy: `SECURITY.md`
- Changelog: `CHANGELOG.md`

## 🧪 For Contributors

```bash
pip install -e .
vett scan . --no-ai
```

## 📤 Release Process (PyPI)

1. Update `vett/__init__.py` version.
2. Update `CHANGELOG.md`.
3. Push to `main`.
4. Create a GitHub release or version tag.
5. Workflow `.github/workflows/publish-pypi.yml` publishes to PyPI.
