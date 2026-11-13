"""Tests for analyst_note.js (what happened to an analyst's level since it was said) and the analyst/weekly-band fields of level_registry.js.
Pure rules run in node; klines are hand-built 15m bars from 2026-11-07 00:00Z, expectations hand-computed (level 100)."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
NOTE = HERE / "analyst_note.js"
REG = HERE / "level_registry.js"
T0 = 1794009600000  # 2026-11-07T00:00:00Z in ms
Q = 900000
BANNED = re.compile(r"\b(should|expect|will|buy|sell)\b", re.I)


def _node(mod, fn, *args):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = "const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(P[j.fn].apply(null,j.a)))})"
    out = subprocess.run([node, "-e", runner, str(mod)], input=json.dumps({"fn": fn, "a": list(args)}), capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert out.returncode == 0, out.stderr[-1500:]
    return json.loads(out.stdout)


def bar(i, o, h, l, c):
    t = T0 + i * Q
    return [t, str(o), str(h), str(l), str(c), "1", t + Q - 1]


LV = {"price": 100, "published": "2026-11-07", "bias": "NEUTRAL", "who": "Krown", "said": "All-time high around $125,000"}
END = T0 + 10 * Q


def st(klines, level=LV, now=END):
    return _node(NOTE, "status", level, klines, now)


def test_untested():
    r = st([bar(0, 90, 95, 88, 92), bar(1, 92, 96, 90, 94)])
    assert (r["state"], r["since"], r["role"]) == ("UNTESTED", None, "ceiling")
    assert r["text"].endswith("Not reached since.") and r["text"].startswith("Krown 11-07:")


def test_held():
    r = st([bar(0, 90, 95, 88, 92), bar(1, 92, 101, 91, 97), bar(2, 97, 98, 95, 96)])
    assert (r["state"], r["since"], r["role"]) == ("HELD", T0 + Q, "ceiling")
    assert "Touched 11-07 00:15Z" in r["text"]


def test_broken():
    r = st([bar(0, 90, 95, 88, 92), bar(1, 92, 102, 91, 101), bar(2, 101, 104, 100.5, 103)])
    assert (r["state"], r["since"], r["role"]) == ("BROKEN", T0 + Q, "floor")
    assert "Broken up 11-07 00:15Z, now a floor." in r["text"]


def test_broken_down_from_above():
    r = st([bar(0, 110, 112, 105, 108), bar(1, 108, 109, 98, 99)])
    assert (r["state"], r["role"]) == ("BROKEN", "ceiling") and "Broken down 11-07 00:15Z" in r["text"]


def test_reclaimed():
    r = st([bar(0, 90, 95, 88, 92), bar(1, 92, 102, 91, 101), bar(2, 101, 104, 99, 103), bar(3, 103, 103, 96, 98)])
    assert (r["state"], r["since"], r["role"]) == ("RECLAIMED", T0 + 3 * Q, "ceiling")
    assert "Reclaimed 11-07 00:45Z, now a ceiling." in r["text"]


def test_wick_through_without_close_is_held_not_broken():
    assert st([bar(0, 90, 95, 88, 92), bar(1, 92, 103, 91, 99.99)])["state"] == "HELD"


def test_no_data():
    r = st([bar(0, 90, 95, 88, 92)])
    assert r["state"] == "NO_DATA" and "Not enough closed bars" in r["text"] and r["since"] is None
    assert st([])["state"] == "NO_DATA"


def test_forming_bar_ignored():
    ks = [bar(0, 90, 95, 88, 92), bar(1, 92, 96, 90, 94), bar(2, 94, 105, 93, 104)]
    assert st(ks, now=T0 + 3 * Q - 1)["state"] == "UNTESTED"      # bar 2 closes exactly at now: not yet closed
    assert st(ks, now=T0 + 3 * Q)["state"] == "BROKEN"


def test_bars_before_published_ignored():
    ks = [bar(-2, 120, 130, 99, 101), bar(-1, 101, 105, 99, 103), bar(0, 90, 95, 88, 92), bar(1, 92, 96, 90, 94)]
    r = st(ks)
    assert r["state"] == "UNTESTED"


def test_text_has_no_advice_words_and_is_short():
    for ks in ([bar(0, 90, 95, 88, 92), bar(1, 92, 96, 90, 94)],
               [bar(0, 90, 95, 88, 92), bar(1, 92, 102, 91, 101), bar(2, 101, 104, 99, 103), bar(3, 103, 103, 96, 98)],
               [bar(0, 90, 95, 88, 92)]):
        t = st(ks)["text"]
        assert not BANNED.search(t) and len(t) <= 125, t


def test_qriptal_shown_as_habib():
    lv = dict(LV, who="Qriptal")
    assert st([bar(0, 90, 95, 88, 92), bar(1, 92, 96, 90, 94)], lv)["text"].startswith("Habib 11-07")
    assert _node(NOTE, "label", {"who": "Qriptal", "published": "2026-11-07", "bias": "BULLISH"}) == "Habib 11-07 bullish"


def test_label():
    assert _node(NOTE, "label", {"who": "Krown", "published": "2026-11-07", "bias": "BEARISH"}) == "Krown 11-07 bearish"
    assert _node(NOTE, "label", {"who": "Rekt", "published": "2026-11-09", "bias": "NEUTRAL"}) == "Rekt 11-09"
    assert _node(NOTE, "label", {"bias": "BULLISH"}) == "Analyst"


def test_zone_label():
    def it(w, d):
        return {"src": "analyst", "who": w, "published": "2026-11-" + d, "bias": "NEUTRAL"}
    ma = {"src": "ma", "label": "MA", "badge": "1DE55"}
    assert _node(NOTE, "zoneLabel", {"items": [it("Krown", "07"), ma]}) == "Krown 11-07"
    assert _node(NOTE, "zoneLabel", {"items": [it("Krown", "07"), it("Rekt", "08")]}) == "Krown 11-07 + Rekt 11-08"
    assert _node(NOTE, "zoneLabel", {"items": [it("Krown", "07"), it("Rekt", "08"), it("Bob", "09"), it("Jala", "10")]}) == "Krown 11-07 + Rekt 11-08 +2"


def test_from_analysts_carries_who_said_published_expired():
    a = {"level": 69000, "analyst": "Qriptal", "published": "2026-11-07", "bias": "NEUTRAL", "said": "  " + "x" * 100, "expired": True}
    r = _node(REG, "fromAnalysts", [a, dict(a, analyst="Krown", expired=False)])
    assert r[0]["who"] == "Habib" and r[1]["who"] == "Krown"
    assert r[0]["said"] == "x" * 80 and r[0]["published"] == "2026-11-07"
    assert r[0]["expired"] is True and r[1]["expired"] is False
    assert r[0]["label"] == "Analyst" and r[0]["badge"] == "QR" and r[0]["src"] == "analyst"   # old fields unchanged


def test_from_ma_weekly_band_badges_and_merge_passthrough():
    rows = [{"tf": "1w", "avgs": {"sma20": {"v": 90000}, "ema21": {"v": 89000}, "ema200": {"v": 50000}}},
            {"tf": "1d", "avgs": {"sma20": {"v": 95000}}}]
    r = _node(REG, "fromMA", rows)
    badges = {x["badge"]: x["price"] for x in r}
    assert badges == {"1WE200": 50000, "1WS20": 90000, "1WE21": 89000}
    assert all(x["label"] == "MA" and x["src"] == "ma" for x in r)
    z = _node(REG, "merge", r)
    assert sorted(b for zz in z for b in zz["badges"]) == ["1WE200", "1WE21", "1WS20"]
    assert sum(len(zz["items"]) for zz in z) == 3
