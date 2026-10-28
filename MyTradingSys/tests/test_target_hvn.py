# test_target_hvn.py - HVN as target candidate in math_object_builder._pick_stop_target.
# Tom [TOM-018]: "if it accepts new prices, then it looks for the next high volume price and that is your target."
# Expected values are hand-picked levels, not derived from the code under test.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "runtime"))

from math_object_builder import _pick_stop_target


def _norm(daily_vp, price=100.0):
    return {
        "current_price": price,
        "daily_vp": daily_vp,
        "weekly_vp": {}, "intraday_4h_vp": {}, "post_funding_vp": {},
        "vwap": {}, "prior_day": {},
        "structure": {"15m": {"swing_high": 103.0, "swing_low": 97.0}},
    }


def test_long_target_is_nearest_hvn_above_zone_when_closer_than_poc():
    # long at zone 98, stop 97 (risk 1): HVN 101.0 = 3R gross, fee-model net ~2.64 and nearer than POC 105
    # (7R). Old nearest-by-price-only code would also pick 101; 99.0 (1R, fee-model net ~0.82) would now be skipped by the floor.
    n = _norm({"poc": 105.0, "hvns": [101.0, 110.0]})
    zone = {"name": "daily_val", "price": 98.0, "type": "daily_val"}
    stop, target = _pick_stop_target(zone, 100.0, n)
    assert (stop, target) == (97.0, 101.0)


def test_short_target_is_nearest_hvn_below_zone():
    # short at zone 102, stop 103 (risk 1): POC 90, HVN 99.0 = 3R gross, fee-model net ~2.64, nearer below zone than 90 / 85
    n = _norm({"poc": 90.0, "hvns": [99.0, 85.0]})
    zone = {"name": "daily_vah", "price": 102.0, "type": "daily_vah"}
    stop, target = _pick_stop_target(zone, 100.0, n)
    assert (stop, target) == (103.0, 99.0)


def test_garbage_hvn_entries_ignored():
    n = _norm({"poc": 105.0, "hvns": [None, "x", True, -5, 0]})
    zone = {"name": "daily_val", "price": 98.0, "type": "daily_val"}
    _, target = _pick_stop_target(zone, 100.0, n)
    assert target == 105.0


def test_missing_or_null_hvns_keeps_old_behaviour():
    zone = {"name": "daily_val", "price": 98.0, "type": "daily_val"}
    assert _pick_stop_target(zone, 100.0, _norm({"poc": 105.0}))[1] == 105.0
    assert _pick_stop_target(zone, 100.0, _norm({"poc": 105.0, "hvns": None}))[1] == 105.0
