"""Synthetic reproduction of critical gaps in the TrendLine layer (2026-10-18).

Reads NO market data and NO VALIDATION/HOLDOUT files. Uses synthetic bars only.
Run: python MyTradingSys/research/trendlines_2026-10-17/repro_trendline_gaps.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "g3_pack"))

from MyTradingSys.backtest.layers.trendlines.trendline_core import detect  # noqa: E402
from MyTradingSys.backtest.layers.trendlines.test_trendline_core import T, scenario  # noqa: E402
import count_only as co  # noqa: E402
import g3_pack as g  # noqa: E402

HOUR = 3_600_000


def gap1_close_arm_wick_penetration():
    """Gap 1 (HIGH): close_arm='close' anchors on closes, but _penetration_ok and _advance check wicks (bar['l']/bar['h'])."""
    bars = [{"t": i * HOUR, "o": 115.0, "h": 125.0, "l": 110.0, "c": 115.0, "v": 100.0} for i in range(40)]
    # Two clean close-series swing lows at 15 (close 100) and 27 (close 106), with normal lower wicks (low = close - 5)
    bars[15]["c"], bars[15]["l"] = 100.0, 95.0
    bars[27]["c"], bars[27]["l"] = 106.0, 101.0
    det = detect(bars, price_arm="close", transform="linear")
    rej = [r for r in det.rejects if r["reject"] == "penetration" and r["ia"] == 15 and r["ib"] == 27]
    assert det.lines == {} and len(rej) == 1, (det.lines, rej)
    print("Gap 1 reproduced: close_arm='close' line rejected by wick penetration on its own anchor bars:", rej[0])


def gap2_pre_availability_replay_events():
    """Gap 2 (HIGH): _pair replays bars ib+1..ib+k (before pivot b is confirmed at ib+k), creating pre-availability
    touches/resets/breaks that make Arm A eligible at birth and count post-birth breaks in count_only.py."""
    # ia=15, ib=27 (pivot b confirmed at bar 30). Bar 28 touches, bar 29 resets -> Arm A eligible at bar 29 (known_at 30).
    # Bar 31 breaks -> count_only counts an Arm A break even though zero contacts occurred after line birth (bar 30).
    tail = [T(1), T(11), T(4), T(-6, h=4, c=-1)]  # bars 28, 29, 30, 31
    det = co.run_config(scenario(tail=tail), "1h", "wick", "linear", 500)
    lid = "1h|support|wick|linear|15|27"
    evs = [e for e in det.events if e["line"] == lid]
    _, counted, _, _ = co.count_detector(det, det.bars)
    assert any(e["state"] == "eligible" and e.get("arm") == "A" and e["bar"] == 29 and e["known_at"] == 30 for e in evs)
    assert ("A", "break", "support", "T1", 31) in counted
    print("Gap 2 reproduced: pre-availability bars 28..29 grant Arm A eligibility at birth (bar=29, known_at=30); counted:", counted)


def gap3_e11_cross_line_anchor_block():
    """Gap 3 (HIGH): _broken_anchor blocks anchor ia globally across all lines on the same side once ANY line using ia breaks."""
    bars = [{"t": i * HOUR, "o": 150.0, "h": 160.0, "l": 150.0, "c": 150.0, "v": 100.0} for i in range(60)]
    # Major swing low at 15 (100), steep inner swing low at 27 (112), break of steep line at 35 (close 115, low 114),
    # later higher low at 40 (106) that would form a valid shallow outer line (15, 40) from 100 to 106.
    bars[15]["l"] = 100.0
    bars[27]["l"] = 112.0
    bars[35]["l"], bars[35]["c"] = 114.0, 115.0
    bars[40]["l"] = 106.0
    det = detect(bars, transform="linear")
    assert "1h|support|wick|linear|15|27" in det.lines
    assert det.lines["1h|support|wick|linear|15|27"]["broken_at"] == 35
    assert "1h|support|wick|linear|15|40" not in det.lines
    print("Gap 3 reproduced: broken inner line (15,27) blocks formation of outer fan line (15,40); lines:", list(det.lines))


def gap4_count_only_multi_touch_and_lookahead_terciles():
    """Gap 4 (MEDIUM): count_only.py counts every subsequent touch episode on the same line (not just first return)
    and computes slope terciles over the full DEV sample rather than causally at event time."""
    tail = [T(4), T(4), T(4), T(1), T(11), T(1), T(11), T(1), T(-6, h=4, c=-1)]
    det = co.run_config(scenario(tail=tail), "1h", "wick", "linear", 500)
    _, counted, _, _ = co.count_detector(det, det.bars)
    a_touches = [e for e in counted if e[0] == "A" and e[1] == "touch"]
    assert len(a_touches) == 2, a_touches
    # Full-sample tercile look-ahead: adding later lines changes the tercile label of line (15, 27)
    b = scenario(ia=15, tail=[T(4)] * 60)
    b[27]["l"], b[50]["l"], b[62]["l"], b[75]["l"], b[87]["l"] = 104.0, 110.0, 122.0, 125.0, 145.0
    t_cut = co.count_detector(co.run_config(b[:45], "1h", "wick", "linear", 500), b[:45])[0][0]["tercile"]
    t_full = co.count_detector(co.run_config(b, "1h", "wick", "linear", 500), b)[0][0]["tercile"]
    assert (t_cut, t_full) == ("T1", "T2"), (t_cut, t_full)
    print(f"Gap 4 reproduced: {len(a_touches)} touches counted on 1 line; slope tercile shifted {t_cut} -> {t_full} with future bars")


def gap5_g3_prefilter_offchart_anchors():
    """Gap 5 (MEDIUM): g3_pack.py swings() searches back i - 260 bars while TL-4H shows 200 bars and TL-1D shows 180 bars."""
    B = [
        {
            "t": k * g.DAY,
            "o": 30000.0 * (1.003 ** k) * 1.02,
            "h": 30000.0 * (1.003 ** k) * 1.04,
            "l": (30000.0 * (1.003 ** k) if k in (10, 40, 220) else 30000.0 * (1.003 ** k) * 1.03),
            "c": 30000.0 * (1.003 ** k) * 1.02,
            "vol": 10.0,
        }
        for k in range(300)
    ]
    # At decision bar i=250 on TL-1D (180 bars shown: indices 71..250), anchors 10 and 40 are off-chart (< 71)
    tag = g.pf_line(B, 250)
    vis_start = 250 - g.UNITS["TL1D"]["shown"] + 1
    assert tag == "support" and 10 < vis_start and 40 < vis_start
    print(f"Gap 5 reproduced: g3_pack pf_line(250)='{tag}' using anchors at 10,40 outside visible TL-1D window [{vis_start}..250]")


def gap6_daily_ledger_schema_v2_drift():
    """Gap 6 (MEDIUM): daily/ledger.jsonl rows lack TRENDLINE_CONTRACT.md section 8 schema v2 fields."""
    ledger = HERE / "daily" / "ledger.jsonl"
    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    v2_required = {"captured_utc", "content_sha256", "selection_string", "selection_list_version", "geometry_source", "record_sha256"}
    missing_all = [v2_required - set(r.keys()) for r in rows]
    assert all(len(m) >= 5 for m in missing_all)
    assert not (HERE / "daily" / "SELECTION_STRINGS.txt").exists()
    print(f"Gap 6 reproduced: {len(rows)}/9 daily/ledger.jsonl rows miss contract s8 v2 fields; SELECTION_STRINGS.txt absent")


def main():
    gap1_close_arm_wick_penetration()
    gap2_pre_availability_replay_events()
    gap3_e11_cross_line_anchor_block()
    gap4_count_only_multi_touch_and_lookahead_terciles()
    gap5_g3_prefilter_offchart_anchors()
    gap6_daily_ledger_schema_v2_drift()
    print("ALL 6 SYNTHETIC GAP REPRODUCTIONS PASSED")


if __name__ == "__main__":
    main()
