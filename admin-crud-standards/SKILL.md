---
name: admin-crud-standards
description: Non-negotiable baseline for every admin/list/CRUD/upload page. Use when building or reviewing any management screen, list view, form, or data-upload flow — pagination, filters, search, type-ahead pickers, destructive-action confirms, consistent tables. Apply proactively; the user should never have to ask for these again.
---

# Admin / CRUD Page Standards

These are the recurring gaps that turn a "finished" management UI into a pile of follow-up bug reports. Treat them as part of the definition of done for ANY management UI — apply without being asked.

## Every list page
- **Pagination** (consistent items-per-page across the whole site — pick one, e.g. 20, use it everywhere), **search**, and **filters** (by category/status/department/whatever the domain has). Filters must affect every component on the page.
- Consistent table style site-wide: same table component, same pagination control, same export/filter affordance placement.
- Counts/aggregates shown on a row (e.g. "Enrolled: 12") must be clickable, drilling into the underlying list.
- No useless rows: hide zero/empty entries; no dead columns; no debug/AI-explanation footers.

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

## Reachability
Every feature must be reachable by clicking from a menu — if it exists only as a URL or API, it doesn't exist. New admin pages get menu entries, gated to the right roles.

## Implementation patterns (modern stack)
- **Tables/grids**: use a headless data-grid (e.g. TanStack Table v8) so sorting/filtering/column-visibility/row-selection are state you control, not bespoke per page. One shared table component site-wide (see consistency rule above).
- **Large datasets**: server-side pagination/sort/filter for the source of truth; **virtualize** rendered rows (TanStack Virtual / react-window) — never put 10k+ DOM rows on screen. For the big-file uploads above, stream/queue server-side and show progress; the preview table virtualizes too.
- **Pickers**: combobox/tree built on an accessible primitive (Radix, React Aria, shadcn/ui) — you get keyboard nav and ARIA for free instead of hand-rolling a broken dropdown.

## Accessibility floor (non-negotiable, every management screen)
These ship broken constantly on admin UIs — bake them in, don't bolt on later:
- Tables use real `<table>` semantics (or grid roles); sortable headers are `<button>`s announcing sort state (`aria-sort`).
- Every form input has an associated `<label>`; validation errors are visible, tied to the field, and say how to fix.
- Full keyboard operability: tab order is logical, focus is always visible, modals trap focus and restore it on close, `Esc` closes overlays.
- Status/required/selection never conveyed by color alone; contrast holds in both light and dark themes.
- Run `a11y-audit` before calling any management screen done.
