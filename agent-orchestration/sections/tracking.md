## §7. Track and resume

Keep a plan and ledger in the repo's declared ignored working directory, for
example `.agents/<task>-plan.md`. If durable documentation was requested, use the
requested path. Templates are in [TEMPLATES.md](../TEMPLATES.md).

Record goal, dependencies, actual models/effort when exposed, owned files,
acceptance checks, status, artifacts, and Astra's verdict. Unknown cost and
hypothetical solo timing remain unknown.

States: `pending → briefed → running → reviewing → done | failed | skipped | blocked`.
Only Astra marks done after acceptance. Record partial results promptly.
Failed dependencies block their dependents; independent work continues.

On resume, reconcile the ledger with the current diff, running processes, tool
results, and external state. Preserve useful partial edits. Recheck completed
nodes if dependencies or artifacts changed. Retry failed nodes only after their
cause is addressed, and do not replay external writes blindly.

After compaction, use both the saved plan and the latest user steering. The plan
does not override newer instructions or authorize more work.

## §8. Continue and communicate

Do useful independent work while workers run. Use the supported completion/wait
mechanism, with waits no longer than 60 seconds, and send meaningful updates at
least every 60 seconds during ongoing work unless the product specifies another
monitoring cadence. State observed progress, remaining uncertainty, and next checks;
do not invent ETAs or claim a launch without a successful tool result.

A helper crash calls for inspection and recovery, not automatic user escalation.
End when complete or when required information/authority is unavailable after
safe independent work is exhausted. Clearly name incomplete nodes and why.

Respect budget and concurrency limits. Record deliberate sampling or skipped
coverage; do not imply exhaustive work. Repeated unchanged external state is
normal for monitoring and is not a blocker by itself.
