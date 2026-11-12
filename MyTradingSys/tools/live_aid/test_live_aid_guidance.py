"""Live Aid guidance rework (operator 2026-11-12): every panel says what to do (long / short / wait + the level), one verdict row per
timeframe, WaveTrend and liquidation panels with a so-what line, chart names its timeframe and axes. Expected texts are written by hand
from the rules in the card, not computed by the code. Skips without node."""
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
LAD = {"at": None, "above": [{"price": 74000, "name": "Today high"}], "below": [{"price": 73500, "name": "Yesterday low"}]}
MD = {"px": 73800, "zones": [], "dir": "WAIT", "bull": 0, "bear": 0, "n": 0, "lad": LAD}


def _run(expr, arg):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    js = "const H=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(" + expr + ")})"
    out = subprocess.run([node, "-e", js, str(HERE / "home.js")], input=json.dumps(arg), capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert out.returncode == 0, out.stderr[-1500:]
    return out.stdout


def _txt(h):
    return re.sub(r"<[^>]*>", "", h)


def _ver(side, up, dn, coiled=False):
    return {"side": side, "up": up, "dn": dn, "n": 6, "coiled": coiled,
            "word": "buyers winning" if side > 0 else "sellers winning" if side < 0 else "mixed, no one winning"}


def test_indicator_grid_is_one_plain_verdict_row_per_timeframe():
    ind = {"tfs": [["15m", 0, "frame"], ["1h", 0, "bias"], ["4h", 0, "context"]], "r": {}, "stale": False,
           "ver": {"15m": _ver(-1, 1, 4, True), "1h": _ver(-1, 2, 4), "4h": _ver(0, 3, 3)}}
    h = _run("H._indCard({ind:j.ind},j.md)", {"ind": ind, "md": MD})
    t = _txt(h)
    assert h.count('class="hm-vr ') == 3 and "hm-ir" not in h                       # three rows, the old grid is gone
    assert "sellers winning" in t and "mixed, no one winning" in t and "4 of 6" in t and "COILED" in t
    assert "COILED = quiet before a move" in t
    assert "So what: short side only while price stays under 74,000 (Today high)" in t   # 15m and 1h both sellers


def test_indicator_so_what_waits_when_15m_and_1h_disagree():
    ind = {"tfs": [["15m", 0, "frame"], ["1h", 0, "bias"]], "r": {}, "ver": {"15m": _ver(1, 4, 1), "1h": _ver(-1, 1, 4)}}
    t = _txt(_run("H._indCard({ind:j.ind},j.md)", {"ind": ind, "md": MD}))
    assert "So what: wait, nobody leads. Act only at 73,500 (Yesterday low) or 74,000 (Today high)" in t


def test_liquidation_panel_says_what_follows():
    win = {"15m": {"long": 3_000_000, "short": 200_000}}
    t = _txt(_run("H._liqCard({liq:{win:j.w,since:0},now:1e12},j.md)", {"w": win, "md": MD}))
    assert "So what: longs were forced out, selling fuel is spent: a long idea only if price holds the floor at 73,500 (Yesterday low)" in t
    win = {"15m": {"long": 100, "short": 5_000_000}}
    t = _txt(_run("H._liqCard({liq:{win:j.w,since:0},now:1e12},j.md)", {"w": win, "md": MD}))
    assert "short idea only if price holds the ceiling at 74,000 (Today high)" in t
    t = _txt(_run("H._liqCard({liq:{win:j.w,since:0},now:1e12},j.md)", {"w": {"15m": {"long": 0, "short": 0}}, "md": MD}))
    assert "So what: quiet, ignore" in t


def _lane(side, big=0, zone="mid", wt1=0):
    return {"side": side, "zone": zone, "wt1": wt1, "bars": [{"x": big, "strong": bool(big)}]}


def test_wavetrend_is_one_line_that_says_what_to_do():
    # operator 2026-11-13: six strips collapse into ONE line; 4h is the last CLOSED bar; levels from the ladder (written by hand)
    f = lambda lanes: html.unescape(_txt(_run("H._wtSoWhat({lanes:j},{lad:" + json.dumps(LAD) + "})", lanes)))
    lanes = {"1m": _lane(1), "2m": _lane(1), "3m": _lane(1), "15m": _lane(1, zone="cold"), "30m": _lane(1, zone="cold"), "4h": _lane(1, zone="cold", wt1=-62.5)}
    t = f(lanes)
    assert ("Timing 1-3m: all crossed up (long side only) · Frame 15m/30m: rising from oversold · "
            "4h (last closed bar): -62 oversold (backdrop, not a trigger) -> wait for a big green dot on 1m-3m, or a 15m close above 74,000") in t, t
    assert t.count("WaveTrend:") == 1
    dn = f({"1m": _lane(-1), "2m": _lane(-1), "3m": _lane(-1), "15m": _lane(-1), "30m": _lane(-1, 1), "4h": _lane(-1, wt1=10)})
    assert "all crossed down (short side only)" in dn and "4h (last closed bar): 10 (backdrop" in dn and "a 15m close below 73,500" in dn
    assert "Frame 15m/30m: 15m and 30m disagree" in f({"15m": _lane(1), "30m": _lane(-1)}) and f({"15m": _lane(1), "30m": _lane(-1)}).strip().endswith("-> wait [show strips]")


def test_wavetrend_strips_are_collapsed_until_clicked():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    h = _run("H._wtSoWhat({lanes:{}},{})", {})
    assert 'data-wttoggle="1"' in h and "[show strips]" in h
    out = _run("(H._wtSetOpen(true),H._wtSoWhat({lanes:{}},{}))", {})
    assert "[hide strips]" in out


def test_chart_names_its_axes_and_off_frame_levels_are_not_listed():
    rows = [[1_794_182_400_000 + i * 300_000, 73800, 73850, 73750, 73800, 1] for i in range(40)]
    svg = _run("H._chart({rows5:j.rows},j.md,1000,500)", {"rows": rows, "md": MD})
    assert "Price (USD)" in svg and "Time (UTC)" in svg
    assert _run("H._inFrame(j.md,{price:73800*1.015})", {"md": MD}).strip() == "true"
    assert _run("H._inFrame(j.md,{price:73800*1.05})", {"md": MD}).strip() == "false"


def test_conflict_names_the_idea_level_and_the_decider():
    md = dict(MD, dir="LONG", bull=5, bear=0, n=5)
    t = _txt(_run("H._biasLine({pulse:{hi:-0.5},k15:null},j.md)", {"md": md}))
    assert "conflict: long idea at 73,500 (Yesterday low) vs short big picture, stand aside until a 15m close decides" in t
