"""Wiring for rsi_40_60_line_behaviour (study.py): RSI vs an independent Wilder RSI, 12h resample (complete closed buckets only), entry/side
detection, hold / break / range classification (incl. crossing count), entry at the next bar open after the classification, as-of confluence
and higher-TF bias (a planted future bar changes nothing), play direction, cushion pick, play pick, power gate, loader end.
Expected numbers are computed here independently, not from study.py."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("rsi4060_study", HERE / "study.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)
DAY, HOUR = T.DAY, T.HOUR


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


def test_rsi_arr_matches_independent_wilder():
    rng = np.random.default_rng(5)
    closes = list(100 + np.cumsum(rng.normal(0, 1, 100)))
    r = T.rsi_arr(closes)
    ref = wilder_rsi(np.array(closes), 14)
    assert np.isnan(r[:14]).all()
    for k in range(14, 100):
        assert abs(r[k] - ref[k]) < 1e-9


def _h(t_hours, c=1.0):
    return {"t": t_hours * HOUR, "o": c, "h": c + 1, "l": c - 1, "c": c, "v": 1.0}


def test_resample_12h_complete_closed_buckets_only():
    bars = [_h(k, 100 + k) for k in range(24)] + [_h(k, 100 + k) for k in range(24, 29)]     # two full buckets, then 5 hours of a third
    out = T.resample_12h(bars)
    assert [b["t"] for b in out] == [0, 12 * HOUR]                                          # the 5-hour partial bucket is not published
    assert out[0]["o"] == 100 and out[0]["c"] == 111 and out[0]["h"] == 112 and out[0]["l"] == 99
    gap = [_h(k) for k in range(24) if k != 5]                                              # a missing hour: that bucket is dropped
    assert [b["t"] for b in T.resample_12h(gap)] == [12 * HOUR]


def test_find_entries_side_is_where_the_last_bar_outside_was():
    r = np.array([np.nan, 70, 61, 70, 50, 59, 50, 64, 58, 70.0])
    # line 60, c 2 -> band [58, 62]; entries: bar 2 (from above, 70 -> 61), bar 5 (from below, 50 -> 59), bar 8 (from above, 64 -> 58, edge inclusive)
    assert T.find_entries(r, 60, 2) == [(2, 1), (5, -1), (8, 1)]
    assert T.find_entries(np.array([70.0, 50.0, 70.0]), 60, 2) == []                        # jumping across the whole band never enters it
    assert T.find_entries(np.array([70.0, 62.0, 70.0]), 60, 2) == [(1, 1)]                  # the band edge (62) is inside


def _r(vals):
    return np.array(vals, float)


def test_classify_hold_break_range():
    # line 60, c 2, N 6; entry at k = 1 from above
    assert T.classify(_r([70, 61, 66, 70, 70, 70, 70, 70]), 1, 1, 60, 2, 6) == ("hold", 2, 0)             # leaves back above: bounce
    assert T.classify(_r([70, 61, 55, 50, 50, 50, 50, 50]), 1, 1, 60, 2, 6) == ("break", 2, 1)            # closes below 58: break
    assert T.classify(_r([70, 61, 59, 60, 61, 60, 59, 60]), 1, 1, 60, 2, 6) == ("range_inside", 7, 3)     # stays inside all 6 bars
    assert T.classify(_r([70, 61, 59, 61, 66, 70, 70, 70]), 1, 1, 60, 2, 6)[0] == "range_chop"            # crosses 60 twice, then exits above
    assert T.classify(_r([70, 61, 59, 61, 59, 55, 50, 50]), 1, 1, 60, 2, 6)[0] == "range_chop"            # crosses three times, exits below
    # from below: entry at k = 1, exit below = hold, exit above = break
    assert T.classify(_r([50, 59, 55, 50, 50, 50, 50, 50]), 1, -1, 60, 2, 6) == ("hold", 2, 0)
    assert T.classify(_r([50, 59, 65, 70, 70, 70, 70, 70]), 1, -1, 60, 2, 6) == ("break", 2, 1)
    assert T.classify(_r([70, 61, 66, 70]), 1, 1, 60, 2, 6) is None                                        # window does not fit: dropped


def test_classify_entry_bar_past_the_line_counts_a_crossing():
    # came from above, entry bar already below 60 (59): that is crossing 1; leaving above needs crossing 2 -> chop, not a clean hold
    assert T.classify(_r([70, 59, 66, 70, 70, 70, 70, 70]), 1, 1, 60, 2, 6) == ("range_chop", 2, 2)
    # came from above, entry bar below the line, leaves below: one crossing -> break
    assert T.classify(_r([70, 59, 55, 50, 50, 50, 50, 50]), 1, 1, 60, 2, 6) == ("break", 2, 1)


def _ser_for(r1, c_other):
    """Synthetic series: 1h bars with the given RSI (opens 100+i, closes 200+i); the other TFs carry RSI only (c_other = {tf: (tcl, r)})."""
    n = len(r1)
    bars = [{"t": i * HOUR, "o": 100.0 + i, "h": 300.0, "l": 1.0, "c": 200.0 + i, "v": 1.0} for i in range(n)]
    ser = {"1h": (bars, np.array([b["t"] + HOUR for b in bars], float), np.array(r1, float))}
    for tf, (tcl, r) in c_other.items():
        ser[tf] = ([], np.array(tcl, float), np.array(r, float))
    return ser


def _st():
    return {"day0": 0, "n": 1000, "regime": np.array(["range"] * 1000, object), "phase": np.array(["mature"] * 1000, object)}


def test_build_events_entry_is_next_bar_open_exit_n_bars_later_and_context_is_as_of():
    r1 = [70.0] * 80
    r1[10] = 61.0                                                    # entry at bar 10 (from above), bar 11 = 70 -> exits above: hold at e = 11
    others = {"4h": ([20 * HOUR, 1e15], [61.0, 0.0]),                 # the 2nd value is a planted FUTURE bar: must not be read
              "12h": ([20 * HOUR, 1e15], [70.0, 0.0]),
              "1d": ([DAY, 1e15], [61.5, 0.0])}
    # tev = bar 10 close = 11 h: no 4h/12h/1d bar is closed yet -> everything is nan -> confl 0 and htf 0
    df = T.build_events("BTCUSDT", _ser_for(r1, others), _st(), 0, 10 ** 13, combos={("1h", 60, 2)})
    assert len(df) == 1
    row = df.iloc[0]
    assert (row["origin"], row["cls"], row["confl"], row["htf"]) == (1, "hold", 0, 0)
    exp = (200.0 + (11 + 24) - (100.0 + 12)) / (100.0 + 12) * 100.0   # entry = OPEN of bar e+1 = 12, exit = CLOSE of bar e+N = 35
    assert abs(row["ret"] - exp) < 1e-12
    assert row["eday"] == 0 and row["regime"] == "range" and row["phase"] == "mature"
    # now let the 4h and 1d bars be closed at the event time: confluence counts bands (61 and 61.5 inside [58, 62]; 70 is not), htf = 4h > 50
    others2 = {"4h": ([5 * HOUR, 1e15], [61.0, 0.0]), "12h": ([5 * HOUR, 1e15], [70.0, 0.0]), "1d": ([5 * HOUR, 1e15], [61.5, 0.0])}
    row2 = T.build_events("BTCUSDT", _ser_for(r1, others2), _st(), 0, 10 ** 13, combos={("1h", 60, 2)}).iloc[0]
    assert row2["confl"] == 2 and row2["htf"] == 1


def test_build_events_window_and_availability():
    r1 = [70.0] * 80
    r1[10] = 61.0
    r1[60] = 61.0                                                    # second entry at bar 60: 60 + 24 >= 80 -> window does not fit, dropped
    others = {"4h": ([0], [50.0]), "12h": ([0], [50.0]), "1d": ([0], [50.0])}
    df = T.build_events("BTCUSDT", _ser_for(r1, others), _st(), 0, 10 ** 13, combos={("1h", 60, 2)})
    assert list(df["tev"]) == [11 * HOUR]
    lo = T.build_events("BTCUSDT", _ser_for(r1, others), _st(), 12 * HOUR, 10 ** 13, combos={("1h", 60, 2)})
    assert len(lo) == 0                                              # event closed at 11 h is before lo


def test_ctx_at_never_wraps_negative_index():
    st = {"day0": 100, "n": 10, "regime": np.array(list("bbbbbbbbbb"), object)}
    assert T.ctx_at(st, "regime", 50 * DAY) is None
    assert T.ctx_at(st, "regime", 105 * DAY) == "b"
    assert T.ctx_at(st, "regime", 110 * DAY) is None


def test_asof_vals_reads_only_closed_bars():
    ser = {"4h": ([], np.array([4 * HOUR, 8 * HOUR, 1e15]), np.array([10.0, 20.0, 99.0]))}
    v = T.asof_vals(ser, "4h", np.array([3.9 * HOUR, 4 * HOUR, 7 * HOUR, 8 * HOUR, 1e13]))
    assert np.isnan(v[0]) and v[1] == 10.0 and v[2] == 10.0 and v[3] == 20.0 and v[4] == 20.0


def test_play_direction_and_gross_sign():
    assert T.play_dir("bounce", 1) == 1 and T.play_dir("bounce", -1) == -1       # held above (came from above) -> long
    assert T.play_dir("wait", 1) == -1 and T.play_dir("wait", -1) == 1           # broke below (came from above) -> short
    import pandas as pd
    df = pd.DataFrame({"cls": ["hold", "break", "hold", "range_chop"], "origin": [1, 1, -1, 1], "ret": [2.0, 3.0, 4.0, 9.0], "eday": [1, 2, 3, 4]})
    s, g = T.play_cell(df, "bounce")
    assert list(g) == [2.0, -4.0]                                                # long +2; held below (came from below) -> short on +4 = -4
    s, g = T.play_cell(df, "wait")
    assert list(g) == [-3.0]                                                     # broke below after coming from above: short, price rose 3


def test_pick_cushion_floor_and_tie_goes_to_smaller_c():
    rows = [{"c": 1, "n": 500, "days": 100, "sep": 0.30}, {"c": 2, "n": 500, "days": 100, "sep": 0.30}, {"c": 3, "n": 99, "days": 100, "sep": 0.9},
            {"c": 5, "n": 500, "days": 39, "sep": 0.9}]
    assert T.pick_cushion(rows)["c"] == 1
    assert T.pick_cushion(rows[2:]) is None


def test_pick_plays_top_six_one_per_cell_with_floor():
    rows = []
    for i in range(8):
        rows.append({"tf": "1h", "L": 40 + i, "side": "above", "ctx": "ALL", "play": "bounce", "n": 50, "days": 30, "net": float(i)})
    rows.append({"tf": "1h", "L": 47, "side": "above", "ctx": "htf_up", "play": "wait", "n": 50, "days": 30, "net": 100.0})   # same cell as net 7
    rows.append({"tf": "4h", "L": 40, "side": "above", "ctx": "ALL", "play": "bounce", "n": 29, "days": 30, "net": 500.0})    # below the n floor
    rows.append({"tf": "4h", "L": 41, "side": "above", "ctx": "ALL", "play": "bounce", "n": 60, "days": 19, "net": 500.0})    # below the days floor
    rows.append({"tf": "4h", "L": 42, "side": "above", "ctx": "ALL", "play": "bounce", "n": 60, "days": 30, "net": float("nan")})
    got = T.pick_plays(rows)
    assert len(got) == 6 and got[0]["net"] == 100.0 and [r["L"] for r in got][1:] == [46, 45, 44, 43, 42]


def test_rates_shares_add_up_and_sep():
    import pandas as pd
    df = pd.DataFrame({"cls": ["hold"] * 5 + ["break"] * 2 + ["range_chop", "range_inside", "range_inside"], "day": list(range(10))})
    r = T.rates(df)
    assert r["n"] == 10 and abs(r["hold"] - 0.5) < 1e-12 and abs(r["brk"] - 0.2) < 1e-12 and abs(r["rng"] - 0.3) < 1e-12
    assert abs(r["hold"] + r["brk"] + r["rng"] - 1) < 1e-12 and abs(r["sep"] - 0.3) < 1e-12


def test_power_gate_blocks_thin_cells_passes_thick_ones():
    assert T.power(0, "1h")["gate"] == "BLOCK"
    assert T.power(300, "1h")["gate"] == "BLOCK"
    assert T.power(10 ** 7, "1d")["gate"] == "PASS"
    assert T.FAMILY_M == 6 and len(T.CTXS) == 10


def test_null_rates_shape():
    T.NULL_BARS = 20000
    nr = T.null_rates()
    d = nr[("1h", 60, 1, 2)]
    assert abs(d["hold"] + d["brk"] + d["rng"] - 1) < 1e-9 and d["n"] > 50


def test_loader_never_returns_bar_at_or_after_end(tmp_path):
    d = tmp_path / "BTCUSDT" / "1d" / "klines"
    d.mkdir(parents=True)
    (d / "x.csv").write_text("\n".join("%d,1,2,0.5,1.5,10,0,0,0,0,0,0" % (k * DAY) for k in range(10)) + "\n")
    bars = T.L.load_spot("1d", 5 * DAY, root=str(tmp_path))
    assert len(bars) == 5 and bars[-1]["t"] < 5 * DAY
