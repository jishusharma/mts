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


def _wt(lanes, pre=""):
    return _run(pre + "H._wtSoWhat({lanes:j},{lad:" + json.dumps(LAD) + "})", lanes)


def test_wavetrend_is_one_chip_row_and_keeps_the_sentence_in_the_tooltip():
    # operator 2026-11-13 (2nd ask): one compact row: six timeframe chips + last cross and age; the full sentence is NOT lost (tooltip)
    lanes = {"1m": _lane(1), "2m": _lane(1), "3m": _lane(1), "15m": _lane(1, zone="cold"), "30m": _lane(1, zone="cold"), "4h": _lane(1, zone="cold", wt1=-62.5)}
    lanes["3m"]["ms"], lanes["3m"]["last"] = 180000, {"side": 1, "ago": 2, "strong": True}      # 6 min ago
    lanes["15m"]["ms"], lanes["15m"]["last"] = 900000, {"side": 1, "ago": 1, "strong": False}   # 15 min ago
    h = _wt(lanes)
    t = html.unescape(_txt(h))
    assert t.count("WaveTrend") == 1 and "1m▲" in t and "15m▲ OS" in t and "4h▲ OS" in t, t
    assert "last cross 3m ▲ up (big dot), 6 min ago" in t, t
    assert "Timing 1-3m" not in t                                           # the long sentence is no longer on the row
    tip = html.unescape(re.search(r'title="([^"]*)"', h).group(1))
    assert ("Timing 1-3m: all crossed up (long side only) · Frame 15m/30m: rising from oversold · "
            "4h (last closed bar): -62 oversold (backdrop, not a trigger) -> wait for a big green dot on 1m-3m, or a 15m close above 74,000") in tip, tip
    dn = html.unescape(re.search(r'title="([^"]*)"', _wt({"1m": _lane(-1), "2m": _lane(-1), "3m": _lane(-1), "15m": _lane(-1), "30m": _lane(-1, 1), "4h": _lane(-1, wt1=10)})).group(1))
    assert "all crossed down (short side only)" in dn and "4h (last closed bar): 10 (backdrop" in dn and "a 15m close below 73,500" in dn
    mixed = html.unescape(re.search(r'title="([^"]*)"', _wt({"15m": _lane(1), "30m": _lane(-1)})).group(1))
    assert "Frame 15m/30m: 15m and 30m disagree" in mixed and "last cross: none in view" in html.unescape(_txt(_wt({"15m": _lane(1)})))


def test_wavetrend_strips_are_collapsed_until_clicked():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    h = _run("H._wtSoWhat({lanes:{}},{})", {})
    assert 'data-wttoggle="1"' in h and "[show strips]" in h and "hm-wfull" not in h
    out = _run("(H._wtSetOpen(true),H._wtSoWhat({lanes:{}},{}))", {})
    assert "[hide strips]" in out and "hm-wfull" in out                     # open: the full sentence appears above the strips


def test_wavetrend_open_choice_is_remembered_per_viewer_and_storage_may_fail():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    run = lambda pre, expr: subprocess.run([node, "-e", pre + "const H=require(process.argv[1]);console.log(" + expr + ")", str(HERE / "home.js")],
                                           capture_output=True, text=True, encoding="utf-8", timeout=60)
    mk = "globalThis.localStorage={_d:{%s},getItem(k){return k in this._d?this._d[k]:null},setItem(k,v){this._d[k]=v}};"
    r = run(mk % "", "(H._wtSetOpen(true),localStorage._d.mts_wt_open)")
    assert r.returncode == 0 and r.stdout.strip() == "1", r.stderr[-800:]                     # click saved
    r = run(mk % "mts_wt_open:'1'", "H._wtSoWhat({lanes:{}},{}).includes('[hide strips]')")
    assert r.stdout.strip() == "true", r.stderr[-800:]                                        # reload: still open
    r = run("Object.defineProperty(globalThis,'localStorage',{get(){throw new Error('blocked')},configurable:true});", "(H._wtSetOpen(true),H._wtSoWhat({lanes:{}},{}).includes('[hide strips]'))")
    assert r.returncode == 0 and r.stdout.strip() == "true", r.stderr[-800:]                  # storage blocked: no crash


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


# ---------- 5-minute chart explains itself (operator 2026-11-13, part C) ----------
D0 = 1_794_528_000_000                      # 2026-11-13 00:00Z
NOW = D0 + 10 * 3600_000 + 3 * 60_000       # 10:03Z: the 10:00 bar is still forming
ROWS5 = [[D0 + 8 * 3600_000 + i * 300_000, 73800, 73850, 73750, 99999 if D0 + 8 * 3600_000 + i * 300_000 == D0 + 10 * 3600_000 else 73800, 1] for i in range(25)]
ZMD = dict(MD, zones=[{"price": 74000, "name": "Today high", "n": 1}, {"price": 73500, "name": "Yesterday low", "n": 1}, {"price": 76000, "name": "Week high", "n": 1}])
FLAG = {"t": D0 + 9 * 3600_000 + 30 * 60_000, "kind": "touch", "level": "Yesterday low 73500", "side": "UP", "price": 73760, "evidence": "TOUCHING Yesterday low 73500"}


def test_caption_is_plain_words_from_closed_bars_with_hit_rate_and_n():
    ctx = {"now": NOW, "rows5": ROWS5, "flagRows": [FLAG], "flagStats": {"touch": {"n": 12, "hit": 58.3}}}
    t = html.unescape(_txt(_run("H._caption(j.ctx,j.md)", {"ctx": ctx, "md": ZMD})))
    # by hand: last CLOSED bar opens 09:55, closes 10:00 at 73,800 (the forming 10:00 bar at 99,999 is ignored); 200/73800=0.27%, 300/73800=0.41%
    assert ("Last closed 5m bar 10:00Z at 73,800: 0.27% under Today high 74,000, 0.41% over Yesterday low 73,500 · session Europe · "
            "last flag touch Yesterday low 73500 at 09:30Z, hit rate 58% of n 12 (too few to trust)") in t, t
    assert "levels SOURCED, session hours and this line OURS" in t
    nof = html.unescape(_txt(_run("H._caption(j.ctx,j.md)", {"ctx": dict(ctx, flagStats={}), "md": ZMD})))
    assert "hit rate not scored yet (n 0)" in nof
    none = html.unescape(_txt(_run("H._caption(j.ctx,j.md)", {"ctx": dict(ctx, flagRows=[]), "md": ZMD})))
    assert "no flag logged yet" in none
    assert "NOT_IN_DATA" in _txt(_run("H._caption(j.ctx,j.md)", {"ctx": {"now": NOW, "rows5": []}, "md": ZMD}))


def test_chart_has_flag_markers_and_session_high_low_lines():
    ctx = {"now": NOW, "rows5": ROWS5, "flagRows": [FLAG]}
    svg = _run("H._chart(j.ctx,j.md,1000,500)", {"ctx": ctx, "md": ZMD})
    assert 'class="hm-fm up"' in svg and "touch 09:30Z: TOUCHING Yesterday low 73500" in svg
    assert "Europe high so far (OURS)" in svg and "Europe low so far (OURS)" in svg
    assert "Asia high" not in svg                                           # fewer than 3 closed Asia bars on screen: no line
    plain = _run("H._chart(j.ctx,j.md,1000,500)", {"ctx": {"now": NOW, "rows5": ROWS5}, "md": ZMD})
    assert "hm-fm" not in plain.replace(".hm-fm", "")                       # no flag rows, no markers
