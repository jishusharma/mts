"""Slow signal tests (>5 s each; split from test_mts_signal.py, card gate-signals-offgate-1113). Off the ship gate via gate_tiers.tsv (tier slow);
they run once on Linux CI in the offgate-tier job. The fast smoke per signals function stays in test_mts_signal.py on the gate."""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exhaust as E
import mts_signal as S
import test_mts_signal as base
from test_mts_signal import sh

class SlowSignalTest(unittest.TestCase):
    setUp, tearDown, machine, payload = base.SignalTest.setUp, base.SignalTest.tearDown, base.SignalTest.machine, base.SignalTest.payload
    bash, ship_with_output, high, ups, ack_back = base.SignalTest.bash, base.SignalTest.ship_with_output, base.SignalTest.high, base.SignalTest.ups, base.SignalTest.ack_back

    def test_direct_to_host_only(self):
        self.machine("jis-nuc", "sharma")
        S.send("only for nb", to="jis-nb")
        self.machine("jis-nb", "pro")
        self.assertEqual(len(S.unseen_for(S.load(S.ensure()), "0")), 1)
        self.machine("other", "x")
        self.assertEqual(S.unseen_for(S.load(S.ensure()), "0"), [])

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

    def test_ensure_recovers_from_zeroed_hub_head(self):
        """bug-nuc-signal-hub-not-a-git-repo: a power loss on JIS-NUC left the hub clone's .git/HEAD all NUL bytes. ensure()
        saw the .git dir, skipped re-init, and every later git call (send()'s `git add -A`) crashed with RuntimeError
        'not a git repository' instead of self-healing."""
        self.machine("jis-nuc", "sharma")
        S.ensure()
        h = S.home()
        (h / ".git" / "HEAD").write_bytes(b"\x00" * 41)
        h2 = S.ensure()
        self.assertEqual(h2, h)
        self.assertTrue(S.send("after corruption", kind="note"))
        self.machine("jis-nb", "pro")
        rows = S.load(S.ensure())
        self.assertIn("after corruption", [r["text"] for r in rows])

    def test_hook_ship_done_twice_gives_one_row(self):
        self.machine("jis-nb", "pro")
        orig = S.last_result
        S.last_result = lambda cwd: ""
        try:
            p = self.ship_with_output("shipped 2 file(s) to origin/fast-track; released s1")
            S.handle(dict(p, session_id="s9"))
            S.handle(dict(p, session_id="s9"))
        finally:
            S.last_result = orig
        self.machine("jis-nuc", "sharma")
        self.assertEqual([r["text"] for r in S.load(S.ensure()) if r["kind"] == "done"], ["ship s1"])

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
        self.assertEqual(S.main(["ack", bid, "told", "--note", "blocked"]), 0)
        self.assertNotIn("ACTION REQUIRED", self.ups())
        start = S.handle(self.payload("SessionStart", sid="new", source="startup"))
        self.assertIn("[MTS reminder", start)
        self.assertIn(bid, start)
        self.assertNotIn("ACTION REQUIRED", start)
        self.assertEqual(S.main(["ack", bid, "done"]), 0)
        quiet = S.handle(self.payload("SessionStart", sid="new2", source="startup"))
        self.assertNotIn("reminder", quiet)                                     # done is silent; only the LOGIN line remains
        self.assertNotIn("ACTION", quiet)

    def test_told_expires_after_ttl_and_is_loud_with_the_blocker_note(self):
        bid = self.high()
        self.machine("jis-lab", "x")
        self.ack_back(bid, "told", S.TOLD_TTL_H * 60 + 30, "needs admin shell")
        loud = self.ups()
        self.assertIn("ACTION REQUIRED", loud)                                # every prompt, not only SessionStart
        self.assertIn("h AGO, NOT DONE", loud)
        self.assertIn("needs admin shell", loud)
        self.assertIn("ACTION REQUIRED", S.handle(self.payload("UserPromptSubmit", sid="s1")))
        self.assertEqual(json.loads(S.handle(self.payload("Stop", last_assistant_message="all done")))["decision"], "block")
        self.assertEqual(S.main(["ack", bid, "done"]), 0)
        self.assertNotIn("ACTION REQUIRED", self.ups())
        self.assertEqual(S.handle(self.payload("Stop", last_assistant_message="all done")), "")
        bc = {"t": S.stamp(S.now() - timedelta(hours=5)), "kind": "broadcast", "prio": "high", "id": "b-fresh1", "to": "all", "from": "x/C"}
        told = {"t": S.stamp(S.now() - timedelta(minutes=60)), "kind": "ack", "id": "b-fresh1", "state": "told", "host": "jis-lab"}
        self.assertFalse(S.needs_action([bc, told], bc))                       # told inside the TTL stays quiet
        self.assertTrue(S.needs_action([bc, {**told, "t": S.stamp(S.now() - timedelta(minutes=S.TOLD_TTL_H * 60 + 5))}], bc))

    def test_expire_command_closes_stale_pairs_and_prints_before_after(self):
        import contextlib
        import io
        self.machine("jis-gone", "pro")
        orig = S.now
        S.now = lambda: orig() - timedelta(hours=S.STALE_H + 30)
        try:
            S.send("last words", kind="note")                      # seen long ago, silent since: it cannot ack
        finally:
            S.now = orig
        bid = self.high(back_min=(S.STALE_H + 5) * 60)            # a HIGH broadcast to everyone, older than STALE_H, nobody acked
        self.machine("jis-nuc", "sharma")
        S.send("a note", kind="note")                              # jis-nuc is active; every other target host stays silent
        rows = S.load(S.ensure())
        silent = {h for b, h in S.stale_open(rows) if b == bid}
        self.assertIn("jis-gone", silent)
        self.assertNotIn("jis-nuc", silent)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(S.main(["expire"]), 0)
        out = buf.getvalue()
        self.assertIn("before: %d stale" % len([1 for b, h in S.stale_open(rows)]), out)
        self.assertIn("after: 0 stale", out)
        self.assertEqual(S.stale_open(S.load(S.ensure())), [])
        for h in silent:
            self.assertEqual(S.ack_state(S.load(S.ensure()), bid, h), "expired")

    def test_told_on_a_cmd_broadcast_needs_a_note_a_plain_one_does_not(self):
        bid = self.high()
        self.machine("jis-nb", "pro")
        self.assertEqual(S.main(["ack", bid, "told"]), 2)
        self.assertEqual(S.main(["ack", bid, "told", "--note", "   "]), 2)
        self.assertEqual(S.ack_state(S.load(S.ensure()), bid, "jis-nb"), "none")
        self.assertEqual(S.main(["ack", bid, "told", "--note", "no admin rights"]), 0)
        self.machine("jis-nuc", "sharma")                                     # a broadcast without --cmd keeps the old rule
        S.main(["broadcast", "fyi", "--prio", "high"])
        nid = [r for r in S.load(S.ensure()) if r.get("prio") == "high"][-1]["id"]
        self.machine("jis-nb", "pro")
        self.assertEqual(S.main(["ack", nid, "told"]), 0)
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(S.main(["pending", "--host", "jis-nb", "--json"]), 0)
        self.assertEqual(json.loads(buf.getvalue()), [])                  # both told just now: nothing pending

    def test_acks_table_and_sender_status(self):
        import contextlib
        import io
        bid = self.high()
        self.machine("jis-nb", "pro")
        S.send("hello", kind="note")                         # nb is now a host seen
        self.assertEqual(S.main(["ack", bid, "done", "--note", "ok"]), 0)
        self.machine("jis-lab", "x")
        S.send("hello", kind="note")
        self.assertEqual(S.main(["ack", bid, "told", "--note", "blocked"]), 0)
        self.machine("jis-nuc", "sharma")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(S.main(["acks", bid]), 0)
            self.assertEqual(S.main(["acks"]), 0)
        table = buf.getvalue()
        self.assertRegex(table, r"jis-desktop\s+done\s+ok")   # acks list the canonical name (hosts.py); the ack was written as jis-nb
        self.assertRegex(table, r"jis-lab\s+told")
        self.assertRegex(table, r"jis-nuc\s+none")
        self.assertEqual(table.count(bid + " HIGH"), 2)      # with id and the all-open listing
        status = S.sender_status(S.load(S.ensure()))
        self.assertIn("1/3 hosts done", status)
        self.assertIn("jis-lab=told", status)
        self.assertIn(bid, S.handle(self.payload("UserPromptSubmit", sid="sender")))
        self.machine("jis-nb", "pro")
        self.assertNotIn("status]", self.ups())              # other machines get the action block, not the sender status

    def test_acks_view_counts_ack_from_host_login_alias(self):
        import contextlib
        import io
        bid = self.high()
        self.machine("jis-nb", "pro")
        S.send("hello", kind="note")
        S.send("ack %s done ok" % bid, kind="ack", extra={"id": bid, "state": "done", "host": "jis-nb/C", "login": "C", "note": "ok"})
        self.machine("jis-nuc", "sharma")
        rows = S.load(S.ensure())
        self.assertEqual(S.ack_state(rows, bid, "jis-nb"), "done")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            S.main(["acks", bid])
        self.assertRegex(buf.getvalue(), r"jis-desktop\s+done")
        self.assertNotIn("jis-desktop/c", buf.getvalue())

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
        self.assertEqual(S.main(["ack", bid, "told", "--note", "blocked"]), 0)
        self.assertEqual(stop(last_assistant_message="all done"), "")

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


class SlowAskTest(unittest.TestCase):
    setUp, tearDown, machine, payload, ask = base.AskTest.setUp, base.AskTest.tearDown, base.AskTest.machine, base.AskTest.payload, base.AskTest.ask

    def test_target_sees_ask_every_prompt_until_told_and_stop_blocks_once(self):
        qid = self.ask()["id"]
        self.machine("jis-nb", "pro")
        out = S.handle(self.payload("UserPromptSubmit"))
        self.assertIn("[MTS ASK", out)
        self.assertIn(qid, out)
        stop = lambda **kw: S.handle(self.payload("Stop", **kw))
        self.assertEqual(json.loads(stop(last_assistant_message="all done"))["decision"], "block")
        self.assertEqual(stop(last_assistant_message="all done", stop_hook_active=True), "")
        self.assertEqual(stop(last_assistant_message="acked %s" % qid), "")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(S.main(["ack", qid, "told"]), 0)
        self.assertEqual(stop(last_assistant_message="all done"), "")
        (S.state_dir() / "last_fetch").unlink()
        self.assertNotIn(qid, S.handle(self.payload("UserPromptSubmit")))       # told and not overdue: quiet
        self.machine("other", "x")
        self.assertEqual(S.ask_block(S.load(S.ensure()), "UserPromptSubmit"), "")   # not addressed to this host

    def test_ask_is_loud_for_one_session_per_machine(self):
        qid = self.ask()["id"]
        self.machine("jis-nb", "pro")
        first = S.handle(self.payload("UserPromptSubmit", sid="s1"))
        self.assertIn(qid, first)
        self.assertNotIn(qid, S.handle(self.payload("UserPromptSubmit", sid="s2")))     # second session: not the owner
        self.assertIn(qid, S.handle(self.payload("UserPromptSubmit", sid="s1")))        # the owner hears it every prompt
        for f in S.state_dir().glob("ask-owner-*"):                                     # unreadable owner state: fail closed, print it
            f.unlink()
            f.mkdir()
        self.assertIn(qid, S.handle(self.payload("UserPromptSubmit", sid="s2")))

    def test_reask_inside_min_wait_refused_after_it_allowed(self):
        a = self.ask()
        self.assertEqual(S.new_ask("Resend  the budget file", to="jis-nb")[0], a["id"])     # same text, collapsed
        rows = S.load(S.ensure())
        self.assertEqual(len([r for r in rows if r.get("kind") == "ask"]), 1)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(S.main(["ask", "resend the budget file", "--to", "jis-nb"]), 3)
        later = S._t(a) + timedelta(minutes=16)
        qid2, msg = S.new_ask("resend the budget file", to="jis-nb", at=later)
        self.assertNotEqual(qid2, a["id"], msg)

    def test_answer_closes_ask_and_reaches_asker(self):
        qid = self.ask()["id"]
        self.machine("jis-nb", "pro")
        S.ensure()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(S.main(["ack", qid, "done"]), 2)                    # an answer needs --note
            self.assertEqual(S.main(["ack", qid, "done", "--note", "resent as budget_v2"]), 0)
        self.machine("jis-nuc", "sharma")
        rows = S.load(S.ensure())
        self.assertEqual(S.asks_open(rows), [])
        self.assertIn("resent as budget_v2", " ".join(r.get("text", "") for r in S.unseen_for(rows, "0")))

    def test_overdue_escalates_once_to_target_login_supervisor_and_lists_overdue(self):
        self.machine("jis-nuc", "sharma")
        S.send("BUDGET login=C 5h=10% week=50% reset=x sup=JIS-LAPTOP mode=NORMAL", kind="note")
        a = self.ask("which reset is right", "C")
        rows = S.load(S.ensure())
        at = S._t(a) + timedelta(minutes=61)
        self.assertEqual(S.escalate(rows, at=S._t(a) + timedelta(minutes=59), send_fn=lambda t, x: None), [])
        sent = []
        self.assertEqual(S.escalate(rows, at=at, send_fn=lambda t, x: sent.append((t, x))), [(a["id"], "jis-laptop")])
        self.assertLessEqual(len(sent[0][0]), 250)
        S.escalate(rows, at=at)                                                   # real send
        rows = S.load(S.ensure())
        self.assertEqual(S.escalate(rows, at=at, send_fn=lambda t, x: sent.append(x)), [])      # once only
        r = S.ask_rows(rows, at=at)[0]
        self.assertTrue(r["overdue"])
        self.assertEqual((r["age_min"], r["esc"]), (61, "jis-laptop"))
        self.machine("jis-laptop", "lenovo")                                     # the supervisor host now sees it
        self.assertIn("OVERDUE", S.ask_block(S.load(S.ensure()), "UserPromptSubmit", at=at))


class SlowTempInsideGitRepo(unittest.TestCase):
    def test_round_trip_with_temp_inside_a_repo_and_no_global_git_config(self):
        if os.environ.get("MTS_D5_INNER"):
            self.skipTest("inner run")
        scratch = tempfile.mkdtemp()
        try:
            subprocess.run(["git", "-C", scratch, "init", "-q"], check=True, capture_output=True)
            tmp = os.path.join(scratch, "tmp")
            os.mkdir(tmp)
            env = dict(os.environ, TEMP=tmp, TMP=tmp, TMPDIR=tmp, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", MTS_D5_INNER="1")
            for k in ("GIT_CEILING_DIRECTORIES", "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL"):
                env.pop(k, None)
            r = subprocess.run([sys.executable, "-m", "unittest", "test_mts_signal.SignalTest.test_send_then_other_machine_reads_not_own"],
                               cwd=str(Path(__file__).resolve().parent), env=env, capture_output=True, text=True, timeout=300)
            self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-1500:])
        finally:
            shutil.rmtree(scratch, ignore_errors=True)


class SlowHubLockTest(unittest.TestCase):
    setUp, tearDown, machine, payload = base.SignalTest.setUp, base.SignalTest.tearDown, base.SignalTest.machine, base.SignalTest.payload

    def test_six_sessions_sending_at_once_all_arrive(self):
        import threading
        self.machine("jis-nb", "pro")
        S.ensure()
        errors, results = [], []

        def go(i):
            try:
                results.append(S.send("note %d" % i, kind="claim"))
            except Exception as e:      # noqa: BLE001
                errors.append(repr(e))
        ts = [threading.Thread(target=go, args=(i,)) for i in range(6)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(errors, [])
        self.assertEqual(results, [True] * 6)
        clone = self.tmp / "verify"
        sh(self.tmp, "clone", "-q", "-b", S.BRANCH, str(self.origin), str(clone))
        self.assertEqual(sorted(r["text"] for r in S.load(clone)), ["note %d" % i for i in range(6)])


if __name__ == "__main__":
    unittest.main()
