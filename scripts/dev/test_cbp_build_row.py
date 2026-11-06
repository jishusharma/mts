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
