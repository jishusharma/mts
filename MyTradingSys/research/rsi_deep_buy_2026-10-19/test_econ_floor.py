"""Tests for econ_floor.py (RSI deep-buy Stage 0). Synthetic data only; fee/cutoff constants from the module."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import econ_floor as ef  # noqa: E402


def _csv(path, rows):
    lines = ["open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore"]
    for t, o, h, l, c in rows:
        lines.append(f"{t},{o},{h},{l},{c},1,{t + 59999},1,1,1,1,0")
    Path(path).write_text("\n".join(lines) + "\n", newline="\n")


def _ms(s):
    return int(np.datetime64(s, "ms").astype("int64"))


def test_loader_refuses_bar_at_or_after_cutoff(tmp_path):
    ok = tmp_path / "ok.csv"
    _csv(ok, [(_ms("2024-06-30T23:59"), 1, 1, 1, 1)])
    assert len(ef.load_klines([ok])["open_time"]) == 1
    bad = tmp_path / "bad.csv"
    _csv(bad, [(_ms("2024-06-30T23:59"), 1, 1, 1, 1), (_ms("2024-07-01T00:00"), 1, 1, 1, 1)])
    with pytest.raises(ValueError):
        ef.load_klines([bad])


def test_fee_is_sourced_from_fees_py():
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backtest"))
    import fees
    assert ef.FEE == pytest.approx(2 * fees.BINANCE_TAKER) == pytest.approx(0.001)


def _walk(n, seed=3):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.002, n)))
    o = np.r_[c[0], c[:-1]]
    return o, c


def test_future_bar_change_leaves_earlier_events_unchanged():
    o, c = _walk(3000)
    c2 = c.copy()
    c2[2500:] *= 0.5          # planted crash in the future
    r1 = ef.rsi_series(c)
    r2 = ef.rsi_series(c2)
    cut = 2400
    e1 = [i for i in ef.find_events(r1, 30.0)[0] if i < cut]
    e2 = [i for i in ef.find_events(r2, 30.0)[0] if i < cut]
    assert e1 == e2 and len(e1) > 0
    # relative (trailing percentile) level is causal as well
    t1 = ef.relative_level(r1, window=500, step=50)
    t2 = ef.relative_level(r2, window=500, step=50)
    assert np.array_equal(np.nan_to_num(t1[:cut], nan=-1), np.nan_to_num(t2[:cut], nan=-1))


def test_hysteresis_one_episode_until_rearmed():
    rsi = np.array([50, 40, 29, 28, 27, 31, 29, 33.5, 29, 20], float)
    ev, _ = ef.find_events(rsi, 30.0, h=3.0)
    # first touch at 2; 31 is not >= 33 so 6 is not a new episode; 33.5 re-arms, so 8 is
    assert ev == [2, 8]


def test_forward_returns_use_next_open_not_signal_close():
    o = np.array([100, 100, 100.0, 100.10, 100, 100, 100])
    c = np.array([100, 90, 100, 100, 100, 100, 100.0])      # signal bar close 90 must be ignored
    g = ef.forward_gross(o, np.array([1]), 1)               # entry open[2]=100, exit open[3]=100.10
    assert g[0] == pytest.approx(0.001)


def test_fee_boundary_dead_rule():
    assert ef.is_dead(0.001 - 1e-9) is True
    assert ef.is_dead(0.001) is False         # exactly at fee is not below it
    assert ef.is_dead(0.0012) is False


def test_falling_series_never_recovering_shows_loss():
    n = 1500
    rng = np.random.default_rng(5)
    drift = np.r_[np.zeros(400), np.full(n - 400, -0.002)]      # flat (arms the episode), then a fall that never recovers
    c = 100 * np.exp(np.cumsum(rng.normal(drift, 0.002)))
    o = np.r_[c[0], c[:-1]]
    rsi = ef.rsi_series(c)
    ev, _ = ef.find_events(rsi, 30.0)
    assert len(ev) > 0
    for h in (1, 4, 16):
        g = ef.forward_gross(o, np.array(ev), h)
        g = g[~np.isnan(g)]
        assert g.mean() < 0


def test_cluster_ci_widens_with_day_clustering():
    x = np.array([0.01, 0.01, 0.01, 0.01, -0.01, -0.01, -0.01, -0.01])
    days = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    m, se = ef.cluster_mean_se(x, days)
    ind_se = x.std(ddof=1) / np.sqrt(len(x))
    assert m == pytest.approx(0.0) and se > ind_se


def test_classify_boundaries():
    assert ef.classify(0.0002, 0.0009) == "dead"
    assert ef.classify(0.0002, 0.001) == "inconclusive"     # upper exactly at fee is not dead
    assert ef.classify(0.001, 0.002) == "alive"


def test_week_clusters_group_seven_days():
    assert list(ef.week_clusters([0, 6, 7, 13, 14])) == [0, 0, 1, 1, 2]


def test_resample_aggregates_ohlc():
    t0 = _ms("2022-01-01T00:00")
    t = t0 + 60000 * np.arange(30)
    o = np.arange(30, dtype=float) + 1
    d = {"open_time": t, "open": o, "high": o + 0.5, "low": o - 0.5, "close": o + 0.1}
    r = ef.resample(d, 15)
    assert len(r["open_time"]) == 2
    assert r["open"][0] == 1 and r["close"][0] == pytest.approx(15.1)
    assert r["high"][0] == 15.5 and r["low"][0] == 0.5
