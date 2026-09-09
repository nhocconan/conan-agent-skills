#!/usr/bin/env python3
"""Check or create thin Claude/Gemini adapters for one project rule directory.

AGENTS.md is the canonical rule file. This utility operates on exactly one explicit
directory; it does not discover nested rule files or assert hierarchy equivalence
between agent tools.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path


CANONICAL = "AGENTS.md"
OVERRIDE = "AGENTS.override.md"
ADAPTERS = ("CLAUDE.md", "GEMINI.md")
ADAPTER_CONTENT = "@AGENTS.md\n"


@dataclass(frozen=True)
class Finding:
    path: Path
    message: str


def exists_or_link(path: Path) -> bool:
    """Return true for existing paths, including dangling symlinks."""
    return os.path.lexists(path)


def inspect(root: Path) -> tuple[list[Finding], list[Path]]:
    """Return validation findings and the adapters that may be created safely."""
    findings: list[Finding] = []
    missing: list[Path] = []
    canonical = root / CANONICAL

    if canonical.is_symlink() or not canonical.is_file():
        findings.append(Finding(
            canonical,
            "must be an existing regular, non-symlink canonical rule file",
        ))
    elif not canonical.read_text(encoding="utf-8").strip():
        findings.append(Finding(canonical, "must not be empty or whitespace only"))

    override = root / OVERRIDE
    if exists_or_link(override):
        if override.is_symlink() or not override.is_file():
            findings.append(Finding(override, "must be absent or an empty regular file"))
        elif override.read_text(encoding="utf-8"):
            findings.append(Finding(
                override,
                "is nonempty and shadows canonical AGENTS.md; refusing to apply adapters",
            ))

    for name in ADAPTERS:
        adapter = root / name
        if not exists_or_link(adapter):
            missing.append(adapter)
            continue
        if adapter.is_symlink() or not adapter.is_file():
            findings.append(Finding(adapter, "must be a regular, non-symlink adapter"))
            continue
        if adapter.read_text(encoding="utf-8") != ADAPTER_CONTENT:
            findings.append(Finding(
                adapter,
                "must contain exactly '@AGENTS.md\\n'; refusing to overwrite user rules",
            ))
    return findings, missing


def check(root: Path) -> int:
    findings, missing = inspect(root)
    for adapter in missing:
        findings.append(Finding(adapter, "missing adapter"))
    if findings:
        for finding in findings:
            print(f"FAIL: {finding.path}: {finding.message}")
        return 1
    print(f"OK: {root} uses {CANONICAL} with exact Claude/Gemini adapters")
    return 0


def apply(root: Path) -> int:
    findings, missing = inspect(root)
    if findings:
        for finding in findings:
            print(f"FAIL: {finding.path}: {finding.message}")
        print("No adapters written: resolve every finding before applying.")
        return 1

    # All potential collisions were checked before the first write. Missing adapters
    # are the only paths this command creates; exclusive creation prevents a later
    # collision from overwriting a file that appeared after preflight.
    for adapter in missing:
        with adapter.open("x", encoding="utf-8") as handle:
            handle.write(ADAPTER_CONTENT)
        print(f"created: {adapter}")
    if not missing:
        print(f"OK: {root} adapters already match {CANONICAL}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", nargs="?", choices=("check", "apply"), default="check",
        help="check is the default; apply creates only missing exact adapters",
    )
    parser.add_argument(
        "--root", default=".", type=Path,
        help="one project directory containing its canonical AGENTS.md (default: .)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.absolute()
    try:
        if not root.is_dir():
            print(f"FAIL: {root}: project root must be an existing directory")
            return 1
        return apply(root) if args.command == "apply" else check(root)
    except (OSError, UnicodeError) as exc:
        print(f"FAIL: {root}: unable to inspect or create project rules: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
