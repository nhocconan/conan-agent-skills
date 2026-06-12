---
name: anti-slop-review
description: Fact-check and de-slop written content — courses, docs, announcements, UI copy, marketing text. Use when reviewing or producing any user-facing prose, when the user says "AI slop", "fact check", "đừng bịa", or before publishing content with claims, numbers, benchmarks, or links.
---

# Anti-Slop Content Review

The user publishes courses and docs under his own name; fabricated facts or AI-flavored filler get him publicly embarrassed. Every claim is checked. Apply this to anything prose-like before calling it done.

## Fact-checking (hard rules)
- **Every number, benchmark, date, price, and product claim must be verified against a live source** at review time. If a source is blocked, open a real browser session (browse skill) and read it — including images/charts on the page. Never carry numbers from memory or training data.
- Every reference link must be alive and actually contain the cited claim. Remove or replace dead/irrelevant links.
- Use the latest numbers from the SAME independent source for all compared items (fairness). If a benchmark hasn't updated, say so rather than inventing newer figures.
- Never invent concrete details: internal channel names, team practices, durations ("25 phút"), statistics, example companies. If an example is hypothetical, it must read as hypothetical.

## De-slop checklist (delete on sight)
- Time estimates per lesson/section; "New!" badges; breathless intro paragraphs recapping the entire industry.
- Footer/caption explanations of where a chart's data was queried from.
- Apologetic placeholder text ("chưa có công thức chính thức — hiển thị —").
- Pairs of disconnected hype sentences ("Bạn đã sẵn sàng" / "Power user AI tại YouNet").
- Overclaiming: "world-class", "đẳng cấp", superlatives without evidence.
- Walls of bullet padding that restate the heading.

## Vietnamese quality
- Proofread for real spelling errors (e.g. "độc giả" not "đọc giả") and tone consistency.
- Internal-tool docs and user guides are written in **Vietnamese** unless told otherwise; keep technical terms in English where natural.
- Short, direct sentences. Guides should be scannable: headings, numbered steps, one idea per bullet.

## Publishing hygiene
- Content going public must be anonymized: no internal company names, real employee names, internal URLs, or credentials. (Run `repo-hygiene-scrub` if it lives in a repo.)
- Keep authorship/footer attribution exactly as the user set it — don't "improve" it.

## Output
Report as: list of removed slop (with before-text), list of corrected facts (claim → verified value → source URL), list of items needing the user's confirmation. Then apply fixes.
