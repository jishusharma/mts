"""ADX / DI strip contract (adx_strip.js, adx_now.py; R26). Hand-computed numbers are in the comments.
Parity: adxSeries must equal backtest/layers/adx/adx.py on the same bars to 0.1; the Python twin adx_now.py must agree on rowState."""
import json
import math
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JS = HERE / "adx_strip.js"
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest" / "layers" / "adx"))
sys.path.insert(0, str(HERE))
import adx as PY  # noqa: E402
import adx_now as NOW  # noqa: E402

DAY = 86400000
NO_WIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _run(expr, payload):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    assert JS.exists(), "adx_strip.js missing"
    runner = ("const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(" + expr + "))})")
    out = subprocess.run([node, "-e", runner, str(JS)], input=json.dumps(payload), capture_output=True, text=True,
                         encoding="utf-8", timeout=30, env=os.environ.copy(), creationflags=NO_WIN)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def k(t, o, h, l, c, v=1.0, close=None):
    return [t, str(o), str(h), str(l), str(c), str(v), t + DAY - 1 if close is None else close]


def walk(n, seed=7):
    rnd = random.Random(seed)
    c, out = 100.0, []
    for i in range(n):
        o = c
        c = max(1.0, c + rnd.uniform(-3, 3.4))
        out.append(k(i * DAY, round(o, 4), round(max(o, c) + rnd.uniform(0, 2), 4), round(min(o, c) - rnd.uniform(0, 2), 4), round(c, 4)))
    return out


def test_adx_series_equals_python_layer():
    bars = walk(300)
    js = _run("P.adxSeries(j, 14)", bars)
    dip, dim, adx = PY.adx_di([float(b[2]) for b in bars], [float(b[3]) for b in bars], [float(b[4]) for b in bars], 14)
    assert len(js["adx"]) == 300
    defined = 0
    for i in range(300):
        for name, ref in (("dip", dip), ("dim", dim), ("adx", adx)):
            if ref[i] is None:
                assert js[name][i] is None, (name, i)
            else:
                defined += 1
                assert js[name][i] == pytest.approx(ref[i], abs=0.1), (name, i)
    assert js["adx"][26] is None and js["adx"][27] is not None   # first DX at bar 14, the 14th DX at bar 27 = first ADX
    assert defined > 800


def test_adx_series_hand_numbers_straight_up():
    # bars rise by 1 each step with high=c+1,low=c-1: TR=2 (high-low), +DM=1, -DM=0 -> +DI = 50, -DI = 0, DX = 100, ADX = 100
    bars = [k(i * DAY, i, i + 1, i - 1, i) for i in range(1, 40)]
    s = _run("P.adxSeries(j, 14)", bars)
    assert s["dip"][20] == pytest.approx(50.0) and s["dim"][20] == pytest.approx(0.0) and s["adx"][30] == pytest.approx(100.0)


def test_adx_series_short_or_bad_input_is_null():
    assert _run("P.adxSeries(j, 14).adx.every(x => x === null)", walk(14)) is True
    bad = walk(60)
    bad[30][3] = "nan"
    assert _run("P.adxSeries(j, 14).adx.every(x => x === null)", bad) is True


def test_fold_buckets_and_sums():
    # epoch days 0..11 (1970-01-01 anchor): 5d buckets start at days 0 and 5 and 10; days 0..11 -> last bucket (10, 11) partial
    d = [k(i * DAY, 10 + i, 20 + i, 5 + i, 11 + i, 2.0) for i in range(12)]
    f = _run("P.fold(j, 5)", d)
    assert [r[0] for r in f] == [0, 5 * DAY, 10 * DAY]
    assert f[0][1:5] == [10, 24, 5, 15] or [float(x) for x in f[0][1:5]] == [10, 24, 5, 15]   # o first, high max(20..24)=24, low 5, close of day 4 = 15
    assert f[0][5] == 10.0 and f[2][5] == 4.0                      # volume sums 5 and 2 days
    assert f[2][6] == 15 * DAY - 1                                   # partial bucket keeps its full end time (reads as forming)
    # first bucket starting before the data is dropped: data begins on day 3 of a 5d bucket
    g = _run("P.fold(j, 5)", d[3:])
    assert g[0][0] == 5 * DAY
    # 2d and 3d on the same days
    assert [r[0] for r in _run("P.fold(j, 2)", d)] == [i * 2 * DAY for i in range(6)]
    assert [r[0] for r in _run("P.fold(j, 3)", d)] == [0, 3 * DAY, 6 * DAY, 9 * DAY]


def test_fold_matches_python_twin_and_tf_resample_anchor():
    d = walk(100)
    for n in (2, 3, 5):
        js = _run("P.fold(j, %d)" % n, d)
        py = NOW.fold(d, n)
        assert len(js) == len(py)
        for a, b in zip(js, py):
            assert [float(x) for x in a] == pytest.approx([float(x) for x in b])
    sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest" / "layers" / "timeframe"))
    import tf_resample as TR
    reg = json.loads((ROOT / "MyTradingSys" / "backtest" / "layers" / "timeframe" / "registry.json").read_text(encoding="utf-8"))
    for n in (2, 3, 5):
        # the folded bucket start equals the registry bucket start for every bar that opens a bucket
        starts = [x for x in d if (x[0] // DAY) % n == 0]
        assert starts
        folded = {r[0] for r in NOW.fold(d, n)}
        for src in starts:
            assert src[0] == TR.bucket_start(src[0], "%dd" % n, reg) and src[0] in folded


def series(adx, dip=None, dim=None):
    dip = dip or [20.0] * len(adx)
    dim = dim or [10.0] * len(adx)
    return {"adx": adx, "dip": dip, "dim": dim}


@pytest.mark.parametrize("last,prev3,chip", [
    (19.9, 15.0, "NO TREND"), (20.0, 19.0, "BUILDING"), (24.9, 24.0, "BUILDING"), (24.9, 26.0, "WEAK"), (24.9, 24.9, "WEAK"),
    (25.0, 24.0, "TREND"), (39.9, 45.0, "TREND"), (40.0, 41.0, "STRETCHED"), (45.0, 44.0, "TREND"), (55.0, 60.0, "STRETCHED"),
])
def test_row_state_chips_at_edges(last, prev3, chip):
    adx = [prev3, prev3, prev3, last]   # index L-3 holds prev3, so the arrow compares last with prev3
    r = _run("P.rowState(j)", series(adx))
    assert r["chip"] == chip, r


def test_row_state_arrow_through_and_cross():
    # ADX 22,23,24,25.5: crossed up through 25 on the last bar (24 < 25 <= 25.5) -> through25; arrow up vs 3 bars ago (22)
    r = _run("P.rowState(j)", series([22, 23, 24, 25.5]))
    assert r["arrow"] == "up" and r["through25"] is True and r["chip"] == "TREND"
    # crossed 4 bars before the end: outside the 3-bar window
    r = _run("P.rowState(j)", series([22, 25.5, 26, 27, 28]))
    assert r["through25"] is False
    # inside the window two bars before the end
    r = _run("P.rowState(j)", series([22, 24, 25.5, 26, 27]))
    assert r["through25"] is True
    # DI cross: +DI above -DI until bar 2, then -DI above: red cross at bar 3 = 2 bars before the last of a 6-bar series
    dip = [20, 20, 20, 15, 15, 15]
    dim = [10, 10, 10, 18, 18, 18]
    r = _run("P.rowState(j)", series([30] * 6, dip, dim))
    assert r["diCross"] == {"dir": "red", "barsAgo": 2} and r["winner"] == "minus" and r["lead"] == pytest.approx(3.0)
    # a cross 11 bars ago is not shown
    n = 14
    dip = [20] * 2 + [10] * (n - 2)
    dim = [10] * 2 + [15] * (n - 2)
    r = _run("P.rowState(j)", series([30] * n, dip, dim))
    assert r["diCross"] is None
    # undefined ADX at the last bar = no row (dash)
    assert _run("P.rowState(j)", series([22, 23, 24, None])) is None


def test_row_forming_bar_and_closed_split():
    bars = walk(80)
    now = bars[-1][0] + 5 * 3600000            # last daily bar is 5 h into its day: forming
    bars[-1][6] = bars[-1][0] + DAY - 1
    r = _run("P.row('1d', j.bars, j.now)", {"bars": bars, "now": now})
    assert r["forming"] is not None and r["bars"] == 79
    closed_only = _run("P.rowState(P.adxSeries(j.slice(0, 79), 14))", bars)
    assert r["adx"] == pytest.approx(closed_only["adx"])
    r2 = _run("P.row('1d', j.bars, j.now)", {"bars": bars, "now": bars[-1][0] + DAY + 1})   # now past the close: nothing forming
    assert r2["forming"] is None and r2["bars"] == 80


def test_python_twin_row_state_agrees_with_js():
    bars = walk(200, seed=11)
    now = bars[-1][0] + DAY + 1
    js = _run("P.row('1d', j.bars, j.now)", {"bars": bars, "now": now})
    py = NOW.row(bars, now)
    for key in ("adx", "dip", "dim", "lead"):
        assert js[key] == pytest.approx(py[key], abs=0.1)
    assert js["chip"] == py["chip"] and js["arrow"] == py["arrow"] and js["through25"] == py["through25"]
    assert js["diCross"] == py["diCross"]


def test_view_row_symbols_and_missing_is_dash():
    bars = walk(120, seed=3)
    html = _run("P.viewRow('2d', P.row('2d', j.bars, j.now), null)", {"bars": bars, "now": bars[-1][0] + DAY + 1})
    assert "<td class=\"tfn\">2d</td>" in html and "adxb" in html and "regime read, thin data" in html
    dash = _run("P.viewRow('5m', null, 'HTTP 451')", [])
    assert "—" in dash and "HTTP 451" in dash and "do not use" in dash


def test_layout_panel_script_and_artifact_tag():
    html = (HERE / "live_aid.html").read_text(encoding="utf-8")
    assert 'id="p-adxs"' in html and '<script src="adx_strip.js"></script>' in html
    assert html.index('id="p-mas"') < html.index('id="p-adxs"') < html.index("</section>", html.index('id="p-adxs"'))
    # directly under the Moving averages panel: nothing but the comment between the two blocks
    between = html[html.index('id="mas-err"'):html.index('id="p-adxs"')]
    assert between.count("<section") == 0 and between.count("<h2>") == 0
    assert '<script src="adx_strip.js"></script>' in (HERE / "build_artifact.py").read_text(encoding="utf-8")
    assert JS.exists()


def test_fold_dates_cover_all_rows():
    assert [r for r in ("1w", "5d", "3d", "2d", "1d", "4h", "1h", "15m", "5m")] == NOW.TFS
    assert set(NOW.USE) == set(NOW.TFS) and all(len(v.split()) <= 6 for v in NOW.USE.values())
