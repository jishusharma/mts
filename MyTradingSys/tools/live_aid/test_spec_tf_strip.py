"""Timeframe strip contract (tf_strip.js). Expected numbers are hand-computed in the comments, not taken from the code."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JS = HERE / "tf_strip.js"
D0 = 1_800_000_000_000 - (1_800_000_000_000 % 86_400_000)  # a UTC midnight
MIN = 60_000


def _run(expr, payload):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    assert JS.exists(), "tf_strip.js missing"
    runner = ("const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(" + expr + "))})")
    out = subprocess.run([node, "-e", runner, str(JS)], input=json.dumps(payload),
                         capture_output=True, text=True, encoding="utf-8", timeout=30, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def k(t, o, h, l, c, vol=1, buy=0.5, span=MIN):
    return [t, str(o), str(h), str(l), str(c), str(vol), t + span - 1, "0", 1, str(buy), "0", "0"]


def test_colour_green_red_and_flat_is_none():
    assert _run("[P.colour(j[0]),P.colour(j[1]),P.colour(j[2]),P.colour(j[3])]",
                [k(0, 1, 2, 1, 2), k(0, 2, 2, 1, 1), k(0, 1, 1, 1, 1), ["x"]]) == ["green", "red", None, None]


def test_flip_when_forming_differs_from_last_closed():
    bars = [k(0, 1, 2, 1, 2), k(MIN, 2, 2, 1, 1.5)]  # last closed green, forming red
    r = _run("P.flip(j.b,j.now)", {"b": bars, "now": MIN + 3 * MIN})
    assert r == {"flipped": True, "ageMs": 3 * MIN}
    same = [k(0, 1, 2, 1, 2), k(MIN, 2, 3, 2, 3)]
    assert _run("P.flip(j.b,j.now)", {"b": same, "now": MIN})["flipped"] is False
    assert _run("P.flip(j,0)", [k(0, 1, 2, 1, 2)]) is None  # one bar: no comparison


def test_cvd_sign_from_taker_buy_volume():
    # volume 10: buy 7 -> sell 3 -> delta +4 up; buy 3 -> -4 down; buy 5 -> 0 no arrow; buy above volume = unreadable
    out = _run("j.map(x=>P.cvd(x))", [k(0, 1, 1, 1, 1, 10, 7), k(0, 1, 1, 1, 1, 10, 3), k(0, 1, 1, 1, 1, 10, 5), k(0, 1, 1, 1, 1, 10, 11)])
    assert out[0] == {"delta": 4, "dir": "up"}
    assert out[1] == {"delta": -4, "dir": "down"}
    assert out[2]["dir"] is None
    assert out[3] is None


def test_bb_above_upper_with_forming_bar():
    # 19 closes of 100 then 120: mean 101, var (19*1+19^2)/20 = 19, sd 4.3589, band 92.282..109.718, raw = 100*(120-92.282)/17.436 = 158.97
    r = _run("P.bbPos(j)", [100] * 19 + [120])
    assert r["label"] == "above upper" and r["pos"] == 100
    assert r["raw"] == pytest.approx(158.97, abs=0.05)


def test_bb_mid_and_below_lower():
    # 10x98 and 10x102 ending 102: mean 100, sd 2, band 96..104, raw = 75 -> mid; ending 98 -> 25 -> mid
    assert _run("P.bbPos(j)", [98] * 10 + [102] * 10)["raw"] == pytest.approx(75)
    assert _run("P.bbPos(j)", [98] * 10 + [102] * 10)["label"] == "mid"
    # 19 closes of 100 then 80: mean 99, var (19*1+19^2)/20 = 19, sd 4.3589, lower 90.282, 80 is below it
    r = _run("P.bbPos(j)", [100] * 19 + [80])
    assert r["label"] == "below lower" and r["pos"] == 0


def test_bb_needs_20_closes_and_a_band():
    assert _run("P.bbPos(j)", [100] * 19) is None
    assert _run("P.bbPos(j)", [100] * 20) is None  # zero width: no position


def test_value_area_hand_computed():
    # one bar per volume, h=l=c=price. Bins (50): 100:10, 150:30, 200:40, 250:15, 300:5; total 100
    # POC 200 (40). 70 % = 70: next larger neighbour 150 (30 vs 15) -> 70 reached. VAL 150, VAH 250 (top edge of bin 200), POC 200
    bars = [k(i * MIN, p, p, p, p, v) for i, (p, v) in enumerate([(120, 10), (170, 30), (210, 40), (260, 15), (310, 5)])]
    assert _run("P.valueArea(j,50,0.7)", bars) == {"val": 150, "vah": 250, "poc": 200}
    assert _run("P.valueArea(j,50,0.7)", []) is None


def _prior_and_today():
    prior = [k(D0 - 1440 * MIN + i * MIN, 100, 110, 90, 100, 1) for i in range(1440)]
    today = [k(D0, 100, 102, 98, 100, 2), k(D0 + 9 * 3600000, 100, 120, 96, 108, 1)]
    return prior + today


def test_levels_ladder_hand_computed():
    now = D0 + 10 * 3600000
    lv = _run("P.levels(j.b,j.now,j.px)", {"b": _prior_and_today(), "now": now, "px": 104})
    by = {x["name"]: x for x in lv}
    # prior day: H 110, L 90, C 100; every bar hlc3 = 100 -> POC 100, VAL 100, VAH 150
    assert (by["Prior day high"]["price"], by["Prior day low"]["price"], by["Prior day close"]["price"]) == (110, 90, 100)
    assert (by["Prior VAH"]["price"], by["Prior VAL"]["price"], by["Prior POC"]["price"]) == (150, 100, 100)
    # Asia 00-08Z: only the 00:00 bar (102/98); London 08-13Z: the 09:00 bar (120/96)
    assert (by["Asia high"]["price"], by["Asia low"]["price"]) == (102, 98)
    assert (by["London high"]["price"], by["London low"]["price"]) == (120, 96)
    # VWAP: (2*100 + 1*(120+96+108)/3) / 3 = (200+108)/3 = 102.667
    assert by["Day VWAP"]["price"] == pytest.approx(102.6667, abs=1e-3)
    assert by["Prior day high"]["dist"] == 6 and by["Prior day high"]["side"] == "above"
    assert by["Prior day low"]["dist"] == -14 and by["Prior day low"]["side"] == "below"
    d = [abs(x["dist"]) for x in lv]
    assert d == sorted(d) and lv[0]["name"] == "Day VWAP"  # nearest first


def test_levels_fail_closed_on_missing_data():
    now = D0 + 10 * 3600000
    holey = _prior_and_today()[1300:]  # prior day has holes: no prior-day levels
    names = [x["name"] for x in _run("P.levels(j.b,j.now,j.px)", {"b": holey, "now": now, "px": 104})]
    assert not any(n.startswith("Prior") for n in names) and "Day VWAP" in names
    assert _run("P.levels(j.b,j.now,j.px)", {"b": _prior_and_today(), "now": now, "px": None}) == []
    assert _run("P.levels(j.b,j.now,j.px)", {"b": [], "now": now, "px": 104}) == []


def _row(colour):
    return {"colour": colour}


def test_alignment_text_counter_trend():
    rows = {t: _row("green") for t in ["1m", "3m", "5m", "15m"]}
    rows.update({"1h": _row("green"), "2h": _row("green"), "4h": _row("red"), "6h": _row("red"), "12h": _row("red")})
    assert _run("P.alignment(j)", rows) == "Scalp 4/4 green · Context 2/5 green: counter-trend scalp"


def test_alignment_text_with_trend_mixed_and_missing():
    g = {t: _row("green") for t in ["1m", "3m", "5m", "15m", "1h", "2h", "4h", "6h", "12h"]}
    assert _run("P.alignment(j)", g).endswith("scalp with the trend")
    m = dict(g)
    m.update({"1m": _row("red"), "3m": _row("red")})  # 2 of 4 green = no side
    assert _run("P.alignment(j)", m) == "Scalp 2/4 green · Context 5/5 green: mixed, no clear side"
    half = {t: _row("red") for t in ["1m", "3m", "5m", "15m"]}  # context all missing
    assert _run("P.alignment(j)", half) == "Scalp 0/4 green · Context —: not enough data"


def test_row_and_time_left_fail_closed():
    bars = [k(i * 5 * MIN, 100, 101, 99, 100 + (i % 2), 10, 7, 5 * MIN) for i in range(25)]
    now = bars[-1][0] + 2 * MIN
    r = _run("P.row(j.b,j.now)", {"b": bars, "now": now})
    assert r["leftMs"] == 3 * MIN + 1 - 1  # close at open+5m-1 -> +1 = open+5m; 3 minutes left
    assert r["cvd"]["dir"] == "up" and len(r["last3"]) == 3 and r["bb"] is not None
    # forming bar already 1 minute past its close: the feed is stale, no row
    assert _run("P.row(j.b,j.now)", {"b": bars, "now": bars[-1][0] + 6 * MIN}) is None
    assert _run("P.row(j,0)", [k(0, 1, 2, 1, 2)]) is None


def test_format_time_left_and_ago():
    assert _run("[P.fmtLeft(j[0]),P.fmtLeft(j[1]),P.fmtLeft(j[2]),P.fmtLeft(null),P.fmtAgo(j[3]),P.fmtAgo(j[4])]",
                [125_000, 3_900_000, 90_000_000, 300_000, 7_500_000]) == ["2m 05s", "1h 5m", "1d 1h", "—", "5m", "2h"]


def test_close_colour_gauge():
    # P(keeps colour) = Phi(|d_sd| / sqrt(t_left)), d_sd = d_atr * 1.5958 (sigma_bar = ATR / (2 sqrt(2/pi))). Standard normal table, not the code.
    K = 1.5957691
    out = _run("[P.pCloseColour('1h',0,0.5,null),P.pCloseColour('4h',1/j[0],1,null),P.pCloseColour('15m',-0.5/j[0],0.25,null),"
               "P.pCloseColour('1h',0,0.5,{delta:0.02}),P.pCloseColour('1h',5,0.01,{delta:0.5}),P.pCloseColour('1h',0.3,0,null)]", [K])
    assert out[0] == pytest.approx(0.5, abs=1e-9)            # d = 0: 0.5 whatever the time left
    assert out[1] == pytest.approx(0.841345, abs=1e-5)       # d = 1 sd, t = 1: Phi(1)
    assert out[2] == pytest.approx(0.841345, abs=1e-5)       # d = -0.5 sd, t = 0.25: |d|/sqrt(t) = 1, the sign is the colour not the odds
    assert out[3] == pytest.approx(0.52, abs=1e-9)           # cell shift added
    assert out[4] == pytest.approx(0.999, abs=1e-9)          # clipped
    assert out[5] == 1.0                                     # bar over: colour final
    bad = _run("[P.pCloseColour('1h',NaN,0.5,null),P.pCloseColour('1h',0.3,1.5,null),P.pCloseColour('7x',0.3,0.5,null),P.pCloseColour('1h',0.3,-0.1,null)]".replace("NaN", "j[0]"), [None])
    assert bad == [None, None, None, None]                   # unreadable input fails closed

    # strip row: 24 closed 5m bars, every TR = 2 (H 101, L 99, C 100) -> ATR14 = 2; forming bar opens 100
    def bars(price):
        b = [k(i * 5 * MIN, 100, 101, 99, 100, 10, 5, 5 * MIN) for i in range(24)]
        b.append(k(24 * 5 * MIN, 100, 102, 98, price, 10, 5, 5 * MIN))
        return b
    t0 = 24 * 5 * MIN
    # price 101.25 after 2.5 of 5 minutes: d_atr = 1.25/2 = 0.625, t_left = 0.5 -> Phi(0.625*1.5958/sqrt(0.5)) = Phi(1.4105) = 0.92080
    g = _run("P.row(j.b,j.now).keep", {"b": bars(101.25), "now": t0 + 150_000})
    assert g["p"] == pytest.approx(0.92080, abs=1e-4) and g["colour"] == "green"
    assert g["dAtr"] == pytest.approx(0.625) and g["tLeft"] == pytest.approx(0.5, abs=1e-4)
    # price 98.75: same distance below the open -> same probability, red; 0.5 min of 5 left, d_atr 0.125 -> Phi(0.125*1.5958/sqrt(0.1)) = Phi(0.6308) = 0.73591
    assert _run("P.row(j.b,j.now).keep", {"b": bars(98.75), "now": t0 + 150_000})["colour"] == "red"
    g2 = _run("P.row(j.b,j.now).keep", {"b": bars(100.25), "now": t0 + 270_000})
    assert g2["p"] == pytest.approx(0.73591, abs=1e-4) and g2["colour"] == "green"
    # 15 bars (needs 16: ATR14 plus the forming bar): no gauge, the row itself still reads
    short = bars(101.25)[10:]
    r = _run("P.row(j.b,j.now)", {"b": short, "now": t0 + 150_000})
    assert r is not None and r["keep"] is None
