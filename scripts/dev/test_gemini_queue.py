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


class RootConfigTest(unittest.TestCase):
    def test_root_from_env(self):
        with tempfile.TemporaryDirectory() as t, mock.patch.dict("os.environ", {"MTS_GQ_ROOT": t}):
            self.assertEqual(gq.root(), Path(t))

    def test_root_default_when_env_unset(self):
        env = {k: v for k, v in __import__("os").environ.items() if k != "MTS_GQ_ROOT"}
        with mock.patch.dict("os.environ", env, clear=True):
            self.assertEqual(gq.root(), gq.ROOT)


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


class IdentityEnvTest(unittest.TestCase):
    def test_sh_passes_identity_env(self):
        with mock.patch.object(gq.subprocess, "run", return_value=cp(0)) as run:
            gq.sh(["git", "commit"])
        env = run.call_args.kwargs["env"]
        for k, v in gq.IDENTITY.items():
            self.assertEqual(env[k], v)


class RunJobTest(unittest.TestCase):
    def _run(self, claim_result, gate=(True, "")):
        calls = []
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "c1").mkdir()

            def fake_git(*a, **kw):
                calls.append(a)
                return cp(0)
            with mock.patch.object(gq, "ROOT", Path(t)), mock.patch.object(gq, "git", side_effect=fake_git), \
                    mock.patch("sync.open_claims", return_value=[]), \
                    mock.patch.object(gq, "card_gate", return_value=gate), \
                    mock.patch.object(gq, "claim_with_retry", return_value=claim_result), \
                    mock.patch.object(gq.subprocess, "run") as run:
                gq.run_job("c1", "low")
            return calls, (Path(t) / "c1.log").read_text(encoding="utf-8"), run

    def _run_claims(self, claims):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "c1").mkdir()
            with mock.patch.object(gq, "ROOT", Path(t)), mock.patch.object(gq, "git", return_value=cp(0)),                     mock.patch("sync.open_claims", return_value=claims),                     mock.patch.object(gq, "card_gate", return_value=(True, "")),                     mock.patch.object(gq, "claim_with_retry", return_value=("fail", "x")),                     mock.patch.object(gq.subprocess, "run"):
                gq.run_job("c1", "low")
            return (Path(t) / "c1.log").read_text(encoding="utf-8")

    def test_own_host_open_claim_not_skipped(self):
        log = self._run_claims([("c1", {"host": socket.gethostname().upper()})])
        self.assertFalse(log.startswith("SKIP"), log)

    def test_other_host_open_claim_skipped(self):
        log = self._run_claims([("c1", {"host": "OTHER-HOST"})])
        self.assertTrue(log.startswith("SKIP c1: already claimed by OTHER-HOST"), log)

    def test_identity_set_and_failure_logged(self):
        calls, log, run = self._run(("fail", "after 6 tries: rejected"))
        # git-identity-1104: identity is per process (env), never `git config` (that wrote the shared .git/config)
        self.assertFalse([c for c in calls if c[:1] == ("config",)], calls)
        self.assertEqual(gq.IDENTITY["GIT_AUTHOR_NAME"], "gemini-queue")
        self.assertEqual(gq.IDENTITY["GIT_COMMITTER_EMAIL"], "gemini-queue@mts.local")
        self.assertTrue(log.startswith("CLAIM FAILED: c1: after 6 tries"), log)
        self.assertEqual(len(log.strip().splitlines()), 1)
        run.assert_not_called()

    def test_skip_logged(self):
        _, log, run = self._run(("skip", "already claimed by X"))
        self.assertTrue(log.startswith("SKIP c1"), log)
        run.assert_not_called()


    def test_done_card_skipped(self):
        calls, log, run = self._run(("ok", ""), gate=(False, "state done/READY"))
        self.assertTrue(log.startswith("SKIP c1: state done"), log)
        self.assertFalse([c for c in calls if c[:1] == ("worktree",)])
        run.assert_not_called()

    def test_shipped_tag_skipped(self):
        calls, log, run = self._run(("ok", ""), gate=(False, "state ready/SHIPPED"))
        self.assertIn("SHIPPED", log)
        self.assertFalse([c for c in calls if c[:1] == ("worktree",)])
        run.assert_not_called()

    def test_ready_card_runs(self):
        calls, log, run = self._run(("fail", "x"))   # gate passed: it reached the claim step
        self.assertTrue(log.startswith("CLAIM FAILED"), log)


class ModelTokenTest(unittest.TestCase):
    """Operator order 2026-10-31: every Antigravity model reachable from `run <card>[:effort][:model]`."""

    def _parse(self, spec):
        with mock.patch.object(gq, "run_job") as rj, mock.patch.object(gq, "AGY", Path(__file__)):   # an existing file = agy "installed"
            rc = gq.main(["run", spec])
        return rc, rj.call_args

    def test_token_parsing_each_model(self):
        for spec, want in (("c1", ("c1", "low", "flash", "solo")), ("c1:flash", ("c1", "low", "flash", "solo")),
                           ("c1:high:argon", ("c1", "high", "argon", "solo")), ("c1:opus:medium", ("c1", "medium", "opus", "solo")),
                           ("c1:sonnet", ("c1", "low", "sonnet", "solo")), ("c1:gpt", ("c1", "low", "gpt", "solo")),
                           ("c1:high:gpt", ("c1", "high", "gpt", "solo"))):
            rc, call = self._parse(spec)
            self.assertEqual((rc, call.args), (0, want), spec)

    def test_bad_model_rejected(self):
        rc, call = self._parse("c1:llama")
        self.assertEqual(rc, 2)
        self.assertIsNone(call)

    def _agy_cmd(self, effort, model):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "c1").mkdir()
            with mock.patch.object(gq, "ROOT", Path(t)), mock.patch.object(gq, "git", return_value=cp(0)),                     mock.patch("sync.open_claims", return_value=[]),                     mock.patch.object(gq, "card_gate", return_value=(True, "")),                     mock.patch.object(gq, "claim_with_retry", return_value=("ok", "")),                     mock.patch.object(gq, "keep_lease"),                     mock.patch.object(gq, "sh", return_value=cp(0, "BRIEF")),                     mock.patch.object(gq.subprocess, "run", return_value=cp(0)) as run:
                gq.run_job("c1", effort, model)
            return run.call_args.args[0]

    def test_exact_model_id_passed_to_agy(self):
        for effort, model, want in (("low", "flash", "gemini-3.8-flash-low"), ("high", "argon", "gemini-4-argon-high"),
                                    ("medium", "opus", "claude-opus-5-5-medium"), ("low", "sonnet", "claude-sonnet-5-5-low"),
                                    ("high", "sonnet", "claude-sonnet-5-5-high")):
            cmd = self._agy_cmd(effort, model)
            self.assertEqual(cmd[cmd.index("--model") + 1], want)
            self.assertEqual(cmd[cmd.index("--effort") + 1], effort)

    def test_gpt_fixed_id_ignores_effort(self):
        for effort in ("low", "high"):
            cmd = self._agy_cmd(effort, "gpt")
            self.assertEqual(cmd[cmd.index("--model") + 1], "gpt-oss-120b-medium")
            self.assertNotIn("--effort", cmd)

    def test_rules_name_actual_model(self):
        self.assertNotIn("Gemini Flash worker", gq.rules_for("opus"))
        self.assertIn("claude-opus-5-5-high", gq.rules_for("opus", "claude-opus-5-5-high"))


class CardGateTest(unittest.TestCase):
    def _gate(self, out, rc=0, tag=""):
        with mock.patch.object(gq, "git", return_value=subprocess.CompletedProcess([], rc, out, "boom")),                 mock.patch("tasks.stop_tag", return_value=tag):
            return gq.card_gate("c1")

    def test_unreadable_card_fails_closed(self):
        self.assertFalse(self._gate("", rc=128)[0])
        self.assertFalse(self._gate("not json")[0])

    def test_done_and_tagged_refused_ready_ok(self):
        self.assertEqual(self._gate('{"state": "done"}')[0], False)
        self.assertEqual(self._gate('{"state": "ready"}', tag="SHIPPED abc")[0], False)
        self.assertEqual(self._gate('{"state": "ready"}'), (True, ""))


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
        subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)   # git 2.24 has no init -b
        subprocess.run(["git", "-C", str(bare), "symbolic-ref", "HEAD", "refs/heads/fast-track"], check=True)
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


class LeaseKeepAliveTest(unittest.TestCase):
    def test_keep_lease_heartbeats_until_stopped(self):
        import threading
        stop = threading.Event()
        calls = []
        with mock.patch.object(gq, "sh", side_effect=lambda cmd, **k: calls.append(cmd) or cp(0)):
            t = threading.Thread(target=gq.keep_lease, args=(Path("."), "card-x", stop, 0.01))
            t.start()
            for _ in range(200):
                if len(calls) >= 2:
                    break
                stop.wait(0.01)
            stop.set()
            t.join(2)
        self.assertGreaterEqual(len(calls), 2)
        self.assertEqual(calls[0][-2:], ["heartbeat", "card-x"])
        self.assertFalse(t.is_alive())


class GeminiStatusTest(unittest.TestCase):
    """gemini-status-no-end-1113: status says DONE, FAILED, RUNNING, STALE or SKIPPED per job, not just the last line."""

    def test_exit_zero_is_done(self):
        self.assertEqual(gq.job_state(["START c 3.8", "out", "EXIT 0 after 5s"], 10), "DONE")

    def test_nonzero_exit_is_failed(self):
        self.assertEqual(gq.job_state(["START c 3.8", "EXIT 1 after 9s"], 10), "FAILED")

    def test_start_without_exit_recent_is_running(self):
        self.assertEqual(gq.job_state(["START c 3.8", "working"], 600), "RUNNING")

    def test_start_without_exit_over_2h_is_stale(self):
        self.assertEqual(gq.job_state(["START gpt-mutation-trendline-core-1031 gpt-oss", "partial"], 3 * 3600), "STALE")

    def test_skip_and_claim_failures_never_look_done(self):
        self.assertEqual(gq.job_state(["SKIP c: state done"], 10), "SKIPPED")
        self.assertEqual(gq.job_state(["CLAIM FAILED: c: push rejected"], 10), "FAILED")

    def test_status_prints_state_per_log(self):
        import io, contextlib, os
        with tempfile.TemporaryDirectory() as t:
            stuck = Path(t) / "gpt-mutation-trendline-core-1031.log"
            stuck.write_text("START gpt-mutation-trendline-core-1031 gpt-oss-120b-medium\npartial\n", encoding="utf-8")
            old = stuck.stat().st_mtime - 3 * 3600
            os.utime(stuck, (old, old))
            (Path(t) / "ok.log").write_text("START ok 3.8\nEXIT 0 after 4s\n", encoding="utf-8")
            buf = io.StringIO()
            with mock.patch.dict("os.environ", {"MTS_GQ_ROOT": t}), contextlib.redirect_stdout(buf):
                self.assertEqual(gq.main(["status"]), 0)
        out = buf.getvalue()
        self.assertIn("gpt-mutation-trendline-core-1031 | STALE |", out)
        self.assertIn("ok | DONE |", out)


class FetchOriginTest(unittest.TestCase):
    """gemini-queue-parallel-runs-fight-over-gi: parallel runs retry a 'cannot lock ref' fetch instead of failing."""
    LOCK = cp(1, "error: cannot lock ref 'refs/remotes/origin/fast-track': is at x but expected y")

    def test_retries_a_ref_lock_then_succeeds(self):
        calls = []

        def fake_git(*a, **kw):
            calls.append(a)
            return self.LOCK if len(calls) < 3 else cp(0)
        with mock.patch.object(gq, "git", side_effect=fake_git):
            r = gq.fetch_origin(sleep=lambda s: None)
        self.assertEqual((r.returncode, len(calls)), (0, 3))

    def test_other_error_returns_at_once(self):
        with mock.patch.object(gq, "git", return_value=cp(128, "fatal: unable to access")) as g:
            r = gq.fetch_origin(sleep=lambda s: None)
        self.assertEqual((r.returncode, g.call_count), (128, 1))

    def test_gives_up_after_6_lock_errors(self):
        with mock.patch.object(gq, "git", return_value=self.LOCK) as g:
            r = gq.fetch_origin(sleep=lambda s: None)
        self.assertEqual((r.returncode, g.call_count), (1, 6))


if __name__ == "__main__":
    unittest.main()


class NoLocalAgyTest(unittest.TestCase):
    """JIS-DESKTOP 2026-11-12: no agy + a STALE card = exit 0 and an empty log. Now: SKIP is printed, and no agy hands off to the NUC."""

    def test_no_agy_hands_specs_to_nuc_task(self):
        import nuc_lab
        with mock.patch.object(gq, "AGY", Path("Z:/none/agy.exe")), mock.patch.object(nuc_lab, "run", return_value=0) as run, \
                mock.patch.object(gq, "run_job") as rj:
            self.assertEqual(gq.main(["run", "c1:low"]), 0)
        run.assert_called_once_with("gemini-task", ["c1:low"])
        rj.assert_not_called()

    def test_skip_is_printed_not_silent(self):
        import io, contextlib
        with tempfile.TemporaryDirectory() as t, mock.patch.dict("os.environ", {"MTS_GQ_ROOT": t}), \
                mock.patch.object(gq, "git", return_value=cp(0)), mock.patch.object(gq, "card_gate", return_value=(False, "state ready/STALE:x")):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                gq.run_job("c1", "low")
        self.assertIn("SKIP c1: state ready/STALE:x", buf.getvalue())
