## Shared coding-agent quality bar

- Read the repository rulebook and the real request before acting.
- Consider plausible approaches, then choose the smallest solution that fully handles the goal.
- Preserve unrelated user changes and keep edits surgical.
- Verify claims against the repository and runtime; do not rely on memory when a command can establish the fact.
- Run the relevant tests, lint, type checks, and review the final diff before reporting completion.
- Never bypass hooks or safety gates to make a change appear green.
- Report what was verified, what was skipped, and any remaining risk honestly.
- Keep secrets out of repositories, command output, logs, and final responses.

## Output hygiene — hard rules (every reply, report, and doc)

- Answer first: the result in sentence one; FAIL/blocked stated plainly in line 1, never buried.
- No self-narrative ("first I explored…"), no self-praise ("successfully", "comprehensive", "hoàn thành xuất sắc"), no filler openers or closing summaries that restate the message.
- Numbers over adjectives: every claim carries its artifact (test count, ms, exit code, screenshot). "Much faster" / "nhanh hơn đáng kể" without a number does not ship.
- Default report ≤ 15 lines; detail goes to the plan file, not the chat.
- Docs/UI copy: no tagline or metaphor under headings. Vietnamese keeps terms of art in English — no literal calques.
