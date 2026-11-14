"""Checks for the 10-symbol layers re-derivation: shared cost model, Holm family size, one-sided p, closed-data regime tags."""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import study as T  # noqa: E402
from MyTradingSys.backtest import research_kit as rk  # noqa: E402


def test_cost_is_shared_taker_model_not_parent_10bp():
    # entry 100, stop 98 (R = 2, stop 2 %), target +1R hit on bar 3: gross +1R, cost = 0.14 % / 2 % = 0.07 R
    n = 168
    O = np.full((1, n), 100.0); H = np.full((1, n), 101.0); Lo = np.full((1, n), 99.0); C = np.full((1, n), 100.0)
    H[0, 3] = 102.5
    r = T.S.L.fwd_exit(np.array([100.0]), np.array([98.0]), O, H, Lo, C, np.zeros_like(O), "tgt", 1.0, T.S.TAKER)
    assert abs(r["net_r"][0] - (1.0 - rk.taker_cost_r(2.0))) < 1e-9
    assert abs(r["net_r"][0] - (1.0 - 0.07)) < 1e-9          # the parent's 10 bp would give 0.95


def test_family_size_is_56_and_holm_uses_it():
    assert T.M_FAMILY == 56
    p = rk.holm([0.001], m=T.M_FAMILY)
    assert abs(p[0] - 0.056) < 1e-12                           # 56 x 0.001, so a lone small p is not rejected at 0.05


def test_one_sided_p():
    assert abs(T.p_one_sided(1.6448536, 1.0) - 0.05) < 1e-6
    assert T.p_one_sided(-1.0, 1.0) > 0.5 and T.p_one_sided(1.0, float("nan")) == 1.0


def test_regime_is_asof_and_bear_absent_in_mix_file():
    txt = (HERE / "regime_mix.txt").read_text()
    assert "VALIDATION" in txt and "bear 0 (0%)" in txt


def test_universe_is_ten_and_subset_of_parent():
    parent20 = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM NEAR UNI TRX BCH ETC FIL APT ARB".split()
    assert len(T.COINS) == 10 and set(T.COINS) <= set(parent20)
    assert "BTC" in T.COINS
