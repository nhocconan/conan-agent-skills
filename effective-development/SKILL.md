---
name: effective-development
description: >-
  Choose meaningful development checks, avoid redundant runs, and diagnose slow
  verification while preserving required repository gates. Use for affected-test
  selection, regression coverage, gate-result reuse, expensive test loops, or
  keeping the suite lean (redundant/slop tests, "test suite too slow", "xoá test thừa").
---

# Effective development

The unit of verification is a changed behavior and its failure modes, not a test
count. Use the cheapest checks that detect those failures; required gates remain
at their declared stage. Finite checks cannot guarantee absence of every defect.

## Choose the proof

1. **Read the actual gate policy.** Inspect repository rules, scripts, hooks and CI.
   Required merge/deploy checks cannot be deferred to a future scheduled run or
   replaced by selected tests. Use existing test commands and runtime recipes.
2. **Map behavior to evidence.** Write one line per changed behavior in the task
   plan/ledger (`.agents/`): input → expected result or durable effect → the check that
   would catch a wrong result → what stays unproven. Focus on changed risks; prose
   with no executable consumers needs no invented runtime test.
3. **Get focused feedback per coherent edit batch.** Run the smallest affected check
   first, then relevant lint/typechecks including dependent packages. Use an existing
   affected-check command without narrowing its selection by hand. Build a selector
   only when recurring work warrants one. Writers run the per-change tier (and every
   cheap static audit the touched paths select) before each commit; the full gate
   confirms, it is never the discovery tool.
4. **Widen for indirect impact** using the rules below. Unknown coverage needs broader
   checks, not an optimistic empty set. Runtime journeys/smoke checks follow affected
   behavior and repository policy; they are not mandatory for every commit.
5. **Verify the integrated result.** After writers finish, run required final gates
   and observe the affected user path in the real runtime. A screenshot proves visible
   state, not persistence; HTTP success alone proves neither a usable app nor a journey.
   Reuse valid optional evidence under the rules below.
6. **Stop on evidence.** Finish when acceptance and required gates pass and material
   concerns are resolved or disclosed. Broaden for new failures, missing coverage or
   explicit exhaustive scope, not repeated empty reviews. Report commands, exits/counts,
   actual coverage and omitted checks with reasons; test count/line coverage alone is
   not proof of the changed contract.

## Widen the affected set

- Include deletions, renames and untracked files; use the integration merge base for
  branch changes. Related/changed runners (vitest related/--changed, jest
  --findRelatedTests, pytest-testmon, Bazel rdeps) find static consumers, not every dependency.
- Search consumers of removed, renamed or re-typed exports (`git diff -U0 | grep '^-export'`
  → grep the name repo-wide); include caller tests and dependent-package typechecks.
- Map route/layout/shared-component paths to relevant journeys in the task ledger or
  an existing map. Repair missing entries in existing maps; unknown paths, dynamic
  consumers, stale maps or unexpectedly empty selection require broader checks.
- Encode contracts/schemas, migrations, auth/session/tenancy, env/config, build/CI,
  prompts, disk fixtures and catalogs → named contract/DB/isolation/eval/audit suites.
  Keep widening rules in an existing selector, not individual memory. When building
  one, test target existence and a representative missed dependency/counterexample.
- Never delete/skip/loosen tests or narrow coverage to pass. Legitimate expectation
  changes need a changed contract; deliberate selection narrowing needs evidence and
  explicit rationale. Files read by code cannot silently become “docs-only.”
- Required full gates and scheduled full suites stay full. A regression missed by
  selection adds a map/widening rule with the fix. Log each selection miss; a rising
  miss count means a stale map. The reviewer confirms the widening matched the touched
  paths (a migration got the DB suite) before the gate. Flake earns one fresh rerun; an
  identical second failure is not flake. A failure in code the diff never touched means a
  stale base: check `git merge-base --is-ancestor <base> HEAD`, rebase, do not retry.
  Do not invent CI jobs without policy authorization.

## Recurring failure → fix the system now

A failure class seen twice in one workflow, or any failure that forces a full gate
re-run, is a process defect, not bad luck. Stop and, in the same session:
1. Root-cause why it reached that stage instead of the edit or commit.
2. Pick the cheapest check at the earliest point: commit hook on staged content
   (judge the index, not other writers' unstaged files; block only findings the base
   lacks), the affected-check tier, or a writer-prompt requirement. Audit mechanics:
   [bug-class-audits](../bug-class-audits/SKILL.md).
3. Apply it, prove it catches the original case, and record it in the repository's
   rules or trap log. A threshold that mostly produces churn without catching defects
   becomes a warning or goes, with the evidence; thresholds live in one data file.

Batch the gate: tiers run to the end so one run lists every finding; fix all of them
before re-running, and re-run only the failed tiers plus the affected checks of the
fix diff when the tooling allows. Never re-run a green tier whole to see the next error.

## Make checks detect wrong behavior

For a bug fix, prove regression sensitivity per
[investigating-bugs](../investigating-bugs/SKILL.md) step 8 before counting the test as coverage.

Assert observable behavior against independently specified expectations. Call counts,
truthiness, copied constants or expected values computed by the subject can miss a
plausible wrong result. Yardstick: a test that would still pass if every function it
calls returned nothing tests nothing; rewrite or delete it. Preserve legitimate type,
relational and absence checks;
use a permitted/effective control when it distinguishes a no-op or unconditional
rejection. A mock may isolate an external boundary, not replace the mechanism proved.

For costly external/AI APIs, use deterministic fixtures for routine feedback and a
representative authorized live contract sample when needed, within known limits.
Mocks cannot prove live behavior; record actual usage when exposed, never invented caps.

## Keep the suite lean (when it triggers)

A test costs every future run; it earns its place only by catching a plausible wrong
result that no cheaper or existing check catches. Trim at the point of entry, not in
a rescue audit.

- **Writing a test (builder).** Its title names the regression it catches (behavior,
  invariant or incident id). Never add: log/console call counts, non-contract wording,
  source greps that a function is called (an `audit:*` script owns static facts),
  counts or lengths of registries that only grow, a helper checked against itself,
  expected values computed by the subject, a mock-only test, near-identical cases as
  separate tests (one table loop that names the failing row), or a slow test whose
  fast twin already proves it. Put this list in every builder brief.
- **Review (merge gate).** The reviewer reads the test diff as code: one finding per
  slop test with its delete-or-merge fix; a test diff that grows the suite without a
  new failure mode is a finding. Test-count/suite-time growth above the repository's
  baseline needs each new test's failure mode named, else it goes.
- **A test-only failure in a gate.** If a gate fails only on a test that pins incidental
  output, delete or rewrite that test and rerun only its file, never the whole gate.
- **Periodic.** When summed suite time or test count grows past the repository threshold
  since the last trim (or the scheduled audit comes up), run one trim pass: cheap static
  signals first (fan-out titles, logger-spy counts, source reads in tests, `toHaveLength`
  on registries, string snapshots), slowest files next, one editor per area, serialized
  runs. Keep tenancy, money, auth, routing, migrations, invariants and every recorded
  incident check. Turn each recurring slop pattern into a static audit
  ([bug-class-audits](../bug-class-audits/SKILL.md)) so the next one fails at commit.

## Reuse valid evidence

Record command/scope, revision plus working-diff fingerprint, relevant dependencies,
tests/selector, config/build/seed/environment, exit, duration and artifact path. Reuse
successful optional checks only while these inputs remain valid and policy permits.
A worker verdict alone is insufficient: inspect the evidence against the final tree.

Rerun failed checks and those invalidated by later edits, including previously green
shards affected by a repair. Unknown impact or mutable external state needs fresh
probes. Required hooks/gates still run at their declared stage. Coordinate one final
integrated run instead of duplicate full runs from every worker.

## Shared host

Memory-lean testing (production build, one browser with many contexts, API-level parity,
component tests, conductor): [SHARED-HOST.md](SHARED-HOST.md).

## Keep verification bounded

Run independent read-only checks concurrently only within host capacity. Isolate DBs,
ports and output paths or serialize stateful checks (`dev-env-lifecycle`). For a long
check record the process handle, log path, last progress and next review point; quiet
output alone is not a hang. An unfinished check is incomplete, never passed, and no
budget justifies weakened assertions or a skipped required gate. Stall, termination and
cleanup rules: [tracking](../agent-orchestration/sections/tracking.md).

Staff runs by work nature
([routing](../agent-orchestration/sections/routing.md#work-nature--tier)): the cheapest tier
runs a gate or shard and triages ≤ 30 lines, the builder tier fixes, a reviewer reads
artifacts and runs no suite, and the lead classifies without running a suite in its own
context.

Repeated user journeys live in the project map
([DISTILL](../senior-operator/DISTILL.md) recipe section; rehearse once before calling
it verified); never a new skill or framework to hold a recipe.

Measure changes on comparable tasks: elapsed time, actual usage, rework and selection
misses; prompt bytes are not billed tokens, and unknown savings stay unknown.

## Sources

Selection/pyramid references (read 2026-10-04):
[Google continuous testing](https://research.google/pubs/taming-google-scale-continuous-testing/),
[Meta selection](https://engineering.fb.com/2018/11/21/developer-tools/predictive-test-selection/),
[test impact analysis](https://martinfowler.com/articles/rise-test-impact-analysis.html),
[test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html).
Runner references: [Vitest](https://vitest.dev/guide/cli.html),
[Turborepo](https://turborepo.dev/docs/reference/run).

Procedure comparison (read 2026-10-12): pstack `tdd`, `principle-test-behavior-not-implementation`,
`create-verification-skill` and `maintain-verification-skill`, pinned at
[1b6d44f](https://github.com/cursor/plugins/tree/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/skills).
Adapted to existing maps and repository authority; no upstream installation required.
