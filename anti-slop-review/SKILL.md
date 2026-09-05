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

## The lexicon (hard = delete, soft = justify)

Run `validate_course.py`'s `prose_checks()` for the mechanical pass; this list is
for prose the validator never sees (announcements, README, UI copy).

**Hard (EN)** — delve · seamless · revolutionary · cutting-edge · game-changing ·
world-class · best-in-class · state-of-the-art · unlock/harness the power ·
supercharge · elevate your · ever-evolving · paradigm shift · tapestry · in the
realm of · it's worth noting · it is important to note · let's dive · dive deep ·
buckle up · look no further · treasure trove · synergy · a testament to · plays a
vital/crucial/pivotal role · in this digital age · at the end of the day ·
meticulously · boasts a · diverse array · underscores the importance · in conclusion.

**Hard (VI)** — trong thế giới ngày nay · trong thời đại số · trong bối cảnh hiện
nay · chìa khoá thành công · nâng tầm · vượt trội · đột phá · mạnh mẽ · toàn diện ·
tối ưu hoá trải nghiệm · kỷ nguyên · làn sóng · tận dụng sức mạnh · sức mạnh của ·
đóng vai trò quan trọng · không thể thiếu · bức tranh toàn cảnh · một cách hiệu
quả/toàn diện/đáng kể · tuyệt vời · hoàn hảo · cực kỳ · vô cùng · hết sức · đáng kể ·
tinh tế · cách mạng · thay đổi cuộc chơi · siêu năng lực · trợ thủ đắc lực · người
bạn đồng hành · chinh phục · bí quyết · tuyệt chiêu · đỉnh cao · hàng đầu thế giới ·
giúp bạn dễ dàng · tóm lại, · kết luận lại.

**Soft (justify or cut)** — EN: leverage · robust · crucial · pivotal · landscape ·
journey · navigate · streamline · comprehensive · powerful · foster · showcase ·
underscore · furthermore · moreover · ultimately · in essence. VI: không chỉ · mà
còn · nói cách khác · có thể nói · quan trọng hơn · hiệu quả · tối ưu · linh hoạt ·
thông minh · bức tranh · điểm nhấn · chìa khoá · trái tim · hành trình.

**Vietnamese machine-translation calques (keep the English term of art)** —
ngăn xếp → stack · công kích → attack/tấn công · chưng cất → distillation ·
teo kỹ năng → mai một kỹ năng · mã thông báo → token · đường ống → pipeline ·
khung nhìn → view · học sâu → deep learning · ảo giác → hallucination ·
lái mô hình / lái được → điều hướng · kỹ thuật nhắc → prompt engineering.
Rule: a term of art that the reader will meet in English docs stays in English at
first use, gets one plain-language gloss, and is never alternated with a synonym.

## Stylometric checks (the tells a lexicon cannot see)

Measure, don't eyeball. Per 1,000 words of body prose:

| Signal | Warn | Error | Why |
|---|---|---|---|
| em dashes (— –) | ≥ 8 | ≥ 13 | human 3.2, literary ≤6.4, GPT-4.1 10.6 (Freeburg 2026) |
| paragraphs with ≥2 em dashes | > 15% | — | the dash-aside rhythm |
| "không chỉ…mà còn" / "not just X but Y" / "it's not X, it's Y" | > 0.8 | — | #1 syntactic tell, Wikipedia *Signs of AI writing* |
| rất / vô cùng / cực kỳ / hết sức | > 2.0 | — | intensifier instead of a number |

Also check, by reading: rule-of-three lists where three is not the real count ·
bolded lead-ins on most paragraphs · present-participle tails ("…, highlighting
the importance of…") · copula avoidance ("serves as", "stands as", "đóng vai trò
là") where "is" was the word · section headings of the form "Challenges and Future
Directions" / "Thách thức và hướng phát triển" · a closing paragraph that restates
the piece ("Tóm lại…", "In conclusion…").

Reference: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (WikiProject
AI Cleanup, ~15k words, actively maintained) — read it before a big review.

## Structural checks (educational content)

- **Every analogy carries its break.** "Sloppy analogies" — a mapping whose
  correspondence does not hold — is one of the 16 slop codes in Jones et al.,
  *AI-Generated "Slop" in Online Biomedical Science Educational Videos*,
  JMIR Med Educ 2025-11-20 (https://mededu.jmir.org/2025/1/e80084; slop in 5.3%
  of 1,082 videos; engagement did not distinguish slop from good content).
  An analogy without a stated limit is a defect, not a flourish.
- **Every number carries a dated source link in the artefact itself**, not only in
  the author's notes. Learner distrust of AI-made material is specifically about
  accuracy: 170 computing students, only 50% could tell AI-generated instructional
  video apart, yet 62% would not trust it equally, top concern "inaccurate
  information" (https://arxiv.org/html/2607.28203, 2026-07-30). Visible provenance
  is the countermeasure.
- **No lesson/section opens with a definition or an announcement** ("Trong bài này
  chúng ta sẽ…", "X là một…"). Open with the situation.
- **No heading followed by a line that paraphrases it.** A heading stands alone or
  is followed by information.
- **Depth is stated and held**: the piece does not drift between beginner and
  expert register inside one section.

## Reporting

Add to the existing output shape: the four stylometric numbers above (measured,
with the word count they were measured on), and — for anything that quotes bad
writing on purpose — the list of passages you exempted and why.

## Layout slop (pages and slides are content too)
- No metaphor/tagline line under a heading; no subtitle that restates the title in different words. A heading either stands alone or is followed by real information.
- Landing/showcase pages lead with ONE hero element (the strongest visual or claim); everything else becomes compact grouped detail below — not a parade of equal-weight sections each with its own breathless intro.
- Cut decorative stat rows ("3 easy steps", "100% awesome") and icon-grid filler that carries no verifiable information.

## Language & readability
- Proofread for real spelling errors and tone consistency in whatever language the content is in. For non-English content, watch for the homophone/diacritic mistakes native readers notice instantly.
- Match the content's existing language; keep technical terms in their conventional form (often English) where that reads naturally.
- Short, direct sentences. Guides should be scannable: headings, numbered steps, one idea per bullet.

## Publishing hygiene
- Content going public must be anonymized: no internal company/employee names, internal URLs, or credentials.
- Keep authorship/footer attribution exactly as the author set it — don't "improve" it.

## Output
Report as: list of removed slop (with before-text), list of corrected facts (claim → verified value → source URL), list of items needing the author's confirmation. Then apply fixes.
