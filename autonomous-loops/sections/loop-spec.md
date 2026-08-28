## Loop spec — the file that makes it a loop

One file per loop, in the repo, beside the skill it invokes (`docs/loops/<name>.md` or
the skill's own directory). Reviewed like code; a change to it is a PR.

```markdown
# loop: nightly-data-recon

RUNG: 3 (headless, read-only)            # current rung; bump only per the escalation law
TRIGGER: launchd 02:30 local, Mon–Sat     # or: push to main / PR opened / /loop 4h / routine <id>
PROMPT: skills/nightly-data-recon/SKILL.md   # frozen in repo; the loop runs THIS, not chat
GATE:   pnpm run verify:data > recon.log 2>&1; echo "EXIT=$?"
        pnpm run verify:rls  > rls.log   2>&1; echo "EXIT=$?"
        green = both EXIT=0 AND recon.log contains "reconciled" — NOT "the run finished"
OUTPUT: docs/loops/reports/nightly-data-recon-<date>.md (one page; first line = verdict)
STOP:   max 1 iteration · 20 min wall-clock · no writes to product code
BRAKES: skip if .dev-server.pid exists (humans are on the box) · skip if last report < 20h old
WRITE:  none  (rung 5 would be: open a PR; never merge)
OWNER:  <operator> — reads the report each morning; three ignored reports = demote or delete
HISTORY:
  - 2026-08-28 rung 1, run by hand ×7, all outputs read
```

The `HISTORY` block is the escalation evidence: a loop with no history has not earned
its rung. When a loop is demoted or deleted, say why in the last history line — the next
person will otherwise re-create it.
