#!/usr/bin/env python3
"""Scan simple des fichiers suivis pour éviter les secrets évidents."""
from __future__ import annotations

import math
import re
import subprocess
import sys
from pathlib import Path


ALLOWLIST_PATTERNS = (
    re.compile(r"pragma: allowlist secret"),
    re.compile(r"placeholder", re.IGNORECASE),
    re.compile(r"example", re.IGNORECASE),
    re.compile(r"os\.environ\.get"),
    re.compile(r"request\.form\.get"),
    re.compile(r"generate_token"),
    re.compile(r"hash_token"),
    re.compile(r"change-in-production", re.IGNORECASE),
)

SECRET_PATTERNS = (
    re.compile(r"(?i)(secret|password|token|api[_-]?key)\w*\s*[:=]\s*['\"]([^'\"]{12,})['\"]"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
)


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line]


def _looks_binary(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return True
    return b"\0" in sample


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {char: value.count(char) for char in set(value)}
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in counts.values())


def main() -> int:
    findings: list[str] = []
    for path in _tracked_files():
        if _looks_binary(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, start=1):
            if any(pattern.search(line) for pattern in ALLOWLIST_PATTERNS):
                continue
            for pattern in SECRET_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                candidate = match.group(match.lastindex or 0)
                if _entropy(candidate) >= 3.0:
                    findings.append(f"{path}:{lineno}: secret-like value")

    if findings:
        print("Secret scan failed:")
        for finding in findings:
            print(f"  {finding}")
        return 1
    print("Secret scan passed for tracked files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
