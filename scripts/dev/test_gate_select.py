"""gate_select: path -> gate steps. Fail closed on live-path and unmapped code."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_select as gs

STEPS = [("1", "python scripts/dev/run_staged_tests.py MyTradingSys/execution -- test_risk_guard"), ("3k", "python -m unittest (scripts/dev/test_sync.py, 3 shards)"),
         ("3ds", "python -m unittest (scripts/dev/test_dsa.py, 2 shards)"), ("3tl", "python scripts/dev/tasks.py lint"), ("3q", "x"), ("3pc", "x"),
         ("3c", "x"), ("3w", "x"), ("3x", "x"), ("3gd", "x"), ("3dl", "x"), ("3xt", "x"), ("4", "pytest MyTradingSys/tests/a"), ("4b", "pytest MyTradingSys/tests/b"),
         ("4d", "pytest MyTradingSys/tests/docs"), ("5b", "unittest"), ("5c", "pytest options")]
MENTIONED = {("dsa", "4b")}   # the pytest shard whose tests mention the module `dsa`
BS = chr(92)


def mentioned(stem, cmd):
    return (stem, next(n for n, c in STEPS if c == cmd)) in MENTIONED


class Select(unittest.TestCase):
    def sel(self, *files):
        return gs.select(list(files), STEPS, mentioned=mentioned)

    def test_nothing(self):
        self.assertEqual(self.sel(), ("none", []))

    def test_docs_only_runs_doc_invariants_only(self):
        mode, steps = self.sel("MyTradingSys/system/RELAY.md", "MyTradingSys/system/tasks/x.json")
        self.assertEqual(mode, "docs")
        self.assertEqual(steps, ["3tl", "3q", "3pc", "3c", "4d"])

    def test_non_live_code_is_smoke_with_its_own_test_and_the_shards_that_mention_it(self):
        mode, steps = self.sel("scripts/dev/dsa.py")
        self.assertEqual(mode, "smoke")
        self.assertIn("3ds", steps)          # name match survives the "(file, N shards)" command text
        self.assertNotIn("3k", steps)
        self.assertTrue({"3w", "3x", "3tl", "4b"} <= set(steps))
        self.assertNotIn("4", steps)         # a shard none of whose tests mention the module is not run

    def test_mentions_reads_the_tests_named_in_the_command(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "t").mkdir()
            (Path(d) / "t" / "test_a.py").write_text("import widget_core" + chr(10), encoding="utf-8")
            self.assertTrue(gs.mentions("widget_core", "pytest t", root=d))
            self.assertFalse(gs.mentions("other", "pytest t t/test_a.py", root=d))
            self.assertFalse(gs.mentions("widget_core", "pytest missing_dir", root=d))

    def refs(self, body, stem="widget_core"):
        """mentions(stem, ...) for a one-file pytest command whose test file holds `body`."""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "t").mkdir()
            (Path(d) / "t" / "test_a.py").write_text(body, encoding="utf-8")
            return gs.mentions(stem, "pytest t/test_a.py", root=d)

    def test_a_bare_word_is_not_a_reference(self):
        # the old bare-word match pulled the shard in for each of these (dsa: 3 of 5 pytest shards)
        for body in ("# widget_core is what we test elsewhere", "widget_core = 1", 'names = ["widget_core-card", "x"]',
                     '"""test_widget_core.py - guards the widget_core docs"""', "import widget_core_extra", "from other import widget_core_helper",
                     "import os  # widget_core", "x = other.widget_core_value", 'p = "docs/widget_core/notes.md"',
                     'assert "widget_core.py boot" in doc_text'):   # the filename inside a doc-text assertion, not a use of the module
            self.assertFalse(self.refs(body), body)

    def test_real_references_select_the_shard(self):
        for body in ("import widget_core", "import os, widget_core", "import widget_core as wc", "from widget_core import run",
                     "from scripts.dev.widget_core import run", "from scripts.dev import widget_core",
                     "from scripts.dev import (a,\n    widget_core)", "def f():\n    import widget_core\n",
                     'subprocess.run(["python", "scripts/dev/widget_core.py", "x"])', 'run("python widget_core.py boot")',
                     'p = ROOT / "scripts" / "dev" / "widget_core.py"', 'p = "scripts" + chr(92) + "dev" + chr(92) + "widget_core.py"',
                     'cmd = "python scripts/dev/widget_core"', 'with patch("widget_core.subprocess.run"):',
                     'm = importlib.import_module("scripts.dev.widget_core")', 'spec_from_file_location("widget_core", p)'):
            self.assertTrue(self.refs(body), body)

    def test_unreadable_test_file_counts_as_a_mention(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "test_a.py").write_text("x = 1", encoding="utf-8")
            with mock.patch.object(Path, "read_text", side_effect=OSError("locked")):
                self.assertTrue(gs.mentions("widget_core", "pytest test_a.py", root=d))

    def test_a_new_research_test_file_runs_the_discovery_check(self):
        # 2026-10-16: an unregistered research test file passed the ship gate and turned CI red (B150 lives in a pytest shard)
        mode, steps = self.sel("MyTradingSys/research/x_2026-10-16/test_x.py")
        self.assertEqual(mode, "smoke")
        self.assertIn("3gd", steps)

    def test_a_new_research_test_file_runs_the_ci_deps_lint(self):
        # 2026-10-16: research tests imported pandas, ci.yml did not install it; only CI saw it (the desktop has every package)
        mode, steps = self.sel("MyTradingSys/research/x_2026-10-16/test_x.py")
        self.assertEqual(mode, "smoke")
        self.assertIn("3dl", steps)

    def test_always_steps_exist_in_the_real_plan(self):
        import run_all_tests
        nums = {s.num for s in run_all_tests.build_plan(quick=True)}
        self.assertTrue(set(gs.ALWAYS) <= nums, set(gs.ALWAYS) - nums)

    def test_layer_code_runs_layer_tests(self):
        mode, steps = self.sel("MyTradingSys/backtest/layers/rsi/rsi.py")
        self.assertEqual(mode, "smoke")
        self.assertIn("5b", steps)

    def test_live_path_is_full(self):
        for f in ("MyTradingSys/execution/auto_trader.py", "scripts/dev/sync.py", "scripts/dev/run_all_tests.py",
                  "scripts/dev/auto_deploy.py", "scripts/sched/relay.py", "src/main/java/A.java", "pom.xml",
                  ".github/workflows/ci.yml", "MyTradingSys/runtime/x.py", "MyTradingSys/backtest/layers/fabio/orderflow_live.py"):
            mode, steps = self.sel(f)
            self.assertEqual(mode, "full", f)
            self.assertEqual(steps, [n for n, _ in STEPS])

    def test_unmapped_code_fails_closed(self):
        for f in ("weird/thing.py", "tools/run.ps1", "MyTradingSys/newarea/x.py", "scripts/dev/run.sh", "Makefile",
                  "MyTradingSys/backtest/data.bin"):
            self.assertEqual(self.sel(f)[0], "full", f)

    def test_one_live_file_among_docs_makes_it_full(self):
        self.assertEqual(self.sel("README.md", "MyTradingSys/execution/executor.py")[0], "full")

    def test_docs_ride_along_with_code(self):
        _, steps = self.sel("scripts/dev/dsa.py", "MyTradingSys/system/RELAY.md")
        self.assertIn("4d", steps)
        self.assertIn("3q", steps)

    def test_windows_separators(self):
        self.assertEqual(self.sel("MyTradingSys" + BS + "execution" + BS + "auto_trader.py")[0], "full")


if __name__ == "__main__":
    unittest.main()
