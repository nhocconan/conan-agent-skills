---
name: metric-integrity
description: >-
  Use when any number a product shows may be wrong or invented — KPIs, dashboards,
  reports, charts, exports, alert thresholds: "số liệu sai", "toàn bịa", "con số này
  lấy từ đâu", "fake number", "the KPI looks wrong", numbers differ between pages, or
  before demoing a BI surface. Hunts hardcoded multipliers and fake denominators,
  formula drift between frontend/backend/recon, filters that miss a query,
  timezone-wrong date bucketing, locale-inconsistent formatting; every threshold names
  its source.
---

# Metric Integrity

Check each class below when a surface renders numbers.

## 1. Never fabricate (the cardinal rule)

- **No hardcoded fractional multipliers on money columns, and no unsourced alert or target thresholds.** `cost = revenue * 0.35`,
  `target = actual * 1.06` — unless the coefficient comes from a real, citable source
  (config table, budget plan, documented formula), it is fabrication. Grep any router/
  procedure for `* 0.` and `* 1.` against money variables; each hit needs a source or
  a one-line source marker.
- **Missing data renders as `—`, never as a plausible number.** If a tenant structurally
  lacks the inputs (no cost data, no ad spend), return a `mode` discriminator in the
  payload and let the client render the honest empty state — not `0.0%`, not a
  placeholder average. Also not "not selling this product" when the input dataset
  (e.g. catalog snapshots) is empty: hide the column instead of asserting a false negative.
- **Check denominators before dividing.** A syntactically valid `GMV / 0 → 0.0%` shipped
  as an authoritative ROAS is the classic form. If the denominator can be structurally
  zero for some tenant, that's a `mode`, not a division.
- **Unresolved keys render explicitly.** When a name lookup misses, a numeric/opaque key
  in the name column (`9999999999999999999` as a product name) reads to the user as corrupted data, and it hides the real defect upstream: the
  ingest created rows whose foreign key resolves to nothing. Render the unresolved state
  explicitly (`— (unmapped: 12345…)`), surface a count of unresolved rows on the surface
  that owns the import, and fail or quarantine the ingest that produced them rather than
  letting each report re-discover the gap.

## 2. One source of truth per formula

- Before implementing any domain metric, **read the canonical formula document** (PRD,
  formula reference, customer workbook). If none exists, write a proposed contract citing
  each rule's source and take unresolved definitions to the owner.
- **Shared math lives in ONE module**, so one metric shows one value and label on every page
  (disagreement is a data bug until proven a caching artifact). When frontend, backend, and reconciliation script
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
`?platforms=`, 2 don't — the operator sees a "Marketplace A" chip over all-platform data.
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
- Compare complete periods only.

## 5. Formatting is part of correctness

- Numbers/dates format through shared locale-aware helpers, never raw `toFixed()` for
  display — in a `vi-VN` product, `639.6` next to `1.305` uses the same dot for two
  different meanings. Money gets the product's one canonical short-format.

## 6. Verify like an operator

- Sanity-scan for impossible values (total below a known floor, 100 % attach, 10× growth in a week), demo data included.

- After any metric change, **open the real page** and cross-check 2–3 values against a
  direct DB/source query. Static gates (typecheck, unit tests) don't catch a wrong
  number that renders confidently.
- When a metric bug turns out to be a *class* (multiple sites), escalate to
  `bug-class-audits`: fix all sites, record the rule, wire a mechanical audit.

## Output

Report per finding: metric → page/component → what's wrong (fabrication / drift / filter
gap / TZ / locale) → root cause → fix. Fix within an implementation request; report-only audits remain read-only. Anything needing a business
decision goes to the user as a short decision list.
