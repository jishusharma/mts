"""Wiring for bear_proxy_context_tuning (study.py): RSI series vs an independent Wilder RSI, SMA200 side/age, as-of proxy state (a planted
future bar changes nothing), the fake-out definition (adverse 1 ATR before favourable 1 ATR; both in one bar = adverse), each Part B filter,
the pick floor and the power gate. Expected numbers are computed here independently, not from study.py."""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("bear_ctx_study", HERE / "study.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)
DAY = T.DAY
REGISTRY = json.loads((HERE.parents[2] / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))


def bar(t, o, h, l, c, v=10.0):
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": v}


def flat_bars(n, px=100.0, rng=2.0):
    return [bar(k * 900000, px, px + rng / 2, px - rng / 2, px) for k in range(n)]


def wilder_rsi(closes, p):
    """Independent Wilder RSI (FORMULAS s1): seed = simple mean of the first p gains/losses, then smoothing."""
    d = np.diff(closes)
    g, l = np.maximum(d, 0), np.maximum(-d, 0)
    ag, al = g[:p].mean(), l[:p].mean()
    out = {p: 100.0 if al == 0 else 100 - 100 / (1 + ag / al)}
    for i in range(p, len(d)):
        ag, al = (ag * (p - 1) + g[i]) / p, (al * (p - 1) + l[i]) / p
        out[i + 1] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def test_rsi_pairs_matches_independent_wilder_and_is_as_of():
    rng = np.random.default_rng(3)
    closes = list(100 + np.cumsum(rng.normal(0, 1, 120)))
    bars = [bar(k * DAY, c, c, c, c) for k, c in enumerate(closes)]
    for p in (14, 21):
        tcl, v = T.rsi_pairs(bars, p)
        ref = wilder_rsi(np.array(closes), p)
        assert len(v) == len(bars) - 1 - p                                   # last bar dropped, first p have no RSI
        for t, x in zip(tcl, v):
            k = int(t // DAY) - 1                                            # bar k closes at (k+1)*DAY
            assert abs(x - ref[k]) < 1e-9
    assert tcl[-1] == (len(bars) - 1) * DAY                                  # final bar never published


def test_sma_side_and_age():
    c = list(np.linspace(300, 100, 260))                                     # falling: below SMA200 once 200 bars exist
    side, age = T.sma_side_age(c)
    assert (side[:199] == 0).all() and (side[199:] == -1).all()
    assert c[199] < np.mean(c[:200])
    assert age[199] == 1 and age[259] == 61
    s2, a2 = T.sma_side_age(list(np.linspace(100, 300, 260)))
    assert (s2[199:] == 1).all() and a2[259] == 61


def _falling_daily(n):
    return [bar(k * DAY, 1000.0 - k, 1000.0 - k, 1000.0 - k, 1000.0 - k) for k in range(n)]


def test_proxy_state_falling_market_fires_rising_market_does_not():
    hi = 520 * DAY
    st = T.day_state(_falling_daily(520), REGISTRY, hi)
    x = 500 - st["day0"]
    assert st["proxy"][(14, 40, "1w", True)][x] and st["proxy"][(14, 40, "1w", False)][x] and st["proxy"][(21, 35, "1d", True)][x]
    assert st["phase"][x] == "mature"
    up = [bar(k * DAY, 1000.0 + k, 1000.0 + k, 1000.0 + k, 1000.0 + k) for k in range(520)]
    su = T.day_state(up, REGISTRY, hi)
    assert not any(su["proxy"][s][x] for s in T.A_SETTINGS)                  # RSI 100 and above SMA200: no setting fires


def test_sma_on_never_fires_where_sma_off_does_not():
    px = [2000.0 - 2 * k for k in range(600)]
    px += [px[-1] + 1.5 * k for k in range(1, 30)]                           # bounce at the end
    d1 = [bar(k * DAY, c, c, c, c) for k, c in enumerate(px)]
    st = T.day_state(d1, REGISTRY, len(d1) * DAY)
    for tf in ("1d", "1w"):
        assert not (st["proxy"][(14, 45, tf, True)] & ~st["proxy"][(14, 45, tf, False)]).any()


def test_sma_filter_blocks_when_close_is_above_sma200():
    # long climb, then a 5-day dip: daily RSI14 low but the close stays above SMA200
    px = [100.0 + k for k in range(600)] + [699.0 - 12.0 * k for k in range(1, 8)]
    d1 = [bar(k * DAY, c, c, c, c) for k, c in enumerate(px)]
    st = T.day_state(d1, REGISTRY, len(d1) * DAY)
    x = len(d1) - 1 - st["day0"]
    assert st["proxy"][(14, 45, "1d", False)][x] and not st["proxy"][(14, 45, "1d", True)][x]


def test_state_is_as_of_planted_future_bars_change_nothing():
    base = _falling_daily(600)
    ext = base + [bar((600 + k) * DAY, 5000.0 + k, 5000.0 + k, 5000.0 + k, 5000.0 + k) for k in range(60)]
    a = T.day_state(base, REGISTRY, 600 * DAY)
    b = T.day_state(ext, REGISTRY, 660 * DAY)
    n = 580
    for s in T.A_SETTINGS:
        assert (a["proxy"][s][:n] == b["proxy"][s][:n]).all(), s
    assert list(a["regime"][:n]) == list(b["regime"][:n]) and list(a["phase"][:n]) == list(b["phase"][:n])


def test_state_at_never_wraps_negative_index():
    st = {"day0": 100, "days": np.arange(100, 110), "regime": np.array(list("bbbbbbbbbb"), object), "proxy": {T.A_BASELINE: np.ones(10, bool)}}
    assert T.state_at(st, "regime", 50 * DAY) is None
    assert T.state_at(st, "proxy", 50 * DAY) is False
    assert T.state_at(st, "regime", 105 * DAY) == "b"


def test_atr_series_simple_mean_true_range():
    atr = T.atr_series(flat_bars(30, rng=2.0))
    assert atr[13] is None and abs(atr[14] - 2.0) < 1e-12 and abs(atr[29] - 2.0) < 1e-12


def _fake_case(path_hl, sgn):
    """15 flat bars (ATR 2), then the given (high, low) path, entry at bar 14 close 100; returns simulate()."""
    bars = flat_bars(15) + [bar(0, 100, h, l, 100) for (h, l) in path_hl] + flat_bars(12)
    for k, b in enumerate(bars):
        b["t"] = k * 900000
    return T.simulate(bars, T.atr_series(bars), 14, 100.0, sgn)


def test_fakeout_adverse_before_favourable():
    # long, ATR 2: adverse = 98, favourable = 102
    assert _fake_case([(100.5, 99.0), (100.5, 97.9), (103, 99)], +1)[1] is True          # drops to 97.9 first
    assert _fake_case([(100.5, 99.0), (102.5, 99.5), (100, 97.0)], +1)[1] is False       # target first, later drop does not count
    assert _fake_case([(103.0, 97.0)], +1)[1] is True                                      # both in one bar = adverse first
    assert _fake_case([(100.5, 99.5)], +1)[1] is False                                     # neither
    # short mirrors: adverse = 102, favourable = 98
    assert _fake_case([(102.1, 99.0)], -1)[1] is True
    assert _fake_case([(101.0, 97.9), (103.0, 99.0)], -1)[1] is False


def test_simulate_gross_return_and_skip_without_exit_bar():
    assert abs(_fake_case([(100.5, 99.5)], +1)[0]) < 1e-12                                 # flat price: 0 % gross
    bars = flat_bars(20)
    assert T.simulate(bars, T.atr_series(bars), 14, 100.0, +1) is None                     # 14 + 10 >= 20: no exit bar
    bars = flat_bars(40)
    bars[24]["c"] = 110.0
    assert abs(T.simulate(bars, T.atr_series(bars), 14, 100.0, +1)[0] - 10.0) < 1e-12      # exit = close 10 bars after entry
    assert abs(T.simulate(bars, T.atr_series(bars), 14, 100.0, -1)[0] + 10.0) < 1e-12


def _ev(i, close_b=100.0, t_close=0):
    return {"i": i, "close_b": close_b, "t_close": t_close}


def test_filter_confirm1():
    bars = flat_bars(20)
    bars[15] = bar(15 * 900000, 100, 103, 100, 102)
    assert T.entry_for("confirm1", bars, _ev(14), +1) == (15, 102)
    assert T.entry_for("confirm1", bars, _ev(14), -1) is None                              # closes up: not a short confirmation
    assert T.entry_for("none", bars, _ev(14), +1) == (14, 100)


def test_filter_volume_strictly_above_prior_mean():
    bars = flat_bars(30)
    assert T.entry_for("volume", bars, _ev(25), +1) is None                                # equal to the mean: not above
    bars[25]["v"] = 10.1
    assert T.entry_for("volume", bars, _ev(25), +1) == (25, 100.0)
    bars[25]["v"] = 10.0
    bars[26]["v"] = 1000.0                                                                  # a later bar's volume must not matter
    assert T.entry_for("volume", bars, _ev(25), +1) is None


def test_filter_htf_rsi_uses_last_closed_and_direction():
    bars = flat_bars(20)
    htf = (np.array([10.0, 20.0, 30.0]), np.array([40.0, 45.0, 44.0]))
    assert T.entry_for("htf_rsi", bars, _ev(14, t_close=25), +1, htf) == (14, 100)         # 45 > 40 rising at t=25
    assert T.entry_for("htf_rsi", bars, _ev(14, t_close=25), -1, htf) is None
    assert T.entry_for("htf_rsi", bars, _ev(14, t_close=35), -1, htf) == (14, 100)         # 44 < 45 falling at t=35
    assert T.entry_for("htf_rsi", bars, _ev(14, t_close=5), +1, htf) is None               # nothing closed yet


def test_filter_retest_waits_for_pullback_then_stops_after_n():
    bars = flat_bars(14) + [bar(k * 900000, 105, 106, 104, 105) for k in range(14, 40)]
    assert T.entry_for("retest", bars, _ev(14, 100.0), +1) is None                         # level 100 never touched
    bars[20] = bar(20 * 900000, 105, 106, 99.0, 104)
    assert T.entry_for("retest", bars, _ev(14, 100.0), +1) == (20, 100.0)                  # fill at the level
    bars[20] = bar(20 * 900000, 105, 106, 104, 105)
    bars[30] = bar(30 * 900000, 105, 106, 99.0, 104)
    assert T.entry_for("retest", bars, _ev(14, 100.0), +1) is None                         # touch at bar 30 is beyond N = 10 from bar 14


def test_pick_floor_and_none():
    rows = [{"n": 29, "d": 40, "net": 9.0}, {"n": 50, "d": 10, "net": 8.0}, {"n": 40, "d": 30, "net": 0.1}, {"n": 60, "d": 30, "net": 0.2}]
    kf = lambda r: (r["n"], r["d"], r["net"])  # noqa: E731
    assert T.pick(rows, kf)["net"] == 0.2
    assert T.pick(rows[:2], kf) is None
    assert T.pick([{"n": 60, "d": 30, "net": float("nan")}], kf) is None


def test_power_gate_blocks_thin_cells_passes_thick_ones():
    assert T.power(0, "15m")["gate"] == "BLOCK"
    assert T.power(46, "15m")["gate"] == "BLOCK"
    assert T.power(2463, "15m")["gate"] == "PASS"
    assert T.power(1616, "1h")["gate"] == "BLOCK"
    assert T.power(10 ** 6, "1d")["gate"] == "PASS"


def test_cell_mask_and_family_size():
    reg = np.array(["bull", "range", "range"], object)
    ph = np.array(["fresh", "fresh", "mature"], object)
    assert T.cell_mask(reg, ph, "range|mature").tolist() == [False, False, True]
    assert T.cell_mask(reg, ph, "ALL").all()
    assert len(T.A_SETTINGS) == 24 and T.FAMILY_M == 11 and len(T.CELLS) == 7


def test_loader_never_returns_bar_at_or_after_end(tmp_path):
    d = tmp_path / "BTCUSDT" / "1d" / "klines"
    d.mkdir(parents=True)
    (d / "x.csv").write_text("\n".join("%d,1,2,0.5,1.5,10,0,0,0,0,0,0" % (k * DAY) for k in range(10)) + "\n")
    bars = T.L.load_spot("1d", 5 * DAY, root=str(tmp_path))
    assert len(bars) == 5 and bars[-1]["t"] < 5 * DAY
