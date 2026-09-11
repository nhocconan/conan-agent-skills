---
name: shipping-changes
description: >-
  Ships verified work end to end — run the gates, review the diff, bump version and changelog,
  commit and push. Use when the user says "ship it", "land this", "đẩy lên", "commit và push",
  "merge về main". Follow repository branch/review controls, preserve the operator's
  commit identity, and require passing hooks. Completion alone does not authorize shipping.
---

# Shipping changes

Wraps gstack's `ship`; user instructions and repository controls take precedence.
Track commit, push and deploy authority separately: permission to deploy/test does not
grant commit/push, and a commit request does not grant deployment. Continue authorized
steps; report missing authority without re-asking for existing authority.

## House rules — non-negotiable

1. **Follow the repository's branch and review policy.** Direct-to-main is appropriate
   only when authorized and compatible with branch protections. Preserve existing
   branches and user work; do not delete branches as automatic cleanup.
2. **Commit identity is the operator's.** No assistant author or co-author attribution.
3. **Hooks must pass, not be skipped.** A `--no-verify` is a failed ship, not a fast one.
   If a hook fails, fix the cause.
4. **Capture each gate's exit status before filtering its output.** A display filter
   can hide failure; a no-match `grep` before `&&` can silently skip the next required
   step. Run required phases separately, record their statuses, and inspect the saved
   log. A phase that never ran is skipped, never passed.
5. **Push only what was asked.** Uncommitted work from another agent's session is not
   yours to sweep in — check `git status` and confirm anything unexpected.

## Procedure

1. Confirm the working tree is what you think it is (`git status`, `git diff`).
2. Run the project's real gate — tests, typecheck, lint — per rule 4.
3. Review the diff hunk by hunk. Delegation moves the typing, not the accountability.
4. For the mechanics beyond this point (version bump, changelog, commit message
   composition, push), read `../.vendor/gstack/ship/SKILL.md` — specifically its
   **"Section index — Read each section when its situation applies"** and
   **"Completeness Principle — Boil the Ocean"** sections — then read the on-demand
   section that index names for the step you are on — they live under
   `../.vendor/gstack/ship/sections/` (changelog wording in `changelog.md`,
   PR body in `pr-body.md`) and since v1.71 no longer load with the skill body —
   and follow it with the house rules above applied. `refsync.py ensure` fetches these.
5. Verify the authorized outcome: inspect the local diff/status for a handoff; check
   commit identity after committing, remote revision after pushing, or deployed build
   and user journey after deployment. Preserve unrelated uncommitted work.

## When NOT to use this

Nothing lands without the operator asking. "Ship" is an instruction, never an inference
from "the work looks done".
