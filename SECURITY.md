# Security Policy

## Supported versions

This project is in early development. Security fixes are applied to the latest version on the default branch.

## Reporting a vulnerability

Please do not open public issues for suspected vulnerabilities.

Instead, report privately to the maintainers with:

- Description of the issue
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

We will acknowledge reports as quickly as possible and coordinate responsible disclosure.

## Secret handling

- Never commit API keys, tokens, or credentials.
- Use environment variables for secrets (`ANTHROPIC_API_KEY`).
- Rotate keys immediately if exposed.
