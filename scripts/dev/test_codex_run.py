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
