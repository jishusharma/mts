"""build_analyst_data.py: every roster analyst is listed (ingested or not), rows outside the roster are added, levels parsed offline."""
import json
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_analyst_data as bad  # noqa: E402


def row(analyst, vid, published, bias, pointers):
    return dict(analyst=analyst, video_id=vid, published=published, bias=bias, quotes=[], trades=[], pointers=pointers,
                symbols=["BTC"], quote_verified=True, expires_at="2026-11-05T00:00:00Z")


def test_roster_complete_rows_rejected_and_levels(tmp_path):
    store = tmp_path / "rows.json"
    store.write_text(json.dumps({"rows": [row("Krown", "v1", "2026-10-27", "BEARISH", ["expects wick in 76-77k"]),
                                          row("Zed", "v2", "2026-10-28", "BULLISH", ["holding $81,180"]),
                                          {"analyst": "Bad"}],
                                 "rejected": [["v3", "Qriptal", "quote not in transcript: x"]]}), encoding="utf-8")
    roster = tmp_path / "analysts.json"
    roster.write_text(json.dumps({"analysts": [
        {"short": "Krown", "channel": "@ECKrown", "enabled": True, "profile": "actionable"},
        {"short": "Bob", "channel": "@bob", "enabled": True, "profile": "thesis"},
        {"short": "Qriptal", "channel": "@qriptal", "enabled": True, "profile": "actionable"},
        {"short": "Malkan", "channel": "@malkan", "enabled": False, "profile": "thesis"}]}), encoding="utf-8")
    stamp = tmp_path / "stamp.json"
    stamp.write_text(json.dumps({"last_run": "2026-10-28T10:53:28+00:00"}), encoding="utf-8")
    now = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)
    b = bad.build(str(store), roster_file=roster, stamp_file=stamp, offline=True, now=now)
    names = [(a["short"], a["ingested"], a["in_roster"], a["enabled"]) for a in b["roster"]]
    # all 4 roster analysts kept (Bob thesis = not ingested, Malkan off); Zed has a row but no roster line -> added; invalid row dropped
    assert names == [("Krown", True, True, True), ("Bob", False, True, True), ("Qriptal", True, True, True), ("Malkan", False, True, False), ("Zed", True, False, True)]
    assert [r["analyst"] for r in b["rows"]] == ["Krown", "Zed"]
    assert b["rejected"] == [{"analyst": "Qriptal", "video_id": "v3", "why": "quote not in transcript: x"}]
    assert b["last_ingest"] == "2026-10-28T10:53:28+00:00" and b["price"] is None
    # 76-77k -> 77,000 and 76,000 (range first), 81,180 from "$81,180"; ladder sorted high to low
    assert [(x["level"], x["analyst"]) for x in b["levels"]] == [(81180.0, "Zed"), (77000.0, "Krown"), (76000.0, "Krown")]
    out = tmp_path / "analyst_data.js"
    bad.write(b, out)
    text = out.read_text(encoding="utf-8")
    assert text.startswith("window.LIVE_AID_ANALYSTS = ") and json.loads(text[len("window.LIVE_AID_ANALYSTS = "):].rstrip().rstrip(";"))["asof"] == b["asof"]
