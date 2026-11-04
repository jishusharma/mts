"""Wiring tests for wavetrend_c30_retest_2026-11-04 (hand arithmetic, never read back from study.py):
dot detection in the band, as-of causality (planted future bar changes nothing), session routing, retest entry
(signal bar never fills, gap fills at the open), RSI / divergence confluence, trend gate, window guards."""
import importlib.util
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("wt_c30_study", HERE / "study.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)

DAY = study.DAY
HOUR = 3600000


def test_dot_only_inside_band():
    # wt1 below wt2 for bars 0,1; bar 2 wt1 = -58 > wt2 = -60 -> up-cross at -58 <= -53: buy dot at i=2
    assert study.find_dots([-70, -65, -58, -50], [-60, -60, -60, -60]) == [(2, 1)]
    # same cross at -10 is outside the band: no dot
    assert study.find_dots([-30, -20, -10, -5], [-15, -15, -15, -15]) == []
    # down-cross at +57 >= 53 is a sell dot
    assert study.find_dots([70, 65, 57, 50], [60, 60, 60, 60]) == [(2, -1)]
    # up-cross at exactly -53 counts (<=), at -52.9 does not
    assert study.find_dots([-60, -53.0], [-55, -55]) == [(1, 1)]
    assert study.find_dots([-60, -52.9], [-55, -55]) == []


def _bars(n, shock=None):
    rnd = random.Random(11)
    out, c = [], 100.0
    for k in range(n):
        c = c * (1 + rnd.gauss(0, 0.01))
        out.append({"t": k * HOUR, "o": c, "h": c + 1, "l": c - 1, "c": c})
    if shock is not None:
        out.append({"t": n * HOUR, "o": shock, "h": shock * 1.2, "l": shock * 0.8, "c": shock})
    return out


def test_dots_ignore_future_bars():
    base = study.dots_for(_bars(1500), "1h")
    more = study.dots_for(_bars(1500, shock=1.0), "1h")
    assert len(base) >= 4
    assert [d for d in more if d["i"] < 1500] == base          # a dot on bar i reads bars <= i only
    assert all(d["t_close"] == d["i"] * HOUR + HOUR for d in base)


def test_session_routing_partitions_events():
    # cutoffs 08 / 13 / 21 UTC; 2024-01-01 00:00 UTC = 1704067200 s
    day0 = 1704067200
    for hour, want in ((3, "asia"), (7, "asia"), (8, "london"), (12, "london"), (13, "ny"), (20, "ny"), (21, "late"), (23, "late")):
        assert study.session_of_ms((day0 + hour * 3600 + 60) * 1000) == want
    evs = [{"t_close": (day0 + h * 3600 + 60) * 1000} for h in (1, 9, 14, 22, 2)]
    parts = [study.by_session(evs, s) for s in study.SESSIONS]
    assert sorted(len(p) for p in parts) == [1, 1, 1, 2]      # asia 2 (01,02), london 1, ny 1, late 1
    assert len(study.by_session(evs, "ALL")) == 5


def test_retest_level_is_bar_midpoint_and_signal_bar_never_fills():
    bars = [{"t": k * HOUR, "o": 100.0, "h": 102.0, "l": 98.0, "c": 101.0} for k in range(40)]
    bars[5].update(l=50.0, h=104.0)                            # midpoint (50 + 104) / 2 = 77; own range must not fill
    ev = [{"i": 5, "side": 1, "t_close": 6 * HOUR}]
    assert study.level_of(bars[5]) == 77.0
    trs, nsig = study.trades_for(ev, bars, "retest", h=10, n=6)
    assert nsig == 1 and trs == []                             # bars 6..11 low 98 > 77: no retest, skipped
    bars[8]["l"] = 70.0                                        # retest on bar 8: fills at 77 (open 100 > level)
    trs, _ = study.trades_for(ev, bars, "retest", h=10, n=6)
    assert len(trs) == 1 and abs(trs[0]["gross"] - (101.0 - 77.0) / 77.0 * 100) < 1e-9   # exit close of bar 18 = 101
    # sell mirror: level = midpoint (130 + 96) / 2 = 113, bar 7 opens 118 above it -> fill at the open 118
    sb = [{"t": k * HOUR, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0} for k in range(40)]
    sb[5].update(h=130.0, l=96.0)
    sb[7].update(o=118.0, h=120.0)
    trs, _ = study.trades_for([{"i": 5, "side": -1, "t_close": 6 * HOUR}], sb, "retest", h=10, n=6)
    assert abs(trs[0]["gross"] - (118.0 - 100.0) / 118.0 * 100) < 1e-9   # short 118 -> exit 100: +15.254 %


def test_signal_entry_is_dot_bar_close_and_window_filter():
    bars = [{"t": k * HOUR, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0 + k} for k in range(30)]
    ev = [{"i": 4, "side": 1, "t_close": 5 * HOUR}, {"i": 20, "side": 1, "t_close": 21 * HOUR}]
    trs, nsig = study.trades_for(ev, bars, "signal", h=5)      # entry close 104, exit close of bar 9 = 109
    assert nsig == 2 and abs(trs[0]["gross"] - (109 - 104) / 104 * 100) < 1e-9
    trs, nsig = study.trades_for(ev, bars, "signal", h=5, lo_ms=10 * HOUR)
    assert nsig == 1 and len(trs) == 1
    trs, _ = study.trades_for([{"i": 28, "side": 1, "t_close": 29 * HOUR}], bars, "signal", h=5)
    assert trs == []                                           # no exit bar in the data: dropped, not padded


def test_confluence_rsi_level_and_divergence_proximity():
    rsi = [50.0, 39.9, 40.0, 40.1, 60.0, 60.1, 59.9]
    assert [study.rsi_ok(rsi, i, 1) for i in range(7)] == [False, True, True, False, False, False, False]    # buy: RSI <= 40
    assert [study.rsi_ok(rsi, i, -1) for i in range(7)] == [False, False, False, False, True, True, False]  # sell: RSI >= 60
    # a divergence event stamped on bar 10 is visible to dots on bars 10..13, not 9 (future) and not 14 (stale)
    assert [study.div_ok({10}, i) for i in (9, 10, 11, 12, 13, 14)] == [False, True, True, True, True, False]


def test_trend_gate_labels():
    assert study.gate_label("above", 1) == "with" and study.gate_label("below", 1) == "against"
    assert study.gate_label("below", -1) == "with" and study.gate_label("above", -1) == "against"
    assert study.gate_label(None, 1) == "none"


def test_context_cache_is_as_of_and_planted_future_changes_nothing():
    n = 400
    td = [(k + 1) * DAY for k in range(n)]
    cd = [100.0 + k for k in range(n)]
    tw = [(7 * k + 7) * DAY for k in range(n // 7)]
    tm = [(30 * k + 30) * DAY for k in range(n // 30)]
    base = ((td, cd), (tw, [70.0] * len(tw)), (tm, [70.0] * len(tm)))
    plant = ((td + [(n + 1) * DAY], cd + [1.0]), (tw + [(n + 7) * DAY], [70.0] * len(tw) + [10.0]),
             (tm + [(n + 30) * DAY], [70.0] * len(tm) + [10.0]))
    t = 300 * DAY + 5
    a = study.make_ctx_at(*base)(t)
    assert a["side"] == "above" and a["regime"] == "bull"
    assert study.make_ctx_at(*plant)(t) == a


def test_windows_never_reach_holdout_and_validation_is_read_once(tmp_path):
    import pandas as pd
    lo, hi = study.window("dev")
    assert hi == study.ms(pd.Timestamp("2024-07-01")) and lo == study.ms(pd.Timestamp("2022-01-01"))
    lo, hi = study.window("val")
    assert hi == study.ms(pd.Timestamp("2025-07-01"))          # HOLDOUT starts here; the loader end is never past it
    assert study.val_guard(tmp_path, []) == "no_survivors"
    assert study.val_guard(tmp_path, [["15m", "buy"]]) == "ok"
    (tmp_path / "val_cells.csv").write_text("x")
    assert study.val_guard(tmp_path, [["15m", "buy"]]) == "already_read"


def test_survivor_rule():
    ok = {"n": 40, "days": 25, "net": 0.1, "holm_p": 0.01, "excess_t": 2.5}
    assert study.is_survivor(ok)
    for k, v in (("n", 29), ("days", 19), ("net", -0.01), ("holm_p", 0.06), ("excess_t", 1.9)):
        assert not study.is_survivor({**ok, k: v})
    assert not study.is_survivor({**ok, "excess_t": float("nan")})
