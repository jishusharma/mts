"""Live Aid Home key and divergence (operator 2026-11-13, 3rd ask): flag markers on a bottom rail, a key line, the divergence line and
its wiring into the LONG / SHORT board. Expected texts written by hand. Skips without node."""
import html
import json
import re

from test_live_aid_guidance import FLAG, MD, NOW, ROWS5, ZMD, _run, _txt


# ---------- operator 2026-11-13 (3rd ask): markers off the candles, a key, WaveTrend how-to, divergence ----------
def test_flag_markers_sit_on_the_bottom_rail_one_per_bar():
    # by hand: chart 1000x500 -> bottom of the price pane B = 500 - 30 = 470; an UP marker's tip is at B - 9 = 461, a DOWN one's at B - 2 = 468
    two = [dict(FLAG, evidence="first"), dict(FLAG, evidence="second", side="DOWN")]
    svg = _run("H._chart(j.ctx,j.md,1000,500)", {"ctx": {"now": NOW, "rows5": ROWS5, "flagRows": two}, "md": ZMD})
    marks = re.findall(r'<path d="M[\d.]+ ([\d.]+) [^"]*" class="hm-fm (\w+)"><title>([^<]*)', svg)
    assert len(marks) == 1, marks                                           # two flags in one 5m bar: one marker
    assert marks[0][0] == "468" and marks[0][1] == "down"                   # the last flag of the bar, on the rail, not at its price
    assert "second (+1 more in this 5m bar)" in html.unescape(marks[0][2])


def test_chart_key_explains_the_triangles():
    t = html.unescape(_txt(_run("H._caption(j.ctx,j.md)", {"ctx": {"now": NOW, "rows5": ROWS5, "flagRows": [FLAG]}, "md": ZMD})))
    assert "Key small triangles on the bottom edge = the LONG / SHORT board or a level alert changed in that 5m bar" in t
    assert "▲ green long-side readings switched on · ▼ red short-side · ▲ amber both or neither" in t
    assert "A log mark, not a signal" in t and "21 EMA, 55 EMA, 200 SMA" in t


def test_divergence_line_and_board_wiring():
    pulse = {"hi": 0, "rows": [{"tf": "5m", "r": {"div": {"rsi": 0, "wt": 1, "cvd": None}}}, {"tf": "15m", "r": {"div": {"rsi": -1, "wt": -1, "cvd": 0}}},
                               {"tf": "1m", "r": {"div": {"rsi": 1, "wt": 1, "cvd": 1}}}, {"tf": "1h", "r": None}]}
    t = _run("H._divLine(j)", {"pulse": pulse})
    assert "5m bullish WaveTrend · 15m bearish WaveTrend + bearish RSI · 1h no data" in t
    assert "OURS" in t
    bi = json.loads(_run("JSON.stringify(H._boardInputs(j))", {"pulse": pulse}))
    assert sorted(bi) == ["15m", "5m"] and bi["5m"]["div"]["wt"] == 1       # 1m is not wired (noise), 1h has no data
    card = _txt(_run("H._boardCard(j.ctx,j.md)", {"ctx": {"pulse": pulse}, "md": MD}))
    assert "5m WaveTrend divergence" in card and "15m RSI divergence" in card
