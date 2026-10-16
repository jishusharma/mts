"""The gate must run below normal priority on Windows so it never starves the live loop (2026-10-16 CPU saturation)."""
import ctypes
import os
import subprocess
import sys
import unittest

CODE = (
    "import sys, ctypes; sys.path.insert(0, 'scripts/dev'); import run_all_tests as r;"
    "k = ctypes.windll.kernel32; before = k.GetPriorityClass(k.GetCurrentProcess()); r.lower_priority();"
    "print(before, k.GetPriorityClass(k.GetCurrentProcess()))"
)


@unittest.skipUnless(sys.platform == "win32", "Windows only")
class GatePriority(unittest.TestCase):
    def test_lowered_to_below_normal(self):
        env = dict(os.environ, MTS_GATE_PRIORITY="")
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        out = subprocess.run([sys.executable, "-c", CODE], capture_output=True, text=True, cwd=root, env=env).stdout.split()
        self.assertEqual(out[1], str(0x4000), out)

    def test_opt_out(self):
        env = dict(os.environ, MTS_GATE_PRIORITY="normal")
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        out = subprocess.run([sys.executable, "-c", CODE], capture_output=True, text=True, cwd=root, env=env).stdout.split()
        self.assertEqual(out[0], out[1])


if __name__ == "__main__":
    unittest.main()
