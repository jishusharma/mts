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


NL = chr(10)


class TwoProcessClaimRaceTest(unittest.TestCase):
    """CT-2 (fix_verification_2026-10-28): two REAL sync.py claim processes against a bare temp origin, no mocked push.
    Asserts the outcome set, never which claimer wins."""
    CARD = "race-card"

    def _git(self, cwd, *a):
        r = subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def _fixture(self, tmp, precreate_claims):
        import shutil
        tmp = Path(tmp)
        bare = tmp / "origin.git"
        subprocess.run(["git", "init", "--bare", "-q", "-b", "fast-track", str(bare)], check=True)
        seed = tmp / "seed"
        subprocess.run(["git", "clone", "-q", str(bare), str(seed)], check=True, capture_output=True)
        shutil.copytree(Path(__file__).resolve().parent, seed / "scripts" / "dev",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (seed / "README").write_text("x")
        for k, v in (("user.name", "seed"), ("user.email", "s@x"), ("commit.gpgsign", "false")):
            self._git(seed, "config", k, v)
        self._git(seed, "checkout", "-q", "-B", "fast-track")
        self._git(seed, "add", "-A")
        self._git(seed, "commit", "-q", "-m", "seed")
        self._git(seed, "push", "-q", "origin", "fast-track")
        if precreate_claims:
            self._git(seed, "checkout", "-q", "--orphan", "claims")
            self._git(seed, "rm", "-rq", "--cached", ".")
            d = seed / "MyTradingSys" / "system" / "claims"
            d.mkdir(parents=True)
            (d / "other.md").write_text(NL.join(["task: other", "host: h", "account: a", "area: -", "epoch: 1", ""]))
            self._git(seed, "add", "MyTradingSys/system/claims/other.md")
            self._git(seed, "commit", "-q", "-m", "claims init")
            self._git(seed, "push", "-q", "origin", "claims")
        clones = []
        for n in ("A", "B"):
            c = tmp / n
            subprocess.run(["git", "clone", "-q", "-b", "fast-track", str(bare), str(c)], check=True, capture_output=True)
            for k, v in (("user.name", "claimer" + n), ("user.email", n + "@x"), ("commit.gpgsign", "false")):
                self._git(c, "config", k, v)
            clones.append(c)
        return bare, clones

    def _race(self, precreate_claims):
        with tempfile.TemporaryDirectory() as tmp:
            bare, clones = self._fixture(tmp, precreate_claims)
            go = Path(tmp) / "go"
            runner = NL.join(["import sys,time,subprocess,pathlib", "g=pathlib.Path(sys.argv[1])", "while not g.exists(): time.sleep(0.005)",
                         "sys.exit(subprocess.run([sys.executable,'scripts/dev/sync.py','claim',sys.argv[2]]).returncode)", ""])
            procs = [subprocess.Popen([sys.executable, "-c", runner, str(go), self.CARD], cwd=str(c),
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                      env={**__import__("os").environ, "GIT_TERMINAL_PROMPT": "0", "MTS_ACCOUNT": "acct"})
                     for c in clones]
            go.write_text("go")
            outs = [p.communicate(timeout=180)[0] for p in procs]
            rcs = [p.returncode for p in procs]
            winners = [i for i, rc in enumerate(rcs) if rc == 0]
            losers = [i for i, rc in enumerate(rcs) if rc != 0]
            self.assertEqual(len(winners), 1, (rcs, outs))
            self.assertEqual(len(losers), 1, (rcs, outs))
            lo = outs[losers[0]]
            self.assertIn("already claimed by", lo)          # the lost-race path ...
            self.assertNotIn("not a race", lo)                # ... not a push error
            self.assertNotIn("still rejected", lo)
            subprocess.run(["git", "-C", str(bare), "rev-parse", "--verify", "claims"], check=True, capture_output=True)
            files = self._git(bare, "ls-tree", "-r", "--name-only", "claims").split()
            mine = [f for f in files if f.endswith(f"{self.CARD}.md")]
            self.assertEqual(mine, [f"MyTradingSys/system/claims/{self.CARD}.md"], files)
            body = self._git(bare, "show", f"claims:{mine[0]}")
            self.assertEqual(body.count("host:"), 1, body)

    def test_two_process_claim_race_against_bare_repo(self):
        self._race(precreate_claims=True)

    def test_two_process_claim_race_claims_branch_absent(self):
        self._race(precreate_claims=False)


if __name__ == "__main__":
    unittest.main()
