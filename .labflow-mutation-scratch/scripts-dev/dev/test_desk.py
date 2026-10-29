"""desk.py: post -> take -> done across two clones, wait reads origin, finished tasks cannot be reopened,
nothing is ever committed in the live tree (.mts_live)."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import desk


def sh(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class DeskTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        origin = self.tmp / "origin.git"
        sh(self.tmp, "init", "-q", "--bare", str(origin))
        sh(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
        self.a, self.b = self.tmp / "a", self.tmp / "b"
        for c in (self.a, self.b):
            sh(self.tmp, "clone", "-q", str(origin), str(c))
            sh(c, "config", "user.email", "t@t")
            sh(c, "config", "user.name", "t")
        (self.a / "README.md").write_text("x\n")
        sh(self.a, "add", "."), sh(self.a, "commit", "-q", "-m", "init")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.b, "pull", "-q", "origin", "fast-track")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_round_trip(self):
        rid = desk.post(self.a, "Copy klines", "copy F:/MTS/data/x to NUC", "file exists", ship=False)
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        self.assertIsNone(desk.wait(self.a, rid, timeout=0.3, poll=0.1))  # still open
        sh(self.b, "pull", "-q", "origin", "fast-track")
        self.assertEqual([t["status"] for t in desk.tasks(self.b)], ["pending"])
        desk.take(self.b, rid, ship=False)
        with self.assertRaises(SystemExit):
            desk.take(self.b, rid, ship=False)  # already taken
        desk.finish(self.b, rid, "copied 2 files", ship=False)
        sh(self.b, "push", "-q", "origin", "HEAD:fast-track")
        got = desk.wait(self.a, rid, timeout=5, poll=0.1)  # a never pulled: reads origin directly
        self.assertEqual((got["status"], got["result"]), ("done", "copied 2 files"))
        with self.assertRaises(SystemExit):
            desk.finish(self.b, rid, "again", ship=False)

    def test_declined_task_raises_operator_line(self):
        rid = desk.post(self.a, "Restart runner", "restart alert runner", "running", ship=False)
        desk.finish(self.a, rid, "declined: restarts are supervisor-only", failed=True, ship=False)
        msg = subprocess.run(["git", "log", "-1", "--format=%B"], cwd=self.a, capture_output=True, text=True).stdout
        self.assertIn("Operator: desk task", msg)
        self.assertEqual(desk.tasks(self.a)[0]["status"], "failed")

    def head(self, repo, ref="HEAD"):
        return subprocess.run(["git", "rev-parse", ref], cwd=repo, capture_output=True, text=True).stdout.strip()

    def test_live_tree_never_gets_a_commit(self):
        """2026-10-10: take/done run in the live tree made commits there that never reached origin (STOP_NOT_FF)."""
        rid = desk.post(self.b, "Fetch captions", "run fetch", "file exists", ship=False)
        sh(self.b, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.a, "pull", "-q", "origin", "fast-track")  # the deployed live tree holds the task file too
        (self.a / ".mts_live").write_text("")
        before = self.head(self.a)
        with self.assertRaises(SystemExit):  # --no-ship would strand the commit in the live tree
            desk.take(self.a, rid, ship=False)
        pushed = lambda wt: sh(wt, "push", "-q", "origin", "HEAD:refs/heads/fast-track")
        with mock.patch.object(desk, "run_ship", pushed):
            desk.take(self.a, rid)
            desk.finish(self.a, rid, "fetched 3 files")  # live copy still says pending: status is read from origin
            desk.post(self.a, "Follow-up", "x", "y")
        self.assertEqual(self.head(self.a), before)
        self.assertEqual(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=self.a,
                                        capture_output=True, text=True).stdout, "")
        self.assertEqual([t["status"] for t in desk.tasks(self.a)], ["pending"])  # live files untouched
        self.assertEqual(len(subprocess.run(["git", "worktree", "list"], cwd=self.a, capture_output=True,
                                            text=True).stdout.splitlines()), 1)  # scratch worktree cleaned up
        sh(self.b, "pull", "-q", "origin", "fast-track")
        got = sorted((t["title"], t["status"]) for t in desk.tasks(self.b))
        self.assertEqual(got, [("Fetch captions", "done"), ("Follow-up", "pending")])

    def row(self, rid, target, status="pending"):
        desk.save(self.a, {"id": rid, "title": rid, "need": "n", "done_when": "d", "target": target,
                           "from": "t", "posted": "x", "status": status})

    def test_next_returns_this_hosts_first_pending_row(self):
        """B180: both DSA bridges read one board; each must be handed only its own lane, oldest first."""
        self.row("20261001-000001-nb", "DSA-NB")
        self.row("20261001-000002-nuc-taken", "DSA-NUC", "taken")
        self.row("20261001-000003-live", "JIS-NUC")          # live-host row: never DSA's
        self.row("20261001-000004-any", "DSA")
        self.row("20261001-000005-nuc", "DSA-NUC")
        self.assertEqual(desk.next_for(self.a, "JIS-NUC")["id"], "20261001-000004-any")
        self.assertEqual(desk.next_for(self.a, "jis-nb")["id"], "20261001-000001-nb")
        desk.finish(self.a, "20261001-000004-any", "ok", ship=False)
        self.assertEqual(desk.next_for(self.a, "JIS-NUC")["id"], "20261001-000005-nuc")
        self.assertIsNone(desk.next_for(self.a, "JIS-XYZ"))  # only the closed shared row and other hosts' rows remain
        with mock.patch.object(desk.socket, "gethostname", return_value="JIS-NUC"):
            self.assertEqual(desk.next_for(self.a)["id"], "20261001-000005-nuc")

    def test_assign_posts_each_ready_dsa_card_once(self):
        import tasks as T
        base = dict(goal="g", scope_in=["x"], steps=["s"], done_when="file exists", size="S", state="ready")
        for cid, lane in (("C1", "DSA-NUC"), ("C2", "SONNET"), ("C3", "JIS-NB")):
            T.save(self.a, {**T.blank(cid, f"card {cid}", lane=lane), **base, "commands": ["python x.py"],
                            "tests": "t fails first" if lane == "SONNET" else "", "live_path": lane == "JIS-NB"})
        T.save(self.a, T.blank("C4", "raw card", lane="DSA"))
        made = desk.assign(self.a, ship=False)
        rows = desk.tasks(self.a)
        self.assertEqual([(r["card"], r["target"], r["status"]) for r in rows], [("C1", "DSA-NUC", "pending")])
        self.assertEqual(made, [rows[0]["id"]])
        self.assertIn("python x.py", rows[0]["need"])
        self.assertEqual(desk.next_for(self.a, "JIS-NUC")["card"], "C1")
        desk.finish(self.a, made[0], "ran", ship=False)
        self.assertEqual(desk.assign(self.a, ship=False), [])  # a closed row is not re-posted
        self.assertEqual(subprocess.run(["git", "status", "--porcelain", "--", desk.QUEUE], cwd=self.a,
                                        capture_output=True, text=True).stdout, "")  # rows are committed


if __name__ == "__main__":
    unittest.main()
