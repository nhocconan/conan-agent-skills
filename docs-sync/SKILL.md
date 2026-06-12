---
name: docs-sync
description: Keep project documentation in sync with shipped reality — PRD, Vietnamese user manual, formula/decision docs, in-app /prd and /manual routes, excalidraw diagrams. Use after shipping features, when the user says docs are outdated, "update documents", or asks for a user guide.
---

# Docs Sync

Every project drifts: PRD describes the old version, the user manual misses new screens, decisions live only in chat. The user repeatedly asks for the same doc shape — produce it without being asked.

## Document set (per project)
- **PRD** — describes the CURRENT shipped product. No changelogs inside the PRD (that's git's job). Diagrams over walls of text.
- **USER-MANUAL** — in **Vietnamese**, written for non-technical internal staff, screen-by-screen with real screenshots, no jargon (no "Data Warehouse", "medallion", "stream chuẩn" — explain in plain words what the user does and sees).
- **Decision log** (`docs/DECISIONS.md` or existing equivalent) — technology/stack/architecture decisions with date and rationale (e.g. SDK vs direct API call). Append, never rewrite history.
- **Formula/business-rule reference** when the domain has customer formulas (see `excel-data-reconcile`).
- Audit/review docs (security, performance): mark items ✅ as completed so work can resume after token/context limits; merge superseded audits into one current file and delete stale ones.

## Delivery format
- User-facing docs (manual, PRD) as **styled HTML** matching the product's design, with collapsible sections, wired to in-app routes `/prd` and `/manual`. Engineering docs (coding standards, DoD, CLAUDE.md) stay **markdown** — they're for agents, keep them token-lean.
- Diagrams: prefer **excalidraw** (render to SVG/PNG embedded in the HTML). If mermaid is used (e.g. GitHub), validate it renders — escape `<br/>` and special chars that break the parser.
- Sample/template files referenced by guides must actually exist and be downloadable from the page that mentions them.

## Process
1. Diff docs against shipped reality (routes, menus, features, formulas) — list every stale claim.
2. Update; verify in-app routes render the new version.
3. Run `anti-slop-review` on the result — docs are content too.
4. Keep CLAUDE.md/AGENTS.md concise; when a rule is added there (e.g. deploy rules), cross-reference instead of duplicating.
