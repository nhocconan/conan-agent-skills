## Harness mechanics — where each rung lives (checked 2026-08-28; re-verify, surfaces move)

### Claude Code

- **Rung 1 — skill.** `.claude/skills/<name>/SKILL.md` in the repo; body loads only when
  invoked. A `!`-prefixed shell line inside the skill injects fresh context (e.g. the
  current `git diff`) before the model reads the body.
- **Rung 2 — hook.** ~30 event types in `settings.json` (PreToolUse, PostToolUse, Stop…).
  A hook that exits **2** blocks the action. Commit the project-shared `settings.json`
  with `deny` rules for secret files so every agent on every machine is blocked alike;
  keep machine-specific hooks in `settings.local.json` (a prettier hook once blocked
  every commit — do not promote that kind of thing to the shared file).
- **Rung 3 — headless.** `claude -p "<prompt>" --output-format json --max-turns N` returns
  a result plus cost; run it from CI or a cron on the box. The official GitHub Action
  can invoke a repo skill by name and run on `schedule:`; keep it read-only (comment /
  report) until rung 5.
- **Rung 4 — scheduled.**
  - Inside a session: `/loop <interval> <prompt|/skill>` (fixed cadence) or `/loop` with
    no interval for self-paced `ScheduleWakeup` — the model picks the next delay from
    what it is waiting on; `CronCreate` for session-bound cron. Session-bound: dies with
    the session, which is the brake.
  - Outside a session: `/schedule` creates **cloud routines** — cron, minimum 1 hour, a
    daily run cap, and **personal skills are not loaded** (the skill must live in the
    repo). A routine's green means "ran", not "succeeded".
  - "Iterate until done" in-session: the `ralph-loop` plugin — a Stop hook re-feeds the
    same prompt; `--max-iterations N` and `--completion-promise '<phrase>'` are the
    brakes, and the promise rule above is binding.
- **Rung 5 — repo-resident.** GitHub Agentic Workflows (`gh-aw`, preview): a markdown
  workflow under `.github/workflows/` compiled to Actions; the agent job runs read-only
  and a separate "safe outputs" job with a narrow token creates issues/PRs. Never merge.

### Codex

Skills are prompt files + `AGENTS.md`; `codex exec` is the headless rung 3; **Codex
Automations** run on a schedule or on Gmail/Slack/GitHub events and drop results into a
review queue (rung 4 with a human gate built in). `codex queue` lets agents message each
other — useful, and exactly the "agents talking unsupervised" channel MIT+Google measured
as a 17× error amplifier without an orchestrator. Keep the lead in the middle.

### Cursor

Custom modes (rung 1), `hooks.json` (rung 2), `/loop` in-session (rung 4, session-bound),
`/goal` persistent agents that watch PRs/Slack (rung 4, write-capable — treat as rung 5
and keep it PR-only). `babysit` is the canonical "keep this PR merge-ready" loop: triage
comments, resolve clear conflicts, fix in-scope CI, never edit CI to make it pass.

### On the box (any harness)

`launchd`/`cron` invoking the headless CLI at night, one loop per night, after the dev
server is down. The kill switch is the cron line itself.
