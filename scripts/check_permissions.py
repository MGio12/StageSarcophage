#!/usr/bin/env python3
"""Vérifie que les fichiers secrets locaux ne sont pas lisibles par group/other."""
from __future__ import annotations

import argparse
import stat
import sys
from pathlib import Path


def check_env_permissions(env_file: Path) -> list[str]:
    if not env_file.exists():
        return []
    mode = env_file.stat().st_mode
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        return [f"{env_file} doit être en 0600 ou plus restrictif"]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=".env", type=Path)
    args = parser.parse_args(argv)

    findings = check_env_permissions(args.env_file)
    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1

    print("permissions OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
