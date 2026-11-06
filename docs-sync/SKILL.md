---
name: docs-sync
description: >-
  Use after shipping features, when the user says docs are outdated, "update
  documents", or asks for a user guide / "hướng dẫn người dùng". Keeps project
  documentation in sync with shipped reality — PRD, user manual, decision log,
  business-rule/formula reference, in-app docs routes, diagrams.
---

# Docs Sync

Update the requested documents against current code and the reader's actual workflow.

## Document set (per project)
- **PRD** — describes the CURRENT shipped product. No changelogs inside the PRD (that's git's job). Diagrams over walls of text.
- **USER-MANUAL** — written for the actual end user (often non-technical staff), screen-by-screen with real screenshots, no internal jargon — explain in plain words what the user does and sees. Write it in the users' language, not necessarily English.
- **Decision log** (`docs/DECISIONS.md` or existing equivalent) — technology/stack/architecture decisions with date and rationale (e.g. SDK vs direct API call). Append, never rewrite history.
- **Business-rule / formula reference** when the domain has non-obvious rules — cite the source of each rule so it can be re-verified.
- Audit/review docs (security, performance): mark items `[x]` as completed so work can resume after a context reset; mark superseded audits clearly; preserve required history and evidence.

## Delivery format
- Match the repository's documentation format and intended audience. Add styled HTML
  or an in-app route only when requested or already part of the product; engineering
  docs usually remain Markdown.
- Diagrams: use the repo's existing diagram tool. If mermaid, validate it renders — escape `<br/>` and special chars that break the parser.
- Sample/template files referenced by guides must actually exist and be downloadable from the page that mentions them.

## Where an artifact is allowed to land
- `docs/` is shipped documentation only. Agent working artifacts (evaluations, plans, handoffs, audit scratch) go to one gitignored path declared in the repo's agent rulebook.
- Supersede, don't accumulate: mark a replaced handoff superseded or consolidate it without losing required history.
- Register each folder's audience: shipped docs use the reader's language and product voice; working notes use the operator's register.

## Process
0. **Establish the latest system state before writing a word.** Read the commits since the
   doc was last verified (`git log --since=<last-verified>`), the code/config the doc
   describes, and the running system (app, read-only prod queries, deployed URLs) for
   user-visible behaviour. Never update a doc from its own old text, a plan, or memory;
   a plan is design direction and must be labelled as such. Record what you read
   (commit hash, paths, screens) in the change record: commit message, PR body or the
   project's docs-maintenance log, or a non-rendered metadata field only where the
   project's doc convention already has one. Reader-facing copy carries no process
   trace (`anti-slop-review`, process stamps).
1. Read the docs index first; update the canonical topic document. New files need a
   distinct topic/audience. Link shared rules; repair links when consolidating. Keep
   catalogs in references and task state in ignored notes, not always-loaded rulebooks.
2. Trace claims about capabilities, counts and architecture to current code/config or
   a dated source. Distinguish implemented behavior from design direction.
3. Update the user's path through the product, including setup, permissions and where
   each action lives. For served docs, verify the deployed version, links, TOC, scrolling
   and diagram layout at desktop and narrow widths; a Markdown render alone is insufficient.
4. Run `anti-slop-review` on the result — docs are content too.
