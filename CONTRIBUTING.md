# Contributing to Vett

Thanks for your interest in contributing.

## Development setup

1. Fork and clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install anthropic click rich
pip install -e .
```

## Running locally

```bash
# Local-only scan
vett scan . --no-ai

# AI scan (requires API key)
export ANTHROPIC_API_KEY=your-key-here   # Mac/Linux
set ANTHROPIC_API_KEY=your-key-here      # Windows CMD
```

On Windows terminals that fail on emoji output, set UTF-8 mode first:

```bash
set PYTHONUTF8=1                         # Windows CMD
$env:PYTHONUTF8=1                        # PowerShell
```

## Pull request guidelines

- Keep PRs small and focused.
- Describe user-facing behavior changes in the PR body.
- Update docs when behavior or commands change.
- Do not commit secrets, API keys, or `.env` files.
- Ensure commands in docs work on at least one Unix shell and Windows shell.

## Reporting issues

Open a GitHub issue with:

- What you ran
- Expected behavior
- Actual behavior
- Python version and OS
- Relevant error output
