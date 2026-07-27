---
name: shipping-changes
description: Ships verified work end to end — run the gates, review the diff, bump version and changelog, commit and push. Use when the user says "ship it", "land this", "đẩy lên", "commit và push", "merge về main", or when a change is finished and needs to land. Enforces the house rules that upstream tooling gets wrong: main only with no feature branches, commits under the operator's own identity with no assistant attribution, and pre-commit/pre-push hooks that must actually pass.
---

# Shipping changes

Thin wrapper over gstack's `ship`. Upstream owns the mechanics; this file owns the rules
that upstream gets wrong for this operator, and they win on every conflict.

## House rules — non-negotiable

1. **main only.** Never create a feature branch. Never leave a stray branch behind. If
   upstream's flow proposes a branch + PR, skip that and commit to main directly.
   Other agents work this machine concurrently — main is the shared surface.
   *(Standing instruction, re-asserted repeatedly: "TẤT CẢ PHẢI ĐƯỢC Ở TRÊN MAIN VÀ
   XOÁ HẾT ĐÁM BRANCH RÁC".)*
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
   composition, push), read `~/.shared-ai-skills/ship/SKILL.md` — specifically its
   **"Skill routing"** and **"Completeness Principle — Boil the Ocean"** sections — and
   follow it with the house rules above applied.
5. Verify after: `git log --oneline -1`, `git status` clean, and the remote actually
   advanced.

## When NOT to use this

Nothing lands without the operator asking. "Ship" is an instruction, never an inference
from "the work looks done".
