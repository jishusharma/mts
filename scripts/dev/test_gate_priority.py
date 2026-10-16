"""The gate must run below normal priority on Windows so it never starves the live loop (2026-10-16 CPU saturation)."""
import ctypes
import os
import subprocess
import sys
import unittest

CODE = (
    "import sys, ctypes; sys.path.insert(0, 'scripts/dev'); import run_all_tests as r;"
    "from ctypes import wintypes; k = ctypes.WinDLL('kernel32'); k.GetCurrentProcess.restype = wintypes.HANDLE;"
    "k.GetPriorityClass.argtypes = [wintypes.HANDLE]; before = k.GetPriorityClass(k.GetCurrentProcess());"
    "ok = r.lower_priority(); print(before, k.GetPriorityClass(k.GetCurrentProcess()))"
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


AFF = (
    "import sys, ctypes; sys.path.insert(0, 'scripts/dev'); import run_all_tests as r;"
    "from ctypes import wintypes; k = ctypes.WinDLL('kernel32'); k.GetCurrentProcess.restype = wintypes.HANDLE;"
    "m = ctypes.c_size_t(); s = ctypes.c_size_t();"
    "k.GetProcessAffinityMask.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)];"
    "k.GetProcessAffinityMask(k.GetCurrentProcess(), ctypes.byref(m), ctypes.byref(s)); before = m.value;"
    "r.lower_priority(); k.GetProcessAffinityMask(k.GetCurrentProcess(), ctypes.byref(m), ctypes.byref(s)); print(m.value, before)"
)


@unittest.skipUnless(sys.platform == "win32" and (os.cpu_count() or 1) >= 4, "Windows, >= 4 logical CPUs")
class GateReservesCores(unittest.TestCase):
    """B191: the gate keeps off the top 2 logical CPUs so the live loop's snapshot always has a core."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def run_aff(self, **env):
        e = dict(os.environ, MTS_GATE_PRIORITY="", **env)
        return [int(x) for x in subprocess.run([sys.executable, "-c", AFF], capture_output=True, text=True, cwd=self.root, env=e).stdout.split()]

    def test_top_two_cpus_left_free(self):
        mask, before = self.run_aff(MTS_GATE_RESERVE="2")   # `before` = what this process inherited (the gate may already be pinned)
        self.assertEqual(mask, before & ((1 << ((os.cpu_count() or 1) - 2)) - 1))

    def test_opt_out_keeps_every_cpu(self):
        mask, before = self.run_aff(MTS_GATE_RESERVE="0")
        self.assertEqual(mask, before)


if __name__ == "__main__":
    unittest.main()
