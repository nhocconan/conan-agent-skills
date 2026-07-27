---
name: skill-miner
description: Mine local coding-agent conversation history (Claude Code, Claude Cowork, Codex) for recurring pain that deserves to become a reusable agent skill — then write the skill. Runs incrementally with a stored watermark, so each run only reads sessions since the last one; a full re-scan is available on request. Use when the user says "scan my conversations for skills", "quét lịch sử tìm skill", "mine my history", "what should become a skill", "review my skills", or on a recurring schedule to keep ~/.conan-agent-skills current.
---

# Skill Miner

Work history is the only honest record of what actually goes wrong repeatedly. This skill
turns that record into skills — and, just as importantly, **refuses** to turn most of it
into skills. The default outcome of a mining run is "nothing new cleared the bar."

## Run modes

```bash
cd ~/.conan-agent-skills/skill-miner

python3 mine_history.py                    # incremental — since the stored watermark
python3 mine_history.py --full             # everything from the beginning
python3 mine_history.py --since 2026-07-04 # explicit floor
python3 mine_history.py --commit           # advance the watermark (ONLY after a good run)
```

The watermark lives in `state/last-run.json` (gitignored) and is advanced **only** with
`--commit`. Run without `--commit` first; commit at the end, once the analysis actually
finished. A crashed run therefore re-mines the same window rather than silently skipping it.

Default to incremental. Use `--full` when the user asks for it, when the bar itself
changed, or when `state/last-run.json` is missing.

## What it reads

| Store | Path |
| --- | --- |
| Claude Code / Desktop | `~/.claude/projects/<slug>/*.jsonl` |
| Claude Cowork | `~/Library/Application Support/Claude/{claude-code-sessions,local-agent-mode-sessions}/**` |
| Codex CLI / Desktop | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` |
| Distilled findings | `~/.claude/projects/*/memory/*.md` |

`subagents/` subtrees are **deliberately skipped** — the "user" turns in those files are
agent-authored prompts, not human intent.

## The pipeline

1. **Scan** → `mine_history.py` writes a markdown digest (stats, per-project volume,
   slash commands used, correction-flavoured turns, procedure-flavoured turns,
   changed memory files). It is a scanner, not an analyst.
2. **Filter to human intent.** The digest still contains agent output that landed in a
   `user` turn: task-notification results, pasted reports, injected `CLAUDE.md`/`AGENTS.md`.
   Drop turns containing `<task-notification>`, `</result>`, `<summary>`,
   `<uploaded_files>`, `# AGENTS.md instructions`, or that are just a rulebook dump.
   Dedupe on the first ~200 chars — the same brief gets replayed across resumed sessions
   and will otherwise fake "recurring". A genuinely typed turn is usually < 1500 chars.
3. **Cluster** the survivors by the *pain*, not the topic. "The dashboard number was
   wrong" and "the KPI drifted between pages" are one cluster.
4. **Apply the bar** (below) to each cluster.
5. **Implement** what passes; **record why** for what doesn't.
6. `--commit` the watermark, update `README.md` + `PROPOSALS.md`, symlink, commit.

## Validate before and after

```bash
python3 validate_skills.py                    # the conan repo
python3 validate_skills.py ~/.claude/skills   # everything installed on this machine
python3 validate_skills.py --errors-only
```

Encodes Anthropic's published authoring spec. **Errors are silent killers** — a skill that
fails one of these does not trigger, and nothing tells you:

- frontmatter must open with `---` on line 1 (otherwise it is never parsed and the literal
  string `name: x` becomes the description);
- `name` ≤64 chars, `[a-z0-9-]` only, **must equal the directory name**, and must not
  contain the reserved words `anthropic` or `claude`;
- `description` non-empty, ≤1024 chars, no XML tags — note that a literal `<slug>` in a
  description counts as a tag.

Warnings cover the quality rules: body ≤500 lines, description states *when* not just
*what*, third person, references exist and stay one level deep, reference files >100 lines
carry a table of contents.

Run it on `~/.claude/skills` too — third-party and generated skills fail these constantly,
and a broken one is invisible rather than loud. Skills owned by an upstream installer are
regenerated on upgrade: report those defects, don't patch them.

## The bar — all four, or it is not a skill

1. **Recurring** — the same pain in **≥2 different projects**, or ≥3 separate sessions in
   one project. One incident is a memory entry.
2. **Generalizable** — it would still be true in a repo that doesn't exist yet. Anything
   naming a specific table, endpoint, or internal system is a *project map*
   (`senior-operator/projects/`) or project memory.
3. **Procedural** — steps, checks, recipes, scripts. Something an agent can *execute*.
4. **Not already covered** — grep every existing `SKILL.md` first. A near-miss becomes a
   **new section in the existing skill**, which is almost always the better outcome:
   one more skill dilutes every skill's triggering.

### Explicitly not skills

Behavioural preferences and demands — tone and address forms, "work autonomously, don't
ask", "test everywhere", "definition of done", git habits (main-only, commit identity),
scolding patterns. These are real and they matter, but they belong in auto-memory or
`CLAUDE.md`. The operator has said this directly: *"các thứ nó quá specific như anh hay
chửi, bắt test ở mọi nơi, có definition of done, etc. đều không phù hợp làm skill."*

Frequency is not the bar. The loudest cluster in any scan is frustration; frustration is
a pointer to a procedure, not the procedure.

## Writing the skill

House format — see any sibling directory. Run `validate_skills.py` after every edit;
the rules below are the ones it cannot check.

**The description is a routing rule, not a summary.** It is the only part loaded at
startup, competing with ~90 other skills for the model's attention. Write it third
person, state **what it does and when to fire**, and include the exact phrasings the
operator types — Vietnamese included. Claude *undertriggers* skills, so lean pushy.
A perfect skill that never fires is worth nothing.

**Be concise; assume the model is already smart.** Only add context it doesn't have.
Challenge every paragraph: does this justify its token cost? Explaining what a PDF is
wastes context that the actual task needs.

**Match freedom to fragility.** Prose steps where many approaches work and judgment
applies; a parameterised script where a preferred pattern exists; an exact command with
"do not modify" where the operation is fragile or destructive. Narrow bridge → guardrails;
open field → direction.

**Prefer scripts to instructions** for anything deterministic. A bundled script is more
reliable than generated code, costs no context until it runs, and produces consistent
results. Scripts must *solve* rather than defer — handle the error, don't hand it back —
and every constant needs a comment justifying its value.

**Progressive disclosure past ~500 lines.** SKILL.md becomes a table of contents pointing
at `reference/*.md`; keep links **one level deep** (nested references get partially read),
and give any reference over 100 lines its own contents list.

**Build the evaluation before the documentation.** Run the task without the skill, note
where it actually fails, and write only enough to close that gap. Then test with the
models that will run it — what Opus infers, Haiku needs spelled out.

Body style: dense, imperative, evidence-backed. Every rule traces to a real incident —
cite the failure, not an abstraction. Avoid time-sensitive phrasing ("as of August…");
put superseded material under an "old patterns" heading instead. Keep terminology
consistent — one term per concept, throughout.

Source: [Anthropic skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

Then:

```bash
ln -sfn ~/.conan-agent-skills/<name> ~/.claude/skills/<name>
```

Add a row to `README.md`'s index and an evidence row to `PROPOSALS.md` (gitignored —
it names internal systems). Record rejections in `PROPOSALS.md` too, with the reason;
next run then re-litigates nothing.

## Also do on every run

- **Polish existing skills** with what the window revealed — a new failure mode, a stale
  path, a trigger phrase the operator used that the description doesn't match.
- **Report honestly.** "3 clusters found, 1 became a skill, 2 folded into existing ones,
  4 rejected as preferences" is a good run. Inventing a skill to have a deliverable is
  the failure mode this skill exists to prevent.

## Scheduling

There is no daemon. Either the operator invokes it, or wire it to a scheduler
(`/loop`, a cron routine) — the watermark makes repeated invocation cheap and correct.
A sensible cadence is every 2–4 weeks: less often and the digest is too big to reason
over, more often and nothing has cleared the "recurring" bar yet.
