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
signals, not proof of AI authorship or automatic defects; interpret them in context
and document intentional exceptions.

**Formatting slop.** Check layout, not only words. Signs that a draft is unedited
model output: a line break after every sentence; bullets for reasoning that should
be a paragraph, each item an "**Label:** clause"; more than one bold phrase per
paragraph; a heading or emoji over a two-sentence section; Title Case in Vietnamese
headings; "Dưới đây là…", "Hy vọng… hữu ích", "Would you like…" left in the text.
Fix by grouping sentences into 2-3 sentence paragraphs, keeping lists only for real
lists (prices, steps, dates), and deleting chat leftovers. A list is legitimate when
each item carries a fact or a term being defined.

**Negative parallelism.** "Không chỉ… mà còn", "không chỉ là… mà là", "not just X
but Y", "it's not X, it's Y": state the positive claim once. Search for the pattern
explicitly; readers name it as the first AI tell.

**Signs age.** Em dashes, "delve", emoji headings and cutoff disclaimers were strong
tells in 2023-2025 and are fading in 2026 output; absence proves nothing, presence is
an edit cue. Judge by information density first: can each sentence be pointed at a
fact? Vietnamese phrase lists are practitioner observation, not research — house
style, never evidence of authorship.

**Process stamps (owner rule).** Reader copy carries no trace of the checking workflow: no "kiểm 28/09/2026" / "checked Sep 28, 2026" stamps, no "(quan sát thực tế)" or "(weak sign)" labels, no source lines that list everything consulted, no caveat repeated in every table row. Keep a date only when the date is the fact. Cite only the sources the reader can open that carry the claim.

Sign catalogue with verbatim quotes, source status, the Vietnamese phrase lists and which signs are fading: `references/sources.md`. Read it before teaching or auditing slop. Mechanical checks in `interactive-course-builder/scripts/validate_course.py` (if that skill is present) are house heuristics, not proof.

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
