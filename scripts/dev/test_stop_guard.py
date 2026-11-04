import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stop_guard


def sh(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class StopGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        origin = self.tmp / "origin.git"
        sh(self.tmp, "init", "-q", "--bare", str(origin))
        sh(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
        self.a = self.tmp / "a"
        sh(self.tmp, "clone", "-q", str(origin), str(self.a))
        sh(self.a, "config", "user.email", "t@t")
        sh(self.a, "config", "user.name", "t")
        (self.a / "README.md").write_text("x\n", newline="\n")
        sh(self.a, "add", "README.md")
        sh(self.a, "commit", "-q", "-m", "init")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.a, "checkout", "-q", "-b", "claude/work")   # a session tree is never on the trunk branch
        os.environ.pop("MTS_STOP_GUARD", None)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_hook(self, **extra):
        return stop_guard.hook(json.dumps({"cwd": str(self.a), **extra}))

    def test_clean_tree_may_stop(self):
        self.assertEqual(self.run_hook(), "")

    def test_uncommitted_file_blocks_once(self):
        (self.a / "wip.py").write_text("x\n", newline="\n")
        out = json.loads(self.run_hook())
        self.assertEqual(out["decision"], "block")
        self.assertIn("sync.py ship", out["reason"])
        self.assertEqual(self.run_hook(stop_hook_active=True), "")   # never a loop

    def test_unshipped_commit_blocks_until_shipped(self):
        (self.a / "w.py").write_text("w\n", newline="\n")
        sh(self.a, "add", "w.py")
        sh(self.a, "commit", "-q", "-m", "w")
        self.assertIn("not shipped", self.run_hook())
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.a, "fetch", "-q", "origin")
        self.assertEqual(self.run_hook(), "")

    def test_commits_with_a_tree_identical_to_origin_do_not_block_but_a_differing_file_does(self):
        """B17: a commit plus its revert (or merge commits trunk already holds) leave HEAD's tree equal to origin's: nothing to ship."""
        (self.a / "w.py").write_text("w\n", newline="\n")
        sh(self.a, "add", "w.py")
        sh(self.a, "commit", "-q", "-m", "w")
        sh(self.a, "revert", "--no-edit", "HEAD")
        sh(self.a, "commit", "-q", "--allow-empty", "-m", "dup")
        self.assertEqual(self.run_hook(), "")
        (self.a / "w.py").write_text("real\n", newline="\n")
        sh(self.a, "add", "w.py")
        sh(self.a, "commit", "-q", "-m", "real")
        self.assertIn("not shipped", self.run_hook())

    def test_identical_content_still_does_not_block_after_the_trunk_moves_on(self):
        """B17 follow-up: HEAD equals an OLD trunk commit while origin/fast-track has moved past it; compare with the merge-base, not the tip."""
        (self.a / "w.py").write_text("w\n", newline="\n")
        sh(self.a, "add", "w.py")
        sh(self.a, "commit", "-q", "-m", "w")
        sh(self.a, "revert", "--no-edit", "HEAD")
        other = self.tmp / "b"
        sh(self.tmp, "clone", "-q", str(self.tmp / "origin.git"), str(other))
        sh(other, "config", "user.email", "t@t")
        sh(other, "config", "user.name", "t")
        (other / "new.py").write_text("n\n", newline="\n")
        sh(other, "add", "new.py")
        sh(other, "commit", "-q", "-m", "trunk moved")
        sh(other, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.a, "fetch", "-q", "origin")
        self.assertEqual(self.run_hook(), "")
        (self.a / "w.py").write_text("real\n", newline="\n")
        sh(self.a, "add", "w.py")
        sh(self.a, "commit", "-q", "-m", "real")
        self.assertIn("not shipped", self.run_hook())

    def test_same_state_blocks_a_session_only_once(self):
        os.environ["MTS_STOP_GUARD_HOME"] = str(self.tmp)
        self.addCleanup(os.environ.pop, "MTS_STOP_GUARD_HOME", None)
        (self.a / "wip.py").write_text("x\n", newline="\n")
        self.assertIn("block", self.run_hook(session_id="s1"))
        self.assertEqual(self.run_hook(session_id="s1"), "")                  # unchanged state: no second ~150k-token turn
        (self.a / "more.py").write_text("y\n", newline="\n")
        self.assertIn("block", self.run_hook(session_id="s1"))                # new work: blocks again
        self.assertIn("block", self.run_hook(session_id="s2"))                # another session: blocks

    def test_live_tree_and_off_switch_are_exempt(self):
        (self.a / "wip.py").write_text("x\n", newline="\n")
        os.environ["MTS_STOP_GUARD"] = "off"
        try:
            self.assertEqual(self.run_hook(), "")
        finally:
            os.environ.pop("MTS_STOP_GUARD", None)
        (self.a / ".mts_live").write_text("", newline="\n")
        self.assertEqual(self.run_hook(), "")

    def test_garbage_input_never_raises(self):
        self.assertEqual(stop_guard.hook("not json"), "")

    def test_antigravity_stop_hook_and_gemini_q_exemption(self):
        os.environ["MTS_STOP_GUARD_HOME"] = str(self.tmp)
        self.addCleanup(os.environ.pop, "MTS_STOP_GUARD_HOME", None)
        (self.a / "wip.py").write_text("x\n", newline="\n")
        payload = json.dumps({
            "conversationId": "conv-123",
            "workspacePaths": [str(self.a)],
            "terminationReason": "NO_TOOL_CALL",
        })
        out = json.loads(stop_guard.hook(payload))
        self.assertEqual(out["decision"], "continue")
        self.assertIn("sync.py ship", out["reason"])
        # Non-NO_TOOL_CALL termination (e.g. USER_CANCELED) is allowed to stop
        canceled = json.dumps({
            "conversationId": "conv-456",
            "workspacePaths": [str(self.a)],
            "terminationReason": "USER_CANCELED",
        })
        self.assertEqual(stop_guard.hook(canceled), "")
        # gemini-q/* branches commit without shipping (reviewed by Claude)
        sh(self.a, "checkout", "-q", "-b", "gemini-q/test-card")
        self.assertEqual(stop_guard.hook(json.dumps({
            "conversationId": "conv-789",
            "workspacePaths": [str(self.a)],
            "terminationReason": "NO_TOOL_CALL",
        })), "")

    def test_fast_path_matches_reference_in_every_state(self):
        for step in ("clean", "wip", "ahead", "live"):
            if step == "wip":
                (self.a / "wip.py").write_text("x\n", newline="\n")
            elif step == "ahead":
                sh(self.a, "add", "wip.py")
                sh(self.a, "commit", "-q", "-m", "w")
            elif step == "live":
                (self.a / ".mts_live").write_text("", newline="\n")
            self.assertEqual(stop_guard.reason(self.a), stop_guard._slow_reason(self.a), step)
        sh(self.a, "checkout", "-q", "fast-track")
        self.assertEqual(stop_guard.reason(self.a), stop_guard._slow_reason(self.a))
        sub = self.a / "deep" / "er"
        sub.mkdir(parents=True)
        self.assertEqual(stop_guard.reason(sub), stop_guard._slow_reason(sub))

    def test_eol_only_rewrite_is_not_work(self):
        """B6: a gate rewrites a file with LF under core.autocrlf=true; status says ` M`, git diff sees no change."""
        sh(self.a, "config", "core.autocrlf", "true")
        (self.a / "README.md").unlink()
        sh(self.a, "checkout", "--", "README.md")              # worktree now CRLF, as on every Windows host
        (self.a / "README.md").write_bytes(b"x\n")              # the gate writes LF
        st = subprocess.run(["git", "-C", str(self.a), "status", "--short"], capture_output=True, text=True).stdout
        self.assertIn("README.md", st)                          # git itself reports it modified
        self.assertIsNone(stop_guard.reason(self.a))
        self.assertIsNone(stop_guard._slow_reason(self.a))
        (self.a / "README.md").write_bytes(b"y\n")              # a real change still blocks
        self.assertIn("uncommitted", stop_guard.reason(self.a))

    def test_files_of_a_nested_worktree_are_not_this_trees_work(self):
        """B3: an Agent's isolation worktree lives inside the parent tree (.claude/worktrees/agent-x); its files are not the
        parent's work and must not block the parent's stop. A real untracked file next to it still blocks."""
        nested = self.a / ".claude" / "worktrees" / "agent-x"
        sh(self.a, "worktree", "add", "-q", "-b", "agent-x", str(nested), "HEAD")
        (nested / "worker_wip.py").write_text("w\n", newline="\n")
        self.assertIsNone(stop_guard.reason(self.a))
        self.assertIsNone(stop_guard._slow_reason(self.a))
        (self.a / ".claude" / "notes.txt").write_text("mine\n", newline="\n")
        self.assertIn("uncommitted", stop_guard.reason(self.a))

    def test_clean_tree_does_not_import_sync(self):
        code = ("import sys, json; sys.path.insert(0, %r); import stop_guard; r = stop_guard.reason(%r); "
                "print(json.dumps([r, 'sync' in sys.modules]))" % (str(Path(__file__).resolve().parent), str(self.a)))
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertEqual(json.loads(r.stdout.strip().splitlines()[-1]), [None, False], r.stderr)


if __name__ == "__main__":
    unittest.main()


class SupervisorWatcherTest(StopGuardTest):
    """test_stop_guard_supervisor_watcher: a Supervisor turn may not end with no live watcher or no fresh plan."""

    def setUp(self):
        super().setUp()
        import role_loader
        import supervisor
        self.rl, self.sup = role_loader, supervisor
        for k in ("MTS_ROLES_HOME", "MTS_RELAY_HOME", "MTS_STOP_GUARD_HOME"):
            os.environ[k] = str(self.tmp / k)
            self.addCleanup(os.environ.pop, k, None)
        self.rl.mark_injected("sup1", "Supervisor", {"login": "B"}, explicit=True)
        self.home = self.sup.loop_home()
        self.home.mkdir(parents=True, exist_ok=True)

    def _plan(self, minutes_ago):
        from datetime import datetime, timedelta, timezone
        at = (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%MZ")
        (self.home / "B-last-plan.json").write_text(json.dumps({"at": at}), newline="\n")

    def _watcher(self):
        from datetime import datetime, timedelta, timezone
        exp = (datetime.now(timezone.utc) + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%MZ")
        (self.home / "B-watcher.json").write_text(json.dumps({"pid": os.getpid(), "expires": exp}), newline="\n")

    def test_blocks_without_watcher_or_plan(self):
        out = json.loads(self.run_hook(session_id="sup1"))
        self.assertEqual(out["decision"], "block")
        self.assertIn("NO WAKE SOURCE", out["reason"])
        self.assertIn("plan", out["reason"])

    def test_blocks_with_stale_plan_even_when_watcher_lives(self):
        self._watcher()
        self._plan(30)
        self.assertIn("no `supervisor.py plan", self.run_hook(session_id="sup1"))

    def test_allows_with_watcher_and_fresh_plan(self):
        self._watcher()
        self._plan(2)
        self.assertEqual(self.run_hook(session_id="sup1"), "")

    def test_blocks_every_idle_turn_inside_the_work_period(self):
        """2026-10-30: blocked once, then idle 16 h. Each fresh turn end blocks again; only the blocked turn's retry
        (stop_hook_active) may end."""
        self.assertIn("block", self.run_hook(session_id="sup1"))
        self.assertIn("block", self.run_hook(session_id="sup1"))
        self.assertEqual(self.run_hook(session_id="sup1", stop_hook_active=True), "")

    def test_ended_work_period_allows_the_stop(self):
        (self.home / "B-work.json").write_text(json.dumps({"until": "2026-10-01T00:00Z", "sid": "sup1"}), newline="\n")
        self.assertEqual(self.run_hook(session_id="sup1"), "")

    def test_supervisor_without_role_line_is_found_by_its_plan_readings(self):
        """The 2026-10-30 Supervisor C had no role line, so the guard failed open; its own `plan` readings name its login."""
        from datetime import datetime, timezone
        at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        (self.home / "C.jsonl").write_text(json.dumps({"at": at, "sid": "norole"}) + "\n", newline="\n")
        out = json.loads(self.run_hook(session_id="norole"))
        self.assertIn("Supervisor C", out["reason"])
        (self.home / "C.jsonl").write_text(json.dumps({"at": at, "sid": "successor"}) + "\n", newline="\n")
        self.assertEqual(self.run_hook(session_id="norole"), "")    # a newer Supervisor of C took over: this one may end

    def test_other_roles_and_errors_fail_open(self):
        self.assertEqual(self.run_hook(session_id="not-a-supervisor"), "")
        self.rl.mark_injected("sup2", "Supervisor", {}, explicit=True)    # login unknown
        self.assertEqual(self.run_hook(session_id="sup2"), "")
        self.assertEqual(self.run_hook(session_id="sup1", stop_hook_active=True), "")
