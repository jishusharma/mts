"""T06 test: costs.csv must list every fee/slippage/spread/funding constant under backtest/ and research/.

Fails on pre-change code (scripts/T06/costs.csv absent). Detector is t06_scan.py (separate from the
inventory writer, which only adds columns: unit, side, maker_taker, applies_to, imports_fees).
"""
import csv
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t06_scan  # noqa: E402

COSTS = HERE / "costs.csv"
COLS = {"file", "line", "name", "value", "unit", "side", "maker_taker", "applies_to", "imports_fees"}


def _rows():
    assert COSTS.exists(), "costs.csv missing: run t06_inventory.py"
    with open(COSTS, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def missing_constants(rows, hits):
    """Scanned (file, line, name) hits with no costs.csv row. Matched by (file, name) count, not line: a docstring or import added
    above a constant moved it and turned CI red with nothing new (52c922ae5 fabio_of_model.py slip, 2026-10-31; 8daa21e51 fees.py
    lines). A new name in a file, or one more binding of a name, is still missing."""
    have = Counter((r["file"], r["name"]) for r in rows)
    out = []
    for p, ln, nm, _v, _t in hits:
        if have[(p, nm)] > 0:
            have[(p, nm)] -= 1
        else:
            out.append((p, ln, nm))
    return out


def test_every_cost_constant_is_inventoried():
    rows = _rows()
    assert COLS <= set(rows[0].keys())
    missing = missing_constants(rows, t06_scan.scan())
    assert not missing, f"{len(missing)} cost constants not in costs.csv, first: {missing[:5]}"


def test_a_constant_moved_down_a_line_is_still_inventoried():
    rows = [{"file": "a.py", "line": "10", "name": "slip"}, {"file": "a.py", "line": "11", "name": "(literal)"}]
    assert missing_constants(rows, [("a.py", 12, "slip", "0.0", ""), ("a.py", 13, "(literal)", "0.0002", "")]) == []


def test_a_new_cost_name_or_a_second_binding_is_missing():
    rows = [{"file": "a.py", "line": "10", "name": "slip"}]
    assert missing_constants(rows, [("a.py", 10, "slip", "0.0", ""), ("a.py", 20, "cost", "1", "")]) == [("a.py", 20, "cost")]
    assert missing_constants(rows, [("a.py", 10, "slip", "0.0", ""), ("a.py", 30, "slip", "0.1", "")]) == [("a.py", 30, "slip")]
    assert missing_constants(rows, [("b.py", 10, "slip", "0.0", "")]) == [("b.py", 10, "slip")]


def test_every_row_has_unit_and_side():
    for r in _rows():
        assert r["unit"] in {"fraction", "pct", "bp", "usd", "points", "ratio", "other"}, r
        assert r["side"] in {"per_side", "round_trip", "per_8h", "n/a"}, r
        assert r["maker_taker"] in {"maker", "taker", "both", "n/a"}, r
