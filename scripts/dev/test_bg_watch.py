"""bg_watch.py (bg-process-audit 2026-10-28): a background task with no completion notice past its cap is reported once per
wake; a finished (notice as message or queued_command attachment), stopped or young task is not; a tool result that merely
quotes a notice does not close a task; supervisor.py plan carries the lines."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bg_watch  # noqa: E402

NOW = datetime.now(timezone.utc).replace(microsecond=0)   # the scan skips transcripts not touched in 3 h of `now`


def iso(minutes_ago):
    return (NOW - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def start(tool_id, name, inp, result_text, minutes_ago):
    return [
        {"type": "assistant", "timestamp": iso(minutes_ago),
         "message": {"content": [{"type": "tool_use", "id": tool_id, "name": name, "input": inp}]}},
        {"type": "user", "timestamp": iso(minutes_ago),
         "message": {"content": [{"type": "tool_result", "tool_use_id": tool_id, "content": result_text}]}},
    ]


def notice(task_id, minutes_ago, as_attachment=False):
    txt = f"<task-notification>\n<task-id>{task_id}</task-id>\n<status>completed</status>\n</task-notification>"
    if as_attachment:
        return {"type": "attachment", "timestamp": iso(minutes_ago), "attachment": {"type": "queued_command", "prompt": txt}}
    return {"type": "user", "timestamp": iso(minutes_ago), "message": {"content": txt}}


SSH = "printf 'Set-Location F:/MTS/mts-codex-lab; python scripts/dev/codex_run.py tick\\n' | ssh -i ~/.ssh/nuc_gate -o BatchMode=yes h ps"


class BgWatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "projects"
        (self.root / "proj").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rows):
        p = self.root / "proj" / "abcdef12-session.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8", newline="\n")
        return p

    def lines(self, repo=None):
        return bg_watch.report_lines(repo or Path(self.tmp.name), root=self.root, now=NOW.timestamp())

    def test_hung_ssh_probe_is_reported_with_its_cap(self):
        self.write(start("t1", "Bash", {"command": SSH, "run_in_background": True},
                         "Command running in background with ID: bhung0001. Output is being written to: x.output", 99))
        out = self.lines()
        self.assertEqual(len(out), 1, out)
        self.assertTrue(out[0].startswith("STALLED-BG nuc bhung0001 99m > cap 5m"), out[0])
        self.assertIn("TaskStop bhung0001", out[0])

    def test_finished_stopped_young_and_quoted_tasks(self):
        rows = []
        rows += start("t1", "Agent", {"description": "Builder x", "prompt": "p"}, "Async agent launched. agentId: a11112222333344445 (x)", 90)
        rows.append(notice("a11112222333344445", 30, as_attachment=True))           # attachment notice closes it
        rows += start("t2", "Bash", {"command": "python scripts/dev/sync.py ship", "run_in_background": True},
                      "Command running in background with ID: bship0002.", 80)
        rows.append(notice("bship0002", 60))                                           # message notice closes it
        rows += start("t3", "Bash", {"command": "until grep -q x f; do sleep 5; done", "run_in_background": True},
                      "Command running in background with ID: bpoll0003.", 70)
        rows.append({"type": "assistant", "timestamp": iso(10), "message": {"content": [
            {"type": "tool_use", "id": "t4", "name": "TaskStop", "input": {"task_id": "bpoll0003"}}]}})   # stopped
        rows += start("t5", "Bash", {"command": "python scripts/dev/run_all_tests.py --quick", "run_in_background": True},
                      "Command running in background with ID: btest0005.", 5)                           # young
        rows += start("t6", "Bash", {"command": "until grep -q y f; do sleep 5; done", "run_in_background": True},
                      "Command running in background with ID: bpoll0006.", 40)
        rows += start("t7", "Bash", {"command": "grep task-id transcript.jsonl"}, "<task-notification><task-id>bpoll0006</task-id>", 3)
        self.write(rows)
        out = [l for l in self.lines() if l.startswith("STALLED-BG")]
        self.assertEqual(len(out), 1, out)
        self.assertIn("poll-loop bpoll0006 40m > cap 10m", out[0])
        self.assertIn("bg_watch.py until", out[0])           # the loop had no deadline: the line names the bounded replacement

    def test_dead_session_is_not_scanned(self):
        p = self.write(start("t1", "Bash", {"command": SSH}, "Command running in background with ID: bold00001.", 600))
        old = NOW.timestamp() - 5 * 3600
        os.utime(p, (old, old))
        self.assertEqual(self.lines(), [])

    def test_until_verb_matches_times_out_and_unbounded_loops_are_told_apart(self):
        f = Path(self.tmp.name) / "x.out" if hasattr(self, "tmp") else None
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "x.out"
            clock = [0.0]
            ticks = lambda s: clock.__setitem__(0, clock[0] + s)
            self.assertEqual(bg_watch.wait_until(f, "DONE", 30, 5, sleep=ticks, now_fn=lambda: clock[0]), 124)   # missing file, then deadline
            self.assertEqual(clock[0], 30)
            f.write_text("run" + chr(10) + "DONE" + chr(10), encoding="utf-8")
            self.assertEqual(bg_watch.wait_until(f, "DONE", 30, 5, sleep=ticks, now_fn=lambda: clock[0]), 0)
            self.assertEqual(bg_watch.main(["until", "--file", str(f), "--pattern", "NOPE", "--timeout", "0", "--interval", "1"]), 124)
        self.assertEqual(bg_watch.main(["until", "--file", "f"]), 2)
        self.assertTrue(bg_watch.unbounded_loop("until grep -q y f; do sleep 5; done"))
        self.assertFalse(bg_watch.unbounded_loop("timeout 600 bash -c 'until grep -q y f; do sleep 5; done'"))
        self.assertFalse(bg_watch.unbounded_loop("python scripts/dev/bg_watch.py until --file f --pattern y"))
        self.assertEqual(bg_watch.CAPS["poll-loop"], 10)

    def test_bare_until_grep_loop_is_flagged_and_names_taskstop(self):
        bare = "until grep -q passed out.txt; do :; done"          # no sleep: old code did not even call it a poll loop
        self.assertTrue(bg_watch.unbounded_loop(bare))
        self.assertEqual(bg_watch.kind_of("Bash", bare), ("poll-loop", 10))
        self.assertTrue(bg_watch.unbounded_loop("while ! grep -q passed out.txt; do tail -f out.txt; done"))
        self.assertFalse(bg_watch.unbounded_loop("python scripts/dev/bg_watch.py until --file f --pattern passed --timeout 60"))
        self.write(start("t1", "Bash", {"command": bare, "run_in_background": True},
                         "Command running in background with ID: bbare0001.", 161))
        out = self.lines()
        self.assertEqual(len(out), 1, out)
        self.assertIn("run TaskStop bbare0001 now", out[0])
        self.assertIn("only allowed poll", out[0])
        self.write(start("t2", "Bash", {"command": "python scripts/dev/bg_watch.py until --file f --pattern y --timeout 60",
                                        "run_in_background": True}, "Command running in background with ID: bok00002.", 5))
        self.assertEqual(self.lines(), [])                          # allowed call, young: nothing

    def test_kind_caps(self):
        k = bg_watch.kind_of
        self.assertEqual(k("Bash", "python scripts/dev/supervisor.py wait --timeout 50m --login C"), ("watcher", 55))
        self.assertEqual(k("Bash", "python scripts/dev/nuc_lab.py status"), ("nuc", 5))
        self.assertEqual(k("Agent", "Agent Builder"), ("worker", 45))
        self.assertEqual(k("Bash", "python scripts/dev/sync.py ship --release x"), ("ship", 20))
        self.assertEqual(k("Bash", "git log --oneline -5"), ("probe", 2))

    def test_raw_important_card_is_surfaced(self):
        repo = Path(self.tmp.name) / "repo"
        tasks = repo / "MyTradingSys" / "system" / "tasks"
        tasks.mkdir(parents=True)
        for cid, state, weight, hours in (("old-raw", "raw", "IMPORTANT", 30), ("new-raw", "raw", "IMPORTANT", 2),
                                          ("routine-raw", "raw", "ROUTINE", 40), ("old-done", "done", "CRUCIAL", 90)):
            (tasks / f"{cid}.json").write_text(json.dumps({"id": cid, "state": state, "weight": weight,
                                                           "created": iso(hours * 60)}), encoding="utf-8")
        out = self.lines(repo)
        self.assertEqual(out, ["RAW-AGED 1 IMPORTANT/CRUCIAL card(s) still raw > 12h (old-raw 30h): refine or drop one this wake"])

    def test_supervisor_plan_carries_the_lines(self):
        import supervisor as S
        from unittest import mock
        with mock.patch.object(bg_watch, "report_lines", return_value=["STALLED-BG nuc bX 9m > cap 5m"]) as rl:
            try:
                lines, _ = S.plan(Path(self.tmp.name), "C", {"five": 10, "week": 20, "five_reset": "2026-10-28T09:00Z",
                                                             "week_reset": "2026-10-30T16:00Z"},
                                  send=False, no_fetch=True, host="JIS-NB", home=Path(self.tmp.name), now=NOW)
            except Exception as e:      # other reads need the real repo; the call itself must have happened
                lines = []
                self.assertTrue(rl.called, f"plan failed before bg_watch: {e!r}")
        self.assertTrue(rl.called)
        if lines:
            self.assertIn("STALLED-BG nuc bX 9m > cap 5m", lines)


class WatcherWakeTest(unittest.TestCase):
    """The watcher (supervisor.py wait) wakes when a task crosses its cap: a hung task never ends, so it never woke anyone."""

    def test_new_stalled_task_is_a_transition_old_one_is_not(self):
        import supervisor as S
        base = {"stalled": ["nuc bA 9m > cap 5m"]}
        self.assertIsNone(S._detect_transition(base, {"stalled": ["nuc bA 30m > cap 5m"]}))
        r = S._detect_transition(base, {"stalled": ["nuc bA 30m > cap 5m", "ship bB 21m > cap 20m"]})
        self.assertEqual(r, "TRANSITION STALLED-BG ship bB 21m > cap 20m: run plan, TaskStop it if it is yours")
        self.assertIsNone(S._detect_transition({"stalled": None}, {"stalled": None}))


if __name__ == "__main__":
    unittest.main()
