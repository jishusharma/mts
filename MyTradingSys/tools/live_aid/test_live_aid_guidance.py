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
    # operator 11-13: the card says what happened, never what follows (no follow-through has been measured)
    assert "What it shows: 3.0M of longs were forced to sell in 15 min (that selling pushed price down); next floor at 73,500 (Yesterday low)" in t, t
    win = {"15m": {"long": 100, "short": 5_000_000}}
    t = _txt(_run("H._liqCard({liq:{win:j.w,since:0},now:1e12},j.md)", {"w": win, "md": MD}))
    assert "5.0M of shorts were forced to buy in 15 min (that buying pushed price up); next ceiling at 74,000 (Today high)" in t, t
    t = _txt(_run("H._liqCard({liq:{win:j.w,since:0},now:1e12},j.md)", {"w": {"15m": {"long": 0, "short": 0}}, "md": MD}))
    assert "What it shows: quiet in the last 15 min" in t


def _lane(side, big=0, zone="mid", wt1=0):
    return {"side": side, "zone": zone, "wt1": wt1, "bars": [{"x": big, "strong": bool(big)}]}


def _wt(lanes, pre=""):
    # the chip-row tests read the CLOSED row; open is the default since 11-13, so close it first unless the test opens it itself
    return _run("(" + (pre or "H._wtSetOpen(false),") + "H._wtSoWhat({lanes:j},{lad:" + json.dumps(LAD) + "}))", lanes)


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
    h = _run("(H._wtSetOpen(false),H._wtSoWhat({lanes:{}},{}))", {})
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


# ---------- seven readings folded behind one click (operator 2026-11-13 "Yes, fold them") ----------
RAIL_CTX = {"now": NOW, "px": 73800, "rows5": ROWS5, "votes": [1, 1, -1, 0, 0, 0], "map": {}, "lanes": {}}


def _rail(pre, expr):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    js = pre + "const H=require(process.argv[1]);const el={innerHTML:'',getBoundingClientRect(){return{width:1200,height:700}},addEventListener(){}};" + expr
    out = subprocess.run([node, "-e", js, str(HERE / "home.js")], capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert out.returncode == 0, out.stderr[-1200:]
    return out.stdout


def test_seven_readings_are_one_collapsed_fold_on_the_home_rail():
    h = _rail("", "H.render(el," + json.dumps(RAIL_CTX) + ");console.log(el.innerHTML)")
    assert h.count('data-foldtoggle="1"') == 1 and "Folded readings" in h and "7 · show" in h
    assert 'class="hm-g"' not in h and "Direction <b" not in h                  # gauge is inside the fold, hidden by default
    assert "What the money is doing" not in _txt(h) and 'href="#verdict"' not in h
    o = _rail("", "H._foldSetOpen(true);H.render(el," + json.dumps(RAIL_CTX) + ");console.log(el.innerHTML)")
    assert 'class="hm-g"' in o and "Direction <b" in o and "7 · hide" in o                  # nothing deleted: gauge is back when opened
    for pg, name in [("verdict", "Verdict and watch list"), ("antic", "Same data, other readings"), ("bc", "Big candle story"), ("lap", "Level approach prep"), ("xliq", "Forced selling on other exchanges")]:
        assert 'href="#%s"' % pg in o and name in o


def test_fold_choice_is_remembered_per_viewer_and_storage_may_fail():
    mk = "globalThis.localStorage={_d:{%s},getItem(k){return k in this._d?this._d[k]:null},setItem(k,v){this._d[k]=v}};"
    assert _rail(mk % "", "H._foldSetOpen(true);console.log(localStorage._d.mts_fold_open)").strip() == "1"
    assert "7 · hide" in _rail(mk % "mts_fold_open:'1'", "console.log(H._foldCard({},{px:1,dir:'WAIT',bull:0,bear:0,n:0,lad:{above:[],below:[]},zones:[]}))")
    blocked = "Object.defineProperty(globalThis,'localStorage',{get(){throw new Error('blocked')},configurable:true});"
    assert "7 · hide" in _rail(blocked, "H._foldSetOpen(true);console.log(H._foldCard({},{px:1,dir:'WAIT',bull:0,bear:0,n:0,lad:{above:[],below:[]},zones:[]}))")


def test_folded_pages_still_exist_and_are_reachable():
    page = (HERE / "live_aid.html").read_text(encoding="utf-8")
    for pid, view in [("p-verdict", "verdict"), ("p-antic", "antic"), ("p-bc", "bc"), ("p-lap", "lap"), ("p-xliq", "xliq"), ("p-money", "money")]:
        assert '<section id="%s">' % pid in page                                       # nothing deleted
        assert re.search(r"\b%s: \['%s'," % (view, pid), page), view                    # and a route reaches it (antic/bc/lap/xliq had none)


# ---------- operator 2026-11-13 (2nd pass): volume off the candles, averages drawn, WaveTrend back, plain words ----------
T0 = 1794300000000   # a 5m boundary
def _bars(n, vol=100.0, buy=60.0):
    # 5m rows [t,o,h,l,c,vol,closeTime,quoteVol,trades,takerBuy]; close rises 10 per bar from 70,000
    return [[T0 + i * 300000, 70000 + i * 10, 70020 + i * 10, 69990 + i * 10, 70010 + i * 10, vol, T0 + (i + 1) * 300000 - 1, 0, 0, buy] for i in range(n)]


def test_volume_has_its_own_strip_and_no_bar_sits_on_the_candles():
    k = _bars(30)
    k[10][9] = 20.0                                                        # one bar where sellers took more
    ctx = {"now": T0 + 30 * 300000, "rows5": [r[:5] for r in k], "k5": k}
    md = {"px": 70300, "zones": [], "lad": {"at": None, "above": [], "below": []}}
    price = _run("H._chart(j.ctx,j.md,1000,400)", {"ctx": ctx, "md": md})
    assert "hm-vb" not in price and "hm-cvd" not in price                  # nothing overlaps the wicks any more
    vol = _run("H._volPane(j.ctx,j.md,1000,78)", {"ctx": ctx, "md": md})
    assert vol.count('class="hm-vb up"') == 29 and vol.count('class="hm-vb down"') == 1
    assert 'class="hm-vavg"' in vol and "white line = normal (20-bar average)" in vol


def test_volume_line_says_how_big_who_and_what_it_shows():
    k = _bars(24)
    k[23][5], k[23][9] = 200.0, 150.0                                      # last closed bar: 200 vs a 20-bar average of 100, buyers 150 of 200, bar up
    k.append([T0 + 24 * 300000, 1, 1, 1, 1, 9999.0, 0, 0, 0, 0.0])        # forming bar: must be ignored
    r = json.loads(_run("JSON.stringify(H._volRead(j))", {"now": T0 + 24 * 300000 + 1000, "k5": k}))
    # by hand: 200/100 = 2.0x >= 1.5 busy; 3-bar (200+100+100)/3 = 133 vs 100 = 1.33 >= 1.25 rising
    assert r["txt"] == "Volume: last closed 5m bar 2.0x normal (busy), buyers took more, 3-bar trend rising: the rise had real buying behind it", r["txt"]
    k2 = _bars(24)
    k2[23][5], k2[23][9] = 50.0, 10.0                                      # 0.5x: thin, sellers; (50+100+100)/3 = 83 vs 100 = 0.83: steady
    r2 = json.loads(_run("JSON.stringify(H._volRead(j))", {"now": T0 + 24 * 300000, "k5": k2}))
    assert r2["txt"] == "Volume: last closed 5m bar 0.5x normal (thin), sellers took more, 3-bar trend steady: few traders took part in the last move", r2["txt"]
    assert "not enough closed bars" in json.loads(_run("JSON.stringify(H._volRead(j))", {"now": T0 + 10 * 300000, "k5": _bars(10)}))["txt"]
    vfi = {"tfs": [], "r": {"15m": {"cells": {"vfi": {"v": 1, "rising": -1}}}, "1h": {"cells": {"vfi": {"v": -1, "rising": 1}}}}}
    h = html.unescape(_txt(_run("H._volRead(j).html", {"now": T0 + 24 * 300000, "k5": k2, "ind": vfi})))
    assert "Money flow (VFI): 15min ▼1hout ▲" in h, h


def test_krown_averages_are_drawn_on_the_5m_chart():
    # by hand, n=3, closes 1..5: seed = mean(1,2,3) = 2, alpha 0.5 -> 3, 4; the simple average gives the same here
    assert json.loads(_run("JSON.stringify([H._emaS(j,3),H._smaS(j,3)])", [1, 2, 3, 4, 5])) == [[None, None, 2, 3, 4], [None, None, 2, 3, 4]]
    assert json.loads(_run("JSON.stringify(H.MA5)", {})) == [["ema", 21, "21 EMA"], ["ema", 55, "55 EMA"], ["sma", 200, "200 SMA"]]
    k = _bars(30)
    ctx = {"now": T0 + 30 * 300000, "rows5": [r[:5] for r in k]}
    md = {"px": 70300, "zones": [], "lad": {"at": None, "above": [], "below": []}}
    svg = html.unescape(_run("H._chart(j.ctx,j.md,1000,400)", {"ctx": ctx, "md": md}))
    assert 'class="hm-ma m0"' in svg and 'class="hm-ma m1"' not in svg     # 30 bars: the 21 exists, the 55 and 200 do not
    assert "55 EMA needs 55 bars" in svg and "200 SMA needs 200 bars" in svg and "Averages on 5m (Krown’s set)" in svg


def test_wavetrend_is_open_by_default_and_only_his_click_closes_it():
    assert _run("H._wtLoad()", {}).strip() == "true"                        # no storage at all: open
    pre = "globalThis.localStorage={getItem(){return '0'},setItem(){}};"
    assert _rail(pre, "console.log(H._wtLoad())").strip() == "false"       # he hid the strips: stays hidden
    pre = "globalThis.localStorage={getItem(){throw new Error('blocked')},setItem(){}};"
    assert _rail(pre, "console.log(H._wtLoad())").strip() == "true"        # storage blocked: open


def test_plain_words_votes_bias_forced_flow_and_analyst_name():
    ind = {"tfs": [["15m", 0, "frame"]], "r": {}, "stale": False, "ver": {"15m": _ver(-1, 1, 5)}}
    t = _txt(_run("H._indCard({ind:j.ind},j.md)", {"ind": ind, "md": MD}))
    assert "5 of 6 say down" in t and "6 readings vote per timeframe: money flow, squeeze, trend strength, WaveTrend, RSI, buy vs sell volume. A lead of 2 wins." in t
    md = dict(MD, dir="SHORT", bull=1, bear=5, n=6)
    b = html.unescape(_run("H._biasLine({pulse:{hi:0}},j)", md))
    assert "The next few minutes lean DOWN; the bigger 1h-4h trend is MIXED. The short-term lean covers the next 15m candle only." in b
    assert "gauge" not in b and "backdrop" not in b and "now (minutes) DOWN 5/6" in b
    liq = {"win": {"1m": {"long": 2000000, "short": 0}, "15m": {"long": 3000000, "short": 100000}}}
    lt = html.unescape(_txt(_run("H._liqCard({liq:j.liq,now:1},j.md)", {"liq": liq, "md": MD})))
    assert "3.0M of longs were forced to sell in 15 min" in lt and "fuel is spent" not in lt
    assert "NOT MEASURED yet (no liquidation history is recorded)" in lt   # liq_rates.js has no rows: no rate is ever made up
    assert _run("H.zoneName(j)", {"items": [{"src": "analyst", "who": "Krown"}, {"src": "ma", "badge": "1WS20"}, {"src": "ma", "badge": "1WE21"}]}).strip() == "Krown call + Bull market band (weekly)"
    assert _run("H.zoneName(j)", {"items": [{"src": "analyst"}]}).strip() == "Analyst call"


def test_news_card_is_quiet_unless_something_matters():
    quiet = html.unescape(_txt(_run("H._newsCard(j)", {"now": 3600000 * 5, "news": [{"id": 1, "t": 3600000 * 5 - 60000, "score": 3, "head": "small thing", "tag": "NEUTRAL"}]})))
    assert "News that matters" in quiet and "Nothing important in the last hour" in quiet and "small thing" not in quiet
    long_head = "Fed cuts rates by 50 basis points in a surprise move, chair cites weakening labour market and falling inflation expectations"
    hot = html.unescape(_txt(_run("H._newsCard(j)", {"now": 3600000 * 5, "news": [{"id": 2, "t": 3600000 * 5 - 120000, "score": 9, "head": long_head, "tag": "POSITIVE"}]})))
    assert long_head in hot and "2 min ago" in hot                          # the full headline, not a 90-character cut


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
