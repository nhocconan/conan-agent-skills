# E2E suites

Playwright docs read 2026-11-07. Launch mechanics:
[headless-server.md](../browsing-web/sections/headless-server.md); memory: [SHARED-HOST.md](SHARED-HOST.md).

## Layer
SWE book ch.11 sizes: small (no I/O), medium (localhost DB/API: route handlers, resolvers),
large (browser). Google's guideline: about 80/15/5 by count; every team's mix differs. A
large test carries one line saying why it cannot be medium; the browser is for journeys that
cross the UI boundary.

## Auth
One setup project per role writes `storageState` to gitignored `playwright/.auth`; projects
declare `dependencies`. Tests that mutate the user take one account per worker
(`testInfo.parallelIndex`). IndexedDB needs `indexedDB: true`; sessionStorage is never saved.

## State
Seed through the `request` fixture or a DB factory in fixtures, with unique ids per test and
cleanup through the same seam. Per-worker DB: `CREATE DATABASE ... TEMPLATE` from a migrated
template kept connection-free, or a rolled-back transaction. No UI-driven
setup, no shared mutable fixtures.

## Assertions
Role or test-id locators; web-first `expect`, no `waitForTimeout`, no `isVisible()` branching;
`toMatchAriaSnapshot` for structure; `toHaveScreenshot` only against a baseline from the same
renderer; third parties via `page.route` or HAR; time via `page.clock`.

## Config
`fullyParallel`; workers and shards from the conductor env; `retries: CI ? 1 : 0`,
`trace: 'on-first-retry'`, `forbidOnly: !!CI`; `webServer` runs `next start` with
`reuseExistingServer: !CI`. CI shards use the blob reporter, then `merge-reports` in a job
with `if: !cancelled()`.

## Selection
Writer tier: `--only-changed=<merge-base>` (git only; selects changed test files and those
importing a changed module; server code a test reaches over HTTP is invisible to it, so the
widening rules in SKILL.md still apply) and `--grep @smoke`. CI needs the base commit fetched:
a shallow checkout fails (use `filter: blob:none`, SETUP-TIME.md §4). Repair
loop: `--last-failed`. Full suite on merge and schedule only. An empty selection exits 0:
[SETUP-TIME.md](SETUP-TIME.md#3-test-the-skip-logic-itself).

## Flake
One rerun; an identical failure is a bug. A pass on retry is a finding, not a green
(`--fail-on-flaky-tests`). Move the test the same day to a non-gating quarantine project
with an owner and an exit criterion (passing for a set period); the list only shrinks.
`--shuffle` exposes order dependence. Near a 1 % flake rate a suite loses its value as a signal (SWE book ch.11).

## Component
Vitest + Testing Library (jsdom) for logic. Vitest browser mode (playwright provider; the
`preview` provider is not for CI) only when CSS or layout is the assertion.
