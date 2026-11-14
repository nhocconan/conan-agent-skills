---
mode: wrap
source: github:vercel-labs/web-interface-guidelines@434b7f91364665f2f733b310ec54809bf8f37937:README.md
tracking_source: github:vercel-labs/web-interface-guidelines@main:README.md
version: 1.0.0
fingerprint: sha256:eda7dfa9998215267c7f920475d1773ea4129cb08ed088276ca598dd45d20aa5
secondary_source: github:GoogleChrome/modern-web-guidance-src@ebb6f3aaae8652dd8938c8496e2809bc408ab986:guides/modern-web-guidance/SKILL.md
secondary_tracking_source: github:GoogleChrome/modern-web-guidance-src@main:guides/modern-web-guidance/SKILL.md
secondary_fingerprint: sha256:ecdcab8472644b2715dd1173b41b39c9630c40e2e19fdd6a8f7dc28f699700f7
reviewed: 2026-11-14
---

# Provenance

A distilled standard, not a copy. Two upstreams were read as untrusted reference data; nothing
from them is vendored into the skill body, and nothing is fetched while an agent does product
work. `refsync.py status` watches one file per upstream for drift
([sections/refresh.md](sections/refresh.md)).

## Why this exists

The house UI skills judged how a screen looks; nothing stated the platform rules for the code
behind it, and two actively maintained public sources do. Their native agent integrations do
not fit: Chrome's skill retrieves guides through a live `npx` CLI from a 252-guide corpus
(about 470k tokens) and requires a disclosure block in every reply; Vercel's review skill
fetches its rule file from `main` at review time. A short, pinned, project-subordinate
distillation does.

## Panel verdict (2026-11-14)

| Source | Pin | Licence | Verdict |
|---|---|---|---|
| Chrome Modern Web Guidance (`GoogleChrome/modern-web-guidance-src`) | `ebb6f3aa` (2026-11-13) | Apache-2.0 | Distilled: Baseline support rule, IME-safe Enter, input hints, focus and forced colours, overlay rules, loading and live-region rules, LCP/INP recipes, `color-scheme`. |
| Vercel Web Interface Guidelines (`vercel-labs/web-interface-guidelines`) | `434b7f91` (2026-10-05) | MIT | Distilled: touch and overscroll, no `transition: all`, hit areas, `scroll-margin-top`, `translate="no"`, unsaved-work guard. Copy rules (Title Case, curly quotes, English voice) and the APCA gate rejected. |
| Vercel UI SDK (`vercel-labs/ui`) | `724a7d6c` (2026-11-13) | Apache-2.0 | Not applicable: a behaviour library with its own skill, not guidance. |

Panel questions for any later rule: is it platform behaviour rather than copy style or a vendor
preference; does it hold across frameworks; does a project rule already cover or contradict it;
can a search, a test or a probe check it.

## Where the numbers come from

| Number in `SKILL.md` | Source |
|---|---|
| Loader show-delay 150-300 ms, minimum visible 300-500 ms | Vercel guidelines, "Interactions" (loading states) |
| Hit area 24px, 44px on touch-first screens | WCAG 2.2 SC 2.5.8 (24px, AA) and SC 2.5.5 (44px, AAA); Vercel "Interactions" |
| Handlers over 50 ms yield | Chrome guidance `performance` (long-task threshold) |
| One polite and one assertive live region | Chrome guidance `accessibility` (live regions) |

## Overrides that MUST survive an upgrade

1. A project's rulebook and design system outrank the baseline; a conflict is reported.
2. No number without a source; the browser-support default is labelled a default.
3. No remote fetch during product work and no mandatory reply block.
4. The "Not adopted" list stays in `SKILL.md` so a later import does not undo it.
5. The skill stays one screen of rules; depth lives upstream and is read at refresh time.

## Upstream sections this depends on

- "Interactions"
- "Animations"
- "Forms"
- "Performance"
- "Design"

## License notice (derived material)

Vercel Web Interface Guidelines: MIT License, copyright Vercel, Inc. Chrome Modern Web Guidance:
Apache License 2.0, copyright Google LLC. Rules here are paraphrased; no upstream text is
reproduced.
