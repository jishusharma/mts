"""Cache-discipline test (SCHEDULER_PLAN s7): the worker prefix must be byte-stable across invocations.

Fails if the prefix contains a timestamp/date, hostname, CRLF or trailing whitespace, or if two invocations of the
wrapper's prefix writer (`run_worker.py --print-prefix-hash`) return different hashes.
Run: python -m unittest tests.test_worker_prefix_hash   (repo root)
"""
import hashlib
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
WORKER = REPO / "scripts" / "sched" / "run_worker.py"
PREFIX = REPO / "MyTradingSys" / "system" / "sched" / "worker_prefix.md"
VOLATILE = re.compile(r"\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}|\d{8}T\d{6}Z|JIS-NB|\bnow\(\)")


def prefix_hash(extra=()):
    p = subprocess.run([sys.executable, str(WORKER), "--print-prefix-hash", *extra],
                       capture_output=True, text=True, cwd=REPO)
    return p.returncode, p.stdout.strip()


class WorkerPrefixHash(unittest.TestCase):
    def test_two_invocations_same_hash(self):
        c1, h1 = prefix_hash()
        time.sleep(1.1)  # a clock in the prefix would differ across a second boundary
        c2, h2 = prefix_hash()
        self.assertEqual((c1, c2), (0, 0))
        self.assertRegex(h1, r"^[0-9a-f]{64}$")
        self.assertEqual(h1, h2)

    def test_hash_is_sha256_of_file_bytes(self):
        _, h = prefix_hash()
        self.assertEqual(h, hashlib.sha256(PREFIX.read_bytes()).hexdigest())

    def test_prefix_file_has_no_volatile_content(self):
        data = PREFIX.read_bytes()
        self.assertNotIn(b"\r", data)
        text = data.decode("utf-8")
        self.assertIsNone(VOLATILE.search(text), VOLATILE.search(text))
        for n, line in enumerate(text.split("\n"), 1):
            self.assertEqual(line, line.rstrip(), f"trailing whitespace line {n}")
        self.assertTrue(text.endswith("=== RUN ===\n"))

    def test_gitattributes_pins_the_prefix_to_lf(self):
        # core.autocrlf=true checks the prefix out as CRLF on Windows; run_worker then refuses it and the scheduled
        # worker never runs there. The attribute makes the checkout byte-identical on every host.
        attrs = (REPO / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("MyTradingSys/system/sched/worker_prefix.md text eol=lf", attrs)

    def test_timestamp_in_prefix_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            bad = pathlib.Path(d) / "bad_prefix.md"
            bad.write_bytes(PREFIX.read_bytes() + b"generated 2026-10-03T01:02:03Z\n")
            code, _ = prefix_hash(["--prefix-file", str(bad)])
            self.assertNotEqual(code, 0, "wrapper must refuse a prefix containing a timestamp")


if __name__ == "__main__":
    unittest.main()
