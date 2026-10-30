"""Tests for pizzino_levels.py. Expected numbers are worked by hand (SPEC.md example 1 bars and the
cases written out below), never taken from the code."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pizzino_levels as pl  # noqa: E402

# SPEC.md worked example 1 (H, L, C); open = close of the bar before (not used by the rules).
EX1_H = [10, 12, 14, 13, 12, 11, 12, 14, 16, 15, 14]
EX1_L = [8, 9, 11, 10, 9, 7, 8, 10, 12, 11, 10]
EX1_C = [9, 11, 13, 11, 10, 8, 11, 13, 15, 12, 13]


def rows(h, l, c, step=86400000):
    return [[i * step, c[i - 1] if i else c[0], h[i], l[i], c[i], 1] for i in range(len(c))]


def by_name(out):
    return {x["n"]: x["p"] for x in out["levels"]}


def test_example1_levels_mid_degree_2():
    # Hand: degree 1 and 2 pivots PH 14 (bar 2), PL 7 (bar 5), PH 16 (bar 8). Degree 3: only PL 7 (bar 5)
    # (bar 8 has 2 bars on its right). 50% on degree 2 = (16 + 7) / 2 = 11.5; close 13 > 11.5 -> strong.
    out = pl.levels_for(rows(EX1_H, EX1_L, EX1_C), "1d", mid_degree=2)
    lv = by_name(out)
    assert lv["PZ 1d PH1"] == 16 and lv["PZ 1d PL1"] == 7 and lv["PZ 1d PH2"] == 16 and lv["PZ 1d PL2"] == 7
    assert lv["PZ 1d PL3"] == 7 and "PZ 1d PH3" not in lv
    assert lv["PZ 1d 50%"] == 11.5 and out["mid"] == 11.5 and out["half"] == "strong"
    assert out["leg"]["from"] == "L"  # leg runs low (bar 5) -> high (bar 8)
    # Each degree has one PL only -> neutral (fewer than two pivots of a kind); sum 0.
    assert [d["state"] for d in out["degrees"]] == [0, 0, 0] and out["conf"] == 0
    # Only bar 10 is after the leg was confirmed (bar 8 + 2): no break of 11.5.
    assert out["retest"]["status"] == "no break"


def test_example1_three_bar_count_and_no_mid_on_degree_3():
    # Degree-3 PL 7 at bar 5 is the lowest low of bars 0-4 (8, 9, 11, 10, 9) -> significant.
    # Bars 6, 7, 8: (12, 8) (14, 10) (16, 12) each HH + HL -> 3; bar 9 high 15 < 16 stops it.
    out = pl.levels_for(rows(EX1_H, EX1_L, EX1_C), "1d")
    assert out["count"] == {"from": "L", "t": 5 * 86400000, "price": 7, "count": 3, "three_bar": True}
    assert out["mid"] is None and out["half"] is None  # degree 3 has no PH yet


UP_H = [10, 12, 11, 13, 12, 14, 13, 15]
UP_L = [8, 10, 9, 11, 10, 12, 11, 13]
UP_C = [9, 11, 10, 12, 11, 13, 12, 14.5]


def test_degree1_up_state_and_nesting_under_parent():
    # n = 1: PH 12 (bar 1), 13 (bar 3), 14 (bar 5); PL 9 (bar 2), 10 (bar 4), 11 (bar 6).
    # 14 > 13, 11 > 10, close 14.5 > 11 -> degree 1 up, break level 11. Degrees 2, 3: no pivot -> 0. Sum +1.
    r = rows(UP_H, UP_L, UP_C, step=3600000)
    strong = {"tf": "4h", "half": "strong", "mid": 100.0}
    out = pl.levels_for(r, "1h", parent=strong)
    assert out["degrees"][0] == {"d": 1, "state": 1, "break": 11, "ph": 14, "pl": 11}
    assert out["conf"] == 1 and out["aligned"] is True and out["parent"]["tf"] == "4h"
    assert pl.levels_for(r, "1h", parent=dict(strong, half="weak"))["aligned"] is False
    assert pl.levels_for(r, "1h")["aligned"] is None  # no parent given


def test_mid_break_and_retest_status():
    # Leg: PH 20 (bar 3), PL 10 (bar 6), degree 3 -> 50% = 15, confirmed at bar 9.
    # Closes after bar 9: 14, 16 (1st above), 17 (2nd above: up-break at bar 12), then bar 13 low 15.05
    # <= 15 * 1.005 = 15.075 and close 16 > 15 -> 'retest hold' at bar 13.
    h = [14, 16, 18, 20, 18, 16, 13, 14, 15, 15, 15, 16.5, 17.5, 17, 17]
    l = [12, 14, 16, 18, 15, 12, 10, 12, 13, 13.5, 13.5, 15.5, 16.2, 15.05, 16.5]
    c = [13, 15, 17, 19, 16, 13, 11, 13, 14, 14.5, 14, 16, 17, 16, 16.8]
    out = pl.levels_for(rows(h, l, c), "1d")
    assert out["mid"] == 15 and out["leg"]["from"] == "H"
    assert out["retest"] == {"dir": "up", "break_at": 12, "retest_at": 13, "status": "retest hold"}


def test_fold_utc_buckets():
    # 1m bars at minutes 3..7 -> 5m buckets [0,5) and [5,10): (o 1, h 5, l 0.5, c 3, v 2) and (o 3, h 9, l 2, c 8, v 3).
    m = 60000
    r = [[3 * m, 1, 5, 0.5, 2, 1], [4 * m, 2, 4, 1, 3, 1], [5 * m, 3, 9, 3, 4, 1], [6 * m, 4, 6, 2, 5, 1], [7 * m, 5, 8, 4, 8, 1]]
    assert pl.fold(r, 5 * m) == [[0, 1, 5, 0.5, 3, 2], [5 * m, 3, 9, 2, 8, 3]]


def test_export_parent_chain_and_labels():
    r = rows(UP_H, UP_L, UP_C, step=60000)
    out = pl.export({"1m": r, "4h": r, "1d": r})
    assert [f["tf"] for f in out["frames"]] == ["1d", "4h", "1m"]
    assert out["frames"][1]["parent"] is None or out["frames"][1]["parent"]["tf"] == "1d"
    assert all(p["label"] in ("SOURCED", "OURS") for p in out["params"].values())
    assert out["params"]["degrees"]["label"] == "SOURCED" and out["params"]["pivot_n"]["label"] == "OURS"
    json.dumps(out)  # plain JSON
