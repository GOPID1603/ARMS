"""
t08_hardcoded.py — Hardcoded Credentials / Secrets Scan
Static analysis of the codebase for committed secrets.
No network requests needed — runs even when server is offline.
"""
import os, re
from pathlib import Path

# Patterns to match common secrets
SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9_\-]{16,})["\']', "API Key"),
    (r'(?i)(secret[_-]?key|secret)\s*[=:]\s*["\']([A-Za-z0-9_\-]{16,})["\']', "Secret Key"),
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^\'"]{4,})["\']', "Hardcoded Password"),
    (r'(?i)(supabase[_-]?key|sb[_-]?key)\s*[=:]\s*["\']([A-Za-z0-9._\-]{20,})["\']', "Supabase Key"),
    (r'eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}', "JWT / Bearer Token"),
    (r'(?i)(groq|openai|anthropic)[_-]?api[_-]?key\s*[=:]\s*["\']([A-Za-z0-9_\-]{16,})["\']', "AI API Key"),
    (r'gsk_[A-Za-z0-9]{20,}', "Groq API Key"),
    (r'sk-[A-Za-z0-9]{20,}', "OpenAI API Key"),
    (r'(?i)(SUPABASE_URL)\s*[=:]\s*["\']https://[^"\']+["\']', "Supabase URL"),
]

EXCLUDE_DIRS  = {'.git', 'node_modules', '__pycache__', 'build', 'android', 'automated_test'}
INCLUDE_EXTS  = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.sh', '.txt', '.md'}
EXCLUDE_FILES = {'package-lock.json', 'dump.json'}

def run(http, record, cfg, base_url):
    workspace = Path(__file__).parent.parent
    findings_total = 0

    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in files:
            if fname in EXCLUDE_FILES:
                continue
            fpath = Path(root) / fname
            if fpath.suffix not in INCLUDE_EXTS:
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            for pattern, label in SECRET_PATTERNS:
                for match in re.finditer(pattern, content):
                    line_no = content[:match.start()].count('\n') + 1
                    snippet = match.group(0)[:60].replace('\n', ' ')
                    rel_path = str(fpath.relative_to(workspace)).replace('\\','/')

                    # Skip known-safe false positives
                    if any(fp in rel_path for fp in ['test', 'example', 'sample', '.gitignore']):
                        continue

                    findings_total += 1
                    note = f"SECRET in {rel_path}:{line_no} — {label}: {snippet}…"
                    record(rel_path, "STATIC", "codebase-scan", 0, 0,
                           "Hardcoded-Secrets", note, 0,
                           finding=True, severity="CRITICAL")

    if findings_total == 0:
        record("codebase", "STATIC", "codebase-scan", 0, 0,
               "Hardcoded-Secrets", "No obvious hardcoded secrets found in codebase scan.", 0,
               finding=False, severity="INFO")
