---
name: investigating-bugs
description: Finds the root cause of a defect before changing anything — reproduce it, locate the mechanism, prove the diagnosis, then fix the class rather than the instance. Use when something is broken, failing, flaky, slow, or behaving unexpectedly; when the user says "sao lại lỗi", "tại sao", "bị sai rồi", "lại bị nữa", "debug", "investigate", "vẫn chưa được"; or before any fix whose cause is not already proven. Prevents the guess-and-patch loop where a symptom is suppressed and the real fault ships.
---

# Investigating bugs

Thin wrapper over gstack's `investigate`. Upstream owns the search procedure; this file
owns the discipline that decides whether the answer is trustworthy.

## The rule that matters most

**A diagnosis you have not reproduced is a hypothesis.** Do not edit code to test a
theory — that overwrites the evidence. Reproduce first, then explain the mechanism, then
fix. If you cannot reproduce it, say so plainly and state what you would need to.

## Before touching anything

1. **Verify the presupposition.** "X is broken" may be false, or broken somewhere else.
   Check that the reported behaviour is real before hunting its cause.
2. **Reproduce it** — a failing test, a command with its output, a screenshot. This
   artifact is what proves the fix later. Without it, "fixed" is unfalsifiable.
3. **Read the actual error.** Full output, not the last line. The pipe-swallows-exit-code
   trap applies here too: `cmd > run.log 2>&1; echo "EXIT=$?"`.

## Diagnosing

4. **Locate the mechanism, not the vicinity.** Name the specific line, state, or ordering
   that produces the symptom, and be able to explain why it produces *this* symptom and
   not a different one.
5. **Verify by re-deriving, not by recognising.** A pattern that looks familiar is the
   most common way a wrong diagnosis survives review — see `senior-operator`
   OPERATING-MANUAL §4.
6. **Label known vs guessed** in the write-up. Anything unverified is marked unverified.

For the search mechanics — log/trace navigation, bisecting, tooling — read
`~/.shared-ai-skills/investigate/SKILL.md`, particularly its **"Skill routing"** and
**"Confusion Protocol"** sections.

## Fixing

7. **Is it a class?** Grep for the same shape elsewhere. More than one hit — or the same
   shape of bug appearing a second time — means fix every site and write the rule down.
   Hand off to `bug-class-audits`.
8. **Prove the fix against the reproduction from step 2**, then re-run the full gate. A
   fix that only fixes the symptom you were shown is a fix that ships the bug.

## Related

`senior-operator` — how to reason under ambiguity. `bug-class-audits` — turning a
confirmed class into a mechanical audit. `metric-integrity` — when the "bug" is a wrong
number on a dashboard.
