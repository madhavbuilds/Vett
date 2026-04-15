# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [Unreleased]

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
