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
        cmd = R.command("codex.exe", card(kind="audit"), "F:/wt", "workspace-write", "C:/repo/.git")
        self.assertEqual(cmd[:4], ["codex.exe", "exec", "-m", "gpt-6-astra"])
        self.assertIn('model_reasoning_effort="high"', cmd)
        self.assertEqual(cmd[cmd.index("-s") + 1], "workspace-write")
        self.assertEqual(cmd[cmd.index("--add-dir") + 1], "C:/repo/.git")
        self.assertIn("sandbox_workspace_write.network_access=true", cmd)
        self.assertEqual(cmd[-1], "-")
        full = R.command("codex.exe", card(kind="run"), "F:/wt", "danger-full-access", "C:/repo/.git")
        self.assertNotIn("--add-dir", full)
        self.assertIn("gpt-6-luna", full)

    def test_prompt_carries_claim_report_trailer_and_the_brief(self):
        p = R.prompt(card(), "F:/wt", "F:/home/packs/lab-a.md", datetime(2026, 10, 12, 9, 5, tzinfo=timezone.utc))
        for want in ('sync.py claim "lab-a"', "layer_lab/reports/2026-10-12_lab-a.md", "MTS-2026-10-12-0905Z-COD-LAB-lab-a",
                     "do NOT mark the card done", "TASK lab-a [CODEX", "codex_run.py index"):
            self.assertIn(want, p)

    def test_gitdir_is_absolute_for_a_work_tree_and_for_the_main_clone(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(R.abs_gitdir("F:/wt", str(Path(d) / ".git") + chr(10)), Path(d) / ".git")
            self.assertEqual(R.abs_gitdir(d, ".git" + chr(10)), (Path(d) / ".git").resolve())

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
