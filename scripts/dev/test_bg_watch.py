"""bg_watch.py (bg-process-audit 2026-10-28): a background task with no completion notice past its cap is reported once per
wake; a finished (notice as message or queued_command attachment), stopped or young task is not; a tool result that merely
quotes a notice does not close a task; supervisor.py plan carries the lines."""
import json
import os
import sys
import tempfile
import time
import unittest
from unittest import mock
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

    def test_shell_older_than_30_min_is_listed_young_one_is_not(self):
        rows = [{"pid": 11, "start": NOW.timestamp() - 12 * 3600, "cmd": "bash -c cat > m.md <<'EOF'"},
                {"pid": 12, "start": NOW.timestamp() - 5 * 60, "cmd": "bash -c git log"}]
        got = bg_watch.live_shells(now=NOW.timestamp(), lister=lambda: rows)
        self.assertEqual([r["pid"] for r in got], [11])
        out = bg_watch.report_lines(Path(self.tmp.name), root=self.root, now=NOW.timestamp(), lister=lambda: rows)
        self.assertTrue(any(l.startswith("OLD-SHELL pid 11 720m > 30m") for l in out), out)
        self.assertFalse(any("pid 12" in l for l in out), out)
        self.assertEqual(bg_watch.live_shells(60, NOW.timestamp(), lambda: rows), [got[0]])

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


LOOP = 'F="x/sweep_NUC.txt"; until grep -q "^EXIT=" "$F"; do sleep 15; done; tail -40 "$F"'


class IdleSubagentTest(BgWatchTest):
    """bg-loop-block-1102: an agent that ends its turn waiting on its own shell writes nothing more, so its transcript looked
    dead after 3 h and a 4.8 h bare poll loop dropped out of the report at hour 3."""

    def sub(self, rows, idle_h):
        d = self.root / "proj" / "sess" / "subagents"
        d.mkdir(parents=True)
        p = d / "agent-a5d0.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8", newline="\n")
        t = NOW.timestamp() - idle_h * 3600
        os.utime(p, (t, t))
        parent = self.root / "proj" / "sess.jsonl"      # the supervisor session that spawned the agent keeps running
        parent.write_text("{}" + chr(10), encoding="utf-8", newline=chr(10))

    def test_loop_in_idle_subagent_transcript_is_still_reported(self):
        self.sub(start("t9", "Bash", {"command": LOOP, "run_in_background": True},
                       "Command running in background with ID: b1w6m0s2s. Output is being written to: x.output", 290), 4.8)
        got = [x for x in self.lines() if "b1w6m0s2s" in x]
        self.assertEqual(len(got), 1, got)
        self.assertIn("bare poll loop", got[0])
        self.assertIn("transcript idle 5h", got[0])

    def test_idle_subagent_of_a_dead_session_is_not_scanned(self):
        self.sub(start("t9", "Bash", {"command": LOOP, "run_in_background": True},
                       "Command running in background with ID: bdead0001. Output is being written to: x.output", 290), 4.8)
        old = NOW.timestamp() - 5 * 3600
        os.utime(self.root / "proj" / "sess.jsonl", (old, old))
        self.assertEqual([x for x in self.lines() if "bdead0001" in x], [])

    def test_idle_transcript_does_not_hold_a_task_forever(self):
        self.sub(start("t9", "Bash", {"command": LOOP, "run_in_background": True},
                       "Command running in background with ID: bold00001. Output is being written to: x.output", 30 * 60), 29)
        self.assertEqual([x for x in self.lines() if "bold00001" in x], [])

    def test_idle_transcript_with_a_notice_is_quiet(self):
        self.sub(start("t9", "Bash", {"command": LOOP, "run_in_background": True},
                       "Command running in background with ID: bdone0001. Output is being written to: x.output", 290)
                 + [notice("bdone0001", 280)], 4.6)
        self.assertEqual([x for x in self.lines() if "bdone0001" in x], [])

    def test_task_whose_agent_is_gone_is_a_ghost_not_a_stalled_task(self):
        """bg-watch-ghost-task-1104: the agent ended long ago (TaskStop: not found), its own transcript idle 7 h; the report
        repeated STALLED-BG every wake and the owner could never clear it. One GHOST-BG line, no TaskStop request."""
        tid = "a41afa0c7c66723ce"
        self.sub(start("t7", "Agent", {"description": "Builder ghost"},
                       f"Async agent launched. agentId: {tid} (ghost)", 428), 7)
        got = [x for x in self.lines() if tid in x]
        self.assertEqual(len(got), 1, got)
        self.assertTrue(got[0].startswith(f"GHOST-BG {tid} 428m > cap "), got[0])
        self.assertIn("transcript idle 7h", got[0])
        self.assertTrue(got[0].endswith("(agent gone; nothing to stop)"), got[0])
        self.assertFalse(any(x.startswith("STALLED-BG") for x in self.lines()), self.lines())
        self.assertNotIn(f"TaskStop {tid}", " ".join(self.lines()))
        rows = [r for r in bg_watch.stalled(self.root, NOW.timestamp()) if r["id"] == tid]
        self.assertEqual(len(rows), 1, rows)
        self.assertTrue(rows[0]["ghost"])

    def test_task_idle_under_six_hours_is_still_stalled(self):
        self.sub(start("t9", "Bash", {"command": LOOP, "run_in_background": True},
                       "Command running in background with ID: bslow001. Output is being written to: x.output", 290), 5.5)
        got = [x for x in self.lines() if "bslow001" in x]
        self.assertEqual(len(got), 1, got)
        self.assertTrue(got[0].startswith("STALLED-BG"), got[0])


class BareLoopGuardTest(unittest.TestCase):
    CASES = [
        (LOOP, True),
        ("while true; do sleep 5; done", True),
        ("ls && while ! test -f f; do sleep 2; done", True),
        ("bash -c 'until grep -q x f; do sleep 5; done'", True),
        ('git commit -m "fix: until grep x; do sleep 5; done is bare"', False),
        ('grep -n "until .*sleep" notes.md', False),
        ("git commit -m \"$(cat <<'EOF'"+chr(10)+"until x; do sleep 1; done"+chr(10)+"EOF"+chr(10)+")\"", False),
        ("python - <<'E'"+chr(10)+"while True:"+chr(10)+"    time.sleep(1)"+chr(10)+"E", False),
        ("for i in $(seq 1 120); do grep -q x f && break; sleep 10; done", False),
        ("until grep -q x f; do sleep 5; done  # timeout none", False),
        ("python scripts/dev/bg_watch.py until --file f --pattern x --timeout 60", False),
        ("echo it" + chr(92) + "'s; until false; do sleep 1; done", True),
        ("echo until; sleep 5", False),
        ("", False),
    ]

    def test_bare_poll_command(self):
        for cmd, want in self.CASES:
            self.assertEqual(bg_watch.bare_poll_command(cmd), want, cmd)

    def hook(self, tool, cmd):
        import preship
        out = preship.hook("hook-commit", json.dumps({"tool_name": tool, "tool_input": {"command": cmd}, "cwd": os.getcwd()}))
        return json.loads(out)["hookSpecificOutput"] if out else None

    def test_hook_denies_bash_loops_and_names_the_fix(self):
        for tool in ("Bash",):
            h = self.hook(tool, LOOP)
            self.assertEqual(h["permissionDecision"], "deny")
            self.assertIn("bg_watch.py until --file F --pattern RE --timeout S", h["permissionDecisionReason"])

    def test_hook_allows_text_and_bounded_loops(self):
        self.assertIsNone(self.hook("Bash", 'git status # until x; do sleep 1; done'))
        self.assertIsNone(self.hook("Bash", "python scripts/dev/bg_watch.py until --file f --pattern x --timeout 60"))
        self.assertIsNone(self.hook("Monitor", "for i in $(seq 1 30); do tail -1 f; sleep 2; done"))

    def test_hook_fails_open_when_the_check_breaks(self):
        import preship
        with mock.patch.object(bg_watch, "bare_poll_command", side_effect=RuntimeError("boom")):
            self.assertIsNone(self.hook("Bash", LOOP))
        self.assertEqual(preship.hook_bg_loop("sleep 1" * 3), "")

    def test_hook_leaves_monitor_alone_it_expires_by_itself(self):
        self.assertIsNone(self.hook("Monitor", LOOP))

    def test_hook_entry_is_registered_for_bash(self):
        cfg = json.loads((Path(__file__).resolve().parents[2] / ".claude" / "settings.json").read_text(encoding="utf-8"))
        ent = [e for e in cfg["hooks"]["PreToolUse"] if any("preship.py" in h["command"] for h in e["hooks"])]
        self.assertTrue(ent and "Bash" in ent[0]["matcher"].split("|"))


class OrphanLoopTest(unittest.TestCase):
    def test_live_bare_loop_older_than_cap_is_reported_without_a_transcript(self):
        now = time.time()
        shell = {"pid": 4242, "start": now - 4 * 3600, "cmd": "bash -c -l \"eval '" + LOOP.replace('"', '\\"') + "'\""}
        young = {**shell, "pid": 7, "start": now - 120}
        text = {"pid": 8, "start": now - 4 * 3600, "cmd": "bash -c 'git commit -m \"until x; do sleep 1; done\"'"}
        with tempfile.TemporaryDirectory() as d:
            got = bg_watch.report_lines(Path(d), root=Path(d) / "none", now=now, lister=lambda: [shell, young, text])
        orphans = [x for x in got if x.startswith("ORPHAN-LOOP")]
        self.assertEqual(len(orphans), 1, got)
        self.assertIn("pid 4242", orphans[0])

    def test_lister_failure_is_silent(self):
        def boom():
            raise OSError("no powershell")
        self.assertEqual(bg_watch.live_loops(lister=boom), [])


if __name__ == "__main__":
    unittest.main()
