# Project rules and native adapters

`AGENTS.md` is the canonical project rulebook. Keep shared rules, decisions, and
durable constraints there; do not maintain a second copied policy for each agent.
The file's directory is part of its scope. A nested rule file is an intentional
scope boundary, not a reason to flatten everything into the repository root.

## Loading contract

| File or tool | Contract |
| --- | --- |
| `AGENTS.md` | Canonical content. Codex loads project instructions from the current directory and its ancestors, with closer instructions taking precedence. |
| `CLAUDE.md` | Thin Claude adapter containing exactly `@AGENTS.md` when it is generated here. Claude Code natively reads `CLAUDE.md`; its documented `@...` import resolves relative to the containing file. Since v2.1.277 Claude Code also reads `AGENTS.md` directly, but by default only when no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` exists in the working directory or above — a personal `CLAUDE.local.md` silently turns that off. Keep the adapter: the import never double-loads, and some sessions (Bedrock, telemetry disabled, first run after an upgrade) cannot read `AGENTS.md` directly. |
| `GEMINI.md` | Thin Gemini adapter containing exactly `@AGENTS.md` when it is generated here. Gemini CLI supports `@` imports; its default context filename is `GEMINI.md`, and filename configuration must be checked before relying on another name. |
| Other agents | No generic import convention is assumed. Add an adapter only after that tool's official documentation and an actual runtime check establish its native behavior. |

Codex reads `AGENTS.md` directly; it does not need (and should not be given) a
Codex-specific copy of the same rules. Claude and Gemini have different discovery
hierarchies, so a root adapter importing the root `AGENTS.md` does not prove that a
nested `AGENTS.md` will be loaded by either tool. Create a matching adapter in each
directory whose rules must be available to that tool, or use that tool's documented
scoped mechanism. Keep the directory scope explicit when invoking the checker.

Tool-specific scoped mechanisms remain native mechanisms: for example, Claude's
`.claude/rules/` supports YAML `paths` constraints, while Codex uses its
hierarchical `AGENTS.md` / `AGENTS.override.md` loading. Do not infer equivalent
precedence or discovery semantics across tools.

## Saving a rule

1. Put a durable project-wide rule in the appropriate canonical `AGENTS.md`.
2. Put a scoped rule in the canonical file at that directory, or in the tool's
   documented scoped facility when the rule is genuinely tool-specific.
3. Keep personal preferences in private auto-memory or an explicitly local file;
   never promote them to public project rules without deliberate user intent.
4. Do not save policy by editing `CLAUDE.md`, `GEMINI.md`, or another generated
   adapter. If an existing adapter contains user-authored rules, first merge the
   desired rule into `AGENTS.md`, then review and replace that adapter manually.

## Drift checker

Run the checker for one explicit project-rule directory:

```text
python3 coding-env-bootstrap/project_rules.py check --root PATH
python3 coding-env-bootstrap/project_rules.py apply --root PATH
```

`check` is the default command and is read-only. It reports a missing canonical
file, missing adapters, symlinks, or adapter content that is not the exact thin
import. `apply` creates only missing adapter files after all existing paths have
been checked; it refuses to overwrite an existing nonmatching user file and does
not write around a preflight conflict. Exclusive creation also prevents overwriting
a file created concurrently; an I/O failure can still leave earlier adapters created
(this is not a multi-file transaction). It does not invent or overwrite canonical
rules. Run `apply` separately for each intended scoped directory.

A nonempty `AGENTS.override.md` at the selected directory is rejected because
Codex would load it instead of the canonical file. Audit ancestor/global overrides
and platform-specific rule directories separately; this is not a whole-machine scan.

The checker is suitable for CI as a structural drift gate. CI can catch a missing
adapter or a changed managed import, but it cannot establish rule quality,
precedence semantics, or that a particular installed agent actually loaded the
file. Verify runtime loading with the relevant agent's own documented diagnostic
or context command when that matters.

This repository runs the check in `.github/workflows/project-rules.yml` on pushes
and pull requests. It becomes active after publication; branch protection is a
separate repository setting. Start a new Codex session after changing rules; inspect
Claude's `/context` or Gemini's `/memory show` after loading/reloading the project.

## Global generated instructions

`coding-env-bootstrap/templates/global-instructions.md` is a separate, secret-free
source for the managed global instruction block written by the bootstrap harness.
It is not a project `AGENTS.md`, and it is not a substitute for project rules.
Changes to global behavior belong in that template and require the authorized
harness apply/verify flow. This project-rules contract makes no global setting
changes and must not be used to edit global auto-memory, account settings, or
generated blocks.

## Official references (checked 2026-09-08; Claude memory re-checked 2026-09-23)

- [Claude Code memory and imports](https://code.claude.com/docs/en/memory): `CLAUDE.md` discovery, `@AGENTS.md` imports, hierarchy, and path-scoped rules.
- [Gemini CLI `GEMINI.md`](https://geminicli.com/docs/cli/gemini-md/): hierarchy, `@` imports, and configurable context filenames.
- [ChatGPT/Codex `AGENTS.md`](https://learn.chatgpt.com/docs/agent-configuration/agents-md): project/global scopes, nested precedence, and fallback filenames.
