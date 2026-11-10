"""Live Aid LEVEL STORY (levelstory.js, operator 2026-11-10): where price is against the nearest named level (rejected, breaking,
accepted, failed break, testing, away), the evidence, and the idea. Rules run in node; every expected value below is worked out by
hand from the rules in levelstory.js and the synthetic bars here. Skips (never fails) without node.

Common setup: 30 completed 15m bars. The "flat" bar is o=100 h=100.5 l=99.5 c=100 vol=20 delta=0, so all closes are 100,
Bollinger width is 0 (no BB evidence), average volume of the 20 bars before the last is 20.
Constants: touch 0.05% (reach = high >= L*0.9995), near 0.3%, wick share 0.5, rel volume 1.5, look 3 bars, idea needs 3 points.

BUG (levelstory.js line 23): res is taken from the LAST close, so closes beyond the level flip the level to the other side and
nb (closes beyond) is always 0. BREAKING and ACCEPTED can never fire; the two tests for them are xfail(strict) until fixed.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
STORY = HERE / "levelstory.js"

T0 = 1_794_182_400_000
M15 = 900_000


def _story(lv, k15, now, ex=None):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = "const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(P.story.apply(null,j.a)))})"
    out = subprocess.run([node, "-e", runner, str(STORY)], input=json.dumps({"a": [lv, k15, now, ex or {}]}), capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert out.returncode == 0, out.stderr[-1500:]
    return json.loads(out.stdout)


def bar(i, o=100.0, h=100.5, l=99.5, c=100.0, vol=20.0, delta=0.0):
    """Binance kline row i; taker buy = (vol + delta) / 2 so 2*buy - vol = delta."""
    t = T0 + i * M15
    return [t, o, h, l, c, vol, t + M15 - 1, 0, 0, (vol + delta) / 2]


def series(n=30):
    """n flat bars."""
    return [bar(i) for i in range(n)]


NOW = T0 + 30 * M15 + 1000   # all 30 bars are completed (last close time is T0 + 30*M15 - 1)


def keys(s):
    return [e["k"] for e in s["ev"]]


def test_rejected_resistance_with_absorption():
    """L=101 (resistance: last close 100 <= 101). Last bar o=100 h=101.5 l=99.9 c=100 vol=60 delta=+30 (buy 45).
    nb=0; reach 101.5 >= 100.9495 and close not above -> touch -> REJECTED.
    Wick share = (101.5-100)/(101.5-99.9) = 1.5/1.6 = 93.75% -> +1. Volume 60 / avg 20 = 3.0x >= 1.5 -> +1.
    Delta +30 with resistance (sgn +1) > 0 -> Absorb +2. Closes all 100 -> no BB. turn = 4, thru = 0.
    4 >= 3 and > 0 -> idea SHORT, voidAt = the wick high 101.5."""
    k = series(29) + [bar(29, h=101.5, l=99.9, vol=60.0, delta=30.0)]
    s = _story({"price": 101.0, "name": "R", "n": 1}, k, NOW)
    assert s["state"] == "REJECTED"
    assert s["res"] is True
    assert keys(s) == ["Wick", "Vol", "Absorb"]
    assert s["ev"][0]["t"] == "long upper wick 94% of the bar"
    assert s["ev"][1]["t"] == "volume 3.0x normal on the touch"
    assert s["turn"] == 4 and s["thru"] == 0
    assert s["idea"] == "SHORT"
    assert s["voidAt"] == 101.5
    assert s["bb"] is None


def test_support_mirror_gives_long():
    """L=99 (support: last close 100 > 99). Last bar o=100 h=100.1 l=98.5 c=100 vol=60 delta=-30 (buy 15).
    reach: low 98.5 <= 99*1.0005 = 99.0495, close 100 not below 99 -> REJECTED.
    Lower wick = (min(o,c)-l)/range = (100-98.5)/(100.1-98.5) = 1.5/1.6 = 93.75% -> +1; vol 3.0x -> +1;
    sgn=-1, delta -30 -> sgn*delta = +30 > 0 -> Absorb +2. turn 4 -> idea LONG, voidAt = wick low 98.5."""
    k = series(29) + [bar(29, h=100.1, l=98.5, vol=60.0, delta=-30.0)]
    s = _story({"price": 99.0, "name": "S", "n": 1}, k, NOW)
    assert s["state"] == "REJECTED"
    assert s["res"] is False
    assert keys(s) == ["Wick", "Vol", "Absorb"]
    assert s["turn"] == 4
    assert s["idea"] == "LONG"
    assert s["voidAt"] == 98.5


def test_accepted_two_closes_above_resistance_long():
    """L=101. Bars 28 and 29 close 102 and 102.3 (o=100 / 102, high 102.5, low 99.9 / 101.5) with buyer delta +10 each, vol 20.
    Two completed closes above 101 with buyers -> ACCEPTED; Close weight -3 (2 closes), CVD 'buyers drove the break' -1 -> thru 4.
    Break volume 20 vs avg 20 = 1.0x < 1.5 -> no Vol. thru 4 >= 3 and > turn -> idea LONG, voidAt = 101."""
    k = series(28) + [bar(28, o=100.0, h=102.5, l=99.9, c=102.0, delta=10.0), bar(29, o=102.0, h=102.5, l=101.5, c=102.3, delta=10.0)]
    s = _story({"price": 101.0, "name": "R", "n": 1}, k, NOW)
    assert s["state"] == "ACCEPTED"
    assert s["thru"] == 4
    assert s["idea"] == "LONG"
    assert s["voidAt"] == 101.0


def test_breaking_single_close_above_no_idea():
    """L=101, only the last bar closes above (102, delta +10, others flat) -> exactly one close beyond -> BREAKING.
    Close weight -1, CVD buyers -1 -> thru 2 < 3 -> no idea."""
    k = series(29) + [bar(29, o=100.0, h=102.5, l=99.9, c=102.0, delta=10.0)]
    s = _story({"price": 101.0, "name": "R", "n": 1}, k, NOW)
    assert s["state"] == "BREAKING"
    assert s["idea"] is None


def test_failed_break_back_below():
    """L=101. Bar 27 closes 102 (above), bars 28 and 29 are o=100.3 h=100.5 l=99.8 c=100 (back under). Highs 100.5 < 100.9495
    so no touch bar; nothing is beyond now (nb=0). Failed break: bar 27 (within 3 bars back) closed above, last close 100 is not -> FAILED BREAK.
    Only evidence: Trap +2 (no BB: last high 100.5 is below upper band minus 10% width ~100.8). turn 2 < 3 -> no idea."""
    k = series(27) + [bar(27, o=100.0, h=102.2, l=100.0, c=102.0), bar(28, o=100.3, h=100.5, l=99.8, c=100.0), bar(29, o=100.3, h=100.5, l=99.8, c=100.0)]
    s = _story({"price": 101.0, "name": "R", "n": 1}, k, NOW)
    assert s["state"] == "FAILED BREAK"
    assert keys(s) == ["Trap"]
    assert s["turn"] == 2
    assert s["idea"] is None


def test_testing_only_forming_bar_wicks():
    """30 flat completed bars (highs 100.5 < 100.9495, so no touch) plus a forming bar (closeTime >= now) with high 101.2 close 100.2.
    L=101: no closes beyond, no failed break, forming high 101.2 >= 100.9495 -> TESTING."""
    forming = bar(30, o=100.0, h=101.2, l=99.9, c=100.2)
    forming[6] = NOW + 600_000   # still open at "now"
    s = _story({"price": 101.0, "name": "R", "n": 1}, series(30) + [forming], NOW)
    assert s["state"] == "TESTING"
    assert s["idea"] is None


def test_forming_bar_not_used_for_closes():
    """A forming bar that is at 102 must not count as a completed close beyond 101 (not BREAKING) nor produce evidence."""
    forming = bar(30, o=100.0, h=101.2, l=99.9, c=102.0, vol=99.0, delta=40.0)
    forming[6] = NOW + 600_000
    s = _story({"price": 101.0, "name": "R", "n": 1}, series(30) + [forming], NOW)
    assert s["state"] == "TESTING"
    assert s["ev"] == []


def test_away_far_from_level():
    """L=102, closes 100: |100/102 - 1| = 1.96% > 0.3%. Highs 100.5 < 101.949, nothing forming -> AWAY, no idea."""
    s = _story({"price": 102.0, "name": "R", "n": 1}, series(30), NOW)
    assert s["state"] == "AWAY"
    assert s["idea"] is None
    assert s["valid"] == "nothing to do at this level yet"


def test_approaching_within_near_band():
    """L=100.3, closes 100: |100/100.3 - 1| = 0.2991% <= 0.3%. Bars with high 100.1 (< 100.3*0.9995 = 100.2498): no touch -> APPROACHING."""
    k = [bar(i, h=100.1) for i in range(30)]
    s = _story({"price": 100.3, "name": "R", "n": 1}, k, NOW)
    assert s["state"] == "APPROACHING"
    assert s["idea"] is None


def test_crowd_text_from_three_calls():
    """lv.n = 3 -> '3 calls here: wait for the 15m close, 1m wicks do not count'; n = 2 or missing -> ''."""
    k = series(30)
    assert _story({"price": 102.0, "name": "R", "n": 3}, k, NOW)["crowd"] == "3 calls here: wait for the 15m close, 1m wicks do not count"
    assert _story({"price": 102.0, "name": "R", "n": 5}, k, NOW)["crowd"] == "5 calls here: wait for the 15m close, 1m wicks do not count"
    assert _story({"price": 102.0, "name": "R", "n": 2}, k, NOW)["crowd"] == ""
    assert _story({"price": 102.0, "name": "R"}, k, NOW)["crowd"] == ""


def test_needs_25_completed_bars():
    """24 completed bars -> null; 24 plus a forming one -> null; 25 completed -> a story."""
    lv = {"price": 102.0, "name": "R", "n": 1}
    now24 = T0 + 24 * M15 + 1000
    assert _story(lv, series(24), now24) is None
    forming = bar(24)
    forming[6] = now24 + 600_000
    assert _story(lv, series(24) + [forming], now24) is None
    assert _story(lv, series(25), T0 + 25 * M15 + 1000)["state"] == "AWAY"


def test_bad_level_returns_null():
    assert _story(None, series(30), NOW) is None
    assert _story({"price": 0, "name": "R"}, series(30), NOW) is None


def _flash_kinds(ideas):
    """home.flashes with two injected level stories (ctx._st cache); returns the flash kinds raised."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    js = ("const H=require(process.argv[1]);const md={px:100,zones:[],lad:{above:[],below:[],at:null},dir:'WAIT'};"
          "const v=JSON.parse(process.argv[2]).map((s,i)=>({price:100+i,state:'REJECTED',idea:s,why:'w',valid:'v',ev:[]}));"
          "H._FL.list=[];H._FL.seen={};const out=H.flashes({now:1e12,k15:[1],setup:null,_st:{md:md,v:v}},md);console.log(JSON.stringify(out.map(f=>f.kind)))")
    out = subprocess.run([node, "-e", js, str(HERE / "home.js"), json.dumps(ideas)], capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert out.returncode == 0, out.stderr[-1500:]
    return json.loads(out.stdout)


def test_opposite_ideas_at_two_levels_raise_no_flash():
    # operator 2026-11-10 screenshot: LONG idea at 74,816 and SHORT idea at 74,950 at the same moment = noise
    assert _flash_kinds(["LONG", "SHORT"]) == []
    # operator 2026-11-10 (later): two SHORT banners for 74,816 and 74,850 were clutter; one banner, for the first (nearest) level
    assert _flash_kinds(["SHORT", "SHORT"]) == ["idea"]
