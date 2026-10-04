## Loop spec

Keep a reviewed project spec with the installed command/configuration and version.
Use real project checks; this example is synthetic:

```markdown
NAME: nightly-data-recon
TRIGGER: 02:30 UTC, Mon–Sat; identity: <scheduler account>
PROMPT: skills/nightly-data-recon/SKILL.md
GATE: ./scripts/check-nightly-recon.sh; nonzero on failure
INPUT: revision + working diff + external data snapshot/window
OUTPUT: .agents/loops/nightly-data-recon-<run-id>.md; first line = gate verdict
STOP: max 1 iteration, 20 min; no product edits
BRAKES: atomic resource lock; skip completed-success input keys only
RETRY: transient failure only within STOP; reconcile partial effects before replay
WRITE: local report only
OWNER: <operator>; reviews results
EVIDENCE: representative pilot runs + forced failure outcomes
REMOVE: <exact disable/remove command>; STOP RUNNING: <cancellation command>
```

The gate must propagate failure. A repository script can preserve both statuses:

```bash
#!/usr/bin/env bash
pnpm run verify:data > recon.log 2>&1
recon_status=$?
pnpm run verify:rls > rls.log 2>&1
rls_status=$?
if [ "$recon_status" -ne 0 ] || [ "$rls_status" -ne 0 ]; then
  exit 1
fi
rg -q 'reconciled' recon.log || exit 1
```

Choose a marker proving the required assertion ran. Bind evidence to INPUT; changed
inputs require fresh checks. Record environment, logs and demotion/removal reasons.
A drafted spec is not an installed scheduler.
