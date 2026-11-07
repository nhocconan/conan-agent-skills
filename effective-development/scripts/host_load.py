#!/usr/bin/env python3
"""Read host load, pressure and memory; print how many workers this agent may start.
Exit 0 admit/ok, 75 defer (--admit or --wait), 69 unsupported, 2 usage. Never signals a process."""
import argparse, glob, json, math, os, re, subprocess, sys, time

KIND_MB = {"playwright": 450, "vitest": 600, "jest": 600, "pytest": 300, "tsc": 1500,
           "next-build": 3000, "ffmpeg": 600, "generic": 500}
KIND_CAP = {"playwright": 2}
LEVELS = ("ok", "busy", "overloaded")


def read(path):
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return None


def count_list(text):
    n = 0
    for part in text.strip().split(","):
        if part:
            lo, _, hi = part.partition("-")
            n += int(hi or lo) - int(lo) + 1
    return n


def cgroup_dirs(proc, sys_root):
    top = os.path.join(sys_root, "fs/cgroup")
    m = re.search(r"^0::(.*)$", read(os.path.join(proc, "self/cgroup")) or "", re.M)
    d = os.path.normpath(top + (m.group(1) if m else ""))
    while True:
        yield d
        if d == os.path.normpath(top) or not d.startswith(top):
            return
        d = os.path.dirname(d)


def logical_cpus(proc, sys_root):
    st = re.search(r"^Cpus_allowed_list:\s*(\S+)", read(os.path.join(proc, "self/status")) or "", re.M)
    n = count_list(st.group(1)) if st else (os.cpu_count() or 1)
    for d in cgroup_dirs(proc, sys_root):
        q = (read(os.path.join(d, "cpu.max")) or "max").split()
        if q[0] != "max":
            n = min(n, math.ceil(int(q[0]) / int(q[1])))
    return max(1, n)


def physical_cores(sys_root, fallback):
    ids = set()
    for t in glob.glob(os.path.join(sys_root, "devices/system/cpu/cpu[0-9]*/topology")):
        pkg, core = (read(os.path.join(t, n)) for n in ("physical_package_id", "core_id"))
        if core is not None:
            ids.add((pkg, core.strip()))
    return len(ids) or fallback


def psi(proc, name):
    text = read(os.path.join(proc, "pressure", name))
    if text is None:
        return None
    out = {}
    for line in text.splitlines():
        kind, *kv = line.split()
        d = dict(p.split("=") for p in kv)
        out[kind] = [float(d["avg10"]), float(d["avg60"])]
    return out


def meminfo(proc):
    text = read(os.path.join(proc, "meminfo"))
    if text is None:
        return None
    kb = {k: int(v) for k, v in re.findall(r"^(\w+):\s+(\d+)", text, re.M)}
    mb = lambda k: kb.get(k, 0) / 1024
    return {"total": mb("MemTotal"), "available": mb("MemAvailable"),
            "swap_total": mb("SwapTotal"), "swap_used": mb("SwapTotal") - mb("SwapFree")}


def cgroup_headroom(proc, sys_root):
    best = None
    for d in cgroup_dirs(proc, sys_root):
        cap, cur = read(os.path.join(d, "memory.max")), read(os.path.join(d, "memory.current"))
        if cap and cur and cap.strip() != "max":
            room = (int(cap) - int(cur)) / 2**20
            best = room if best is None else min(best, room)
    return best


def sysctl(name):
    try:
        return int(subprocess.run(["sysctl", "-n", name], capture_output=True, text=True).stdout)
    except (OSError, ValueError):
        return None


def sense(proc, sys_root):
    if sys.platform == "darwin":
        c = sysctl("hw.logicalcpu") or os.cpu_count() or 1
        return {"cpus": c, "physical": sysctl("hw.physicalcpu") or c, "load": list(os.getloadavg()),
                "psi": None, "mem": None, "cg_room": None}
    load = read(os.path.join(proc, "loadavg"))
    if not sys.platform.startswith("linux") or load is None:
        return None
    c = logical_cpus(proc, sys_root)
    return {"cpus": c, "physical": physical_cores(sys_root, c), "load": [float(x) for x in load.split()[:3]],
            "psi": {n: psi(proc, n) for n in ("cpu", "memory", "io")} if psi(proc, "cpu") else None,
            "mem": meminfo(proc), "cg_room": cgroup_headroom(proc, sys_root)}


def pressure_level(p, busy, over, resume):
    a10, a60 = p
    if a10 >= over and a60 >= resume:
        return 1 if a10 < 0.85 * a60 else 2
    return 1 if a10 >= busy else 0


def decide(s, share, kind, per_worker):
    c, l1 = s["cpus"], s["load"][0]
    rows = {"load": 0 if l1 / c < 0.7 else 1 if l1 / c < 1.0 else 2}
    psi_, mem = s["psi"], s["mem"]
    if psi_:
        for name, limits in (("cpu", (10, 40, 10)), ("memory", (1, 10, 10)), ("io", (1, 10, 10))):
            rows[name] = pressure_level(psi_[name]["some" if name == "cpu" else "full"], *limits)
    bounds = {"share": math.floor(share * c), "idle": math.floor(max(0, c - l1))}
    if kind in KIND_CAP:
        bounds["kind"] = KIND_CAP[kind]
    if mem:
        room = mem["available"] if s["cg_room"] is None else min(mem["available"], s["cg_room"])
        reserve = max(2048, 0.1 * mem["total"])
        rows["avail"] = 2 if room < reserve else 1 if room < reserve + per_worker else 0
        if mem["swap_total"]:
            ratio = mem["swap_used"] / mem["swap_total"]
            rows["swap"] = 0 if ratio < 0.5 else 1 if ratio <= 0.8 else 2  # parked pages are not pressure; PSI is
        bounds["mem"] = math.floor((room - reserve) / per_worker)
    workers = max(0, min(bounds.values()))
    state = LEVELS[max(rows.values())]
    reasons = [f"{k}={LEVELS[v]}" for k, v in rows.items() if v] + \
              [f"bound:{k}={v}" for k, v in bounds.items() if v == workers]
    return {"state": state, "workers": workers, "bound": [k for k, v in bounds.items() if v == workers],
            "decision": "defer" if state == "overloaded" or workers == 0 else "admit", "reasons": reasons}


def render(s, d, share, kind):
    g = lambda v: "n/a" if v is None else f"{v[0]:g}/{v[1]:g}"
    p = s["psi"] or {}
    cell = lambda n, k: g(p[n][k]) if p.get(n) else "n/a"
    m = s["mem"]
    gb = lambda k: "n/a" if not m else f"{m[k] / 1024:.1f}G"
    return (f"host cpus={s['cpus']}({s['physical']}c) load={'/'.join('%.1f' % x for x in s['load'])} "
            f"psi cpu.some={cell('cpu', 'some')} mem.full={cell('memory', 'full')} io.full={cell('io', 'full')} "
            f"avail={gb('available')} "
            f"swap={gb('swap_used')} share={share:g} state={d['state']} "
            f"workers[{kind}]={d['workers']} bound={','.join(d['bound'])} decision={d['decision']}")


def parse(argv):
    env = os.environ.get("HOST_SHARE")
    ap = argparse.ArgumentParser(prog="host_load.py", description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--workers-for", dest="kind", choices=sorted(KIND_MB), default="generic")
    ap.add_argument("--worker-mem", type=float, metavar="MB")
    ap.add_argument("--share", type=float, default=float(env) if env else 0.5)
    ap.add_argument("--admit", action="store_true", help="exit 75 when the decision is defer")
    ap.add_argument("--wait", type=float, default=0, metavar="SECS", help="re-check with backoff up to SECS")
    ap.add_argument("--proc-root", default="/proc")
    ap.add_argument("--sys-root", default="/sys")
    return ap.parse_args(argv)


def main(argv=None, clock=time.monotonic, sleep=time.sleep):
    try:
        a = parse(argv)
    except ValueError:
        print("HOST_SHARE must be a number", file=sys.stderr)
        return 2
    if not 0 < a.share <= 1:
        print("share must be in (0, 1]", file=sys.stderr)
        return 2
    per_worker = a.worker_mem or KIND_MB[a.kind]
    deadline, delay = clock() + a.wait, 5.0
    while True:
        s = sense(a.proc_root, a.sys_root)
        if s is None:
            print("unsupported: no /proc/loadavg", file=sys.stderr)
            return 69
        d = decide(s, a.share, a.kind, per_worker)
        left = deadline - clock()
        if d["decision"] == "admit" or left <= 0:
            break
        sleep(min(delay, left))
        delay = min(delay * 1.5, 60)
    if a.json:
        m = s["mem"]
        print(json.dumps({"cpus": s["cpus"], "physical": s["physical"], "load": s["load"], "psi": s["psi"],
                          "mem": m and {"total": m["total"], "available": m["available"],
                                        "swap_used": m["swap_used"], "cgroup_room": s["cg_room"]},
                          "share": a.share, "kind": a.kind, **d}))
    else:
        print(render(s, d, a.share, a.kind))
    return 75 if (a.admit or a.wait) and d["decision"] == "defer" else 0


if __name__ == "__main__":
    sys.exit(main())
