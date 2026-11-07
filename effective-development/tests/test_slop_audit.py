import os, re, subprocess, sys, tempfile, unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "slop_audit.py")

def run(cwd, *args):
    p = subprocess.run([sys.executable, SCRIPT, *args], cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout

class Base(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.d = self._t.name
        self.addCleanup(self._t.cleanup)

    def write(self, name, text):
        path = os.path.join(self.d, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def codes(self, name):
        rc, out = run(self.d, "--paths", name)
        return rc, [l.split()[1] for l in out.splitlines() if re.match(r"\S+:\d+ ", l)]

class Errors(Base):
    def test_each_error_once(self):
        self.write("a.test.ts", "\n".join([
            "it.only('x', () => {});",
            "await page.waitForTimeout(500);",
            "expect(true).toBe(true);",
            "expect(console.error).toHaveBeenCalledTimes(1);",
            "// Added retry for the ticket",
            "// const x = 1",
        ]) + "\n")
        rc, codes = self.codes("a.test.ts")
        self.assertEqual((rc, sorted(codes)), (1, ["E1", "E2", "E3", "E4", "E5", "E6"]))

    def test_clean_file(self):
        self.write("ok.test.ts", "it('rejects an empty name', () => {\n  expect(f('')).toBe(false);\n});\n")
        self.assertEqual(self.codes("ok.test.ts"), (0, []))

    def test_marker_reason_honored_and_todo_rejected(self):
        self.write("m.test.ts", "page.waitForTimeout(1); // audit-ok-slop: animation has no event\n"
                                "page.waitForTimeout(1); // audit-ok-slop: TODO\n")
        rc, out = run(self.d, "--paths", "m.test.ts")
        self.assertEqual(rc, 1)
        self.assertIn("m.test.ts:2 E2", out)
        self.assertNotIn("m.test.ts:1 ", out)

    def test_non_test_ts_gets_comment_rules_only(self):
        self.write("src.ts", "it.only('x');\nwaitForTimeout(1);\nexpect(true).toBe(true);\n"
                             "// Fixed in commit abc1234\n")
        self.assertEqual(self.codes("src.ts"), (1, ["E5"]))

    def test_python_hash_code(self):
        self.write("m.py", "# import os\n# def f(x):\n# return f(x)\nx = 1\n")
        self.assertEqual(self.codes("m.py"), (1, ["E6", "E6", "E6"]))

    def test_python_assert_tautology_in_test(self):
        self.write("tests/test_a.py", "def test_a():\n    assert True\n    assert 1 == 1\n")
        self.assertEqual(self.codes("tests/test_a.py"), (1, ["E3", "E3"]))

class Precision(Base):
    def test_no_false_positives(self):
        self.write("n.ts", "\n".join([
            "// Fixed-size buffer holds one frame",           # no W9: "Fixed-" is an adjective
            "const c = '#fff'; // see http://x.dev/a#b",
            "const u = 'http://example.com/a';",
            "const s = \"// const x = 1;\";",
            "// eslint-disable-next-line no-console;",
            "// @ts-expect-error: legacy;",
            "// prettier-ignore;",
            "/**",
            " * const sample = 1;",
            " */",
            "const t = `",
            "// const inside = 1;",
            "`;",
            "// return early when the list is empty",
            "// export the list for tests",
            "// Playwright usage: node probe.js --url=x;",
            "// return null when the user is missing (see docs)",
            "// import order matters: polyfills first ('core-js')",
            "// export shape = { id, name }; keep in sync",
            "// Updated at read time; UTF-8 and RFC-3339 only",
        ]) + "\n")
        rc, codes = self.codes("n.ts")
        self.assertEqual((rc, sorted(codes)), (0, ["W10", "W10", "W10", "W9"]))  # prose stays warning-level

    def test_python_exclusions(self):
        self.write("n.py", "\n".join([
            "#!/usr/bin/env python3",
            "x = '#fff'  # type: int",
            "y = 1  # noqa: E501",
            "z = 2  # pragma: no cover",
            "s = 'http://a/#frag'",
            '"""',
            "# import os",
            '"""',
            "# import the module before use",
            "# return early if empty",
        ]) + "\n")
        self.assertEqual(self.codes("n.py"), (0, []))
        self.write("w.py", "# return the cached value when the key is present ('hot' path)\n")
        self.assertEqual(self.codes("w.py"), (0, ["W10"]))

    def test_sha_needs_a_digit(self):
        self.write("s.ts", "// commit effaced the old path\n// per sha 1a2b3c4d5\n")
        self.assertEqual(self.codes("s.ts"), (1, ["E5"]))

class Warnings(Base):
    def test_warnings_only_exit_zero(self):
        self.write("w.test.ts", "\n".join([
            "// load user name",                          # W5
            "const load = (user, name) => 1;",
            "expect(registry).toHaveLength(3);",              # W1
            "expect(x).toMatchSnapshot();",                   # W2
            "it('works', () => {});",                         # W3
            "// TODO tidy this",                              # W4
            "readFileSync('src/a.ts');",                      # W6
            "// 2026-01-02 workaround",                       # W7
            "// Removed the old branch",                      # W9
        ]) + "\n")
        self.write("tests/test_w.py", "import time\ntime.sleep(1)\n")  # audit-ok-slop: fixture text for W8
        rc, codes = self.codes("w.test.ts")
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(codes), ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W9"])
        self.assertEqual(self.codes("tests/test_w.py"), (0, ["W8"]))

class BaseMode(Base):
    def git(self, *a):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=self.d, check=True, capture_output=True)

    def test_only_added_lines(self):
        self.git("init", "-q")
        self.write("a.test.ts", "await page.waitForTimeout(1);\n")
        self.git("add", "."); self.git("commit", "-qm", "base")
        self.write("a.test.ts", "await page.waitForTimeout(1);\nawait page.waitForTimeout(2);\n")
        rc, out = run(self.d, "--base", "HEAD")
        self.assertEqual(rc, 1)
        self.assertIn("a.test.ts:2 E2", out)
        self.assertNotIn("a.test.ts:1 ", out)

    def test_subdir_and_untracked_files_are_audited(self):
        self.git("init", "-q")
        self.write("web/a.test.ts", "it('a', () => {});\n")
        self.git("add", "."); self.git("commit", "-qm", "base")
        self.write("web/a.test.ts", "it('a', () => {});\nawait page.waitForTimeout(2);\n")
        self.write("web/new.spec.ts", "it.only('b', () => {});\n")
        rc, out = run(os.path.join(self.d, "web"), "--base", "HEAD")
        self.assertEqual(rc, 1, out)
        self.assertIn("web/a.test.ts:2 E2", out)
        self.assertIn("web/new.spec.ts:1 E1", out)

    def test_noprefix_git_config_still_audited(self):
        self.git("init", "-q")
        self.write("a.test.ts", "it('a', () => {});\n")
        self.git("add", "."); self.git("commit", "-qm", "base")
        self.write("a.test.ts", "it('a', () => {});\nawait page.waitForTimeout(2);\n")
        env = dict(os.environ, GIT_CONFIG_COUNT="2", GIT_CONFIG_KEY_0="diff.noprefix", GIT_CONFIG_VALUE_0="true",
                   GIT_CONFIG_KEY_1="diff.mnemonicPrefix", GIT_CONFIG_VALUE_1="true")
        p = subprocess.run([sys.executable, SCRIPT, "--base", "HEAD"], cwd=self.d, env=env, capture_output=True, text=True)
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("a.test.ts:2 E2", p.stdout)

    def test_usage_error(self):
        self.assertEqual(run(self.d)[0], 2)

if __name__ == "__main__":
    unittest.main()
