"""Pure-function checks for malkan_div_trade_charts: window start uses the earlier bound (min), span bucket separates 12 vs 13-18."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("malkan_charts", HERE / "malkan_div_trade_charts.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_window_starts_30_before_swing_b():
    # A=100, B=112: A-4=96, B-30=82 -> must start at 82 (old max code gave 96)
    assert m.window_start(100, 112) == 82
    assert m.window_start(100, 118) == 88


def test_window_clamped_at_zero_and_pad():
    assert m.window_start(5, 10) == 0
    assert m.window_start(100, 112, before=5) == 96  # A-4 is earlier than B-5


def test_span_class_splits_arms():
    assert [m.span_class(s) for s in (3, 12, 13, 18, 19)] == ["3-12", "3-12", "13-18", "13-18", ">18"]
