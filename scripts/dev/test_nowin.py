import os
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nowin


class NoWin(unittest.TestCase):
    def setUp(self):
        self.orig = subprocess.Popen.__init__

    def tearDown(self):
        subprocess.Popen.__init__ = self.orig
        subprocess.Popen._mts_nowin = False

    def test_adds_flag_when_forced_and_keeps_explicit(self):
        seen = []
        subprocess.Popen.__init__ = lambda self, *a, **kw: seen.append(kw.get("creationflags"))
        subprocess.Popen._mts_nowin = False
        self.assertTrue(nowin.install(force=True))
        subprocess.Popen(["x"])
        subprocess.Popen(["x"], creationflags=7)
        self.assertEqual(seen, [0x08000000, 7])

    def test_inactive_under_plain_python(self):
        os.environ.pop("MTS_NOWIN", None)
        self.assertFalse(nowin.wanted())

    def test_never_active_off_windows(self):
        # Production callers use install() without force: a Linux/macOS process (cloud container, CI) must never get the shim,
        # because POSIX Popen raises ValueError for any creationflags. This is why test_real_child_runs may be Windows-only.
        before = subprocess.Popen.__init__
        with mock.patch.dict(os.environ, {"MTS_NOWIN": "1"}), mock.patch.object(sys, "platform", "linux"):
            self.assertFalse(nowin.wanted())
            self.assertFalse(nowin.install())
        self.assertIs(subprocess.Popen.__init__, before)

    @unittest.skipUnless(sys.platform == "win32", "CREATE_NO_WINDOW is Windows-only")
    def test_real_child_runs(self):
        nowin.install(force=True)
        r = subprocess.run([sys.executable, "-c", "print(1)"], capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "1")


if __name__ == "__main__":
    unittest.main()
