---
name: effective-development
description: >-
  Select verification for a development change while preserving required repository
  gates. Use when speeding up test loops, choosing affected tests, investigating
  selection misses, or designing test impact analysis. Track gaps alongside runtime.
---

# Effective development

Use affected tests for fast feedback when selection covers the changed behavior.
Required repository gates, hooks and branch protections still run at their declared
stage. Selection can miss dependencies; measure misses alongside runtime.

## Tiers

| Tier | When | What runs | Budget |
| --- | --- | --- | --- |
| T0 inner loop | every edit | typecheck of the touched packages **and their dependents**; lint on changed files; unit tests that import the changed modules (`vitest related` / `--changed`, `jest --findRelatedTests`, `pytest-testmon`, Bazel `rdeps`) | seconds to a few minutes, no lock |
| T1 pre-merge | before each commit to the integration branch | T0 + the widening rules below + the E2E/journey specs mapped from the touched routes, plus the smoke spec | minutes; one at a time on a shared host |
| T2 deploy gate | each deploy batch | the project's full gate (typecheck, lint, audits, all unit, build) + full E2E on a fresh DB + an independent reviewer pass over the combined diff | the long run, once per batch |
| T3 schedule | nightly, or CI on every push off the dev host | full suite; it exists to catch what T0/T1 selection missed | free of the agent's wall clock |

The tiers are a starting design, not permission to replace existing gates.
One command per project implements T0/T1 (`check:affected`-style), with a pure
selection function and a test that asserts every mapped spec and widening target
exists. The agent never hand-picks tests when such a command exists.

## Side-effect discovery (run in this order, record what each step added)

1. **Import graph.** The test runner's related/changed mode finds tests that statically
   import the changed files. It cannot see dynamic imports, fixtures read from disk,
   SQL, prompts, JSON catalogs or templates: those are the widening triggers.
2. **Consumers of changed exports.** For every removed, renamed or re-typed export
   (`git diff -U0 | grep '^-export'`), grep its name across the repo; add the callers'
   tests. Typechecking the *dependents* of the touched package catches the typed half.
3. **Route → journey map.** A path prefix (page, route handler, shared layout, shared
   component library) maps to the E2E specs that drive it; the smoke spec is always in.
   A touched route with no row is a finding: add the row in the same commit.
4. **Widening triggers are rules, not judgement.** A change under contracts/schemas,
   migrations, auth/session/tenancy, env/config schema, build or CI config, prompts,
   fixtures or copy catalogs widens to a named set (all contract tests, all DB suites,
   the auth/isolation journeys, the mock evals, the copy audits). Encode the set in the
   command so the widening does not depend on who runs it.
5. **Widen on uncertain coverage.** Include deletions, renames and untracked files;
   use the integration merge base for branch work. Unknown paths, dynamic consumers,
   a stale map or an unexpectedly empty selected set require a broader check.
   A known documentation-only path may use static checks if executable consumers
   are ruled out; required gates still apply.
6. **State what did not run.** The report lists the tier, every command with its exit
   code and counts, and actual omitted checks with reasons. Never label a completed
   required gate as skipped merely because the tier normally omits it.

## Goodhart guard

When a measure becomes a target it stops measuring (Goodhart; Campbell). An agent
rewarded for "green" will narrow the selection; these rules keep the proxy honest.

- **Green is the proxy; behaviour is the goal.** After the selected run passes, make one
  observation of the touched journey in the real runtime: open the page, run the CLI,
  read the job log, compare the screenshot. Verification by re-deriving, not by
  recognising the exit code.
- **Never shrink to pass.** No deleting, skipping or loosening a test, no narrowing a map
  row or a widening rule, no "docs-only" classification for a file that code reads.
  A map or rule changes only to widen, or in a commit whose subject says what it narrows
  and why, with the evidence.
- **Misses are data.** Every T2/T3 failure on a change a lower tier passed is logged as a
  Trap (open) with the fix being a new map row or widening rule, landed with the code fix.
  Watch the miss count, not just the run time; a rising miss count means the map is stale.
- **Reviewer checks the tier, not just the diff.** The reviewer confirms the claimed tier
  matches the touched paths (did a migration really get the DB widening?) and re-runs the
  T1 command on the integrated tree before the deploy gate.
- **Full runs stay full.** The deploy gate and the schedule never adopt selection; they are
  the oracle that makes selection safe to use everywhere else.

## Setting a project up

1. Add one script: changed files (diff against a ref + untracked) → plan (typecheck
   filters, lint list, related-test list, widening steps, mapped specs) → run, or print
   with `--list`. Default ref = HEAD (uncommitted work); `--since <ref>` for a commit.
2. Put the route map and widening table in that script; test that every target exists.
3. Run independent read-only checks concurrently when resources permit. Route heavy
   or state-sharing steps through the project's lock/queue; isolate DBs, ports and
   output paths before parallel E2E.
4. Make the full suite run off the dev host on every push (CI) and at the deploy gate.
5. Propose tiers in the canonical testing standard. Change required merge gates only
   within an authorized policy change, supported by measured selection coverage.

## Synthetic example

A fix to `packages/core/pricing/round.ts`. T0: typecheck `core` and its dependents
`web` and `worker`, lint 1 file, `vitest related` finds 4 suites (2 s). The export
`roundMinor` was renamed, so step 2 greps it: one caller in `apps/web/lib/cost.ts`
with its own test, added. No route touched, no widening trigger: T1 = T0 + smoke spec.
Behaviour check: the price on the one page that shows minor units reads 12,50 €
after the change. Report: "T1, 5 suites 41 tests, smoke 6/6, exit 0 ×4; not run: full
gate, full E2E (deploy gate)". The nightly full run passes; had it failed on a template
snapshot, the miss would add a `templates/` → pixel-test widening rule.

## Sources (read 2026-10-04)

- Memon et al., "Taming Google-Scale Continuous Testing", ICSE 2017 — few tests ever
  fail, and those sit close to the changed code; frequently modified code breaks more.
  https://research.google/pubs/taming-google-scale-continuous-testing/
- Meta Engineering, "Predictive test selection" (2018-11-21) — runs about a third of the
  transitively dependent tests and catches over 99.9 % of regressions; retrains on recent
  outcomes. https://engineering.fb.com/2018/11/21/developer-tools/predictive-test-selection/
- Paul Hammant, "The Rise of Test Impact Analysis" (martinfowler.com, 2017-08-22) — subset
  pre-integration, full suite nightly or before release; misses are the cost to manage.
  https://martinfowler.com/articles/rise-test-impact-analysis.html
- Ham Vocke, "The Practical Test Pyramid" (martinfowler.com, 2018-02-26) — keep E2E to the
  high-value journeys, run them late in the pipeline, push checks down the pyramid.
  https://martinfowler.com/articles/practical-test-pyramid.html
- Goodhart's law (Strathern's phrasing) and Campbell's law.
  https://en.wikipedia.org/wiki/Goodhart%27s_law
- Anthropic, Claude Code best practices, "Give Claude a way to verify its work" and
  "The trust-then-verify gap" — a check the agent can run, evidence over assertion, a
  fresh reviewer that did not write the code. https://code.claude.com/docs/en/best-practices
- Vitest CLI, `vitest related` and `--changed` (static imports only).
  https://vitest.dev/guide/cli.html · Turborepo `--filter=...[ref]` / `--affected`.
  https://turborepo.dev/docs/reference/run
