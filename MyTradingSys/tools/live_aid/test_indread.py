"""Live Aid indicator read (indread.js, operator 2026-11-10): Volume Flow, Squeeze Momentum and ADX/DI in the page, plus the plain
sentences on Home. Expected numbers are the hand toys of backtest/layers/FORMULAS.md sections 30.2, 31.2 and 32.2 (written there
by hand, not taken from this code). Skips (never fails) without node.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
IND = HERE / "indread.js"


def _node(fn, *args):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = ("const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);"
              "console.log(JSON.stringify(P[j.fn].apply(null,j.a),(k,v)=>typeof v==='number'&&!isFinite(v)?null:v))})")
    out = subprocess.run([node, "-e", runner, str(IND)], input=json.dumps({"fn": fn, "a": list(args)}), capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert out.returncode == 0, out.stderr[-1500:]
    return json.loads(out.stdout)


def test_adx_matches_the_formulas_toy():
    # FORMULAS 30.2, n = 3
    h = [10, 11, 12, 11, 13, 14, 13, 12, 11, 12, 13, 15, 14, 13, 12, 11, 12, 14, 15, 14]
    l = [8, 9, 10, 9, 10, 12, 11, 10, 9, 10, 11, 12, 12, 11, 10, 9, 10, 11, 13, 12]
    c = [9, 10, 11, 10, 12, 13, 12, 11, 10, 11, 12, 14, 13, 12, 11, 10, 11, 13, 14, 13]
    r = _node("adx", h, l, c, 3)
    assert r["pdi"][2] is None and r["adx"][4] is None
    assert r["pdi"][3] == pytest.approx(33.333, abs=1e-3) and r["mdi"][3] == pytest.approx(16.667, abs=1e-3)
    assert r["pdi"][5] == pytest.approx(48.333, abs=1e-3) and r["mdi"][5] == pytest.approx(6.667, abs=1e-3)
    assert r["adx"][5] == pytest.approx(5800 / 99, abs=1e-9)
    assert r["adx"][6] == pytest.approx(435500 / 9207, abs=1e-9)
    assert r["adx"][19] == pytest.approx(34.938, abs=1e-3)


def test_squeeze_matches_the_formulas_toy():
    # FORMULAS 31.2: textbook band (2.0 * sd), n = 5
    c = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19] + [19.5] * 8 + [21, 23, 25, 26, 28, 30, 31]
    h = [x + 0.5 for x in c[:10]] + [19.75] * 8 + [21.5, 23.5, 25.5, 26.5, 28.5, 30.5, 31.5]
    l = [x - 0.5 for x in c[:10]] + [19.25] * 8 + [19.5, 21.5, 23.5, 25.5, 26.5, 28.5, 29.5]
    r = _node("squeeze", h, l, c, 5, 1.5, 2.0)
    assert [i for i in range(25) if r["on"][i]] == list(range(12, 18))
    assert [i for i in range(25) if r["off"][i]] == list(range(4, 12)) + list(range(19, 25))   # bar 18 is the tie: neither
    want = [2, 2, 1.8425, 1.3775, 0.785, 0.225, -0.125, -0.18, -0.1275, -0.0475, 0.5475, 1.6025, 2.815, 3.485, 3.885, 3.97, 3.6075]
    assert r["mom"][7] is None
    assert r["mom"][8:] == pytest.approx(want, abs=1e-9)


def test_vfi_matches_the_formulas_toy():
    # FORMULAS 32.2: stdev 2, length 3, smooth 2
    c = [100, 102, 101, 105, 105, 104, 110, 108, 108.25]
    v = [10, 20, 30, 20, 40, 10, 100, 30, 50]
    r = _node("vfi", [x + 1 for x in c], [x - 1 for x in c], c, v, 3, 0.2, 2.5, 2, 2)
    assert r["vfi"][:5] == [None] * 5
    assert r["vfi"][5:] == pytest.approx([1 / 3, 29 / 14, 11 / 30, 47 / 28], abs=1e-9)
    assert r["sm"][5] is None
    assert r["sm"][6:] == pytest.approx([101 / 84, 128 / 105, 859 / 840], abs=1e-9)


def _cells(vfi_rising, cvd, dpx, adx=30.0, side=-1, on=False, rel=-1, rel_vol=1.0):
    return {"dpx": dpx, "relVol": rel_vol, "cells": {
        "vfi": {"v": 1, "rising": vfi_rising}, "cvd": {"v": cvd},
        "adx": {"v": side if adx >= 20 else 0, "adx": adx, "side": side, "strong": adx >= 25},
        "sqz": {"v": -1, "on": on, "rel": rel}}}


def test_sentences_say_when_volume_does_not_back_the_move():
    # price fell, but flow is rising: the fall is not backed -> bounce risk (amber), then the 1h trend line
    s = _node("says", {"15m": _cells(1, -1, -0.004), "1h": _cells(-1, -1, -0.01)})
    assert s[0]["cls"] == "amber" and "fall is NOT backed by volume (flow rising): bounce risk" in s[0]["t"]
    assert s[1] == {"cls": "down", "t": "1h trend down, strong (ADX 30)"}
    # price fell with falling flow and sellers leading: backed; 3x volume is named
    s = _node("says", {"15m": _cells(-1, -1, -0.004, rel_vol=3.0), "1h": _cells(-1, -1, -0.01)})
    assert s[0]["cls"] == "down" and s[0]["t"] == "15m fall is backed by volume: flow falling, sellers lead; last bar 3.0x normal volume"
    # price rose while sellers lead the tape: not backed -> fade risk
    s = _node("says", {"15m": _cells(1, -1, 0.004), "1h": _cells(1, 1, 0.01, side=1)})
    assert s[0]["cls"] == "amber" and "rise is NOT backed by volume (sellers lead the tape): fade risk" in s[0]["t"]


def test_flat_price_is_not_called_a_rise_or_a_fall():
    # live 11-10: +0.03 % over 10 bars printed as "15m rise is NOT backed"; under 0.1 % is flat
    s = _node("says", {"15m": _cells(1, -1, 0.0003), "1h": _cells(-1, -1, -0.01)})
    assert s[0] == {"cls": "dim", "t": "15m price flat, volume mixed (flow rising, sellers lead the tape)"}
    s = _node("says", {"15m": _cells(-1, -1, -0.0003), "1h": _cells(-1, -1, -0.01)})
    assert s[0] == {"cls": "down", "t": "15m price flat while flow is falling and sellers lead: quiet selling"}


def test_sentences_name_no_trend_and_the_coil():
    s = _node("says", {"15m": _cells(-1, -1, -0.004, adx=14, on=True), "1h": _cells(-1, -1, -0.01, adx=17)})
    assert s[1] == {"cls": "dim", "t": "No trend on 15m or 1h (ADX 14 / 17): range, levels matter more than indicators"}
    assert s[2]["cls"] == "amber" and s[2]["t"].startswith("15m coiled (squeeze on)")
    s = _node("says", {"15m": _cells(-1, -1, -0.004, rel=1), "1h": _cells(-1, -1, -0.01)})
    assert s[2]["t"] == "Squeeze just released: 15m down"


def test_read_drops_the_forming_bar_and_needs_history():
    t0, ms = 1_794_182_400_000, 900_000
    rows = [[t0 + i * ms, 100, 101 + (i % 7), 99 - (i % 5), 100 + (i % 9) - 4, 20 + (i % 3), t0 + (i + 1) * ms - 1, 0, 0, 10 + (i % 4)] for i in range(300)]
    assert _node("read", rows[:59], ms, t0 + 300 * ms) is None
    full = _node("read", rows, ms, t0 + 300 * ms)                 # all 300 closed
    part = _node("read", rows, ms, t0 + 300 * ms - 5)             # the last bar is still forming: dropped
    assert full["t"] == rows[299][0] and part["t"] == rows[298][0]
    assert full["cells"]["vfi"]["v"] is not None and full["n"] == 6
    short = _node("read", rows[:200], ms, t0 + 300 * ms)          # under 263 bars: VFI says so, the rest still read
    assert short["cells"]["vfi"] == {"v": None, "txt": "needs 263 bars"} and short["n"] == 5
