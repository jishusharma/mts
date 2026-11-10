"""Gate child run_all_tests.py must survive non-UTF-8 bytes (0x98) from child processes."""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_all_tests as rat  # noqa: E402

_REAL_RUN = subprocess.run
_CHILD = "import sys; sys.stdout.buffer.write(bytes([97, 98, 0x98, 99, 10])); sys.stderr.buffer.write(bytes([101, 0x98, 10]))"


class _Patched:
    """Replace every subprocess.run in run_all_tests with a child that emits byte 0x98."""
    def __enter__(self):
        self.calls = []

        def fake(cmd, *a, **kw):
            self.calls.append(kw)
            return _REAL_RUN([sys.executable, "-c", _CHILD], *a, **kw)
        self._orig = rat.subprocess.run
        rat.subprocess.run = fake
        return self

    def __exit__(self, *exc):
        rat.subprocess.run = self._orig


class GateReaderEncoding(unittest.TestCase):
    def test_git_out_survives_0x98(self):
        with _Patched():
            out = rat._git_out(".", "log")
        self.assertIn("ab", out)

    def test_short_sha_survives_0x98(self):
        saved = list(rat._SHA)
        del rat._SHA[:]
        try:
            with _Patched():
                self.assertNotEqual(rat._short_sha(), "?")
        finally:
            rat._SHA[:] = saved

    def test_mvn_version_probe_has_explicit_decode(self):
        with _Patched() as p:
            try:
                rat.run_mvn()
            except Exception:
                pass
        probe = p.calls[0]
        self.assertEqual(probe.get("errors"), "replace")
        self.assertTrue(probe.get("encoding"))


if __name__ == "__main__":
    unittest.main()
