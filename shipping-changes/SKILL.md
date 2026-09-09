---
name: shipping-changes
description: >-
  Ships verified work end to end — run the gates, review the diff, bump version and changelog,
  commit and push. Use when the user says "ship it", "land this", "đẩy lên", "commit và push",
  "merge về main". Follow repository branch/review controls, preserve the operator's
  commit identity, and require passing hooks. Completion alone does not authorize shipping.
---

# Shipping changes

Thin wrapper over gstack's `ship`. Upstream owns the mechanics; this file owns the rules
for this operator. User instructions and repository controls take precedence.

## House rules — non-negotiable

1. **Follow the repository's branch and review policy.** Direct-to-main is appropriate
   only when authorized and compatible with branch protections. Preserve existing
   branches and user work; do not delete branches as automatic cleanup.
2. **Commit identity is the operator's.** No assistant co-author trailer, no assistant
   name anywhere in the message. *("Đảm bảo mọi thứ dưới tên tao, đừng có dính gì Claude.")*
3. **Hooks must pass, not be skipped.** A `--no-verify` is a failed ship, not a fast one.
   If a hook fails, fix the cause. *("tại sao không tuân thủ definition of done là phải
   check các hook commit, push?")*
4. **Never pipe the gate through `tail`/`head`/`grep`** — the exit code becomes the pipe's
   and a broken build reads as green. Redirect and check both signals:
   `cmd > run.log 2>&1; echo "EXIT=$?"`, then grep the log for a positive marker.
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
5. Verify after: `git log --oneline -1`, `git status` clean, and the remote actually
   advanced.

## When NOT to use this

Nothing lands without the operator asking. "Ship" is an instruction, never an inference
from "the work looks done".
