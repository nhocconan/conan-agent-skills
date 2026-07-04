---
name: metric-integrity
description: Correctness audit for every number a product displays — KPIs, dashboards, reports, charts, exports. Hunts fabricated values (hardcoded multipliers, fake denominators), formula drift between frontend/backend/recon, filters that don't reach every query, timezone-wrong date bucketing, and locale-inconsistent formatting. Use when building or reviewing any dashboard/report/metric, when numbers differ between pages, when the user says "số liệu sai", "fake number", "the KPI looks wrong", or before demoing a BI surface. A dashboard is a promise — a wrong number is worse than no number.
---

# Metric Integrity

A dashboard tells the operator "this is what your business looks like." A fabricated or
mis-scoped number turns it into a confident lie — and operators discover it at the worst
moment (a demo, a board meeting, a trading decision). These are the recurring classes of
metric bugs; check every one when touching any surface that renders numbers.

## 1. Never fabricate (the cardinal rule)

- **No hardcoded fractional multipliers on money columns.** `cost = revenue * 0.35`,
  `target = actual * 1.06` — unless the coefficient comes from a real, citable source
  (config table, budget plan, documented formula), it is fabrication. Grep any router/
  procedure for `* 0.` and `* 1.` against money variables; each hit needs a source or
  a same-line justification comment.
- **Missing data renders as `—`, never as a plausible number.** If a tenant structurally
  lacks the inputs (no cost data, no ad spend), return a `mode` discriminator in the
  payload and let the client render the honest empty state — not `0.0%`, not a
  placeholder average.
- **Check denominators before dividing.** A syntactically valid `GMV / 0 → 0.0%` shipped
  as an authoritative ROAS is the classic form. If the denominator can be structurally
  zero for some tenant, that's a `mode`, not a division.
- **Absence of data ≠ a negative fact.** Zero snapshots of the customer's catalog must
  not render as "not selling this product" — hide the column when the input dataset is
  empty instead of asserting a false negative.

## 2. One source of truth per formula

- Before implementing any domain metric, **read the canonical formula document** (PRD,
  formula reference, the customer's workbook). If none exists, write one and cite the
  source of each rule — the formula doc is what makes the number auditable later.
- **Shared math lives in ONE module.** When frontend, backend, and reconciliation script
  each reimplement the same period-comparison / label / allocation logic, they WILL
  drift. Extract to a shared package and add a check that compares their outputs.
- **Derived breakdowns allocate the canonical total** — a line-grain breakdown must sum
  back to the same canonical column the headline uses (allocate it), never recompute
  `qty × unit_price` and hope it matches.
- Per-platform/per-source differences (column semantics, pre- vs post-subsidy, net vs
  gross) are **explicit contracts in code**, not heuristics. Source columns that differ
  only by capitalization or position are a known trap — pin them by documented meaning.

## 3. Filters reach everything

A global filter (platform, date range, org, brand) must affect **every query block and
every component on the page**. The classic failure: the page has 8 SQL blocks, 6 honor
`?platforms=`, 2 don't — the operator sees a "Shopee" chip over all-platform data.
When adding any new query to a filtered page, check the filter plumbs through; where the
codebase allows, write a mechanical audit that lists query blocks missing the filter
condition (see `bug-class-audits`).

## 4. Time is a business-timezone concept

- **Never bucket with bare `date_trunc`** / naive UTC day-slicing when the business runs
  in a non-UTC timezone — orders placed after 5pm land in tomorrow's bucket. Always
  `AT TIME ZONE '<business tz>'` (or the equivalent) at the bucketing site, and rebuild
  rollups after fixing.
- Date **labels** go through one shared helper too — `timestamp.slice(0, 10)` on a UTC
  ISO string and `::date` casts leak adjacent days at the edges.
- Comparisons anchor to real complete periods (full month vs full month) — never quietly
  compare a partial week to a full one.

## 5. Formatting is part of correctness

- Numbers/dates format through shared locale-aware helpers, never raw `toFixed()` for
  display — in a `vi-VN` product, `639.6` next to `1.305` uses the same dot for two
  different meanings. Money gets the product's one canonical short-format.
- The same metric shows the same value and the same label on every page that displays it.
  When pages disagree, treat it as a data bug until proven a caching artifact.

## 6. Verify like an operator

- After any metric change, **open the real page** and cross-check 2–3 values against a
  direct DB/source query. Static gates (typecheck, unit tests) don't catch a wrong
  number that renders confidently.
- Sanity-scan for impossible values: totals below a known floor, 100% attach rates,
  growth that implies the company 10×'d in a week. Impossible numbers are bugs even in
  demo data.
- When a metric bug turns out to be a *class* (multiple sites), escalate to
  `bug-class-audits`: fix all sites, record the rule, wire a mechanical audit.

## Output

Report per finding: metric → page/component → what's wrong (fabrication / drift / filter
gap / TZ / locale) → root cause → fix. Fix what's safe; anything needing a business
decision (which formula is canonical, what the empty state should say) goes to the user
as a short decision list.
