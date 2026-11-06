"""MA strip contract (ma_strip.js). Expected numbers are hand-computed in the comments, not taken from the code.
Parity: the JS row must equal the Python twin research/ma_layer_2026-11/ma_state.py on the same bars."""
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JS = HERE / "ma_strip.js"
sys.path.insert(0, str(HERE.parent.parent / "research" / "ma_layer_2026-11"))
import ma_state as PY  # noqa: E402


def _run(expr, payload):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    assert JS.exists(), "ma_strip.js missing"
    runner = ("const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(" + expr + "))})")
    out = subprocess.run([node, "-e", runner, str(JS)], input=json.dumps(payload),
                         capture_output=True, text=True, encoding="utf-8", timeout=30, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def k(i, o, h, l, c):
    return [i * 60000, str(o), str(h), str(l), str(c), "1", i * 60000 + 59999, "0", 1, "0.5", "0", "0"]


def flat_then_jump():
    return [k(i, 100, 101, 99, 100) for i in range(299)] + [k(299, 100, 111, 99, 110)]


def ramp(final):
    return [k(i, c, c + 1, c - 1, c) for i, c in enumerate(range(1, 300))] + [k(299, *final)]


def test_jump_row_hand_numbers():
    # 299 closes of 100 then 110: ema21 = 100 + 10*2/22 = 100.90909, sma200 = (199*100+110)/200 = 100.05, ATR14 = 2
    r = _run("P.row('1h',j)", flat_then_jump())
    a = r["avgs"]
    assert a["ema21"]["v"] == pytest.approx(100.909091, abs=1e-5)
    assert a["ema55"]["v"] == pytest.approx(100.357143, abs=1e-5)
    assert a["sma200"]["v"] == pytest.approx(100.05)
    assert a["ema200"]["v"] == pytest.approx(100.099502, abs=1e-5)
    assert r["atr"] == pytest.approx(2.0)
    assert a["ema21"]["distAtr"] == pytest.approx(4.545455, abs=1e-5)   # (110-100.90909)/2
    assert a["sma200"]["ratio"] == pytest.approx(1.099450, abs=1e-6)    # 110/100.05
    assert r["band"] == "above" and r["pullback"] is None


def test_pullback_ramp_and_not():
    # ramp closes 1..299, forming o299 h300 l283 c285: ema21 288.636, low 283 touches, close above ema55 272.46 -> up
    assert _run("P.row('15m',j).pullback", ramp((299, 300, 283, 285))) == "up"
    assert _run("P.row('15m',j).pullback", ramp((299, 301, 298, 300))) is None  # low 298 stays above ema21 290 + 0.5
    assert _run("P.row('15m',j).pullback", ramp((299, 300, 250, 260))) is None  # close 260 through ema55 271.6


def test_cross_state_hand_series():
    # same hand series as the Python spec: 1,2,3,2,1 vs 2 -> down, 0 bars since; 1,3,3,3 vs 2 -> up, 2 bars since
    assert _run("P.crossState(j[0],j[1])", [[1, 2, 3, 2, 1], [2] * 5]) == {"state": "down", "barsSince": 0}
    assert _run("P.crossState(j[0],j[1])", [[1, 3, 3, 3], [2] * 4]) == {"state": "up", "barsSince": 2}
    assert _run("P.crossState(j[0],j[1])", [[None, 3], [None, 1]]) == {"state": "up", "barsSince": None}


def test_series_hand_numbers_and_fail_closed():
    # closes 1..200: sma200 100.5; [10,10,10,20] ema3 = 15 (alpha 0.5)
    assert _run("P.smaSeries(j,200).pop()", [float(x) for x in range(1, 201)]) == pytest.approx(100.5)
    assert _run("P.emaSeries(j,3)", [10, 10, 10, 20]) == [None, None, 10, 15]
    short = [k(i, 100, 101, 99, 100) for i in range(60)]
    r = _run("P.row('1M',j)", short)
    assert r["avgs"]["sma200"] is None and r["avgs"]["ema55"] is not None
    assert _run("P.row('1d',j)", short[:1]) is None
    assert _run("P.rows({'1h':j})", flat_then_jump())[2]["tf"] == "1h"


def test_view_symbols_for_the_jump_row():
    # price 110 above all four lines: arrows up, 21 EMA distance 100*(110-100.90909)/100.90909 = +9.0%, bar = 50 + 50*min(4.545/6,1) = 87.88
    v = _run("P.view(P.row('1h',j))", flat_then_jump())
    assert [c["sym"] for c in v["cells"]] == ["▲", "▲", "▲", "▲"]
    assert v["cells"][0]["pct"] == "+9.0%"
    assert v["bar"]["pos"] == pytest.approx(50 + 50 * 4.545455 / 6, abs=1e-3)
    assert v["pullback"] is None and v["cross"] == {"dir": "up", "barsSince": None, "fresh": False, "text": "21>55"}
    assert v["gd"] == {"dir": "up", "text": "golden"}
    # pullback row reads "pullback to 21"; a missing row has no view
    assert _run("P.view(P.row('1h',j)).pullback", ramp((299, 300, 283, 285))) == {"dir": "up", "text": "pullback to 21"}
    assert _run("P.view(null)", []) is None


def test_bar_is_capped_at_six_atr():
    # one-bar jump of 110 vs ema ~100.9 is 4.5 ATR; a 130 close is (130-101.8)/2 = 14 ATR -> capped, pos 100
    bars = [k(i, 100, 101, 99, 100) for i in range(299)] + [k(299, 100, 131, 99, 130)]
    assert _run("P.view(P.row('5m',j)).bar.pos", bars) == pytest.approx(100)


def _close(a, b, path=""):
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), path
        for key in a:
            _close(a[key], b[key], path + "." + key)
    elif isinstance(a, float) or isinstance(b, float):
        assert a is not None and b is not None and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9), (path, a, b)
    else:
        assert a == b, (path, a, b)


@pytest.mark.parametrize("name", ["jump", "ramp_pullback", "wave", "short"])
def test_js_equals_python_twin(name):
    if name == "jump":
        bars = flat_then_jump()
    elif name == "ramp_pullback":
        bars = ramp((299, 300, 283, 285))
    elif name == "short":
        bars = [k(i, 100 + i % 3, 102 + i % 3, 98, 100 + i % 3) for i in range(70)]
    else:  # deterministic wave with crosses of 21/55 and 50/200
        bars = []
        for i in range(500):
            c = round(100 + 30 * math.sin(i / 23.0) + 12 * math.sin(i / 7.0) + i * 0.05, 4)
            bars.append(k(i, c - 0.5, c + 1.5, c - 1.5, c))
    js_row = _run("P.row('1h',j)", bars)
    py_row = json.loads(json.dumps(PY.ma_row("1h", bars)))
    _close(js_row, py_row)
    if name == "wave":
        assert js_row["cross2155"]["barsSince"] is not None  # the wave really crosses, so parity is not on a trivial row
