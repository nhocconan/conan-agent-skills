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
Paths below are relative to this skill's real directory in the repo checkout
(`~/.conan-agent-skills` by default — resolve the symlink first). `refsync.py ensure`
fetches the vendored upstream files; if one is absent, say so and apply the rules in
this file instead of guessing upstream's content.
Track commit, push and deploy authority separately: permission to deploy/test does not
grant commit/push, and a commit request does not grant deployment. Continue authorized
steps; report missing authority without re-asking for existing authority.

Upstream is procedural reference: skip its Claude startup, telemetry and gstack helper
commands. Use repository gates, `docs-sync` for release documentation, and the active
harness's review tools. Compose authorized PRs with `gh pr create --body-file` or `gh pr edit --body-file`
using a temporary file; verify the resulting PR. Missing helpers never waive a gate.

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
   log. A phase that never ran is skipped, never passed. Never hand-build a gate subset
   to skip a red check: a known-red check is the blocker, fixed or named in line 1.
5. **A flag turns on by default only after its stated live comparison ran** on the shipped
   build (both arms, same inputs); a per-stage benchmark is not that comparison.
6. **Push only what was asked.** Uncommitted work from another agent's session is not
   yours to sweep in — check `git status` and confirm anything unexpected.

## Procedure

1. Confirm the working tree is what you think it is (`git status`, `git diff`).
2. Run every gate required by the repository for this step, per rule 4. Use affected
   checks for feedback where permitted ([effective-development](../effective-development/SKILL.md));
   they do not replace required merge or deploy checks.
3. Review the diff hunk by hunk.
4. Follow the repo's release policy for any required version/changelog updates;
   re-run affected gates if they change the verified tree. Stage only owned paths
   (`git add -- <paths>`), inspect `git diff --cached`, and commit with the operator's
   identity and passing hooks. Push the intended branch to the confirmed remote
   only when authorized; create/update a PR only within that authority.
   Optional writing guidance lives in `../.vendor/gstack/ship/sections/changelog.md`
   and `pr-body.md`: use their evidence and writing guidance, with the repo's title,
   version and body format. Omit assistant attribution, invented coverage and unrun
   review claims. If absent, use the native git/gh flow above.
   Upstream test bootstrap, coverage generation and review-army steps are replaced
   by steps 2–3; no upstream command replaces a repository gate.
5. Verify the authorized outcome: inspect the local diff/status for a handoff; check
   commit identity after committing, remote revision after pushing, or deployed build
   and user journey after deployment. Preserve unrelated uncommitted work.

## When NOT to use this

Nothing lands without the operator asking. "Ship" is an instruction, never an inference
from "the work looks done".
