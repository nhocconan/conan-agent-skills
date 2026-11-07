# Trigger evaluation

`trigger_eval.py` runs synthetic prompts through installed Claude, Codex or agy
CLIs. These are real model calls with network usage and possible charges. Use
`trigger-smoke.synthetic.json` first, then `trigger-set.synthetic.json` for routing
coverage across every repository skill and near-miss negatives. Keep results in
the repository's ignored working directory.

Run from an empty temporary Git fixture without production integrations:

```bash
python3 skill-miner/trigger_eval.py skill-miner/trigger-smoke.synthetic.json \
  .agents/codex-smoke.json --harness codex --selection-only --cwd <fixture> --timeout 120 -j 1
python3 skill-miner/trigger_eval.py skill-miner/trigger-smoke.synthetic.json \
  .agents/agy-smoke.json --harness agy --selection-only --cwd <fixture> --timeout 120 -j 1 \
  --skills-dir "$HOME/.gemini/config/skills"
```

Default harness is Claude. Pass `--model` to record a deliberate target from the
canonical routing policy; a requested model is not proof of actual model identity.
`--selection-only` keeps the request as a routing scenario instead of attempting
an unavailable application task; the report records that mode explicitly.
Use `--runs 2` for description acceptance. Keep each harness's results separate:
recall must reach 85% and every negative must be clean. CLI exit 1 means recall
is below the threshold or a negative failed; individual positive misses remain
reported. Inspect `accepted` and `status` before calling an error a routing miss.
`--min-recall` defaults to 0.85; use 1 for a
strict all-positive gate. A failed or denied negative always fails acceptance.

Freeze case labels against skill contracts and global rules before evaluating.
Task-authoring and domain-data requests may need workflows even when they look
small. An independently justified `allowed_auxiliary` list can permit a named
external reference on one negative; raw `fired` and `extra` remain visible and
`unexpected` records other loads. Never blanket-ignore external or owned skills.

Codex uses its read-only sandbox. AGY uses plan mode, terminal sandbox and session
denies for writes, commands, URL reads and MCP; `--skills-dir` grants exact reads
of installed public Markdown files after resolving symlinks. Private directories
and escaping links are excluded. No global permission setting changes. Existing
browser-tab interactions are not proven isolated; use an empty fixture and no
production browser session. Claude retains its read-only tool restrictions.

Only completed successful root reads/invocations count. Failed, malformed,
incomplete or denied runs fail negatives too. Reports omit raw prompts and tool
output. Codex recognizes direct cat/head/sed reads conservatively; other read
mechanisms may undercount. Cutoffs count assistant messages for Claude and tool
steps for Codex/agy, so do not compare them as latency measurements. A skill loaded
on a synthetic prompt does not prove a correct implementation, live-service
compatibility, or equal task effectiveness across models.
