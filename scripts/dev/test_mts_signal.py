import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mts_signal as S


def sh(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class SignalTest(unittest.TestCase):
    """Two 'machines' (own clone dir + host name each) sharing one bare origin."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.origin = self.tmp / "origin.git"
        sh(self.tmp, "init", "-q", "--bare", str(self.origin))
        self.keep = {k: os.environ.get(k) for k in
                     ("MTS_SIGNALS_HOME", "MTS_SIGNALS_ORIGIN", "MTS_SIGNALS_HOST", "MTS_SIGNALS_SYNC", "MTS_ACCOUNT", "MTS_SIGNALS",
                      "MTS_LOGIN", "MTS_CLAUDE_JSON", "MTS_LOGINS_MD")}
        os.environ.pop("MTS_LOGIN", None)       # no real login detection in tests: a fake claude.json and table when a test needs one
        os.environ["MTS_CLAUDE_JSON"] = str(self.tmp / "none.json")
        self.md = self.tmp / "ACCOUNTS.md"
        self.md.write_text("| A: alice.fake@example.test | x |\n| B: bob.fake | y |\n| C: carol1985@example.test (Max) | z |\n", encoding="utf-8")
        os.environ["MTS_LOGINS_MD"] = str(self.md)
        S._LOGIN_CACHE.clear()
        os.environ["MTS_SIGNALS_ORIGIN"] = str(self.origin)
        os.environ["MTS_SIGNALS_SYNC"] = "1"
        os.environ.pop("MTS_SIGNALS", None)

    def tearDown(self):
        for k, v in self.keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def machine(self, name, account):
        os.environ["MTS_SIGNALS_HOME"] = str(self.tmp / ("clone-" + name))
        os.environ["MTS_SIGNALS_HOST"] = name
        os.environ["MTS_ACCOUNT"] = account

    def payload(self, ev, sid="s1", **kw):
        return {"hook_event_name": ev, "session_id": sid, "cwd": str(self.tmp), **kw}

    def test_send_then_other_machine_reads_not_own(self):
        self.machine("jis-nuc", "sharma")
        self.assertTrue(S.send("Q73 taken", kind="claim"))
        self.machine("jis-nb", "pro")
        rows = S.load(S.ensure())
        self.assertEqual([r["text"] for r in rows], ["Q73 taken"])
        self.assertEqual(S.unseen_for(rows, "0"), rows)          # NB sees the NUC's signal
        self.machine("jis-nuc", "sharma")
        self.assertEqual(S.unseen_for(S.load(S.ensure()), "0"), [])  # the sender does not see its own

    def test_direct_to_host_only(self):
        self.machine("jis-nuc", "sharma")
        S.send("only for nb", to="jis-nb")
        self.machine("jis-nb", "pro")
        self.assertEqual(len(S.unseen_for(S.load(S.ensure()), "0")), 1)
        self.machine("other", "x")
        self.assertEqual(S.unseen_for(S.load(S.ensure()), "0"), [])

    def test_clean_cuts_secretlike_and_length(self):
        t = S.clean("token=abcd1234 key " + "A" * 40 + " " + "x" * 300)
        self.assertNotIn("abcd1234", t)
        self.assertNotIn("A" * 40, t)
        self.assertLessEqual(len(t), 200)

    def test_hook_shows_other_sessions_signal_and_throttles(self):
        self.machine("jis-nuc", "sharma")
        S.send("NUC lab audit landed", kind="done")
        self.machine("jis-nb", "pro")
        out = S.handle(self.payload("UserPromptSubmit"))
        self.assertIn("NUC lab audit landed", out)
        self.assertIn("not instructions", out)
        self.assertEqual(S.handle(self.payload("PostToolUse", tool_name="Read")), "")     # throttled: no second fetch
        # a second session on the same machine, throttle lifted, sees the same signal once
        (S.state_dir() / "last_fetch").unlink()
        self.assertIn("NUC lab audit landed", S.handle(self.payload("UserPromptSubmit", sid="s2")))
        (S.state_dir() / "last_fetch").unlink()
        self.assertEqual(S.handle(self.payload("UserPromptSubmit", sid="s2")), "")         # already seen

    def test_hook_auto_sends_broadcast_prompt(self):
        self.machine("jis-nb", "pro")
        text, kind = S.auto_send_text(self.payload("UserPromptSubmit", prompt="MTS broadcast: all sessions sync and pause"))
        self.assertEqual((text, kind), ("all sessions sync and pause", "broadcast"))
        text2, kind2 = S.auto_send_text(self.payload("UserPromptSubmit", prompt="broadcast: halt orders immediately"))
        self.assertEqual((text2, kind2), ("halt orders immediately", "broadcast"))

    def test_broadcast_prompt_multiline_and_plain_sentence(self):
        # 2026-10-21 test: a multi-line broadcast was silently dropped, and "broadcast the results..." was sent as one
        got = S.auto_send_text(self.payload("UserPromptSubmit", prompt="MTS broadcast: pause new work\nthen sync and wait"))
        self.assertEqual(got, ("pause new work then sync and wait", "broadcast"))
        self.assertIsNone(S.auto_send_text(self.payload("UserPromptSubmit", prompt="broadcast the results to the team")))
        self.assertIsNone(S.auto_send_text(self.payload("UserPromptSubmit", prompt="broadcasting is slow, why?")))
        self.assertEqual(S.auto_send_text(self.payload("UserPromptSubmit", prompt="MTS Broadcast stop all")), ("stop all", "broadcast"))

    def test_broadcast_reaches_sibling_sessions_on_sender_machine(self):
        # every session on one machine shares one sender id, so a broadcast never reached the sender's own siblings
        self.machine("jis-nb", "?")
        S.handle(self.payload("UserPromptSubmit", sid="sender", prompt="MTS broadcast: siblings too"))
        (S.state_dir() / "last_fetch").unlink()
        self.assertIn("siblings too", S.handle(self.payload("UserPromptSubmit", sid="sibling")))
        (S.state_dir() / "last_fetch").unlink()
        self.assertNotIn("siblings too", S.handle(self.payload("UserPromptSubmit", sid="sender")))   # not echoed to the sender
        S.send("ship x", kind="done")                                                             # plain notes stay off-machine
        (S.state_dir() / "last_fetch").unlink()
        self.assertEqual(S.handle(self.payload("UserPromptSubmit", sid="sibling")), "")

    def test_second_session_sees_broadcast_without_waiting_for_gate(self):
        # the per-machine 5-minute fetch gate made a second session wait up to 5 more minutes for what the clone already held
        self.machine("jis-nuc", "sharma")
        S.main(["broadcast", "heads up"])
        self.machine("jis-nb", "pro")
        self.assertIn("heads up", S.handle(self.payload("UserPromptSubmit", sid="s1")))
        self.assertIn("heads up", S.handle(self.payload("UserPromptSubmit", sid="s2")))   # gate closed, clone has it
        self.assertEqual(S.handle(self.payload("UserPromptSubmit", sid="s2")), "")

    def test_post_tool_use_only_sends_never_receives(self):
        # review 2026-10-22: a fetch/read after every tool call cost time and context for nothing
        self.machine("jis-nuc", "sharma")
        S.main(["broadcast", "heads up"])
        self.machine("jis-nb", "pro")
        self.assertEqual(S.handle(self.payload("PostToolUse", sid="s3", tool_name="Read")), "")
        self.assertFalse((S.state_dir() / "last_fetch").exists())
        self.assertIn("heads up", S.handle(self.payload("UserPromptSubmit", sid="s3")))

    def test_broadcast_sender_told_it_is_pull_only_and_cut(self):
        # operator 2026-10-22: a broadcast "did not work", nothing flashed; the sender was never told it only lands on a
        # session's next turn, nor that the 200-character cap dropped the steps
        self.machine("jis-nb", "?")
        out = S.handle(self.payload("UserPromptSubmit", sid="sender", prompt="MTS broadcast: " + "step " * 60))
        self.assertIn("[MTS BROADCAST SENT]", out)
        self.assertIn("next turn", out)
        self.assertIn("send_message", out)
        self.assertIn("lost", out)
        short = S.handle(self.payload("UserPromptSubmit", sid="sender2", prompt="MTS broadcast: pause"))
        self.assertIn("[MTS BROADCAST SENT]", short)
        self.assertNotIn("lost", short)
        self.assertNotIn("[MTS BROADCAST SENT]", S.handle(self.payload("UserPromptSubmit", sid="s3", prompt="hello")))

    def test_broadcast_banner_rendered_prominently(self):
        self.machine("jis-nuc", "sharma")
        self.assertEqual(S.main(["broadcast", "urgent notice for all models"]), 0)
        self.machine("jis-nb", "pro")
        out = S.handle(self.payload("UserPromptSubmit"))
        self.assertIn("[MTS BROADCAST from operator/session across hosts]", out)
        self.assertIn("urgent notice for all models", out)

    def test_hook_auto_sends_claim_and_ship(self):
        self.machine("jis-nb", "pro")
        S.handle(self.payload("PostToolUse", tool_name="Bash",
                              tool_input={"command": 'python scripts/dev/sync.py claim "Q73 move files"'}))
        S.handle(self.payload("PostToolUse", sid="s9", tool_name="Bash", tool_input={"command": "python scripts/dev/sync.py ship"}))
        S.handle(self.payload("PostToolUse", sid="s9", tool_name="Bash", tool_input={"command": "ls"}))      # not a signal
        self.machine("jis-nuc", "sharma")
        texts = [(r["kind"], r["text"]) for r in S.load(S.ensure())]
        self.assertEqual(texts, [("claim", "claim Q73 move files"), ("done", "ship")])

    def test_two_signals_in_one_second_load_in_send_order(self):
        # 2026-10-16: names were second-stamp + random tail, so same-second signals sorted by chance (ubuntu CI red)
        from datetime import datetime, timezone
        self.machine("jis-nb", "pro")
        base = datetime.now(timezone.utc).replace(microsecond=0)
        clock = [base]
        orig_now, orig_rand = S.now, S.random.randrange
        S.now = lambda: clock[0]
        vals = iter([0xFFFF, 0x0000])                       # the later signal gets the smaller random tail
        S.random.randrange = lambda n: next(vals)
        try:
            clock[0] = base.replace(microsecond=100)
            S.send("first", kind="claim")
            clock[0] = base.replace(microsecond=200)
            S.send("second", kind="done")
        finally:
            S.now, S.random.randrange = orig_now, orig_rand
        self.assertEqual([r["text"] for r in S.load(S.ensure())], ["first", "second"])

    def test_session_start_signal_and_subagent_and_off_are_silent(self):
        self.machine("jis-nb", "pro")
        S.handle(self.payload("SessionStart", source="startup"))
        S.handle(self.payload("SessionStart", source="compact"))                           # a compact is not a start
        S.handle(self.payload("SessionStart", sid="sub", source="startup", agent_id="a1"))   # subagent
        os.environ["MTS_SIGNALS"] = "off"
        S.handle(self.payload("SessionStart", sid="off", source="startup"))
        os.environ.pop("MTS_SIGNALS")
        self.machine("jis-nuc", "sharma")
        rows = S.load(S.ensure())
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["text"].startswith("session started"))

    def test_prune_drops_old_files(self):
        self.machine("jis-nb", "pro")
        h = S.ensure()
        (h / "20200101T000000Z-x-0000.json").write_text("{}", newline="\n")
        self.assertEqual(S.prune(h), 1)

    def test_no_origin_is_silent(self):
        os.environ["MTS_SIGNALS_ORIGIN"] = ""
        os.environ["MTS_SIGNALS_HOME"] = str(self.tmp / "none")
        cwd = self.tmp / "norepo"
        cwd.mkdir()
        self.assertFalse(S.send("x", cwd=cwd))
        self.assertEqual(S.handle(self.payload("UserPromptSubmit", cwd=str(cwd))), "")

    def bash(self, cmd, cwd=None):
        return {"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": cwd or str(self.tmp)}

    def test_hook_text_drops_shell_tail(self):
        cases = [
            ("python scripts/dev/sync.py ship 2>&1 | tail -6", ("ship", "done")),
            ("python scripts/dev/sync.py start my-slug 2>&1 | grep -E \"WORKTREE|branch\"", ("start my-slug", "note")),
            ("python scripts/dev/sync.py claim fix-x \"long task text\" 2>&1 | tail -3", ("claim fix-x", "claim")),
            ("python scripts/dev/sync.py ship --release nuc-slug 2>&1 | tail -8; echo hi", ("ship nuc-slug", "done")),
            ("python scripts/dev/sync.py release s1 2>&1 | tail -3", ("release s1", "done")),
            ("cd x && python scripts/dev/sync.py ship && sync.py release gpt-fix", ("ship", "done")),
        ]
        orig = S.last_result
        S.last_result = lambda cwd: ""
        try:
            for cmd, want in cases:
                self.assertEqual(S.auto_send_text(self.bash(cmd)), want, cmd)
        finally:
            S.last_result = orig

    def test_ship_signal_carries_result_line(self):
        sh(self.tmp, "init", "-q", "repo")
        repo = self.tmp / "repo"
        sh(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "feat" + chr(10) * 2 + "Result: 5 layers live")
        text, kind = S.auto_send_text(self.bash("python scripts/dev/sync.py ship 2>&1 | tail -6", cwd=str(repo)))
        self.assertEqual((text, kind), ("ship Result: 5 layers live", "done"))
        self.assertNotIn("tail", text)

    def test_ship_signal_reads_the_tree_that_shipped_not_the_session_cwd(self):
        # 2026-10-23: DESKTOP-F7IU69N sessions sit in the primary checkout (newest commit: an old claim) and ship from a worktree;
        # every ship signalled the primary's stale text instead of the worktree's Result
        nl2 = chr(10) * 2
        for name, msg in (("main", "E on PC" + nl2 + "Result: E on PC works on: old task"), ("wt", "feat" + nl2 + "Result: 8 cards sized")):
            sh(self.tmp, "init", "-q", name)
            sh(self.tmp / name, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", msg)
        main, wt = str(self.tmp / "main"), (self.tmp / "wt").as_posix()
        want = ("ship x Result: 8 cards sized", "done")
        for cmd in ('cd "%s" && python scripts/dev/sync.py ship --release x' % wt,
                    "python %s/scripts/dev/sync.py ship --release x 2>&1 | tail -4" % wt,
                    "cd %s; python scripts/dev/sync.py ship --release x" % wt):
            self.assertEqual(S.auto_send_text(self.bash(cmd, cwd=main)), want, cmd)
        self.assertEqual(S.auto_send_text(self.bash("python scripts/dev/sync.py ship --release x", cwd=main))[0],
                         "ship x Result: E on PC works on: old task")      # no tree named: the session cwd, as before
        self.assertEqual(S.auto_send_text(self.bash("cd /no/such/dir && python scripts/dev/sync.py ship", cwd=main))[0],
                         "ship Result: E on PC works on: old task")

    def test_ship_signal_skips_claim_release_and_merge_commits(self):
        # 2026-10-23: DESKTOP-F7IU69N ships all signalled the stale claim text "works on: gemini-yt-pipeliner ..."
        sh(self.tmp, "init", "-q", "repo")
        repo = self.tmp / "repo"
        nl2 = chr(10) * 2
        for msg in ("feat" + nl2 + "Result: lease env set", "claim old-task" + nl2 + "Result: E on PC works on: old task",
                    "release tc2" + nl2 + "Result: claim tc2 closed", "Merge remote-tracking branch 'origin/fast-track' into x"):
            sh(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", msg)
        self.assertEqual(S.last_result(str(repo)), "Result: lease env set")
        sh(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "docs only")
        self.assertEqual(S.last_result(str(repo)), "")      # the newest work commit states no Result: say nothing, not an old one

    def test_budget_command_sends_line_traffic_parses_and_writes_file(self):
        self.machine("nb", "sharma")
        os.environ["MTS_RELAY_HOME"] = str(self.tmp / "claudehome")
        self.assertEqual(S.main(["budget", "--login", "b", "--five", "12.4", "--week", "40", "--reset", "2026-10-22T19:59Z"]), 0)
        self.assertEqual(S.main(["budget", "--login", "X", "--five", "1", "--week", "1", "--reset", "2026-10-22T19:59Z"]), 2)
        self.assertEqual(S.main(["budget", "--login", "A", "--five", "1", "--week", "1", "--reset", "soon"]), 2)
        h = S.ensure()
        texts = [r["text"] for r in S.load(h)]
        self.assertEqual(texts, ["BUDGET login=B 5h=12% week=40% reset=2026-10-22T19:59Z"])
        import traffic
        self.assertTrue(traffic.BUDGET_RE.search(texts[0]))
        import json
        rec = json.loads((self.tmp / "claudehome" / "mts-budget.json").read_text(encoding="utf-8"))
        self.assertEqual((rec["weekly_all_pct"], rec["five_hour_pct"], rec["weekly_resets_at"]), (40.0, 12.4, "2026-10-22T19:59Z"))
        import budget
        self.assertEqual(sorted(rec), ["five_hour_pct", "utc", "weekly_all_pct", "weekly_resets_at"])
        self.assertIn(budget.state()[0], ("NORMAL", "SPEND", "THROTTLE"))
        os.environ.pop("MTS_RELAY_HOME")

    def test_odd_slug_is_dropped(self):
        orig = S.last_result
        S.last_result = lambda cwd: ""
        try:
            self.assertEqual(S.auto_send_text(self.bash("sync.py start $(whoami)"))[0], "start")
        finally:
            S.last_result = orig

    # ---- HIGH broadcasts (operator 2026-10-22): act on every machine, per-host ack, Stop reminder -----------------------

    def high(self, text="every machine needs the exclusions", cmd="powershell scripts/operator/x.ps1", back_min=0):
        """Broadcast a HIGH message from jis-nuc, optionally stamped back_min minutes in the past; returns its id."""
        self.machine("jis-nuc", "sharma")
        orig = S.now
        S.now = lambda: orig() - timedelta(minutes=back_min)
        try:
            self.assertEqual(S.main(["broadcast", text, "--prio", "high", "--cmd", cmd]), 0)
        finally:
            S.now = orig
        return [r for r in S.load(S.ensure()) if r.get("prio") == "high"][-1]["id"]

    def ups(self, sid="s1"):
        (S.state_dir() / "last_fetch").unlink(missing_ok=True)
        return S.handle(self.payload("UserPromptSubmit", sid=sid))

    def test_high_broadcast_repeats_every_turn_until_this_host_acks_done(self):
        bid = self.high()
        self.machine("jis-nb", "pro")
        first = self.ups()
        self.assertIn("[MTS ACTION REQUIRED %s prio HIGH %s %s from jis-nuc/sharma at" % (chr(183), chr(183), bid), first)
        self.assertIn('"ACTION FOR THIS MACHINE (jis-nb): powershell scripts/operator/x.ps1"', first)
        self.assertIn("ack %s told" % bid, first)
        self.assertIn("ack %s done" % bid, first)
        for _ in range(3):                                   # every turn, also inside the fetch gate, any session
            self.assertIn(bid, S.handle(self.payload("UserPromptSubmit", sid="s1")))
        self.assertIn(bid, S.handle(self.payload("UserPromptSubmit", sid="s2")))
        self.assertEqual(S.main(["ack", bid, "done", "--note", "ran as admin"]), 0)
        self.assertNotIn("ACTION REQUIRED", self.ups())
        self.assertNotIn("ACTION REQUIRED", S.handle(self.payload("SessionStart", sid="s9", source="startup")))
        self.machine("jis-lab", "x")                         # another host is still nagged
        self.assertIn(bid, self.ups(sid="s5"))

    def test_session_started_later_sees_two_hour_old_high_broadcast(self):
        bid = self.high(back_min=120)
        self.machine("jis-nb", "pro")
        out = S.handle(self.payload("SessionStart", sid="late", source="startup"))
        self.assertIn("ACTION REQUIRED", out)
        self.assertIn(bid, out)
        self.assertIn(bid, self.ups(sid="late"))             # the 30-minute look-back no longer hides it

    def test_told_is_a_reminder_once_per_session_done_is_silent(self):
        bid = self.high()
        self.machine("jis-nb", "pro")
        self.assertEqual(S.main(["ack", bid, "told"]), 0)
        self.assertNotIn("ACTION REQUIRED", self.ups())
        start = S.handle(self.payload("SessionStart", sid="new", source="startup"))
        self.assertIn("[MTS reminder", start)
        self.assertIn(bid, start)
        self.assertNotIn("ACTION REQUIRED", start)
        self.assertEqual(S.main(["ack", bid, "done"]), 0)
        quiet = S.handle(self.payload("SessionStart", sid="new2", source="startup"))
        self.assertNotIn("reminder", quiet)                                     # done is silent; only the LOGIN line remains
        self.assertNotIn("ACTION", quiet)

    def test_acks_table_and_sender_status(self):
        import contextlib
        import io
        bid = self.high()
        self.machine("jis-nb", "pro")
        S.send("hello", kind="note")                         # nb is now a host seen
        self.assertEqual(S.main(["ack", bid, "done", "--note", "ok"]), 0)
        self.machine("jis-lab", "x")
        S.send("hello", kind="note")
        self.assertEqual(S.main(["ack", bid, "told"]), 0)
        self.machine("jis-nuc", "sharma")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(S.main(["acks", bid]), 0)
            self.assertEqual(S.main(["acks"]), 0)
        table = buf.getvalue()
        self.assertRegex(table, r"jis-nb\s+done\s+ok")
        self.assertRegex(table, r"jis-lab\s+told")
        self.assertRegex(table, r"jis-nuc\s+none")
        self.assertEqual(table.count(bid + " HIGH"), 2)      # with id and the all-open listing
        status = S.sender_status(S.load(S.ensure()))
        self.assertIn("1/3 hosts done", status)
        self.assertIn("jis-lab=told", status)
        self.assertIn(bid, S.handle(self.payload("UserPromptSubmit", sid="sender")))
        self.machine("jis-nb", "pro")
        self.assertNotIn("status]", self.ups())              # other machines get the action block, not the sender status

    def test_stop_blocks_once_unless_reply_has_the_line_or_stop_hook_active(self):
        import json
        bid = self.high()
        self.machine("jis-nb", "pro")
        S.ensure()
        stop = lambda **kw: S.handle(self.payload("Stop", **kw))
        out = json.loads(stop(last_assistant_message="all done"))
        self.assertEqual(out["decision"], "block")
        self.assertIn(bid, out["reason"])
        self.assertIn("ACTION FOR THIS MACHINE (jis-nb)", out["reason"])
        self.assertEqual(stop(last_assistant_message="all done", stop_hook_active=True), "")          # never twice in a turn
        self.assertEqual(stop(last_assistant_message="ACTION FOR THIS MACHINE (jis-nb): x\ndone"), "")
        self.assertEqual(stop(last_assistant_message="see %s" % bid), "")
        tp = self.tmp / "t.jsonl"                            # without the payload field the transcript is read
        tp.write_text("\n".join(json.dumps(e) for e in [
            {"type": "user", "message": {"content": "hi"}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "ACTION FOR THIS MACHINE (jis-nb): x"}]}},
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}]), encoding="utf-8", newline="\n")
        self.assertEqual(stop(transcript_path=str(tp)), "")
        self.assertEqual(json.loads(stop(transcript_path=str(self.tmp / "none.jsonl")))["decision"], "block")
        self.assertEqual(S.main(["ack", bid, "told"]), 0)
        self.assertEqual(stop(last_assistant_message="all done"), "")

    def test_stop_ignores_normal_broadcasts(self):
        self.machine("jis-nuc", "sharma")
        S.main(["broadcast", "plain"])
        self.machine("jis-nb", "pro")
        S.ensure()
        self.assertEqual(S.handle(self.payload("Stop", last_assistant_message="x")), "")

    def test_future_stamped_record_does_not_hide_a_newer_signal(self):
        self.machine("jis-bad", "x")                         # wrong clock: one day ahead
        orig = S.now
        S.now = lambda: orig() + timedelta(days=1)
        try:
            S.send("from the future", kind="done")
        finally:
            S.now = orig
        self.machine("jis-nb", "pro")
        self.assertNotIn("from the future", self.ups())      # ignored, not shown
        self.machine("jis-nuc", "sharma")
        S.send("real news", kind="done")
        self.machine("jis-nb", "pro")
        self.assertIn("real news", self.ups())               # the marker did not jump a day ahead

    def test_normal_broadcast_is_unchanged(self):
        self.machine("jis-nuc", "sharma")
        self.assertEqual(S.main(["broadcast", "plain heads up"]), 0)
        rec = S.load(S.ensure())[-1]
        self.assertNotIn("id", rec)
        self.assertNotIn("prio", rec)
        self.machine("jis-nb", "pro")
        out = self.ups()
        self.assertIn("[MTS BROADCAST from operator/session across hosts]", out)
        self.assertIn("plain heads up", out)
        self.assertNotIn("ACTION REQUIRED", out)
        self.assertEqual(self.ups(), "")                     # shown once, as before

    def as_login(self, email):
        (self.tmp / "claude.json").write_text(json.dumps({"oauthAccount": {"emailAddress": email}, "other": "x"}), encoding="utf-8")
        os.environ["MTS_CLAUDE_JSON"] = str(self.tmp / "claude.json")
        S._LOGIN_CACHE.clear()

    def test_login_detected_from_app_account_and_env_overrides(self):
        self.assertEqual(S.login(), "")
        self.as_login("alice.fake@example.test")
        self.assertEqual(S.login(), "A")
        self.as_login("bob.fake@example.test")                  # key = local part
        self.assertEqual(S.login(), "B")
        self.as_login("carol1985@example.test")                 # key = full address
        self.assertEqual(S.login(), "C")
        self.as_login("stranger@example.test")
        self.assertEqual(S.login(), "")
        os.environ["MTS_LOGIN"] = "b"
        self.assertEqual(S.login(), "B")

    def test_record_carries_login_and_sender_id_uses_the_letter(self):
        self.machine("lenovo", "")
        os.environ.pop("MTS_ACCOUNT")
        self.assertEqual(S.who(), "lenovo/?")
        self.as_login("alice.fake@example.test")
        self.assertEqual(S.who(), "lenovo/A")
        S.send("hello")
        rec = S.load(S.ensure())[-1]
        self.assertEqual((rec["login"], rec["from"]), ("A", "lenovo/A"))
        self.assertNotIn("example.test", json.dumps(rec))      # the address never travels
        os.environ["MTS_ACCOUNT"] = "sharma"
        self.assertEqual(S.who(), "lenovo/sharma")             # an explicit account label still wins

    def test_session_start_announces_login_and_tells_the_session(self):
        self.machine("jis-nb", "")
        os.environ.pop("MTS_ACCOUNT")
        self.machine("jis-nuc", "")
        os.environ.pop("MTS_ACCOUNT")
        self.as_login("alice.fake@example.test")
        S.send("BUDGET login=A 5h=10% week=40% reset=2026-10-27T19:59Z sup=NUC mode=SPEND")
        self.machine("jis-nb", "")
        os.environ.pop("MTS_ACCOUNT")
        self.as_login("carol1985@example.test")
        out = S.handle(self.payload("SessionStart", source="startup"))
        self.assertIn("LOGIN: this session is login C on JIS-NB (from the app account)", out)
        self.assertIn("login A ", out)                          # who lines follow
        self.assertNotIn("example.test", out)
        texts = [r["text"] for r in S.load(S.ensure())]
        self.assertIn("session started in %s login=C" % self.tmp.name, texts)

    def test_login_mismatch_uses_detected_letter_and_login_is_optional(self):
        self.machine("lenovo", "")
        os.environ["MTS_RELAY_HOME"] = str(self.tmp / "claudehome")
        self.as_login("alice.fake@example.test")
        self.assertEqual(S.resolve_login("C"), ("A", "LOGIN MISMATCH: you passed C, this app is logged in as A; using A"))
        self.assertEqual(S.resolve_login("a"), ("A", ""))
        self.assertEqual(S.resolve_login(""), ("A", ""))
        self.assertEqual(S.main(["budget", "--login", "C", "--five", "1", "--week", "2", "--reset", "2026-10-23T09:00Z"]), 0)
        self.assertEqual(S.main(["budget", "--five", "1", "--week", "2", "--reset", "2026-10-23T09:00Z"]), 0)
        texts = [r["text"] for r in S.load(S.ensure())]
        self.assertEqual(texts, ["BUDGET login=A 5h=1% week=2% reset=2026-10-23T09:00Z"])   # second one is a repeat: dropped
        os.environ.pop("MTS_RELAY_HOME")

    def test_who_lines_stale_supervisor_note_and_conflict(self):
        at = S.now()
        def row(h, lg, text, ago_min, **kw):
            return dict({"t": S.stamp(at - timedelta(minutes=ago_min)), "from": "%s/%s" % (h, lg or "?"), "to": "all", "kind": "note",
                         "text": text, **({"login": lg} if lg else {})}, **kw)
        rows = [row("lenovo", "A", "BUDGET login=C 5h=3% week=50% reset=2026-10-23T09:00Z", 10),
                row("jis-nb", "C", "BUDGET login=C 5h=9% week=20% reset=2026-10-27T19:59Z sup=JIS-NB mode=SPEND run=1", 20),
                row("jis-nb", "C", "ROLE LOADED: Builder", 5),
                row("old-pc", "B", "BUDGET login=B 5h=1% week=2% reset=2026-10-25T00:00Z", 8 * 60)]
        out = S.roll_lines(rows, 24, at)
        text = " ".join(out)
        self.assertEqual(len([x for x in out if x.startswith("CONFLICT")]), 1)
        self.assertIn("CONFLICT login C: reset 2026-10-23T09:00 on lenovo vs 2026-10-27T19:59 on jis-nb", out[0])
        nb = [x for x in out if "jis-nb" in x and x.startswith("login")][0]
        self.assertIn("sup=JIS-NB mode=SPEND", nb)
        self.assertIn("ROLE LOADED: Builder", nb)
        self.assertIn("5h=9% week=20%", nb)
        self.assertNotIn("STALE", nb)
        self.assertIn("MISLABELLED login=C", [x for x in out if "lenovo" in x and x.startswith("login A")][0])
        self.assertIn("STALE", [x for x in out if "old-pc" in x][0])      # 8 h old reading
        self.assertEqual(len(S.roll_lines(rows, 1, at)), 3)                # old-pc is outside a 1 h window, CONFLICT line stays
        self.assertNotIn("example.test", text)

    def test_clean_cuts_email_addresses(self):
        self.assertEqual(S.clean("mail alice.fake@example.test now"), "mail [cut] now")

    def test_who_command_prints_own_login_and_rows(self):
        self.machine("jis-nb", "")
        os.environ.pop("MTS_ACCOUNT")
        self.as_login("bob.fake@example.test")
        S.send("start foo")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(S.main(["who", "--hours", "2"]), 0)
        o = buf.getvalue()
        self.assertIn("LOGIN: this session is login B on JIS-NB", o)
        self.assertIn("login B jis-nb seen", o)
        self.assertIn("start foo", o)


if __name__ == "__main__":
    unittest.main()
