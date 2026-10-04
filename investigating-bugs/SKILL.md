---
name: investigating-bugs
description: Finds the root cause of a defect before changing anything — reproduce it, locate the mechanism, prove the diagnosis, then fix the class rather than the instance. Use when something is broken, failing, flaky, slow, or behaving unexpectedly; when the user says "sao lại lỗi", "tại sao", "bị sai rồi", "lại bị nữa", "debug", "investigate", "vẫn chưa được"; or before any fix whose cause is not already proven. Prevents the guess-and-patch loop where a symptom is suppressed and the real fault ships.
---

# Investigating bugs

Thin wrapper over gstack's `investigate`. Upstream owns the search procedure; this file
owns the discipline that decides whether the answer is trustworthy.
Paths below are relative to this skill's real directory in the repo checkout
(`~/.conan-agent-skills` by default — resolve the symlink first). `refsync.py ensure`
fetches the vendored upstream files; if one is absent, say so and apply the rules in
this file instead of guessing upstream's content.

## The rule that matters most

**An unproven diagnosis is a hypothesis.** Preserve the original failure evidence.
Use isolated tests, temporary instrumentation or a scratch worktree to distinguish
competing causes; remove diagnostic changes before delivery. If reproduction is
unavailable, continue safe probes and label the limits instead of declaring a fix.

## Before touching anything

1. **Verify the presupposition.** "X is broken" may be false, or broken somewhere else.
   Check that the reported behaviour is real before hunting its cause.
2. **Reproduce it** — a failing test, a command with its output, a screenshot. This
   artifact is what proves the fix later. Without it, "fixed" is unfalsifiable.
3. **Read the actual error.** Full output, not the last line. The pipe-swallows-exit-code
   trap applies: `cmd > run.log 2>&1; echo "EXIT=$?"`.

## Diagnosing

4. **Locate the mechanism, not the vicinity.** Name the specific line, state, or ordering
   that produces the symptom, and be able to explain why it produces *this* symptom and
   not a different one.
5. **Verify by re-deriving, not by recognising.** A pattern that looks familiar is the
   most common way a wrong diagnosis survives review — see `senior-operator`
   OPERATING-MANUAL §4.
6. **Label known vs guessed** in the write-up. Anything unverified is marked unverified.

For the search mechanics — log/trace navigation, bisecting, tooling — read
`../.vendor/gstack/investigate/SKILL.md`, particularly its **"Phase 1: Root Cause
Investigation"**, **"Phase 2: Pattern Analysis"** and **"Confusion Protocol"** sections.

## Fixing

7. **Is it a class?** Search for the same shape and confirm the violated invariant
   at each candidate. Fix confirmed sites within scope; report unrelated ones.
   Hand off recurring classes to `bug-class-audits`.
8. **Prove the fix against the reproduction from step 2**, then run the relevant
   regression checks and required repository gate. Size optional checks with
   `effective-development`; broaden for uncertain coverage or a new failure.

## Related

[agent-orchestration](../agent-orchestration/SKILL.md) — subsystem work: the harness lead
owns diagnosis and quality; workers survey and fix
([routing](../agent-orchestration/sections/routing.md)).
`senior-operator` — how to reason under ambiguity. `bug-class-audits` — turning a confirmed class into a mechanical audit. `metric-integrity` — when the "bug" is a wrong number on a dashboard.
