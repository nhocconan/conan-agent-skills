---
name: remote-host-access
description: Diagnose and fix "the port is open but it still won't connect" on any remote host — VPS, cloud VM, container host, home server — by descending one layer at a time instead of guessing, and set up durable agent sessions on those hosts. Covers name resolution, TCP reachability, cloud security groups, host firewalls (ufw / firewalld / CSF / iptables-legacy vs nftables / hypervisor firewalls), systemd socket-activated services, and the service's own bind address. Use when SSH or any service refuses to connect, when a rule was added and nothing changed, when the user says "không connect được", "mở port rồi mà vẫn lỗi", "ssh timeout", "connection refused", "firewall", "remote server", or when running a long task on a remote box.
---

# Remote Host Access

The reported symptom is almost always "I opened the port and it still doesn't work." That
sentence contains an unverified presupposition — that the rule which was added is the rule
that is being consulted. It usually is not. Guessing costs a session; descending the layers
costs five minutes and terminates.

## Read the failure before touching anything

The client's error already names the layer, and the two common ones mean opposite things:

- **Timeout / no route** — the packet is being dropped silently. A firewall, a security
  group, or a wrong address. Nothing is listening *or* nothing is allowed to reach it.
- **Connection refused** — the packet arrived and the host actively rejected it. The
  network path works; nothing is bound on that port, or it is bound to the wrong interface.
  Firewall rules are almost never the cause of a refusal.
- **Authentication / handshake failure** — the network is fine. Stop debugging the network.

Never edit a firewall rule in response to `connection refused`.

## The ladder — descend, do not skip

Run each rung, record the result, and only continue while the answer is "fine". The first
rung that fails is the bug; rungs below it are not evidence.

1. **Name → address.** Resolve the host and confirm the address is the one you think.
   A stale DNS record, a CDN/proxy in front, or an IPv6 AAAA record answering first is a
   frequent and invisible cause. Test the literal address, and test v4 and v6 separately.
2. **Path to the port.** From the client, probe TCP directly. From elsewhere too — a
   second network distinguishes "the host blocks the world" from "the host blocks you"
   (residential ISP blocks, corporate egress rules, an IP-allowlist you are not on).
3. **The perimeter you cannot see from inside.** Cloud security groups, VPC/network ACLs,
   provider-level firewalls and hypervisor firewalls are enforced *outside* the guest and
   are invisible to every command you can run on the host. Check them from the provider's
   control plane. A host that shows an ACCEPT rule and still times out is this, nearly
   every time.
4. **The host firewall — and which one is actually in charge.** This is the rung that
   eats sessions. Multiple firewall front-ends can be installed at once, and the one you
   edited may not be the one enforcing:
   - `iptables` may be a shim over nftables. Inspect *both* the legacy tables and the
     nft ruleset; a rule visible in one and absent in the other explains a "rule exists,
     traffic dropped" contradiction.
   - Managed front-ends (ufw, firewalld, CSF, a panel's own firewall, a hypervisor
     firewall) regenerate the underlying rules and will silently discard a rule you added
     by hand at the layer below. Edit through the front-end that owns the host, then
     reload it, then re-read the raw ruleset to confirm the rule actually landed.
   - Check the chain *policy* and rule *order*, not just the presence of an ACCEPT: an
     ACCEPT below a broad DROP never runs. Read rules with counters; a rule whose packet
     counter stays at zero while you are testing is not being hit.
   - Check the OUTPUT and FORWARD chains, not only INPUT, for anything containerised.
5. **Is the service actually listening, and where.** List listening sockets with the
   owning process. A service bound to `127.0.0.1` is unreachable from outside no matter
   how open the firewall is, and this is the single most common cause of `connection
   refused` on a correctly-configured host. Fix the service's bind address, not the
   firewall.
6. **Socket activation and the unit that really runs.** On modern systemd hosts a daemon
   may be started by a `.socket` unit, in which case the *socket* unit owns the listening
   port and the daemon's own config port is ignored. Changing the daemon's config and
   restarting the daemon changes nothing. Identify which unit owns the socket, edit that,
   reload the daemon, restart the socket. Verify with the listening-socket list, not with
   the exit code of the restart.
7. **The application's own gate.** Allowlists, `AllowUsers`, host-based access files,
   rate-limiters and intrusion-prevention daemons that ban an address after failed
   attempts. If access worked and then stopped, look here first — you are probably banned
   by your own protection.

## After the fix

- Re-test from the original client *and* from a second network. Fixing one and not
  checking the other leaves half the bug in place.
- Make the change survive reboot. A rule added at runtime and never persisted is a
  scheduled recurrence; confirm persistence explicitly rather than assuming the front-end
  did it.
- Write the finding into the project's or host's notes: which front-end owns the firewall,
  which unit owns the port, what the bind address is. This class recurs on every new host.
- Do not leave the perimeter wider than the task needed. Narrow the source range and
  remove any temporary allow-all rule in the same session that added it.

## Durable sessions for long remote work

An agent or build that outlives the connection must not be tied to it.

- Run the work inside a detachable multiplexer session (`tmux`/`screen`) with a stable,
  predictable name, so a dropped link is reattachment rather than a lost run.
- Wrap the connection in an auto-reconnecting tunnel for links that flap. Set its gate
  time so a fast initial failure is reported instead of being retried forever.
- Keep the connection alive at the protocol level (client keepalive intervals) rather than
  relying on a busy terminal.
- Make the launcher a small parameterised script kept with the operator's other scripts,
  taking the host alias and deriving the session name, so the same invocation works for
  every host and the session name is guessable months later.
- Nothing about the remote run may depend on the local terminal staying open. Verify by
  disconnecting deliberately once and reattaching.

## Output

State the rung that failed, the evidence that identified it (the command and its output),
the change made, the re-test from both networks, and the persistence check. Name anything
you widened and confirm it was narrowed again.
