---
name: docs-sync
description: Keep project documentation in sync with shipped reality — PRD, user manual, decision log, business-rule/formula reference, in-app docs routes, diagrams. Use after shipping features, when the user says docs are outdated, "update documents", or asks for a user guide.
---

# Docs Sync

Every project drifts: the PRD describes the old version, the user manual misses new screens, decisions live only in chat. Produce the same dependable doc shape without being asked.

## Document set (per project)
- **PRD** — describes the CURRENT shipped product. No changelogs inside the PRD (that's git's job). Diagrams over walls of text.
- **USER-MANUAL** — written for the actual end user (often non-technical staff), screen-by-screen with real screenshots, no internal jargon — explain in plain words what the user does and sees. Write it in the users' language, not necessarily English.
- **Decision log** (`docs/DECISIONS.md` or existing equivalent) — technology/stack/architecture decisions with date and rationale (e.g. SDK vs direct API call). Append, never rewrite history.
- **Business-rule / formula reference** when the domain has non-obvious rules — cite the source of each rule so it can be re-verified.
- Audit/review docs (security, performance): mark items ✅ as completed so work can resume after a context reset; merge superseded audits into one current file and delete stale ones.

## Delivery format
- User-facing docs (manual, PRD) as **styled HTML** matching the product's design, with collapsible sections, wired to an in-app docs route when the product has one. Engineering docs (coding standards, DoD, CLAUDE.md/AGENTS.md) stay **markdown** — they're for agents, keep them token-lean.
- Diagrams: prefer **excalidraw** (render to SVG/PNG embedded in the HTML). If mermaid is used (e.g. on GitHub), validate it renders — escape `<br/>` and special chars that break the parser.
- Sample/template files referenced by guides must actually exist and be downloadable from the page that mentions them.

## Process
1. Diff docs against shipped reality (routes, menus, features, rules) — list every stale claim.
2. Update; if docs are served in-app, verify the route renders the new version.
3. Run `anti-slop-review` on the result — docs are content too.
4. Keep CLAUDE.md/AGENTS.md concise; when a rule is added there, cross-reference instead of duplicating.
