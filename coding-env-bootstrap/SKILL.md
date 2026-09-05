---
name: coding-env-bootstrap
description: Reproduce this operator's coding-agent environment on a new or remote machine — the skills, plugins, MCP servers, model/effort settings, CLI toolchain and secrets protocol that make Claude Code and Codex perform here. Point an agent at BOOTSTRAP.md on the target machine and it installs and verifies everything itself. Use when setting up a new laptop/server/container, onboarding a remote production box, moving to a different machine, or when the user says "bring my setup over", "cài lại máy mới", "setup remote", "config snapshot", "what do I need to install".
---

# Coding Environment Bootstrap

The portable half of this workstation, written so an agent on the target machine can
install it without the operator narrating each step.

## Use it

On the new machine, in a shell with a coding agent (Claude Code, Codex, agy):

```
Read ~/.conan-agent-skills/coding-env-bootstrap/BOOTSTRAP.md and execute it.
Report each step as done / skipped / failed with the verification output.
```

If `~/.conan-agent-skills` isn't there yet, that's step 0 of `BOOTSTRAP.md` — clone it
first, then re-issue the instruction.

## What's in here

| File | Purpose |
| --- | --- |
| `BOOTSTRAP.md` | The agent-executable install + verification runbook. This is the artifact. |
| `AUDIT.md` | Findings from the source-machine scan and what to change — read before trusting the current config as ideal. |
| `harness.py` | Idempotent `audit` / `apply` / `verify` entry point for Claude, Codex, or both. |
| `templates/` | Secret-free Claude settings, Codex production profile, and shared global quality bar. |
| `local/` | Gitignored. Machine-specific values and anything sensitive. Never committed. |

## Ground rules

- **This repo is public.** No API keys, tokens, account identifiers, internal hostnames,
  or employer project names in `BOOTSTRAP.md` or `AUDIT.md`. Secrets are named and
  sourced, never printed.
- **A production machine is not a workstation clone.** `BOOTSTRAP.md` tiers everything:
  what's universal, what's optional, and what to deliberately skip (macOS-only tooling,
  interactive/desktop integrations, research and statusline toys). Copying the whole
  workstation onto a server imports weight and risk, not capability.
- **Keep it current.** After changing skills, plugins, MCP servers, or settings on any
  machine, update `BOOTSTRAP.md` in the same session — a snapshot that lies is worse
  than no snapshot, because the next machine is built on it.
- **Use the script, not hand-copied snippets.** The script merges Claude's portable
  settings, writes Codex settings as a separate `production` profile, preserves existing
  global instructions outside its managed block, and never copies credentials.
