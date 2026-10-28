"""Live validation store (operator decision 2026-10-28, card live-validation-store-signal-chart-hook).

One operator validation per signal category; look-alikes inherit it; anything different, new or corrected is a DOUBT and
never gets a verdict on its own. Expected outcomes below are written from the card and the Malkan rules in
rsi/params/malkan_divergence_default.json (regular 3-10 bars; PRD/NRD 5-14 bars, RSI >= 60 / <= 40 at both points).
"""
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.layers.rsi import live_validation as lv  # noqa: E402

SEED_CSV = REPO / "MyTradingSys" / "research" / "malkan_div_flags_2026-10-28" / "BTCUSDT_divergences.csv"


def sig(code="R-BEAR", tf="1d", bars=5, pa=100.0, pb=101.0, ra=70.0, rb=65.0, sid="s1", symbol="BTCUSDT"):
    return {"id": sid, "symbol": symbol, "tf": tf, "code": code, "bars": bars,
            "price_a": pa, "price_b": pb, "rsi_a": ra, "rsi_b": rb, "t": 1}


def confirmed_store(tmp_path):
    st = lv.Store(tmp_path / "store.json")
    lv.seed_from_csv(st, SEED_CSV)
    case = st.case_for(("regular", "bear", "1d", "BTCUSDT"))
    st.record_verdict(case["case"], "yes, that is a regular bearish divergence", by="operator")
    return st, case["case"]


def test_seed_one_example_per_type_and_no_auto_verdict(tmp_path):
    st = lv.Store(tmp_path / "store.json")
    seeded = lv.seed_from_csv(st, SEED_CSV)
    cats = {tuple(c["category"]) for c in st.cases()}
    # history has 6 of the 8 type x side x tf categories; PRD 1d and NRD 1w have no example (recorded, not invented)
    assert ("regular", "bull", "1d", "BTCUSDT") in cats and ("hidden", "bull", "1w", "BTCUSDT") in cats
    assert len(cats) == 6 and len(st.cases()) == 6
    assert sorted(seeded["missing"]) == [["hidden", "bear", "1w", "BTCUSDT"], ["hidden", "bull", "1d", "BTCUSDT"]]
    assert all(c["verdict"] is None for c in st.cases())          # seeding never writes a verdict
    assert lv.seed_from_csv(st, SEED_CSV)["added"] == 0             # idempotent


def test_lookalike_inherits_validated_case(tmp_path):
    st, n = confirmed_store(tmp_path)
    assert st.match(sig()) == "matches validated case #%d" % n


def test_pending_case_is_not_a_verdict(tmp_path):
    st = lv.Store(tmp_path / "store.json")
    lv.seed_from_csv(st, SEED_CSV)
    out = st.match(sig())
    assert out.startswith("PENDING case #") and "validated" not in out


def test_differing_geometry_and_unknown_category_go_to_doubts(tmp_path):
    st, _ = confirmed_store(tmp_path)
    # same category, but the RSI made a higher high: not the validated geometry
    assert st.match(sig(sid="g1", ra=60.0, rb=65.0)) == "DOUBT"
    # same category, 12 bars: outside the regular 3-10 window
    assert st.match(sig(sid="g2", bars=12)) == "DOUBT"
    # PRD 1d has no history example: a new category is a doubt
    assert st.match(sig(sid="g3", code="PRD", bars=6, pa=100, pb=101, ra=70, rb=65)) == "DOUBT"
    # Krown generic hidden flags are not Malkan
    assert st.match(sig(sid="g4", code="K-HBEAR")) == "DOUBT"
    ids = [d["signal"]["id"] for d in st.doubts()]
    assert ids == ["g1", "g2", "g3", "g4"]
    assert all(d["verdict"] is None for d in st.doubts())


def test_correction_writes_verdict_and_moves_the_doubt(tmp_path):
    st, n = confirmed_store(tmp_path)
    st.match(sig(sid="g1", ra=60.0, rb=65.0))
    st.correct("g1", "no, RSI rose: not a divergence", by="operator")
    assert st.doubts() == []
    moved = [c for c in st.cases() if c.get("from_signal") == "g1"]
    assert len(moved) == 1 and moved[0]["verdict"]["text"] == "no, RSI rose: not a divergence"
    # a correction of the validated category itself also makes later look-alikes a doubt, never an inherited verdict
    st.correct_case(n, "actually wrong", by="operator")
    assert st.match(sig(sid="s9")) == "DOUBT"


def test_restart_and_reset_keep_the_store(tmp_path):
    st, n = confirmed_store(tmp_path)
    st.match(sig(sid="g1", ra=60.0, rb=65.0))
    again = lv.Store(tmp_path / "store.json")                       # process restart
    assert again.match(sig(sid="s2")) == "matches validated case #%d" % n
    assert [d["signal"]["id"] for d in again.doubts()] == ["g1"]
    # a torn / corrupt store file fails closed: refuse to load, never start empty and re-verdict
    (tmp_path / "store.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(lv.StoreError):
        lv.Store(tmp_path / "store.json")


def test_hook_send_error_leaves_signal_pending_and_fails_closed(tmp_path):
    st, n = confirmed_store(tmp_path)
    charts = []

    def chart(signal, out_png):
        charts.append(out_png)
        Path(out_png).write_bytes(b"png")
        return out_png

    def broken_send(msg):
        raise OSError("network down")

    res = lv.on_signal(sig(sid="s3"), st, chart_fn=chart, send_fn=broken_send, chart_dir=tmp_path / "charts")
    assert res["sent"] is False and res["status"] == "matches validated case #%d" % n
    assert [p["signal"]["id"] for p in st.outbox()] == ["s3"]        # kept for a retry, not dropped
    assert all(c["verdict"] is None or c["case"] == n for c in st.cases())  # no new verdict from a failed send
    sent = []
    assert lv.retry_outbox(st, send_fn=sent.append) == 1
    assert st.outbox() == [] and "matches validated case #%d" % n in sent[0]["text"] and sent[0]["chart"] == charts[0]


def test_hook_chart_error_fails_closed(tmp_path):
    st, _ = confirmed_store(tmp_path)

    def bad_chart(signal, out_png):
        raise RuntimeError("matplotlib missing")

    sent = []
    res = lv.on_signal(sig(sid="s4"), st, chart_fn=bad_chart, send_fn=sent.append, chart_dir=tmp_path)
    assert res["sent"] is False and sent == [] and [p["signal"]["id"] for p in st.outbox()] == ["s4"]


def test_event_adapter_from_live_rsi_layer():
    ev = {"t": 5, "event": "rsi_div_bear", "side": "short", "bars": 4, "chain": 1,
          "close_a": 100.0, "close_b": 102.0, "rsi_a": 70.0, "rsi_b": 66.0}
    s = lv.signal_from_event(ev, tf="1d", symbol="BTCUSDT")
    assert s["code"] == "R-BEAR" and s["tf"] == "1d" and s["price_b"] == 102.0 and s["id"] == "BTCUSDT-1d-5-R-BEAR"
    assert lv.category_of(s) == ("regular", "bear", "1d", "BTCUSDT")


def test_store_file_is_plain_json(tmp_path):
    st, _ = confirmed_store(tmp_path)
    data = json.loads((tmp_path / "store.json").read_text(encoding="utf-8"))
    assert set(data) >= {"cases", "doubts", "outbox", "version"}
