#!/usr/bin/env python3
"""Install and verify the portable Claude/Codex coding-agent harness.

This script is intentionally stdlib-only and does not handle credentials. It
merges a safe Claude settings subset, installs a separate Codex profile, adds a
small managed global-instructions block, and delegates skill linking to
refsync.py.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


HOME = Path.home()
HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REFSYNC = REPO / "ref-skills" / "refsync.py"
TEMPLATES = HERE / "templates"
START = "<!-- conan-agent-harness:start -->"
END = "<!-- conan-agent-harness:end -->"


def targets(value: str) -> list[str]:
    if value == "both":
        return ["claude", "codex"]
    if value == "all":
        return ["claude", "codex", "agy"]
    return [value]


def run(command: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True)
    if result.stdout.strip():
        print(result.stdout.rstrip())
    if result.stderr.strip():
        print(result.stderr.rstrip(), file=sys.stderr)
    if check and result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}")
    return result


def find_cli(name: str) -> str | None:
    """Find an agent CLI, including common per-user install locations."""
    discovered = shutil.which(name)
    if discovered:
        return discovered

    candidates = [
        HOME / ".local" / "bin" / name,
        HOME / ".claude" / "local" / name,
        HOME / ".npm-global" / "bin" / name,
        HOME / ".volta" / "bin" / name,
    ]
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def merge(base, overlay):
    if isinstance(base, dict) and isinstance(overlay, dict):
        result = dict(base)
        for key, value in overlay.items():
            result[key] = merge(result.get(key), value)
        return result
    if isinstance(base, list) and isinstance(overlay, list):
        return list(dict.fromkeys([*base, *overlay]))
    return overlay


def backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = path.with_name(f"{path.name}.bak-{stamp}")
    shutil.copy2(path, destination)
    return destination


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        saved = backup(path)
        print(f"  backup: {saved}")
    path.write_text(content, encoding="utf-8")
    return True


def install_managed_instructions(path: Path) -> bool:
    body = (TEMPLATES / "global-instructions.md").read_text(encoding="utf-8").rstrip()
    block = f"{START}\n{body}\n{END}"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if START in current and END in current:
        before, rest = current.split(START, 1)
        _, after = rest.split(END, 1)
        updated = f"{before}{block}{after}"
    else:
        separator = "\n\n" if current.strip() else ""
        updated = f"{current.rstrip()}{separator}{block}\n"
    return write_if_changed(path, updated)


def install_claude_config() -> None:
    path = HOME / ".claude" / "settings.json"
    template = json.loads(
        (TEMPLATES / "claude-settings.core.json").read_text(encoding="utf-8")
    )
    current = {}
    if path.exists():
        current = json.loads(path.read_text(encoding="utf-8"))
    merged = merge(current, template)
    # This laptop-only bypass must never survive application of the production
    # harness. Unknown settings are preserved, but this specific key is unsafe
    # for an unattended machine.
    merged.pop("skipDangerousModePermissionPrompt", None)
    updated = json.dumps(merged, indent=2, ensure_ascii=False) + "\n"
    changed = write_if_changed(path, updated)
    print(f"claude settings: {'updated' if changed else 'already current'}")

    changed = install_managed_instructions(HOME / ".claude" / "CLAUDE.md")
    print(f"claude global instructions: {'updated' if changed else 'already current'}")


def install_codex_config() -> None:
    source = TEMPLATES / "codex-production.config.toml"
    destination = HOME / ".codex" / "production.config.toml"
    changed = write_if_changed(destination, source.read_text(encoding="utf-8"))
    print(f"codex production profile: {'updated' if changed else 'already current'}")

    changed = install_managed_instructions(HOME / ".codex" / "AGENTS.md")
    print(f"codex global instructions: {'updated' if changed else 'already current'}")


def install_skills(target: str, profile: str) -> None:
    command = [
        sys.executable,
        str(REFSYNC),
        "loadout",
        "--target",
        target,
        "--profile",
        profile,
        "--migrate",
    ]
    if run(command).returncode:
        raise RuntimeError(f"skill installation failed for {target}/{profile}")


def ensure_upstreams(target: str, profile: str) -> None:
    if profile == "core":
        return
    command = [
        sys.executable, str(REFSYNC), "ensure",
        "--target", target, "--profile", profile,
    ]
    if run(command).returncode:
        raise RuntimeError(f"upstream install failed for {target}/{profile}")


def mcp_names(cli: str | None) -> str:
    if not cli:
        return ""
    return run([cli, "mcp", "list"]).stdout


def install_context7(target: str) -> None:
    cli = find_cli(target)
    if not cli:
        raise RuntimeError(
            f"{target} CLI was not found in PATH or a common user install "
            "location; cannot install context7"
        )
    configured = mcp_names(cli).lower()
    if "context7" in configured:
        print(f"{target} MCP context7: already configured")
    else:
        if target == "claude":
            command = [
                cli, "mcp", "add", "-s", "user", "context7", "--",
                "npx", "-y", "@upstash/context7-mcp@latest",
            ]
        else:
            command = [
                cli, "mcp", "add", "context7", "--",
                "npx", "-y", "@upstash/context7-mcp@latest",
            ]
        if run(command).returncode:
            raise RuntimeError(f"failed to configure context7 for {target}")
    if target == "codex":
        configured = mcp_names(cli).lower()
        if "openaideveloperdocs" not in configured:
            command = [
                cli, "mcp", "add", "openaiDeveloperDocs",
                "--url", "https://developers.openai.com/mcp",
            ]
            if run(command).returncode:
                raise RuntimeError("failed to configure OpenAI developer docs for codex")


def desired_names(profile: str) -> list[str]:
    path = REPO / "ref-skills" / "loadouts" / f"{profile}.txt"
    if profile == "claude-dev" and not path.exists():
        path = REPO / "ref-skills" / "loadout.txt"
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.split("#", 1)[0].strip()
        if value:
            names.append(value)
    return names


def active_dir(target: str) -> Path:
    return {
        "claude": HOME / ".claude" / "skills",
        "codex": HOME / ".agents" / "skills",
        "agy": HOME / ".gemini" / "config" / "skills",
    }[target]


def verify_target(target: str, profile: str) -> list[str]:
    errors = []
    active = active_dir(target)
    for name in desired_names(profile):
        repo_skill = REPO / name / "SKILL.md"
        path = active / name
        if repo_skill.is_file():
            if not path.is_dir() or not (path / "SKILL.md").exists():
                errors.append(f"{target}: missing or invalid skill {path}")
            elif profile in {"core", "codex-dev"}:
                expected = (REPO / name).resolve()
                if path.resolve() != expected:
                    errors.append(
                        f"{target}: skill collision at {path} "
                        f"(resolved {path.resolve()}, expected {expected})"
                    )
        elif path.exists() and not (path / "SKILL.md").exists():
            errors.append(f"{target}: invalid skill {path}")

    if target == "claude":
        settings = HOME / ".claude" / "settings.json"
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
            if data.get("skipDangerousModePermissionPrompt"):
                errors.append("claude: dangerous-mode prompt bypass is enabled")
        except Exception as exc:
            errors.append(f"claude: invalid settings.json: {exc}")
        instructions = HOME / ".claude" / "CLAUDE.md"
    elif target == "codex":
        profile_path = HOME / ".codex" / "production.config.toml"
        if not profile_path.is_file():
            errors.append(f"codex: missing profile {profile_path}")
        instructions = HOME / ".codex" / "AGENTS.md"
    else:
        return errors

    if not instructions.is_file() or START not in instructions.read_text(
        encoding="utf-8"
    ):
        errors.append(f"{target}: managed global instructions are missing")
    return errors


def audit(args) -> int:
    print(f"home: {HOME}")
    print(f"repo: {REPO}")
    failures = []
    for target in targets(args.target):
        profile = args.profile or "core"
        result = run([
            sys.executable, str(REFSYNC), "loadout",
            "--target", target, "--profile", profile,
        ])
        failures.extend(verify_target(target, profile))
        if result.returncode:
            failures.append(f"{target}: load-out audit failed")
    for item in failures:
        print(f"FAIL: {item}")
    return 1 if failures else 0


def apply(args) -> int:
    profile = args.profile or "core"
    ensure_upstreams(args.target, profile)
    for target in targets(args.target):
        install_skills(target, profile)
        if target == "claude":
            install_claude_config()
        elif target == "codex":
            install_codex_config()
        if args.with_mcp and target in {"claude", "codex"}:
            install_context7(target)
    return audit(args)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["audit", "apply", "verify"])
    parser.add_argument(
        "--target",
        choices=["claude", "codex", "agy", "both", "all"],
        default="both",
    )
    parser.add_argument(
        "--profile",
        help="explicit load-out profile; defaults to core (production-safe). "
             "Use --profile auto on a workstation — that fetches wrap sources + impeccable first.",
    )
    parser.add_argument(
        "--with-mcp",
        action="store_true",
        help="configure context7 using the installed CLIs (may need network)",
    )
    args = parser.parse_args()
    try:
        if args.command == "apply":
            return apply(args)
        return audit(args)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
