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


def sh(cwd, *args):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.test", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode:   # D5: git reports some failures (hooks, identity) on stdout only
        raise RuntimeError("git %s: %s %s" % (" ".join(args), r.stderr.strip(), r.stdout.strip()))


class SignalTest(unittest.TestCase):
    """Two 'machines' (own clone dir + host name each) sharing one bare origin."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.origin = self.tmp / "origin.git"
        sh(self.tmp, "init", "-q", "--bare", str(self.origin))
        self.keep = {k: os.environ.get(k) for k in
                     ("MTS_SIGNALS_HOME", "MTS_SIGNALS_ORIGIN", "MTS_SIGNALS_HOST", "MTS_SIGNALS_SYNC", "MTS_ACCOUNT", "MTS_SIGNALS",
                      "MTS_LOGIN", "MTS_CLAUDE_JSON", "MTS_LOGINS_MD", "GIT_CEILING_DIRECTORIES")}
        os.environ["GIT_CEILING_DIRECTORIES"] = os.path.realpath(str(self.tmp.parent)).replace(os.sep, "/")   # D5: TEMP may sit inside a git repo (bridge children)
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


    def test_clean_cuts_secretlike_and_length(self):
        t = S.clean("token=abcd1234 key " + "A" * 40 + " " + "x" * 300)
        self.assertNotIn("abcd1234", t)
        self.assertNotIn("A" * 40, t)
        self.assertLessEqual(len(t), 200)


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



    def test_session_start_keeps_long_folder_name(self):
        # a 32+ char worktree folder name was cut to [cut] by clean() (read as a token): the note keeps its first 28 chars
        long_name = "mts-desktop-f7iu69n-every-station-save-unshipped-worktree-wo-2"
        text, kind = S.auto_send_text(self.payload("SessionStart", source="startup", cwd=str(self.tmp / long_name)))
        self.assertEqual(kind, "note")
        self.assertTrue(text.startswith("session started in mts-desktop-f7iu69n-every-st~"), text)
        self.assertNotIn("[cut]", text)



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

    def ship_with_output(self, out, cwd=None):
        p = self.bash("python scripts/dev/sync.py ship --release s1 2>&1 | tail -8", cwd=cwd)
        p["tool_response"] = {"stdout": out, "stderr": "", "exit_code": 0}
        return p

    def test_failed_ship_is_not_done(self):
        orig = S.last_result
        S.last_result = lambda cwd: ""
        try:
            ok = S.auto_send_text(self.ship_with_output("push rejected (someone shipped first), retry 1/3\nshipped 3 file(s) to origin/fast-track; released s1"))
            self.assertEqual(ok, ("ship s1", "done"))
            for out in ("push rejected (someone shipped first), retry 3/3\nship failed", "shipped 3 file(s) to origin/fast-track\nCI RED abc12345: tests https://x"):
                text, kind = S.auto_send_text(self.ship_with_output(out))
                self.assertEqual(kind, "note", out)
                self.assertTrue(text.startswith("ship failed"), text)
        finally:
            S.last_result = orig


    def test_repeat_ship_done_dropped(self):
        t0 = "20261105T100000Z"
        row = {"kind": "done", "from": "a", "text": "ship s1 Result: x", "t": t0}
        rec = lambda t: {"kind": "done", "from": "a", "text": "ship s1 Result: x", "t": t}
        self.assertTrue(S.is_repeat([row], rec("20261105T101400Z")))
        self.assertFalse(S.is_repeat([row], rec("20261105T101600Z")))
        note = dict(row, kind="note", text="n")
        self.assertFalse(S.is_repeat([note], dict(note, t="20261105T100800Z")))   # a note keeps the 5 minute window

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

    def test_ship_signal_uses_pushed_commit_result(self):
        # 2026-10-28: after a fast-track merge the newest non-merge commit was a trunk context-fold commit; its Result was signalled
        nl2 = chr(10) * 2
        c = ("-c", "user.name=t", "-c", "user.email=t@t")
        sh(self.tmp, "init", "-q", "repo")
        repo = self.tmp / "repo"
        sh(repo, *c, "commit", "-q", "--allow-empty", "-m", "base")
        sh(repo, "branch", "-M", "main")
        sh(repo, "checkout", "-q", "-b", "trunk")
        sh(repo, *c, "commit", "-q", "--allow-empty", "-m", "fold context into card x" + nl2 + "Result: fold noise")
        sh(repo, "checkout", "-q", "main")
        sh(repo, *c, "commit", "-q", "--allow-empty", "-m", "feat" + nl2 + "Result: 7 gaps closed")
        sh(repo, *c, "merge", "-q", "--no-ff", "-m", "Merge origin/fast-track", "trunk")
        self.assertEqual(S.last_result(str(repo)), "Result: 7 gaps closed")
        # the identical ship signal is sent once
        a = {"t": "20261028T100000Z", "from": "h", "kind": "done", "text": "ship x Result: 7 gaps closed"}
        self.assertTrue(S.is_repeat([a], dict(a, t="20261028T100100Z")))
        self.assertFalse(S.is_repeat([a], dict(a, t="20261028T100100Z", text="ship y Result: other")))
        self.assertFalse(S.is_repeat([dict(a, kind="broadcast")], dict(a, t="20261028T100100Z", kind="broadcast")))

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




    def ack_back(self, bid, state, back_min, note=""):
        """Ack as the current machine, stamped back_min minutes in the past."""
        orig = S.now
        S.now = lambda: orig() - timedelta(minutes=back_min)
        try:
            args = ["ack", bid, state] + (["--note", note] if note else [])
            self.assertEqual(S.main(args), 0)
        finally:
            S.now = orig


    def test_stale_broadcast_expires(self):
        at = S.now()
        bc = {"t": S.stamp(at - timedelta(hours=S.STALE_H + 5)), "kind": "broadcast", "prio": "high", "id": "b-old001", "to": "jis-gone", "from": "x/C"}
        live = {"t": S.stamp(at - timedelta(hours=1)), "kind": "note", "host": "jis-live"}
        fresh = {**bc, "id": "b-new001", "t": S.stamp(at - timedelta(hours=3)), "to": "jis-gone"}
        self.assertEqual(S.stale_open([bc, fresh, live], at), [("b-old001", "jis-gone")])   # only the old one, only the silent host
        closed = {"t": S.stamp(at), "kind": "ack", "id": "b-old001", "state": "expired", "host": "jis-gone"}
        self.assertEqual(S.stale_open([bc, fresh, live, closed], at), [])



    def test_pending_lists_none_and_expired_told_per_host(self):
        import contextlib
        import io
        at = S.now()

        def t(h):
            return S.stamp(at - timedelta(hours=h))
        b = {"t": t(7), "from": "jis-nuc/C", "to": "all", "kind": "broadcast", "prio": "high", "id": "b-aaaaaa", "cmd": "x", "text": "t"}
        told = {"t": t(10), "from": "jis-nb/B", "kind": "ack", "id": "b-aaaaaa", "state": "told", "host": "jis-nb", "note": "no admin"}
        rows = [b, told, {"t": t(1), "from": "jis-lenovo/C", "to": "all", "kind": "note", "text": "loop alive"}]
        self.assertIn("jis-lenovo", S.hosts_active(rows))
        len_ = S.pending(rows, "jis-lenovo", at)[0]
        self.assertEqual((len_["state"], len_["id"]), ("none", "b-aaaaaa"))
        self.assertAlmostEqual(len_["hours"], 7, delta=0.1)
        nb = S.pending(rows, "jis-nb", at)[0]
        self.assertEqual((nb["state"], nb["note"]), ("expired-told", "no admin"))
        fresh = [b, {**told, "t": t(1)}]
        self.assertEqual(S.pending(fresh, "jis-nb", at), [])               # told inside the TTL is not pending
        self.assertEqual(S.pending([b, {**told, "state": "done"}], "jis-nb", at), [])




    def test_stop_ignores_normal_broadcasts(self):
        self.machine("jis-nuc", "sharma")
        S.main(["broadcast", "plain"])
        self.machine("jis-nb", "pro")
        S.ensure()
        self.assertEqual(S.handle(self.payload("Stop", last_assistant_message="x")), "")



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

    def test_sender_id_uses_the_letter(self):
        self.machine("lenovo", "")
        os.environ.pop("MTS_ACCOUNT")
        self.assertEqual(S.who(), "lenovo/?")
        self.as_login("alice.fake@example.test")
        self.assertEqual(S.who(), "lenovo/A")
        os.environ["MTS_ACCOUNT"] = "sharma"
        self.assertEqual(S.who(), "lenovo/sharma")             # an explicit account label still wins

    def test_session_start_announces_login_and_tells_the_session(self):
        self.machine("jis-nb", "")
        self.as_login("carol1985@example.test")
        self.assertEqual(S.auto_send_text(self.payload("SessionStart", source="startup")), ("session started in %s login=C" % self.tmp.name, "note"))
        os.environ["MTS_SIGNALS_ORIGIN"] = ""                  # no clone: only the session's own LOGIN line, no network
        os.environ["MTS_SIGNALS_HOME"] = str(self.tmp / "none")
        os.environ["MTS_SIGNALS_SYNC"] = ""
        out = S.handle(self.payload("SessionStart", sid="x", source="compact"))
        self.assertEqual(out, "LOGIN: this session is login C on JIS-DESKTOP (the desktop) (from the app account)")
        self.assertNotIn("example.test", out)
        self.as_login("stranger@example.test")
        self.assertIn("LOGIN: unknown on JIS-DESKTOP", S.handle(self.payload("SessionStart", sid="y", source="compact")))

    def test_login_mismatch_uses_detected_letter_record_carries_login(self):
        self.machine("lenovo", "")
        os.environ.pop("MTS_ACCOUNT")
        os.environ["MTS_RELAY_HOME"] = str(self.tmp / "claudehome")
        self.as_login("alice.fake@example.test")
        letter, msg = S.resolve_login("C")
        self.assertEqual(letter, "")
        self.assertIn("passed C", msg)
        self.assertIn("detected A", msg)
        self.assertIn("home config", msg)
        self.assertEqual(S.resolve_login("a"), ("A", ""))
        self.assertEqual(S.resolve_login(""), ("A", ""))
        self.assertEqual(S.main(["budget", "--login", "C", "--five", "1", "--week", "2", "--reset", "2026-10-23T09:00Z"]), 2)
        os.environ["MTS_LOGIN"] = "A"
        letter, msg = S.resolve_login("B")
        self.assertEqual(letter, "")
        self.assertIn("env MTS_LOGIN", msg)
        del os.environ["MTS_LOGIN"]
        self.assertEqual(S.main(["budget", "--login", "A", "--five", "1", "--week", "2", "--reset", "2026-10-23T09:00Z"]), 0)
        rec = S.load(S.ensure())[-1]
        self.assertEqual(rec["text"], "BUDGET login=A 5h=1% week=2% reset=2026-10-23T09:00Z")
        self.assertEqual((rec["login"], rec["from"]), ("A", "lenovo/A"))
        self.assertNotIn("example.test", json.dumps(rec))      # the address never travels
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

    def test_clean_keeps_card_ids_and_cuts_keys(self):
        # operator 11-09: a 32-char card id arrived as [cut], the NUC got "gemini_queue.py run [cut]:low"
        cmd = "python scripts/dev/gemini_queue.py run tom-swing-trendline-extract-1109:low"
        self.assertEqual(S.clean(cmd), cmd)
        self.assertIn("tom-fabio-rebuild-from-beginner-videos-1109", S.clean("own tom-fabio-rebuild-from-beginner-videos-1109 now"))
        for secret in ("sk-ant-api03-" + "Ab9xQ" * 12, "3a904876-e92c-4569-8b37-acd0ef507736", "a1b2c3d4" * 5,
                       "ghp_" + "abcdefghij" * 4, "abcdefghijklmnopqrstuvwxyz-abcdefghijk-xy"):
            self.assertEqual(S.clean("k " + secret), "k [cut]", secret)

    def test_clean_cuts_email_addresses(self):
        self.assertEqual(S.clean("mail alice.fake@example.test now"), "mail [cut] now")


class AskTest(unittest.TestCase):
    """Mandatory reply (operator 2026-10-30): an ask has an id, a minimum wait and a deadline; the target must ack and answer;
    a same-text re-ask inside the wait is refused; past the deadline it escalates once to the target login's supervisor host."""
    setUp, tearDown, machine, payload = SignalTest.setUp, SignalTest.tearDown, SignalTest.machine, SignalTest.payload

    def ask(self, text="resend the budget file", to="jis-nb", *extra):
        self.machine("jis-nuc", "sharma")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = S.main(["ask", text, "--to", to, *extra])
        self.assertEqual(rc, 0, buf.getvalue())
        return [r for r in S.load(S.ensure()) if r.get("kind") == "ask"][-1]

    def test_ask_record_carries_id_wait_deadline(self):
        a = self.ask()
        self.assertTrue(a["id"].startswith("q-"))
        self.assertEqual((a["to"], a["wait"], a["due"], a["type"]), ("jis-nb", 15, 60, "ask"))
        self.assertLessEqual(len(a["text"]), 250)

    def test_send_kind_ask_takes_the_ask_path(self):
        self.machine("jis-nuc", "sharma")
        with contextlib.redirect_stdout(io.StringIO()):
            S.main(["send", "THINK c1: route", "--to", "all", "--kind", "ask"])
        a = [r for r in S.load(S.ensure()) if r.get("kind") == "ask"]
        self.assertEqual(len(a), 1)
        self.assertTrue(a[0].get("id", "").startswith("q-"))






    def test_login_letter_target_and_worker_env_skip(self):
        qid = self.ask("x", "C")["id"]
        self.machine("jis-nb", "pro")
        os.environ["MTS_LOGIN"] = "C"
        rows = S.load(S.ensure())
        self.assertIn(qid, S.ask_block(rows, "UserPromptSubmit"))
        os.environ["MTS_LOGIN"] = "A"
        self.assertEqual(S.ask_block(rows, "UserPromptSubmit"), "")
        os.environ["MTS_LOGIN"] = "C"
        os.environ["MTS_ROLE"] = "Builder"
        try:
            self.assertEqual(S.ask_block(rows, "UserPromptSubmit"), "")
        finally:
            os.environ.pop("MTS_ROLE", None)


class ExhaustReadTest(unittest.TestCase):
    """B199 (BUGS.md): a quota number names its source and read time; exhaust.py plan --read <UTC of the get_usage call>
    refuses a reading older than 10 min. Expected values are hand-counted minutes on a fixed clock, not read from exhaust.py."""

    NOW = datetime(2026, 10, 26, 8, 0, 0, tzinfo=timezone.utc)
    RESET = "2026-10-26T09:30Z"          # 90 min after NOW: phase plan (120 >= 90 > 60)
    BASE = ["plan", "--login", "C", "--week", "40", "--five", "10", "--reset", RESET, "--model", "opus=10", "--model", "sonnet=30"]

    def run_main(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = E.main(self.BASE + list(extra), now=self.NOW)
        return code, out.getvalue(), err.getvalue()

    def read_at(self, minutes_ago):
        return (self.NOW - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%MZ")

    def test_stale_read_rejected(self):
        code, out, err = self.run_main("--read", self.read_at(11))       # 07:49Z, 11 min old
        self.assertEqual(code, 2)
        self.assertNotIn("{", out)                                       # no phase JSON for a stale number
        self.assertIn("STALE quota reading", err)
        self.assertIn("read 2026-10-26T07:49Z", err)                     # names the read time
        self.assertIn("11 min old", err)                                 # names the age
        self.assertIn("get_usage", err)                                  # names the source and the cure

    def test_fresh_read_echoed_with_source(self):
        code, out, err = self.run_main("--read", self.read_at(9))        # 07:51Z, 9 min old
        self.assertEqual(code, 0)
        rec = json.loads(out)
        self.assertEqual(rec["read_utc"], "2026-10-26T07:51Z")
        self.assertEqual(rec["source"], "get_usage")
        self.assertEqual((rec["phase"], rec["minutes_to_reset"], rec["models"]), ("plan", 90, ["opus", "sonnet"]))

    def test_exactly_ten_minutes_still_accepted(self):
        code, out, err = self.run_main("--read", self.read_at(10))       # 07:50Z: the limit is "older than 10 min"
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["read_utc"], "2026-10-26T07:50Z")

    def test_no_read_is_unstated_not_refused(self):
        code, out, err = self.run_main()
        self.assertEqual(code, 0)
        rec = json.loads(out)
        self.assertEqual((rec["read_utc"], rec["source"]), ("unstated", "unstated"))

    def test_future_read_rejected(self):
        code, out, err = self.run_main("--read", (self.NOW + timedelta(minutes=3)).strftime("%Y-%m-%dT%H:%MZ"))   # 08:03Z
        self.assertEqual(code, 2)
        self.assertNotIn("{", out)
        self.assertIn("in the future", err)
        code, out, err = self.run_main("--read", (self.NOW + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%MZ"))   # 2 min of clock skew is allowed
        self.assertEqual(code, 0)



class TempInsideGitRepo(unittest.TestCase):
    """D5 repro: bridge children get TEMP inside a git repo and may have no global git identity. A signal round trip must still work."""


class WhoAgentTest(unittest.TestCase):
    def _who(self, agent):
        old = os.environ.pop("MTS_AGENT", None)
        try:
            if agent is not None:
                os.environ["MTS_AGENT"] = agent
            return S.who()
        finally:
            os.environ.pop("MTS_AGENT", None)
            if old is not None:
                os.environ["MTS_AGENT"] = old

    def test_who_appends_agent_name(self):
        base = self._who(None)
        self.assertEqual(base.count("/"), 1)
        self.assertEqual(self._who("gemini-nuc"), base + "/gemini-nuc")
        self.assertEqual(self._who("Gemini Laptop!/x"), base + "/geminilaptopx")   # sanitised: no extra slash
        self.assertEqual(self._who("  "), base)
        self.assertEqual(self._who("a" * 50), base + "/" + "a" * 24)

    def test_roll_login_still_second_segment(self):
        rec = {"t": S.stamp(), "from": "H1/B/gemini-nuc", "to": "*", "kind": "note", "text": "x"}
        out = " ".join(S.roll_lines([rec]))
        self.assertIn("H1", out.upper())


class HubLockTest(SignalTest):
    """Operator 2026-11-11 (audit finding 5): every session on a machine shares ONE signals clone, and its fetch / checkout -B / commit /
    push ran with no cross-process lock: index.lock and FETCH_HEAD collisions in hook_errors.log, acks lost. One lock file beside the
    clone serialises them; the fetch lands in a named ref instead of the shared FETCH_HEAD."""

    def test_the_hub_lock_is_exclusive_and_released(self):
        self.machine("jis-nb", "pro")
        h = S.home()
        with S.hub_lock(h) as first:
            self.assertTrue(first)
            t0 = time.time()
            with S.hub_lock(h, wait=0.4) as second:
                self.assertFalse(second)                # held: a second holder times out, never runs "inside" the first
            self.assertGreaterEqual(time.time() - t0, 0.3)
        with S.hub_lock(h, wait=0.4) as again:
            self.assertTrue(again)                      # released on exit, even when the first holder is gone

    def test_a_stale_lock_is_taken_over(self):
        self.machine("jis-nb", "pro")
        h = S.home()
        h.parent.mkdir(parents=True, exist_ok=True)
        lock = S.hub_lock_path(h)
        lock.write_text("dead\n")
        old = time.time() - 3600
        os.utime(lock, (old, old))                      # a crashed holder left it an hour ago
        with S.hub_lock(h, wait=0.4, stale=60) as got:
            self.assertTrue(got)

    def test_the_hub_never_reads_the_shared_fetch_head(self):
        self.machine("jis-nb", "pro")
        seen = []
        real = S.git

        def spy(cwd, *args, **kw):
            seen.append(args)
            return real(cwd, *args, **kw)
        S.git = spy
        try:
            self.assertTrue(S.send("hello"))
            S.ensure()
        finally:
            S.git = real
        self.assertEqual([a for a in seen if "FETCH_HEAD" in a], [], "a concurrent fetch rewrites FETCH_HEAD under us")



for _n in dir(SignalTest):      # reuse SignalTest's fixture only: its own tests already ran once
    if _n.startswith("test_") and _n not in HubLockTest.__dict__:
        setattr(HubLockTest, _n, None)


class SenderNoteCutTest(unittest.TestCase):
    def test_redaction_is_not_a_length_cut(self):
        n = S.sender_note("x " + "a1" * 20 + " y")
        self.assertNotIn("Cut to", n)
        self.assertIn("a token-like string was redacted", n)

    def test_long_text_still_says_cut(self):
        n = S.sender_note("w " * 150)
        self.assertIn("Cut to %d characters" % S.TEXT_MAX, n)
        self.assertNotIn("redacted", n)

    def test_plain_short_text_has_neither(self):
        n = S.sender_note("hello there")
        self.assertNotIn("Cut to", n)
        self.assertNotIn("redacted", n)


if __name__ == "__main__":
    unittest.main()
