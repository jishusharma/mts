"""Tests for live_aid_indicators.js: independent Python maths vs the JS (run through node).

Data: 300 Binance fapi BTCUSDT 1m klines (live, 20 s timeout) or the committed public fixture.
Set LIVE_AID_BREAK=<rsi|rsiSma|bb|atr|vwap|days|pnl> to run the JS with that function deliberately
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
let open = A.inversePnlBtc('short', 8280, 81414.42, 81000);
if (brk === 'rsi') rsi = bump(rsi);
if (brk === 'rsiSma') rsiSma = bump(rsiSma);
if (brk === 'bb') bb.pctB = bump(bb.pctB);
if (brk === 'atr') atr = bump(atr);
if (brk === 'vwap') vwap = bump(vwap);
if (brk === 'days') days = days.map(r => [r[0], r[1], r[2], r[3] * 1.001, r[4], r[5]]);
if (brk === 'pnl') { pnl = -pnl; open = -open; }
const n = a => a.map(v => Number.isFinite(v) ? v : null);
process.stdout.write(JSON.stringify({rsi:n(rsi), rsiSma:n(rsiSma), pctB:n(bb.pctB), width:n(bb.width), atr:n(atr), vwap:n(vwap), days, pnl, open}));
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
