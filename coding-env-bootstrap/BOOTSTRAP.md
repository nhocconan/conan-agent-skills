# BOOTSTRAP — reproduce the coding-agent environment

**Audience: an AI coding agent running on the target machine.** Execute top to bottom.
After each step run its verification and report `done` / `skipped (reason)` /
`failed (output)`. Do not silently skip a failing step; do not invent versions.

**Conventions**

- `[CORE]` — install everywhere, including a headless production server.
- `[DEV]` — workstation only (interactive, GUI, or platform-specific). Skip on a server.
- `[MAC]` — macOS/Xcode only. Skip on Linux.

Read the whole file before starting. Ask the operator only for the items in §7.

---

## 0. [CORE] Preconditions

```bash
uname -a; echo "---"; echo "$SHELL"; echo "HOME=$HOME"
```

Confirm you can write to `$HOME`, that outbound HTTPS works, and that `git` exists.
If the target is a container, confirm the home directory is on a **persistent volume** —
everything below lives in `$HOME` and is lost on rebuild otherwise.

Get or refresh the harness without overwriting a dirty checkout:

```bash
if [ -d "$HOME/.conan-agent-skills/.git" ]; then
  git -C "$HOME/.conan-agent-skills" status --short
  git -C "$HOME/.conan-agent-skills" pull --ff-only
else
  git clone https://github.com/nhocconan/conan-agent-skills.git "$HOME/.conan-agent-skills"
fi
```

If `pull --ff-only` refuses because the checkout is dirty or diverged, stop and resolve
that checkout. Do not reset it or overwrite local work.

---

## 1. [CORE] Toolchain

Reference versions from the source machine (2026-07). Newer is fine; note any major
version you install that differs, and don't downgrade to match.

| Tool | Source version | Tier | Notes |
| --- | --- | --- | --- |
| node | 24.x | CORE | agent CLIs and most projects |
| npm | 11.x | CORE | ships with node |
| pnpm | 11.x | CORE | primary package manager for the operator's repos |
| python3 | 3.14 | CORE | skill scripts assume `python3`, stdlib only |
| uv | 0.9.x | CORE | python env/deps without polluting system python |
| git | 2.47+ | CORE | |
| gh | 2.95+ | CORE | PR/issue flows |
| ripgrep (`rg`) | 15.x | CORE | agents lean on this constantly |
| jq | 1.7+ | CORE | |
| ffmpeg | 8.x | DEV | media/video/preview pipelines only |
| docker | 29.x | CORE if the project stacks are containerized | |
| fd | — | optional | not installed on source; `rg --files` covers it |

```bash
# Linux (Debian/Ubuntu)
sudo apt-get update && sudo apt-get install -y git curl jq ripgrep
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash - && sudo apt-get install -y nodejs
curl -LsSf https://astral.sh/uv/install.sh | sh
sudo corepack enable && corepack prepare pnpm@latest --activate
# gh: https://github.com/cli/cli/blob/trunk/docs/install_linux.md

# macOS
brew install git jq ripgrep ffmpeg gh node python@3.14
curl -LsSf https://astral.sh/uv/install.sh | sh
corepack enable && corepack prepare pnpm@latest --activate
```

**Verify**

```bash
for c in node npm pnpm python3 uv git gh rg jq; do printf "%-8s " "$c"; command -v $c >/dev/null && $c --version 2>&1 | head -1 || echo MISSING; done
```

---

## 2. [CORE] Agent CLIs

```bash
npm i -g @openai/codex          # Codex CLI
npm i -g @google/gemini-cli     # optional second opinion / cheap fan-out
# Claude Code: install per https://docs.claude.com/en/docs/claude-code
```

Then authenticate each — **interactive, the operator must do this themselves**:

```
claude    # then /login
codex     # follow its login prompt
```

Do not attempt to copy credentials from another machine. If the operator runs multiple
accounts, they have per-CLI profile tooling for that (§7).

**Verify**: `claude --version`, `codex --version`, and one trivial prompt through each.

---

## 3. [CORE] Apply the portable harness

The operator's own skills carry accumulated project knowledge. This single step delivers
most of the quality difference between a fresh machine and the source machine.

On a workstation (real browser present):

```bash
python3 "$HOME/.conan-agent-skills/coding-env-bootstrap/harness.py" \
  apply --target all --profile auto --with-mcp
```

`auto` fetches the wrap sources (gstack markdown into `.vendor/`) and installs impeccable before linking. It does **not** run gstack's installer.
On a headless production machine, pin `core` so those suites are skipped:

```bash
python3 "$HOME/.conan-agent-skills/coding-env-bootstrap/harness.py" \
  apply --target both --profile core --with-mcp
```

This one command:

- links the self-contained production skills into `~/.claude/skills` and
  `~/.agents/skills` (Codex's documented user-skill directory);
- merges the portable subset into Claude settings without deleting unrelated keys;
- installs the shared quality bar as managed blocks in `~/.claude/CLAUDE.md` and
  `~/.codex/AGENTS.md`, preserving text outside those blocks;
- writes `~/.codex/production.config.toml` instead of copying the source machine's
  path-specific base config; and
- configures `context7` for both CLIs and the official OpenAI docs MCP for Codex.

Run Codex production jobs with the bounded profile:

```bash
codex exec --profile production "Run the repository verification gates"
```

The production profile uses `workspace-write`, no command-network access, and
`approval_policy = "never"` so an unattended run does not stall while remaining bounded
to the workspace. Install dependencies and authenticate before starting the agent.

Load-outs are explicit and version-controlled:

| Profile | Destination | Contents |
| --- | --- | --- |
| `core` | Claude and/or Codex | Repo-owned, headless-safe skills only |
| `claude-dev` | `~/.claude/skills` | Exact workstation Claude load-out, including installed third parties |
| `codex-dev` | `~/.agents/skills` | Repo-owned Codex skills; external suites are preserved |

Do not edit a shared load-out to prune a server. Select `--profile core`.

The harness defaults to `core` (production-safe). Pass `--profile auto` on a workstation so it fetches wrap sources + impeccable and then links the matching per-agent load-out. `refsync.py` defaults to `auto` on every target: headless hosts get `core` for Claude, and optional third-party skills that exist only on some machines are skipped rather than aborting the apply. `CONAN_AGENT_HEADLESS=1` forces the headless decision; `CONAN_AGENT_ENSURE=0` skips network installs.

**Verify**

```bash
python3 "$HOME/.conan-agent-skills/coding-env-bootstrap/harness.py" \
  verify --target both --profile core
python3 "$HOME/.conan-agent-skills/skill-miner/validate_skills.py" \
  "$HOME/.claude/skills"
python3 "$HOME/.conan-agent-skills/skill-miner/validate_skills.py" \
  "$HOME/.agents/skills"
```

> Two things do **not** come from this repo and must not be assumed present:
> per-project execution maps (`senior-operator/projects/`) and `PROPOSALS.md` are
> gitignored because they name internal systems. If the target machine needs them,
> the operator copies them out of band (§7).

### 3b. [DEV] Third-party skill suites

Do **not** install gstack. The wrappers in this repo (`browsing-web`, `shipping-changes`,
`investigating-bugs`, `web-qa`, `design-qa`) read a handful of SKILL.md files that
`harness.py apply --profile auto` / `refsync.py ensure` fetch from GitHub into
`$HOME/.conan-agent-skills/.vendor/gstack/`.

The source machine may still have a leftover `~/.shared-ai-skills` tree from an older
gstack install. Leave it; do not re-run `./setup`. Before wiping a machine, `refsync.py
rescue` lists anything that lives only there.

---

## 4. [CORE] Settings and global instructions

The canonical secret-free files are under `coding-env-bootstrap/templates/`:

- `claude-settings.core.json` — output/thinking budgets plus a narrow command allowlist;
- `codex-production.config.toml` — a separate production profile, not a replacement for
  `~/.codex/config.toml`;
- `global-instructions.md` — vendor-neutral quality and verification rules installed
  into both agents.

`harness.py apply` installs and merges them. Re-running it is idempotent. A timestamped
backup is written before changing an existing file.

**Deliberately not carried over** — see `AUDIT.md` for the reasoning:

- `skipDangerousModePermissionPrompt` — do **not** set this on a production machine. The
  template uses an explicit `permissions.allow` list instead.
- `tui: "fullscreen"` — interactive preference, harmless but pointless headless.
- Any `env_*` block holding provider API tokens — those are secrets, handled in §7.

Tune permissions to the repositories on that machine. Keep provider configuration,
`[projects.*]` trust, notification commands, plugin state, and credentials in the base
machine config; none belongs in the portable template.

**Verify**: start Claude and run `/config`; run `codex --profile production` and inspect
`/status`. Confirm the repository's own `CLAUDE.md` / `AGENTS.md` still takes precedence.

---

## 5. Plugins, commands, and marketplaces

Enable through `claude` → `/plugin` (it manages `enabledPlugins` and the marketplace
registry itself — hand-editing is more fragile).

| Plugin | Tier | Why |
| --- | --- | --- |
| `code-review` | CORE | diff review before landing |
| `plugin-dev` | CORE | authoring/validating skills and plugins |
| `typescript-lsp` | CORE for TS repos | real symbol resolution beats grep |
| `frontend-design` | DEV | UI work |
| `clangd-lsp` | optional | C/C++ repos only |
| `swift-lsp` | MAC | iOS/macOS repos only |
| `karpathy-skills` | CORE | the behavioural guidelines the operator's `CLAUDE.md` mirrors |
| `claude-hud` | DEV | statusline; cosmetic |
| `caveman` | DEV | token-compression mode; situational |
| `ralph-loop` | DEV | |
| `last30days` | DEV | research; needs its own API keys |

Rule of thumb for the production machine: **LSP for the languages present + code-review +
plugin-dev.** Everything else is optional weight.

For Codex, install only a plugin required by the repository or its production workflow.
The source machine's browser, Chrome, documents, slides, Sites, and visualization plugins
are workstation capabilities, not server defaults. Use `codex plugin list` and
`codex plugin add <plugin-id>` on the target; do not copy the source machine's plugin
cache or marketplace snapshot.

There is no Claude custom-command tree to reproduce on the source machine. Its nine
legacy Codex `speckit.*` prompts are deliberately not copied: Codex custom prompts are
deprecated, and reusable workflows belong in skills. Convert a prompt to a repo skill
only when that production repository actually uses it.

**Verify**: `/plugin` lists the enabled set; restart and confirm no load errors.

---

## 6. MCP servers

| Server | Tier | Command |
| --- | --- | --- |
| `context7` | CORE | Installed for Claude and Codex by `harness.py --with-mcp` |
| `openaiDeveloperDocs` | CORE for Codex | Official OpenAI docs; installed by the harness |
| XcodeBuild MCP | MAC | only where Xcode exists; skip on Linux |
| Chrome/browser MCP | DEV | needs a desktop browser + extension; skip headless |

`context7` is the one that matters everywhere: it pulls current library documentation
instead of relying on model memory, which is the difference between a correct API call
and a confidently wrong one.

**Verify**: `claude mcp list` and `codex mcp list`. MCP configuration is not credential
configuration; complete any required OAuth interaction as the operator.

---

## 7. Secrets and identity — operator-only, never automated

Ask the operator for each of these. **Never copy them from another machine's config
files, never print them, never write them into a repo.**

1. **Agent CLI auth** — interactive login per §2.
2. **Git identity** — the name/email commits must carry on this machine:
   `git config --global user.name "..."` / `user.email "..."`.
3. **`gh auth login`** if the machine pushes or opens PRs.
4. **Alternative model providers.** If the machine uses a non-Anthropic backend, keep the
   token in a file outside any repo (e.g. `~/.config/agent-keys.env`, mode `600`) and
   source it from a shell wrapper that exports `ANTHROPIC_BASE_URL` /
   `ANTHROPIC_AUTH_TOKEN` for that invocation. Do not park provider tokens in
   `settings.json`.
5. **Per-project `.env` files** — never in git; the operator supplies them per repo.
6. **Internal per-project maps** (`senior-operator/projects/`) if the machine works on
   those repos — copied out of band, and confirm the destination is gitignored.

**Verify**: `git -C ~/.conan-agent-skills status --porcelain` is clean. Inspect only
configuration key names when auditing; never print a whole settings file to a shared log.

---

## 8. [CORE] Per-project rulebook

Each repo carries its own `CLAUDE.md` / `AGENTS.md` — that's project-local and arrives
with the clone. Two machine-level rules the operator applies everywhere:

- A rulebook that grows past the char limit stops being loaded. Keep it to invariants
  and traps; link out the reference material.
- The behavioural baseline (think before coding, simplicity, surgical changes,
  goal-driven verification) lives in the project `CLAUDE.md`, matching the
  `karpathy-skills` plugin.

---

## 9. Final verification

Run the secret-safe checks:

```bash
echo "=== tools ==="
for c in node pnpm python3 uv git gh rg jq; do printf "%-8s " "$c"; command -v $c >/dev/null && $c --version 2>&1|head -1 || echo MISSING; done
echo "=== claude skills ==="; find ~/.claude/skills -mindepth 1 -maxdepth 1 | wc -l
echo "=== codex user skills ==="; find ~/.agents/skills -mindepth 1 -maxdepth 1 | wc -l
echo "=== skills repo ==="; git -C ~/.conan-agent-skills log --oneline -1
echo "=== claude mcp ==="; claude mcp list
echo "=== codex mcp ==="; codex mcp list
python3 ~/.conan-agent-skills/coding-env-bootstrap/harness.py \
  verify --target both --profile core
```

Then the real check — a live task, not a version string. In a scratch clone, ask the
agent to run one skill end to end (`secure-code-audit` needs no browser and no
credentials). If it loads, executes, and produces findings, the environment works.

Report anything skipped and why. An honest "skipped: no Xcode on this host" is the
correct outcome for the `[MAC]` rows.
