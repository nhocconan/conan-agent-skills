---
name: admin-crud-standards
description: >-
  Baseline for admin, back-office and CRUD surfaces. Use when building or
  reviewing a management screen, admin list view, record add/edit form, bulk
  data-upload flow, or an ops console — pagination, filters, search, type-ahead
  pickers, destructive-action confirms, upload preview, consistent tables.
  Scope is the admin surface, not end-user or marketing UI.
---

# Admin / CRUD Page Standards

These are the recurring gaps that turn a "finished" management UI into a pile of follow-up bug reports. Treat them as part of the definition of done for ANY management UI — apply without being asked.

## Every list page
- **Pagination** (consistent items-per-page across the whole site — pick one, e.g. 20, use it everywhere), **search**, and **filters** (by category/status/department/whatever the domain has). Filters must affect every component on the page.
- Consistent table style site-wide: same table component, same pagination control, same export/filter affordance placement.
- Counts/aggregates shown on a row (e.g. "Enrolled: 12") must be clickable, drilling into the underlying list.
- Preserve meaningful zero/empty records; hide them only under an explicit, visible filter. Remove dead columns and debug footers.

## Forms & pickers
- Add/Edit forms open on demand (modal/route) — never permanently expanded eating the list screen.
- Any select with potentially many options → **type-ahead/searchable combobox**, grouped by category. Never a raw 100-item dropdown.
- Hierarchical data (departments, org trees, categories) → tree picker, with parent selection implying children.
- Colors → color picker, never free-text hex. Dates → proper date picker.
- Non-obvious inputs get a (?) tooltip explaining meaning and effect — instant on hover, not delayed.
- Validation/block messages must be visible; a silently blocked action is a bug.

## Destructive actions
- Always a confirm dialog stating the consequences (cascade effects spelled out).
- High-stakes deletes (users with history, datasets): require re-typing the identifier/email to confirm.
- Deleting a parent cleans up its orphans (files, jobs, history entries) — say what gets removed.

## Upload flows
- Provide downloadable sample/template files matching exact expected columns.
- Flow: upload → parse → **preview table with problems highlighted** (unmapped/invalid cells) → user edits or accepts → only then commit to the system. Allow discard, which removes the file and all traces.
- Uploads of different data types get separate, labeled entry points near the data they belong to (admin data in admin, operator data in operator pages).
- Must handle large files (hundreds of thousands of rows): stream/queue, progress feedback, no timeouts.

Bulk deletes, uploads and connector actions require the active org/tenant: see [tenant-scope-integrity](../tenant-scope-integrity/SKILL.md). UI changes still run the [frontend-design](../frontend-design/SKILL.md) loop.

## Reachability
Every feature must be reachable by clicking from a menu — if it exists only as a URL or API, it doesn't exist. New admin pages get menu entries, gated to the right roles.

## Operational actions belong in the admin UI, not in a growing pile of scripts
- **Self-service parameters.** Expose what the script took as argv (org/tenant, connector, period from-to); "re-run everything" is a fallback.
- **Tenant config lives in the product** (form + **Test connection**), not in `.env`.
- **Long jobs are jobs**: queued, with visible status, progress, and history — not a request that hangs. Failures name the failing unit and are re-runnable for that unit alone.
- **Production migrations follow the release procedure** (locking, compatibility, recovery), never automatic for convenience; an operation needing a person to inspect each record was moved, not automated.
- **Dry-run / preview before commit** for anything that writes at scale, and an audit trail of who ran what with which parameters.
- Health/status pages must reflect reality: a connector shown green must have actually succeeded recently, and a stored error is rendered as human copy, never a raw stack trace or validation dump.

## Accessibility floor (non-negotiable, every management screen)
`a11y-audit` owns the checklist and is the gate: run it before calling any management
screen done. The one rule admin surfaces add: a sortable column header is a `<button>`
inside the `<th>`, and the `<th>` carries `aria-sort` (`ascending`/`descending`/`none`)
reflecting current state. A plain `<div>` with a chevron announces nothing.
