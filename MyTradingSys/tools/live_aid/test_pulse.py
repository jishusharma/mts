"""Live Aid pulse grid (pulse.js, operator 2026-11-09 17Z): RSI, WaveTrend and Binance spot CVD per timeframe 1m..4h, their
divergences with price, a weighted lean, and the "setup forming" flag at a named level. Pure rules run in node; expected numbers are
written by hand from the synthetic bars below. Skips (never fails) without node.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PULSE = HERE / "pulse.js"


def _node(fn, *args):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = "const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(P[j.fn].apply(null,j.a)))})"
    out = subprocess.run([node, "-e", runner, str(PULSE)], input=json.dumps({"fn": fn, "a": list(args)}), capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert out.returncode == 0, out.stderr[-1500:]
    return json.loads(out.stdout)


T0 = 1_794_182_400_000   # 2026-11-09 00:00Z


def kl(t, c, delta, vol=20.0):
    """Binance kline row: taker buy = (vol + delta) / 2, so 2*buy - vol = delta."""
    return [t, c, c + 0.5, c - 0.5, c, vol, t + 59_999, 0, 0, (vol + delta) / 2]


def bars_bearish_cvd():
    """60 x 1m. 0-29 flat 100, delta 0. 30-44 climb to 110, delta +10 each (cum 150 at bar 44).
    45-58 drift down 0.5 a bar, delta -5; bar 59 jumps to 111 (higher close), delta -5. Last 15 vs the 15 before:
    price max 111 > 110 while cum delta max 145 < 150 -> bearish CVD divergence (-1). CVD of the last 10 bars = -50 -> vote -1."""
    rows = []
    for i in range(60):
        if i < 30:
            c, d = 100.0, 0.0
        elif i < 45:
            c, d = 100 + (i - 29) * 10 / 15, 10.0
        elif i < 59:
            c, d = 110 - (i - 44) * 0.5, -5.0
        else:
            c, d = 111.0, -5.0
        rows.append(kl(T0 + i * 60_000, c, d))
    return rows


def test_fold_sums_volume_and_taker_buy():
    rows = [kl(T0 + i * 60_000, 100 + i, 2 * i) for i in range(4)]   # taker buy 10, 11, 12, 13
    f = _node("foldK", rows, 120_000)
    assert [r[0] for r in f] == [T0, T0 + 120_000]
    assert [r[5] for r in f] == [40, 40] and [r[9] for r in f] == [21, 25]
    assert f[0][1] == 100 and f[0][4] == 101 and f[0][2] == 101.5 and f[0][3] == 99.5


def test_bearish_cvd_divergence_and_votes():
    r = _node("read", bars_bearish_cvd(), 60_000)
    assert r["div"]["cvd"] == -1
    assert r["cvd"] == -50 and r["v"]["cvd"] == -1
    assert r["score"] == (r["v"]["rsi"] or 0) + (r["v"]["wt"] or 0) - 1 + 2 * r["dsum"]


def test_rsi_vote_uses_the_gauge_50_line():
    # operator 2026-11-10: 1h RSI 46 was grey in the grid (old 45-55 band) but red on the Direction gauge (RSI vs 50)
    # steps alternate +0.20 / -0.25: Wilder averages settle near gain 0.10, loss 0.125 -> RSI about 100 - 100/1.8 = 44.4 (under 50, over 45)
    c, rows = 100.0, []
    for i in range(60):
        c += 0.20 if i % 2 else -0.25
        rows.append(kl(T0 + i * 60_000, c, 0))
    r = _node("read", rows, 60_000)
    assert 45 < r["rsi"] < 50 and r["v"]["rsi"] == -1


def test_too_few_bars_is_no_read():
    assert _node("read", bars_bearish_cvd()[:39], 60_000) is None


def test_grid_lean_from_one_row():
    g = _node("grid", {"1m": bars_bearish_cvd()})
    assert [x["tf"] for x in g["rows"]] == ["1m", "2m", "3m", "5m", "7m", "10m", "15m", "30m", "1h", "2h", "4h"]
    one = g["rows"][0]["r"]
    assert g["n"] == 1 and g["rows"][1]["r"] is None          # 2m folds to 30 bars, under the 40-bar floor
    assert abs(g["lean"] - max(-7, min(7, one["score"])) / 7) < 1e-12
    assert g["hi"] is None                                    # no 1h-4h row: NaN serialises to null


LAD = {"at": None, "above": [{"price": 75000, "name": "Today high"}], "below": [{"price": 73750, "name": "Today low"}]}
G_DOWN = {"hi": -0.3, "rows": [{"tf": "5m", "r": {"div": {"rsi": 0, "wt": None, "cvd": -1}}}, {"tf": "1h", "r": {"div": {"rsi": -1, "wt": 0, "cvd": 0}}}]}


def test_short_setup_at_high_with_down_lean_and_divergence():
    s = _node("setup", G_DOWN, LAD, 74950, "WAIT")          # 0.067 % under the high
    assert s["side"] == "SHORT" and s["level"] == 75000 and s["divs"] == ["5m CVD"]   # 1h divergence is not a low timeframe
    assert s["why"][0] == "at Today high"


def test_no_setup_far_from_level_or_without_agreement():
    assert _node("setup", G_DOWN, LAD, 74800, "WAIT") is None                       # 0.27 % away
    up = dict(G_DOWN, hi=0.3)
    assert _node("setup", up, LAD, 74950, "WAIT") is None                           # big picture up
    assert _node("setup", up, LAD, 74950, "SHORT")["side"] == "SHORT"               # Home direction says down
    nodiv = {"hi": -0.3, "rows": [{"tf": "5m", "r": {"div": {"rsi": 0, "wt": 0, "cvd": 0}}}]}
    assert _node("setup", nodiv, LAD, 74950, "WAIT") is None


def test_short_setup_when_price_pokes_through_a_level():
    # 2026-11-09 15:46Z: US-session high 75,553 sat 0.14 % ABOVE the playbook "if up" 75,450, which the ladder lists below price
    lad = {"at": None, "above": [{"price": 76200, "name": "Weekly high"}], "below": [{"price": 75450, "name": "Playbook if up"}]}
    s = _node("setup", G_DOWN, lad, 75553, "WAIT")
    assert s["side"] == "SHORT" and s["level"] == 75450


def test_positions_subtitle_in_plain_words():
    # operator 2026-11-10: "15 min, 2 venues (Deribit, Bybit; Binance blocked here)" read as "versions"; the blocked note goes to the tooltip
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    js = ("const H=require(process.argv[1]);console.log(H._moneyCard({money:{label:'15 min',n:3,dp:0.001,doi:-0.002,text:'x',"
          "venues:[{name:'Bybit',btc:50,share:0.5},{name:'Hyperliquid',btc:30,share:0.3},{name:'Deribit',btc:20,share:0.2}],missing:['Binance: blocked']}}))")
    out = subprocess.run([node, "-e", js, str(HERE / "home.js")], capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert out.returncode == 0, out.stderr[-1500:]
    import re
    m = re.search(r'<span class="hm-sub" title="([^"]*)">([^<]*)</span>', out.stdout)
    assert m, out.stdout
    # operator 11-10: list only the venues that answered, biggest first, with their share; the missing ones go to the tooltip
    assert m.group(2) == "change over the last 15 min " + chr(183) + " from Bybit 50% + Hyperliquid 30% + Deribit 20%"
    assert "Binance: blocked" in m.group(1) and "Binance" not in m.group(2)


def _vee(n_down=100, n_up=5):
    """1m bars falling 0.5 a bar, the last 5 falls 1.5 a bar, then rising 0.5 a bar. A steady fall drives wt1 to its floor: esa trails
    price by slope*(1-a1)/a1 and dev equals that same gap, so ci = -1/0.015 = -66.7, under -53 (LazyBear oversold 2). The sharper last
    5 bars push the gap faster than dev, so wt1 dips under its 4-bar average (a cross needs a side to flip FROM; equal lines are no
    side). The first up bar only slows wt1 (-76.3, still under wt2 -75.5); the second lifts it over -> up cross 3 bars before the end, at
    wt1 -74, from oversold (numbers from the run, the sign and zone from the reasoning above)."""
    c, rows = 200.0, []
    for i in range(n_down + n_up):
        c += (-1.5 if i >= n_down - 5 else -0.5) if i < n_down else 0.5
        rows.append(kl(T0 + i * 60_000, c, 1 if i >= n_down else -1))
    return rows


def test_wavetrend_lane_cross_from_oversold():
    # operator 2026-11-10: WaveTrend crosses on 1m/2m/3m time the move; 15m/30m the frame; 4h context
    L = _node("lane", {"1m": _vee()}, "1m", 60)
    assert len(L["bars"]) == 60 and L["tf"] == "1m"
    assert L["last"]["side"] == 1 and L["last"]["ago"] == 3 and L["last"]["strong"] is True
    assert L["last"]["wt1"] < -53
    # the sharp leg first flips wt1 under wt2 (a down cross deep in oversold: NOT strong, strong = a turn back out of the zone), then the up cross
    xs = [(b["x"], b["strong"]) for b in L["bars"] if b["x"]]
    assert xs == [(-1, False), (1, True)], xs
    assert L["bars"][-1]["delta"] == 1
    assert _node("laneWords", L).startswith("▲ crossed up 3 bars ago from oversold")


def test_wavetrend_lane_folds_2m_and_no_data():
    L = _node("lane", {"1m": _vee(200, 10)}, "2m", 60)
    assert L["ms"] == 120_000 and len(L["bars"]) == 60 and L["bars"][1]["t"] - L["bars"][0]["t"] == 120_000
    assert _node("lane", {"1m": _vee()[:30]}, "1m", 60) is None
    assert _node("laneWords", None) == "not enough candles yet"


def test_long_setup_at_low():
    g = {"hi": 0.4, "rows": [{"tf": "7m", "r": {"div": {"rsi": 1, "wt": 1, "cvd": 0}}}]}
    s = _node("setup", g, LAD, 73800, "WAIT")
    assert s["side"] == "LONG" and s["divs"] == ["7m RSI", "7m WaveTrend"]
