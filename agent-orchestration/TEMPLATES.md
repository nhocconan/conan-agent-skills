# Templates — briefs, ledgers, verifier prompts

Copy-paste shapes for `SKILL.md`. Fill every field; a blank field in a brief becomes an
invented assumption in the executor.

## Contents

1. Handoff brief (implementation node)
2. Structured return schema
3. Verifier prompt (independent, scored)
4. Plan file
5. Fleet ledger
6. Final report shape

---

## 1. Handoff brief (implementation node)

```markdown
MODE: build | investigate | patch | refactor | migrate | verify   (contract in sections/worker-modes.md)
GOAL (one sentence, outcome not activity)
  Creator detail page shows the same NMV as the org export for the selected month.

CONTEXT THE EXECUTOR CANNOT INFER
  Working dir: /abs/path/to/repo   Branch: wip/<topic>   Start: ./scripts/start-dev.sh
  Ground truth for this number: <file/table/oracle>, not the code.

FILES IN SCOPE (absolute paths — everything else is off-limits)
  /abs/path/src/a.ts
  /abs/path/src/b.tsx

ACCEPTANCE CHECKS (exact commands + what green looks like)
  1. pnpm --filter @yng/web build > build.log 2>&1; echo "EXIT=$?"
     → EXIT=0 and build.log contains "Compiled successfully"
  2. pnpm run verify:data > data.log 2>&1; echo "EXIT=$?"
     → EXIT=0 and the new assertion for <metric> appears in the output
  Never pipe a gate through tail/head/grep — the exit code becomes the pipe's.

KNOWN TRAPS HERE
  §41 UTC day-edge leak on month filters; §35 no fabricated multipliers.
  <past incident in this area, one line>

BOUNDARIES
  Implement, do NOT commit. Do not touch migrations. Do not create new docs or scratch
  files outside <scratch dir>. Do not widen scope to adjacent files.

RETURN (exactly this, nothing else — the builder contract in sections/worker-modes.md)
  - files changed + one line each on what changed and why
  - the two command outputs above, verbatim tail (EXIT line included)
  - anything you could NOT verify, and why
  - assumptions you had to make
```

---

## 2. Structured return schema

Use whenever the result feeds a merge or a gate — smaller than prose and mergeable
without re-reading.

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
  "confidence": 9,
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

## 3. Verifier prompt (independent, scored)

Fresh context. Give it the location and the rules — **never the previous agent's verdict**,
or it will confirm it.

```
Read the code at <path>:<line>. Assess independently: is there a <category> defect here?

Rules that make something NOT a finding:
  <FP filter rules for this domain — the specific ones, not "use judgment">

Return:
  score: 1-10 confidence that this is a real defect
  failure_scenario: concrete inputs/state → wrong output (required if score >= 8)
  why_not: if score < 8, explain what makes it not real
Default to a LOW score when uncertain. A plausible mechanism is not a defect.
```

Gate: discard below 8 for anything that would cause a code change. Two different lenses
hitting the same fingerprint raise confidence — say which lenses agreed.

---

## 4. Plan file

`docs/plans/<topic>-<yyyy-mm>.md` — written before wave 1, updated the moment a node lands.

```markdown
# <Topic> — plan (<yyyy-mm-dd>)

GOAL: <one sentence>
DONE WHEN: <the acceptance check for the whole run>
OUT OF SCOPE: <explicitly>

## Seam contracts (decided by the lead, before fan-out)
- types/interfaces: …
- route + i18n key names: …

## Waves
Wave 1 (parallel): N1 survey · N2 schema · N3 research
Wave 2 (needs N2): N4 API · N5 promoter
Wave 3 (needs N4,N5): N6 UI · N7 recon assertion
Lead, wave 1: <the tricky 10%>

## Status
- [x] N1 survey — landed <date>, artifact: docs/plans/notes/n1.md
- [ ] N2 schema — in progress (sonnet, high)
- [ ] N3 …

## Resume
Next session: read this file, continue at the first unchecked box. No re-derivation needed.

## Caps and gaps (never silent)
- N3 research capped at 8 sources; the rest unread.
```

---

## 5. Fleet ledger

Lives in the plan file or beside it. One row per node, updated on landing.

```markdown
| Node | Tier/effort | Status | Acceptance check | Artifact | Verdict | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| N1 survey | haiku/low | done | list of call sites | notes/n1.md | accepted | 14 sites |
| N2 schema | sonnet/med | done | verify:data EXIT=0 | data.log | re-run by lead ✓ | |
| N4 API | sonnet/med | rework 1/2 | build EXIT=0 | build.log | rejected: no tenancy filter | escalate on next fail |
| N6 UI | opus/high | running | browser check | — | — | lead reviewing N4 meanwhile |
```

`Verdict` is the lead's, after re-running the check — not the agent's self-report.

Close every run with the four pilot numbers under the table, so fleets are judged by
data: `wall-clock vs solo: … · tokens: … · defects caught by verification: … · operator
interventions: …`.
`rework 2/2` means the next failure escalates a tier or comes back to the lead
(`SKILL.md` §5.6).

---

## 6. Final report shape

One change, not N agent reports stapled together (`SKILL.md` §6).

```markdown
<Answer first: what is now true, in one or two sentences.>

What landed: <the merged change, by area>
Verified: <the checks the LEAD ran, with their artifacts>
Not verified / assumed: <explicitly, in the same breath as the success>
Dropped: <findings below the gate, capped scope, skipped lenses — with counts>
Next: <what a follow-up run should pick up, or "nothing pending">
```
