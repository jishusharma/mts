"""route_audit.py, the sync.py ship route-tag gate and tasks.py done --next (d-route-tag-every-session-1104)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import route_audit as RA
import sync
import tasks as T

CARDS = "MyTradingSys/system/tasks"


def sh(cwd, *args, env=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout.strip()


def commit(repo, msg, files=None, when=None, author="t@t"):
    for rel, text in (files or {}).items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
        sh(repo, "add", rel)
    env = dict(os.environ, GIT_AUTHOR_EMAIL=author, GIT_COMMITTER_EMAIL=author)
    if when:
        env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    sh(repo, "commit", "-q", "--allow-empty", "-m", msg, env=env)
    return sh(repo, "rev-parse", "HEAD")


def card(cid, state="raw"):
    return {f"{CARDS}/{cid}.json": json.dumps({"id": cid, "state": state, "created": "2026-11-01T00:00:00Z"})}


class RepoCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.r = self.tmp / "r"
        self.r.mkdir()
        sh(self.r, "init", "-q")
        sh(self.r, "symbolic-ref", "HEAD", "refs/heads/fast-track")  # git < 2.28 has no init -b
        sh(self.r, "config", "user.name", "t")
        sh(self.r, "config", "user.email", "t@t")
        commit(self.r, "init", {"README.md": "x\n"})
        sh(self.r, "update-ref", "refs/remotes/origin/fast-track", "HEAD")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class ParseNext(unittest.TestCase):
    def test_grammar(self):
        self.assertEqual(RA.parse_next("END: no edge, fee-net"), ("end", "no edge, fee-net"))
        self.assertEqual(RA.parse_next("backtest"), ("stage", "backtest"))
        self.assertEqual(RA.parse_next("gemini-blind-read-x (review)"), ("card", "gemini-blind-read-x"))
        self.assertEqual(RA.parse_next('new:"Follow up"', allow_new=True), ("new", "Follow up"))
        for bad in ("", "END:", "END:   ", 'new:"x"', "?? what"):
            self.assertIsNone(RA.parse_next(bad)[0], bad)

    def test_card_id_with_trailing_colon(self):
        self.assertEqual(RA.parse_next("some-card-id: reason here"), ("card", "some-card-id"))
        self.assertEqual(RA.parse_next("some-card-id:reason"), ("card", "some-card-id"))
        self.assertEqual(RA.parse_next("backtest: next step"), ("stage", "backtest"))

    def test_reject_gives_fix_hint(self):
        why = RA.parse_next("?? what")[1]
        self.assertIn("fix:", why)
        self.assertNotIn(chr(10), why)

    def test_exempt(self):
        self.assertTrue(RA.exempt("claim foo", ["x.py"]))
        self.assertTrue(RA.exempt("Revert \"x\"", ["x.py"]))
        self.assertTrue(RA.exempt("tasks: refine", [f"{CARDS}/a.json"]))
        self.assertFalse(RA.exempt("study: no edge", ["MyTradingSys/research/s/RESULT.md"]))


class Check(RepoCase):
    def run_check(self):
        found, n = RA.check(self.r, "HEAD", 7, 72)
        return sorted(k for k, *_ in found), n

    def test_untagged_bad_and_missing_card(self):
        commit(self.r, "study A\n\nResult: no edge", {"a.md": "a"})
        commit(self.r, "study B\n\nResult: 3 rows\nNext: no-such-card", {"b.md": "b"}, author="other@t")
        commit(self.r, "study C\n\nResult: x\nNext: ?? later", {"c.md": "c"}, author="third@t")
        self.assertEqual(self.run_check(), (["BAD-TAG", "NO-CARD", "UNTAGGED"], 3))

    def test_end_and_existing_card_pass_and_later_tag_covers_ship(self):
        commit(self.r, "cards", card("next-one"))   # card-only commit: exempt
        commit(self.r, "part 1\n\nResult: half", {"a.md": "a"})
        commit(self.r, "part 2\n\nResult: all\nNext: next-one", {"b.md": "b"})
        commit(self.r, "other\n\nResult: dead\nNext: END: no edge", {"c.md": "c"}, author="o@t")
        self.assertEqual(self.run_check(), ([], 3))

    def test_stale_next_card(self):
        old = (datetime.now(timezone.utc) - timedelta(hours=100)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        commit(self.r, "cards", card("old-card"), when=old)
        commit(self.r, "study\n\nResult: x\nNext: old-card", {"a.md": "a"})
        self.assertEqual(self.run_check()[0], ["STALE-CARD"])
        commit(self.r, "cards", card("old-card", "done"))
        self.assertEqual(self.run_check()[0], [])

    def test_main_exit_code(self):
        commit(self.r, "study\n\nResult: x", {"a.md": "a"})
        self.assertEqual(RA.main(["check", "--repo", str(self.r), "--ref", "HEAD"]), 1)


class ShipGate(RepoCase):
    def test_refuses_untagged_ship(self):
        commit(self.r, "work\n\nResult: x", {"a.py": "x = 1\n"})
        with self.assertRaises(sync.SyncError) as e:
            sync.check_route_tags(self.r)
        self.assertIn("--next", str(e.exception))
        self.assertEqual(len(str(e.exception).splitlines()), 1)

    def test_refuses_missing_card_even_with_route_commit(self):
        commit(self.r, "work\n\nResult: x\nNext: ghost-card", {"a.py": "x = 1\n"})
        with self.assertRaises(sync.SyncError):
            sync.check_route_tags(self.r)
        sync.commit_pending(self.r, None, nxt="END: no edge, recorded")
        with self.assertRaises(sync.SyncError):   # the ghost card still refuses
            sync.check_route_tags(self.r)

    def test_end_passes_and_chores_exempt(self):
        commit(self.r, "claim x\n\nResult: claim", {"MyTradingSys/system/claims/x.md": "c"})
        commit(self.r, "tasks: new card\n\nResult: card", card("c1"))
        sync.check_route_tags(self.r)   # only exempt commits: no tag needed
        commit(self.r, "work\n\nResult: x", {"a.py": "x = 1\n"})
        sync.commit_pending(self.r, None, nxt="c1")
        sync.check_route_tags(self.r)


class DoneNext(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.old = T.REPO
        T.REPO = self.tmp
        (self.tmp / CARDS).mkdir(parents=True)
        T.save(self.tmp, T.blank("base-card", "Base"))

    def tearDown(self):
        T.REPO = self.old
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_grammar_and_new_card(self):
        c = T.get(self.tmp, "base-card")
        self.assertIsNone(T.route_next(c, None))
        self.assertEqual(T.route_next(c, "END: no edge"), "END: no edge")
        self.assertEqual(T.route_next(c, "base-card"), "base-card")
        with self.assertRaises(SystemExit):
            T.route_next(c, "missing-card")
        with self.assertRaises(SystemExit):
            T.route_next(c, "END:")
        cid = T.route_next(c, 'new:"Gemini blind read of base"')
        self.assertEqual(cid, "gemini-blind-read-of-base")
        self.assertEqual(T.get(self.tmp, cid)["state"], "raw")

    def test_done_requires_next(self):
        with self.assertRaises(SystemExit):
            T.main(["done", "base-card", "--result", "x"])


if __name__ == "__main__":
    unittest.main()
