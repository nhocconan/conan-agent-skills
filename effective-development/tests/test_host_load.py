import contextlib, importlib.util, io, json, os, subprocess, sys, tempfile, unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "scripts", "host_load.py")
spec = importlib.util.spec_from_file_location("host_load", SCRIPT)
hl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hl)


def put(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def build(root, cpus=32, cores=16, load=1.0, allowed=None, cpu_max=None, avail_gb=100, swap_used_gb=0,
          psi=None, no_psi=False, total_gb=128):
    proc, sysr = os.path.join(root, "proc"), os.path.join(root, "sys")
    put(proc, "loadavg", f"{load} {load} {load} 1/100 1\n")
    put(proc, "self/status", f"Cpus_allowed_list:\t{allowed or f'0-{cpus - 1}'}\n")
    put(proc, "self/cgroup", "0::/grp\n")
    kb = 1024 * 1024
    put(proc, "meminfo", f"MemTotal: {total_gb * kb} kB\nMemAvailable: {int(avail_gb * kb)} kB\n"
        f"SwapTotal: {16 * kb} kB\nSwapFree: {int((16 - swap_used_gb) * kb)} kB\n")
    put(sysr, "fs/cgroup/grp/cpu.max", cpu_max or "max 100000")
    put(sysr, "fs/cgroup/cpu.max", "max 100000")
    for i in range(cpus):
        t = f"devices/system/cpu/cpu{i}/topology/"
        put(sysr, t + "physical_package_id", "0\n")
        put(sysr, t + "core_id", f"{i % cores}\n")
    if not no_psi:
        vals = {"cpu": (0, 0), "memory": (0, 0), "io": (0, 0), **(psi or {})}
        for name, (a10, a60) in vals.items():
            line = f"avg10={a10} avg60={a60} avg300=0 total=0"
            put(proc, f"pressure/{name}", f"some {line}\nfull {line}\n")
    return proc, sysr


def run(root, *args, clock=lambda: 0, sleep=lambda s: None, **kw):
    proc, sysr = build(root, **kw)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = hl.main([*args, "--proc-root", proc, "--sys-root", sysr, "--json"],
                     clock=clock, sleep=sleep)
    return rc, json.loads(out.getvalue())


class HostLoad(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop("HOST_SHARE", None)
        self._t = tempfile.TemporaryDirectory()
        self.root = self._t.name
        self.addCleanup(self._t.cleanup)

    def sense(self, **kw):
        return hl.sense(*build(self.root, **kw))

    def test_cgroup_quota_caps_cpus(self):
        self.assertEqual(self.sense(cpu_max="800000 100000")["cpus"], 8)

    def test_affinity_not_system_count(self):
        self.assertEqual(self.sense(cpus=32, allowed="0-7")["cpus"], 8)

    def test_physical_cores_from_topology(self):
        self.assertEqual(self.sense(cpus=32, cores=16)["physical"], 16)
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(hl.sense(*build(d, cpus=8, cores=8))["physical"], 8)

    def test_decision_table(self):
        rows = [
            ("idle admits half the cpus", {}, 0, 16),
            ("load over cpu count defers", {"load": 34}, 75, 0),
            ("cpu pressure rising defers", {"psi": {"cpu": (45, 12)}}, 75, None),
            ("cpu pressure falling only busy", {"psi": {"cpu": (12, 45)}}, 0, None),
            ("memory pressure defers", {"psi": {"memory": (12, 12)}}, 75, None),
            ("avail under reserve defers", {"avail_gb": 1}, 75, None),
            ("swap over 80 % is overloaded", {"swap_used_gb": 14}, 75, None),
            ("swap over half is busy, still admits", {"swap_used_gb": 10}, 0, None),
            ("parked swap under half is not pressure", {"swap_used_gb": 3}, 0, 16),
            ("load fills cpus leaves no worker", {"load": 32}, 75, 0),
        ]
        for name, kw, rc_want, workers_want in rows:
            with self.subTest(name), tempfile.TemporaryDirectory() as d:
                rc, out = run(d, "--admit", **kw)
                self.assertEqual(rc, rc_want)
                if workers_want is not None:
                    self.assertEqual(out["workers"], workers_want)
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run(d, **{"load": 34})[0], 0)

    def test_memory_bounds_workers(self):
        rc, out = run(self.root, "--workers-for", "vitest", avail_gb=10, total_gb=16)
        self.assertEqual(out["workers"], 13)
        self.assertIn("mem", out["bound"])

    def test_browser_kind_cap(self):
        self.assertEqual(run(self.root, "--workers-for", "playwright")[1]["workers"], 2)

    def test_share_flag_beats_env_and_env_beats_default(self):
        old = os.environ.get("HOST_SHARE")
        self.addCleanup(lambda: os.environ.pop("HOST_SHARE", None) if old is None
                        else os.environ.__setitem__("HOST_SHARE", old))
        os.environ["HOST_SHARE"] = "0.25"
        self.assertEqual(run(self.root)[1]["workers"], 8)
        self.assertEqual(run(self.root, "--share", "0.75")[1]["workers"], 24)

    def test_missing_psi_degrades(self):
        rc, out = run(self.root, "--admit", no_psi=True)
        self.assertEqual((rc, out["psi"], out["decision"]), (0, None, "admit"))

    def test_wait_backoff_times_out(self):
        now, slept = [0.0], []

        def sleep(s):
            slept.append(s)
            now[0] += s

        rc, _ = run(self.root, "--wait", "20", load=40, clock=lambda: now[0], sleep=sleep)
        self.assertEqual((rc, slept), (75, [5, 7.5, 7.5]))

    def test_live_smoke(self):
        p = subprocess.run([sys.executable, SCRIPT, "--json", "--admit"], capture_output=True, text=True)
        self.assertIn(p.returncode, (0, 75))
        json.loads(p.stdout)


if __name__ == "__main__":
    unittest.main()
