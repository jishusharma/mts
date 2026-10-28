"""dax_engine.py passes -Dmts.spikeFade only on request (card tom-encode-spike-fade)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "MyTradingSys" / "backtest"))
import dax_engine  # noqa: E402


class FlagPassThrough(unittest.TestCase):
    def test_default_off(self):
        cmd = dax_engine.java_cmd("cp", "GER40", "datafeed.SnapAt", ["a"])
        self.assertFalse(any("spikeFade" in c for c in cmd))

    def test_on(self):
        cmd = dax_engine.java_cmd("cp", "GER40", "datafeed.SnapAt", ["a"], spike_fade=True)
        self.assertIn("-Dmts.spikeFade=true", cmd)
        self.assertLess(cmd.index("-Dmts.spikeFade=true"), cmd.index("-cp"))


if __name__ == "__main__":
    unittest.main()
