"""feed-watchdog.ps1 regression (2026-10-16): a Python-escaped backslash-r turned `$root\runtime_data` into a carriage return
and the deployed watchdog wrote to a bogus path. No control characters allowed; the orderflow writer must be started
and a hung one (alive, no csv for 10 min) killed."""
import pathlib
import unittest

SRC = (pathlib.Path(__file__).resolve().parents[1] / "live" / "feed-watchdog.ps1").read_bytes()


class FeedWatchdogScript(unittest.TestCase):
    def test_no_control_characters(self):
        bad = sorted({c for c in SRC if c < 32 and c not in (9, 10, 13)} | ({13} if b"\r\n" not in SRC and 13 in SRC else set()))
        self.assertEqual(bad, [])

    def test_paths_intact(self):
        t = SRC.decode("utf-8")
        for p in (r"$root\runtime_data\orderflow_live.err.txt", r"$root\MyTradingSys\runtime\orderflow_live\*.csv",
                  r"$root\runtime_data\orderflow_watchdog_kill.txt"):
            self.assertIn(p, t)

    def test_starts_and_unsticks_orderflow_writer(self):
        t = SRC.decode("utf-8")
        self.assertIn("fabio.orderflow_live", t)
        self.assertIn("$csvAge -gt 600", t)
        self.assertIn("Stop-Process -Id $of.ProcessId", t)


if __name__ == "__main__":
    unittest.main()
