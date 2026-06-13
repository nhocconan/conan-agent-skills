---
name: anti-slop-review
description: Fact-check and de-slop written content — courses, docs, announcements, UI copy, marketing text, README/landing copy. Use when reviewing or producing any user-facing prose, when the user says "AI slop", "fact check", "don't make things up" / "đừng bịa", or before publishing anything containing claims, numbers, benchmarks, or links.
---

# Anti-Slop Content Review

Published content carries the author's name. Fabricated facts and AI-flavored filler are the two failure modes that embarrass them. Verify every claim; cut every empty phrase. Apply this to anything prose-like before calling it done.

## Fact-checking (hard rules)
- **Every number, benchmark, date, price, and product claim must be verified against a live source** at review time. If a source is blocked, open a real browser session and read it — including images/charts on the page. Never carry numbers from memory or training data.
- Every reference link must be alive and actually contain the cited claim. Remove or replace dead/irrelevant links.
- When comparing items, use the latest numbers from the SAME independent source for all of them (fairness). If a benchmark hasn't updated, say so rather than inventing newer figures.
- Never invent concrete details: channel names, team practices, durations ("25 min"), statistics, example companies. If an example is hypothetical, it must read as hypothetical.

## De-slop checklist (delete on sight)
- Time estimates per lesson/section; "New!" badges; breathless intro paragraphs recapping the entire industry.
- Footer/caption explanations of where a chart's data was queried from.
- Apologetic placeholder text ("no official formula yet — showing —").
- Pairs of disconnected hype sentences ("You're all set!" / "Become a power user").
- Overclaiming: "world-class", "best-in-class", superlatives without evidence.
- Walls of bullet padding that restate the heading.
- Em-dash-and-triad rhythm, "it's not just X, it's Y", and other tells of unedited model output.

## Language & readability
- Proofread for real spelling errors and tone consistency in whatever language the content is in. For non-English content, watch for the homophone/diacritic mistakes native readers notice instantly.
- Match the content's existing language; keep technical terms in their conventional form (often English) where that reads naturally.
- Short, direct sentences. Guides should be scannable: headings, numbered steps, one idea per bullet.

## Publishing hygiene
- Content going public must be anonymized: no internal company/employee names, internal URLs, or credentials.
- Keep authorship/footer attribution exactly as the author set it — don't "improve" it.

## Output
Report as: list of removed slop (with before-text), list of corrected facts (claim → verified value → source URL), list of items needing the author's confirmation. Then apply fixes.
