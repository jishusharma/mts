"""Placebo for the acceptance claim: synthetic series with known answers (hand-computed, not read from placebo80.py)."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location("vaacc_" + name, HERE / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pl():
    return _load("placebo80")


def _day(date_ms, closes):
    # 1440 one-minute bars (t, o, h, l, c, vol); open = previous close, high = low = close so the low of the rest of the day is a minimum of closes
    rows, prev = [], closes[0]
    for i, c in enumerate(closes):
        rows.append((date_ms + i * 60000, prev, max(prev, c), min(prev, c), c, 1.0))
        prev = c
    return rows


def _days(kind):
    base = 1700000000000 // 86400000 * 86400000
    out = {}
    for n, dname in enumerate(("2026-01-01", "2026-01-02", "2026-01-03")):
        if kind == "drift":
            closes = [100000.0 - 1000.0 * i / 1439 for i in range(1440)]   # falls 1000 over the day
        else:
            closes = [100000.0] * 1440
        out[dname] = _day(base + n * 86400000, closes)
    return out


def test_every_day_drifting_down_gives_rate_one(pl):
    # segment 10 closes at minute 10*30+29 = 329; the day then falls from 99763.1 .. to 99000.0: drop >= 700 >> d = 5
    drop = pl.drop_matrix(_days("drift"))
    assert drop.shape[0] == 3
    rates = pl.placebo_draws(drop, ks=[10, 10, 10], ds=[5.0, 5.0, 5.0], excluded=[], n_draws=50, seed=7)
    assert np.all(rates == 1.0)


def test_flat_days_give_rate_zero(pl):
    drop = pl.drop_matrix(_days("flat"))
    rates = pl.placebo_draws(drop, ks=[10, 10], ds=[5.0, 5.0], excluded=[], n_draws=50, seed=7)
    assert np.all(rates == 0.0)


def test_excluded_days_are_never_drawn(pl):
    # day 0 drifts down (hit), days 1-2 flat (no hit); excluding days 1 and 2 leaves only the drifting day -> 1.0
    d = _days("flat")
    k0 = sorted(d)[0]
    d[k0] = _days("drift")[k0]
    drop = pl.drop_matrix(d)
    rates = pl.placebo_draws(drop, ks=[10, 10], ds=[5.0, 5.0], excluded=[1, 2], n_draws=50, seed=7)
    assert np.all(rates == 1.0)
    rates = pl.placebo_draws(drop, ks=[10, 10], ds=[5.0, 5.0], excluded=[0], n_draws=50, seed=7)
    assert np.all(rates == 0.0)


def test_distance_larger_than_any_drop_gives_zero(pl):
    drop = pl.drop_matrix(_days("drift"))
    rates = pl.placebo_draws(drop, ks=[10], ds=[5000.0], excluded=[], n_draws=20, seed=7)
    assert np.all(rates == 0.0)


def test_seed_is_deterministic(pl):
    d = _days("drift")
    d[sorted(d)[1]] = _days("flat")[sorted(d)[1]]
    drop = pl.drop_matrix(d)
    a = pl.placebo_draws(drop, [10, 10, 10, 10], [5.0] * 4, [], 30, 7)
    b = pl.placebo_draws(drop, [10, 10, 10, 10], [5.0] * 4, [], 30, 7)
    assert np.array_equal(a, b)
    assert 0.0 < a.mean() < 1.0
