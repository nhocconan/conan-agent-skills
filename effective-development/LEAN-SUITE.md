# Keep the suite lean

A test costs every future run; it earns its place only by catching a plausible wrong
result that no cheaper or existing check catches. Trim at the point of entry, not in
a rescue audit.

- **Writing a test (builder).** Its title names the regression it catches (behavior,
  invariant or incident id). Never add: log/console call counts, non-contract wording,
  source greps that a function is called (an `audit:*` script owns static facts),
  counts or lengths of registries that only grow, a helper checked against itself,
  expected values computed by the subject, a mock-only test, near-identical cases as
  separate tests (one table loop that names the failing row), a slow test whose
  fast twin already proves it, or fixed sleeps (`waitForTimeout`, `sleep`) or `isVisible()`
  branching in place of a web-first assertion. Put this list in every builder brief.
- **Review (merge gate).** The reviewer reads the test diff as code: one finding per
  slop test with its delete-or-merge fix; a test diff that grows the suite without a
  new failure mode is a finding. Test-count/suite-time growth above the repository's
  baseline needs each new test's failure mode named, else it goes.
- **A test-only failure in a gate.** If a gate fails only on a test that pins incidental
  output, delete or rewrite that test and rerun only its file, never the whole gate.
- **Periodic.** When summed suite time or test count grows past the repository threshold
  since the last trim (or the scheduled audit comes up), run one trim pass:
  [`slop_audit.py`](scripts/slop_audit.py) `--paths <tests>` and the lint rules `jest/expect-expect`,
  `jest/valid-title`, `jest/no-identical-title` (ruff `PT` for Python) first, slowest files
  next, one editor per area, serialized runs. Keep tenancy, money, auth, routing, migrations, invariants and every recorded
  incident check. Turn each recurring slop pattern into a static audit
  ([bug-class-audits](../bug-class-audits/SKILL.md)) so the next one fails at commit.
- **Enforce at commit.** Copy [`slop_audit.py`](scripts/slop_audit.py) to the project's
  `scripts/audit/` and run `--base <merge-base>` in the pre-push hook (it judges added lines
  only, so existing debt never blocks); wire it per bug-class-audits steps 4-5.
- **Test-value proof in a trim pass.** Mutation testing on the changed files only
  (`stryker --incremental --mutate <files>`); a surviving mutant on a line the suite claims
  to cover is a finding; never a repo-wide score gate.

## Recipes and measurement

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

Test-design references (read 2026-11-07): [12 test desiderata](https://testdesiderata.com)
(undated; structure-insensitive and behavioral are the two this file enforces),
[SWE book ch.12](https://abseil.io/resources/swe-book/html/ch12.html) (brittle and interaction
tests), [diff-only mutation testing](https://arxiv.org/abs/2102.11378),
[mutation-guided test generation](https://arxiv.org/abs/2501.12862),
[SWE mutation study](https://arxiv.org/abs/2605.22175).

Procedure comparison (read 2026-10-12): pstack `tdd`, `principle-test-behavior-not-implementation`,
`create-verification-skill` and `maintain-verification-skill`, pinned at
[1b6d44f](https://github.com/cursor/plugins/tree/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/skills).
Adapted to existing maps and repository authority; no upstream installation required.
