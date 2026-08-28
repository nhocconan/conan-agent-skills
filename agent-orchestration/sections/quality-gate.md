## §5. Quality gate — verify the fleet, never trust it

### 5.1 Never trust a green claim

- **Never pipe a build or test through `tail`/`head`/`grep`** — the exit code becomes the
  pipe's. Redirect and inspect both signals: `cmd > run.log 2>&1; echo "EXIT=$?"`, then
  grep the log for a *positive* marker (`BUILD SUCCESSFUL`, an actual test count) **and**
  confirm `EXIT=0`.
- **A claim without an artifact is a guess.** "Tests pass" needs the count. "The page
  renders" needs the screenshot or HTTP status. "The API returns X" needs the payload.
- The lead re-runs the check itself for anything load-bearing. Delegation moves the typing,
  not the accountability.

### 5.2 Independent verification, scored

For each finding or claim that matters, spawn a verifier with **fresh context** that sees
the location and the rules but not the reasoning. Ask for a 1–10 confidence score with a
written justification, and instruct it to explain *why not* below the bar.

| Score | Meaning | Action |
| --- | --- | --- |
| 9–10 | Re-derived independently; concrete failing input or exploit path | act on it |
| 7–8 | Strong pattern match, not re-derived | act, flag as unverified |
| 5–6 | Plausible | report with caveat only |
| ≤4 | Speculation | discard (keep in an appendix if severity would be P0) |

Default gate: **discard below 8** for anything that would cause a code change; loosen only
for a deliberately exhaustive sweep, and say that you did.

### 5.3 Diverse lenses beat redundant ones

Three identical verifiers mostly agree with each other. Give each a different lens —
correctness, security, performance, "does it actually reproduce" — when a finding can fail
in more than one way. **Security and performance are insurance lenses: run them even when
they are usually silent**, on anything touching auth, tenancy, money, user input, uploads,
migrations, or a hot query path.

### 5.4 Merge findings like a reviewer, not a stapler

Fingerprint each finding (`path:line:category`), group, keep the highest-confidence
version, and mark the rest as confirmations. **Two independent lenses hitting the same
fingerprint is real signal** — raise its confidence and say which lenses agreed. Then rank
by severity, and state the count you dropped and why.

### 5.5 Know when you are done looking

For discovery work with no known answer count, run until **two consecutive waves surface
nothing new** (dedup against everything seen, not against what survived the gate — or
rejected findings reappear forever). Then run one **completeness critic**: what modality
was never run, what claim was never verified, what source was never read? Its answer is
the next wave, or the honest limits paragraph in your report.

### 5.6 Escalate — the ladder runs both ways

Delegation down is the default; **escalation up is mandatory after repeated failure.**
If a tier fails the same acceptance check twice, do not send it a third time — the spec is
wrong, or the task needed the top tier all along. Take it back, re-spec it, or do it
yourself. Symmetrically: if the lead is doing something a cheap tier could verify
mechanically, that is waste. Both directions are errors.

---
### 5.7 The review–fix loop — bounded, and it knows a stalemate

A finding that survives the gate goes back to the **same builder** (context intact — it
knows why it wrote what it wrote), never applied by the lead, and never by the reviewer.
The builder marks each item `fixed` or `wontfix` with a reason. Then:

- **Re-review with a fresh verifier**, not the one that found it — a reviewer that
  re-reads its own list confirms its own list.
- **Bound: three cycles.** A review that still applies fixes on the third pass is not
  converging; stop and report which findings keep reappearing. That is a real blocker
  worth the operator's eyes, not a fourth run.
- **Stalemate = escalate, not iterate.** If a builder's `wontfix` is re-opened by the
  next reviewer, the two cannot settle it. Put both positions to the operator as a
  single question with selectable options and the lead's recommendation. Their decision
  is final; the builder incorporates it without further debate.
- **Two failures on the same acceptance check** still escalate a tier or come back to
  the lead (§5.6) — the fix loop does not reset that counter.

### 5.8 Reviewer slots — how many lenses, chosen by scope

Effort buys lenses, not repetition. Allocate by what the diff touches, then fill the
remaining slots with *independent* general reviewers (fresh contexts differ enough to be
worth it):

| Diff touches | Lens added |
| --- | --- |
| auth, user input, secrets, permissions, tenancy, uploads | security (**never gated off**, even when usually silent) |
| a spec, plan file, or issue | **spec-alignment** — missing requirements, scope creep, requirement implemented wrong; quotes the spec line per finding |
| new logic, endpoints, data processing, business rules | tests — coverage of the *new* branches, edge cases, mocking honesty |
| migrations, schema, backfills | data-migration (**never gated off**) |
| a hot query path, a list page, a batch job | performance |
| frontend files | design — calibrated against the repo's `DESIGN.md` if one exists |

Under ~50 changed lines: one general reviewer, no specialists — say so. Over ~200 lines
or any P0/P1 from a specialist: add a **red team** that receives the merged findings and
is told to find what the specialists *missed* (cross-cutting, integration boundaries,
failure modes no checklist covers). Keep standards-vs-spec findings under separate
headings; do not rerank across axes — a style smell and a missed requirement are not on
one scale.

### 5.9 The pre-emit quote gate

Before a finding is promoted, the reviewer must **quote the verbatim line(s) that
motivate it** — the model class body for "field doesn't exist", the dict initialization
for "might be None", both sides for "race between A and B". Cannot quote it → the finding
is unverified: confidence drops to 4–5 and it goes to the appendix, never the main
report, and never "rounded up" to a 7. For framework-generated symbols (ORM decorators,
migrations, `Meta` blocks) the quote is the construct that *creates* the symbol; "I
grepped and didn't find it" is not verification. This one rule kills the largest
false-positive class in automated review.
