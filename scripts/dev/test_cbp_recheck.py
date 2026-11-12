"""test_cbp_recheck.py - cbp_run --recheck marks bad stored trades (no delete), --quick-new lists unknown uploads, the supervisor wake runs it."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "MyTradingSys"))
import cbp
import cbp_run

NOW = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)


def _row(vid, bias, trades):
    return {"analyst": "Krown", "video_id": vid, "published": "2026-11-11", "bias": bias, "symbols": ["BTC"],
            "quotes": [], "pointers": [], "quote_verified": True, "expires_at": "2026-11-16T00:00:00Z", "trades": trades}


def _t(d, entry, target, stop):
    return {"asset": "BTC", "direction": d, "entry": entry, "target": target, "invalidation": stop, "quote": "q"}


def _store(tmp_path):
    p = tmp_path / "rows.json"
    cbp.save({"schema": 1, "rows": [_row("bad", "BEARISH", [_t("LONG", "74573", "77,000", "82,000")]),
                                    _row("ok", "BULLISH", [_t("LONG", "74000", "77,000", "72,000")])], "rejected": []}, p)
    return p


def test_recheck_marks_wrong_side_stop_keeps_text(tmp_path):
    p = _store(tmp_path)
    out = cbp_run.recheck(p, spot=lambda a, d: 74000.0)
    assert [(v, f) for _, v, f in out] == [("bad", ["stop_wrong_side", "bias_contradicts_trades"])]
    rows = {r["video_id"]: r for r in cbp.load(p)["rows"]}
    assert rows["bad"]["trades"][0]["invalidation"] == "82,000"      # not deleted
    assert rows["bad"]["trades"][0]["flag"] == "stop_wrong_side"
    assert "flags" not in rows["ok"]
    assert cbp.is_tradable(rows["bad"]) is False and cbp.is_tradable(rows["ok"]) is True
    assert cbp_run.recheck(p, spot=lambda a, d: 74000.0) == out     # idempotent


def test_recheck_flags_far_entry(tmp_path):
    p = _store(tmp_path)
    out = cbp_run.recheck(p, spot=lambda a, d: 90000.0)
    assert {v for _, v, f in out if "entry_far_from_spot" in f} == {"bad", "ok"}


def test_quick_new_lists_only_unknown(tmp_path, monkeypatch):
    p = _store(tmp_path)
    monkeypatch.setattr(cbp_run, "analysts", lambda: ({"exclude_regex": "(?i)#shorts", "include_regex": "btc"},
                                                      [{"short": "Krown", "channel": "@ECKrown"}]))
    monkeypatch.setattr(cbp_run, "local_videos", lambda c: [])
    fake = lambda ch, n: [("ok", "T", "2026-11-11"), ("newv", "T", "2026-11-12"), ("old", "T", "2026-10-01"), ("sh", "x #shorts", "2026-11-12")]
    got = cbp_run.quick_new(NOW, store=p, lister=fake, state=tmp_path / "st.json")
    assert got == [("Krown", "newv")]
    again = cbp_run.quick_new(NOW, store=p, lister=lambda c, n: 1 / 0, state=tmp_path / "st.json")   # inside the TTL: no listing
    assert again == [("Krown", "newv")]


def test_supervisor_wake_runs_quick_new():
    import supervisor
    src = Path(supervisor.__file__).read_text(encoding="utf-8")
    assert "cbp_run.py --due --quick-new" in src
