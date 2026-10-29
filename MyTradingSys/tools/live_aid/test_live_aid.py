"""Tests for live_aid_indicators.js: independent Python maths vs the JS (run through node).

Data: 300 Binance fapi BTCUSDT 1m klines (live, 20 s timeout) or the committed public fixture.
Set LIVE_AID_BREAK=<rsi|rsiSma|bb|atr|vwap|days|wt|pnl> to run the JS with that function deliberately
broken (fail-first demo): the matching test must then fail.
"""
import json
import math
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JS = HERE / "live_aid_indicators.js"
FIXTURE = HERE / "fixture_klines.json"
TOL = 1e-6
URL = "https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1m&limit=300"


def load_klines():
    if os.environ.get("CI"):  # CI runners: deterministic fixture, no network
        return json.loads(FIXTURE.read_text())["klines"], "fixture"
    try:
        with urllib.request.urlopen(URL, timeout=20) as r:
            rows = json.load(r)
        if len(rows) >= 150:
            return rows, "live"
    except Exception:
        pass
    return json.loads(FIXTURE.read_text())["klines"], "fixture"


ROWS, SOURCE = load_klines()
T = [int(r[0]) for r in ROWS]
H = [float(r[2]) for r in ROWS]
L = [float(r[3]) for r in ROWS]
C = [float(r[4]) for r in ROWS]
V = [float(r[5]) for r in ROWS]


# ---------- independent Python maths ----------
def py_rma(x, n):
    out, prev, seen = [], None, []
    for v in x:
        if v is None:
            out.append(None)
            continue
        if prev is None:
            seen.append(v)
            if len(seen) == n:
                prev = sum(seen) / n
                out.append(prev)
            else:
                out.append(None)
        else:
            prev = (prev * (n - 1) + v) / n
            out.append(prev)
    return out


def py_rsi(c, n=14):
    gains = [None] + [max(c[i] - c[i - 1], 0.0) for i in range(1, len(c))]
    losses = [None] + [max(c[i - 1] - c[i], 0.0) for i in range(1, len(c))]
    ag, al = py_rma(gains, n), py_rma(losses, n)
    out = []
    for a, b in zip(ag, al):
        if a is None:
            out.append(None)
        elif b == 0:
            out.append(50.0 if a == 0 else 100.0)
        else:
            out.append(100 - 100 / (1 + a / b))
    return out


def py_sma(x, n):
    out = []
    for i in range(len(x)):
        w = x[max(0, i - n + 1): i + 1]
        out.append(sum(w) / n if len(w) == n and None not in w else None)
    return out


def py_bb(c, n=20, k=2):
    pct, width = [], []
    for i in range(len(c)):
        if i < n - 1:
            pct.append(None)
            width.append(None)
            continue
        w = c[i - n + 1: i + 1]
        m = sum(w) / n
        sd = math.sqrt(sum((v - m) ** 2 for v in w) / n)  # population (TradingView)
        up, lo = m + k * sd, m - k * sd
        pct.append((c[i] - lo) / (up - lo))
        width.append((up - lo) / m)
    return pct, width


def py_atr(h, l, c, n=14):
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, len(c))]
    return py_rma(tr, n)


def py_vwap(t, h, l, c, v):
    out, pv, vv, day = [], 0.0, 0.0, None
    for i in range(len(t)):
        d = t[i] // 86_400_000
        if d != day:
            day, pv, vv = d, 0.0, 0.0
        pv += (h[i] + l[i] + c[i]) / 3 * v[i]
        vv += v[i]
        out.append(pv / vv)
    return out


def py_short_closed(entry, fills):
    return sum(-(s * (1 / entry - 1 / p)) for s, p in fills)


# ---------- JS through node ----------
RUNNER = r"""
const A = require(process.argv[process.argv.length - 1]);
const d = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const brk = process.env.LIVE_AID_BREAK || '';
const bump = a => a.map(v => v * 1.001);
let rsi = A.rsi(d.c, 14);
let rsiSma = A.sma(rsi, 14);
let bb = A.bollinger(d.c, 20, 2);
let atr = A.atr(d.h, d.l, d.c, 14);
let vwap = A.dayVwap(d.t, d.h, d.l, d.c, d.v);
let pnl = A.closedPnlBtc('short', 81414.42, [{size:3240,price:81127},{size:4140,price:81024},{size:900,price:80947.5}]);
let days = A.utcDays(d.t.map((t, i) => [t - 3 * 3600000, 0, d.h[i], d.l[i], d.c[i], d.v[i]]));
let wt = A.wavetrend(d.t, d.h, d.l, d.c, 60000, 200);
let open = A.inversePnlBtc('short', 8280, 81414.42, 81000);
if (brk === 'rsi') rsi = bump(rsi);
if (brk === 'rsiSma') rsiSma = bump(rsiSma);
if (brk === 'bb') bb.pctB = bump(bb.pctB);
if (brk === 'atr') atr = bump(atr);
if (brk === 'vwap') vwap = bump(vwap);
if (brk === 'days') days = days.map(r => [r[0], r[1], r[2], r[3] * 1.001, r[4], r[5]]);
if (brk === 'wt') wt.wt1 = bump(wt.wt1);
if (brk === 'pnl') { pnl = -pnl; open = -open; }
const n = a => a.map(v => Number.isFinite(v) ? v : null);
process.stdout.write(JSON.stringify({rsi:n(rsi), rsiSma:n(rsiSma), pctB:n(bb.pctB), width:n(bb.width), atr:n(atr), vwap:n(vwap), days, wt1:n(wt.wt1), wt2:n(wt.wt2), wtEv:wt.event, pnl, open}));
"""


@pytest.fixture(scope="module")
def js():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed: JS side not run (Python maths still checked in test_pnl_sourced)")
    out = subprocess.run([node, "-e", RUNNER, str(JS)], input=json.dumps({"t": T, "h": H, "l": L, "c": C, "v": V}),
                         capture_output=True, text=True, timeout=60, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def same(js_vals, py_vals, name):
    assert len(js_vals) == len(py_vals) == len(C) >= 150, (name, SOURCE)
    checked = 0
    for i, (a, b) in enumerate(zip(js_vals, py_vals)):
        if b is None:
            assert a is None, f"{name}[{i}] js={a} py=None"
            continue
        assert a is not None and abs(a - b) <= TOL, f"{name}[{i}] js={a} py={b} ({SOURCE})"
        checked += 1
    assert checked >= 100, f"{name}: only {checked} values compared"


def test_rsi14_wilder(js):
    same(js["rsi"], py_rsi(C), "rsi")


def test_rsi_sma14(js):
    same(js["rsiSma"], py_sma(py_rsi(C), 14), "rsiSma")


def test_bollinger_20_2_population(js):
    pct, width = py_bb(C)
    same(js["pctB"], pct, "pctB")
    same(js["width"], width, "width")


def test_atr14_wilder(js):
    same(js["atr"], py_atr(H, L, C), "atr")


def test_day_vwap_hlc3(js):
    same(js["vwap"], py_vwap(T, H, L, C, V), "vwap")


def test_utc_days(js):
    # bars shifted 3 h earlier: the fixture (00:00Z-05:00Z) then straddles midnight, two UTC days
    days = {}
    for t, h, l in zip(T, H, L):
        d = (t - 3 * 3_600_000) // 86_400_000 * 86_400_000
        hi, lo = days.get(d, (-math.inf, math.inf))
        days[d] = (max(hi, h), min(lo, l))
    assert len(js["days"]) == len(days) >= (2 if SOURCE == "fixture" else 1)
    for row in js["days"]:
        hi, lo = days[row[0]]
        assert abs(row[2] - hi) <= TOL and abs(row[3] - lo) <= TOL, (row, hi, lo)


def test_wavetrend_matches_layer_module(js):
    # the repo's WaveTrend layer (FORMULAS.md s20, checked there against its own golden series) is the reference
    import importlib.util
    spec = importlib.util.spec_from_file_location("wavetrend", HERE.parents[1] / "backtest/layers/wavetrend/wavetrend.py")
    wtm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wtm)
    rows = wtm.compute([(t, h, l, c) for t, h, l, c in zip(T, H, L, C)], 60_000)
    nan = lambda v: None if math.isnan(v) else v
    same(js["wt1"], [nan(r.wt1) for r in rows], "wt1")
    same(js["wt2"], [nan(r.wt2) for r in rows], "wt2")
    assert js["wtEv"] == [r.event for r in rows]


FILLS = [(3240, 81127.0), (4140, 81024.0), (900, 80947.5)]


def test_pnl_sourced():
    # SOURCED: operator's Deribit log 2026-10-28, short 8,280 USD avg 81,414.42 -> +0.0004498 BTC before fees
    assert sum(s for s, _ in FILLS) == 8280
    assert abs(py_short_closed(81414.42, FILLS) - 0.0004498) < 5e-8


def test_pnl_js(js):
    assert abs(js["pnl"] - py_short_closed(81414.42, FILLS)) <= TOL
    assert abs(js["pnl"] - 0.0004498) < 5e-8
    assert abs(js["open"] - (-(8280 * (1 / 81414.42 - 1 / 81000)))) <= TOL
    assert js["open"] > 0  # short gains when mark is below entry


# ---------- in-trade panel (card live-aid-in-trade-panel): fixed OURS rules, hand-computed expectations ----------
# Extra LIVE_AID_BREAK modes: itdiv itflow itsqueeze itdom itsupport itvwap itconf (each must fail one test below).
IT_RUNNER = r"""
const A = require(process.argv[process.argv.length - 1]);
const brk = process.env.LIVE_AID_BREAK || '';
const w = 15;
const lowP = [], lowI = [], hiP = [], hiI = [];
for (let i = 0; i < 30; i++) {            // h1 = bars 0-14, h2 = bars 15-29
  const h2 = i >= 15;
  lowP.push(h2 ? 98 + (i % 3) : 100 + (i % 3));  lowI.push(h2 ? 35 + (i % 3) : 30 + (i % 3));   // price lower low, ind higher low
  hiP.push(h2 ? 112 - (i % 3) : 110 - (i % 3));  hiI.push(h2 ? 60 - (i % 3) : 65 - (i % 3));    // price higher high, ind lower high
}
const flatP = Array(30).fill(100), flatI = Array(30).fill(50);
let dv = [A.divergence(lowP, lowI, w), A.divergence(hiP, hiI, w), A.divergence(flatP, flatI, w), A.divergence(lowP.slice(0, 20), lowI.slice(0, 20), w)];
if (brk === 'itdiv') dv[0] = -dv[0];
const now = 1000000;
let fl = A.flow([{t: now - 300000, usd: 200, buy: false}, {t: now - 30000, usd: 50, buy: false}, {t: now - 10000, usd: 100, buy: true}], now);
if (brk === 'itflow') fl.cvd = -fl.cvd;
let sq = [A.squeeze(0.001, 0.002), A.squeeze(0.001, -0.002), A.squeeze(-0.001, 0.002), A.squeeze(-0.001, -0.002), A.squeeze(0.0001, 0.01), A.squeeze(0.001, 0.0001)];
if (brk === 'itsqueeze') sq[1] = sq[0];
let dm = A.dom([[99900, 5], [99800, 9], [90000, 100]], [[100100, 2], [100300, 3], [110000, 50]], 100000);
if (brk === 'itdom') dm.imb = -dm.imb;
const lv = [{n: 'a', p: 99}, {n: 'b', p: 95}, {n: 'c', p: 101}, {n: 'd', p: 98}, {n: 'nan', p: NaN}];
let sup = [A.supports(lv, 100, 1).map(x => x.n), A.supports(lv, 100, -1).map(x => x.n)];
if (brk === 'itsupport') sup = [sup[1], sup[0]];
const mk = (hh, ll, cc) => ({h: Array(5).fill(hh), l: Array(5).fill(ll), c: Array(5).fill(cc), v: Array(5).fill(100)});
const vt = (b, sd) => A.vwapTest(b.h, b.l, b.c, b.v, sd);
let vw = [vt(mk(102, 98, 101), 1).result, vt(mk(102, 98, 99), 1).result, vt(mk(102, 98, 99), -1).result, vt(mk(110, 105, 107), 1).result, vt(mk(102, 98, 101), 1).dist];
if (brk === 'itvwap') vw[1] = 'held';
let fg = [A.flagDiv(1, 1), A.flagDiv(1, -1), A.flagDiv(0, 1), A.flagDiv(null, 1),
          A.flagSqueeze(0.001, 0.002, 1), A.flagSqueeze(0.001, -0.002, 1), A.flagSqueeze(-0.001, 0.002, 1), A.flagSqueeze(-0.001, 0.002, -1),
          A.flagFlow({cvd: 5, delta: 1}, 1), A.flagFlow({cvd: -5, delta: -1}, 1), A.flagFlow({cvd: 5, delta: -1}, 1), A.flagFlow({cvd: -5, delta: -1}, -1),
          A.flagDom({imb: 0.5}, 1), A.flagDom({imb: 0.5}, -1), A.flagDom({imb: 0.1}, 1), A.flagVwap({result: 'held'}), A.flagVwap({result: 'lost'}), A.flagVwap({result: 'no test'}), A.flagVwap(null)];
let cf = [A.confidence([1, -1, -1, -1, null, 0]), A.confidence([1, -1, -1, 0, null, 0]), A.confidence([null, null])];
if (brk === 'itconf') cf[1].reduceRule = true;
process.stdout.write(JSON.stringify({dv, fl, sq, dm, sup, vw, fg, cf}));
"""


@pytest.fixture(scope="module")
def it():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    out = subprocess.run([node, "-e", IT_RUNNER, str(JS)], capture_output=True, text=True, timeout=60, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_it_divergence(it):
    assert it["dv"] == [1, -1, 0, None]  # bullish, bearish, none, too few bars -> NOT_IN_DATA


def test_it_flow_cvd_vs_delta(it):
    # 15 min cvd = -200 -50 +100 = -150; 60 s window holds the 30 s sell 50 and the 10 s buy 100: delta = +50
    assert it["fl"] == {"delta": 50, "cvd": -150, "spanMs": 300000}


def test_it_squeeze_oi(it):
    assert it["sq"] == ["up, OI up: new longs", "up, OI down: short covering (squeeze)", "down, OI up: new shorts",
                        "down, OI down: long unwind", "flat", "up, OI flat"]


def test_it_dom(it):
    d = it["dm"]  # band +/-0.25% of 100000 = 99750..100250: bids 5+9, asks 2 (100300 is outside)
    assert (d["bid"], d["ask"]) == (14, 2)
    assert abs(d["imb"] - 0.75) < 1e-12
    assert d["wall"] == {"side": "bid", "price": 99800, "size": 9}


def test_it_supports(it):
    assert it["sup"] == [["a", "d"], ["c"]]  # long: nearest below 100; short: above


def test_it_vwap_test(it):
    # vwap level 100 on all 5 bars; bars (high 102, low 98) touch it, (110, 105) do not
    assert it["vw"] == ["held", "lost", "held", "no test", 1]  # close 101 long; close 99 long; close 99 short; no touch; dist


def test_it_flags(it):
    assert it["fg"] == [1, -1, 0, None, 1, 0, -1, 1, 1, -1, 0, 1, 1, -1, 0, 1, -1, 0, None]


def test_it_confidence_and_reduce_rule(it):
    a, b, c = it["cf"]
    assert (a["avail"], a["for"], a["against"], a["reduceRule"]) == (5, 1, 3, True)
    assert (b["avail"], b["for"], b["against"], b["reduceRule"]) == (5, 1, 2, False)
    assert c["avail"] == 0 and c["reduceRule"] is False
