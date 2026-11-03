"""Signal v1: queue/signal_v1.schema.json is the one schema file; D6 seam rejects kind option."""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys"))

import cbp  # noqa: E402

NEW = ROOT / "MyTradingSys" / "queue" / "signal_v1.schema.json"
OLD = ROOT / "MyTradingSys" / "cbp" / "schema.json"


def _row(**extra):
    r = {"analyst": "Krown", "video_id": "abcdefghijk", "published": "2026-10-24", "bias": "BULLISH",
         "quotes": [], "trades": [], "pointers": [], "symbols": ["BTC"], "quote_verified": True,
         "expires_at": "2026-10-29T00:00:00Z"}
    r.update(extra)
    return r


def test_one_schema_file_at_queue_path():
    assert NEW.is_file()
    assert not OLD.exists()


def test_schema_matches_cbp_constants():
    s = json.loads(NEW.read_text(encoding="utf-8"))
    assert list(s["required"]) == list(cbp.ROW_FIELDS)
    assert tuple(s["properties"]["bias"]["enum"]) == cbp.BIASES
    assert tuple(s["properties"]["trades"]["items"]["properties"]["direction"]["enum"]) == cbp.DIRECTIONS
    assert s["properties"]["instrument"]["properties"]["kind"]["enum"] == ["perp"]
    assert "instrument" not in s["required"]
    assert Path(cbp.SCHEMA_PATH) == NEW


def test_valid_row_with_perp_instrument_passes():
    assert cbp.validate_row(_row()) == []
    assert cbp.validate_row(_row(instrument={"venue": "binance", "symbol": "BTCUSDT", "kind": "perp"})) == []


def test_option_kind_and_non_object_instrument_rejected_without_raising():
    errs = cbp.validate_row(_row(instrument={"venue": "deribit", "symbol": "BTC-1JAN27-80000-C", "kind": "option"}))
    assert any("kind not enabled" in e for e in errs)
    errs = cbp.validate_row(_row(instrument="option"))
    assert any("instrument must be an object" in e for e in errs)
