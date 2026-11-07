import os, subprocess, unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "colocate.sh")


def run(*args):
    return subprocess.run(["bash", SCRIPT, *args], capture_output=True, text=True,
                          env=dict(os.environ, COLOCATE_ENV="/nonexistent"))


class Colocate(unittest.TestCase):
    def test_script_parses(self):
        self.assertEqual(subprocess.run(["bash", "-n", SCRIPT]).returncode, 0)

    @unittest.skipIf(os.geteuid() == 0, "root would apply for real")
    def test_mutating_commands_refuse_without_root(self):
        for cmd in ("apply", "revert"):
            with self.subTest(cmd):
                res = run(cmd)
                self.assertEqual(res.returncode, 2)
                self.assertIn("run as root", res.stderr)

    def test_unknown_command_is_usage_error(self):
        self.assertEqual(run("aply").returncode, 2)


if __name__ == "__main__":
    unittest.main()
