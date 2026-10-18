import sys
sys.dont_write_bytecode = True
"""Tests for the V2 recall functions of tom_dax_recall.py (card tom-v2-recall-fire-rate).
Hand numbers: T3 entry 24229, stop 24257, width 28, so the break level is 24229 - 28 = 24201."""
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tom_dax_recall as R  # noqa: E402

E, W = 24229.0, 28.0
BARS = [(1000, 24220, 24240, 24215, 24235), (2000, 24235, 24260, 24230, 24255),   # lows stay above 24201
        (3000, 24250, 24255, 24199, 24205),                                       # low 24199 <= 24201: price traded there
        (4000, 24205, 24210, 24190, 24195)]


def test_break_ms_is_first_later_bar_at_or_below_entry_minus_width():
    assert R.v2_break_ms(BARS, E, W) == 3000
    assert R.v2_break_ms(BARS[:2], E, W) is None


def test_session_opening_far_below_entry_is_not_a_fall():
    # opens 63 under his entry (24166 vs 24229), spikes up through his band: price rising through 24201 is not "fell"
    rise = [(1000, 24166, 24170, 24160, 24168), (2000, 24168, 24215, 24166, 24212),
            (3000, 24212, 24232, 24210, 24230), (4000, 24230, 24235, 24195, 24198)]
    assert R.v2_break_ms(rise, E, W) == 4000
    assert R.v2_is_hit(24230, 3000, E, W, 4000) is True      # a detector emitting at his own entry price must hit
    assert R.v2_is_hit(24230, 4000, E, W, 4000) is False
    assert R.v2_break_ms([(1000, 24100, 24150, 24090, 24140)], E, W) is None   # never reached his band


def test_candidate_before_break_within_width_is_hit():
    brk = R.v2_break_ms(BARS, E, W)
    assert R.v2_is_hit(24250, 2000, E, W, brk) is True      # |24250 - 24229| = 21 <= 28, before 24201 traded
    assert R.v2_is_hit(24257, 2000, E, W, brk) is True      # exactly one stop-width away
    assert R.v2_is_hit(24260, 2000, E, W, brk) is False     # 31 > 28 away
    assert R.v2_is_hit(24250, 3000, E, W, brk) is False     # emitted on or after the bar that traded 24201
    assert R.v2_is_hit(24250, 4000, E, W, brk) is False


def test_group_hit_uses_any_candidate():
    assert R.v2_group_hit([(2000, 24260), (1000, 24250)], E, W, BARS) is True
    assert R.v2_group_hit([(2000, 24260), (3000, 24250)], E, W, BARS) is False
    assert R.v2_group_hit([], E, W, BARS) is False


def _flat_bars(n=40, price=24229.0):
    return [(60_000 * i, price, price + 1, price - 1, price) for i in range(n)]


def test_every_minute_candidate_set_gives_full_random_recall_and_fails_the_5pct_test():
    d = [dt.date(2026, 5, 11 + i) for i in range(5)]
    bars = {x: _flat_bars() for x in d}
    gd = [(f"G{i}", f"S{i}", [(24229.0, 28.0, d[i])]) for i in range(5)]
    n = {f"G{i}": len(bars[d[i]]) for i in range(5)}      # a candidate on every session minute
    rec = R.v2_random_recall(gd, n, bars, draws=50, seed=1)
    assert rec == [5] * 50                                  # random instants match everywhere: recall 100 %
    share = sum(1 for r in rec if r >= 5) / len(rec)
    assert share == 1.0
    assert R.v2_verdict_design({1: 5}, {1: share}) == (1, "FAIL")


def test_random_instants_miss_when_price_is_far_away():
    d = dt.date(2026, 5, 12)
    gd = [("G", "S1", [(24229.0, 28.0, d)])]
    far = {d: _flat_bars(price=24500.0)}
    assert R.v2_random_recall(gd, {"G": 10}, far, draws=20, seed=1) == [0] * 20


def test_k_star_is_largest_count_keeping_four_of_five():
    assert R.v2_verdict_design({1: 5, 2: 4, 3: 3, 4: 1}, {1: 0.0, 2: 0.01, 3: 0.2, 4: 0.5}) == (2, "PASS")
    assert R.v2_verdict_design({1: 3, 2: 2, 3: 1, 4: 0}, {1: 0, 2: 0, 3: 0, 4: 0}) == (None, "FAIL")
    assert R.v2_verdict_design({1: 4}, {1: 0.2}) == (1, "FAIL")        # recall passes, random clock matches too often


def test_check_verdict():
    assert [R.v2_verdict_check(h) for h in (2, 1, 0)] == ["PASS", "INCONCLUSIVE", "FAIL"]


def test_groups_come_from_the_ledger():
    g = {x["id"]: x for x in R.v2_groups()}
    assert g["T3"]["width"] == 36.0 and g["T3"]["session"] == "S3" and g["T3"]["contract"] == "M6"
    assert abs(g["T3"]["entry_adj"][dt.date(2026, 5, 12)] - (24229 - 50.4495)) < 1e-3   # basis by hand: 24229*0.02*38/365
    assert g["T1"]["width"] == 20.0      # ledger shows the stop only after it was moved: A-S2
    assert g["T6"]["width"] == 20.0 and len(g["T6"]["dates"]) == 2
    assert g["T5"]["width"] == 63.0 and g["T12"]["width"] == 23.0 and g["T11"]["width"] == 46.0
    assert "T7" not in g and "T4" not in g
