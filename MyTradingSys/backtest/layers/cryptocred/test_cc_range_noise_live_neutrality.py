"""B145: is classify_msb(filter_range_noise=True) neutral-or-better than the live default (False) on the archive? Spec: items/B145.

Runs the LIVE layer constructor (alerts/live_layers._cc_layer) over the archive twice (flag off / on), simulates every alert with the
same trade-through limit-fill rules and fees as run_cc_setups.py (all_taker variant, funding if present), and asserts per setup:
  1. kept-alert count with the flag on is >= 30
  2. mean net R with the flag on >= mean net R with the flag off
  3. no alert present with the flag on is absent from the flag-off set (the filter only removes)
Data-dependent and slow (minutes), so it is OPT-IN: set MTS_CC_NEUTRALITY_DATA to a root holding klines/ (1m Binance csv), optional
MTS_CC_NEUTRALITY_FUNDING to a funding root. Without it the test skips. The 25 percent threshold inside the filter is NO-SOURCE like
the other CryptoCred values (B143): a pass shows neutrality, not a sourced rule, and the flag must not be tuned.
"""
import functools
import os
import unittest

DATA = os.environ.get("MTS_CC_NEUTRALITY_DATA")
FUNDING = os.environ.get("MTS_CC_NEUTRALITY_FUNDING")


@unittest.skipUnless(DATA, "set MTS_CC_NEUTRALITY_DATA to a root with klines/ to run (minutes)")
class TestRangeNoiseNeutrality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from MyTradingSys.backtest.layers.cryptocred import run_cc_setups as R
        cls.R = R
        cls.bars_1m, cls.tf_bars, cls.funding = R.load_data(DATA, FUNDING, "1h")

    def _alerts_and_trades(self, setup_fn, on):
        from MyTradingSys.backtest.layers.alerts.live_layers import _cc_layer
        R = self.R
        fn = functools.partial(setup_fn, msb_kwargs={"filter_range_noise": True}) if on else setup_fn
        layer_alerts = _cc_layer(fn, "x")(self.tf_bars)
        signals = fn(self.tf_bars)
        trades = R.build_trades(signals, self.bars_1m, self.funding, "all_taker", R.TF_MS["1h"])
        return {(a["t"], a["side"]) for a in layer_alerts}, trades

    def test_filter_range_noise_is_neutral_or_better_on_archive_replay(self):
        R = self.R
        for name, fn in R.SETUPS.items():
            with self.subTest(setup=name):
                off_keys, off_tr = self._alerts_and_trades(fn, False)
                on_keys, on_tr = self._alerts_and_trades(fn, True)
                self.assertGreaterEqual(len(on_keys), 30, f"{name}: kept alerts {len(on_keys)} < 30")
                self.assertTrue(on_keys <= off_keys, f"{name}: filter added alerts {sorted(on_keys - off_keys)[:3]}")
                mean = lambda tr: sum(t["net_r"] for t in tr) / len(tr) if tr else float("-inf")
                self.assertGreaterEqual(mean(on_tr), mean(off_tr),
                                        f"{name}: mean net R on {mean(on_tr):.4f} < off {mean(off_tr):.4f} (n on {len(on_tr)}, off {len(off_tr)})")


if __name__ == "__main__":
    unittest.main()
