"""Ship train card 3/5: bisect + eject + signal, queue ref names, status wait, and `sync.py ship --train` (default path unchanged)."""
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ship_train as T
import sync


class RefNames(unittest.TestCase):
    def test_queue_ref_from_branch(self):
        self.assertEqual(T.queue_ref("JIS-NB/my-slug"), "queue/JIS-NB/my-slug")
        self.assertEqual(T.queue_ref("queue/h/s"), "queue/h/s")
        self.assertEqual(T.queue_ref("solo", host="H1"), "queue/H1/solo")

    def test_split_ref(self):
        self.assertEqual(T.split_ref("queue/JIS-NB/a/b"), ("JIS-NB", "a/b"))
        for bad in ("queue/onlyhost", "fast-track", "queue//x"):
            with self.assertRaises(ValueError):
                T.split_ref(bad)


class Bisect(unittest.TestCase):
    def setUp(self):
        self.refs = ["queue/h1/good1", "queue/h2/red", "queue/h3/good2"]

    def run_ref(self, ref):
        return (False, "test_x::boom", "https://ci/1") if ref.endswith("/red") else (True, "", "")

    def test_fake_red_ref_ejected_green_refs_land(self):
        batches = []
        res = T.bisect_batch(self.refs, self.run_ref, lambda g: batches.append(list(g)) or True)
        self.assertEqual(list(res["ejected"]), ["queue/h2/red"])
        self.assertEqual(res["ejected"]["queue/h2/red"], ("test_x::boom", "https://ci/1"))
        self.assertEqual(res["green"], ["queue/h1/good1", "queue/h3/good2"])
        self.assertEqual(batches, [res["green"]])     # the rest re-ran without the ejected ref
        self.assertTrue(res["batch_ok"])

    def test_runs_alone_in_parallel(self):
        seen, lock = set(), threading.Lock()
        gate = threading.Barrier(3, timeout=5)        # only passes when all three run at once

        def run_ref(ref):
            gate.wait()
            with lock:
                seen.add(ref)
            return True, "", ""
        T.bisect_batch(self.refs, run_ref, lambda g: True)
        self.assertEqual(seen, set(self.refs))

    def test_nothing_ejected_means_nothing_lands(self):
        res = T.bisect_batch(self.refs, lambda r: (True, "", ""), lambda g: self.fail("no rerun without an eject"))
        self.assertFalse(res["batch_ok"])
        self.assertEqual(res["ejected"], {})

    def test_remainder_still_red_does_not_land(self):
        res = T.bisect_batch(self.refs, self.run_ref, lambda g: False)
        self.assertFalse(res["batch_ok"])

    def test_all_ejected_skips_rerun(self):
        res = T.bisect_batch(["queue/h/a"], lambda r: (False, "t", "l"), lambda g: self.fail("empty rerun"))
        self.assertEqual(res["green"], [])
        self.assertFalse(res["batch_ok"])


class Signal(unittest.TestCase):
    def test_signal_goes_to_host_with_slug_test_and_link(self):
        sent = []
        T.signal_eject("queue/JIS-NB/my-slug", "test_a::t1", "https://x/run/9", send=lambda text, **kw: sent.append((text, kw)) or True)
        text, kw = sent[0]
        self.assertEqual(kw["to"], "JIS-NB")
        for part in ("my-slug", "test_a::t1", "https://x/run/9"):
            self.assertIn(part, text)


class Wait(unittest.TestCase):
    def test_waits_for_fresh_verdict(self):
        rows = [None, {"state": "queued", "t": "20260101T000000Z"}, {"state": "landed", "t": "20250101T000000Z"},
                {"state": "ejected", "t": "20260101T000100Z", "test": "t::x", "link": "L"}]
        out, clock = [], [0.0]
        it = iter(rows)
        v = T.wait_status("queue/h/s", since="20260101T000000Z", fetch=lambda r: next(it), sleep=lambda s: clock.__setitem__(0, clock[0] + s),
                          now_fn=lambda: clock[0], out=out.append)
        self.assertEqual(v, "ejected")
        self.assertIn("t::x", out[0])

    def test_timeout(self):
        clock = [0.0]
        v = T.wait_status("queue/h/s", fetch=lambda r: None, sleep=lambda s: clock.__setitem__(0, clock[0] + s), now_fn=lambda: clock[0],
                          timeout=60, poll=20, out=lambda m: None)
        self.assertEqual(v, "timeout")


def _git(cwd, *a):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.test", *a], cwd=cwd, check=True, capture_output=True, text=True)


def _rev(origin, ref):
    return subprocess.run(["git", "-C", str(origin), "rev-parse", ref], capture_output=True, text=True).stdout.strip()


class StatusAndShip(unittest.TestCase):
    """Real git: status file round trip on a bare mts-signals origin; ship(push_ref=...) leaves the trunk alone."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.keep = {k: os.environ.get(k) for k in ("MTS_SIGNALS_HOME", "MTS_SIGNALS_ORIGIN", "GIT_CEILING_DIRECTORIES")}
        os.environ["GIT_CEILING_DIRECTORIES"] = os.path.realpath(str(self.tmp.parent)).replace(os.sep, "/")
        self.origin = self.tmp / "origin.git"
        _git(self.tmp, "init", "-q", "--bare", "-b", sync.TRUNK, str(self.origin))
        os.environ["MTS_SIGNALS_ORIGIN"] = str(self.origin)
        os.environ["MTS_SIGNALS_HOME"] = str(self.tmp / "hub")
        self.work = self.tmp / "work"
        _git(self.tmp, "clone", "-q", str(self.origin), str(self.work))
        (self.work / "a.txt").write_text("1\n")
        _git(self.work, "add", "-A")
        _git(self.work, "commit", "-q", "-m", "base")
        _git(self.work, "push", "-q", "origin", "HEAD:refs/heads/" + sync.TRUNK)
        _git(self.work, "fetch", "-q", "origin")
        (self.work / "b.txt").write_text("2\n")
        _git(self.work, "add", "-A")
        _git(self.work, "commit", "-q", "-m", "work", "-m", "Result: x")

    def tearDown(self):
        for k, v in self.keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_status_roundtrip(self):
        ref = "queue/h1/slug-a"
        self.assertTrue(T.set_status(ref, "ejected", "t::x", "L"))
        os.environ["MTS_SIGNALS_HOME"] = str(self.tmp / "hub2")      # a second machine reads it from origin
        st = T.read_status(ref)
        self.assertEqual((st["state"], st["test"], st["link"]), ("ejected", "t::x", "L"))

    def test_ship_train_pushes_queue_ref_not_trunk(self):
        before = _rev(self.origin, sync.TRUNK)
        pushed = sync.ship(self.work, gate=lambda *a, **k: None, docs_gate=None, push_ref="queue/H/slug")
        self.assertIsInstance(pushed, sync.Pushed)
        self.assertEqual(_rev(self.origin, sync.TRUNK), before)
        self.assertEqual(_rev(self.origin, "queue/H/slug"), pushed.sha)

    def test_ship_default_still_pushes_trunk(self):
        pushed = sync.ship(self.work, gate=lambda *a, **k: None, docs_gate=None)
        self.assertEqual(_rev(self.origin, sync.TRUNK), pushed.sha)


if __name__ == "__main__":
    unittest.main()
