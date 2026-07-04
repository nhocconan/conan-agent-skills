---
name: bug-class-audits
description: Turn any recurring bug into a permanent, mechanically-enforced rule — fix the class, not the instance. When a bug greps to multiple call sites or the same shape of bug appears a second time, fix every site, append a numbered rule to the project's anti-pattern list, write an audit script, and wire it into pre-push/CI with a baseline that only shrinks. Use after fixing any bug that could recur, when the user says "this happened again" / "lại bị nữa", when a review keeps flagging the same pattern, or when setting up quality enforcement for a project.
---

# Bug-Class Audits

Fixing the instance you were shown is the minimum. The question after every bug fix is:
**is this a class?** If the same shape can exist elsewhere (now or in future code), an
instance-fix just schedules the next incident. The loop below turned three repeat
dashboard incidents into a system where ~35 rules are enforced automatically.

## The loop

1. **Detect the class.** After fixing a bug, grep the codebase for the same pattern.
   More than one hit — or the second time this shape of bug appears — makes it a class.
   (Real examples: `toFixed(` for display → 38 sites; a global filter missing from SQL
   blocks → 8 sites across 3 routers; `× 0.N` fabricated KPI coefficients → 6 sites.)
2. **Fix every site now**, not just the reported one. The report was a sample, not the bug.
3. **Write the rule down** as a numbered entry in the project's anti-pattern list
   (CLAUDE.md / AGENTS.md "Anti-patterns to avoid"): what the pattern is, why it's wrong,
   what to do instead. Numbered rules are citable ("§33") and become the project's
   institutional memory across context resets and sessions.
4. **Write a mechanical audit** when the rule is grep-able/parse-able: a small script in
   `scripts/audit/` that scans the relevant code and exits non-zero on violations.
   Deterministic, fast, zero-dependency (stdlib + regex/AST is fine).
5. **Wire it into the gate** — pre-push hook and/or CI — so the rule enforces itself.
   A rule that relies on someone remembering it is a suggestion.
6. **Keep an index**: a table of concern → rule § → audit script → where it's wired.
   Rules that can't be mechanically checked (visual collisions, design judgment) still get
   a numbered entry, marked "review-only", so reviews have a checklist.

## Audit-script conventions

- **Allowlist with justification, never silently.** Legitimate exceptions get a same-line
  marker comment (`// audit-ok-<rule>: <reason citing a source>`) that the script honors.
  A reason of "TODO" is not a reason.
- **Baselines only move DOWN.** For rules adopted with pre-existing debt, the script
  carries a baseline count/list. Genuinely removing debt lowers the baseline; refreshing
  the baseline to admit NEW violations is dodging, not fixing — never do it, and treat a
  baseline bump in a diff as a red flag. When touching a file that carries baselined debt,
  clean the part you touch; at minimum don't add to it.
- **Fail with actionable output**: file:line, the offending snippet, and the rule number +
  one-line fix direction — the developer (or agent) should be able to fix from the audit
  output alone.
- Keep runtime in seconds; a slow audit gets bypassed.

## What qualifies (and what doesn't)

Good candidates: formatting/locale leaks, missing filter/authz conditions, fabricated
coefficients, hardcoded user-facing strings, timezone-naive bucketing, forbidden APIs,
release-config regressions (obfuscation off, debug hooks outside `#if DEBUG`). The same
pattern generalizes beyond code: an App Store **rejection ledger** with a per-rejection
checklist item is a bug-class audit for submissions (see `appstore-review-guard`).

Not worth an audit: one-off bugs with no pattern, rules cheaper to enforce with a type
(make illegal states unrepresentable first — an audit is the fallback when the type system
can't see it), and style preferences a formatter already handles.

## Output

After the loop runs: all sites fixed, the numbered rule appended, the audit script added +
wired, the index table updated, and the audit run shown green on the current tree. Report
which of the four artifacts were produced and where.
