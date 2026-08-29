"""Falha a CI quando segredos comuns ou artefatos locais entram no Git."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path, PurePosixPath

SECRET_PATTERNS = {
    "GitHub token": re.compile(rb"(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    "OpenAI key": re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    "AWS access key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "Google API key": re.compile(rb"AIza[0-9A-Za-z_-]{30,}"),
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}

FORBIDDEN_PARTS = {
    ".venv",
    ".playwright-cli",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}
FORBIDDEN_NAMES = {".coverage", ".env"}
FORBIDDEN_SUFFIXES = {".db", ".key", ".p12", ".pem", ".pfx", ".pyc", ".sqlite3"}


def _git_bytes(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
    ).stdout


def _tracked_files() -> list[Path]:
    return [
        Path(item.decode("utf-8")) for item in _git_bytes("ls-files", "-z").split(b"\0") if item
    ]


def _forbidden_artifact(path: Path) -> bool:
    normalized = PurePosixPath(path.as_posix())
    return (
        normalized.name in FORBIDDEN_NAMES
        or normalized.suffix.lower() in FORBIDDEN_SUFFIXES
        or any(part in FORBIDDEN_PARTS or part.endswith(".egg-info") for part in normalized.parts)
    )


def _secret_findings(payload: bytes, location: str) -> list[str]:
    return [
        f"{location}: {name}"
        for name, pattern in SECRET_PATTERNS.items()
        if pattern.search(payload)
    ]


def scan(*, include_history: bool) -> list[str]:
    findings: list[str] = []
    for path in _tracked_files():
        if _forbidden_artifact(path):
            findings.append(f"{path.as_posix()}: forbidden artifact")
            continue
        try:
            payload = path.read_bytes()
        except OSError as exc:
            findings.append(f"{path.as_posix()}: unreadable tracked file ({exc})")
            continue
        findings.extend(_secret_findings(payload, path.as_posix()))

    if include_history:
        history = _git_bytes("log", "-p", "--all", "--format=")
        findings.extend(_secret_findings(history, "git history"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", action="store_true", help="scan all reachable Git diffs")
    args = parser.parse_args()
    findings = scan(include_history=args.history)
    if findings:
        print("Security scan failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Security scan passed: no common secrets or forbidden artifacts found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
