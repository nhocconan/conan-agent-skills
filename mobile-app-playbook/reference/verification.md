## §5. Verification discipline — where projects actually die

The bugs that kill releases are the ones your gates don't cover. These rules exist
because each was paid for:

### 5.1 Fake green (the worst class)

Piping a build through `tail`/`head`/`grep` makes the exit code the PIPE's exit code.
A missing SDK produced "BUILD SUCCESSFUL"-looking output for SIX stages once; nothing
had compiled. **Rule: never pipe build commands. Redirect to a log
(`> build.log 2>&1; echo EXIT=$?`), then check BOTH the exit code and a positive marker
(`BUILD SUCCESSFUL`, test counts) in the log.** An agent claiming green counts for
nothing until the orchestrator has re-run the command itself (§OP).

### 5.2 The per-stage gate (run ALL of it, every stage, no exceptions)

For a KMP/CMP project the minimum is: unit tests for EVERY flavor × the assemble for
EVERY flavor × the iOS framework link × (if backend touched) backend lint+test+build.
The stage isn't done until all are green AT HEAD — not green on the files you think
you touched.

**Bootstrap on a cold repo (do this FIRST, before any change):** derive the concrete
gate and freeze it into a script so you never re-derive it wrong. Recipe:
`./gradlew projects` (module list) → `./gradlew tasks | grep -E "test.*UnitTest|assemble|linkDebugFramework"`
(the real task names, including every flavor) → check `package.json`/`Makefile`/CI
config for the backend/web halves → write the full command list into `scripts/verify.sh`
with the §5.1 exit-code discipline baked in → run it once on a clean HEAD to prove the
baseline is green. From then on, "the gate" = that script, and any new module/flavor
must be added to it in the same PR that introduces it.

### 5.3 Behavior verification outranks green gates

Green gates prove you didn't break what the gates cover. After any UI/flow change:
launch the real app (emulator/simulator), traverse the changed journey, screenshot it.
Where simulator input automation is unavailable (common on iOS: no idb, no Accessibility
permission), build a **debug-only capture harness** into the app: launch args select a
screen, skip tutorials/prompts, autopilot gameplay. It pays for itself the first week
— and it must be compiled out of release builds (§6 debug-hook rule).

### 5.4 Bot-verify game difficulty (genre-specific but generalizes)

Hand-tuning difficulty is guessing. Write a headless bot that plays the real engine
thousands of runs across the whole level range, and assert invariants: every level
reachable, no level with median-death-at-zero, gap/reaction-time floors ≥ human limits,
difficulty monotonic where designed. This converts "feels hard" into a regression test —
and it once caught levels that were mathematically impossible.

### 5.5 Determinism as a test target

Same seed ⇒ identical obstacle/event IDs across two runs of the engine. Assert it in CI.
The day this silently breaks, daily challenges stop being fair and nobody notices for weeks
(silent × wide blast radius = highest risk class).

### 5.6 Class, not instance

Any bug that greps to more than one call site, or whose shape you've seen before, gets:
fix every site + a written rule + a mechanical audit script wired into pre-push.
See `bug-class-audits`.

**Gate §5:** the project has a single mirror command (`verify.sh` or equivalent) that
runs the full §5.2 set; the fake-green rule is followed in every script; a behavior
check on the touched journey is recorded (screenshot/film) for the stage.

---
