## Cost

Cost of a call is the context it re-reads, so the levers are context size and turn count,
not prompt length. Rules live in their owners; state the expected turns per agent and the
stop condition in the brief.

- Turn caps, fresh agent per task, two failed loops: [routing](routing.md#work-nature--tier), [quality gate](quality-gate.md)
- Strongest model writes specs and reviews; the default builder implements: [routing](routing.md#work-nature--tier)
- Lead context: hand off at 120k: [tracking](tracking.md)
- Polling, long output, return size: [brief](brief.md), [fan-out patterns](../FANOUT-PATTERNS.md)
- Resume instead of re-spawn: [tracking](tracking.md)
- Heavy jobs on one host: [shared host](../../effective-development/SHARED-HOST.md)

### Paid third-party jobs

- Estimate spend before running: unit price x count; show it.
- Run the smallest or cheapest configuration first and show its output before scaling.
- Caps, timeouts and rate limits come from vendor docs or the operator, never invented.
- While a job is running, wait on its status once; do not re-submit or retry it.
- Record each paid call (job id, cost) in the results file.
- Stop and report before exceeding the operator's stated budget.
