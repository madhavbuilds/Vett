"""Tests for static analysis scanners."""

from pathlib import Path

import pytest

from vett.scanner import scan_complexity, scan_security, scan_todos


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_scan_security_no_false_positives_on_pattern_definitions():
    """Regression: issue descriptions must not match their own security regexes."""
    scanner_src = (_repo_root() / "vett" / "scanner.py").read_text(encoding="utf-8")
    files = [
        {
            "path": "vett/scanner.py",
            "language": "Python",
            "content": scanner_src,
            "lines": len(scanner_src.splitlines()),
        }
    ]
    findings = scan_security(files)
    assert findings == []


def test_scan_security_detects_hardcoded_secret():
    # Build at runtime so this file does not contain a line matching the hardcoded-key heuristics.
    name = "api" + "_" + "key"
    val = "z" * 20
    code = f'{name} = "{val}"\n'
    files = [{"path": "bad.py", "language": "Python", "content": code, "lines": 1}]
    findings = scan_security(files)
    assert len(findings) == 1
    assert findings[0]["severity"] == "CRITICAL"
    assert "API key" in findings[0]["issue"]


def test_scan_todos_finds_comment():
    # Self-scan: do not spell the work-item marker (hash sign plus TODO) literally in this comment.
    code = "# " + "TODO" + ": fix this\n"
    files = [{"path": "a.py", "language": "Python", "content": code, "lines": 1}]
    assert len(scan_todos(files)) == 1


@pytest.mark.parametrize(
    "src,expect_fn",
    [
        ("def a():\n" + "    pass\n" * 60 + "\ndef b():\n    pass\n", "a"),
        ("async def longone():\n" + "    x = 1\n" * 55 + "\n", "longone"),
    ],
)
def test_scan_complexity_flags_long_functions(src, expect_fn):
    files = [{"path": "m.py", "language": "Python", "content": src, "lines": len(src.splitlines())}]
    hits = scan_complexity(files)
    assert any(h["function"] == expect_fn for h in hits)


def test_scan_complexity_skips_non_python():
    files = [{"path": "x.js", "language": "JavaScript", "content": "function a() {}", "lines": 1}]
    assert scan_complexity(files) == []
