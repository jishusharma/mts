"""U8 detector: hand-built 15m bars. Fails on a tree without cvd_u7_u8.py (module missing), passes after.

Two swing lows 0.05% apart: heavy selling into the second low (CVD lower) must flag div=True; buying into it must flag
div=False; a second low 0.5% lower is not an equal low and must not be returned.
"""
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MOD = REPO / "MyTradingSys" / "research" / "fabio_cvd_2026-10-30" / "cvd_u7_u8.py"


def _load():
    spec = importlib.util.spec_from_file_location("cvd_u7_u8", MOD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _bars(second_low, second_delta):
    lows = [105, 104, 100, 103, 104, 103, second_low, 104, 105]
    deltas = [0, 0, -50, 10, 10, 0, second_delta, 0, 0]
    return [(i * 900, l + 1, l + 2, l, l + 1, d) for i, (l, d) in enumerate(zip(lows, deltas))]


def test_cvd_lower_low_at_flat_price_is_divergence():
    m = _load()
    out = m.find_equal_lows(_bars(100.05, -80))
    assert len(out) == 1 and out[0]['div'] is True and out[0]['i'] == 6 and out[0]['prev'] == 2


def test_cvd_higher_low_at_flat_price_is_control():
    m = _load()
    out = m.find_equal_lows(_bars(100.05, 40))
    assert len(out) == 1 and out[0]['div'] is False


def test_price_lower_low_is_not_equal_low():
    m = _load()
    assert m.find_equal_lows(_bars(99.5, -80)) == []
