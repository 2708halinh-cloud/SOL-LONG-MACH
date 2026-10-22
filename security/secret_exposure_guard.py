#!/usr/bin/env python3
"""Fail-closed source guard. Prints only locations/categories, never secret values.
Use locally or in CI: python3 security/secret_exposure_guard.py
"""
import fnmatch
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAX_TEXT_SIZE = 12_000_000
TEXT_EXTENSIONS = {
    ".txt", ".md", ".json", ".jsonl", ".yml", ".yaml", ".toml", ".ini",
    ".env", ".xml", ".py", ".js", ".jsx", ".ts", ".tsx", ".sh", ".ps1",
    ".bat", ".cmd", ".csv", ".html", ".sql", ".properties", ".conf",
}
FORBIDDEN_SUFFIXES = (".p12", ".pfx", ".key")
FORBIDDEN_FILES = (".env", ".env.local", ".env.production", "id_rsa", "id_ed25519")
PATTERNS = {
    "github_token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|github_pat_[A-Za-z0-9_]{50,}"),
    "openai_secret": re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{28,}\b"),
    "aws_access_id": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "gitlab_token": re.compile(r"\bglpat-[A-Za-z0-9_-]{18,}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "client_integration_secret": re.compile(r"\bci_live_[0-9a-zA-Z]{20,}\b"),
    "private_key_pem": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "url_embedded_password": re.compile(r"\b(?:https?|ftp)://[^/\s:@]+:[^/@\s]{8,}@"),
    "plaintext_secret_assignment": re.compile(
        r'''(?ix)(?<![\w])(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password|bearer[_-]?token)\s*["']?\s*[:=]\s*["'](?!YOUR_|REDACTED|MASKED|EXAMPLE|PLACEHOLDER|\$\{|<)[^"'\\\r\n]{16,}["']'''
    ),
}
def tracked_paths():
    if (ROOT / ".git").exists():
        p = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            capture_output=True, check=True
        )
        return [pathlib.PurePosixPath(x.decode("utf-8", errors="replace")) for x in p.stdout.split(b"\0") if x]
    # GitHub's source snapshot is independent of malformed legacy gitlinks.
    return [
        pathlib.PurePosixPath(path.relative_to(ROOT).as_posix())
        for path in ROOT.rglob("*")
        if path.is_file() and not path.is_symlink() and ".git" not in path.relative_to(ROOT).parts
    ]

def scan():
    failures = []
    seen = 0
    for name in tracked_paths():
        rel = name.as_posix()
        path = ROOT.joinpath(*name.parts)
        if not path.is_file():
            continue
        seen += 1
        low = name.name.lower()
        if low in FORBIDDEN_FILES or low.endswith(FORBIDDEN_SUFFIXES) or fnmatch.fnmatch(low, ".env.*"):
            failures.append((rel, "credential_bearing_filename"))
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        size = path.stat().st_size
        if size > MAX_TEXT_SIZE:
            failures.append((rel, "text_too_large_to_inspect"))
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for category, regex in PATTERNS.items():
            if regex.search(text):
                failures.append((rel, category))
    unique = sorted(set(failures))
    print("tracked_files_examined", seen, "alerts", len(unique))
    for rel, category in unique[:80]:
        print("GUARD_ALERT", category, rel)  # never print the matching text
    if len(unique) > 80:
        print("ADDITIONAL_ALERTS_REDACTED", len(unique)-80)
    return 1 if unique else 0

if __name__ == "__main__":
    try:
        sys.exit(scan())
    except Exception as exc:
        # Missing git or file-read error must fail, not silently pass.
        print("GUARD_INCOMPLETE", type(exc).__name__)
        sys.exit(2)
