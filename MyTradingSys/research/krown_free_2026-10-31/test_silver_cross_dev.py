"""Tests for silver_cross_dev.py (Krown silver cross, DEV only). Hand-worked expected values, synthetic data.

Hand work (fast span 2 = alpha 2/3, slow span 3 = alpha 1/2), closes 10,10,10,12,16,16,10:
  fast e: 10,10,10,11.3333,14.4444,15.4815,11.8272 ; slow s: 10,10,10,11,13.5,14.75,12.375
  diff : 0,0,0,+0.3333,+0.9444,+0.7315,-0.5478 -> first diff<=0 -> >0 on day 3 (cross-day close).
  entry = open of day 4 = 12 ; hold 2 days -> exit open of day 6 = 16 ; gross 16/12-1 = 0.333333 ; net = gross - 0.001.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import silver_cross_dev as sc  # noqa: E402

CLOSES = np.array([10, 10, 10, 12, 16, 16, 10], dtype=float)
OPENS = np.r_[10.0, CLOSES[:-1]]


def test_ema_hand_values():
    f = sc.ema(CLOSES, 2)      # span 2 -> alpha 2/3
    s = sc.ema(CLOSES, 3)      # span 3 -> alpha 1/2
    assert f[3] == pytest.approx(11.333333, abs=1e-5)
    assert f[4] == pytest.approx(14.444444, abs=1e-5)
    assert s[3] == pytest.approx(11.0)
    assert s[4] == pytest.approx(13.5)
    assert s[5] == pytest.approx(14.75)


def test_cross_day_is_day_3_only():
    assert list(sc.cross_up_days(CLOSES, 2, 3)) == [3]


def test_trade_net_return_hand_value():
    tr = sc.trades(OPENS, CLOSES, fast=2, slow=3, hold=2, first_day=0)
    assert len(tr) == 1
    assert tr[0]["entry_i"] == 4 and tr[0]["exit_i"] == 6
    assert tr[0]["gross"] == pytest.approx(16 / 12 - 1)
    assert tr[0]["net"] == pytest.approx(16 / 12 - 1 - 0.001)
    assert tr[0]["hit"] is True


def test_fee_comes_from_fees_py():
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backtest"))
    import fees
    assert sc.FEE_RT == pytest.approx(2 * fees.BINANCE_TAKER) == pytest.approx(0.001)


def test_event_dropped_when_exit_beyond_data():
    tr = sc.trades(OPENS, CLOSES, fast=2, slow=3, hold=5, first_day=0)   # exit index 9 > last 6
    assert tr == []


def test_first_day_filters_warmup_events():
    assert sc.trades(OPENS, CLOSES, fast=2, slow=3, hold=2, first_day=4) == []


def test_one_bar_shift_causality():
    """Signal on day t exists with data up to t, and is absent with data up to t-1."""
    assert 3 in sc.cross_up_days(CLOSES[:4], 2, 3)
    assert 3 not in sc.cross_up_days(CLOSES[:3], 2, 3)


def test_future_perturbation_leaves_earlier_events():
    rng = np.random.default_rng(5)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.03, 400)))
    base = [d for d in sc.cross_up_days(c, 21, 55) if d <= 250]
    c2 = c.copy()
    c2[251:] *= 0.3
    pert = [d for d in sc.cross_up_days(c2, 21, 55) if d <= 250]
    assert base == pert and len(base) >= 1


def test_blocks_chain_within_hold():
    # entries 0, 10, 100 with hold 30 -> blocks [0,10], [100]
    assert sc.block_ids([0, 10, 100], 30) == [0, 0, 1]


def test_loader_refuses_bar_at_or_after_cutoff(tmp_path):
    p = tmp_path / "k.csv"
    ms = int(np.datetime64("2024-07-01T00:00", "ms").astype("int64"))
    p.write_text("open_time,open,high,low,close\n%d,1,1,1,1\n" % ms, newline="\n")
    with pytest.raises(ValueError):
        sc.load_klines([p])


def test_refuses_run_without_frozen_prereg(tmp_path):
    f = tmp_path / "PRE_REG.md"
    f.write_text("no freeze line\n", newline="\n")
    with pytest.raises(SystemExit):
        sc.require_frozen(f)
    f.write_text("x\n\nFROZEN_UTC: 2026-10-31T01:05:00Z\n", newline="\n")
    assert len(sc.require_frozen(f)) == 64
