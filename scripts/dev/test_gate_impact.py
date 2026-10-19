"""Tests for gate_impact.py and the fast ship gate (GATE_SPEED.md X1-X6). Runs as a script (gate step 3gi): python scripts/dev/test_gate_impact.py"""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_impact as gi
import run_all_tests as rat


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True)


def make_repo(files):
    d = Path(tempfile.mkdtemp())
    git(d, "init", "-q")
    for name, text in files.items():
        p = d / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, newline="\n")
    git(d, "add", "-A")
    return d


class Reach(unittest.TestCase):
    def reach(self, files, changed):
        d = make_repo(files)
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        return gi.reach(changed, d)

    def test_reverse_import_closure_reaches_tests_two_hops_away_but_only_the_direct_one_is_direct(self):
        r = self.reach({"a.py": "X = 1\n", "b.py": "import a\n", "test_b.py": "import b\n", "test_a.py": "import a\n", "other.py": "Y = 1\n",
                        "test_other.py": "import other\n"}, ["a.py"])
        self.assertEqual(r.tests, {"test_a.py", "test_b.py"})
        self.assertEqual(r.direct, {"test_a.py"})
        self.assertEqual(r.closure, {"a.py", "b.py", "test_a.py", "test_b.py"})

    def test_from_import_of_a_name_and_relative_import_are_edges(self):
        r = self.reach({"pkg/__init__.py": "", "pkg/a.py": "X = 1\n", "pkg/b.py": "from . import a\n", "t/test_b.py": "from pkg import b\n",
                        "t/test_z.py": "from pkg import zzz\n"}, ["pkg/a.py"])
        self.assertEqual(r.tests, {"t/test_b.py"})

    def test_a_string_mention_in_a_hub_script_is_not_followed_transitively(self):
        r = self.reach({"a.py": "X = 1\n", "hub.py": "RUN = 'python a.py'\n", "test_hub.py": "import hub\n", "test_a.py": "import a\n"}, ["a.py"])
        self.assertEqual(r.tests, {"test_a.py"})

    def test_a_test_that_runs_the_module_by_path_or_dash_m_or_dotted_string_is_direct(self):
        r = self.reach({"scripts/dev/tool.py": "X = 1\n",
                        "t1/test_x.py": "import subprocess\nsubprocess.run(['python', 'scripts/dev/tool.py'])\n",
                        "t2/test_y.py": "import sys\nCMD = [sys.executable, '-m', 'scripts.dev.tool']\n",
                        "t3/test_z.py": "from unittest import mock\nmock.patch('tool.fn')\n",
                        "t4/test_n.py": "print('nothing')\n"}, ["scripts/dev/tool.py"])
        self.assertEqual(r.direct, {"t1/test_x.py", "t2/test_y.py", "t3/test_z.py"})
        self.assertNotIn("t4/test_n.py", r.tests)

    def test_conftest_or_init_change_reaches_every_test_beside_it(self):
        files = {"tests/conftest.py": "", "tests/test_a.py": "x = 1\n", "tests/sub/test_b.py": "x = 2\n", "other/test_c.py": "x = 3\n"}
        r = self.reach(files, ["tests/conftest.py"])
        self.assertEqual(r.direct, {"tests/test_a.py", "tests/sub/test_b.py"})

    def test_a_deleted_file_still_reaches_the_tests_that_import_it(self):
        r = self.reach({"b.py": "import gone\n", "test_b.py": "import b\n", "test_g.py": "import gone\n"}, ["gone.py"])
        self.assertEqual(r.direct, {"test_g.py"})
        self.assertEqual(r.tests, {"test_g.py", "test_b.py"})

    def test_a_changed_data_file_seeds_the_modules_and_tests_that_name_it(self):
        r = self.reach({"loader.py": "P = 'cfg.json'\n", "test_loader.py": "import loader\n", "test_cfg.py": "open('cfg.json')\n",
                        "unrelated.py": "x = 1\n", "test_unrelated.py": "import unrelated\n"}, ["cfg.json"])
        self.assertEqual(r.tests, {"test_loader.py", "test_cfg.py"})
        self.assertEqual(r.direct, {"test_cfg.py", "test_loader.py"})

    def test_doc_files_seed_nothing(self):
        r = self.reach({"a.py": "p = 'README.md'\n", "test_a.py": "import a\n"}, ["README.md"])
        self.assertEqual(r.tests, set())

    def test_live_code_importing_the_change_is_reported_and_the_change_itself_is_not(self):
        files = {"lib.py": "X = 1\n", "MyTradingSys/execution/live.py": "import lib\n", "test_lib.py": "import lib\n"}
        self.assertEqual(self.reach(files, ["lib.py"]).live_hit, ["MyTradingSys/execution/live.py"])
        self.assertEqual(self.reach(files, ["lib.py", "MyTradingSys/execution/live.py"]).live_hit, [])

    def test_real_repo_small_script_reaches_its_own_test_and_no_live_code(self):
        r = gi.reach(["scripts/dev/nowin.py"])
        self.assertEqual(r.live_hit, [])
        self.assertIn("scripts/dev/test_nowin.py", r.direct)


class Budget(unittest.TestCase):
    EST = {"a": 5, "b": 10, "c": 40, "d": 3}.get

    def test_direct_files_are_always_kept_even_over_budget(self):
        kept, deferred = gi.plan_budget(["c"], ["a"], self.EST, 1, budget=30)
        self.assertEqual(kept, ["c"])
        self.assertEqual(deferred, ["a"])

    def test_others_fill_the_budget_cheapest_first(self):
        kept, deferred = gi.plan_budget([], ["b", "a", "d", "c"], self.EST, 1, budget=20)
        self.assertEqual(sorted(kept), ["a", "b", "d"])
        self.assertEqual(deferred, ["c"])

    def test_more_workers_fit_more_work(self):
        k1, _ = gi.plan_budget([], ["a", "b", "d"], self.EST, 1, budget=10)
        k3, _ = gi.plan_budget([], ["a", "b", "d"], self.EST, 3, budget=10)
        self.assertLess(len(k1), len(k3))

    def test_a_single_file_longer_than_the_budget_is_deferred(self):
        kept, deferred = gi.plan_budget([], ["c"], self.EST, 8, budget=30)
        self.assertEqual((kept, deferred), ([], ["c"]))

    def test_balance_splits_into_chunks_of_similar_weight(self):
        chunks = gi.balance(["a", "b", "c", "d"], self.EST, 2)
        self.assertEqual(sorted(sum(chunks, [])), ["a", "b", "c", "d"])
        self.assertEqual(len(chunks), 2)
        self.assertEqual(gi.balance([], self.EST, 4), [])
        self.assertEqual(len(gi.balance(["a"], self.EST, 4)), 1)


class Quarantine(unittest.TestCase):
    TODAY = date(2026, 10, 18)

    def rows(self, *lines):
        return gi.quarantine_rows("\n".join(lines))

    def test_rows_skip_comments_and_blank_lines(self):
        r = self.rows("# header", "", "scripts/dev/test_x.py::T::t\tjis\t2026-11-01\tflaky on windows")
        self.assertEqual(r, [("scripts/dev/test_x.py::T::t", "jis", "2026-11-01", "flaky on windows")])

    def test_a_valid_row_is_active_and_clean(self):
        r = self.rows("scripts/dev/test_x.py::T::t\tjis\t2026-11-01\twhy")
        self.assertEqual(gi.quarantine_problems(r, self.TODAY), [])
        self.assertEqual(gi.active_deselects(r, self.TODAY), ["scripts/dev/test_x.py::T::t"])

    def test_an_expired_row_is_a_problem_and_deselects_nothing(self):
        r = self.rows("scripts/dev/test_x.py::T::t\tjis\t2026-10-01\twhy")
        self.assertIn("expired", gi.quarantine_problems(r, self.TODAY)[0])
        self.assertEqual(gi.active_deselects(r, self.TODAY), [])

    def test_missing_owner_or_bad_date_is_a_problem(self):
        self.assertTrue(gi.quarantine_problems(self.rows("t.py::a\t\t2026-11-01\twhy"), self.TODAY))
        self.assertIn("YYYY-MM-DD", gi.quarantine_problems(self.rows("t.py::a\tjis\tsoon\twhy"), self.TODAY)[0])
        self.assertEqual(gi.active_deselects(self.rows("t.py::a\tjis\tsoon\twhy"), self.TODAY), [])

    def test_live_path_tests_are_never_quarantined(self):
        r = self.rows("MyTradingSys/execution/test_o.py::T::t\tjis\t2026-11-01\twhy")
        self.assertIn("never quarantined", gi.quarantine_problems(r, self.TODAY)[0])
        self.assertEqual(gi.active_deselects(r, self.TODAY), [])

    def test_the_repo_quarantine_file_is_valid(self):
        path = gi.REPO / gi.QUARANTINE
        self.assertTrue(path.is_file())
        self.assertEqual(gi.quarantine_problems(gi.quarantine_rows(path.read_text(encoding="utf-8"))), [])

    def test_rows_come_from_the_trunk_ref_not_the_working_copy(self):
        d = make_repo({gi.QUARANTINE: "t.py::a\tjis\t2099-01-01\ttrunk row\n"})
        git(d, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "x")
        git(d, "update-ref", "refs/remotes/origin/fast-track", "HEAD")
        (d / gi.QUARANTINE).write_text("t.py::mine\tjis\t2099-01-01\tmy own row\n", newline="\n")
        self.assertEqual([r[0] for r in gi.trunk_quarantine(d)], ["t.py::a"])
        self.assertEqual(gi.trunk_quarantine(make_repo({"x.py": ""})), [])


class FastPlan(unittest.TestCase):
    """run_all_tests.apply_selection with --fast on the real step list."""

    def setUp(self):
        self.saved = (rat.fast_applied, rat.fast_info, rat.gate_mode, rat.gate_reason)
        self.addCleanup(lambda: setattr_all(rat, ("fast_applied", "fast_info", "gate_mode", "gate_reason"), self.saved))

    def select(self, files, reach=None):
        fd = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, newline="\n")
        fd.write("\n".join(files) + "\n")
        fd.close()
        self.addCleanup(lambda: Path(fd.name).unlink())
        args = ["--quick", "--smoke", "--fast", "--changed-file", fd.name]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            if reach is None:
                return rat.apply_selection(rat.build_plan(True), args) + (out.getvalue(),)
            with mock.patch.object(gi, "reach", reach):
                return rat.apply_selection(rat.build_plan(True), args) + (out.getvalue(),)

    def test_small_change_runs_a_few_reached_steps_and_defers_the_rest_to_ci(self):
        plan, mode, _ = self.select(["scripts/dev/nowin.py"])
        self.assertEqual(mode, "smoke")
        self.assertTrue(rat.fast_applied)
        run = [s for s in plan if not s.skip]
        self.assertLess(len(run), 25)
        self.assertTrue(any(s.num == "3gd" for s in run))
        self.assertTrue(any(str(s.skip).startswith("fast:") for s in plan))
        self.assertTrue(any("test_nowin" in s.cmd_text for s in run))

    def test_live_code_importing_the_change_forces_the_full_gate(self):
        r = gi.Reach()
        r.live_hit = ["MyTradingSys/execution/live.py"]
        plan, mode, _ = self.select(["scripts/dev/nowin.py"], reach=lambda files: r)
        self.assertEqual(mode, "full")
        self.assertFalse(rat.fast_applied)
        self.assertFalse(any(str(s.skip).startswith("fast:") for s in plan))

    def test_any_failure_in_the_fast_path_falls_back_to_the_whole_shard_smoke_selection(self):
        def boom(files):
            raise RuntimeError("graph broke")
        plan, mode, out = self.select(["scripts/dev/nowin.py"], reach=boom)
        self.assertEqual(mode, "smoke")
        self.assertFalse(rat.fast_applied)
        self.assertIn("fast path unavailable", out)
        self.assertFalse(any(str(s.skip).startswith("fast:") for s in plan))

    def test_live_path_files_never_take_the_fast_path(self):
        plan, mode, _ = self.select(["scripts/dev/sync.py"])
        self.assertEqual(mode, "full")
        self.assertFalse(rat.fast_applied)

    def test_fast_gate_runs_3dl_on_any_py_or_ci_yml_change(self):
        plan, mode, _ = self.select(["scripts/dev/nowin.py"])
        self.assertEqual(mode, "smoke")
        self.assertTrue(rat.fast_applied)
        run_nums = [s.num for s in plan if not s.skip]
        self.assertIn("3dl", run_nums)

        plan_ci = rat.build_plan(True)
        new_plan, _ = rat.apply_fast(plan_ci, [".github/workflows/ci.yml"], nums=[s.num for s in plan_ci], jobs=2)
        ci_run_nums = [s.num for s in new_plan if not s.skip]
        self.assertIn("3dl", ci_run_nums)

    def test_save_record_stores_deferred_tests_list(self):
        d = make_repo({"a.py": "x = 1\n"})
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        git(d, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "init")
        plan = []
        results = {}
        deferred_tests = ["MyTradingSys/tests/test_foo.py", "scripts/dev/test_bar.py"]
        ok = rat.save_record(plan, results, root=d, deferred=deferred_tests)
        self.assertTrue(ok)
        rec = json.loads(rat.record_path(d).read_text(encoding="utf-8"))
        self.assertEqual(rec.get("deferred"), deferred_tests)


def setattr_all(mod, names, values):
    for n, v in zip(names, values):
        setattr(mod, n, v)


if __name__ == "__main__":
    unittest.main(verbosity=1)
