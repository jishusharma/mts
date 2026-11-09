"""Tests for spinning_top.py (T01). Hand-built bars for every rule, split refusal,
no-lookahead, and the fee / R / funding arithmetic. Run: python -m pytest -q test_spinning_top.py  (or python test_spinning_top.py)
"""
import sys
import pathlib
import tempfile

import numpy as np
import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import spinning_top as st  # noqa: E402

MS4H = 4 * 3600 * 1000


def _flat(n, price=100.0, vol=10.0):
    o = np.full(n, price)
    h = np.full(n, price + 1.0)
    l = np.full(n, price - 1.0)
    c = np.full(n, price)
    v = np.full(n, vol)
    return o, h, l, c, v


def _set(arrs, i, o, h, l, c, v):
    O, H, L, C, V = arrs
    O[i], H[i], L[i], C[i], V[i] = o, h, l, c, v


# ---------- rules on hand-built bars ----------

def test_spinning_top_long_flag_fires_on_its_rule():
    # 25 flat bars (range 2, volume 10), then a bar at a new 20-bar low:
    # range 4 (l 96, h 100), body 0.4 (<= 0.25*4 = 1.0), upper shadow 0.3?? -> build explicitly
    arr = list(_flat(25))
    # setup at index 24: open 98.0, close 98.5 (body 0.5), high 99.0 (upper 0.5), low 94.0 (lower 4.0), range 5
    # body 0.5 <= 0.25*5 = 1.25 ok; upper 0.5 >= 1.25? NO -> must build upper >= 0.25*range
    _set(arr, 24, o=97.0, h=100.0, l=94.0, c=98.0, v=30.0)  # range 6, body 1.0 <= 1.5; upper 2.0 >= 1.5; lower 3.0 >= 1.5
    lf, sf = st.setup_flags(*arr)
    assert lf[24] and not sf[24]


def test_body_too_big_rejects():
    arr = list(_flat(25))
    _set(arr, 24, o=94.5, h=100.0, l=94.0, c=99.5, v=30.0)  # body 5 > 0.25*6
    lf, sf = st.setup_flags(*arr)
    assert not lf[24] and not sf[24]


def test_one_shadow_missing_rejects():
    arr = list(_flat(25))
    _set(arr, 24, o=97.0, h=97.4, l=94.0, c=97.2, v=30.0)  # upper shadow 0.2 < 0.25*3.4 = 0.85
    lf, sf = st.setup_flags(*arr)
    assert not lf[24] and not sf[24]


def test_volume_below_two_x_median_rejects():
    arr = list(_flat(25))
    _set(arr, 24, o=97.0, h=100.0, l=94.0, c=98.0, v=19.9)  # median of prior 20 = 10, need >= 20
    lf, sf = st.setup_flags(*arr)
    assert not lf[24]


def test_volume_exactly_two_x_median_passes():
    arr = list(_flat(25))
    _set(arr, 24, o=97.0, h=100.0, l=94.0, c=98.0, v=20.0)
    lf, sf = st.setup_flags(*arr)
    assert lf[24]


def test_location_not_lowest_low_rejects():
    arr = list(_flat(25))
    arr[2][10] = 93.0  # an earlier low inside the 20-bar window (index 10 is in 4..24)
    _set(arr, 24, o=97.0, h=100.0, l=94.0, c=98.0, v=30.0)
    lf, sf = st.setup_flags(*arr)
    assert not lf[24]


def test_short_flag_at_20_bar_high():
    arr = list(_flat(25))
    _set(arr, 24, o=103.0, h=106.0, l=100.0, c=103.0, v=30.0)  # top; body 0; upper 3 >= 1.5; lower 3 >= 1.5
    lf, sf = st.setup_flags(*arr)
    assert sf[24] and not lf[24]


# ---------- entry, stop, target, time stop, ties ----------

def _bars_from(rows):
    """rows: list of (o,h,l,c,v). Returns arrays."""
    a = np.array(rows, dtype=float)
    return a[:, 0].copy(), a[:, 1].copy(), a[:, 2].copy(), a[:, 3].copy(), a[:, 4].copy()


def _pad_to(rows, n_pre=25):
    return [(100.0, 101.0, 99.0, 100.0, 10.0)] * n_pre + rows


def test_long_entry_fills_at_trigger_and_hits_target():
    rows = _pad_to([(97.0, 100.0, 94.0, 98.0, 30.0)])  # setup at index 25? (n_pre=25 -> index 25)
    # setup index 25: high 100, low 94 -> trigger 100.01, stop 94, risk from fill 100.01 -> 6.01; target 3R = 118.04
    rows += [(99.0, 100.5, 98.0, 100.0, 10.0)]          # idx 26: no trigger (high 100.5 < 100.01? it is >=; see below)
    o, h, l, c, v = _bars_from(rows)
    # idx 26 high 100.5 >= 100.01 -> fill at max(open 99, 100.01) = 100.01
    t = np.arange(len(o)) * MS4H
    tr = st.simulate(o, h, l, c, v, t, *st.setup_flags(o, h, l, c, v), MS4H, funding=None, start=0)[0]
    assert len(tr) == 1 and tr[0]["side"] == "long"
    assert tr[0]["fill_idx"] == 26
    assert abs(tr[0]["entry"] - 100.01) < 1e-9
    assert tr[0]["stop"] == 94.0
    # now a target path: idx 27 high 120 -> hits 3R target
    rows2 = rows + [(101.0, 120.0, 100.5, 119.0, 10.0)]
    o, h, l, c, v = _bars_from(rows2)
    t = np.arange(len(o)) * MS4H
    tr = st.simulate(o, h, l, c, v, t, *st.setup_flags(o, h, l, c, v), MS4H, funding=None, start=0)[0]
    assert tr[0]["outcome"] == "target"
    assert abs(tr[0]["gross_r"] - 3.0) < 1e-9


def test_no_trigger_within_three_bars_means_no_trade():
    rows = _pad_to([(97.0, 100.0, 94.0, 98.0, 30.0)])
    rows += [(98.0, 99.5, 97.0, 98.0, 10.0)] * 3  # three bars that never trade above 100.01
    rows += [(98.0, 120.0, 97.0, 119.0, 10.0)]     # the fourth bar would trigger, but it is outside the 3-bar window
    o, h, l, c, v = _bars_from(rows)
    t = np.arange(len(o)) * MS4H
    tr = st.simulate(o, h, l, c, v, t, *st.setup_flags(o, h, l, c, v), MS4H, funding=None, start=0)[0]
    assert tr == []


def test_gap_open_fills_at_open():
    rows = _pad_to([(97.0, 100.0, 94.0, 98.0, 30.0)])
    rows += [(102.0, 103.0, 101.0, 102.5, 10.0)]   # opens above the trigger: fill at the open 102
    rows += [(102.5, 103.0, 101.0, 102.0, 10.0)]
    o, h, l, c, v = _bars_from(rows)
    t = np.arange(len(o)) * MS4H
    tr = st.simulate(o, h, l, c, v, t, *st.setup_flags(o, h, l, c, v), MS4H, funding=None, start=0)[0]
    assert tr[0]["entry"] == 102.0


def test_stop_wins_same_bar_tie():
    rows = _pad_to([(97.0, 100.0, 94.0, 98.0, 30.0)])
    rows += [(100.5, 101.0, 93.0, 100.0, 10.0)]  # fill bar: high 101 triggers; low 93 breaches stop 94; target not reached
    o, h, l, c, v = _bars_from(rows)
    t = np.arange(len(o)) * MS4H
    tr = st.simulate(o, h, l, c, v, t, *st.setup_flags(o, h, l, c, v), MS4H, funding=None, start=0)[0]
    assert tr[0]["outcome"] == "stop"
    assert abs(tr[0]["gross_r"] - (-1.0 - (100.01 - 94.0) * 0)) < 1e-6 or tr[0]["gross_r"] < -0.99


def test_time_stop_exits_at_close_of_20th_bar():
    rows = _pad_to([(97.0, 100.0, 94.0, 98.0, 30.0)])
    rows += [(100.5, 101.0, 98.0, 100.0, 10.0)]          # fill bar (index 26)
    rows += [(100.0, 101.0, 98.5, 100.2, 10.0)] * 19      # bars 27..45 inside the range, no stop, no target
    rows += [(100.0, 101.0, 98.5, 100.7, 10.0)]           # bar 46 closes at 100.7
    rows += [(100.0, 101.0, 98.5, 100.0, 10.0)]
    o, h, l, c, v = _bars_from(rows)
    t = np.arange(len(o)) * MS4H
    tr = st.simulate(o, h, l, c, v, t, *st.setup_flags(o, h, l, c, v), MS4H, funding=None, start=0)[0]
    assert tr[0]["outcome"] == "time"
    assert tr[0]["exit_idx"] == 26 + 19
    assert abs(tr[0]["exit_price"] - c[26 + 19]) < 1e-12


def test_one_position_rule_skips_overlapping_setups():
    rows = _pad_to([(97.0, 100.0, 94.0, 98.0, 30.0)])
    rows += [(100.5, 101.0, 98.0, 100.0, 10.0)]       # fill
    rows += [(100.0, 101.0, 98.5, 100.0, 10.0)] * 2
    # another setup inside the open trade:
    rows += [(97.0, 100.0, 94.0, 98.0, 30.0)]
    o, h, l, c, v = _bars_from(rows)
    t = np.arange(len(o)) * MS4H
    tr = st.simulate(o, h, l, c, v, t, *st.setup_flags(o, h, l, c, v), MS4H, funding=None, start=0)[0]
    assert len(tr) == 1


# ---------- fee / R / funding arithmetic ----------

def test_fee_r_is_round_trip_over_stop_fraction():
    # stop distance 2 % of entry: fee 12 bps round trip -> fee_r = 0.0012 / 0.02 = 0.06 R
    assert abs(st.fee_r(stop_frac=0.02) - 0.06) < 1e-12


def test_net_r_is_gross_minus_fee_minus_funding():
    # long, stop fraction 0.02, funding rates summing to +0.0001 (longs pay): funding_R = 0.0001 / 0.02 = 0.005
    net = st.net_r(gross=1.0, stop_frac=0.02, fund_sum=0.0001, side="long")
    assert abs(net - (1.0 - 0.06 - 0.005)) < 1e-12
    # short receives the same positive funding
    net_s = st.net_r(gross=1.0, stop_frac=0.02, fund_sum=0.0001, side="short")
    assert abs(net_s - (1.0 - 0.06 + 0.005)) < 1e-12


def test_funding_sum_window_is_open_at_start_closed_at_end():
    ts = np.array([1000, 2000, 3000])
    rates = np.array([0.1, 0.2, 0.4])
    assert abs(st.funding_sum(ts, rates, 1000, 3000) - 0.6) < 1e-12  # (1000, 3000] -> 2000 and 3000
    assert st.funding_sum(ts, rates, 3000, 3000) == 0.0


# ---------- split refusal and loader ----------

def test_dev_loader_refuses_bars_past_dev_end(tmp_path):
    p = tmp_path / "BTCUSDT" / "4h" / "klines"
    p.mkdir(parents=True)
    # one monthly file that contains a bar closing after 2024-07-01
    # close_time of bar opened 2024-07-01 00:00 UTC of 4h = 2024-07-01 03:59:59.999
    open_ms = 1719792000000  # 2024-07-01 00:00 UTC
    row = f"{open_ms},1,2,0.5,1.5,10,{open_ms + MS4H - 1},1,1,1,1,0\n"
    (p / "BTCUSDT-4h-2024-07.csv").write_text(row, encoding="utf-8")
    with pytest.raises(st.SplitViolation):
        st.assert_bars_in_window(st.read_monthly(tmp_path, "BTCUSDT", "4h", "2024-07"), "DEV")


def test_holdout_is_never_loaded(tmp_path):
    with pytest.raises(st.SplitViolation):
        st.load_bars("BTCUSDT", "4h", "HOLDOUT", root=tmp_path)


def test_validation_loader_refuses_end_past_validation(tmp_path):
    with pytest.raises(st.SplitViolation):
        st.check_window_end("2025-07-02")


# ---------- no lookahead ----------

def test_setup_flag_does_not_depend_on_later_bars():
    rng = np.random.default_rng(7)
    n = 80
    base = 100 + np.cumsum(rng.normal(0, 1, n))
    o = base + rng.normal(0, 0.3, n)
    c = base + rng.normal(0, 0.3, n)
    h = np.maximum(o, c) + np.abs(rng.normal(0, 1.5, n))
    l = np.minimum(o, c) - np.abs(rng.normal(0, 1.5, n))
    v = np.abs(rng.normal(10, 4, n)) + 1
    lf, sf = st.setup_flags(o, h, l, c, v)
    cut = 50
    o2, h2, l2, c2, v2 = o.copy(), h.copy(), l.copy(), c.copy(), v.copy()
    o2[cut + 1:] *= 1.5
    h2[cut + 1:] *= 1.5
    l2[cut + 1:] *= 0.5
    c2[cut + 1:] *= 1.2
    v2[cut + 1:] *= 9
    lf2, sf2 = st.setup_flags(o2, h2, l2, c2, v2)
    assert np.array_equal(lf[:cut + 1], lf2[:cut + 1])
    assert np.array_equal(sf[:cut + 1], sf2[:cut + 1])


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
