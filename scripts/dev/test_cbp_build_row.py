"""test_cbp_build_row.py - a quote-gate rejection keeps the full bad quote (<=400 chars) in the rejected row's reason."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cbp_run

FAKE = " ".join("fabricated%03d" % i for i in range(11))[:150]


def _video(d, vid="v9"):
    p = d / (vid + "_raw.txt")
    p.write_text(chr(10).join(["# Video ID: " + vid, "# Title: T", "# Published: 2026-10-30", "# Analyst: Jala",
                               "# Channel: @jalacrypto", "# ---", "btc looks fine here", ""]), encoding="utf-8")
    return (vid, "Jala", "2026-10-30", "T", p, "@jalacrypto")


def test_rejected_reason_keeps_full_quote():
    assert len(FAKE) == 150
    row, why = cbp_run.build_row(("v9", "Jala", "2026-10-30", "T", None, None),
                                 {"quotes": [FAKE], "trades": []}, "btc looks fine here")
    assert row is None
    assert why == "quote not in transcript: " + FAKE


def test_rejected_reason_caps_at_400(tmp_path):
    long = ("zq" * 300)
    _, why = cbp_run.build_row(("v9", "Jala", "2026-10-30", "T", None, None), {"quotes": [long], "trades": []}, "btc")
    assert why == "quote not in transcript: " + long[:400]


def test_run_once_stores_full_quote_in_rejected(tmp_path):
    _video(tmp_path)
    old, cbp_run.TRANSCRIPTS = cbp_run.TRANSCRIPTS, tmp_path
    try:
        got = {"bias": "NEUTRAL", "symbols": ["BTC"], "quotes": [FAKE], "trades": [], "pointers": []}
        cbp_run.run_once(datetime(2026, 10, 31, tzinfo=timezone.utc), fetch=lambda c, k: None,
                         extract=lambda v, b: got, store=tmp_path / "rows.json")
    finally:
        cbp_run.TRANSCRIPTS = old
    rej = json.loads((tmp_path / "rows.json").read_text(encoding="utf-8"))["rejected"]
    assert rej and rej[0][2] == "quote not in transcript: " + FAKE


# --- impossible extractor output: flags (spot injected, offline) ---
def _flagged(analyst, bias, trades, spot, body="x btc eth"):
    got = {"bias": bias, "symbols": ["BTC"], "quotes": [], "pointers": [],
           "trades": [dict(t, quote="btc eth") for t in trades]}
    return cbp_run.build_row(("v1", analyst, "2026-11-11", "T", None, None), got, body, spot=spot)


def test_long_stop_above_entry_is_blanked_and_flagged():
    t = {"asset": "BTC", "direction": "LONG", "entry": "74,573", "target": "80k", "invalidation": "82,000"}
    row, why = _flagged("Krown", "BEARISH", [t], lambda a, d: 74500.0)
    assert row and row["trades"][0]["invalidation"] == ""
    assert "stop_wrong_side" in row["flags"] and "bias_contradicts_trades" in row["flags"]
    assert "entry_far_from_spot" not in row["flags"]


def test_short_stop_below_entry_flagged_and_good_stop_kept():
    bad = {"asset": "BTC", "direction": "SHORT", "entry": "75000", "target": "70000", "invalidation": "74000"}
    ok = {"asset": "BTC", "direction": "LONG", "entry": "75000", "target": "80000", "invalidation": "73k"}
    row, _ = _flagged("K", "NEUTRAL", [bad, ok], lambda a, d: 75000.0)
    assert row["trades"][0]["invalidation"] == "" and row["trades"][1]["invalidation"] == "73k"
    assert row["flags"] == ["stop_wrong_side"]


def test_entry_far_from_spot_flagged_entry_kept():
    t = {"asset": "ETH", "direction": "LONG", "entry": "hold above 2360", "target": "2800", "invalidation": "2300"}
    row, _ = _flagged("Michaal", "BULLISH", [t], lambda a, d: 2100.0)
    assert row["flags"] == ["entry_far_from_spot"] and row["trades"][0]["entry"] == "hold above 2360"


def test_clean_row_has_no_flags_and_missing_spot_skips():
    t = {"asset": "ETH", "direction": "LONG", "entry": "2100", "target": "2300", "invalidation": "2000"}
    row, _ = _flagged("M", "BULLISH", [t], lambda a, d: 2090.0)
    assert "flags" not in row
    far = dict(t, entry="9000")
    row, _ = _flagged("M", "BULLISH", [far], lambda a, d: None)
    assert "flags" not in row


def test_bullish_with_short_flagged():
    t = {"asset": "BTC", "direction": "SHORT", "entry": "75000", "target": "70000", "invalidation": "76000"}
    row, _ = _flagged("K", "BULLISH", [t], lambda a, d: 75000.0)
    assert row["flags"] == ["bias_contradicts_trades"]
