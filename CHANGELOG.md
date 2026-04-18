# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [Unreleased]

## [0.1.4] - 2026-04-19

### Added
- Unit tests (scanner, utils, AI response normalization) and dev extras (`pytest`, `ruff`).
- CI runs Ruff and pytest before the CLI smoke test.
- README presence row in terminal and markdown reports.

### Fixed
- Security scanner false positives from pattern descriptions and from test fixtures when scanning this repository.
- Deterministic ordering of collected source files.

### Improved
- AI JSON responses are sanitized before display; suggestion items accept varied shapes from models.

## [0.1.3] - 2026-04-15

### Added
- Multi-provider AI support: Anthropic, OpenAI, Gemini, and OpenRouter.
- New scan options: `--provider` and `--model`.
- Provider-specific API key support via environment variables:
  `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`.
- Interactive arrow-key mode selection when no API key is configured.

### Improved
- More polished CLI help and version output.
- Better README and run guides for user-friendly install, usage, and troubleshooting.

## [0.1.1] - 2026-04-15

### Added
- Release automation and packaging improvements.

### Fixed
- Windows `UnicodeEncodeError` when writing `vett_report.md` by forcing UTF-8 report output.

## [0.1.0] - 2026-04-15

### Added
- Initial release of Vett CLI.
- Local codebase scanning (security patterns, TODO/FIXME/HACK, large files, complexity).
- Optional AI analysis via Anthropic API.
- Terminal report output and markdown report export (`vett_report.md`).
