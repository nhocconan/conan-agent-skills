---
name: dev-env-lifecycle
description: Own the full lifecycle of everything a run starts — dev servers, workers, containers, tunnels, ports, temp files, backups. One command brings the stack up, one brings ALL of it down, and nothing survives that the operator did not ask for. Use before starting any local stack, after finishing a task that started one, when handing a machine back, when the user says "stop dev", "stop hết", "start lại", "sao còn process", "port bị chiếm", "máy đầy rác", "cleanup", "teardown", or before any delete of files/volumes/backups. Prevents the residue that makes the next run fail on a port that is already bound.
---

# Dev-Environment Lifecycle

Anything a run starts, the run owns. The failure this prevents is not dramatic — it is a
second `pnpm dev` that dies on `EADDRINUSE`, a worker from three tasks ago still consuming
a queue, a 4 GB backup nobody deleted, a container holding a volume the next migration
needs. Each is cheap alone; together they make a machine untrustworthy, and the operator
pays for the diagnosis every time.

## The contract

1. **Inventory before you start.** Record what is already running on the ports and paths
   you are about to use. You are responsible for what *you* start, and you must not kill
   what you did not. If a port is already bound, find out by whom before taking it.
2. **Up and down are one artifact each.** The stack gets a single documented entry point
   for start, one for stop, one for status — a script, a compose file, a make target,
   whatever the repo already uses. Two commands that must be run in the right order is a
   design that will be run in the wrong order.
3. **Down means all of it.** Stop covers every process the up path created, not the
   foreground one: background workers, schedulers, queue consumers, watchers, tunnels,
   sidecar containers, port-forwards. The test is mechanical — after `down`, the inventory
   from step 1 matches the starting state.
4. **Verify, do not assume.** A stop command that exits 0 has proved nothing. Re-check the
   ports (`lsof -i`, `ss -ltnp`), the process table, and the container list. A process that
   ignored SIGTERM is still running.
5. **Leave no residue.** Temp exports, dumps, generated fixtures, screenshot batches and
   `.pid`/`.lock` files created by the run get removed or moved to a declared scratch
   location. Disk that fills silently is the same failure as a port that stays bound.
6. **Ask before deleting anything you did not create.** Backups, volumes, databases, and
   anything under a user directory require an explicit confirmation naming what will be
   deleted and its size. "I removed the old backups" after the fact is not a confirmation.
   Once confirmed, delete the *files*, not just the index entry that pointed at them —
   a retention policy that unlinks a record and leaves 40 GB on disk is a leak.
7. **Hand the machine back clean.** When the task ends, state which processes are still
   running and why, or state that none are. Silence reads as "nothing is running" and is
   the most expensive thing to be wrong about.

## Writing the up/down artifact

- `status` is the important one and the one usually missing. It answers "is anything of
  mine running?" in one command and is what steps 4 and 7 depend on.
- Track PIDs the stack actually owns (a pidfile or a process group), rather than matching
  process names — a name match kills the operator's unrelated editor server eventually.
- Make `down` idempotent and safe to run when nothing is up. It will be run that way.
- Make `up` refuse to start on top of itself. Detect the running stack and either attach
  or fail with a clear message; two copies of a queue consumer corrupt work silently.
- Prefer stopping by the same mechanism that started: compose down for compose up, the
  supervisor for a supervised process. Reaching for `kill -9` first hides shutdown bugs.
- If the stack binds privileged or shared resources (a fixed port, a system service, a
  shared database), say so in the artifact's header — those are the ones that collide.

## Ephemeral by default

Data a run generates for its own purposes — seeded fixtures, masked exports, capture
batches — lives in a declared, gitignored scratch path, is regenerable from a command,
and is removed on `down`. Anything that must outlive the run gets stated explicitly as
durable, with a location the operator chose. If you cannot say which of the two a file is,
it is scratch, and it goes.

## Production is not dev

The same discipline inverts on a production or shared host: never stop what you did not
start, never restart a service to "clean up", and never delete a backup at all. On a host
whose name or context carries `prod`, the lifecycle contract narrows to inventory and
report — changes to running services need an explicit instruction naming the service.

## Output

Report, in one place: what was started (processes, ports, containers), what was stopped,
what is still running deliberately, what was deleted (with sizes) and what was kept, and
the `status` output proving the end state. If anything refused to die, say which and why.
