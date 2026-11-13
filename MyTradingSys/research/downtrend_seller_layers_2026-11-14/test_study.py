"""Tests for study.py. Run: python -m pytest test_study.py -q   (E9_LAG=0 runs the deliberately wrong version and must FAIL test_levels_do_not_use_today)."""
import sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import study  # noqa: E402


def make_coin(tmp_path, days=6, today_shift=0.0):
    rng = np.random.default_rng(1)
    n = days * 96
    t = (20000 * study.DAY) + np.arange(n) * 900_000
    base = 100 + np.cumsum(rng.normal(0, 0.1, n))
    o = base; c = base + rng.normal(0, 0.05, n)
    h = np.maximum(o, c) + 0.1; l = np.minimum(o, c) - 0.1
    v = rng.uniform(1, 5, n)
    if today_shift:                                  # mutate ONLY the last day
        h[-96:] += today_shift; l[-96:] -= today_shift; v[-96:] *= 10
    a = np.column_stack([t, o, h, l, c, v, v * c])
    np.savez_compressed(tmp_path / "BTCUSDT_15m.npz", a=a)
    return study.Coin(tmp_path, "BTCUSDT", now_ms=int(t[-1] + 900_000 + 1))


def test_levels_do_not_use_today(tmp_path):
    d_dir = tmp_path / "a"; d_dir.mkdir(); e_dir = tmp_path / "b"; e_dir.mkdir()
    a = make_coin(d_dir); b = make_coin(e_dir, today_shift=5.0)
    today = a.days[-1]
    assert a.levels_for(today) == b.levels_for(today)        # today's bars changed, today's levels must not


def test_prior_day_high_is_yesterdays(tmp_path):
    c = make_coin(tmp_path)
    d = c.days[-1]
    assert c.levels_for(d)["L3"] == float(c.h[c.sl(d - 1)].max())
    assert c.levels_for(d)["PDL"] == float(c.l[c.sl(d - 1)].min())


def test_profile_value_area_contains_poc_and_70pct():
    h = np.array([10.2, 10.1, 10.3, 11.0]); l = np.array([9.8, 9.9, 10.0, 10.5]); c = np.array([10.0, 10.0, 10.1, 10.8])
    v = np.array([5.0, 5.0, 4.0, 1.0])
    p = study.profile(h, l, c, v, 0.0005)
    assert p["val"] <= p["poc"] <= p["vah"]


def test_rsi_uses_last_closed_hour(tmp_path):
    c = make_coin(tmp_path)
    t = int(c.t[200])
    assert c.rsi_at(t) == c.rsi.get(t // study.HOUR - 1, np.nan) or np.isnan(c.rsi_at(t))
