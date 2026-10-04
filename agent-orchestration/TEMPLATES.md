# Templates — briefs, ledgers, verifier prompts

Adapt these synthetic examples to the project.

## Contents

[Brief](#1-handoff-brief-implementation-node) · [Returns](#2-structured-return-schema) ·
[Verifier](#3-verifier-prompt-independent-evidence-based) · [Plan](#4-plan-file) ·
[Ledger](#5-fleet-ledger) · [Report](#6-final-report-shape)

## 1. Handoff brief (implementation node)

```markdown
MODE: build | investigate | patch | refactor | migrate | verify   (contract in sections/worker-modes.md)
GOAL (one sentence, outcome not activity)
  Creator detail page shows the same NMV as the org export for the selected month.

CONTEXT THE EXECUTOR CANNOT INFER
  Working dir: /abs/path/to/repo   Branch: wip/<topic>   Start: ./scripts/start-dev.sh
  Ground truth: <file/table/oracle>.

FILES IN SCOPE (absolute paths — everything else is off-limits)
  /abs/path/src/a.ts
  /abs/path/src/b.tsx

ACCEPTANCE CHECKS (exact commands + what green looks like)
  1. pnpm --filter @app/web build > build.log 2>&1; echo "EXIT=$?"
     → EXIT=0 and build.log contains "Compiled successfully"
  2. pnpm run verify:data > data.log 2>&1; echo "EXIT=$?"
     → EXIT=0 and the new assertion for <metric> appears in the output
  Never pipe a gate through tail/head/grep — the exit code becomes the pipe's.

KNOWN TRAPS HERE
  <applicable project invariants + evidence>

BOUNDARIES
  Edit owned files only; no commits, migrations or external writes.
  Scratch artifacts: <ignored directory>.

RETURN (builder contract in sections/worker-modes.md)
  - changed files and reasons
  - the two command outputs above, verbatim tail (EXIT line included)
  - anything you could NOT verify, and why
  - assumptions you had to make
```

---

## 2. Structured return schema

```json
{
  "status": "done | blocked | partial",
  "changes": [{ "path": "src/a.ts", "summary": "…", "risk": "low|med|high" }],
  "checks": [{ "cmd": "pnpm build", "exit": 0, "marker": "Compiled successfully" }],
  "unverified": ["…"],
  "assumptions": ["…"],
  "blocked_on": null
}
```

Finding-shaped work (reviews, audits, sweeps):

```json
{
  "severity": "critical|major|minor",
  "status": "confirmed | concern | unavailable",
  "path": "src/a.ts", "line": 42,
  "category": "tenancy",
  "summary": "one sentence — the defect, not the vibe",
  "failure_scenario": "concrete inputs/state → wrong output",
  "fix": "…",
  "fingerprint": "src/a.ts:42:tenancy",
  "lens": "security"
}
```

---

## 3. Verifier prompt (independent, evidence-based)

Use fresh context, criteria and raw artifacts without the builder's verdict.

```
Read the code at <path>:<line>. Assess independently: is there a <category> defect here?

Rules that make something NOT a finding:
  <FP filter rules for this domain — the specific ones, not "use judgment">

Return:
  status: confirmed | concern | unavailable
  failure_scenario: concrete inputs/state → wrong output
  evidence: relevant lines, reproducible check, or violated invariant
  uncertainty: what remains unverified
A plausible mechanism is a concern until supported by evidence.
```

---

## 4. Plan file

`.agents/<task>-plan.md`: update on each landing.

```markdown
# <Topic> — plan (<yyyy-mm-dd>)

GOAL: <one sentence>
DONE WHEN: <the acceptance check for the whole run>
OUT OF SCOPE: <explicitly>

## Seam contracts (before fan-out)
- types/interfaces: …
- route + i18n key names: …

## Waves
Wave 1 (parallel): N1 survey · N2 schema · N3 research
Wave 2 (needs N2): N4 API · N5 promoter
Wave 3 (needs N4,N5): N6 UI · N7 recon assertion
Lead, wave 1: <the tricky 10%>

## Status
- [x] N1 survey — landed <date>, artifact: .agents/notes/n1.md
- [ ] N2 schema — in progress (builder tier, medium effort)
- [ ] N3 …

## Resume
Next session: reconcile this file with the current diff, workers and latest user
steering; continue ready nodes after checking their dependencies.

## Caps and gaps (never silent)
- N3 research capped at 8 sources; the rest unread.
```

---

## 5. Fleet ledger

One row per node in the plan or adjacent ledger.

```markdown
Record actual models; tiers: `sections/routing.md`.

| Node | Tier/effort | Status | Acceptance check | Artifact | Verdict | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| N1 survey | simple/low | done | list of call sites | notes/n1.md | accepted | 14 sites |
| N2 schema | builder/medium | done | verify:data EXIT=0 | data.log | accepted, re-run by lead | |
| N4 API | builder/medium | rework 1/2 | build EXIT=0 | build.log | rejected: no tenancy filter | escalate on next fail |
| N6 UI | builder/high | running | browser check | — | — | lead reviewing N4 meanwhile |
```

Observed metrics (unknown stays unknown): `wall-clock vs solo: … · tokens: … · defects caught by verification: … · operator
interventions: …`.
`rework 2/2` means two failures have occurred: escalate or re-plan now
(`sections/quality-gate.md`, "Bounded review and repair").

---

## 6. Final report shape

```markdown
<Answer first: what is now true, in one or two sentences.>

Verified: <the checks the LEAD ran, with their artifacts>
Not verified / assumed: <explicitly, in the same breath as the success>
Coverage limits: <unverified concerns, capped scope, skipped lenses>
Next: <what a follow-up run should pick up, or "nothing pending">
```
