"""scripts/dev/lease.py (TRAFFIC_CONTROLLER.md Part A): a singleton role (Pipeliner) cannot run as two instances.
Two clones of one bare 'origin' play two machines. Written to fail on the code before lease.py existed: there was no
lease, so two Pipeliners on two machines both ran (2026-10-18: JIS-NUC ebfffe68/0efac858 and DESKTOP-F7IU69N 41c8a303)."""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEV = REPO / "scripts" / "dev"
sys.path.insert(0, str(DEV))
import lease  # noqa: E402  (absent before this change: every test below fails on the old tree)

FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0


def git(d, *a, stdin=None):
    r = subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", *a],
                       input=stdin.encode("utf-8") if isinstance(stdin, str) else stdin,
                       capture_output=True, text=False, creationflags=FLAGS)
    if r.returncode:
        raise RuntimeError(r.stderr.decode("utf-8", errors="replace"))
    return r.stdout.decode("utf-8", errors="replace").strip()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        t = Path(self.tmp.name)
        self.origin = t / "origin.git"
        git(t, "init", "-q", "--bare", str(self.origin))
        git(self.origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
        b = git(self.origin, "hash-object", "-w", "--stdin", stdin="x\n")
        tr = git(self.origin, "mktree", stdin=f"100644 blob {b}\tREADME.md\n")
        c = git(self.origin, "commit-tree", tr, "-m", "seed")
        git(self.origin, "update-ref", "refs/heads/fast-track", c)
        self.a = t / "nuc"
        self.b = t / "lenovo"
        for d in (self.a, self.b):
            git(t, "clone", "-s", "-q", "-b", "fast-track", str(self.origin), str(d))
            git(d, "config", "user.email", "t@t")
            git(d, "config", "user.name", "t")
        self.ident_a = {"MTS_LEASE_HOST": "JIS-NUC", "MTS_LEASE_SESSION": "sess-a", "MTS_ACCOUNT": "sharma",
                        "MTS_LEASE_HOME": str(t / "home_nuc")}
        self.ident_b = {"MTS_LEASE_HOST": "DESKTOP-F7IU69N", "MTS_LEASE_SESSION": "sess-b", "MTS_ACCOUNT": "?",
                        "MTS_LEASE_HOME": str(t / "home_lenovo")}

    def as_(self, ident):
        lease._LOCAL.env = ident

    def tearDown(self):
        lease._LOCAL.env = None

    def trunk_lease(self, role="Pipeliner"):
        git(self.a, "fetch", "-q", "origin")
        return json.loads(git(self.a, "show", f"origin/fast-track:{lease.rel_path(role)}"))

    def cli(self, cwd, ident, *args, role=None):
        env = {k: v for k, v in os.environ.items() if k not in ("PYTEST_CURRENT_TEST", "CLAUDE_CODE_SESSION_ID", "MTS_ROLE")}
        env.update(ident)
        env["MTS_LEASE_TEST_FORCE"] = "1"
        if role:
            env["MTS_ROLE"] = role
        return subprocess.run([sys.executable, *args], cwd=str(cwd), env=env, capture_output=True, text=True,
                              creationflags=FLAGS)


class Race(Base):
    def test_two_simultaneous_acquirers_exactly_one_wins(self):
        """Both read the same trunk tip (barrier before push), both push; exactly one lands, the other is refused."""
        barrier = threading.Barrier(2, timeout=30)
        results = {}

        def run(name, repo, ident):
            self.as_(ident)
            try:
                hooks = {"before_push": lambda attempt: barrier.wait() if attempt == 1 else None}
                results[name] = ("ok", lease.acquire(repo, "Pipeliner", hooks=hooks))
            except lease.LeaseError as e:
                results[name] = (e.code, str(e))
            finally:
                lease._LOCAL.env = None
        ts = [threading.Thread(target=run, args=("a", self.a, self.ident_a)),
              threading.Thread(target=run, args=("b", self.b, self.ident_b))]
        for t in ts:
            t.start()
        for t in ts:
            t.join(60)
        outcomes = sorted(str(v[0]) for v in results.values())
        self.assertEqual(outcomes, [str(lease.REFUSED), "ok"], results)
        winner = next(n for n, v in results.items() if v[0] == "ok")
        want = (self.ident_a if winner == "a" else self.ident_b)["MTS_LEASE_HOST"]
        self.assertEqual(self.trunk_lease()["holder"]["host"], want)
        loser = next(v for v in results.values() if v[0] != "ok")
        self.assertIn("held by", loser[1])

    def test_second_machine_refused_while_first_holds(self):
        self.as_(self.ident_a)
        lease.acquire(self.a, "Pipeliner")
        self.as_(self.ident_b)
        with self.assertRaises(lease.Refused):
            lease.acquire(self.b, "Pipeliner")


class Stale(Base):
    def test_takeover_after_expiry_plus_skew(self):
        self.as_(self.ident_a)
        t0 = time.time()
        lease.acquire(self.a, "Pipeliner", now_fn=lambda: t0 - lease.TTL - lease.SKEW - 60)  # holder died long ago
        self.as_(self.ident_b)
        got = lease.acquire(self.b, "Pipeliner")
        self.assertEqual(got["holder"]["host"], "DESKTOP-F7IU69N")
        self.assertEqual(got["took_over_from"], "JIS-NUC/" + lease.hashlib.sha256(b"sess-a").hexdigest()[:12])
        # the old holder comes back: it lost, every write path refuses
        self.as_(self.ident_a)
        with self.assertRaises(lease.Refused):
            lease.require(self.a, "Pipeliner")
        with self.assertRaises(lease.Refused):
            lease.renew(self.a, "Pipeliner")

    def test_no_takeover_inside_skew(self):
        self.as_(self.ident_a)
        t0 = time.time()
        lease.acquire(self.a, "Pipeliner", now_fn=lambda: t0 - lease.TTL - 60)   # expired 1 min ago: within SKEW
        self.as_(self.ident_b)
        with self.assertRaises(lease.Refused):
            lease.acquire(self.b, "Pipeliner")

    def test_release_frees_it(self):
        self.as_(self.ident_a)
        lease.acquire(self.a, "Pipeliner")
        lease.release(self.a, "Pipeliner")
        self.assertEqual(self.trunk_lease()["state"], "released")
        self.as_(self.ident_b)
        self.assertEqual(lease.acquire(self.b, "Pipeliner")["holder"]["host"], "DESKTOP-F7IU69N")

    def test_require_renews_when_low(self):
        self.as_(self.ident_a)
        t0 = time.time()
        first = lease.acquire(self.a, "Pipeliner", now_fn=lambda: t0 - (lease.TTL - lease.RENEW_BELOW) - 120)
        got = lease.require(self.a, "Pipeliner")
        self.assertGreater(got["expires"], first["expires"])
        self.assertEqual(got["nonce"], first["nonce"])


class FailClosed(Base):
    def test_offline_refuses(self):
        git(self.a, "remote", "set-url", "origin", str(Path(self.tmp.name) / "nowhere.git"))
        self.as_(self.ident_a)
        with self.assertRaises(lease.Unreachable):
            lease.acquire(self.a, "Pipeliner")
        r = self.cli(self.a, self.ident_a, str(DEV / "lease.py"), "guard", role="Pipeliner")
        self.assertEqual(r.returncode, lease.UNREACHABLE, r.stderr)

    def test_offline_after_holding_still_refuses(self):
        self.as_(self.ident_a)
        lease.acquire(self.a, "Pipeliner")
        git(self.a, "remote", "set-url", "origin", str(Path(self.tmp.name) / "nowhere.git"))
        with self.assertRaises(lease.Unreachable):
            lease.require(self.a, "Pipeliner")

    def test_malformed_lease_is_ambiguous(self):
        p = self.a / lease.rel_path("Pipeliner")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{not json")
        git(self.a, "add", "-A")
        git(self.a, "commit", "-qm", "broken lease")
        git(self.a, "push", "-q", "origin", "HEAD:refs/heads/fast-track")
        self.as_(self.ident_b)
        with self.assertRaises(lease.Unreachable):
            lease.acquire(self.b, "Pipeliner")

    def test_push_error_that_did_not_land_is_not_a_renew(self):
        """Review (Sonnet #1): renew kept the nonce, so an unlanded push looked landed and the holder trusted 45 more min."""
        self.as_(self.ident_a)
        lease.acquire(self.a, "Pipeliner")
        real = lease.push
        lease.push = lambda repo, commit: "error"
        try:
            with self.assertRaises(lease.Unreachable):
                lease.renew(self.a, "Pipeliner")
        finally:
            lease.push = real

    def test_no_session_id_refused(self):
        """Review (Sonnet #3): two runners without a session id on one host shared HOST/nosession and both held it."""
        self.as_({k: v for k, v in self.ident_a.items() if k != "MTS_LEASE_SESSION"})
        with self.assertRaises(lease.Unreachable):
            lease.acquire(self.a, "Pipeliner")

    def test_release_by_non_holder_refused(self):
        self.as_(self.ident_a)
        lease.acquire(self.a, "Pipeliner")
        self.as_(self.ident_b)
        with self.assertRaises(lease.Refused):
            lease.release(self.b, "Pipeliner")
        self.assertEqual(self.trunk_lease()["state"], "held")

    def test_held_without_holder_is_ambiguous(self):
        p = self.a / lease.rel_path("Pipeliner")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"state": "held", "expires": 0}))
        git(self.a, "add", "-A")
        git(self.a, "commit", "-qm", "half lease")
        git(self.a, "push", "-q", "origin", "HEAD:refs/heads/fast-track")
        self.as_(self.ident_b)
        with self.assertRaises(lease.Unreachable):
            lease.acquire(self.b, "Pipeliner")

    def test_not_a_singleton_role(self):
        with self.assertRaises(lease.LeaseError):
            lease.acquire(self.a, "MTS_Doctor")


class SameHost(Base):
    def test_same_host_duplicate_refused_by_local_lock_even_offline(self):
        ident_a2 = {**self.ident_a, "MTS_LEASE_SESSION": "sess-a2"}   # second session, same machine, same lock dir
        self.as_(self.ident_a)
        lease.acquire(self.a, "Pipeliner")
        git(self.b, "remote", "set-url", "origin", str(Path(self.tmp.name) / "nowhere.git"))
        self.as_(ident_a2)
        with self.assertRaises(lease.Refused) as cm:
            lease.acquire(self.b, "Pipeliner")
        self.assertIn("same-host duplicate", str(cm.exception))

    def test_same_session_reacquire_is_a_renew(self):
        self.as_(self.ident_a)
        one = lease.acquire(self.a, "Pipeliner")
        two = lease.acquire(self.a, "Pipeliner")
        self.assertEqual(one["nonce"], two["nonce"])


class Wiring(Base):
    def test_desk_and_sync_refuse_a_pipeliner_without_the_lease(self):
        r = self.cli(self.b, self.ident_b, str(DEV / "desk.py"), "sweep", "--no-fetch", role="Pipeliner")
        self.assertEqual(r.returncode, lease.REFUSED, r.stdout + r.stderr)
        self.assertIn("LEASE REFUSED", r.stderr)
        r = self.cli(self.b, self.ident_b, str(DEV / "sync.py"), "ship", role="Pipeliner")
        self.assertEqual(r.returncode, lease.REFUSED, r.stdout + r.stderr)
        r = self.cli(self.b, self.ident_b, str(DEV / "sync.py"), "claim", "x", role="Pipeliner")
        self.assertEqual(r.returncode, lease.REFUSED, r.stdout + r.stderr)

    def test_holder_passes_guard_and_other_machine_does_not(self):
        r = self.cli(self.a, self.ident_a, str(DEV / "lease.py"), "acquire", "Pipeliner")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.cli(self.a, self.ident_a, str(DEV / "lease.py"), "guard", role="Pipeliner")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.cli(self.b, self.ident_b, str(DEV / "lease.py"), "acquire", "Pipeliner")
        self.assertEqual(r.returncode, lease.REFUSED, r.stderr)
        self.assertIn("JIS-NUC", r.stderr)

    def test_role_spelling_does_not_skip_the_guard(self):
        r = self.cli(self.b, self.ident_b, str(DEV / "desk.py"), "sweep", "--no-fetch", role="pipeliner")
        self.assertEqual(r.returncode, lease.REFUSED, r.stdout + r.stderr)

    def test_email_shaped_account_never_reaches_trunk(self):
        self.as_({**self.ident_a, "MTS_ACCOUNT": "someone@example.com"})
        lease.acquire(self.a, "Pipeliner")
        self.assertEqual(self.trunk_lease()["holder"]["account"], "?")
        self.assertNotIn("@example", git(self.a, "log", "-1", "--format=%B", "origin/fast-track"))

    def test_non_singleton_session_unaffected(self):
        r = self.cli(self.b, self.ident_b, str(DEV / "lease.py"), "guard", role="MTS_Doctor")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_banner_shows_holder(self):
        import role_loader
        self.as_(self.ident_a)
        lease.acquire(self.a, "Pipeliner")
        git(self.b, "fetch", "-q", "origin")
        self.assertIn("held by JIS-NUC/sharma", role_loader.lease_suffix("Pipeliner", self.b))
        self.assertEqual(role_loader.lease_suffix("Eagle_Eyes", self.b), "")


if __name__ == "__main__":
    unittest.main()
