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


class Explain(unittest.TestCase):
    """explain() = select() plus the reason (2026-10-16: no record of WHY the ship gate chose full vs smoke)."""

    def ex(self, *files):
        return gs.explain(list(files), STEPS, mentioned=mentioned)

    def test_select_signature_and_return_unchanged(self):
        import inspect
        self.assertEqual(list(inspect.signature(gs.select).parameters), ["files", "steps", "mentioned"])
        self.assertEqual(len(self.sel_all("src/x.java")), 2)

    def sel_all(self, *files):
        return gs.select(list(files), STEPS, mentioned=mentioned)

    def test_full_names_the_file_that_forced_it(self):
        mode, nums, reason = self.ex("README.md", "scripts/dev/dsa.py", "src/x.java")
        self.assertEqual(mode, "full")
        self.assertEqual(nums, [n for n, _ in STEPS])
        self.assertIn("src/x.java", reason)
        self.assertIn("live path", reason)

    def test_full_for_unknown_path_says_so(self):
        mode, _, reason = self.ex("tools/odd.rb")
        self.assertEqual(mode, "full")
        self.assertIn("tools/odd.rb", reason)
        self.assertIn("no rule", reason)

    def test_smoke_names_the_always_steps(self):
        mode, nums, reason = self.ex("scripts/dev/dsa.py")
        self.assertEqual(mode, "smoke")
        self.assertTrue(reason.startswith("smoke"))
        for n in gs.ALWAYS:
            self.assertIn(n, reason)

    def test_explain_agrees_with_select(self):
        for files in ([], ["a.md"], ["scripts/dev/dsa.py"], ["src/x.java"], ["x.rb"]):
            mode, nums, _ = self.ex(*files)
            self.assertEqual((mode, nums), self.sel_all(*files))

    def test_none_and_docs_have_reasons(self):
        self.assertIn("nothing", self.ex()[2])
        self.assertIn("docs", self.ex("a.md")[2])



def tree(files):
    """A temp repo root holding {relpath: text}."""
    d = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(text, encoding="utf-8")
    return d


class FastGateRules(unittest.TestCase):
    """GATE_SPEED.md X1-X6 review: the fast gate's own machinery must not ship as smoke (it could weaken itself)."""

    def sel(self, *files):
        return gs.explain(list(files), STEPS, mentioned=mentioned, named=lambda b, c: False)[:2]

    def test_the_gate_machinery_is_full_gate(self):
        for f in ("wiring_scan", "ci_watch", "config_check", "ci_deps_lint", "run_staged_tests", "gate_impact"):
            self.assertEqual(self.sel(f"scripts/dev/{f}.py")[0], "full", f)
        self.assertEqual(self.sel("scripts/dev/gate_quarantine.tsv")[0], "full")

    def test_an_ordinary_dev_script_is_still_smoke(self):
        self.assertEqual(self.sel("scripts/dev/example_tool.py")[0], "smoke")

    def test_wiring_registry_edit_runs_the_wiring_steps_not_only_the_doc_steps(self):
        mode, nums = self.sel("MyTradingSys/system/wiring_registry.json")
        self.assertEqual(mode, "docs")
        self.assertIn("3x", nums)
        self.assertIn("3w", nums)
        self.assertNotIn("3x", self.sel("MyTradingSys/system/critical_files.json")[1])


class GateSpeedRules(unittest.TestCase):
    """GATE_SPEED.md D5/D6 (2026-10-18)."""

    def sel(self, *files, step_files=None):
        return gs.explain(list(files), STEPS, mentioned=mentioned, named=lambda b, c: False, step_files=step_files)[:2]

    def test_research_tsv_gz_and_err_are_data_not_a_full_gate(self):
        for f in ("MyTradingSys/research/x_2026/out.tsv", "MyTradingSys/research/x_2026/bars.json.gz", "MyTradingSys/research/x/run.err"):
            self.assertEqual(self.sel(f)[0], "docs", f)

    def test_config_files_are_smoke_not_full_and_settings_gets_its_json_step(self):
        steps = STEPS + [("3js", "python scripts/dev/test_config_check.py")]
        for f in (".gitignore", ".aiexclude", "scripts/dev/lookahead_allowlist.tsv", "scripts/dev/control_room.tpl.html"):
            mode, nums = gs.explain([f], steps, mentioned=mentioned, named=lambda b, c: False)[:2]
            self.assertEqual(mode, "smoke", f)
            self.assertNotIn("3js", nums, f)
        mode, nums = gs.explain([".claude/settings.json"], steps, mentioned=mentioned, named=lambda b, c: False)[:2]
        self.assertEqual(mode, "smoke")
        self.assertIn("3js", nums)

    def test_config_change_picks_the_steps_whose_tests_name_it(self):
        mode, nums = gs.explain(["scripts/dev/lookahead_allowlist.tsv"], STEPS, mentioned=mentioned,
                                named=lambda b, c: b == "lookahead_allowlist.tsv" and "tests/b" in c)[:2]
        self.assertEqual(mode, "smoke")
        self.assertIn("4b", nums)

    def test_live_and_unknown_config_still_full(self):
        for f in (".gitattributes", ".github/workflows/ci.yml", "mts.ps1", "scripts/core/x.json", "scripts/dev/run_extra_tests.py",
                  "MyTradingSys/runtime/run_list.txt", "scripts/dev/sub/x.tsv"):
            self.assertEqual(self.sel(f)[0], "full", f)

    def test_extra_subset_picks_own_test_study_folder_shared_module_and_references(self):
        tests = ["MyTradingSys/research/s1/test_a.py", "MyTradingSys/research/s2/test_b.py", "scripts/dev/test_tool.py",
                 "scripts/dev/test_other.py", "MyTradingSys/research/layer_lab/l1/test_event_table.py"]
        root = tree({tests[0]: "", tests[1]: "import tool\n", tests[2]: "", tests[3]: "x = open('RELAY.md')\n", tests[4]: ""})
        self.assertEqual(gs.extra_subset(["MyTradingSys/research/s1/a.py"], tests, root), [tests[0]])         # its study folder
        self.assertEqual(gs.extra_subset(["scripts/dev/tool.py"], tests, root), [tests[1], tests[2]])        # references + test_<base>
        self.assertEqual(gs.extra_subset(["MyTradingSys/system/RELAY.md"], tests, root), [tests[3]])        # a doc: only tests naming it
        self.assertEqual(gs.extra_subset(["MyTradingSys/research/layer_lab/l1/common.py"], tests, root), [tests[4]])
        self.assertEqual(gs.extra_subset(["MyTradingSys/research/s1/NOTES.md"], tests, root), [])           # a doc does not pull its folder

    def test_layer_subset_folder_references_and_all_on_shared_or_untested(self):
        mods = ["MyTradingSys.backtest.layers.rsi.test_rsi", "MyTradingSys.backtest.layers.bb.test_bb", "MyTradingSys.backtest.layers.vol.test_vol"]
        root = tree({"MyTradingSys/backtest/layers/rsi/test_rsi.py": "", "MyTradingSys/backtest/layers/bb/test_bb.py": "from ..rsi import rsi_core\n",
                     "MyTradingSys/backtest/layers/vol/test_vol.py": ""})
        self.assertEqual(gs.layer_subset(["MyTradingSys/backtest/layers/rsi/rsi_core.py"], mods, root), mods[:2])
        self.assertEqual(gs.layer_subset(["MyTradingSys/backtest/layers/vol/v.py"], mods, root), [mods[2]])
        self.assertEqual(gs.layer_subset(["MyTradingSys/backtest/layers/engine.py"], mods, root), mods)            # directly in layers/
        self.assertEqual(gs.layer_subset(["MyTradingSys/backtest/layers/vol/__init__.py"], mods, root), mods)      # shared module
        self.assertEqual(gs.layer_subset(["MyTradingSys/backtest/layers/newfam/x.py"], mods, root), mods)          # folder without tests

    def test_explain_with_step_files_picks_3xt_and_5b_only_when_the_subset_is_not_empty(self):
        sf = {"3xt": ["MyTradingSys/research/s1/test_a.py"], "5b": ["MyTradingSys.backtest.layers.rsi.test_rsi"]}
        with mock.patch.object(gs, "extra_subset", return_value=[]), mock.patch.object(gs, "layer_subset", return_value=[]):
            mode, nums = self.sel("MyTradingSys/research/s9/x.py", step_files=sf)
        self.assertEqual(mode, "smoke")
        self.assertFalse({"3xt", "5b"} & set(nums))
        with mock.patch.object(gs, "extra_subset", return_value=["t"]), mock.patch.object(gs, "layer_subset", return_value=["m"]):
            self.assertTrue({"3xt", "5b"} <= set(self.sel("MyTradingSys/backtest/layers/rsi/x.py", step_files=sf)[1]))

if __name__ == "__main__":
    unittest.main()
