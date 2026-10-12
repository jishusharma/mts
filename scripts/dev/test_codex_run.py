"""codex_run.py (layer lab runner): card choice, model/effort from the card, the command line, the lock, the ask templates,
the delivery index, and the CODEX lane rules in tasks.py. Spec: MyTradingSys/system/LAYER_LAB.md."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codex_run as R
import tasks as T


def card(cid="lab-a", kind="audit", **kw):
    c = R.make_card("Audit the Tom v2 spec", kind, ["MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md"], cid=cid,
                    cmds=kw.pop("cmds", ["python x.py"] if kind == "run" else []), tests=kw.pop("tests", "test_x fails first" if kind == "build" else ""))
    c.update({"state": "ready", **kw})
    return c


class LaneRulesTest(unittest.TestCase):
    def test_each_kind_template_meets_the_definition_of_ready(self):
        for kind in R.TEMPLATES:
            with self.subTest(kind=kind):
                self.assertEqual(T.problems(card(kind=kind)), [])

    def test_build_template_leaves_the_gate_to_the_runner(self):
        text = " ".join(R.TEMPLATES["build"]["steps"]) + R.TEMPLATES["build"]["done_when"]
        self.assertIn("Do not run scripts/dev/run_all_tests.py", text)
        self.assertNotIn("quick gate passes", text)

    def test_kind_is_required_and_checked(self):
        self.assertTrue(any("kind" in m for m in T.problems(card(kind="audit") | {"kind": ""})))
        self.assertTrue(any("kind" in m for m in T.problems(card() | {"kind": "think"})))

    def test_build_needs_tests_and_run_needs_commands(self):
        self.assertTrue(any("tests" in m for m in T.problems(card(kind="build", tests=""))))
        self.assertTrue(any("commands" in m for m in T.problems(card(kind="run", cmds=[]))))

    def test_effort_override_is_checked(self):
        self.assertTrue(any("effort" in m for m in T.problems(card(effort="huge"))))
        self.assertEqual(T.problems(card(effort="xhigh")), [])

    def test_setting_comes_from_kind_unless_the_card_overrides(self):
        self.assertEqual(T.codex_setting(card(kind="audit")), ("gpt-6-astra", "high"))
        self.assertEqual(T.codex_setting(card(kind="run")), ("gpt-6-luna", "low"))
        self.assertEqual(T.codex_setting(card(kind="build", model="gpt-6-astra", effort="max")), ("gpt-6-astra", "max"))

    def test_brief_names_the_report_and_fits_the_cap(self):
        b = T.brief(card())
        self.assertIn("layer_lab/reports/<UTC date>_lab-a.md", b)
        self.assertLessEqual(len(b.splitlines()), T.MAX_BRIEF)

    def test_plain_next_hides_codex_cards_from_claude_sessions(self):
        with tempfile.TemporaryDirectory() as d:
            T.save(d, card())
            old, T.REPO = T.REPO, Path(d)
            try:
                for lane, want in ((None, "NO_READY_CARD"), ("CODEX", "lab-a [CODEX")):
                    buf = io.StringIO()
                    with contextlib.redirect_stdout(buf):
                        T.main(["next"] + (["--lane", lane] if lane else []))
                    self.assertIn(want, buf.getvalue())
            finally:
                T.REPO = old


class PickTest(unittest.TestCase):
    def test_skips_claimed_stuck_and_foreign_lanes(self):
        a, b, c, s = card("lab-a"), card("lab-b"), card("lab-c"), card("son") | {"lane": "SONNET"}
        self.assertEqual(R.pick([s, a, b, c], {"lab-a"}, {"lab-b": R.MAX_ATTEMPTS})["id"], "lab-c")
        self.assertIsNone(R.pick([s], set(), {}))
        self.assertEqual(R.pick([a, b], set(), {"lab-a": R.MAX_ATTEMPTS - 1})["id"], "lab-a")

    def test_attempts_count_only_real_runs_that_did_not_finish(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "lab_runs"
            p.mkdir()
            rows = [{"card": "x", "outcome": "INCOMPLETE"}, {"card": "x", "outcome": "BLOCKED"}, {"card": "x", "outcome": "DONE"},
                    {"card": "y", "outcome": "INCOMPLETE", "dry": True}]
            (p / "runs.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n", encoding="utf-8")
            self.assertEqual(R.attempts(d), {"x": 2})
            self.assertEqual(R.attempts(Path(d) / "none"), {})


class CommandTest(unittest.TestCase):
    def test_model_effort_and_sandbox_reach_the_command_line(self):
        cmd = R.command("codex.exe", card(kind="audit"), "F:/wt", "workspace-write")
        self.assertEqual(cmd[:4], ["codex.exe", "exec", "-m", "gpt-6-astra"])
        self.assertIn('model_reasoning_effort="high"', cmd)
        self.assertEqual(cmd[cmd.index("-s") + 1], "workspace-write")
        self.assertEqual(cmd[cmd.index("-C") + 1], "F:/wt")
        self.assertEqual(cmd[-1], "-")
        self.assertIn("gpt-6-luna", R.command("codex.exe", card(kind="run"), "F:/wt", "workspace-write"))

    def test_prompt_forbids_git_and_carries_report_and_brief(self):
        p = R.prompt(card(), "F:/wt", "F:/home/packs/lab-a.md", datetime(2026, 10, 12, 9, 5, tzinfo=timezone.utc))
        for want in ("do NOT run git", "layer_lab/reports/2026-10-12_lab-a.md", "tasks.py done lab-a", "do NOT mark the card done", "TASK lab-a [CODEX"):
            self.assertIn(want, p)
        self.assertNotIn("sync.py claim \"", p)

    def test_commit_message_has_result_and_session_trailer(self):
        m = R.commit_message(card(), "DONE", "FIX-FIRST, 2 HIGH", datetime(2026, 10, 12, 9, 5, tzinfo=timezone.utc))
        self.assertIn("Result: FIX-FIRST, 2 HIGH", m)
        self.assertIn("MTS-Session: MTS-2026-10-12-0905Z-COD-LAB-lab-a", m)
        self.assertIn("gpt-6-astra / high", m)


class JudgeTest(unittest.TestCase):
    REP = "MyTradingSys/research/layer_lab/reports/2026-10-12_lab-a.md"
    CARD = "MyTradingSys/system/tasks/lab-a.json"

    def test_done_needs_the_card_closed_and_a_report(self):
        self.assertEqual(R.judge({"state": "done"}, [self.REP], "audit", [self.REP, self.CARD]), "DONE")
        self.assertEqual(R.judge({"state": "ready"}, [self.REP], "audit", [self.REP]), "BLOCKED")
        self.assertEqual(R.judge({"state": "done"}, [], "audit", [self.CARD]), "INCOMPLETE")
        self.assertEqual(R.judge({"state": "ready"}, [], "audit", []), "INCOMPLETE")

    def test_audit_and_run_may_not_write_code_but_build_may(self):
        code = "MyTradingSys/backtest/tom_dax_bt.py"
        for kind in ("audit", "run"):
            self.assertEqual(R.judge({"state": "done"}, [self.REP], kind, [self.REP, self.CARD, code]), "OUT_OF_SCOPE")
        self.assertEqual(R.judge({"state": "done"}, [self.REP], "build", [self.REP, self.CARD, code]), "DONE")
        self.assertEqual(R.out_of_scope("run", [self.REP, "MyTradingSys/research/layer_lab/TRIALS.md", "MyTradingSys/system/tasks/new.json"]), [])

    def test_out_of_scope_and_ship_failures_count_as_tries(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "lab_runs"
            p.mkdir()
            (p / "runs.jsonl").write_text(json.dumps({"card": "x", "outcome": "OUT_OF_SCOPE"}) + chr(10) + json.dumps({"card": "x", "outcome": "SHIP_FAILED"}) + chr(10), encoding="utf-8")
            self.assertEqual(R.attempts(d), {"x": 2})

    def test_exe_lookup_order(self):
        self.assertEqual(R.find_exe({"MTS_CODEX_EXE": "X"}, lambda n: "P", lambda g: ["G"]), "X")
        self.assertEqual(R.find_exe({}, lambda n: "P", lambda g: ["G"]), "P")
        self.assertEqual(R.find_exe({"LOCALAPPDATA": "L"}, lambda n: None, lambda g: ["G"]), "G")
        with self.assertRaises(SystemExit):
            R.find_exe({}, lambda n: None, lambda g: [])


class BudgetTest(unittest.TestCase):
    LINE = ('{"type":"event_msg","payload":{"type":"token_count","rate_limits":{"limit_id":"codex","primary":{"used_percent":%s,'
            '"window_minutes":300,"resets_at":5000},"secondary":{"used_percent":%s,"window_minutes":10080,"resets_at":90000},"plan_type":"plus"}}}')

    def reading(self, d, five, week):
        p = Path(d) / "sessions" / "2026" / "10" / "12"
        p.mkdir(parents=True, exist_ok=True)
        (p / "rollout-a.jsonl").write_text('{"type":"other"}\n' + self.LINE % (five, week) + '\nnot json\n', encoding="utf-8")
        return R.budget(d)

    def test_reading_comes_from_the_newest_session_file(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(R.budget(d))
            rl = self.reading(d, 70.0, 11.0)
            self.assertEqual((rl["primary"]["used_percent"], rl["secondary"]["resets_at"]), (70.0, 90000))

    def test_full_window_holds_the_card_until_it_resets(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(R.hold(self.reading(d, 70.0, 11.0), 1000), "")
            full = self.reading(d, float(R.WINDOW_STOP), 11.0)
            self.assertIn("5-hour window 85% used, resets 1970-01-01 01:23Z", R.hold(full, 1000))
            self.assertEqual(R.hold(full, 5001), "")
            self.assertIn("weekly allowance", R.hold(self.reading(d, 10.0, float(R.WEEK_STOP)), 5001))
            self.assertEqual(R.hold(None, 1000), "")
            self.assertIn("5-hour window 0% used; week 85% used", R.budget_line(self.reading(d, 99.0, 85.0), 5001))

    def test_a_run_stopped_by_the_allowance_is_not_a_try(self):
        self.assertTrue(R.limit_hit("INCOMPLETE", [], "ERROR: You've hit your usage limit. Try again at 4:17 AM."))
        self.assertFalse(R.limit_hit("INCOMPLETE", ["a.md"], "usage limit"))
        self.assertFalse(R.limit_hit("INCOMPLETE", [], "tokens used\n9"))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "lab_runs"
            p.mkdir()
            (p / "runs.jsonl").write_text(json.dumps({"card": "x", "outcome": "LIMIT"}) + "\n", encoding="utf-8")
            self.assertEqual(R.attempts(d), {})


class StatusTest(unittest.TestCase):
    ROW = {"at": "2026-10-12T05:47:00Z", "card": "lab-a", "model": "gpt-6.1-sol", "effort": "medium", "tokens": 94135, "seconds": 452}

    def test_needs_look_names_each_thing_the_lab_cannot_fix(self):
        a, b, c = card("lab-a"), card("lab-b"), card("lab-c")
        self.assertEqual(R.needs_look([a, b, c], {}, [self.ROW | {"outcome": "DONE"}]), [])
        look = R.needs_look([a], {"lab-a": R.MAX_ATTEMPTS}, [self.ROW | {"outcome": "SHIP_FAILED", "note": "gate failed"}], unshipped=2, stopped="why")
        text = " | ".join(look)
        for want in ("switched off: why", "2 unshipped", "lab-a failed 2 times", "ended SHIP_FAILED (lab-a): gate failed", "queue is empty"):
            self.assertIn(want, text)
        self.assertIn("only 1 card(s) left", R.needs_look([a], {}, [])[0])
        self.assertEqual(R.needs_look([a], {}, [self.ROW | {"outcome": "LIMIT"}], held="window full"), [])
        self.assertEqual(R.needs_look([a, b, c], {}, [self.ROW | {"outcome": "SHIP_FAILED"}], closed={"lab-a"}), [])

    def test_status_is_plain_text_with_queue_deliveries_and_runs(self):
        done = card("lab-old", state="done", closed="2026-10-11T08:00:00Z", result="SOUND")
        t = R.status_text([card("lab-a"), card("lab-b"), card("lab-c")], [done], {}, [self.ROW | {"outcome": "DONE"}], None, 1791784000, "06:30Z IDLE")
        for want in ("Queue: 3 ready", "lab-a [audit, gpt-6-astra / high]", "2026-10-11 lab-old: SOUND",
                     "2026-10-12 05:47Z lab-a DONE (gpt-6.1-sol / medium, 94k tokens, 452s)", "NEEDS A LOOK: nothing", "Last check by the scheduler: 06:30Z IDLE"):
            self.assertIn(want, t)
        self.assertNotIn("{", t)
        away = R.status_text([], [done], {}, [], None, 1791784000, host_has_lab=False)
        self.assertIn("does not run the lab", away)
        self.assertNotIn("NEEDS A LOOK", away)


class LockTest(unittest.TestCase):
    def test_second_run_is_refused_until_the_lock_is_stale(self):
        with tempfile.TemporaryDirectory() as d:
            lock = Path(d) / "lab.lock"
            self.assertTrue(R.acquire(lock, now=1000))
            os.utime(lock, (1000, 1000))
            self.assertFalse(R.acquire(lock, now=1000 + R.LOCK_STALE_S - 1))
            self.assertTrue(R.acquire(lock, now=1000 + R.LOCK_STALE_S + 1))


class IndexTest(unittest.TestCase):
    def test_delivered_newest_first_with_report_link_then_queue(self):
        done1 = card("lab-old", state="done", closed="2026-10-11T08:00:00Z", result="SOUND")
        done2 = card("lab-new", kind="run", state="done", closed="2026-10-12T08:00:00Z", result="recall 3/7 | fire 0.4/day")
        text = R.index_text([done1, done2, card("lab-q"), card("son") | {"lane": "SONNET"}],
                            ["2026-10-11_lab-old.md", "2026-10-12_lab-new.md", "2026-10-12_other.md"])
        self.assertLess(text.index("lab-new"), text.index("lab-old"))
        self.assertIn("[2026-10-12_lab-new.md](reports/2026-10-12_lab-new.md)", text)
        self.assertIn("recall 3/7 / fire 0.4/day", text)
        self.assertIn("| ready | lab-q | audit |", text)
        self.assertNotIn("son", text.split("## Queued")[1])
        self.assertEqual(text, R.index_text([done2, card("lab-q"), done1], ["2026-10-12_lab-new.md", "2026-10-11_lab-old.md"]))


if __name__ == "__main__":
    unittest.main()
