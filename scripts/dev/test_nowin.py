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
        # B193: the gate itself runs hidden on the live host (AutoDeploy), where the real console probe is True and this test
        # went red on every deploy since B190b; pin the probe so the result no longer depends on who launched the gate.
        with mock.patch.object(nowin, "_console_hidden", return_value=False):
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

    def test_hidden_console_counts_as_windowless(self):
        # B190: wscript launchers run python.exe with a hidden console; the shim must engage there, not only under pythonw.
        os.environ.pop("MTS_NOWIN", None)
        with mock.patch.object(sys, "platform", "win32"), mock.patch.object(nowin, "_console_hidden", return_value=True):
            self.assertTrue(nowin.wanted())
        with mock.patch.object(sys, "platform", "win32"), mock.patch.object(nowin, "_console_hidden", return_value=False):
            self.assertFalse(nowin.wanted())

    def test_no_console_counts_as_windowless(self):
        # A python.exe with no console at all (detached, or started by a GUI app) opens a visible console for every git child.
        if sys.platform != "win32":
            self.skipTest("Windows console API")
        with mock.patch("ctypes.windll.kernel32.GetConsoleWindow", return_value=0):
            self.assertTrue(nowin._console_hidden())

    def test_git_callers_install_the_shim(self):
        d = os.path.dirname(os.path.abspath(__file__))
        for name in ("make_status.py", "testnet_canary.py", "auto_deploy.py", "live_mirror.py", "shot.py",
                     "stop_guard.py"):
            self.assertIn("nowin.install(", open(os.path.join(d, name), encoding="utf-8").read(), name)

    def test_backup_snapshot_forces_the_shim(self):
        # B190: MTS-Backup runs python.exe through launch-backup.vbs, never pythonw, so plain install() was a no-op there.
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_snapshot.py"), encoding="utf-8").read()
        self.assertIn("nowin.install(force=", src)

    def test_signal_hook_never_detaches_its_console(self):
        # B192: DETACHED_PROCESS makes Windows ignore CREATE_NO_WINDOW; every git.exe of the hook sender then flashed a window.
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mts_signal.py"), encoding="utf-8").read()
        self.assertNotIn("0x00000008", src)
        self.assertIn("flags = 0x08000000 if os.name", src)
        self.assertIn("creationflags=0x08000000 if os.name", src)


if __name__ == "__main__":
    unittest.main()
