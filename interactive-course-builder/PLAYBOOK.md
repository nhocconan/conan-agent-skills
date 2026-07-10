# Course Authoring Playbook — the model-agnostic pipeline

> `reference.md` defines WHAT a house-standard course is. This file defines
> **HOW to build one so the result is the same no matter which model (or
> human) does the work.** The trick is never taste — it's sequence + artifacts
> + mechanical gates. Follow the phases in order; each phase produces a file
> the next phase consumes, so quality survives weak links and context resets.
>
> Written by Claude Fable 5 (2026-07) after building multi-module courses with
> parallel Opus builders. Every rule here paid for itself at least once.

## The one-line method

**Digest sources → contract before prose → build fragments → assemble by
script → validate by script → human pass.** Never skip a phase; never author
from memory; never hand-edit the assembled file for structure.

---

## Phase 0 · Orient (10 minutes, saves hours)

1. Read `reference.md` fully, then skim `template.html` top-to-bottom once —
   you are learning the component vocabulary, not memorizing markup.
2. Decide the build mode:
   - **Solo** (one author, one sitting): course ≤ ~8 lessons.
   - **Fan-out** (parallel builders + assembler): > 8 lessons, or multiple
     source documents, or multiple authors/models. When in doubt, fan out —
     the fragment protocol costs little and removes merge risk.
3. Check for sibling courses in the target folder. A new course must NOT
   re-teach an existing one — write one "if you want X in depth, see course Y"
   pointer instead, and keep the new course standalone (reference.md §11).

## Phase 1 · Source digests — never author from memory

**Rule: if a fact is not in a digest file, it does not go in the course.**
This single rule kills hallucinated facts, which are the #1 way a course
loses trust (reference.md §7).

For every source (book, slide deck, codebase, product doc), produce
`digests/<source>.md` with exactly these sections:

1. **Key concepts & definitions** — the source's actual definitions and
   formulas, written out (not "see book").
2. **Figures worth recreating** — each described precisely enough that
   someone who never saw the original can redraw it as SVG (nodes, arrows,
   layout, the point the picture makes).
3. **Worked examples with real numbers** — capture the numbers verbatim.
   Real numbers are what make lessons feel true; invented ones are slop.
4. **Relevance hooks** — bullets mapping concepts to the learner's world
   (their product, their domain).

Long sources: split by chapter and digest in parallel — one digester per
chunk, each writing its own file. Digests are the ONLY thing lesson authors
read; nobody re-reads the primary source downstream.

If the course maps theory onto a real system (the best kind), also write
`digests/system-context.md`: a verified, compact description of that system
with paths/names/numbers. Authors may claim about the system ONLY what this
file says. One wrong system claim poisons the learner's trust in every
correct one.

### The distribution gate (decide BEFORE digesting — a lived failure)

Declare in `curriculum.md` line 1: **PUBLIC or INTERNAL.** For a PUBLIC
course, the system-context digest must be **anonymized at digest time, not at
review time**: no client/shop names, no real revenue or operational metrics,
no internal repo/product/component names, no internal doc citations (§N), and
the system is framed as *"một hệ ví dụ"* — an illustrative example — never
"our production system". Add a visible disclaimer callout on the overview
pane saying names/numbers are example values.

Why digest-time: fragments and digests are the **source of truth** — if only
the assembled HTML is scrubbed, the next re-assembly silently re-leaks
everything (this happened: a public course shipped a real client's name and
client-confirmed revenue that survived one "de-brand" pass because the pass
cleaned the output, not the sources). Keep a `sensitive-terms.txt` (client
names, internal repos, real figures) next to the digests and run
`validate_course.py <file> --sensitive sensitive-terms.txt` as part of every
build and every review of a public course.

## Phase 2 · Curriculum contract — before any prose

Write `curriculum.md` (the shared contract every builder reads first):

- Course identity: final file path, title, audience, promise, `data-theme`,
  `lang`, slug. Explicit pointer duties to sibling courses.
- Parts (= L1→L5 level bands) → modules → lessons. 12–28 lessons total.
- **Per-lesson brief** (6–9 lines each): id (`mN-lK`), title, level, ~minutes,
  **the core idea in ONE sentence** (the felt problem, the takeaway and the
  quiz must all serve this sentence — the coherence triangle, see
  `examples.md §4`), the *felt problem* to open with, which digest sections
  feed it, the visual plan (which diagram FORM from the `examples.md §6`
  decision tree, and what relationship it shows), **new terms introduced
  (≤3 for L1–L2 lessons; each gets a first-use explanation + glossary row)**,
  and the map-to-reality hook if any.
- The fragment protocol (Phase 3 below) copied in, so the contract is
  self-contained for builder agents.
- Quality bar reminders: quiz style ("test application, not recall"),
  takeaway style, banned slop phrases.

**Why contract-first:** with the outline fixed, N builders can work in
parallel and their output composes; without it, every module drifts in scope,
tone, and difficulty and no amount of review stitches it back.

## Phase 3 · Build lessons

Author every lesson to the §4 rhythm (felt problem → name it → show it →
apply it → Takeaway → Quiz). Then the mode-specific mechanics:

**Solo mode:** author directly in your copy of `template.html`, one lesson at
a time, keeping `LESSONS` in sync as you go. Run the validator every few
lessons — don't batch 20 lessons of errors.

**Fan-out mode (the fragment protocol):** each builder writes, per module N:

- `module-N.html` — ONLY `<article class="lesson" id="mN-lK" data-lesson>`
  blocks (markup copied from the template), each ending with an EMPTY
  `<div class="lesson-nav" data-navfor="mN-lK"></div>`. No `<html>/<head>`,
  no module header (the assembler owns those).
- `module-N-meta.json` —
  `{"module": N, "moduleTitle": "…", "part": "Phần I · …", "lessons":
  [{"id": "mN-lK", "title": "…", "desc": "…", "minutes": 6, "level": 2,
  "takeaway": "the exact takeaway sentence"}]}`
- **SVG id prefixing (hard rule):** every internal SVG id (markers,
  gradients, clip paths) is prefixed `mNlK-` (e.g. `m2l1-arrow`). Without
  this, merged fragments produce duplicate DOM ids and arrowheads silently
  render wrong. The validator catches it; the prefix prevents it.

The recap lesson ("Tổng kết · cheat sheet") is built LAST, from the
`takeaway` fields of all meta files — that's why metas carry takeaways.

**Builder prompt — copy this verbatim and fill the blanks** (do not
re-derive it; weaker builders degrade exactly when the prompt is improvised):

```
You are building module {N} of an interactive course to a fixed house
standard. Work ONLY from these files, in this order:
1. {path}/curriculum.md            — the contract; your module's briefs are §{…}
2. {skill}/reference.md            — the standard (§3 visuals, §4 pedagogy)
3. {skill}/examples.md             — GOLD vs FAIL patterns; imitate the GOLD shapes
4. {skill}/template.html           — copy component markup exactly from here
5. {digest paths}                  — the ONLY source of facts

Write: {fragments}/module-{N}.html and module-{N}-meta.json per the fragment
protocol in curriculum.md. Hard rules: every fact traces to a digest line —
no digest, no claim; every internal SVG id prefixed m{N}l{K}-; each lesson =
felt problem → name it → show it → apply it → takeaway → quiz, all serving
the ONE core idea in its brief; distractors are misconceptions
(examples.md §2 procedure); ≤3 new terms per L1–L2 lesson; formulas always
formula ⇒ worked number ⇒ plain words.

Final reply (this is your compliance check, not a message): per lesson —
id · title · word count · the core idea · the takeaway sentence · quiz
correct-letter · any deviation from the brief and why.
```

Vary the quiz correct-answer positions across lessons — a module where every
`data-correct` is the same index reads as untrustworthy (the validator warns).

## Phase 4 · Assemble — by script, never by hand

Run `scripts/assemble_course.py <contract.json>` (see its docstring for the
contract shape). It merges fragments into the template, generates the
`LESSONS` array from metas, sets theme/lang/hero/completion/glossary, and
**localizes every visible chrome/engine string** (built-in Vietnamese table;
`chromeOverrides` for other languages). It finishes by invoking the
validator.

Hand-editing the assembled file is allowed only for CONTENT fixes flagged by
review — structural changes go back to the fragments + re-assemble, so the
fragments stay the source of truth and the build is reproducible.

## Phase 5 · Validate — script first, then the human pass

1. `python3 scripts/validate_course.py <course.html>` — loop until **0
   errors**. Warnings are judgment calls: fix or consciously accept, never
   ignore silently.
2. The parts a script cannot judge (do them in a real browser):
   - keyboard-only walk (nav, quiz, accordions, complete);
   - 375px pass (sidebar toggles, tables scroll, no horizontal overflow);
   - BOTH color modes (loads light; 🌙 persists across reload);
   - every diagram: does the figcaption state the point, and would the lesson
     be weaker without the picture? If not, the diagram is decoration — redo it.
3. Fact pass: re-check every number/name/date in the course against the
   digests (not against memory). Run the `anti-slop-review` skill on prose.
4. Self-test before shipping — answer honestly:
   1. Could a beginner follow every lesson without opening another tab?
   2. Does every quiz test a *decision*, not a memory?
   3. Did I verify every fact against a digest file?
   4. Would the course still work with all images removed EXCEPT the SVGs
      (i.e., do diagrams carry load, not decoration)?
   5. Is there one sentence per lesson a learner will still quote in 6 months?
   6. For 3 random lessons: do the felt problem, takeaway and quiz all serve
      the SAME core idea (the coherence triangle)? Drift here is the #1
      structural failure of parallel builds.
   7. If the course is PUBLIC: did the `--sensitive` pass run clean, and is
      the example system framed as illustrative (never "our production
      system"), with the disclaimer callout present?

## Failure modes — the tells (check yourself against this table)

| Tell | What went wrong | Fix |
|---|---|---|
| Lesson opens with a definition | Skipped the felt problem | Rewrite the first paragraph as a scenario the learner recognises |
| Quiz answerable by re-reading one sentence | Tests recall, not application | Turn it into a scenario with a plausible wrong choice |
| Diagram = three boxes restating headings | Decoration, not information | Draw the *relationship* (flow, contrast, before/after) or delete |
| Numbers with no digest source | Invented facts | Trace to a digest or cut the claim |
| "mạnh mẽ / powerful / seamless…" | Slop intensifiers | State the mechanism instead of the adjective |
| English chrome in a Vietnamese course | Skipped localization table | Assembler table / `chromeOverrides` |
| Arrowheads missing/wrong after merge | Duplicate SVG marker ids | `mNlK-` prefix rule |
| A later lesson quietly assumes an earlier optional one | Difficulty not monotonic | Reorder or state the prerequisite in the module header |
| Reviewer "fixes" a correct source number | Trusted memory over digest | Digests win; re-verify before changing any number |
| Quiz correct answer is the same letter in most lessons | Builder defaulted; learners game it | Vary `data-correct`; validator warns on skew |
| Quiz tests a side detail from paragraph 4 | Coherence triangle broken | Re-anchor quiz on the brief's core-idea sentence |
| "X is like a library/toolbox" analogy | Maps vibes, not mechanism | Rewrite: map the mechanism AND state where the analogy breaks (`examples.md §5`) |
| Client name / real revenue / internal repo in a public course | Distribution gate skipped; sources never scrubbed | Anonymize the DIGESTS, add `sensitive-terms.txt`, run `--sensitive`; scrubbing only the output re-leaks on re-assembly |
| `data-explain` says "Correct!" and nothing else | Feedback praises instead of teaching | Explain why each distractor is wrong (`examples.md §2`) |

## Reviewing & retrofitting an existing course

Reviews come in two shapes — classify FIRST, then pick the lane:

1. **Template-native** (has the `LESSONS` engine): run the validator; fix
   every error; fix or consciously accept each warning (record the acceptance
   — e.g. "10 lessons < 12 floor: focused course, padding would be slop").
   Then the human pass (Phase 5.2–5.4). Content fixes are edited in place.
2. **Legacy / pre-template** (no engine, external CSS/JS, hardcoded hex):
   do NOT chase individual structural checks — they fail by construction.
   Allowed in place: content-level fixes only (facts, slop, meta description,
   sensitive terms, broken links). Everything structural waits for a full
   migration: digest the existing course's own content (Phase 1, with the
   course as source), write the contract, rebuild via fragments + assembler.
   Migration is a scheduled decision, not a side effect of a review.

Every review of a PUBLIC course includes the `--sensitive` pass, regardless
of what the review was originally about.

## Writing so ANYONE understands (the "dễ hiểu" rules)

These are mandatory for beginner-audience courses and good defaults always:

1. **Example before definition.** Show the situation, then name the concept.
2. **First-use rule:** every English technical term gets a one-line
   plain-language explanation at first appearance (and an entry in the
   overview glossary). After that, use the English term consistently — do
   not alternate synonyms.
3. **One idea per paragraph; 1–3 sentence paragraphs.** If a sentence needs
   a second reading, split it.
4. **Concrete over abstract:** real quantities ("100 products × 4 quarters ×
   3 stores = 1,200 rows"), never "a large amount of data".
5. **Each abstract concept gets a mental-model analogy** (the `insight`
   callout) — one line the learner can repeat.
6. **Same concept, ≥2 domains.** Transfer comes from seeing the shape twice.
7. **The learner's question order wins.** Answer "why do I care?" before
   "what is it?" before "how does it work?" — never the reverse.
8. **Never let notation carry the lesson.** Every formula appears with a
   worked number example and a one-sentence reading in plain words.
