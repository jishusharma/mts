"""News headline panel contract (news_feed.js, card news-headline-panel-tree-rest-1108).

Context only: the panel shows Tree News headlines, marks importance >= 7 and tags words from the N6 list
(research/news_feeds_2026-10-30/REPORT.md). It gates and sizes nothing.
Expected values below are written by hand from the saved sample (research/news_feeds_2026-10-30/sample_tree_news.json,
20 items fetched 2026-11-08), not taken from the code.
Run: python MyTradingSys/tools/live_aid/test_news_feed.py
"""
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JS = HERE / "news_feed.js"
SAMPLE = HERE.parent.parent / "research" / "news_feeds_2026-10-30" / "sample_tree_news.json"

COINDESK = "1794073023724CUTmtcoceMo1biaif"   # importance 7.1: the one item >= 7 in the sample
TECHCRUNCH = "1794072247815TBCiltpanva6bh"    # "... after $6.3 billion hack", importance 5.2
CNA = "1794073010301CBCKNsdJYnnfc"            # Binance CFO steps down, importance 5.2

RUNNER = r"""
const fs = require('fs');
const NF = require(process.argv[1]);
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(payload.map(c => NF[c.fn].apply(null, c.args || []))));
"""


def call(*calls):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed or not on PATH")
    assert JS.exists(), "news_feed.js missing"
    p = subprocess.run([node, "-e", RUNNER, str(JS)], input=json.dumps([{"fn": f, "args": list(a)} for f, *a in calls]),
                       capture_output=True, text=True, timeout=30)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


def sample():
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def test_sample_is_20_tree_items():
    items = sample()
    assert len(items) == 20
    assert all({"_id", "source", "title", "url", "time", "importance"} <= set(x) for x in items)


def test_rows_last_12_newest_first_with_utc_time():
    items = sample()
    (rows,) = call(("rows", items, 12))
    assert len(rows) == 12
    newest = sorted(items, key=lambda x: -x["time"])[:12]
    assert [r["id"] for r in rows] == [x["_id"] for x in newest]
    r0 = rows[0]
    assert r0["utc"] == datetime.fromtimestamp(newest[0]["time"] / 1000, timezone.utc).strftime("%H:%M:%S")
    assert r0["source"] == newest[0]["source"] and r0["score"] == newest[0]["importance"]


def test_three_known_items_are_classified():
    items = sample()
    (rows,) = call(("rows", items, 20))
    by = {r["id"]: r for r in rows}
    # 7.1 COINDESK: marked, no N6 word in the title
    assert by[COINDESK]["hi"] is True and by[COINDESK]["score"] == 7.1 and by[COINDESK]["tags"] == []
    # TECHCRUNCH: the word "hack" tags it, 5.2 is under the mark
    assert by[TECHCRUNCH]["tags"] == ["hack"] and by[TECHCRUNCH]["hi"] is False
    # CNA: plain item, neither marked nor tagged
    assert by[CNA]["hi"] is False and by[CNA]["tags"] == []
    assert sum(1 for r in rows if r["hi"]) == 1


def test_mark_boundary_is_importance_7():
    (a, b, c, d) = call(("mark", {"importance": 6.9}), ("mark", {"importance": 7}), ("mark", {"importance": "8.5"}), ("mark", {"importance": None}))
    assert (a, b, c, d) == (False, True, True, False)


@pytest.mark.parametrize("title,want", [
    ("Exchange hacked, attacker drains hot wallet", ["hack"]),
    ("Kraken suspends withdrawals after exploit", ["hack", "halt"]),
    ("SEC delays spot ETF decision", ["etf"]),
    ("Fed holds rates, CPI hotter than forecast", ["fed"]),
    ("New sanctions and tariffs announced", ["war"]),
    ("Binance will delist three pairs", ["delist"]),
    ("Gold rallies again", []),
    ("", []),
])
def test_n6_word_tags(title, want):
    (got,) = call(("tags", title))
    assert got == want


def test_poll_only_while_visible_every_15s():
    t = 1_000_000
    got = call(("shouldPoll", False, 0, t), ("shouldPoll", True, 0, t), ("shouldPoll", False, t - 14_900, t),
               ("shouldPoll", False, t - 15_000, t), ("shouldPoll", True, t - 60_000, t))
    assert [g[0] if isinstance(g, list) else g for g in got] == [True, False, False, True, False]


def test_fetch_limit_20_while_current_and_300_after_a_gap():
    t = 10_000_000
    got = call(("fetchLimit", 0, t), ("fetchLimit", t - 15_000, t), ("fetchLimit", t - 119_000, t), ("fetchLimit", t - 600_000, t))
    assert got == [300, 20, 20, 300]


def test_page_wires_the_module_and_the_visibility_gate():
    page = (HERE / "live_aid.html").read_text(encoding="utf-8")
    assert page.count('<script src="news_feed.js"></script>') == 1
    assert "NF.shouldPoll(document.hidden" in page
    assert "setInterval(loadNews, 15000)" not in page, "unconditional 15 s poll must be gone"
    sys.path.insert(0, str(HERE))
    import build_artifact
    built = build_artifact.build()
    assert 'src="news_feed.js"' not in built and "root.NEWSFEED = api" in built


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
