"""Gate coverage: run_all_tests.py must run Fabio v3 + live-writer tests (TF1, review E7)."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_all_tests as rat

# tests that run fake plans must not append to the real runtime_data/gate_timing.jsonl
os.environ["MTS_GATE_TIMING"] = os.path.join(tempfile.mkdtemp(prefix="gate_timing_test_"), "t.jsonl")


class GateCoverage(unittest.TestCase):
    def test_pytest_paths_cover_v3_and_live_writers(self):
        paths = getattr(rat, "PYTEST_LAYER_PATHS", [])
        for want in ("fabio/v3/tests", "test_orderflow_live.py", "test_of_backfill.py", "test_htf_context_live.py"):
            self.assertTrue(any(p.endswith(want) for p in paths), want)

    def test_every_gated_path_exists(self):
        for p in getattr(rat, "PYTEST_LAYER_PATHS", []):
            self.assertTrue((rat.REPO / p).exists(), p)



class GateTmpCleanup(unittest.TestCase):
    def test_basetemp_dirs_are_removed_when_the_gate_process_exits(self):
        import subprocess
        code = ("import sys; sys.path.insert(0, r'%s'); import run_all_tests as r; "
                "print(r.pytest_cmd(['x'])[-1].split('=', 1)[1]); print(r.isolate_pytest_tmp())") % Path(__file__).resolve().parent
        env = dict(os.environ)
        env.pop("PYTEST_DEBUG_TEMPROOT", None)
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        made = [Path(line).parent if line.endswith("bt") else Path(line) for line in out.stdout.split()]
        self.assertEqual(len(made), 2, out.stdout)
        for d in made:
            self.assertFalse(d.exists(), f"{d} left in TEMP after the gate exited")


class TestPytestTmpIsolation(unittest.TestCase):
    def test_isolate_pytest_tmp_sets_fresh_root_for_children(self):
        import os
        old = os.environ.pop("PYTEST_DEBUG_TEMPROOT", None)
        try:
            root = rat.isolate_pytest_tmp()
            self.assertTrue(os.path.isdir(root))
            self.assertEqual(os.environ["PYTEST_DEBUG_TEMPROOT"], root)
        finally:
            os.environ.pop("PYTEST_DEBUG_TEMPROOT", None)
            if old is not None:
                os.environ["PYTEST_DEBUG_TEMPROOT"] = old


class TestParallelLayerGate(unittest.TestCase):
    def test_quick_gate_runs_every_layer_module(self):
        mods = rat.find_layer_modules()
        self.assertTrue(mods)
        for jobs in (1, 2, 4, 7, 10_000):
            chunks = rat.split_modules(mods, jobs)
            flat = [m for c in chunks for m in c]
            self.assertEqual(sorted(flat), sorted(mods), jobs)
            self.assertEqual(len(flat), len(set(flat)), jobs)
            self.assertTrue(all(chunks))

    def test_chunk_with_only_testless_modules_passes(self):
        ok, out = rat.exec_layer_chunks(["MyTradingSys.backtest.layers.alerts.test_live_toc_tfs"], 1)
        self.assertTrue(ok, out)

    def test_chunk_with_missing_module_still_fails(self):
        ok, _ = rat.exec_layer_chunks(["MyTradingSys.backtest.layers.alerts.no_such_module_xyz"], 1)
        self.assertFalse(ok)

    def test_gate_jobs_env(self):
        import os
        old = os.environ.get("MTS_GATE_JOBS")
        try:
            os.environ["MTS_GATE_JOBS"] = "1"
            self.assertEqual(rat.gate_jobs(), 1)
            os.environ["MTS_GATE_JOBS"] = "0"
            self.assertEqual(rat.gate_jobs(), 1)
            os.environ.pop("MTS_GATE_JOBS")
            self.assertGreaterEqual(rat.gate_jobs(), 1)
        finally:
            os.environ.pop("MTS_GATE_JOBS", None)
            if old is not None:
                os.environ["MTS_GATE_JOBS"] = old

    def test_backup_trigger_minute_differs_from_deploy_slot(self):
        import re
        d = rat.REPO / "scripts"
        backup = (d / "dev" / "install_backup_task.ps1").read_text(encoding="utf-8")
        deploy = (d / "sched" / "register_cicd_tasks.ps1").read_text(encoding="utf-8")
        b = re.search(r"-At \(Get-Date\)\.Date(?:\.AddMinutes\((\d+)\))?\s+-RepetitionInterval", backup)
        self.assertIsNotNone(b, "backup trigger must anchor on today's midnight")
        d_ = re.search(r"-At \(Get-Date\)\.Date(?:\.AddMinutes\((\d+)\))?\s+-RepetitionInterval \(New-TimeSpan -Minutes 15\)", deploy)
        self.assertIsNotNone(d_)
        bo, do = int(b.group(1) or 0), int(d_.group(1) or 0)
        self.assertNotEqual(bo % 15, do % 15)


# The 46 steps the gate had before it ran concurrently: speeding it up must not drop one.
# One label per line; a new gate step needs no edit here (the test is a subset check).
ORIGINAL_LABELS = {
    "Step 1: Execution tests",
    "Step 2: G1G2 offline test",
    "Step 3: Static test suite",
    "Step 3b: Guide checker tests",
    "Step 3c: Guide in sync",
    "Step 3r: Alert rate checker tests",
    "Step 3s: Testnet status tests",
    "Step 3f: Funnel report tests",
    "Step 3dk: Desk board tests",
    "Step 3tk: Task card tests",
    "Step 3td: Tom ledger date tests",
    "Step 3hs: Tom holdout split tests",
    "Step 3sq: Spec quote checker tests",
    "Step 3ly: Layer index tests",
    "Step 3cx: Layer lab runner tests",
    "Step 3tl: Task card lint",
    "Step 3q: INDEX/BUGS consistency",
    "Step 3p: P4 corrected script tests",
    "Step 3t: T093 imbalance tests",
    "Step 3d: Quote checker tests",
    "Step 3h: Launcher static tests",
    "Step 3g: Gate coverage tests",
    "Step 3k: sync.py tests",
    "Step 3e: DSA worker tests",
    "Step 3sh: Screenshot intake tests",
    "Step 3mg: Project group map tests",
    "Step 3xt: Extra tests",
    "Step 3ad: Auto-deploy tests",
    "Step 3hy: Daily hygiene tests",
    "Step 3ms: make_status tests",
    "Step 3cs: Cloud setup hook tests",
    "Step 3pc: Prompt contract tests",
    "Step 3ds: DSA helper CLI tests",
    "Step 3cr: Control Room tests",
    "Step 3lh: GPT lane health tests",
    "Step 3rb: Relay board tests",
    "Step 3af: Artifact registry tests",
    "Step 3bk: Backup snapshot tests",
    "Step 3lm: Live mirror tests",
    "Step 3w: Wiring gate tests",
    "Step 3x: Wiring check",
    "Step 4: Pytest tests",
    "Step 5: Maven tests",
    "Step 5b: Layer tests",
    "Step 5c: Options tests",
    "Step 6: Backtest tests",
}


class TestGateKeepsEveryStep(unittest.TestCase):
    def test_plan_has_every_original_step_exactly_once(self):
        for quick in (True, False):
            labels = [s.label for s in rat.build_plan(quick)]
            self.assertEqual(len(labels), len(set(labels)), quick)
            self.assertLessEqual(ORIGINAL_LABELS, set(labels), quick)

    def test_quick_skips_only_maven_and_backtest(self):
        skipped = {s.num for s in rat.build_plan(True) if s.skip}
        self.assertEqual(skipped, {"5", "6"})
        self.assertEqual({s.num for s in rat.build_plan(False) if s.skip} - {"6"}, set())

    def test_serial_steps_are_real_steps_and_get_the_serial_lane(self):
        plan = {s.num: s for s in rat.build_plan(True)}
        for num in rat.SERIAL_STEPS:
            self.assertIn(num, plan)
            self.assertEqual(plan[num].lane, "seq", num)
        self.assertEqual(plan["4"].lane, "par")

    def test_pytest_steps_that_run_beside_others_have_own_basetemp_and_no_cache(self):
        plan = {s.num: s for s in rat.build_plan(True)}
        for num in rat.PYTEST_SHARD_NUMS + ("4d", "4e", "4f", "5c"):
            cmd = " ".join(plan[num].cmd_text.split())
            self.assertIn("--basetemp=", cmd, num)
            self.assertIn("no:cacheprovider", cmd, num)


class TestShardedPytest(unittest.TestCase):
    def test_every_test_file_of_the_tests_dir_is_in_exactly_one_shard(self):
        plan = {s.num: s for s in rat.build_plan(True)}
        shards = [plan[n].cmd_text for n in rat.PYTEST_SHARD_NUMS + ("4d",)]
        for f in (rat.REPO / "MyTradingSys" / "tests").glob("test_*.py"):
            hits = sum(f"MyTradingSys/tests/{f.name}" in c.split() or f"MyTradingSys/tests/{f.name}" in c for c in shards)
            self.assertEqual(hits, 1, f.name)

    def test_smoke_selection_skips_unselected_steps_and_full_keeps_all(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.txt"
            f.write_text("MyTradingSys/system/RELAY.md\n", encoding="utf-8")
            plan, mode = rat.apply_selection(rat.build_plan(True), ["--smoke", "--changed-file", str(f)])
            self.assertEqual(mode, "docs")
            ran = {s.num for s in plan if not s.skip}
            self.assertLessEqual({"3tl", "3q", "3pc", "3c", "4d"}, ran)
            self.assertLessEqual(ran - {"3tl", "3q", "3pc", "3c", "4d"}, {"3xt"})   # GATE_SPEED D6: extra tests that name RELAY.md
            f.write_text("MyTradingSys/execution/executor.py\n", encoding="utf-8")
            plan, mode = rat.apply_selection(rat.build_plan(True), ["--smoke", "--changed-file", str(f)])
            self.assertEqual(mode, "full")
            self.assertEqual({s.num for s in plan if s.skip}, {"5", "6"})
            plan, mode = rat.apply_selection(rat.build_plan(True), ["--smoke", "--changed-file", str(Path(d) / "missing")])
            self.assertIsNone(mode)   # unreadable list: everything runs
            self.assertEqual({s.num for s in plan if s.skip}, {"5", "6"})


def fake(num, log, seconds=0.15, ok=True, boom=False):
    def run():
        log.append(("start", num, time.monotonic()))
        time.sleep(seconds)
        log.append(("end", num, time.monotonic()))
        if boom:
            raise RuntimeError("boom " + num)
        return ok, f"out of {num}\nWARN note {num}"
    return rat.Step(num, "desc " + num, "Step " + num + ": label", run=run, cmd_text="fake " + num)


def max_overlap(log, nums):
    running, peak = set(), 0
    for kind, num, _ in sorted(log, key=lambda e: e[2]):
        if num not in nums:
            continue
        running.add(num) if kind == "start" else running.discard(num)
        peak = max(peak, len(running))
    return peak


def at(log, kind, num):
    return next(t for k, n, t in log if k == kind and n == num)


class TestConcurrentGate(unittest.TestCase):
    def run_plan(self, plan, jobs):
        buf = io.StringIO()
        results = rat.run_plan(plan, jobs, out=buf)
        return results, buf.getvalue()

    def test_independent_steps_overlap_and_all_results_come_back(self):
        log = []
        plan = [fake(n, log) for n in ("3a", "3b", "3c", "3d")]
        results, _ = self.run_plan(plan, 4)
        self.assertEqual(results, {"3a": True, "3b": True, "3c": True, "3d": True})
        self.assertGreaterEqual(max_overlap(log, {"3a", "3b", "3c", "3d"}), 2)

    def test_jobs_1_runs_one_at_a_time_in_definition_order(self):
        log = []
        plan = [fake(n, log, 0.02) for n in ("3a", "3ly", "3b", "4")]
        self.run_plan(plan, 1)
        self.assertEqual(max_overlap(log, {s.num for s in plan}), 1)
        self.assertEqual([n for k, n, _ in log if k == "start"], ["3a", "3ly", "3b", "4"])

    def test_serial_steps_start_after_the_pool_and_never_overlap(self):
        log = []
        plan = [fake(n, log) for n in ("3a", "3ly", "3b", "3af", "4", "3x")]
        self.run_plan(plan, 4)
        pool_end = max(at(log, "end", n) for n in ("3a", "3b", "4"))
        for n in ("3ly", "3af", "3x"):
            self.assertGreaterEqual(at(log, "start", n), pool_end, n)
        self.assertEqual(max_overlap(log, {"3ly", "3af", "3x"}), 1)

    def test_slowest_step_is_submitted_first(self):
        log = []
        plan = [fake(n, log, 0.05) for n in ("3a", "3b", "3c", "4")]
        self.run_plan(plan, 2)
        first_two = [n for k, n, _ in sorted(log, key=lambda e: e[2]) if k == "start"][:2]
        self.assertIn("4", first_two)

    def test_each_step_prints_one_whole_block_with_time_and_progress(self):
        log = []
        plan = [fake(n, log, 0.05) for n in ("3a", "3b", "3c", "4")]
        _, text = self.run_plan(plan, 4)
        blocks = [b for b in text.split("\n[Step ")[1:]]
        self.assertEqual(len(blocks), 4)
        for b in blocks:
            self.assertEqual(sum(1 for ln in b.splitlines() if ln.startswith("Step ") and ln.endswith(": PASS")), 1, b)
            self.assertIn("Command: fake", b)
            self.assertRegex(b, r"Elapsed: \d+\.\ds \(\d/4 done, \+\d+s\)")
            self.assertIn("WARN note", b)      # a warning on a passing step stays visible
        self.assertIn("Gate: 4 steps, 4 at a time", text)

    def test_a_failing_and_a_crashing_step_are_failed_steps_not_a_dead_gate(self):
        log = []
        plan = [fake("3a", log, ok=False), fake("3b", log, boom=True), fake("3c", log)]
        results, text = self.run_plan(plan, 3)
        self.assertEqual(results, {"3a": False, "3b": False, "3c": True})
        self.assertIn("Step 3a: FAIL", text)
        self.assertIn("RuntimeError: boom 3b", text)
        self.assertIn("Last output:", text)

    def test_skipped_steps_are_reported_first_and_count_as_none(self):
        plan = [rat.Step("5", "Maven Java tests", "Step 5: Maven tests", skip="skipped with --quick"), fake("3a", [])]
        results, text = self.run_plan(plan, 2)
        self.assertEqual(results, {"5": None, "3a": True})
        self.assertIn("Step 5: SKIP (skipped with --quick)", text)

    def test_stdout_becomes_line_buffered(self):
        stream = io.TextIOWrapper(io.BytesIO(), write_through=False)
        self.assertFalse(stream.line_buffering)
        self.assertIs(rat.unbuffer(stream), stream)
        self.assertTrue(stream.line_buffering)

    def test_missing_executable_is_a_skip_with_a_reason(self):
        ok, why = rat.exec_step(["definitely-not-a-real-executable-xyz"])
        self.assertIsNone(ok)
        self.assertIn("not found", why)

    def test_failure_shows_the_tail_and_ci_shows_everything(self):
        out = "\n".join(f"line {i}" for i in range(40))
        old = os.environ.pop("CI", None)   # GitHub sets CI=true; the tail view is only asserted with it unset
        try:
            block = "\n".join(rat.format_step("3a", "d", "c", False, out, 1.0))
            self.assertIn("line 39", block)
            self.assertNotIn("line 10\n", block)
            os.environ["CI"] = "1"
            self.assertIn("line 0\n", "\n".join(rat.format_step("3a", "d", "c", False, out, 1.0)) + "\n")
        finally:
            os.environ.pop("CI", None)
            if old is not None:
                os.environ["CI"] = old


class TestCiAnnotation(unittest.TestCase):
    """2026-10-16: job logs need a login even on a public repo, so a red ubuntu job could not be read by any session; an ::error
    annotation is public through the check-runs API."""

    def setUp(self):
        self.old = os.environ.get("GITHUB_ACTIONS")

    def tearDown(self):
        os.environ.pop("GITHUB_ACTIONS", None)
        if self.old is not None:
            os.environ["GITHUB_ACTIONS"] = self.old

    def test_off_actions_there_is_no_annotation(self):
        os.environ.pop("GITHUB_ACTIONS", None)
        self.assertIsNone(rat.ci_annotation("4f", "d", "FAIL: x"))
        self.assertFalse(any(ln.startswith("::error") for ln in rat.format_step("4f", "d", "c", False, "FAIL: x", 1.0)))

    def test_failed_step_on_actions_emits_one_escaped_error_line_from_the_first_failure(self):
        os.environ["GITHUB_ACTIONS"] = "true"
        out = "noise 1\nnoise 2\nFAIL: test_a (m.T)\nAssertionError: 100% wrong\n"
        lines = rat.format_step("4f", "Pytest layer tests", "c", False, out, 1.0)
        notes = [ln for ln in lines if ln.startswith("::error ")]
        self.assertEqual(len(notes), 1)
        self.assertIn("title=Step 4f FAIL", notes[0])
        self.assertIn("100%25 wrong", notes[0])
        self.assertNotIn("noise", notes[0])
        self.assertNotIn("\n", notes[0])

    def test_failed_step_with_empty_output_is_still_annotated(self):
        os.environ["GITHUB_ACTIONS"] = "true"
        notes = [ln for ln in rat.format_step("4f", "d", "c", False, "", 1.0) if ln.startswith("::error ")]
        self.assertEqual(len(notes), 1)
        self.assertIn("(no output)", notes[0])

    def test_passing_step_has_no_annotation(self):
        os.environ["GITHUB_ACTIONS"] = "true"
        self.assertFalse(any(ln.startswith("::error") for ln in rat.format_step("4f", "d", "c", True, "all ok", 1.0)))


class TestExtraTestsRunConcurrently(unittest.TestCase):
    def test_files_overlap_each_gets_own_basetemp_and_failures_keep_list_order(self):
        import threading
        import run_extra_tests as rx
        seen, live, peak, lock = [], [0], [0], threading.Lock()

        def one(rel, basetemp):
            with lock:
                live[0] += 1
                peak[0] = max(peak[0], live[0])
                seen.append(str(basetemp))
            time.sleep(0.1)
            with lock:
                live[0] -= 1
            return (rel not in ("b.py", "d.py")), ("missing" if rel == "d.py" else "1 passed")

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            bad = rx.run_files(["a.py", "b.py", "c.py", "d.py"], 4, one=one, tmp=tempfile.mkdtemp())
        self.assertGreaterEqual(peak[0], 2)
        self.assertEqual(len(set(seen)), 4)
        self.assertEqual(bad, ["b.py", "d.py: missing"])
        self.assertEqual(sorted(ln[:4] for ln in buf.getvalue().splitlines()), ["FAIL", "FAIL", "ok  ", "ok  "])

    def test_one_job_is_sequential(self):
        import run_extra_tests as rx
        order = []
        with contextlib.redirect_stdout(io.StringIO()):
            rx.run_files(["a.py", "b.py", "c.py"], 1, one=lambda rel, bt: (order.append(rel) or True, "ok"), tmp=tempfile.mkdtemp())
        self.assertEqual(order, ["a.py", "b.py", "c.py"])

    def test_jobs_env_knob(self):
        import run_extra_tests as rx
        old = os.environ.get("MTS_GATE_JOBS")
        try:
            os.environ["MTS_GATE_JOBS"] = "3"
            self.assertEqual(rx.jobs(), 3)
            os.environ["MTS_GATE_JOBS"] = "0"
            self.assertEqual(rx.jobs(), 1)
        finally:
            os.environ.pop("MTS_GATE_JOBS", None)
            if old is not None:
                os.environ["MTS_GATE_JOBS"] = old


class TestGateTimingLog(unittest.TestCase):
    """Per-step timings persist as JSON lines in an untracked file (2026-10-16: no gate timing was kept anywhere)."""

    def test_record_timing_writes_one_valid_json_line(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "sub" / "gate_timing.jsonl"
            rat.record_timing("3w", "Wiring", 1.234, True, "smoke", path=path)
            rat.record_timing("4", "Pytest", 9.0, False, "full", path=path)
            rows = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 2)
        self.assertEqual({"step", "name", "secs", "ok", "mode", "utc", "sha"}, set(rows[0]))
        self.assertEqual((rows[0]["step"], rows[0]["name"], rows[0]["secs"], rows[0]["ok"], rows[0]["mode"]), ("3w", "Wiring", 1.23, True, "smoke"))
        self.assertFalse(rows[1]["ok"])

    def test_record_timing_never_breaks_the_gate(self):
        rat.record_timing("1", "x", 1.0, True, None, path=Path(__file__) / "t.jsonl")   # a file where a directory is needed: swallowed

    def test_run_plan_logs_every_finished_step(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "t.jsonl"
            with mock.patch.dict(os.environ, {"MTS_GATE_TIMING": str(path)}):
                plan = [rat.Step("9a", "A", "Step 9a", run=lambda: (True, "")), rat.Step("9b", "B", "Step 9b", run=lambda: (False, "boom"))]
                rat.run_plan(plan, 1, out=io.StringIO())
            rows = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([(r["step"], r["ok"]) for r in rows], [("9a", True), ("9b", False)])

    def test_timing_file_is_gitignored(self):
        import subprocess
        r = subprocess.run(["git", "check-ignore", "-q", "runtime_data/gate_timing.jsonl"], cwd=str(rat.REPO))
        self.assertEqual(r.returncode, 0)

    def test_plan_reason_is_printed_for_a_ship(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.txt"
            f.write_text("src/x.java" + chr(10), encoding="utf-8")
            plan, mode = rat.apply_selection(rat.build_plan(True), ["--smoke", "--changed-file", str(f)])
            self.assertEqual(mode, "full")
            self.assertIn("src/x.java", rat.gate_reason)



class TestGateSpeed(unittest.TestCase):
    """GATE_SPEED.md D1-D3 (2026-10-18): precheck, fail-fast, slot around the main phase only, same-tree pass record."""

    def setUp(self):
        rat.NOT_RUN.clear()

    def run_plan(self, plan, **kw):
        buf = io.StringIO()
        return rat.run_plan(plan, 4, out=buf, **kw), buf.getvalue()

    def slot(self, log):
        @contextlib.contextmanager
        def held():
            log.append(("start", "slot", time.monotonic()))
            yield
            log.append(("end", "slot", time.monotonic()))
        return held

    def test_a_cheap_failure_stops_the_gate_before_the_slow_steps_and_the_slot(self):
        log = []
        plan = [fake("4d", log, 0.01, ok=False), fake("3c", log, 0.01), fake("4h", log, 0.01), fake("3xt", log, 0.01)]
        results, text = self.run_plan(plan, precheck=True, fail_fast=True, slot=self.slot(log))
        self.assertEqual(results, {"4d": False, "3c": True, "4h": None, "3xt": None})
        self.assertEqual({n for _, n, _ in log}, {"4d", "3c"})          # neither slow step nor the slot ran
        self.assertIn("Step 4h: NOT RUN (precheck failed: step 4d)", text)
        self.assertEqual(rat.NOT_RUN, {"4h": "precheck failed: step 4d", "3xt": "precheck failed: step 4d"})

    def test_slot_is_held_around_the_main_phase_only(self):
        log = []
        plan = [fake("4d", log, 0.02), fake("4h", log, 0.02), fake("3xt", log, 0.02)]
        _, text = self.run_plan(plan, precheck=True, slot=self.slot(log))
        self.assertGreaterEqual(at(log, "start", "slot"), at(log, "end", "4d"))
        self.assertLessEqual(at(log, "start", "slot"), min(at(log, "start", "4h"), at(log, "start", "3xt")))
        self.assertIn("Precheck passed", text)

    def test_fail_fast_does_not_start_new_steps_after_a_failure(self):
        log = []
        plan = [fake("4h", log, 0.01, ok=False)] + [fake(f"9{i}", log, 0.01) for i in range(6)]
        with mock.patch.object(rat, "record_timing") as timing:
            results, text = rat.run_plan(plan, 1, out=io.StringIO(), fail_fast=True), None
        self.assertEqual(results["4h"], False)
        self.assertTrue(all(results[f"9{i}"] is None for i in range(6)))
        self.assertEqual([c.args[0] for c in timing.call_args_list], ["4h"])   # a NOT RUN step is not timed

    def test_summary_fails_closed_on_a_not_run_step(self):
        plan = [fake("3a", [], 0.0)]
        with mock.patch.object(rat, "build_plan", return_value=plan), mock.patch.object(rat, "run_plan",
                side_effect=lambda *a, **k: (rat.NOT_RUN.update({"3a": "x"}) or {"3a": None})), \
                mock.patch.object(rat, "lower_priority"), mock.patch.object(rat, "isolate_pytest_tmp"), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(rat.main(["--quick"]), 1)
        self.assertIn("NOT RUN (x)", out.getvalue())

    def test_targeted_tests_name_the_test_files_that_reference_the_change(self):
        with tempfile.TemporaryDirectory() as d:
            t = Path(d) / "MyTradingSys" / "tests"
            t.mkdir(parents=True)
            (t / "test_relay.py").write_text("RELAY = 'MyTradingSys/system/RELAY.md'\n", encoding="utf-8")
            (t / "test_kit.py").write_text("import screen\n", encoding="utf-8")
            (t / "test_none.py").write_text("x = 1\n", encoding="utf-8")
            self.assertEqual(rat.targeted_tests(["MyTradingSys/system/RELAY.md", "MyTradingSys/research/s/screen.py"], d),
                             ["MyTradingSys/tests/test_kit.py", "MyTradingSys/tests/test_relay.py"])

    def test_precheck_flag_adds_the_targeted_step_in_every_mode(self):
        with tempfile.TemporaryDirectory() as d:
            lst = Path(d) / "changed.txt"
            lst.write_text("MyTradingSys/system/RELAY.md\n", encoding="utf-8")
            plan, mode = rat.apply_selection(rat.build_plan(True), ["--smoke", "--precheck", "--changed-file", str(lst)])
            self.assertEqual(mode, "docs")
            four_t = [s for s in plan if s.num == rat.TARGET_STEP]
            self.assertEqual(len(four_t), 1)
            self.assertIsNone(four_t[0].skip)
            self.assertIn("test_relay_prompts.py", four_t[0].cmd_text)
            plan, _ = rat.apply_selection(rat.build_plan(True), ["--smoke", "--changed-file", str(lst)])
            self.assertFalse([s for s in plan if s.num == rat.TARGET_STEP])   # CI / auto_deploy argv: no precheck step

    def test_config_check_is_a_cheap_gate_step(self):
        plan = {s.num: s for s in rat.build_plan(True)}
        self.assertIn("test_config_check.py", plan["3js"].cmd_text)
        self.assertIn("3js", rat.CHEAP_STEPS)


class TestPassRecord(unittest.TestCase):
    """GATE_SPEED D3: a step that passed on this exact clean tree, same signature, same python, < 24 h, is not run again."""

    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", "-C", str(self.d), *args], check=True, capture_output=True)
        (self.d / "a.py").write_text("a\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.d), "add", "a.py"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.d), "commit", "-q", "-m", "a"], check=True, capture_output=True)
        self.plan = [rat.Step("3a", "d", "l", cmd_text="python x.py --basetemp=C:/t/1"), rat.Step("3b", "d", "l", cmd_text="python y.py")]

    def tearDown(self):
        import shutil
        shutil.rmtree(self.d, ignore_errors=True)

    def save(self, results, **kw):
        return rat.save_record(self.plan, results, root=self.d, **kw)

    def test_passing_steps_are_reused_on_the_same_tree_and_a_failed_step_runs_again(self):
        self.assertTrue(self.save({"3a": True, "3b": False}))
        self.assertEqual(set(rat.load_reused(self.plan, root=self.d)), {"3a"})

    def test_basetemp_does_not_change_the_signature_but_the_command_does(self):
        self.save({"3a": True, "3b": True})
        again = [rat.Step("3a", "d", "l", cmd_text="python x.py --basetemp=C:/t/9"), rat.Step("3b", "d", "l", cmd_text="python y.py --only z")]
        self.assertEqual(set(rat.load_reused(again, root=self.d)), {"3a"})

    def test_a_new_commit_a_dirty_tree_or_an_old_record_reuses_nothing(self):
        self.save({"3a": True, "3b": True})
        (self.d / "new.txt").write_text("u\n", encoding="utf-8")            # untracked file: dirty
        self.assertEqual(rat.load_reused(self.plan, root=self.d), {})
        self.assertFalse(self.save({"3a": True}))                            # and a dirty tree writes no record
        (self.d / "new.txt").unlink()
        self.assertEqual(set(rat.load_reused(self.plan, root=self.d)), {"3a", "3b"})
        self.assertEqual(rat.load_reused(self.plan, root=self.d, now=time.time() + rat.RECORD_MAX_AGE_S + 1), {})
        (self.d / "a.py").write_text("b\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.d), "commit", "-qam", "b"], check=True, capture_output=True)
        self.assertEqual(rat.load_reused(self.plan, root=self.d), {})

    def test_head_moving_during_the_gate_writes_no_record(self):
        start = rat.tree_state(self.d)[0]
        (self.d / "a.py").write_text("c\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.d), "commit", "-qam", "c"], check=True, capture_output=True)
        self.assertFalse(self.save({"3a": True}, start_tree=start))

    def test_reused_steps_print_pass_and_do_not_run(self):
        ran = []
        plan = [rat.Step("3a", "d", "l", run=lambda: (ran.append(1), (True, ""))[1], cmd_text="x")]
        results = rat.run_plan(plan, 2, out=io.StringIO(), reused={"3a": "reused: passed"})
        self.assertEqual((results, ran), ({"3a": True}, []))

    def test_ci_never_uses_the_record(self):
        with mock.patch.dict(os.environ, {"CI": "true"}), mock.patch.object(rat, "build_plan", return_value=[]), \
                mock.patch.object(rat, "load_reused") as load, mock.patch.object(rat, "save_record") as save, \
                mock.patch.object(rat, "lower_priority"), mock.patch.object(rat, "isolate_pytest_tmp"), \
                contextlib.redirect_stdout(io.StringIO()):
            rat.main(["--quick", "--record"])
        load.assert_not_called()
        save.assert_not_called()

if __name__ == "__main__":
    unittest.main()
