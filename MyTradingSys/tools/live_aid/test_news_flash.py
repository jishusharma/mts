"""News flash card (news_flash.js): one important headline with detail, else a quiet line. Hand-built items, run through node."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JS = HERE / "news_flash.js"
NOW = 1_800_000_000_000
MIN = 60000
RUNNER = r"""
const fs = require('fs');
const NF = require(process.argv[1]);
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(payload.map(c => NF[c.fn].apply(null, c.args || []))));
"""
LONG = ("Bitcoin spot ETFs record largest daily inflow since March as issuers report fresh demand across several funds, "
        "data from analysts shows")
BANNED = re.compile(r"\b(should|expect\w*|will|buy|sell)\b", re.I)


def call(fn, *args):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed or not on PATH")
    p = subprocess.run([node, "-e", RUNNER, str(JS)], input=json.dumps([{"fn": fn, "args": list(args)}]),
                       capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)[0]


def item(i, ago, score, head="Some headline", tag="NEUTRAL", **kw):
    d = {"id": i, "t": NOW - ago * MIN, "score": score, "head": head, "tag": tag}
    d.update(kw)
    return d


def test_quiet_hour_shows_minor_count_and_link():
    items = [item(1, 5, 3), item(2, 20, 6.9), item(3, 30, 5)]
    p = call("pick", items, NOW)
    assert p["quiet"] and p["top"] is None and p["minor"] == 3
    h = call("html", items, NOW)
    assert "Nothing important in the last hour (3 minor headlines)" in h
    assert '<a href="#news">all 3 headlines</a>' in h


def test_empty_hour():
    h = call("html", [], NOW)
    assert "(0 minor headlines)" in h and 'href="#news"' in h


def test_one_important_full_headline_and_detail_line():
    items = [item(1, 4, 8, LONG, "POSITIVE", source="Tree"), item(2, 10, 2)]
    assert len(LONG) > 90
    p = call("pick", items, NOW)
    assert p["top"]["id"] == 1 and p["also"] == [] and p["minor"] == 1 and not p["quiet"]
    d = call("detail", items[0], NOW)
    assert d["head"] == LONG and d["kind"] == "ETF flows / regulation" and d["lean"] == "good for BTC"
    assert d["age"] == "4 min ago" and d["source"] == "Tree"
    h = call("html", items, NOW)
    assert LONG in h and "nf-up" in h
    assert "ETF flows / regulation · good for BTC · 4 min ago · Tree" in h
    assert "all 2 headlines" in h


def test_two_important_order_and_also():
    items = [item(1, 30, 7), item(2, 3, 9, "Exchange drained in hack", "NEGATIVE"), item(3, 8, 7.5), item(4, 9, 7.2)]
    p = call("pick", items, NOW)
    assert p["top"]["id"] == 2 and [x["id"] for x in p["also"]] == [3, 4] and p["minor"] == 0
    h = call("html", items, NOW)
    assert h.count('class="nf-also"') == 2 and "nf-down" in h


def test_tie_goes_to_newest():
    p = call("pick", [item(1, 20, 8), item(2, 5, 8)], NOW)
    assert p["top"]["id"] == 2


def test_older_than_60_min_ignored():
    items = [item(1, 61, 9), item(2, 30, 4)]
    p = call("pick", items, NOW)
    assert p["quiet"] and p["minor"] == 1
    assert "all 1 headline<" in call("html", items, NOW)


def test_weight_fields_preferred_when_present():
    # W 70 qualifies even with a low score; W 30 with a high score does not
    p = call("pick", [item(1, 5, 2, w=70, k=0), item(2, 4, 9, w=30, k=0)], NOW)
    assert p["top"]["id"] == 1 and p["minor"] == 1


def test_past_clause_from_news_weight():
    d = call("detail", item(1, 2, 8, "CPI comes in hotter than forecast", "NEGATIVE"), NOW)
    assert d["kind"] == "Macro data" and d["past"].startswith("Past:") and "2026-10-14" in d["past"] and "-1.2%" in d["past"]
    assert call("detail", item(1, 2, 8), NOW)["past"] == ""


def test_html_escapes():
    bad = 'A <b>"x"</b> & y'
    h = call("html", [item(1, 1, 9, bad, source="<s>")], NOW)
    assert "&lt;b&gt;&quot;x&quot;&lt;/b&gt; &amp; y" in h and "<b>" not in h and "&lt;s&gt;" in h


def test_no_forecast_words_in_generated_text():
    cpi = "CPI comes in hotter than forecast"
    items = [item(1, 2, 9, cpi, "NEGATIVE", source="Tree"), item(2, 5, 8), item(3, 9, 1)]
    for its in (items, [item(1, 5, 2)]):
        text = re.sub(r"<[^>]+>", " ", call("html", its, NOW)).replace(cpi, "").replace("Some headline", "")
        assert not BANNED.search(text), text
    d = call("detail", items[0], NOW)
    assert not BANNED.search(" ".join(str(d[k]) for k in ("kind", "lean", "age", "past")))
