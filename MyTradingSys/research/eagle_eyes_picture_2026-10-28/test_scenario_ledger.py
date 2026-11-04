import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("scenario_ledger", Path(__file__).with_name("scenario_ledger.py"))
sl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sl)


def test_first_touch_order():
    bars = [(1, 100.5, 99.5), (2, 101.2, 100.0), (3, 100.0, 98.0)]
    assert sl.first_touch(bars, 101.0, 98.5) == ("UP", 2)
    assert sl.first_touch(bars, 102.0, 98.5) == ("DOWN", 3)
    assert sl.first_touch(bars, 103.0, 90.0) == ("NEITHER", None)
    assert sl.first_touch([(1, 105.0, 95.0)], 101.0, 99.0) == ("BOTH", 1)


def test_score_and_summary():
    assert sl.score_of("UP", "UP") == "HIT"
    assert sl.score_of("UP", "DOWN") == "MISS"
    assert sl.score_of("NONE", "UP") == "NA"
    assert sl.score_of("DOWN", "BOTH") == "NA"
    rows = [{"score": "HIT", "outcome": "UP"}] * 3 + [{"score": "MISS", "outcome": "DOWN"}, {"score": "", "outcome": ""}]
    s = sl.summary(rows)
    assert "HIT 3 MISS 1" in s and "open 1" in s and "keep logging (4/20" in s
