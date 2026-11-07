---
name: bug-class-audits
description: >-
  Use when the same bug keeps coming back or one case was patched repeatedly while the
  class stayed broken — "lại bị nữa", "sửa tới sửa lui", "còn các trường hợp khác thì
  sao", "làm cho đúng cả class", "this happened again", "make sure it can never come
  back", a review flagging the same pattern. Turns it into an enforced rule: fix every
  site, numbered anti-pattern entry, audit script, pre-push/CI gate with a baseline
  that only shrinks. Diagnosis belongs to investigating-bugs.
---

# Bug-Class Audits

Fixing the instance you were shown is the minimum. The question after every bug fix is:
**is this a class?** If the same shape can exist elsewhere (now or in future code), an
instance-fix just schedules the next incident. The loop turns a repeat incident into one
numbered rule plus one mechanical check, so no class is re-argued.

## The loop

1. **Detect the class.** Start from the sites `investigating-bugs` already confirmed;
   grep for any it missed and confirm the same violated invariant before grouping.
   (Typical shapes: `toFixed(` for display across dozens of components; a filter applied
   in the UI but absent from SQL in several routers; a fabricated `× 0.N` coefficient in
   several metrics.)
2. **Fix confirmed sites within the authorized scope.** Report unrelated sites for follow-up.
   For independent modules use [agent-orchestration](../agent-orchestration/SKILL.md):
   the harness lead defines the invariant and owns the gate; workers apply per-site fixes
   ([routing](../agent-orchestration/sections/routing.md)).
3. **Write the rule down** as a numbered entry in the project's anti-pattern list
   (canonical AGENTS.md, not adapters): the pattern, why it's wrong,
   what to do instead. Numbered rules are citable ("§33") and become the project's
   institutional memory across context resets and sessions.
4. **Write a mechanical audit** when the rule is grep-able/parse-able: a small script in
   `scripts/audit/` that scans the relevant code and exits non-zero on violations.
   Use AST/type-aware checks when syntax alone is ambiguous. Test the audit with a failing example and a legitimate counter-case.
   In the commit that wires it (step 5), the numbered entry shrinks to one line naming the audit (its index row);
   the audit's fix text carries the why.
5. **Wire it into the gate** — pre-push hook and/or CI — so the rule enforces itself.
   A rule that relies on someone remembering it is a suggestion. When the class is an
   agent action (a skipped gate, a bypassed hook, a credential misuse), the owning layer
   is the agent harness: a fail-open tool/stop hook, replayed over past transcripts to
   count hits and false positives before it ships.
6. **Keep an index**: a table of concern → rule § → audit script → where it's wired.
   Rules that can't be mechanically checked (design judgment) still get a numbered entry,
   marked "review-only", so reviews have a checklist. A visual class with a measurable shape
   (text wrapping beside empty space, overflow, overlap) is checkable: add a rendered DOM probe
   to the E2E route sweep (`design-qa` has one for text width).

## Audit-script conventions

- **Allowlist with justification, never silently.** Legitimate exceptions get a same-line
  marker comment (`// audit-ok-<rule>: <short source-cited reason>`) the script honors.
  A reason of "TODO" is not a reason.
- **Baselines only move DOWN.** For rules adopted with pre-existing debt, the script
  carries a baseline count/list. Genuinely removing debt lowers the baseline; refreshing
  the baseline to admit NEW violations is dodging, not fixing — never do it, and treat a
  baseline bump in a diff as a red flag. When touching a file that carries baselined debt,
  clean the part you touch; at minimum don't add to it.
- **Fail with actionable output**: file:line, the offending snippet, the rule number and a
  one-line fix direction — fixable from the output alone.
- Keep runtime in seconds; slow audits get bypassed.
- No incident story in the audit or its comments; the rule is one line.

## What qualifies (and what doesn't)

Good candidates: formatting/locale leaks, missing filter/authz conditions, fabricated
coefficients, hardcoded user-facing strings, timezone-naive bucketing, forbidden APIs,
release-config regressions (obfuscation off, debug hooks outside `#if DEBUG`). The same
pattern generalizes beyond code: an App Store **rejection ledger** with a per-rejection
checklist item is a bug-class audit for submissions (see `appstore-review-guard`).

Not worth an audit: one-off bugs with no pattern, rules cheaper to enforce with a type
(make illegal states unrepresentable first — an audit is the fallback when the type system
can't see it), and style preferences a formatter handles.

## Output

After the loop: all sites fixed, the numbered rule appended, the audit script added and
wired, the index table updated, and the audit shown green on the current tree. Report
which of the artifacts (rule, audit script, gate wiring, index) were produced and where.
