# Examples — the few-shot pack (annotated GOLD vs FAIL)

> Rules tell a strong model what to do; **examples are what weaker models
> actually imitate.** Every builder prompt must include this file. Each pair
> below is GOLD (shipped house output or equivalent) vs FAIL (the pattern
> weak models produce when left to taste), with the load-bearing differences
> named. Do not copy the GOLD text into a course — copy its *shape*.

---

## 1 · Felt-problem opening (the first paragraph of every lesson)

**GOLD (VI, shipped):**

> Một sáng, báo cáo **NMV** (net merchandise value — doanh thu thuần sau giảm
> giá) tháng của một shop mỹ phẩm nhảy vọt gần gấp đôi. Không phải bán chạy:
> một file Shopee bị giải mã nhầm — công cụ đọc trúng *sheet pivot* ở đầu file
> thay vì sheet dữ liệu, nhân đôi vài trăm dòng. Nếu con số đó chạy thẳng lên
> KPI headline, cả quyết định tuần dựa trên nó đều sai.

Why it works — the four properties every opening needs:
1. **A specific moment** ("một sáng", one report, one shop) — not "in data
   systems, quality matters".
2. **A surprise that demands explanation** (doubled revenue that isn't real).
3. **Stakes stated in the learner's currency** (decisions based on it go wrong).
4. **The technical term is smuggled in via the story** (NMV explained in one
   parenthetical at first use), not lectured.

**FAIL (what weak models write):**

> Chất lượng dữ liệu là một yếu tố quan trọng trong mọi hệ thống phân tích.
> Trong bài này, chúng ta sẽ tìm hiểu khái niệm data quality và tại sao nó
> quan trọng.

Tells: opens with a definition + importance claim ("quan trọng" ×2, zero
information), announces the lesson instead of starting it, no person, no
moment, no stakes. If your first paragraph could open any lesson in any
course, delete it and write the incident that makes THIS lesson urgent.

---

## 2 · Quiz — distractors are misconceptions, not filler

**GOLD (VI, shipped — guardrail lesson; correct = B):**

> **Q:** Hệ gợi ý "giảm giá 15% cho combo X" và tín hiệu vượt ngưỡng tin cậy.
> Việc gì xảy ra tiếp theo trong một hệ có guardrail đúng nghĩa?
> - A. Hệ tự thực thi ngay vì số đã đủ mạnh. ← *misconception: automation
>   means removing the human*
> - B. Đề xuất qua cổng duyệt của người chịu trách nhiệm, kèm biên nhận
>   điều kiện nào pass/fail. ← correct
> - C. Tự động kích hoạt giảm 18% vì đó là trần cho phép. ← *misconception:
>   a cap is a target*
>
> `data-explain`: "Guardrail chặn hệ ĐỀ XUẤT vượt ngưỡng — không có nghĩa hệ
> được TỰ thực thi (A sai), và trần 18% là giới hạn trên, không phải mức nên
> dùng (C sai). Quyết định kích hoạt luôn qua người duyệt."

Procedure that produced it (follow it, in this order):
1. Write the lesson's **core idea** in one sentence.
2. Write the **two most common wrong beliefs** about it (ask: what would a
   smart person who skimmed the lesson still get wrong?).
3. Those two wrong beliefs ARE options A and C — verbatim as a believer
   would phrase them, confident tone, no "never/always" tells.
4. The correct option is precise, not the longest, not always the same letter.
5. `data-explain` names **why each distractor is wrong**, not just why the
   right one is right — the learner who picked A must learn something too.

**FAIL:**

> **Q:** Guardrail là gì?
> - A. Một loại rào chắn trên đường cao tốc.
> - B. Ngưỡng an toàn chặn đề xuất vượt giới hạn. ← correct
> - C. Một thư viện JavaScript.
>
> `data-explain`: "Chính xác!"

Tells: recall question answerable by re-reading one sentence; distractors no
adult would pick (a joke and a non-sequitur); explain praises instead of
teaching. Also the correct answer is the longest option — a test-taking tell.

---

## 3 · Takeaway — quotable, load-bearing, specific

**GOLD (shipped):**

> Một chênh lệch **không mặc định là bug** — xác nhận ngữ nghĩa với
> ground-truth ngoài trước khi "sửa" bất kỳ con số nào.

Test it passes: you could quote it in a meeting six months later and it would
change a decision. It contains a *behavioral instruction* with a *condition*.

**FAIL patterns (all shipped-looking, all empty):**
- "Data quality rất quan trọng trong hệ quyết định." (importance claim — zero behavior)
- "Hãy luôn cẩn thận với dữ liệu đầu vào." (vague virtue)
- The same takeaway sentence pasted into three lessons. (the validator now
  flags duplicate takeaways — but don't make it near-duplicates either)

Write the takeaway BEFORE writing the lesson body. If you can't state it in
one sentence, the lesson has no core idea yet — fix that first.

---

## 4 · The coherence triangle (felt problem ↔ takeaway ↔ quiz)

The #1 structural drift in weak-model lessons: the opening tells story X, the
takeaway summarizes Y, the quiz tests footnote Z. Each lesson has **ONE core
idea**; all three anchors serve it.

GOLD wiring (from the example above): opening = doubled-NMV incident (bad
data → bad decisions) → takeaway = "discrepancy ≠ bug; verify against
external ground truth first" → quiz = a scenario where the learner must
choose between "fix the number" and "verify semantics first".
Same idea, three exposures, three depths.

Mechanical self-check per lesson before submitting: write the core idea in
one line; confirm (a) the opening dramatizes *that*, (b) the takeaway states
*that*, (c) the quiz forces a decision that hinges on *that*. If any leg
tests something else, rewrite the leg, not the idea.

---

## 5 · Analogy (the `insight` callout) — map the mechanism, state the break

**GOLD:**

> Star schema giống quầy tính tiền siêu thị: hoá đơn (fact) ở giữa ghi *con
> số*, còn kệ hàng, khách, khung giờ (dimensions) là *ngữ cảnh* đứng quanh.
> Điểm khác quan trọng: hoá đơn siêu thị in một lần là xong — bảng fact thì
> được cả nghìn câu truy vấn đọc lại mỗi ngày, nên grain phải chọn từ đầu.

Two required parts: (1) the mapping works at the **mechanism** level (center
records numbers, surroundings give context), not just vibes; (2) it **states
where the analogy breaks** — that's what stops learners over-extending it.

**FAIL:** "Data warehouse giống như một thư viện khổng lồ." (maps nothing —
any orderly thing is "like a library"; no mechanism, no break, no reuse value)

---

## 6 · SVG diagram — relationship, not decoration

**GOLD test (apply to every figure):** count the facts a reader gets from the
picture that are NOT in the caption. If < 2, it's decoration — delete or redraw.

GOLD example (shipped, described): two parallel rows — Simon's five-stage
decision model on top, the example system's decision lifecycle below, dashed lines
connecting corresponding stages, one loop-back arrow labeled "learning".
Facts carried by the picture alone: which stages correspond 1:1, that one
stage has NO counterpart (the gap is visible), where the loop closes. Words
would need a paragraph; the eye gets it in two seconds.

**FAIL:** three rounded boxes labeled "Extract → Transform → Load" restating
the section headings, caption "Quy trình ETL". The picture teaches nothing
the headings didn't. (This is the single most common weak-model diagram.)

Diagram decision tree — pick the FORM before drawing:
| The relationship is… | Draw |
|---|---|
| a flow / pipeline | left→right boxes + arrows, ≤9 nodes |
| a contrast (before/after, bad/good) | two-panel side-by-side, same layout both sides |
| correspondence between two models | two parallel rows + dashed mapping lines |
| a hierarchy / containment | nested boxes, ≤3 levels |
| a threshold / zones | one axis with shaded bands + a marker |
| change over time / feedback | timeline or loop with one labeled return arrow |

Mobile rule: at `viewBox` width ≥ 700, text under `font-size:9` is unreadable
on a 375px phone. Fewer, bigger labels; move detail to the caption.

---

## 7 · Formula ⇒ worked number ⇒ plain words (never notation alone)

**GOLD (shipped):**

> Công thức niềm tin `confidence = |r|·k/(k+3)` là một bộ *damping theo cỡ
> mẫu*: với |r| = 0,51 — 6 tuần dữ liệu → 0,51·6/9 ≈ **0,34**; đủ 20 tuần →
> 0,51·20/23 ≈ **0,44**. Đọc bằng lời: *cùng một tương quan, hệ tin hơn khi
> có nhiều tuần quan sát hơn — và không bao giờ tin quá chính |r|.*

Three parts, always: the formula, one worked number the reader can recompute,
and a one-sentence plain-words reading. A formula without the worked number
is notation; a worked number without the plain-words reading is arithmetic.

---

## 8 · First-use rule in practice

**GOLD:** "…cổng **verify:data** khẳng định *headline == SUM(các dòng bảng
hiển thị)* — tức là con số to trên đầu dashboard phải đúng bằng tổng các dòng
bảng mà người dùng nhìn thấy."
(EN term appears, immediately translated into consequence-language, then used
consistently — never alternated with a synonym.)

**FAIL:** using "rollup", "bảng tổng hợp", "aggregate", "agg" interchangeably
across three lessons for the same thing. Pick one term at first use; the
glossary row fixes the mapping; repeat the same term forever after.
