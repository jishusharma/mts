import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
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
                     ("MTS_SIGNALS_HOME", "MTS_SIGNALS_ORIGIN", "MTS_SIGNALS_HOST", "MTS_SIGNALS_SYNC", "MTS_ACCOUNT", "MTS_SIGNALS")}
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
        self.assertTrue((self.tmp / "claudehome" / "mts-budget.json").is_file())
        os.environ.pop("MTS_RELAY_HOME")

    def test_odd_slug_is_dropped(self):
        orig = S.last_result
        S.last_result = lambda cwd: ""
        try:
            self.assertEqual(S.auto_send_text(self.bash("sync.py start $(whoami)"))[0], "start")
        finally:
            S.last_result = orig


if __name__ == "__main__":
    unittest.main()
