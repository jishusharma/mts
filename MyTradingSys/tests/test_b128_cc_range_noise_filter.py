"""B128 TC-W1-6: classify_msb(filter_range_noise=...). Spec (cc_structure.py is_range_extreme, FORMULAS s9): an MSB is range
noise unless its confirm close sits in the outer 25% of the prior 50-bar range; the flag defaults to False (live _cc_layer
passes none), True keeps only at_range_extreme events."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from MyTradingSys.backtest.layers.cryptocred import cc_structure as cs  # noqa: E402


def _bar(t, o, h, l, c):
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": 1.0}


def _fixture():
    # prior range 90..110 (span 20); a swing high at 100 broken by a close of 101 (mid-range -> noise)
    # then a swing high 108 broken by close 112 (above the range top -> extreme)
    bars = [_bar(i, 100, 110 if i == 1 else 101, 90 if i == 2 else 99, 100) for i in range(6)]
    bars += [_bar(6, 100, 102, 99, 101)]          # closes above swing 100 mid-range
    return bars


def test_default_keeps_range_noise_events_and_flags_them():
    bars = _fixture()
    swings = [{"i": 3, "price": 100.0, "kind": "high", "confirmed_i": 4},
              {"i": 1, "price": 105.0, "kind": "high", "confirmed_i": 2}]
    events = cs.classify_msb(bars, swings, require_prior_sequence=False)
    assert events, "fixture must produce at least one MSB"
    assert any(not e["at_range_extreme"] for e in events)


def test_filter_range_noise_true_drops_non_extreme_events():
    bars = _fixture()
    swings = [{"i": 3, "price": 100.0, "kind": "high", "confirmed_i": 4},
              {"i": 1, "price": 105.0, "kind": "high", "confirmed_i": 2}]
    base = cs.classify_msb(bars, swings, require_prior_sequence=False)
    kept = cs.classify_msb(bars, swings, require_prior_sequence=False, filter_range_noise=True)
    assert all(e["at_range_extreme"] for e in kept)
    assert len(kept) < len(base)
    assert [e for e in base if e["at_range_extreme"]] == kept


def test_is_range_extreme_boundaries():
    bars = [_bar(0, 100, 110, 90, 100), _bar(1, 100, 110, 90, 100), _bar(2, 100, 100, 100, 105)]
    assert cs.is_range_extreme(bars, 2) is True           # 105 >= 110 - 0.25*20 = 105 (boundary inclusive)
    bars[2]["c"] = 104.9
    assert cs.is_range_extreme(bars, 2) is False
    assert cs.is_range_extreme(bars, 1) is False          # fewer than 2 prior bars
