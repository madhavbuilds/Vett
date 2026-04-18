from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "React JSX",
    ".tsx": "React TSX",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".rb": "Ruby",
    ".php": "PHP",
}

SKIP_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "coverage",
    ".pytest_cache",
    "migrations",
}


def collect_files(root_path: str, max_files: int = 50) -> list:
    root = Path(root_path)
    files = []
    for filepath in root.rglob("*"):
        if any(skip in filepath.parts for skip in SKIP_DIRS):
            continue
        if filepath.suffix in SUPPORTED_EXTENSIONS:
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                if content.strip():
                    files.append(
                        {
                            "path": str(filepath.relative_to(root)),
                            "language": SUPPORTED_EXTENSIONS[filepath.suffix],
                            "content": content,
                            "lines": len(content.splitlines()),
                        }
                    )
            except Exception:
                continue
        if len(files) >= max_files:
            break
    files.sort(key=lambda f: f["path"].replace("\\", "/").lower())
    return files


def has_readme(root_path: str) -> bool:
    root = Path(root_path)
    for name in ["README.md", "README.txt", "README.rst", "readme.md"]:
        if (root / name).exists():
            return True
    return False
