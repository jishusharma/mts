"""Tests for level_delta_log.py (offline reclaim + delta-at-level logger). Numbers are hand-computed on planted series."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("level_delta_log", HERE / "level_delta_log.py")
ldl = importlib.util.module_from_spec(_spec)
sys.modules["level_delta_log"] = ldl
_spec.loader.exec_module(ldl)

M5 = 300000
T0 = 1_700_000_000_000 // 86400000 * 86400000 + 8 * 3600000   # a UTC day, 08:00 (london block)
LVL = 80900.0


def b5(i, h, l, c):
    return {"t": T0 + i * M5, "o": c, "h": h, "l": l, "c": c}


def test_one_reclaim_one_knife():
    # reclaim: bar2 probes above 80900, bar3 closes back below -> 1 event (short, kind range_hi)
    bars = [b5(0, 80800, 80700, 80750), b5(1, 80850, 80750, 80800), b5(2, 81000, 80800, 80950),
            b5(3, 80950, 80700, 80800), b5(4, 80850, 80750, 80800)]
    ev = ldl.find_reclaims(bars, [(LVL, "range_hi")])
    assert len(ev) == 1
    e = ev[0]
    assert (e["level"], e["kind"], e["side"], e["session"], e["extreme"]) == (LVL, "range_hi", "short", "london", 81000.0)
    assert e["ts"] == bars[3]["t"] + M5      # decision time = close of the reclaim bar
    # knife: probe above and never close back inside within 3 bars
    knife = [b5(0, 80800, 80700, 80750), b5(1, 81000, 80800, 80950), b5(2, 81100, 80950, 81050),
             b5(3, 81200, 81050, 81150), b5(4, 81250, 81100, 81200), b5(5, 81100, 80700, 80800)]
    assert ldl.find_reclaims(knife, [(LVL, "range_hi")]) == []


def test_low_side_reclaim_is_long():
    lo = 75400.0
    bars = [b5(0, 75600, 75500, 75550), b5(1, 75550, 75300, 75350), b5(2, 75600, 75350, 75500)]
    ev = ldl.find_reclaims(bars, [(lo, "range_lo")])
    assert len(ev) == 1 and ev[0]["side"] == "long" and ev[0]["extreme"] == 75300.0


def test_only_london_ny_sessions_logged():
    # same planted reclaim but at 02:00 UTC (asia) -> not logged
    shift = -6 * 3600000
    bars = [dict(b, t=b["t"] + shift) for b in [b5(0, 80800, 80700, 80750), b5(1, 81000, 80800, 80950), b5(2, 80950, 80700, 80800)]]
    assert ldl.find_reclaims(bars, [(LVL, "range_hi")]) == []


def of(i, delta, cvd):
    return {"t": T0 + i * 60000, "delta": delta, "cvd_day": cvd}


def test_delta_window_sum_and_missing_minute():
    ts = T0 + 15 * 60000                      # window = minutes 0..14, bar = minutes 10..14
    bars = [of(i, 1.0 + i, 10.0 + sum(1.0 + k for k in range(i + 1))) for i in range(15)]
    r = ldl.delta_at(bars, ts)
    assert abs(r["delta_15m"] - sum(1.0 + i for i in range(15))) < 1e-9          # 120
    assert abs(r["delta_bar"] - sum(1.0 + i for i in range(10, 15))) < 1e-9      # 60
    assert abs(r["cvd_chg"] - 120.0) < 1e-9
    gap = [x for x in bars if x["t"] != T0 + 7 * 60000]
    r = ldl.delta_at(gap, ts)
    assert r["delta_15m"] is None and r["cvd_chg"] is None and r["delta_bar"] is not None   # never 0
    gap2 = [x for x in bars if x["t"] != T0 + 12 * 60000]
    assert ldl.delta_at(gap2, ts)["delta_bar"] is None


def test_duplicate_append_adds_nothing(tmp_path):
    p = tmp_path / "LOG.csv"
    row = {"ts": 1, "level": LVL, "kind": "range_hi", "side": "short", "session": "ny",
           "delta_15m": None, "delta_bar": 2.5, "cvd_chg": None}
    assert ldl.append_rows(p, [row]) == 1
    assert ldl.append_rows(p, [row]) == 0
    lines = p.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "ts,level,kind,side,session,delta_15m,delta_bar,cvd_chg" and len(lines) == 2
    assert lines[1].endswith(",,2.5,")       # missing = empty
