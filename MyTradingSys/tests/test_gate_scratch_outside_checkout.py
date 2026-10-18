"""Gate flake guard: no test scratch dir inside the checkout, and the gate's pytest commands survive one that vanishes.

2026-10-16: `Step 4f: Pytest layer + live-writer tests` failed in 1 s with "ERROR collecting test session ... pathlib.py lstat
... FileNotFoundError: ...\\MyTradingSys\\backtest\\tmppuq59r8k" (CI run 38825784050, windows-latest; the JIS-NB deploy gate on 50f8f6b
at 03:00Z; one ship gate). Cause: MyTradingSys/backtest/test_tom_dax_bt.py (step 4e) made its scratch dirs with
tempfile.TemporaryDirectory(dir=D.HERE) = MyTradingSys/backtest, a directory step 4f's pytest was collecting under at the same time
(the gate runs 4e and 4f side by side). On Windows pytest lstat()s every directory entry beside the path it descends into
(_pytest.main.Session.collect -> samefile_nofollow); an entry listed and then deleted by the other process raises.

Guards: (1) no tracked test file makes tempfile scratch under the checkout (a dot-prefixed prefix is skipped by pytest and allowed);
(2) every pytest step of the gate carries run_all_tests.transient_ignore_glob(), so tempfile's default tmpXXXXXXXX dirs never become
collection nodes; (3) with the vanishing-entry race injected deterministically, the gate command collects fine and the same run
without the flag fails (Windows only: other platforms never lstat the siblings).
"""
import ast
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import run_all_tests  # noqa: E402

SCRATCH_FUNCS = {"TemporaryDirectory", "mkdtemp", "mkstemp", "NamedTemporaryFile", "TemporaryFile", "SpooledTemporaryFile"}
POSITIONAL_DIR = {"TemporaryDirectory": 2, "mkdtemp": 2, "mkstemp": 2}   # index of `dir` among the positional arguments
CHECKOUT_NAMES = {"HERE", "REPO", "ROOT", "REPO_ROOT", "__file__"}          # names a test uses for its own checkout location


def scratch_in_checkout(source):
    """(line, code) of every tempfile call in `source` whose dir= is anchored on the checkout and whose prefix is not dot-prefixed."""
    hits = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name not in SCRATCH_FUNCS:
            continue
        kw = {k.arg: k.value for k in node.keywords if k.arg}
        where = kw.get("dir")
        idx = POSITIONAL_DIR.get(name)
        if where is None and idx is not None and len(node.args) > idx:
            where = node.args[idx]
        if where is None:
            continue
        used = {n.id for n in ast.walk(where) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(where) if isinstance(n, ast.Attribute)}
        if not used & CHECKOUT_NAMES:
            continue
        prefix = kw.get("prefix")
        if isinstance(prefix, ast.Constant) and isinstance(prefix.value, str) and prefix.value.startswith("."):
            continue   # pytest's default norecursedirs skips ".*"
        hits.append((node.lineno, ast.unparse(node)))
    return hits


def tracked_test_files():
    out = subprocess.check_output(["git", "ls-files", "*test_*.py"], cwd=REPO, text=True).splitlines()
    return [p for p in out if Path(p).name.startswith("test_") and not p.startswith(("Dumps/", "_archive/"))]


class ScratchOutsideCheckoutTest(unittest.TestCase):
    def test_scanner_flags_checkout_anchored_scratch_only(self):
        src = (
            "import tempfile\n"
            "a = tempfile.TemporaryDirectory(dir=D.HERE)\n"                                  # flagged
            "b = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)\n"         # flagged
            "c = tempfile.mkdtemp(dir=REPO)\n"                                               # flagged
            "d = tempfile.mkdtemp('', 'x', HERE)\n"                                          # flagged (positional dir)
            "e = tempfile.mkdtemp(dir=REPO, prefix='.tmp_x_')\n"                             # dot prefix: pytest skips it
            "f = tempfile.TemporaryDirectory()\n"                                            # system temp
            "g = tempfile.mkdtemp(dir=self.tmp)\n"                                           # a scratch dir of the test's own
            "h = tempfile.NamedTemporaryFile(dir=hb_dir)\n"                                  # not a checkout name
        )
        self.assertEqual([ln for ln, _ in scratch_in_checkout(src)], [2, 3, 4, 5])

    def test_no_tracked_test_creates_scratch_inside_the_checkout(self):
        bad = []
        for rel in tracked_test_files():
            try:
                src = (REPO / rel).read_text(encoding="utf-8")
                hits = scratch_in_checkout(src)
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            bad += [f"{rel}:{ln}: {code}" for ln, code in hits]
        self.assertEqual(bad, [], "scratch dirs inside the checkout race a concurrent pytest collection (see this file's docstring): "
                                  "use tempfile.TemporaryDirectory() / pytest tmp_path, or a dot-prefixed prefix")


class GateCommandSurvivesVanishingDirTest(unittest.TestCase):
    PLUGIN = (
        "import os\n"
        "_real = os.scandir\n"
        "_parent = os.path.normcase(os.environ['MTS_RACE_PARENT'])\n"
        "_victim = os.environ['MTS_RACE_VICTIM']\n"
        "\n"
        "\n"
        "class _Racy:\n"
        "    # a directory listing that deletes the victim as soon as it has been read to the end: the entry exists when pytest\n"
        "    # lists the folder and is gone when pytest lstat()s it (the interleaving of the CI failure)\n"
        "    def __init__(self, it):\n"
        "        self._it = it\n"
        "    def __enter__(self):\n"
        "        self._it.__enter__()\n"
        "        return self\n"
        "    def __exit__(self, *a):\n"
        "        return self._it.__exit__(*a)\n"
        "    def __iter__(self):\n"
        "        return self\n"
        "    def __next__(self):\n"
        "        try:\n"
        "            return next(self._it)\n"
        "        except StopIteration:\n"
        "            if os.path.isdir(_victim):\n"
        "                os.rmdir(_victim)\n"
        "            raise\n"
        "    def close(self):\n"
        "        self._it.close()\n"
        "\n"
        "\n"
        "def scandir(path='.'):\n"
        "    it = _real(path)\n"
        "    return _Racy(it) if os.path.normcase(os.path.abspath(path)) == _parent else it\n"
        "\n"
        "\n"
        "os.scandir = scandir\n"
    )

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="mts_race_")
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        self.pkg = self.root / "pkg"
        (self.pkg / "sub").mkdir(parents=True)
        (self.pkg / "tmp_fixtures").mkdir()    # a real test folder whose name merely starts with tmp: must stay collected
        (self.pkg / "sub" / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8", newline="\n")
        (self.pkg / "tmp_fixtures" / "test_kept.py").write_text("def test_kept():\n    assert True\n", encoding="utf-8", newline="\n")
        (self.root / "race_plugin.py").write_text(self.PLUGIN, encoding="utf-8", newline="\n")
        self.victim = self.pkg / "tmpa1b2c3d4"   # the shape tempfile.mkdtemp() gives: "tmp" + 8 of [a-z0-9_]

    def collect(self, cmd, victim_exists=True):
        if victim_exists:
            self.victim.mkdir(exist_ok=True)
        env = dict(os.environ, MTS_RACE_PARENT=str(self.pkg), MTS_RACE_VICTIM=str(self.victim), PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run(cmd + ["-p", "race_plugin"], cwd=self.root, env=env, capture_output=True, text=True, errors="replace")
        return r.returncode, r.stdout + r.stderr

    def bare_cmd(self, *targets):
        return [sys.executable, "-m", "pytest", *targets, "-q", "-p", "no:cacheprovider"]

    @unittest.skipUnless(sys.platform == "win32", "pytest lstat()s the sibling entries on Windows only")
    def test_without_the_flag_a_vanishing_tmp_dir_breaks_collection(self):
        rc, out = self.collect(self.bare_cmd("pkg/sub/test_ok.py"))
        if rc == 0:
            self.skipTest("this pytest no longer fails on an entry that vanished after the listing: the hazard is gone")
        self.assertIn("FileNotFoundError", out)
        self.assertIn("tmpa1b2c3d4", out)

    def test_gate_pytest_cmd_ignores_a_vanishing_tmp_dir(self):
        cmd = run_all_tests.pytest_cmd(["pkg/sub/test_ok.py", "pkg/tmp_fixtures"], root=self.root)
        rc, out = self.collect(cmd)
        self.assertEqual(rc, 0, out)
        self.assertIn("2 passed", out, "the ignore glob must not hide a real test folder that merely starts with tmp")
        self.assertFalse(self.victim.exists(), "the race was not injected: the victim directory is still there")

    def test_ignore_glob_matches_tempfile_names_only(self):
        import fnmatch
        pat = run_all_tests.transient_ignore_glob(self.root).split("=", 1)[1]
        pat = os.path.abspath(pat)        # pytest passes --ignore-glob through absolutepath() before matching
        hit = lambda p: fnmatch.fnmatch(str(p), pat)  # noqa: E731
        self.assertTrue(hit(self.root / "tmpa1b2c3d4"))
        self.assertTrue(hit(self.root / "MyTradingSys" / "backtest" / "tmppuq59r8k"))
        self.assertTrue(hit(self.root / "x" / "tmp_0abc_9z"))
        self.assertFalse(hit(self.root / "tmp_fixtures"))
        self.assertFalse(hit(self.root / "x" / "test_tmp_fixture"))
        self.assertFalse(hit(self.root / "tmp12345"))
        self.assertFalse(hit(Path(self.root.anchor) / "elsewhere" / "tmpa1b2c3d4"))


class EveryGatePytestStepCarriesTheGlobTest(unittest.TestCase):
    def test_every_pytest_step_has_the_ignore_glob(self):
        scratch = tempfile.TemporaryDirectory(prefix="mts_plan_")
        self.addCleanup(scratch.cleanup)
        real_mkdtemp = tempfile.mkdtemp   # build_plan makes one basetemp parent per pytest step: keep them inside `scratch`
        with mock.patch("tempfile.mkdtemp", side_effect=lambda **k: real_mkdtemp(prefix=k.get("prefix", "p_"), dir=scratch.name)):
            plan = run_all_tests.build_plan(quick=True)
        pytest_steps = [s for s in plan if "-m pytest" in (s.cmd_text or "")]
        self.assertGreaterEqual(len(pytest_steps), 7, [s.num for s in plan])
        glob_flag = run_all_tests.transient_ignore_glob()
        self.assertEqual([s.num for s in pytest_steps if glob_flag not in s.cmd_text], [],
                         "every gate pytest step must use run_all_tests.pytest_cmd / transient_ignore_glob")


if __name__ == "__main__":
    unittest.main()
