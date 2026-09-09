---
name: anti-slop-review
description: >-
  Review factual claims, clarity, and unnecessary filler in courses, docs,
  announcements, UI copy, and marketing text. Use for fact checking, "AI slop",
  "đừng bịa", or a publication review. Preserve the author's voice and intent.
---

# Content review

Check accuracy first, then edit for clarity. Match the audience, language, and
requested review mode. A review alone produces findings; apply edits when requested.

## Claims and sources

- Verify consequential or time-sensitive numbers, dates, prices, comparisons, and
  product claims against current primary sources. Stable internal facts may use
  supplied evidence; do not send private claims to public search.
- A citation must support its nearby claim. Check public links before publication.
  Label unavailable evidence and hypothetical examples; never invent details.
- Comparisons need compatible methods, populations, dates, and units. State when
  sources cannot support a fair ranking.
- Keep useful provenance, limitations, and uncertainty visible. Do not delete a
  chart's source or a missing-data explanation merely because it sounds technical.

## Clarity and voice

Remove empty superlatives, heading paraphrases, repetitive intros, decorative
statistics, and padding that adds no information. Prefer concrete verbs and
examples. Preserve legitimate definitions, technical terms, quotations, and the
author's chosen style.

Repeated em dashes, triads, intensifiers, and formulaic transitions are editing
signals, not proof of AI authorship or automatic defects. Mechanical prose checks
in `interactive-course-builder/scripts/validate_course.py` are house-style
heuristics; interpret them in context and document intentional exceptions.

For Vietnamese, proofread diacritics and natural phrasing. Use the audience's
established technical vocabulary; do not impose one translation on every context.

## Educational content

Check that examples teach the stated objective and analogies do not mislead.
Explain an analogy's limits when they affect understanding. Keep prerequisites
and difficulty consistent. Use scenarios, definitions, quizzes, and visuals where
they teach something; do not force every section into one template.

## Publication and handoff

Keep author attribution unchanged. Remove secrets and unintended private context
before publication; retain names and facts the author explicitly intends to publish.
Summarize material factual corrections with sources, editing decisions, and
unresolved claims. Do not claim content is error-free or that style metrics
establish truth, authorship, or publication readiness.
