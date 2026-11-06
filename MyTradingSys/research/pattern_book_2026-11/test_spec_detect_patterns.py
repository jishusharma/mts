"""Spec tests for detect_patterns.py. Expected values are worked out by hand from the pattern definitions in PATTERN_BOOK.md
(Edwards & Magee measured moves, Nison candle shapes), on small synthetic fixtures; the Bible-turns test uses the committed
16-year daily history. Each test fails when the module is stubbed out."""
import datetime as dt
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detect_patterns as dp  # noqa: E402


def path(points, leg=12, wick=0.003):
    """Bars along straight legs between waypoint prices (leg bars each). o = previous close, wicks +-0.3 %."""
    closes = [points[0]]
    for a, b in zip(points, points[1:]):
        for k in range(1, leg + 1):
            closes.append(a + (b - a) * k / leg)
    bars, pc = [], closes[0]
    for i, c in enumerate(closes):
        o = pc
        bars.append({"t": i * 3600000, "o": o, "h": max(o, c) * (1 + wick), "l": min(o, c) * (1 - wick), "c": c, "v": 1.0})
        pc = c
    return bars


def pats(bars, name, scales=(1.5,), tf="1h"):
    return [r for r in dp.detect_chart_patterns(bars, tf, scales) if r["pattern"] == name]


def test_swings_alternate_and_are_causal():
    bars = path([100, 120, 100, 120, 100], leg=15)
    piv, prov = dp.swings(bars, 2.0)
    assert [p["kind"] for p in piv] == ["L", "H", "L", "H"]     # bar 0 is the first extreme of the series
    assert all(p["conf"] > p["i"] for p in piv)          # confirmed only after the retrace, never at the extreme
    assert abs(piv[0]["price"] - 100 * 0.997) < 0.01 and abs(piv[1]["price"] - 120 * 1.003) < 0.01
    assert prov["kind"] == "L"


def test_double_top_confirmed_and_target():
    bars = path([100, 150, 120, 150.4, 105])
    r = pats(bars, "double_top")
    assert len(r) == 1 and r[0]["status"] == "confirmed"
    top, neck = 150.4 * 1.003, 120 * 0.997
    assert abs(r[0]["neck"] - neck) < 0.01
    assert abs(r[0]["target"] - (neck - (top - neck))) < 0.6     # Edwards & Magee: neckline minus pattern height
    assert abs(r[0]["invalid"] - top) < 0.6 and r[0]["bias"] == "bear"


def test_double_top_forming_then_failed():
    forming = pats(path([100, 150, 120, 150.4, 140]), "double_top")
    assert len(forming) == 1 and forming[0]["status"] == "forming"
    failed = pats(path([100, 150, 120, 150.4, 140, 165]), "double_top")
    assert len(failed) == 1 and failed[0]["status"] == "failed"   # close above the top before the neckline broke


def test_double_bottom_mirror():
    r = pats(path([150, 100, 130, 99.8, 145]), "double_bottom")
    assert len(r) == 1 and r[0]["status"] == "confirmed" and r[0]["bias"] == "bull"
    low, neck = 99.8 * 0.997, 130 * 1.003
    assert abs(r[0]["target"] - (neck + (neck - low))) < 0.6


def test_head_and_shoulders_top():
    bars = path([100, 130, 115, 150, 115, 130, 95])
    r = pats(bars, "head_shoulders_top")
    assert len(r) == 1 and r[0]["status"] == "confirmed"
    neck = 115 * 0.997
    assert abs(r[0]["lines"][0]["p1"] - neck) < 0.01 and abs(r[0]["lines"][0]["p2"] - neck) < 0.01
    assert abs(r[0]["target"] - (neck - (150 * 1.003 - neck))) < 0.8
    assert pats(path([100, 130, 115, 150, 115, 150.3, 95]), "head_shoulders_top") == []   # equal "shoulder" and head: no head


def test_inverse_head_and_shoulders():
    r = pats(path([150, 120, 135, 100, 135, 120, 160]), "head_shoulders_bottom")
    assert len(r) == 1 and r[0]["status"] == "confirmed" and r[0]["bias"] == "bull"


def test_ascending_triangle_and_trigger():
    bars = path([100, 120, 104, 120, 109, 120, 113, 120, 116, 120, 119.5], leg=14, wick=0.001)
    r = pats(bars, "ascending_triangle", scales=(1.2,))
    assert len(r) >= 1 and r[0]["bias"] == "bull"
    up = [l for l in r[0]["lines"] if l["name"] == "upper"][0]
    assert abs(up["p1"] - 120 * 1.001) < 0.05 and abs(up["p2"] - 120 * 1.001) < 0.05   # flat resistance
    assert r[0]["status"] == "forming"
    assert abs(r[0]["trigger"] - 120 * 1.001) < 0.3                                      # long trigger = a close above it


def test_broken_triangle_reports_the_realised_side():
    bars = path([100, 120, 104, 120, 109, 120, 113, 120, 116, 120, 118], leg=14, wick=0.001)   # ends under the rising floor
    r = pats(bars, "ascending_triangle", scales=(1.2,))
    assert r and r[0]["status"] == "breakout_down"
    lo = [l for l in r[0]["lines"] if l["name"] == "lower"][0]
    assert abs(r[0]["trigger"] - dp.line_at(lo, r[0]["confirm_i"])) < 1e-6    # trigger = the floor at the break bar
    assert r[0]["target"] < r[0]["trigger"]                                    # target is below, by the pattern height


def test_rising_and_falling_wedge_bias():
    rw = pats(path([100, 120, 112, 128, 122, 134, 130, 138, 135.5, 140], leg=14, wick=0.001), "rising_wedge", scales=(1.2,))
    assert rw and rw[0]["bias"] == "bear"
    fw = pats(path([140, 120, 128, 112, 118, 106, 110, 102, 104, 100.5], leg=14, wick=0.001), "falling_wedge", scales=(1.2,))
    assert fw and fw[0]["bias"] == "bull"


def test_break_vs_fakeout_vs_pullback():
    def run(closes):
        bars = [{"t": i, "o": c, "h": c, "l": c, "c": c, "v": 1} for i, c in enumerate(closes)]
        return dp.break_after(bars, 0, lambda i: 100.0, None, 3, 0.02)
    assert run([99, 99, 101, 102, 103, 104]) == ("up", 2, False)        # real breakout: holds above
    assert run([99, 99, 101, 99.5, 99, 99])[2] is True                  # +1 % poke, back inside next bar: fakeout
    assert run([99, 99, 110, 99.5, 99, 99])[2] is False                 # +10 % excursion that returns = pullback, not fakeout
    assert run([99, 98, 97])[0] is None


def trend_down(n=14, start=120.0, step=1.5):
    bars, c = [], start
    for i in range(n):
        o, c = c, c - step
        bars.append({"t": i, "o": o, "h": o + 0.2, "l": c - 0.2, "c": c, "v": 1})
    return bars


def mirror(bars, k=240.0):
    return [dict(x, o=k - x["o"], c=k - x["c"], h=k - x["l"], l=k - x["h"]) for x in bars]


def with_tail(prefix, tail):
    return [dict(b, t=i) for i, b in enumerate(prefix + tail)]


def names_at(bars, i):
    return {e["name"] for e in dp.candle_patterns(bars) if e["i"] == i and e["trend_ok"]}


def test_candle_hammer_and_hanging_man_need_the_trend():
    down = trend_down()
    last = down[-1]["c"]                                   # 99.0
    hammer = {"t": 0, "o": last, "h": last + 0.5, "l": last - 5, "c": last + 0.5, "v": 1}   # body .5, lower 5, upper 0
    b = with_tail(down, [hammer])
    assert "hammer" in names_at(b, len(b) - 1)
    up = mirror(down)
    uh = {"t": 0, "o": up[-1]["c"], "h": up[-1]["c"] + 0.5, "l": up[-1]["c"] - 5, "c": up[-1]["c"] + 0.5, "v": 1}
    b2 = with_tail(up, [uh])
    assert "hanging_man" in names_at(b2, len(b2) - 1) and "hammer" not in names_at(b2, len(b2) - 1)


def test_candle_shooting_star_and_engulfing_and_stars():
    up = mirror(trend_down())
    top = up[-1]["c"]
    star = {"t": 0, "o": top, "h": top + 5, "l": top - 0.2, "c": top - 0.5, "v": 1}
    b = with_tail(up, [star])
    assert "shooting_star" in names_at(b, len(b) - 1)
    down = trend_down()
    p = down[-1]["c"]
    red = {"t": 0, "o": p + 1, "h": p + 1.2, "l": p - 0.2, "c": p, "v": 1}
    eng = {"t": 0, "o": p - 0.3, "h": p + 2.5, "l": p - 0.5, "c": p + 2.2, "v": 1}      # body 2.5 swallows the red body 1.0
    b = with_tail(down, [red, eng])
    assert "bullish_engulfing" in names_at(b, len(b) - 1)
    first = {"t": 0, "o": p + 4, "h": p + 4.1, "l": p - 0.1, "c": p, "v": 1}           # long red
    small = {"t": 0, "o": p - 0.2, "h": p + 0.3, "l": p - 0.6, "c": p - 0.1, "v": 1}    # small body (0.1 <= 0.3 x 4)
    third = {"t": 0, "o": p, "h": p + 3.5, "l": p - 0.1, "c": p + 3.2, "v": 1}          # closes above the first body's midpoint p+2
    b = with_tail(down, [first, small, third])
    assert "morning_star" in names_at(b, len(b) - 1)


def test_candle_three_soldiers_and_doji():
    base = trend_down()
    p = base[-1]["c"]
    s = [{"t": 0, "o": p, "h": p + 2.1, "l": p - 0.1, "c": p + 2, "v": 1},
         {"t": 0, "o": p + 1, "h": p + 4.1, "l": p + 0.9, "c": p + 4, "v": 1},
         {"t": 0, "o": p + 3, "h": p + 6.1, "l": p + 2.9, "c": p + 6, "v": 1}]
    b = with_tail(base, s)
    assert "three_white_soldiers" in names_at(b, len(b) - 1)
    d = {"t": 0, "o": p, "h": p + 2, "l": p - 2, "c": p + 0.2, "v": 1}                 # body 0.2 <= 10 % of range 4
    b = with_tail(base, [d])
    assert "doji" in names_at(b, len(b) - 1)


def test_candle_next_stats_counts_hits():
    bars = [{"t": i, "o": 1, "h": 1, "l": 1, "c": c, "v": 1} for i, c in enumerate([10, 11, 12, 11, 12, 13, 12])]
    ev = [{"i": 0, "name": "x", "bias": "bull", "trend_ok": True}, {"i": 2, "name": "x", "bias": "bull", "trend_ok": True},
          {"i": 5, "name": "x", "bias": "bull", "trend_ok": True}, {"i": 3, "name": "y", "bias": "bear", "trend_ok": True}]
    st, base = dp.candle_next_stats(bars, ev)
    assert st["x"] == {"n": 3, "rate": 1 / 3, "bias": "bull"}          # next close up after bar 0 yes, bar 2 no, bar 5 no
    assert st["y"]["n"] == 1 and st["y"]["rate"] == 0.0                 # bar 3 -> bar 4 is up, a bear call misses
    assert abs(base - 4 / 6) < 1e-9                                     # 4 of the 6 steps are up (10-11, 11-12, 11-12, 12-13)


def fractal_fixture(pivots, n, side="resistance", close=95.0):
    """Flat bars (high 91, low 89, close 95 clipped into the range) with a spike high (or low) at each pivot index."""
    bars = []
    for i in range(n):
        h, l = 91.0, 89.0
        if i in pivots:
            if side == "resistance":
                h = pivots[i]
            else:
                l = pivots[i]
        bars.append({"t": i, "o": close, "h": max(h, close), "l": min(l, close), "c": close, "v": 1})
    return bars


def test_strip_trendline_three_touch_resistance():
    # highs at bars 10, 20, 30 on a log-line (100 -> 110 -> 121: +10 % per 10 bars); last bar 44, close 95
    bars = fractal_fixture({10: 100.0, 20: 110.0, 30: 121.0}, 45)
    t = dp.strip_trendline(bars, "resistance")
    assert t["touches"] == 3
    want = 100 * 1.1 ** ((44 - 10) / 10)
    assert abs(t["value"] - want) < 1e-6
    assert abs(t["dist_pct"] - (95 - want) / 95 * 100) < 1e-6
    assert abs(t["slope_pct_per_bar"] - math.log(1.1) / 10 * 100) < 1e-9


def test_strip_trendline_two_touch_fallback_and_broken():
    t = dp.strip_trendline(fractal_fixture({10: 100.0, 20: 108.0, 30: 140.0}, 45), "resistance")   # middle is 3 % off the line
    assert t["touches"] == 2 and t["i1"] == 20 and t["i2"] == 30
    broken = fractal_fixture({10: 100.0, 20: 110.0, 30: 121.0}, 45)
    broken[40] = dict(broken[40], c=300.0, h=300.0)                                                  # close through the line
    assert dp.strip_trendline(broken, "resistance") is None


def test_strip_trendline_support_rising_low_line_is_below_price():
    bars = fractal_fixture({10: 80.0, 20: 84.0, 30: 88.2}, 45, side="support", close=95.0)           # +5 % per 10 bars
    t = dp.strip_trendline(bars, "support")
    assert t["touches"] == 3 and t["value"] < 95 and t["dist_pct"] > 0
    assert abs(t["value"] - 80 * 1.05 ** 3.4) < 1e-6


def test_core_trendlines_find_the_rising_support():
    # lows exactly on a log line (80 x 1.05^k, a trough every 24 bars), highs flat at 120: a textbook up-trend line with 5 touches
    pts = []
    for k in range(7):
        pts += [80 * 1.05 ** k, 120]
    bars = path(pts, leg=12, wick=0.003)
    for i in range(0, len(bars), 12):      # the turning bars get the longer wick, so every pivot is strict (no ties)
        if (i // 12) % 2 == 0:
            bars[i]["l"] = bars[i]["c"] * 0.99
        else:
            bars[i]["h"] = bars[i]["c"] * 1.01
    out = dp.core_trendlines(bars, "1h")
    sup = [x for x in out if x["side"] == "support"]
    assert sup and sup[0]["p2"] > sup[0]["p1"] and 0 < sup[0]["dist_pct"] < 40 and sup[0]["value"] < bars[-1]["c"]
    ratio = sup[0]["p2"] / sup[0]["p1"]
    assert abs(ratio - 1.05 ** round(math.log(ratio) / math.log(1.05))) < 1e-6      # anchors are two of the exact trough lows


def found(history, pattern, d1, d2, tol_days=3):
    """The detection of `pattern` at any scale whose first and last extreme are within tol_days of d1 and d2, else None."""
    atrp = dp.atr_pct(history)
    day = 86400000
    t1 = int(dt.datetime.fromisoformat(d1).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    t2 = int(dt.datetime.fromisoformat(d2).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    s = 1 if pattern == "double_top" else -1
    for sc in (2, 3, 4, 5, 6, 8, 12):
        piv, _ = dp.swings(history, sc, atrp)
        for r in dp.double_tops(history, piv, s, "1d", sc, atrp):
            if abs(r["points"][0]["t"] - t1) <= tol_days * day and abs(r["points"][2]["t"] - t2) <= tol_days * day:
                return r
    return None


def test_bible_turns_are_found_on_the_history():
    h = dp.load_history()
    assert found(h, "double_top", "2021-04-14", "2021-11-10")          # Bible s2: top 2021, 64,854 / 69,000
    assert found(h, "double_top", "2025-08-14", "2025-10-06")          # top 2025, 124,474 / 126,200
    assert found(h, "double_bottom", "2018-12-15", "2019-01-29")       # bottom 2018-19, 3,156 / 3,350
    assert found(h, "double_bottom", "2022-06-18", "2022-11-21")       # bottom 2022, 17,622 / 15,476 (second lower)
    assert found(h, "double_bottom", "2026-02-06", "2026-07-01")       # bottom 2026, 60,000 / 57,800 (second lower)
    r = found(h, "double_top", "2021-04-14", "2021-11-10")
    assert abs(r["neck"] - 28805) < 1 and r["status"] in ("confirmed", "target_hit")
