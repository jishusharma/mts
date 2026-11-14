"""CBP Analyst Desk board: no tab repeats another tab's rows, and the board is not older than its sources.

Operator 2026-11-15: every CBP tab deduped and refreshed. A call, level or coin has ONE home.
The pure checks run on any HTML; the live check runs on the built board when this machine has CBP_HOME (else skipped).
"""
import os
import re
from pathlib import Path

import pytest

PANE = re.compile(r'<section class="pane" id="t-(\w+)"[^>]*>(.*?)</section>', re.S)
EVENT_ROW = re.compile(r"<li><time>([^<]*)</time><strong>([^<]*)</strong><span class=\"sym\">(.*?)</span>", re.S)
ALT_TILE = re.compile(r'<div class="alt"><b>([A-Z0-9]+)<s')
LADDER_ROW = re.compile(r'class="px (?:up|dn)"[^>]*>([^<]*)</text>.*?class="who">(\w[\w.]*) ', re.S)


def dedupe_problems(html):
    """Return a list of strings, empty when the board is clean."""
    panes = {k: v for k, v in PANE.findall(html)}
    bad = []
    seen = {}
    for tab, body in panes.items():
        for date, who, sym in EVENT_ROW.findall(body):
            key = (date, who, re.sub(r"<[^>]+>", "", sym))
            if key in seen and seen[key] != tab:
                bad.append("event %s %s shown on tab %s and %s" % (date, who, seen[key], tab))
            seen.setdefault(key, tab)
    coins = [c for c in ALT_TILE.findall(panes.get("alts", ""))]
    for c in sorted({c for c in coins if coins.count(c) > 1}):
        bad.append("coin %s appears %d times on the alts tab" % (c, coins.count(c)))
    rows = LADDER_ROW.findall(panes.get("levels", ""))
    for r in sorted({r for r in rows if rows.count(r) > 1}):
        bad.append("ladder level %s repeated" % (r,))
    return bad


def _board(events_now, events_trail, coins=("ETH",), ladder=()):
    li = '<li><time>%s</time><strong>%s</strong><span class="sym"><s>▼✗</s></span><p>x</p></li>'
    return ('<section class="pane" id="t-now" role="tabpanel">' + "".join(li % e for e in events_now) + "</section>"
            '<section class="pane" id="t-trail" role="tabpanel">' + "".join(li % e for e in events_trail) + "</section>"
            '<section class="pane" id="t-alts" role="tabpanel">' + "".join('<div class="alt"><b>%s<s class="up">✓</s></b></div>' % c for c in coins) + "</section>"
            '<section class="pane" id="t-levels" role="tabpanel">'
            + "".join('<text class="px up">%s</text><text class="who">%s · x</text>' % l for l in ladder) + "</section>")


def test_clean_board_has_no_problems():
    assert dedupe_problems(_board([("11/13", "Jala")], [("11/09", "Krown")])) == []


def test_event_on_now_and_trail_is_flagged():
    # the pre-change board: "What changed" (Now) and "Change log" (Trail) both listed the newest flips
    probs = dedupe_problems(_board([("11/13", "Jala")], [("11/13", "Jala"), ("11/09", "Krown")]))
    assert any("11/13 Jala" in p for p in probs)


def test_coin_twice_on_alts_is_flagged():
    # the pre-change board listed ETH under Buy and again under Dark horse
    assert any("ETH" in p for p in dedupe_problems(_board([], [], coins=("ETH", "ETH"))))


def test_same_ladder_level_twice_is_flagged():
    assert dedupe_problems(_board([], [], ladder=[("75,000", "Jala"), ("75,000", "Jala")]))


def _home():
    h = os.environ.get("CBP_HOME") or "F:/CryptoScrapper"
    return Path(h) if (Path(h) / "cbp_v2" / "cbp_board.html").is_file() else None


@pytest.mark.skipif(_home() is None, reason="no CBP_HOME on this machine")
def test_built_board_is_deduped():
    assert dedupe_problems((_home() / "cbp_v2" / "cbp_board.html").read_text(encoding="utf-8")) == []


@pytest.mark.skipif(_home() is None, reason="no CBP_HOME on this machine")
def test_built_board_not_older_than_its_sources():
    home = _home()
    board = (home / "cbp_v2" / "cbp_board.html").stat().st_mtime
    for src in ("cbp_store/verdicts.json", "cbp_store/rows.json"):
        p = home / src
        if p.is_file():
            assert board >= p.stat().st_mtime, "cbp_board.html older than %s: run cbp_v2/tools/build_board.py" % src
