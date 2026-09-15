---
name: reference-parity
description: Rebuild something to match an existing artifact — a competitor's dashboard, a vendor deliverable, a legacy screen, a design comp, a report a client already receives — without discovering the missing half at review time. Extract the reference's complete inventory first (every tab, sub-tab, section, state and content type), turn it into a parity checklist that is the deliverable's definition of done, and verify row by row with evidence. Use for any port, migration, replication, redesign-to-match or "make ours like theirs" job, and when the user says "so sánh apple to apple", "giống bên kia", "match the reference", "port màn hình này", "parity", "vẫn thiếu", "vẫn chưa giống".
---

# Reference Parity

For reference-driven work, enumerate the agreed surfaces and states before building.
A description or landing screenshot rarely captures the complete target.

## Inventory the reference before writing anything

Inspect the actual file, live surface, export or recording. A summary or landing
screenshot is incomplete evidence. If the reference is unavailable, report the gap
before building and distinguish agreed assumptions from verified parity.

Enumerate exhaustively and mechanically. Depth is where the misses live:

- Every top-level surface, and inside each, every sub-surface: tabs, sub-tabs, accordions,
  drawers, modals, print/export views, drill-downs reached by clicking a row.
- Every distinct **content type**, listed separately from where it appears: metric tile,
  time series, ranked table, cohort grid, map, narrative commentary, footnote,
  methodology note, glossary, legend, filter bar, date-range control, export button.
- Every **state** by intended role: populated, empty, partial, loading, error and
  permission-denied. Exercise controls, keyboard actions, feedback and persistence
  after reload; visible content alone does not establish interaction parity.
- Every **input** that changes the output: filters, date ranges, comparison periods,
  segments, currency/locale, and which of them persist.
- Every **number**, with its label, unit, precision, and the period it covers — these are
  what the reviewer will actually compare.
- Ordering, grouping and hierarchy, which carry meaning the components alone do not.

Store the inventory as a table, one row per item, with its location in the reference. This
table *is* the spec; it outlives the session and is what a second agent or a later run
works from.

## Turn the inventory into a parity checklist

Add columns to each row: **status** (missing / partial / done), **evidence** (the artifact
proving it — a screenshot path, a test name, a query result, a line reference),
**decision** (match / deliberately differ / out of scope) and **why** for anything not
matched. Nothing is marked done without evidence; "implemented" is not evidence.

Deliberate differences are legitimate and must be *recorded as decisions*, not left as
silent gaps. "Their chart is a pie; ours is a bar because pies mislead at this cardinality"
is a decision the reviewer can accept or overturn. An unmentioned missing pie is a defect.

## Match structure before polish

Order of work, because it is the order the reviewer checks in:

1. **Coverage** — every surface and content type exists, even if rough. A reviewer who
   finds a missing tab stops reading; nothing after that gets evaluated.
2. **Content correctness** — the numbers, labels, units, periods and orderings agree with
   the reference. Where they disagree, the reference may be wrong; note the discrepancy for
   the operator to take up with its authors rather than quietly conforming to it or
   quietly ignoring it.
3. **Layout and hierarchy** — density, grouping, where the eye lands. A rebuild that
   contains everything but reorganises it is not parity, and this is the second-most-common
   complaint after missing surfaces.
4. **Polish** — typography, spacing, motion. Last, and never before 1–3 are green.

Do not report progress in terms of effort spent. Report it as the checklist fraction:
*38 of 51 rows done, 6 partial, 7 missing* — and name the missing ones.

## Verify against the reference, side by side

Compare the intended target URL/build as the same role, filters, date range, locale,
scope and zoom. Establish the served build/version before diagnosing stale output.
Go row by row: compare rendered states and exercise interactions;
for data, diff values. When delivery includes deployment, verify that deployed build,
not just localhost. Record unavailable roles or targets as unverified.

The reference is the oracle for agreed parity dimensions, not permission to copy private data or protected assets. Record deliberate differences required by accessibility, security, or correctness. Verifying the rebuild against your own re-derivation of what
the reference "should" say proves only that the rebuild agrees with itself.

## Orchestration for parity rebuilds
Use [agent-orchestration](../agent-orchestration/SKILL.md) for independent surfaces.
The harness lead owns inventory, seam contracts, and final parity review; the default
builder takes scoped views and the cheapest checked tier takes simple content. Keep
shared state changes serialized.

## Output

Deliver the parity table with every row resolved: done with evidence, deliberately
differing with a reason, or missing with what remains. Lead with the fraction and the list
of what is not yet matched. If the reference itself appears wrong or internally
inconsistent, say so separately — that is a finding for its owner, not a licence to
deviate.
