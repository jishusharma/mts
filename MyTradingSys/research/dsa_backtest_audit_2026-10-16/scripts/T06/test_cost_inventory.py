"""T06 test: costs.csv must list every fee/slippage/spread/funding constant under backtest/ and research/.

Fails on pre-change code (scripts/T06/costs.csv absent). Detector is t06_scan.py (separate from the
inventory writer, which only adds columns: unit, side, maker_taker, applies_to, imports_fees).
"""
import csv
import sys
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


def test_every_cost_constant_is_inventoried():
    rows = _rows()
    assert COLS <= set(rows[0].keys())
    have = {(r["file"], int(r["line"]), r["name"]) for r in rows}
    missing = [(p, ln, nm) for p, ln, nm, _v, _t in t06_scan.scan() if (p, ln, nm) not in have]
    assert not missing, f"{len(missing)} cost constants not in costs.csv, first: {missing[:5]}"


def test_every_row_has_unit_and_side():
    for r in _rows():
        assert r["unit"] in {"fraction", "pct", "bp", "usd", "points", "ratio", "other"}, r
        assert r["side"] in {"per_side", "round_trip", "per_8h", "n/a"}, r
        assert r["maker_taker"] in {"maker", "taker", "both", "n/a"}, r
