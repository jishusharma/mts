import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prob_table_run as pt


def test_future_bar_does_not_change_prior_state():
    bars = pt.synthetic_bars([10, 11, 10, 12, 11, 13] * 4)
    before = pt.states(bars)
    changed = bars.copy()
    changed.loc[changed.index[-1] + pt.pd.Timedelta(hours=1)] = [999, 1000, 998, 999]
    after = pt.states(changed)
    assert before.iloc[:-1].equals(after.loc[before.index[:-1]])


def test_hand_logloss_for_two_cells():
    # EXPECT: y=[up, down], p_up=[.75, .75] -> (-ln(.75)-ln(.25))/2.
    got = pt.mean_logloss([1, 0], [0.75, 0.75])
    assert math.isclose(got, -0.5 * (math.log(.75) + math.log(.25)))


def test_shrinkage_uses_regime_parent_below_30():
    # EXPECT: 29-cell observation uses parent p_up=.6; 30-cell uses its own .2.
    cell, parent = {"n": 29, "p_up": .2}, {"n": 100, "p_up": .6}
    assert pt.shrunk_probability(cell, parent) == .6
    assert pt.shrunk_probability({"n": 30, "p_up": .2}, parent) == .2


def test_loader_refuses_any_window_after_frozen_cutoff():
    try:
        pt.load_minutes(Path("missing-data-is-not-read"), "2024-01-01", "2024-07-02")
    except ValueError as exc:
        assert "exceeds frozen cutoff" in str(exc)
    else:
        raise AssertionError("post-cutoff data window must be refused")
