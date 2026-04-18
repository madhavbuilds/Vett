"""Tests for filesystem helpers."""

from pathlib import Path

from vett.utils import collect_files, has_readme


def test_has_readme_true(tmp_path: Path):
    (tmp_path / "README.md").write_text("# hi", encoding="utf-8")
    assert has_readme(str(tmp_path)) is True


def test_has_readme_false(tmp_path: Path):
    (tmp_path / "not_readme.txt").write_text("x", encoding="utf-8")
    assert has_readme(str(tmp_path)) is False


def test_collect_files_sorted_and_capped(tmp_path: Path):
    (tmp_path / "z.py").write_text("z = 1\n", encoding="utf-8")
    (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")
    (tmp_path / "m.py").write_text("m = 1\n", encoding="utf-8")
    files = collect_files(str(tmp_path), max_files=2)
    assert len(files) == 2
    paths = [f["path"].replace("\\", "/") for f in files]
    assert paths == sorted(paths, key=str.lower)
