"""copy_fork: the operator's copy-paste fork keeps slope and width at a new anchor.

Expected numbers by hand: P0 (0,100) P1 (10,150) P2 (20,110), Standard.
Midpoint (15,130), slope 30/15 = 2; ML at t=10 is 120 so UML offset +30, ML at t=20 is 140 so LML offset -30.
Pasted with P0 on (100,200): ML(110) = 220, UML(110) = 250, LML(110) = 190, width 60.
"""

import math
import unittest

from MyTradingSys.backtest.layers.pitchfork.pitchfork_detector import (
    PitchforkChannel,
    PitchforkPivot,
    PitchforkVariant,
    LogPitchforkChannel,
    copy_fork,
)


class TestCopyFork(unittest.TestCase):

    def setUp(self):
        self.p0 = PitchforkPivot(index=0, price=100.0, is_high=False)
        self.p1 = PitchforkPivot(index=10, price=150.0, is_high=True)
        self.p2 = PitchforkPivot(index=20, price=110.0, is_high=False)

    def test_copy_keeps_slope_and_width_at_new_anchor(self):
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.STANDARD)
        cp = copy_fork(pf, anchor_index=100, anchor_price=200.0)
        self.assertAlmostEqual(cp.slope, 2.0)
        self.assertAlmostEqual(cp.channel_width, 60.0)
        self.assertAlmostEqual(cp.get_ml(100), 200.0)
        self.assertAlmostEqual(cp.get_ml(110), 220.0)
        self.assertAlmostEqual(cp.get_uml(110), 250.0)
        self.assertAlmostEqual(cp.get_lml(110), 190.0)
        self.assertTrue(cp.p2_is_lower)

    def test_schiff_copy_is_a_pure_translation(self):
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.SCHIFF)
        cp = copy_fork(pf, anchor_index=100, anchor_price=200.0)  # dt=+100, dp=+100
        for t in (20.0, 35.0, 60.0):
            self.assertAlmostEqual(cp.get_ml(t + 100), pf.get_ml(t) + 100.0)
            self.assertAlmostEqual(cp.get_uml(t + 100), pf.get_uml(t) + 100.0)
            self.assertAlmostEqual(cp.get_lml(t + 100), pf.get_lml(t) + 100.0)

    def test_copy_of_copy_returns_to_source(self):
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.MODIFIED_SCHIFF)
        back = copy_fork(copy_fork(pf, 57, 333.0), 0, 100.0)
        for t in (5.0, 30.0):
            self.assertAlmostEqual(back.get_ml(t), pf.get_ml(t))
            self.assertAlmostEqual(back.get_uml(t), pf.get_uml(t))

    def test_log_copy_keeps_percent_width(self):
        pf = LogPitchforkChannel(self.p0, self.p1, self.p2)
        cp = copy_fork(pf, anchor_index=100, anchor_price=1000.0)  # 10x the source handle
        self.assertTrue(cp.log_scale)
        self.assertAlmostEqual(cp.get_ml(100), pf.get_ml(0) * 10.0)
        for t in (15.0, 40.0):
            self.assertAlmostEqual(cp.get_uml(t + 100) / cp.get_lml(t + 100), pf.get_uml(t) / pf.get_lml(t))
            self.assertAlmostEqual(cp.get_ml(t + 100), pf.get_ml(t) * 10.0, places=6)


if __name__ == "__main__":
    unittest.main()


class TestCopyForkSymbolArg(unittest.TestCase):
    """run_copy_fork_study.load_bars(symbol): ETH folder selected, 4H built by hand, bars >= DEV_END refused."""

    @staticmethod
    def _mod():
        import importlib.util
        from pathlib import Path
        p = Path(__file__).resolve().parents[3] / "research/pitchfork_2026-10-19/run_copy_fork_study.py"
        sp = importlib.util.spec_from_file_location("rcfs", p)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        return m

    def test_eth_builds_4h_from_chosen_folder_and_drops_dev_end(self):
        import tempfile
        from pathlib import Path
        import pandas as pd
        m = self._mod()
        end_ms = int(pd.Timestamp("2024-07-01").value // 1_000_000)
        start = end_ms - 2 * 240 * 60_000          # two 4H groups before DEV_END, one after
        rows = ["open_time,open,high,low,close,volume"]
        for k in range(3 * 240):
            t = start + k * 60_000
            rows.append("%d,%d,%d,%d,%d,1" % (t, 100 + k, 200 + k, 50 + k, 101 + k))
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "ETHUSDT-1m-2024-06.csv").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
            bars = m.load_bars("ETHUSDT", root=d)
        self.assertEqual(len(bars), 2)             # third group is at/after DEV_END
        b = bars[0]                                # hand: open k=0 -> 100, high max k=239 -> 439, low min k=0 -> 50, close k=239 -> 340
        self.assertEqual((b["o"], b["h"], b["l"], b["c"], b["v"]), (100, 439, 50, 340, 240))
        self.assertLess(bars[-1]["t"], end_ms)

    def test_eth_missing_folder_refuses(self):
        import tempfile
        m = self._mod()
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(SystemExit):
                m.load_bars("ETHUSDT", root=d)
