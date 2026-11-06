"""Spec test for boot_audit.py (the 2026-11-06 slow-boot audit). Run: python scripts/dev/test_boot_audit.py

Pins: authorised MTS items are KEEP, an unauthorised MTS task or Run value is REMOVE, AIBridge-Agent is DELAY (needed, not
authorised), anything not MTS is never touched by --fix, and the c_drive_guard logon run waits before its heavy cleanup.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boot_audit as ba  # noqa: E402


def row(kind, name, cmd="", done=False, raw=None):
    owner, verdict, reason, ask = ba.classify(kind, name, cmd)
    return {"kind": kind, "name": name, "cmd": cmd, "owner": owner, "verdict": verdict, "reason": reason, "ask": ask,
            "done": done or verdict == "KEEP", "raw": raw or {"hive": "HKCU", "key": "x"}}


class TestClassify(unittest.TestCase):
    def test_authorised_mts_tasks_are_keep(self):
        for n in ("MTS-CBP-Ingestion", "MTS-WorktreeMaint-JIS-NB", "MTS-SuccWake-C"):
            self.assertEqual(ba.classify("task", n)[:2], ("MTS", "KEEP"), n)

    def test_unauthorised_mts_task_is_remove(self):
        for n in ("MTS-CodexLab", "MTS-DailyHygiene", "MTS-AutoDeploy", "MTS-NUC-Worker"):
            self.assertEqual(ba.classify("task", n)[:2], ("MTS", "REMOVE"), n)

    def test_aibridge_agent_is_delay_not_remove(self):
        self.assertEqual(ba.classify("task", "AIBridge-Agent")[:2], ("MTS", "DELAY"))

    def test_authorised_run_values_keep_other_mts_run_removed(self):
        self.assertEqual(ba.classify("run", "MTSTempGuard")[:2], ("MTS", "KEEP"))
        self.assertEqual(ba.classify("run", "MTSLogonWake")[:2], ("MTS", "KEEP"))
        cmd = r'python C:\Users\x\IdeaProjects\BinanceDataFeed\scripts\dev\supervisor.py wait'
        self.assertEqual(ba.classify("run", "MTSSupervisor", cmd)[:2], ("MTS", "REMOVE"))

    def test_third_party_is_never_mts_and_heavy_ones_are_flagged_ask(self):
        o, v, _, ask = ba.classify("run", "Docker Desktop", r"C:\Program Files\Docker\Docker\Docker Desktop.exe")
        self.assertEqual((o, v, ask), ("other", "KEEP", True))
        self.assertEqual(ba.classify("task", "ZoomUpdateTaskUser-S-1")[:2], ("other", "KEEP"))
        self.assertEqual(ba.classify("run", "SecurityHealth", r"C:\WINDOWS\system32\SecurityHealthSystray.exe")[:3:2][0], "other")


class TestFixPlan(unittest.TestCase):
    def test_fix_only_acts_on_mts_remove_and_pending_delay(self):
        rows = [row("task", "MTS-CodexLab"), row("task", "AIBridge-Agent"), row("task", "MTS-CBP-Ingestion"),
                row("run", "Docker Desktop", "docker.exe"), row("task", "ZoomUpdateTaskUser-S-1"),
                row("run", "MTSBad", r"python C:\BinanceDataFeed\scripts\dev\x.py")]
        acts = [(a, n) for a, n, _ in ba.plan_fix(rows)]
        self.assertEqual(sorted(acts), sorted([("remove_task", "MTS-CodexLab"), ("delay_task", "AIBridge-Agent"), ("remove_run", "MTSBad")]))

    def test_already_delayed_item_is_not_touched_again(self):
        self.assertEqual(ba.plan_fix([row("task", "AIBridge-Agent", done=True)]), [])


class TestGuardLogonDelay(unittest.TestCase):
    def test_logon_waits_before_the_heavy_cleanup(self):
        import c_drive_guard as g
        calls = []
        orig_logon, orig_sleep = g.logon, g.time.sleep
        try:
            g.logon = lambda repos=(): calls.append("logon") or 0
            g.time.sleep = lambda s: calls.append(("sleep", s))
            g.main(["logon"])
        finally:
            g.logon, g.time.sleep = orig_logon, orig_sleep
        self.assertEqual(calls[0][0], "sleep")
        self.assertGreaterEqual(calls[0][1], 60)
        self.assertEqual(calls[1], "logon")


if __name__ == "__main__":
    unittest.main()
