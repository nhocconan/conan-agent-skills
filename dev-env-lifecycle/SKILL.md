---
name: dev-env-lifecycle
description: >-
  Use when a machine is overloaded or littered by what a run started — "load cao",
  "giảm tải server", "chỉnh resources", "stop dev", "stop hết", "start lại", "sao còn
  process", "port bị chiếm", "máy đầy rác", "cleanup", "teardown" — or before deleting
  files/volumes/backups. Inventories every dev server, worker, container, tunnel, port
  and temp file a run started; one command up, one brings ALL down; caps concurrent
  browsers/workers to the operator's share.
---

# Dev-Environment Lifecycle

Anything a run starts, the run owns. Inventory existing resources before claiming
ownership; stale workers, occupied ports and abandoned files all survive a shell exit.

## Use the declared runtime

Read the repo's start/deploy entrypoint and identify the host or container, service,
working directory, Compose files and project name before running commands. Run imports,
migrations and load-bearing verification in that target runtime; a host-shell test does
not prove the deployed service uses the same dependencies, config or mounted files.
Preserve the requested delivery mechanism (such as a mounted config override); do not
substitute an image rebuild or service restart without checking scope and necessity.
A deploy that builds from the working tree starts only from a clean tree, and nobody
edits that tree until it ends; prefer building from a committed snapshot.

## The contract

1. **Inventory before you start.** Record what is already running on the ports and paths
   you are about to use. You are responsible for what *you* start, and you must not kill
   what you did not. If a port is already bound, find out by whom before taking it.
   The operator's share is enforced by cgroup, not promises: root runs
   [`scripts/colocate.sh`](scripts/colocate.sh) `apply` once (production `MemoryLow`; agent
   `CPUWeight`/`MemoryHigh`/`MemoryMax`/`TasksMax`; systemd-oomd on `user@.service`). Each heavy
   job runs as `systemd-run --user --scope -p CPUWeight= -p MemoryHigh= -p MemoryMax= -p
   RuntimeMaxSec=`, sized by effective-development's `host_load.py`; weights, never `CPUQuota`
   (quotas throttle an idle host). Verify in the scope's cgroup files.
2. **One entrypoint each for up, down and status.** Use the repo's script, Compose or
   Make target; encode required ordering there.
3. **Down means all of it.** Stop covers every process the up path created, not the
   foreground one: background workers, schedulers, queue consumers, watchers, tunnels,
   sidecar containers, port-forwards, and detached helpers (`setsid`, `nohup`, `disown`),
   which must share a kill path with their watchdog. The test is mechanical — after `down`, the inventory
   from step 1 matches the starting state.
   A test runner that launches the app through a wrapper (`webServer` command via a
   package runner or `tsx`) leaves grandchildren holding ports after a crash or kill. Start
   it in its own process group and kill the group; give every post-run step (report merge,
   teardown) a timeout so a hang cannot skip the cleanup trap.
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
7. **Hand the machine back clean.** State which run-owned processes remain and why,
   or verify that none remain.

## Writing the up/down artifact

- `status` is the important one and the one usually missing. It answers "is anything of
  mine running?" in one command and is what steps 4 and 7 depend on.
- Track a run ID, PIDs with start times, container IDs, and owned paths (a manifest or process group), rather than matching
  process names — a name match kills the operator's unrelated editor server eventually.
- Make `down` idempotent and safe to run when nothing is up.
- Make `up` refuse to start on top of itself. Detect the running stack and either attach
  or fail with a clear message; two copies of a queue consumer corrupt work silently.
- Stop by the mechanism that started: compose down for compose up, the supervisor for a
  supervised process; `kill -9` first hides shutdown bugs.
- Name privileged or shared resources (fixed port, system service, shared database) in the artifact's header.

## Ephemeral by default

Run-generated data (seeded fixtures, masked exports, capture batches) lives in a declared,
gitignored scratch path, is regenerable, and is removed on `down`. Anything that must outlive the run gets stated explicitly as
durable, with a location the operator chose. If ownership or durability is unclear, preserve the file and resolve it before deletion.

## Production is not dev

The same discipline inverts on a production or shared host: never stop what you did not
start, never restart a service to "clean up", and never delete a backup at all. Use explicit deployment context; a hostname alone is not a reliable classification. On a production or uncertain shared host, the lifecycle contract narrows to inventory and
report — changes to running services need an explicit instruction naming the service.

## Output

Report in one place: started (processes, ports, containers), stopped, deliberately still
running, deleted (with sizes) and kept, and the `status` output proving the end state.
Say which resource refused to die and why.
