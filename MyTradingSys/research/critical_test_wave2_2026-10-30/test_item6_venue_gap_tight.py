"""Fail-first tests for item6_venue_gap_tight.py (card venue-gap-tight-stop-rerun-on-deribit)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def test_variants_are_the_card_variants():
    import item6_venue_gap_tight as m
    names = [v["name"] for v in m.VARIANTS]
    assert names == ["stop_1p0", "stop_0p10", "stop_0p15", "wick_touch_1p0"], names
    by = {v["name"]: v for v in m.VARIANTS}
    assert abs(by["stop_1p0"]["stop_pct"] - 0.01) < 1e-12
    assert abs(by["stop_0p10"]["stop_pct"] - 0.001) < 1e-12
    assert abs(by["stop_0p15"]["stop_pct"] - 0.0015) < 1e-12
    assert by["wick_touch_1p0"]["wick_touch"] is True
    assert by["stop_0p10"]["wick_touch"] is False


def test_stop_1p0_reproduces_item6_event_and_trade_counts():
    import item6_venue_gap_tight as m
    base = json.loads((HERE / "item6_result.json").read_text(encoding="utf-8"))
    b, d = m.load_binance(), m.load_deribit()
    ev_b, ev_d = m.rsi_events(b), m.rsi_events(d)
    assert len(ev_b) == base["layer"]["events_binance"] == 52
    assert len(ev_d) == base["layer"]["events_deribit"] == 55
    tr_b = m.run_layer(b, [], ev_b, 0.01, False)
    tr_d = m.run_layer(d, [], ev_d, 0.01, False)
    assert sum(1 for x in tr_b if x["net_r"] is not None) == base["layer"]["trades_binance"] == 51
    assert sum(1 for x in tr_d if x["net_r"] is not None) == base["layer"]["trades_deribit"] == 54
