"""Core checks: cost includes slippage, exit charges it, best-5-days share, day-cluster bootstrap, placebo size guard."""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "backtest")))
import fees  # noqa: E402
import rsi_grid_lib as L  # noqa: E402
import study  # noqa: E402


def test_cost_has_slippage():
    assert abs(study.COST - (2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13)) < 1e-12 and study.COST > 2 * fees.BINANCE_TAKER


def test_fwd_exit_charges_cost():
    n = 168
    O = np.full((1, n), 100.0); H = np.full((1, n), 101.0); Lo = np.full((1, n), 99.0); C = np.full((1, n), 100.0)
    H[0, 2] = 104.5   # +2R target (R=2 -> 104)
    r = L.fwd_exit(np.array([100.0]), np.array([98.0]), O, H, Lo, C, np.zeros_like(O), "tgt", 2.0, study.COST / 2)
    assert abs(r["net_r"][0] - (2.0 - study.COST * 100.0 / 2.0)) < 1e-9


def test_best5_and_day_boot():
    df = pd.DataFrame(dict(day=[1, 1, 2, 3, 4, 5, 6, 7], net_r=[5.0, 5.0, 4.0, 3.0, 2.0, 1.0, -1.0, -1.0]))
    share, wo, n = study.best5(df)
    assert abs(share - 20.0 / 18.0) < 1e-9 and n == 2 and wo == -1.0
    lo, hi, p = study.boot_day(df.net_r.values, df.day.values)
    assert lo <= hi and 0 < p <= 1
    assert np.isnan(study.placebo_p(np.arange(5.0), 5, 1.0))
