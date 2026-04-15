import re
from pathlib import Path

SECURITY_PATTERNS = [
    (r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded password"),
    (r'(?i)(api_key|apikey|api-key)\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded API key"),
    (r'(?i)(secret|token)\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded secret/token"),
    (r'(?i)aws_access_key_id\s*=\s*["\'][^"\']+["\']', "Hardcoded AWS key"),
    (r'eval\s*\(', "Use of eval() - dangerous"),
    (r'exec\s*\(', "Use of exec() - potentially dangerous"),
    (r'subprocess\.call\(.*shell\s*=\s*True', "Shell injection risk"),
    (r'os\.system\(', "Use of os.system() - prefer subprocess"),
    (r'pickle\.loads?\(', "Unsafe pickle deserialization"),
]

TODO_PATTERNS = [
    (r'#\s*TODO', "TODO comment"),
    (r'#\s*FIXME', "FIXME comment"),
    (r'#\s*HACK', "HACK comment"),
]

def scan_security(files):
    findings = []
    for file in files:
        for line_num, line in enumerate(file["content"].splitlines(), 1):
            for pattern, description in SECURITY_PATTERNS:
                if re.search(pattern, line):
                    findings.append({
                        "file": file["path"], "line": line_num,
                        "issue": description, "snippet": line.strip()[:80],
                        "severity": "CRITICAL" if "Hardcoded" in description else "WARNING",
                    })
    return findings

def scan_todos(files):
    findings = []
    for file in files:
        for line_num, line in enumerate(file["content"].splitlines(), 1):
            for pattern, description in TODO_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "file": file["path"], "line": line_num,
                        "issue": description, "snippet": line.strip()[:80],
                    })
    return findings

def scan_large_files(files, threshold=300):
    return [
        {"file": f["path"], "lines": f["lines"], "language": f["language"]}
        for f in files if f["lines"] > threshold
    ]

def scan_complexity(files):
    findings = []
    for file in files:
        if file["language"] != "Python":
            continue
        lines = file["content"].splitlines()
        in_function = False
        func_start = 0
        func_name = ""
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("async def "):
                if in_function and (i - func_start) > 50:
                    findings.append({
                        "file": file["path"], "function": func_name,
                        "line": func_start + 1, "length": i - func_start,
                    })
                in_function = True
                func_start = i
                func_name = stripped.split("(")[0].replace("def ", "").replace("async ", "").strip()
        if in_function and (len(lines) - func_start) > 50:
            findings.append({
                "file": file["path"], "function": func_name,
                "line": func_start + 1, "length": len(lines) - func_start,
            })
    return findings
