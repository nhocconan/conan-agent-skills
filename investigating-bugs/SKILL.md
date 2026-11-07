---
name: investigating-bugs
description: >-
  Use when something is broken, failing, flaky, slow, or behaving unexpectedly; on
  "sao lại lỗi", "tại sao", "bị sai rồi", "lại bị nữa", "debug", "investigate", "vẫn
  chưa được"; or before any fix whose cause is not already proven. Finds the root
  cause before changing anything — reproduce, locate the mechanism, prove the
  diagnosis, then fix (recurring classes go to bug-class-audits); stops the
  guess-and-patch loop that suppresses a symptom.
---

# Investigating bugs

Wraps gstack's `investigate`; local rules govern diagnosis and proof. Resolve paths
from this skill's real directory. `ref-skills/refsync.py ensure` fetches the vendored
upstream (markdown only, no install); if absent, say so and apply these rules.

## The rule that matters most

**An unproven diagnosis is a hypothesis.** Preserve the original failure evidence.
Use isolated tests, temporary instrumentation or a scratch worktree to distinguish
competing causes; remove diagnostic changes before delivery. If reproduction is
unavailable, continue safe probes and label the limits instead of declaring a fix.

## Before touching anything

1. **Verify the presupposition.** "X is broken" may be false, or broken somewhere else.
   Check that the reported behaviour is real before hunting its cause.
2. **Reproduce it** — preserve a failing test, command output or journey artifact.
   Without it, "fixed" is unfalsifiable.
   Prefer a cheap existing test path; don't build unrelated infrastructure for a small fix.
   No command that can show the failure, no fix: with no test, build the smallest
   harness that can go red. Then minimise inputs
   until each remaining one is load-bearing.
3. **Read the actual error.** Full output, not the last line. The pipe-swallows-exit-code
   trap applies: `cmd > run.log 2>&1; echo "EXIT=$?"`.

## Diagnosing

4. **Locate the mechanism.** Name the line, state or ordering that produces *this*
   symptom and not a different one. Rank 3-5 hypotheses, each with the
   observation that would kill it.
5. **Verify by re-deriving, not by recognising.** A pattern that looks familiar is the
   most common way a wrong diagnosis survives review — see `senior-operator`
   OPERATING-MANUAL §4.
6. **Label known vs guessed** in the write-up. Anything unverified is marked unverified.

For the search mechanics — log/trace navigation, bisecting, tooling — read
`../.vendor/gstack/investigate/SKILL.md`, particularly its **"Phase 1: Root Cause
Investigation"**, **"Phase 2: Pattern Analysis"** and **"Phase 3: Hypothesis Testing"**.
Before a fix, read the matching `../.vendor/gstack/investigate/sections/` file: `flake`
(intermittent/CI-only), `polluter` (passes alone, fails in suite), `race` (timing, shared
state), `eval-bisect` (metric regressed between revisions), `blast-radius` (shared helper
or format).

## Fixing

7. **Same shape elsewhere?** Confirm the violated invariant at each candidate, fix
   confirmed sites within scope, report the rest. Making the class mechanically
   enforced (rule, audit, gate, baseline) is `bug-class-audits`. A repair or fallback that rewrites
   an object must still satisfy its contract (length caps, enums): replace capped text,
   never append, and parse the repaired object in the test; one bad item never fails the batch.
8. **Prove regression sensitivity.** Same check, inputs and environment before and after
   the fix: fails for the intended defect, then passes. A setup failure (missing import,
   credential, startup) proves nothing. Already fixed? Run the check against the old
   revision in a scratch worktree; if no before-proof is practical, say so. No correct seam to test through is itself a finding. When the check
   asserts an absence or rejection, add a control input that must succeed. Forced the red by
   mutation? Diff against a pristine copy to prove it landed. The test meets
   [LEAN-SUITE](../effective-development/LEAN-SUITE.md).
9. **Verify the final tree.** Before choosing regressions or reusing evidence, read
   [effective-development](../effective-development/SKILL.md); run required gates.

## Related

[agent-orchestration](../agent-orchestration/SKILL.md) — lead owns diagnosis and quality.
`senior-operator` — reasoning; `bug-class-audits` — enforcement; `metric-integrity` — numbers.
