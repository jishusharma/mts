"""Pins the single volume-profile definition (FORMULAS 18.1: fixed 10 USDT grid, uniform overlap weighting,
POC = bin centre, VAH = top edge, VAL = bottom edge) as decision OURS (ZONE_MISMATCH.md). Synthetic days, expected
values worked by hand from FORMULAS 18.1, no archive, no Java."""
import numpy as np

import zone_mismatch_classify as Z
from MyTradingSys.backtest.vp_pivot_probe import build_profile


def _arr(bars):
    a = np.array(bars, float)
    return a[:, 1], a[:, 0], a[:, 2]          # h, l, v


# (bars (l,h,v), expected poc_price, vah, val), all by hand with w = 10
DAYS = {
    # bin100 = 10, bin110 = 5+30+10 = 45, bin120 = 5; total 60, target 42; POC bin110 alone holds 45
    "spread": ([(100, 120, 20), (110, 130, 10), (110, 120, 30)], 115.0, 120.0, 110.0),
    # point masses at bin centres, volumes [1,2,10,4,3]: POC bin120, take upper (4 > 2) -> acc 14 stop
    "worked_b": ([(105, 105, 1), (115, 115, 2), (125, 125, 10), (135, 135, 4), (145, 145, 3)], 125.0, 140.0, 120.0),
    # tie [3,10,3]: ties go to the lower bin -> val 200, vah 220
    "tie": ([(205, 205, 3), (215, 215, 10), (225, 225, 3)], 215.0, 220.0, 200.0),
}


def test_standard_profile_matches_hand_values():
    for name, (bars, poc, vah, val) in DAYS.items():
        h, l, v = _arr(bars)
        r = Z.standard_profile(h, l, v)
        assert (r["poc_price"], r["vah"], r["val"]) == (poc, vah, val), name


def test_standard_profile_equals_research_reference():
    for name, (bars, *_rest) in DAYS.items():
        h, l, v = _arr(bars)
        ref = build_profile(l, h, v, Z.W)
        got = Z.standard_profile(h, l, v)
        for k in ("poc_price", "vah", "val"):
            assert abs(ref[k] - got[k]) < 1e-9, (name, k)


def test_java_port_on_fixed_grid_with_18_1_edges_equals_standard_for_point_mass_days():
    for name in ("worked_b", "tie"):
        h, l, v = _arr(DAYS[name][0])
        c = (h + l) / 2
        poc, vah, val, bs, _ = Z.java_port(h, l, c, v, fixed=Z.W)
        assert bs == Z.W
        c18 = Z.conv(poc, vah, val, bs)
        std = Z.standard_profile(h, l, v)
        assert (c18["poc"], c18["vah"], c18["val"]) == (std["poc_price"], std["vah"], std["val"]), name
