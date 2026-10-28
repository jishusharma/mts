# Operator ruling 2026-10-03: no 2.0R-3.5R window, no VWAP/VAL/VAH/prior-day high-low target members.
# Target = nearest POC/HVN node in trade direction with netRR >= floor, else the farthest node; runner = next node beyond.
# B070 fee model: cost = 2 * 0.0005 * 87064 = 87.064 price units; net = (reward - 87.064) / (174 + 87.064) = (reward - 87.064) / 261.064. Expected numbers by hand arithmetic next to each assert.
# Staged as .new with math_object_builder.py.new; run via scripts/dev/run_staged_tests.py.
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent / "runtime"))

import math_object_builder as mob
from math_object_builder import _pick_stop_target, _pick_stop_target_runner

ZONE = {"name": "daily_vah", "price": 87064.0, "type": "daily_vah"}


def _norm(daily_vp, vwap=None, prior_day=None):
    return {
        "current_price": 87000.0,
        "daily_vp": daily_vp, "weekly_vp": {}, "intraday_4h_vp": {},
        "vwap": vwap or {}, "prior_day": prior_day or {},
        "structure": {"15m": {"swing_high": 87238.0, "swing_low": 86000.0}},   # short: stop 87238, risk 174
    }


def _run(norm):
    with mock.patch.object(mob, "load_floor", return_value=1.25):
        return _pick_stop_target_runner(ZONE, 87000.0, norm)


def test_nearest_qualifying_node_with_runner():
    # 86600: reward 464 -> net (464 - 87.064) / 261.064 = 1.4439 >= 1.25 -> target. runner = 83851 (next, farther).
    assert _run(_norm({"poc": 0, "hvns": [86600.0, 83851.0]})) == (87238.0, 86600.0, 83851.0)


def test_node_passing_old_flat_haircut_but_failing_fee_model_is_skipped():
    # 86687: reward 377, gross 2.1667R (old gross*0.75 = 1.625 passed). Fee model: (377 - 87.064) / 261.064 = 1.1106 < 1.25 -> skip.
    assert _run(_norm({"poc": 0, "hvns": [86687.0, 83851.0]})) == (87238.0, 83851.0, None)


def test_close_node_failing_floor_is_skipped():
    # 86900: 164/174 = 0.943R gross, net 0.707 < 1.25 -> skip. 83851: 3213/174 = 18.47R gross -> target, no runner.
    assert _run(_norm({"poc": 86900.0, "hvns": [83851.0]})) == (87238.0, 83851.0, None)


def test_single_node_at_5R_is_kept():
    # 86194: 870/174 = 5.0R gross (old window cap 3.5R excluded it), net 3.75 -> target.
    assert _run(_norm({"poc": 86194.0}))[1] == 86194.0


def test_no_node_qualifies_takes_farthest():
    # nodes 86900 (0.943R) and 86800 (264/174 = 1.517R gross, fee-model net (264 - 87.064) / 261.064 = 0.678 < 1.25): both fail -> farthest 86800.
    assert _run(_norm({"poc": 86900.0, "hvns": [86800.0]})) == (87238.0, 86800.0, None)


def test_vwap_val_prior_day_low_are_not_targets():
    # only unsourced members below the zone: VWAP 86000, VAL 85000, prior_day low 84000 -> no target
    n = _norm({"val": 85000.0}, vwap={"price": 86000.0}, prior_day={"low": 84000.0, "val": 84500.0})
    assert _run(n)[1] is None


def test_stop_helper_keeps_two_tuple_and_zone_math_has_runner():
    with mock.patch.object(mob, "load_floor", return_value=1.25):
        assert _pick_stop_target(ZONE, 87000.0, _norm({"hvns": [86600.0, 83851.0]})) == (87238.0, 86600.0)
