#!/usr/bin/env python3
"""
refsync.py — manage skills derived from upstream suites, and enforce the load-out.

Three jobs:

  status    what drifted upstream since you last reviewed it, and how the active
            skill directory differs from loadout.txt
  upgrade   wrap → report drift and re-verify; fork → 3-way merge onto your version
  loadout   apply a named profile to Claude, Codex, or both

Why `loadout` exists: upstream installers (gstack's ./setup in particular) write their
whole skill suite into ~/.claude/skills on every upgrade, via link_claude_skill_dirs.
There is no setting that stops them. So the load-out is *enforced after* an upgrade,
not configured once. Run `upgrade` (which ends by re-applying it) rather than calling
an upstream installer directly.

Usage:
  python3 refsync.py status
  python3 refsync.py upgrade [name ...]
  python3 refsync.py loadout                         # Claude dev dry run
  python3 refsync.py loadout --apply                 # backward-compatible Claude dev
  python3 refsync.py loadout --target both --profile core --apply
  python3 refsync.py loadout --target codex --profile codex-dev --apply
  python3 refsync.py loadout --migrate               # legacy symlink → real directory
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from urllib.request import urlopen

HOME = Path.home()
REPO = Path(__file__).resolve().parent.parent
LOADOUT_DIR = REPO / "ref-skills" / "loadouts"
LEGACY_LOADOUT = REPO / "ref-skills" / "loadout.txt"

# Where a load-out name is resolved from, in order.
ROOTS = [
    REPO,
    HOME / ".shared-ai-skills",
    HOME / ".agents" / "skills",
    HOME / ".codex" / "skills",
]

TARGET_DIRS = {
    "claude": HOME / ".claude" / "skills",
    # Codex's documented user-skill location. ~/.codex/skills is reserved for
    # bundled/plugin-managed content and is intentionally only a resolution root.
    "codex": HOME / ".agents" / "skills",
}

AUTO_PROFILE = "auto"
BROWSER_COMMANDS = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
    "msedge",
)
BROWSER_APP_PATHS = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
)

# ------------------------------------------------------------------ helpers

def sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw, body = text[3:end], text[end + 4:]
    out, key = {}, None
    for line in raw.split("\n"):
        m = re.match(r"^([a-zA-Z][\w-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            out[key] = m.group(2).strip()
        elif key and line.strip():
            out[key] += " " + line.strip()
    return out, body


def read_source(spec: str) -> str | None:
    """spec: local:<path> | github:<owner>/<repo>@<ref>:<path> | https:<url>"""
    try:
        if spec.startswith("local:"):
            p = Path(spec[6:].strip()).expanduser()
            return p.read_text(encoding="utf-8", errors="replace") if p.exists() else None
        if spec.startswith("github:"):
            m = re.match(r"github:([^/]+)/([^@]+)@([^:]+):(.+)", spec)
            if not m:
                return None
            owner, repo, ref, path = m.groups()
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
            with urlopen(url, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        if spec.startswith(("http://", "https://")):
            with urlopen(spec, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"    ! fetch failed: {e}")
    return None


def ref_skills() -> list[tuple[Path, dict, str]]:
    out = []
    for ref in sorted(REPO.glob("*/REF.md")):
        fm, body = parse_frontmatter(ref.read_text(encoding="utf-8", errors="replace"))
        out.append((ref.parent, fm, body))
    return out


def depended_sections(body: str) -> list[str]:
    """Headings listed under '## Upstream sections this depends on'."""
    m = re.search(r"##\s*Upstream sections this depends on\s*\n(.*?)(?=\n##\s|\Z)", body, re.S)
    if not m:
        return []
    return re.findall(r'^\s*[-*]\s*"?([^"\n]+?)"?\s*(?:—|-{2}|$)', m.group(1), re.M)


# ------------------------------------------------------------------ status

def cmd_status(args) -> int:
    skills = ref_skills()
    if not skills:
        print("no ref skills yet (no */REF.md in the repo)")
    requested_profile = args.profile or default_profile(args.target)
    profiles = selected_profiles(args.target, requested_profile)
    active_refs = {
        name
        for profile in profiles.values()
        for name in read_loadout(profile)
    }
    drift = 0
    for d, fm, body in skills:
        if d.name not in active_refs:
            print(
                f"  {d.name:26} skipped; not active in "
                f"{', '.join(sorted(set(profiles.values())))}"
            )
            continue
        mode = fm.get("mode", "?")
        src = fm.get("source", "")
        cur = read_source(src)
        if cur is None:
            print(f"  {d.name:26} {mode:5}  UNREACHABLE  {src}")
            drift += 1
            continue
        if sha256(cur) == fm.get("fingerprint", ""):
            print(f"  {d.name:26} {mode:5}  up to date")
            continue
        drift += 1
        print(f"  {d.name:26} {mode:5}  UPSTREAM CHANGED since {fm.get('reviewed','?')}")
        missing = [s for s in depended_sections(body) if s.lower() not in cur.lower()]
        for s in missing:
            print(f"      ! depended-on section vanished upstream: {s!r}")
    print()
    loadout_rc = cmd_loadout(argparse.Namespace(
        apply=False, migrate=False, quiet=False,
        target=args.target, profile=requested_profile,
    ))
    return 1 if drift or loadout_rc else 0


# ------------------------------------------------------------------ upgrade

def three_way(ours: Path, base: Path, theirs_text: str) -> tuple[bool, str]:
    """git merge-file --diff3. Returns (clean, merged_text)."""
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        o, b, th = t / "ours", t / "base", t / "theirs"
        o.write_text(ours.read_text(encoding="utf-8", errors="replace"))
        b.write_text(base.read_text(encoding="utf-8", errors="replace"))
        th.write_text(theirs_text)
        # -L labels the conflict markers. Without them git prints the temp paths,
        # which tells whoever resolves the conflict nothing.
        r = subprocess.run(
            ["git", "merge-file", "--diff3", "-p",
             "-L", "YOURS (local edits)",
             "-L", "BASE (upstream when you forked)",
             "-L", "THEIRS (new upstream)",
             str(o), str(b), str(th)],
            capture_output=True, text=True)
        # exit 0 = clean; >0 = that many conflicts; <0 = error
        return r.returncode == 0, r.stdout


def bump_ref(ref: Path, fingerprint: str, version: str | None) -> None:
    text = ref.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"^fingerprint:.*$", f"fingerprint: {fingerprint}", text, count=1, flags=re.M)
    text = re.sub(r"^reviewed:.*$", f"reviewed: {date.today().isoformat()}",
                  text, count=1, flags=re.M)
    if version:
        text = re.sub(r"^version:.*$", f"version: {version}", text, count=1, flags=re.M)
    ref.write_text(text)


def cmd_upgrade(args) -> int:
    targets = set(args.names or [])
    requested_profile = args.profile or default_profile(args.target)
    profiles = selected_profiles(args.target, requested_profile)
    active_refs = {
        name
        for profile in profiles.values()
        for name in read_loadout(profile)
    }
    problems = 0
    for d, fm, body in ref_skills():
        if targets and d.name not in targets:
            continue
        if not targets and d.name not in active_refs:
            print(
                f"{d.name}: skipped; not active in "
                f"{', '.join(sorted(set(profiles.values())))}"
            )
            continue
        src = fm.get("source", "")
        cur = read_source(src)
        if cur is None:
            print(f"{d.name}: UNREACHABLE source {src}")
            problems += 1
            continue
        if sha256(cur) == fm.get("fingerprint", ""):
            print(f"{d.name}: already current")
            continue

        mode = fm.get("mode", "wrap")
        print(f"\n{d.name}: upstream changed ({mode})")

        if mode == "wrap":
            # Never auto-edit a wrapper — its whole value is the local rules.
            missing = [s for s in depended_sections(body) if s.lower() not in cur.lower()]
            for s in missing:
                print(f"  ! depended-on section gone: {s!r} — the wrapper may now be wrong")
                problems += 1
            snap = d / ".upstream-preview.md"
            snap.write_text(cur)
            print(f"  new upstream written to {snap.relative_to(REPO)} for review")
            print(f"  re-read it, confirm the wrapper's claims still hold, then:")
            print(f"    python3 refsync.py upgrade {d.name} --accept")
            if args.accept:
                bump_ref(d / "REF.md", sha256(cur), None)
                snap.unlink(missing_ok=True)
                print("  accepted: fingerprint updated")
        else:  # fork
            base = d / ".upstream" / "SKILL.md"
            ours = d / "SKILL.md"
            if not base.exists():
                print(f"  ! no merge base at {base.relative_to(REPO)} — cannot merge")
                problems += 1
                continue
            clean, merged = three_way(ours, base, cur)
            if clean:
                ours.write_text(merged)
                base.write_text(cur)
                bump_ref(d / "REF.md", sha256(cur), None)
                print("  merged cleanly; SKILL.md and merge base updated")
            else:
                out = d / "SKILL.md.merge"
                out.write_text(merged)
                print(f"  CONFLICT — resolve {out.relative_to(REPO)}, copy over SKILL.md,")
                print(f"  refresh .upstream/SKILL.md, then re-run with --accept")
                problems += 1

    print("\n--- validating ---")
    v = subprocess.run([sys.executable, str(REPO / "skill-miner" / "validate_skills.py")],
                       capture_output=True, text=True)
    print(v.stdout.strip() or v.stderr.strip())
    problems += v.returncode

    print("\n--- re-applying load-out ---")
    loadout_rc = cmd_loadout(argparse.Namespace(
        apply=True, migrate=False, quiet=False,
        target=args.target, profile=requested_profile,
    ))
    return 1 if problems or loadout_rc else 0


# ------------------------------------------------------------------ loadout

def default_profile(target: str) -> str:
    # Auto is safe on both developer workstations and remote machines: it
    # keeps the workstation profile only when its runtime is present.
    return "core" if target == "both" else AUTO_PROFILE


def loadout_path(profile: str) -> Path:
    candidate = LOADOUT_DIR / f"{profile}.txt"
    if candidate.exists():
        return candidate
    # Keep old checkouts and invocations working while loadout.txt remains the
    # workstation Claude load-out.
    if profile == "claude-dev":
        return LEGACY_LOADOUT
    return candidate


def read_loadout(profile: str) -> list[str]:
    path = loadout_path(profile)
    if not path.exists():
        return []
    names = []
    for line in path.read_text().split("\n"):
        line = line.split("#")[0].strip()
        if line:
            names.append(line)
    return names


def resolve(name: str) -> Path | None:
    for root in ROOTS:
        p = root / name
        if (p / "SKILL.md").exists():
            return p
    return None


def requested_targets(target: str) -> list[str]:
    return list(TARGET_DIRS) if target == "both" else [target]


def real_browser_available() -> bool:
    """Return whether this host has a usable interactive browser runtime.

    Auto selection is intentionally conservative: a browser executable on a
    headless Linux host is not enough for workstation browser/design skills.
    Set CONAN_AGENT_BROWSER=1 to opt in on a host with a supported remote
    browser session; CONAN_AGENT_BROWSER=0 or CONAN_AGENT_HEADLESS=1 forces
    the production-safe profile.
    """
    override = os.environ.get("CONAN_AGENT_BROWSER")
    if override is not None:
        return override.strip().lower() in {"1", "true", "yes", "on"}
    if os.environ.get("CONAN_AGENT_HEADLESS", "").strip().lower() in {
        "1", "true", "yes", "on",
    }:
        return False

    executable = any(shutil.which(command) for command in BROWSER_COMMANDS)
    app_bundle = any(path.is_file() for path in BROWSER_APP_PATHS)
    if not (executable or app_bundle):
        return False
    if sys.platform == "darwin":
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def unresolved_names(profile: str) -> list[str]:
    return sorted({name for name in read_loadout(profile) if resolve(name) is None})


def select_profile(target: str, requested: str, *, announce: bool = True) -> str:
    """Resolve auto to a complete profile, keeping explicit profiles strict."""
    if requested != AUTO_PROFILE:
        return requested

    if target == "both":
        return "core"

    workstation = "claude-dev" if target == "claude" else "codex-dev"
    if target == "claude" and not real_browser_available():
        missing = unresolved_names(workstation)
        detail = f"; unavailable entries: {', '.join(missing)}" if missing else ""
        if announce:
            print(
                f"{target}/auto: no real browser detected; using core "
                f"(skipping {workstation} workstation/browser skills{detail})"
            )
        return "core"

    missing = unresolved_names(workstation)
    if not missing:
        if announce:
            print(f"{target}/auto: using {workstation}")
        return workstation

    if announce:
        missing_text = ", ".join(missing)
        print(
            f"{target}/auto: {workstation} is unavailable ({len(missing)} "
            f"unresolved: {missing_text}); using core"
        )
    return "core"


def selected_profiles(target: str, requested: str) -> dict[str, str]:
    return {
        name: select_profile(name, requested)
        for name in requested_targets(target)
    }


def repo_owned_link(path: Path) -> bool:
    if not path.is_symlink():
        return False
    try:
        path.resolve().relative_to(REPO)
        return True
    except (OSError, ValueError):
        return False


def apply_loadout(target: str, profile: str, apply: bool, quiet: bool) -> int:
    active = TARGET_DIRS[target]
    profile = select_profile(target, profile, announce=not quiet)
    wanted = read_loadout(profile)
    label = f"{target}/{profile}"
    if not wanted:
        print(f"{label}: load-out is empty or missing: {loadout_path(profile)}")
        return 1

    if active.is_symlink():
        print(f"! {active} is still a symlink to {active.resolve()}")
        print("  run this command again with --migrate")
        return 1

    have = {p.name for p in active.iterdir()} if active.exists() else set()
    want = set(wanted)
    missing = sorted(want - have)
    collisions = []
    for name in sorted(want & have):
        path = active / name
        expected = resolve(name)
        try:
            actual = path.resolve(strict=True)
        except OSError:
            actual = None
        if expected is not None and actual != expected.resolve():
            collisions.append((name, actual, expected.resolve()))

    for name, actual, expected in collisions:
        print(f"  ! '{name}' collision: {actual or 'broken link'} (expected {expected})")
    if collisions:
        print(f"{label}: refusing to overwrite {len(collisions)} existing skill collision(s)")
        return 1

    # Claude's directory is deliberately an exact curated load-out. Codex's
    # ~/.agents/skills may also contain suites managed by other installers, so
    # only remove links into this repo when changing Codex profiles.
    if target == "claude":
        extra = sorted(have - want)
    else:
        extra = sorted(
            name for name in have - want if repo_owned_link(active / name)
        )

    unresolved = [n for n in missing if resolve(n) is None]
    for n in unresolved:
        print(f"  ! '{n}' in {profile} resolves to no skill in any root")
    if unresolved:
        print(f"{label}: refusing a partial apply ({len(unresolved)} unresolved)")
        return 1

    if not quiet:
        print(
            f"{label}: {len(want)} wanted · {len(missing)} to add · "
            f"{len(extra)} to remove"
        )
        for n in missing:
            print(f"    + {n}")
        for n in extra:
            print(f"    - {n}")

    if not apply:
        if missing or extra:
            print("  (dry run — re-run with --apply)")
        return 0

    active.mkdir(parents=True, exist_ok=True)
    for n in missing:
        src = resolve(n)
        dst = active / n
        if dst.exists() or dst.is_symlink():
            dst.unlink()
        dst.symlink_to(src)
        print(f"    linked {n} -> {src}")

    for n in extra:
        p = active / n
        if p.is_symlink():
            p.unlink()
            print(f"    unlinked {n}")
        elif target == "claude":
            # Never delete real content that lives only here.
            park = HOME / ".shared-ai-skills" / n
            if park.exists():
                shutil.rmtree(p)
                print(f"    removed {n} (real dir; copy retained at {park})")
            else:
                print(f"    ! {n} is a real directory with no upstream copy — left in place")
    return 0


def cmd_loadout(args) -> int:
    profile = args.profile or default_profile(args.target)
    if args.migrate:
        return migrate(args.target, profile)

    return max(
        apply_loadout(target, profile, args.apply, args.quiet)
        for target in requested_targets(args.target)
    )


# ------------------------------------------------------------------ rescue

SHARED = HOME / ".shared-ai-skills"
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", ".venv"}


def orphans() -> list[Path]:
    """Skills that exist ONLY in ~/.shared-ai-skills — not gstack's, not symlinks.

    That tree has no git remote, so anything here exists on one machine only.
    """
    if not SHARED.is_dir():
        return []
    gstack_own = {p.name for p in (SHARED / "gstack").iterdir() if p.is_dir()} \
        if (SHARED / "gstack").is_dir() else set()
    out = []
    for p in sorted(SHARED.iterdir()):
        if p.name.startswith(".") or p.name == "gstack" or p.is_symlink() or not p.is_dir():
            continue
        if p.name in gstack_own or p.name.startswith("_gstack"):
            continue
        out.append(p)
    return out


def dir_size_kb(d: Path) -> tuple[int, int]:
    """(kilobytes, file count) excluding SKIP_DIRS."""
    total = files = 0
    for f in d.rglob("*"):
        if any(part in SKIP_DIRS for part in f.parts):
            continue
        if f.is_file() and not f.is_symlink():
            try:
                total += f.stat().st_size
                files += 1
            except OSError:
                pass
    return total // 1024, files


def cmd_rescue(args) -> int:
    found = orphans()
    if not found:
        print("no orphan skills — nothing lives only in ~/.shared-ai-skills")
        return 0

    rows = [(p, *dir_size_kb(p)) for p in found]
    rows.sort(key=lambda r: -r[1])
    big = [r for r in rows if r[1] > args.max_kb]

    print(f"{len(rows)} skills exist only in {SHARED} (no git remote there):\n")
    for p, kb, n in rows:
        mark = "  [SKIP: over --max-kb]" if kb > args.max_kb else ""
        print(f"  {p.name:30} {kb:>8,} KB  {n:>5} files{mark}")
    if big:
        print(f"\n  {len(big)} skipped as bulk assets — reinstall them from source instead"
              f" of backing them up.")

    if not args.out:
        print("\n(report only — pass --out <dir> to write a tarball)")
        return 0

    import tarfile
    dest = Path(args.out).expanduser()
    dest.mkdir(parents=True, exist_ok=True)
    tar_path = dest / f"orphan-skills-{date.today().isoformat()}.tar.gz"

    def keep(ti: tarfile.TarInfo):
        return None if any(part in SKIP_DIRS for part in Path(ti.name).parts) else ti

    with tarfile.open(tar_path, "w:gz") as tar:
        for p, kb, _ in rows:
            if kb > args.max_kb:
                continue
            tar.add(p, arcname=p.name, filter=keep)
    print(f"\nwrote {tar_path} ({tar_path.stat().st_size // 1024:,} KB)")
    print("Keep this off the machine — that is the entire point.")
    return 0


def migrate(target: str, profile: str) -> int:
    """Convert legacy skill-dir symlinks, then apply the selected load-out."""
    for name in requested_targets(target):
        active = TARGET_DIRS[name]
        if not active.is_symlink():
            active.mkdir(parents=True, exist_ok=True)
            continue
        old_target = active.resolve()
        backup = active.parent / f"{active.name}.symlink-backup-{date.today().isoformat()}"
        if backup.exists() or backup.is_symlink():
            print(f"! backup already exists; refusing to overwrite: {backup}")
            return 1
        print(f"{active} -> {old_target}")
        active.rename(backup)
        active.mkdir()
        print(f"  old symlink preserved as {backup}")

    return max(
        apply_loadout(name, profile, True, False)
        for name in requested_targets(target)
    )


# ------------------------------------------------------------------ main

def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    st = sub.add_parser("status")
    st.add_argument("--target", choices=["claude", "codex", "both"], default="claude")
    st.add_argument("--profile", help="load-out profile or auto (defaults to auto on one target)")

    up = sub.add_parser("upgrade")
    up.add_argument("names", nargs="*")
    up.add_argument("--accept", action="store_true",
                    help="record the new upstream fingerprint after reviewing it")
    up.add_argument("--target", choices=["claude", "codex", "both"], default="claude")
    up.add_argument("--profile", help="load-out profile or auto (defaults to auto on one target)")

    lo = sub.add_parser("loadout")
    lo.add_argument("--apply", action="store_true")
    lo.add_argument("--migrate", action="store_true")
    lo.add_argument("--quiet", action="store_true")
    lo.add_argument("--target", choices=["claude", "codex", "both"], default="claude")
    lo.add_argument(
        "--profile",
        help="load-out profile under ref-skills/loadouts; defaults to auto on one target and core for both",
    )

    rc = sub.add_parser("rescue", help="find skills that exist only on this machine")
    rc.add_argument("--out", help="directory to write the backup tarball into")
    rc.add_argument("--max-kb", type=int, default=5000,
                    help="skip anything bigger; bulk assets belong in a reinstall, "
                         "not a backup (default 5000)")

    args = ap.parse_args()
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "upgrade":
        return cmd_upgrade(args)
    if args.cmd == "rescue":
        return cmd_rescue(args)
    return cmd_loadout(args)


if __name__ == "__main__":
    sys.exit(main())
