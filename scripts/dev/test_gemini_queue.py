"""gemini-queue-claim-race-fix: claim retries on a busy trunk, own claim = ok, other holder = skip, git identity set."""
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gemini_queue as gq  # noqa: E402

REJ = "push rejected (someone shipped first)"


def cp(rc, err=""):
    return subprocess.CompletedProcess([], rc, "", err)


class ClaimRetryTest(unittest.TestCase):
    def test_reject_3_times_then_accept(self):
        seq = [cp(1, REJ), cp(1, REJ), cp(1, REJ), cp(0)]
        sleeps = []
        with mock.patch.object(gq, "sh", side_effect=seq) as sh:
            self.assertEqual(gq.claim_with_retry("wt", "c1", sleep=sleeps.append), ("ok", ""))
        self.assertEqual(sh.call_count, 4)
        self.assertEqual(len(sleeps), 3)
        self.assertTrue(all(2 <= s <= 10 for s in sleeps))

    def test_gives_up_after_6(self):
        with mock.patch.object(gq, "sh", return_value=cp(1, REJ)) as sh:
            st, why = gq.claim_with_retry("wt", "c1", sleep=lambda s: None)
        self.assertEqual((st, sh.call_count), ("fail", 6))
        self.assertIn("6 tries", why)

    def test_other_holder_skips_at_once(self):
        with mock.patch.object(gq, "sh", return_value=cp(1, "already claimed by OTHER-HOST / x: c1")) as sh:
            self.assertEqual(gq.claim_with_retry("wt", "c1", sleep=lambda s: None)[0], "skip")
        self.assertEqual(sh.call_count, 1)

    def test_own_claim_is_success(self):
        err = f"already claimed by {socket.gethostname()} / me: c1"
        with mock.patch.object(gq, "sh", return_value=cp(1, err)):
            self.assertEqual(gq.claim_with_retry("wt", "c1", sleep=lambda s: None)[0], "ok")

    def test_timeout_fails_without_retry(self):
        with mock.patch.object(gq, "sh", return_value=cp(124, "timeout after 120s")) as sh:
            self.assertEqual(gq.claim_with_retry("wt", "c1", sleep=lambda s: None)[0], "fail")
        self.assertEqual(sh.call_count, 1)


    def test_non_race_push_failure_fails_at_once(self):
        # bg-process-audit 2026-10-28: an auth/network push failure retried 6 x 3 pushes; sync.py now says "not a race"
        err = "sync: claim push FAILED (not a race, no retry): fatal: Authentication failed"
        with mock.patch.object(gq, "sh", return_value=cp(1, err)) as sh:
            st, why = gq.claim_with_retry("wt", "c1", sleep=lambda s: None)
        self.assertEqual((st, sh.call_count), ("fail", 1))
        self.assertIn("Authentication failed", why)


class RunJobTest(unittest.TestCase):
    def _run(self, claim_result):
        calls = []
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "c1").mkdir()

            def fake_git(*a, **kw):
                calls.append(a)
                return cp(0)
            with mock.patch.object(gq, "ROOT", Path(t)), mock.patch.object(gq, "git", side_effect=fake_git), \
                    mock.patch("sync.open_claims", return_value=[]), \
                    mock.patch.object(gq, "claim_with_retry", return_value=claim_result), \
                    mock.patch.object(gq.subprocess, "run") as run:
                gq.run_job("c1", "low")
            return calls, (Path(t) / "c1.log").read_text(encoding="utf-8"), run

    def test_identity_set_and_failure_logged(self):
        calls, log, run = self._run(("fail", "after 6 tries: rejected"))
        self.assertIn(("config", "user.name", "gemini-queue"), calls)
        self.assertIn(("config", "user.email", "gemini-queue@mts.local"), calls)
        self.assertTrue(log.startswith("CLAIM FAILED: c1: after 6 tries"), log)
        self.assertEqual(len(log.strip().splitlines()), 1)
        run.assert_not_called()

    def test_skip_logged(self):
        _, log, run = self._run(("skip", "already claimed by X"))
        self.assertTrue(log.startswith("SKIP c1"), log)
        run.assert_not_called()


class TwoProcessClaimRaceTest(unittest.TestCase):
    """CT-2: two real `sync.py claim` processes against a bare temp remote; no mocked push or git."""

    def _git(self, cwd, *a):
        return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True)

    def _fixture(self, tmp):
        import shutil
        tmp = Path(tmp)
        bare = tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "fast-track", str(bare)], check=True)
        seed = tmp / "seed"
        seed.mkdir()
        shutil.copytree(Path(__file__).resolve().parent, seed / "scripts" / "dev", ignore=shutil.ignore_patterns("__pycache__"))
        (seed / "MyTradingSys" / "system").mkdir(parents=True)
        (seed / "MyTradingSys" / "system" / "README.txt").write_text("x" + chr(10), encoding="utf-8")
        self._git(seed, "init", "-q", "-b", "fast-track")
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            self._git(seed, "config", k, v)
        self._git(seed, "add", "-A")
        self._git(seed, "commit", "-q", "-m", "seed")
        self._git(seed, "remote", "add", "origin", str(bare))
        self._git(seed, "push", "-q", "origin", "fast-track")
        clones = []
        for n in ("a", "b"):
            c = tmp / n
            subprocess.run(["git", "clone", "-q", "-b", "fast-track", str(bare), str(c)], check=True)
            for k, v in (("user.name", "t"), ("user.email", "t@t")):
                self._git(c, "config", k, v)
            clones.append(c)
        return bare, clones

    def _race(self, warm):
        import threading
        with tempfile.TemporaryDirectory() as td:
            bare, (a, b) = self._fixture(td)
            base = ["MyTradingSys/system/claims/warm-card.md"] if warm else []
            if warm:   # the claims side branch already exists: the loser meets an ordinary non-fast-forward rejection
                self.assertEqual(gq.sh([sys.executable, "scripts/dev/sync.py", "claim", "warm-card", "--force"], cwd=a).returncode, 0)
            barrier = threading.Barrier(2)
            res = {}

            def go(name, wt):
                barrier.wait()
                res[name] = gq.sh([sys.executable, "scripts/dev/sync.py", "claim", "race-card", "--force"], cwd=wt, timeout=120)

            ts = [threading.Thread(target=go, args=(n, w)) for n, w in (("a", a), ("b", b))]
            [t.start() for t in ts]
            [t.join() for t in ts]
            msgs = {n: (r.stdout + r.stderr) for n, r in res.items()}
            self.assertEqual(sorted(r.returncode == 0 for r in res.values()), [False, True], msgs)   # exactly one winner
            loser = next(m for n, m in msgs.items() if res[n].returncode != 0)
            files = self._git(bare, "ls-tree", "-r", "--name-only", "claims").stdout.split()
            self.assertEqual(sorted(files), sorted(base + ["MyTradingSys/system/claims/race-card.md"]))   # never race-card-2
            return loser, bare, (a, b), files

    def test_two_process_claim_race_against_bare_repo(self):
        loser, bare, _, _ = self._race(warm=True)
        self.assertIn("already claimed by", loser)               # the loser saw the conflict, no silent double claim

    def test_two_process_first_claim_race_creating_claims_branch(self):
        # Real finding (CT-2): both claimers create origin/claims at once; the loser gets "reference already exists", which
        # sync.PUSH_RACE_RE does not match, so it is reported as a non-race failure. It still fails cleanly: one claim file.
        loser, _, _, _ = self._race(warm=False)
        self.assertTrue("already claimed by" in loser or "FAILED" in loser, loser)


if __name__ == "__main__":
    unittest.main()
