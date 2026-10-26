"""Look-ahead and hand-computed fixtures for candidates.py (PRE_REG.md in this folder)."""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidates as C  # noqa: E402

MS5 = 300_000
T0 = 1_717_200_000_000  # 2024-06-01 00:00 UTC


def bar(i, o, h, l, c, v=100.0, tb=50.0):
    return {"t": T0 + i * MS5, "close_ms": T0 + (i + 1) * MS5, "o": o, "h": h, "l": l, "c": c, "v": v, "tb": tb}


def flat_bars(n, px=100.0):
    return [bar(i, px, px + 1, px - 1, px) for i in range(n)]


def oi_from(values):
    """OI stamped at each bar open so it is usable by the bar closing one bar later (D2 lag = 5 min)."""
    return {T0 + i * MS5: float(v) for i, v in enumerate(values)}


def test_atr_plain_sma_hand_computed():
    # FORMULAS.md s12 example shape: TR = max(h-l, |h-pc|, |l-pc|); SMA over 14.
    bars = [bar(0, 10, 10, 10, 10)]
    trs = []
    prev = 10.0
    for i in range(1, 16):
        h, l, c = prev + 2, prev - 1, prev + 1
        bars.append(bar(i, prev, h, l, c))
        trs.append(max(h - l, abs(h - prev), abs(l - prev)))  # always 3
        prev = c
    assert C.atr(bars, 15, 14) == 3.0
    assert C.atr(bars, 5, 14) is None


def test_oi_slope_flip_fires_once():
    # price falling 100->..., OI rises then turns down: slope flips + to - exactly once.
    n = 30
    bars = [bar(i, 100 - i * 0.1, 101 - i * 0.1, 99 - i * 0.1, 100 - i * 0.1) for i in range(n)]
    vals = [1000 + i * 5 for i in range(20)] + [1100 - (i - 19) * 5 for i in range(20, n)]
    oi = oi_from(vals)
    fires = [f for f in C.candidates(bars, oi) if f["name"] == "oi_flip"]
    assert len(fires) == 1, fires
    assert fires[0]["side"] == "BOTTOM"  # price fell over L bars


def test_lookahead_changing_future_bar_leaves_candidates_unchanged():
    n = 80
    bars = []
    px = 100.0
    for i in range(n):
        px += (1 if (i // 7) % 2 == 0 else -1) * 0.4
        bars.append(bar(i, px, px + 0.6, px - 0.6, px, v=100 + (400 if i % 11 == 0 else 0), tb=30 + (i % 5) * 20))
    oi = oi_from([1000 + 30 * ((i // 6) % 2 * 2 - 1) * (i % 6) for i in range(n)])
    base = C.candidates(bars, oi)
    assert base, "fixture must fire something"
    for cut in (40, 55, 70):
        mod = copy.deepcopy(bars)
        for j in range(cut + 1, n):
            mod[j].update(o=500.0, h=900.0, l=1.0, c=777.0, v=1e6, tb=1.0)
        oi2 = dict(oi)
        for j in range(cut + 1, n):
            oi2[T0 + j * MS5] = 1e9
        a = [f for f in base if f["i"] <= cut]
        b = [f for f in C.candidates(mod, oi2) if f["i"] <= cut]
        assert a == b, (cut, a, b)


def test_oi_lag_blocks_same_bar_stamp():
    # OI stamped at the bar's own close time must not be usable by that bar (needs stamp <= close_ms - 5 min).
    bars = flat_bars(5)
    oi = {bars[4]["close_ms"]: 5.0, bars[3]["close_ms"]: 4.0}
    assert C.oi_at(oi, bars[4]["close_ms"]) is None or C.oi_at(oi, bars[4]["close_ms"]) == 4.0
    assert C.oi_at(oi, bars[4]["close_ms"]) != 5.0


def test_swing_label_uses_bars_through_j_plus_2_only():
    lows = [5, 4, 3, 1, 2, 4, 6]
    bars = [bar(i, 10, 12, lw, 10) for i, lw in enumerate(lows)]
    assert C.swing_label(bars, 3) == "low"
    mod = copy.deepcopy(bars)
    mod[6].update(l=-100.0, h=999.0)  # bar j+3 changes: label unchanged
    assert C.swing_label(mod, 3) == "low"
    mod[5].update(l=0.5)  # bar j+2 changes: label changes
    assert C.swing_label(mod, 3) is None
    tie = copy.deepcopy(bars)
    tie[4].update(l=1)  # tie is not a pivot
    assert C.swing_label(tie, 3) is None
    assert C.swing_label(bars, 6) is None  # needs j+2 bars


def test_outcome_hit_miss_timeout_ambiguous_censored():
    # entry open of bar i+1 = 100, A = 2, k = 1 -> up barrier 102, down barrier 98.
    def mk(rows):
        return [bar(i, 100, h, l, 100) for i, (h, l) in enumerate(rows)]

    base = [(101, 99)] * 3  # signal bar 0 + two quiet horizon bars
    cases = {
        "HIT": base + [(103, 99.5)],
        "MISS": base + [(101, 97)],
        "AMBIGUOUS": base + [(103, 97)],
        "TIMEOUT": [(101, 99)] + [(101.5, 99.5)] * 3,
        "CENSORED": base,
    }
    for want, rows in cases.items():
        bars = mk(rows)
        got = C.outcome(bars, 0, 2.0, "BOTTOM", k=1.0, H=3, last_idx=len(bars) - 1)
        assert got == want, (want, got)
    # TOP mirrors: the down move is the reversal.
    assert C.outcome(mk(base + [(101, 97)]), 0, 2.0, "TOP", k=1.0, H=3, last_idx=3) == "HIT"


def test_day_clustered_se_hand_computed():
    # days: d1 n=2 h=2 ; d2 n=2 h=0 ; P = 0.5. SE = sqrt((2-0.5*2)^2 + (0-0.5*2)^2)/4 = sqrt(2)/4
    p, se = C.cluster_p_se([("d1", 1), ("d1", 1), ("d2", 0), ("d2", 0)])
    assert p == 0.5
    assert abs(se - (2 ** 0.5) / 4) < 1e-12
