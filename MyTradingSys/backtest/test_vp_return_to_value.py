import sys
sys.dont_write_bytecode = True
"""Tests for vp_return_to_value.py. Every expected number is worked by hand from the toy days below (levels
POC 100, VAH 110, VAL 90), never from the code. Pre-reg: research/tom_transfer_2026-10-11/vp_return/PRE_REG.md."""
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vp_return_to_value as V  # noqa: E402

LV = {"poc_price": 100.0, "vah": 110.0, "val": 90.0}

# Day 1 RETURN (up leave). 5 bars (h, l, c):
#   bar0 c=105 inside; bar1 c=112 > VAH 110 -> EVENT at bar1 (up)
#   later bars 2..4: bar2 l=112, bar3 l=107, bar4 l=99 h=103 -> 99 <= 100 <= 103 touches POC -> RETURN
#   closes inside value after the event: bar3 c=108 -> back_inside True
#   N=3 acceptance needs closes of bars 1,2,3 = 112,113,108: bar3 108 <= 110 -> NOT accepted (applicable: 1+2=3 <= 4)
D1 = dict(h=[106, 113, 114, 109, 103], l=[104, 111, 112, 107, 99], c=[105, 112, 113, 108, 101])
# Day 2 RUN-AWAY (down leave). bar0 c=95 inside; bar1 c=89 < VAL 90 -> EVENT at bar1 (down)
#   later highs 86, 81, 84 all < 100 -> no touch of POC -> RUN-AWAY; no close back inside (85, 80, 82 < 90)
#   N=3: closes of bars 1,2,3 = 89, 85, 80 all < 90 -> ACCEPTED; after bar3 only bar4 (h=84 < 100) -> no return
#   N=6: needs bar 1+5 = 6 > 4 -> NOT applicable
D2 = dict(h=[96, 90, 86, 81, 84], l=[94, 88, 84, 79, 80], c=[95, 89, 85, 80, 82])
# Day 3 NO EVENT: every close inside [90, 110]
D3 = dict(h=[101, 109, 108, 104, 100], l=[99, 100, 98, 96, 95], c=[100, 105, 102, 98, 97])


def test_return_day():
    r = V.analyse_day(LV, D1["h"], D1["l"], D1["c"])
    assert r["event"] == 1
    assert r["side"] == 1
    assert r["returned"] is True
    assert r["back_inside"] is True
    assert r["acc"][3] == {"applicable": True, "accepted": False, "returned": None}


def test_run_away_day():
    r = V.analyse_day(LV, D2["h"], D2["l"], D2["c"])
    assert r["event"] == 1
    assert r["side"] == -1
    assert r["returned"] is False
    assert r["back_inside"] is False
    assert r["acc"][3] == {"applicable": True, "accepted": True, "returned": False}
    assert r["acc"][6]["applicable"] is False


def test_no_event_day():
    r = V.analyse_day(LV, D3["h"], D3["l"], D3["c"])
    assert r["event"] is None
    assert r["returned"] is None


def test_toy_set_share_is_half():
    rs = [V.analyse_day(LV, d["h"], d["l"], d["c"]) for d in (D1, D2, D3)]
    ev = [r for r in rs if r["event"] is not None]
    assert len(ev) == 2
    assert sum(r["returned"] for r in ev) / len(ev) == pytest.approx(0.5)


def test_shift_levels_by_d_times_atr():
    # d = -0.5, R = 10 -> every level moves by -5
    s = V.shift_levels(LV, -0.5, 10.0)
    assert s == {"poc_price": 95.0, "vah": 105.0, "val": 85.0}


def test_shifted_band_changes_outcome():
    # Day 1 against the band shifted by -5 (POC 95, VAH 105, VAL 85): bar1 c=112 > 105 -> event at bar1;
    # later lows 112, 107, 99 and highs up to 114: 95 is never inside any bar range -> RUN-AWAY
    s = V.shift_levels(LV, -0.5, 10.0)
    r = V.analyse_day(s, D1["h"], D1["l"], D1["c"])
    assert r["event"] == 1 and r["returned"] is False


def test_share_and_diff_hand_numbers():
    import numpy as np
    # two days: day A 2 events 2 returns, day B 1 event 0 returns -> pooled 2/3; resamples give 1.0, 0.0 or 2/3
    num, den = np.array([2.0, 0.0]), np.array([2.0, 1.0])
    s = V.share(num, den, np.ones(2, bool))
    assert s["n"] == 3 and s["share"] == pytest.approx(2 / 3)
    assert 0.0 <= s["ci"][0] <= 2 / 3 <= s["ci"][1] <= 1.0
    # same stream against itself: difference exactly 0 on every resample
    d = V.diff(num, den, num, den, np.ones(2, bool))
    assert d["diff"] == pytest.approx(0.0) and d["ci"] == [0.0, 0.0]


def test_event_ignores_future_bars():
    # changing bars after the event bar must not move the event index (no look-ahead)
    h = list(D1["h"]); l = list(D1["l"]); c = list(D1["c"])
    h[4], l[4], c[4] = 500, 1, 2
    assert V.analyse_day(LV, h, l, c)["event"] == 1
