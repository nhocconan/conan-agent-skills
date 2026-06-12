---
name: git-rescue
description: Standard recovery procedure for git failures — pull/push failed, merge conflicts, pre-commit/pre-push hook rejections, diverged main. Use whenever the user says "git pull failed", "merge conflict", "push failed", "fix git", or a commit/push is rejected by hooks.
---

# Git Rescue

The user is a **solo dev working directly on main** across many machines (laptop + prod servers pulling from GitHub). "git pull failed, fix it" is a weekly event. Resolve it safely and completely — don't ask them to run commands.

## Procedure
1. **Diagnose first**: `git status`, `git log --oneline -5 HEAD origin/main`, `git fetch`. Identify which case: diverged history, uncommitted changes blocking pull, untracked-file collision, hook failure, or auth issue.
2. **Protect local work before anything else**: if there are uncommitted changes, commit them as WIP or stash with a named message. Never checkout/reset over uncommitted work.
3. **Resolve**:
   - Diverged: `git pull` (merge, not rebase — history rewrites confuse the other machines) and resolve conflicts preserving BOTH intents; when one side is clearly newer work by the user, prefer it, and say which side won per file.
   - Untracked collision: move the local file aside, pull, then diff and merge manually.
   - Generated/lockfiles conflicts (pnpm-lock, drizzle/prisma snapshots, next-env.d.ts): regenerate rather than hand-merge.
4. **Hook failures**: fix the underlying lint/type/test failure properly. `--no-verify` only with the user's explicit OK, and note the debt.
5. **Verify done**: clean `git status`, branch up to date with origin, and the app still builds/starts (a bad conflict resolution that breaks dev is worse than the conflict).
6. **Commit & push** under `Tien Le <nhocconan@gmail.com>`. Never force-push without explicit confirmation; if force-push is unavoidable, explain what gets overwritten and remind that prod machines must re-pull cleanly (`git fetch && git reset --hard origin/main` ONLY if prod has no local changes — check first).

## Report
One short summary: what was wrong, how it was resolved, which files had conflicts and what won, and confirmation the working tree is clean and the app starts.
