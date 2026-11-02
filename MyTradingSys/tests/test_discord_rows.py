"""discord_rows: IST->UTC, hand rows, message JSON, DOM HTML parse, ingest dedupe. Hand-made fixtures only."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys"))
sys.path.insert(0, str(ROOT / "MyTradingSys" / "cbp"))

import cbp  # noqa: E402
import discord_rows as dr  # noqa: E402

HTML = """<ul>
<li id="chat-messages-111-901"><h3><span class="username-x username">Hab</span><time datetime="2026-10-13T11:00:00.000Z">x</time></h3>
<div id="message-content-901">BTC needs <b>82k</b> hold,   else lower</div></li>
<li id="chat-messages-111-902"><time datetime="2026-10-13T12:00:00.000Z">x</time><div id="message-content-902"></div></li>
</ul>"""


def test_ist_to_utc_three_samples():
    assert dr.ist_to_utc("2026-10-13 16:30") == datetime(2026, 10, 13, 11, 0, tzinfo=timezone.utc)
    assert dr.ist_to_utc("2026-10-14 20:34") == datetime(2026, 10, 14, 15, 4, tzinfo=timezone.utc)
    assert dr.ist_to_utc("2026-10-16 03:00") == datetime(2026, 10, 15, 21, 30, tzinfo=timezone.utc)


def test_hand_row_valid_and_query(tmp_path):
    f = tmp_path / "h.json"
    f.write_text(json.dumps([
        {"src": "s", "posted_local": "2026-10-13 16:30", "kind": "RECAP", "dir": "long", "entry": "81,944", "q": "caught the long"},
        {"src": "s", "posted_local": "2026-10-14 20:34", "kind": "VIEW", "dir": "NOT STATED", "q": "brick wall"},
        {"src": "s", "posted_local": "bad", "q": "x"},
    ]), encoding="utf-8")
    rows, rej = dr.load_rows(f, "habib-tt", "Habib")
    assert len(rows) == 2 and len(rej) == 1
    assert all(cbp.validate_row(r) == [] and r["channel"] == "habib-tt" for r in rows)
    assert rows[0]["published_utc"] == "2026-10-13T11:00:00Z" and rows[0]["bias"] == "BULLISH"
    assert rows[1]["bias"] == "NO_VIEW" and rows[1]["trades"] == []
    store = tmp_path / "s.json"
    assert dr.ingest(rows, store) == 2 and dr.ingest(rows, store) == 0
    now = datetime(2026, 10, 15, tzinfo=timezone.utc)
    assert len(cbp.query(channel="habib-tt", now=now, store=store)) == 2
    assert cbp.query(channel="other", now=now, store=store) == []


def test_message_json_rejects_naive_and_empty():
    msgs = [{"id": 1, "timestamp": "2026-10-13T11:00:00Z", "author": {"name": "K"}, "content": "long 80k"},
            {"id": 2, "timestamp": "2026-10-13T11:00:00", "content": "naive"},
            {"id": 3, "timestamp": "2026-10-13T11:00:00Z", "content": ""}]
    rows, rej = dr.parse_messages_json(json.dumps(msgs), "krown")
    assert len(rows) == 1 and len(rej) == 2 and rows[0]["analyst"] == "K"


def test_html_parse():
    rows, rej = dr.parse_html(HTML, "habib-tt")
    assert len(rows) == 1 and len(rej) == 1  # empty content rejected
    r = rows[0]
    assert r["analyst"] == "Hab" and r["quotes"] == ["BTC needs 82k hold, else lower"]
    assert r["published"] == "2026-10-13" and cbp.validate_row(r) == []


def test_cli_dry_run_writes_nothing(tmp_path):
    h = tmp_path / "p.html"
    h.write_text(HTML, encoding="utf-8")
    store = tmp_path / "st.json"
    assert dr.main(["--html", str(h), "--channel", "c", "--store", str(store)]) == 0
    assert not store.exists()
    assert dr.main(["--html", str(h), "--channel", "c", "--store", str(store), "--ingest"]) == 0
    assert len(cbp.load(store)["rows"]) == 1
