"""Spec tests for gemini_queue claim handling, written from the claim_with_retry / claim_holder docstrings (f724f4eeb)."""
import socket
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import gemini_queue as gq  # noqa: E402


def cp(rc, out="", err=""):
    return subprocess.CompletedProcess([], rc, stdout=out, stderr=err)


def claim(results):
    with mock.patch.object(gq, "sh", side_effect=results) as sh:
        r = gq.claim_with_retry(Path("."), "card", tries=3, sleep=lambda s: None)
    return r, sh.call_count


class ClaimSpec(unittest.TestCase):
    def test_own_host_holder_is_ok(self):
        me = socket.gethostname()
        r, n = claim([cp(1, "", f"already claimed by {me.upper()}")])
        self.assertEqual(r, ("ok", ""))
        self.assertEqual(n, 1)

    def test_other_host_holder_skips_at_once(self):
        r, n = claim([cp(1, "", "already claimed by NO-SUCH-STATION-X")])
        self.assertEqual(r[0], "skip")
        self.assertEqual(n, 1)

    def test_timeout_fails_at_once(self):
        r, n = claim([cp(124, "", "")])
        self.assertEqual(r[0], "fail")
        self.assertEqual(n, 1)

    def test_not_a_race_fails_at_once(self):
        r, n = claim([cp(1, "", "push failed, not a race")])
        self.assertEqual(r[0], "fail")
        self.assertEqual(n, 1)

    def test_race_retries_then_succeeds(self):
        r, n = claim([cp(1, "", "rejected"), cp(0)])
        self.assertEqual(r, ("ok", ""))
        self.assertEqual(n, 2)

    def test_holder_free_and_held(self):
        self.assertEqual(gq.claim_holder("c", [("other", {"host": "H"})]), "")
        self.assertEqual(gq.claim_holder("c", [("c", {"host": "H"})]), "H")


if __name__ == "__main__":
    unittest.main()
