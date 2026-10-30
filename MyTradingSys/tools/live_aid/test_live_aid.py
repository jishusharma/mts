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
# Extra LIVE_AID_BREAK modes: itdiv itflow itsqueeze itdom itsupport itvwap itconf itlive itliqside itliqdb itliqsum itfund itbybit itfold itnews itpulse avroster avwatch avzone avlean avact (each must fail one test below).
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
let lv2 = [A.flowLive(now - 60000, now - 1000, now), A.flowLive(now - 60000, now - 60000, now), A.flowLive(0, now, now), A.flowLive(now - 1000, 0, now)];
if (brk === 'itlive') lv2[0] = false;
const sides = a => a.map(e => e.side + ':' + e.usd);
let lqv = [sides(A.liqDeribit({liquidation: 'T', direction: 'sell', amount: 1000, price: 100}, 7)), sides(A.liqDeribit({liquidation: 'M', direction: 'sell', amount: 1000, price: 100}, 7)),
           sides(A.liqDeribit({liquidation: 'MT', direction: 'buy', amount: 500, price: 100}, 7)), sides(A.liqDeribit({direction: 'buy', amount: 500, price: 100}, 7)),
           sides([A.liqBybit({T: 5, S: 'Buy', v: '0.5', p: '80000'}), A.liqBybit({T: 5, S: 'Sell', v: '0.25', p: '80000'})]),
           sides([A.liqBinance({o: {S: 'SELL', q: '0.1', ap: '80000', T: 5}}), A.liqBinance({o: {S: 'BUY', q: '0.2', ap: '80000', T: 5}})])];
if (brk === 'itliqside') lqv[4] = lqv[4].reverse();
if (brk === 'itliqdb') lqv[1] = lqv[0];
const ev = [{t: now - 30000, side: 'long', usd: 150000}, {t: now - 120000, side: 'short', usd: 20000}, {t: now - 400000, side: 'long', usd: 10000}, {t: now + 1, side: 'short', usd: 5000}];
let lqs = [A.liqSum(ev, now, 60000), A.liqSum(ev, now, 300000), A.liqSum(ev, now, 900000),
           A.liqSum([{t: now, side: 'long', usd: 100}, {t: now, side: 'short', usd: 60}], now, 60000).dom, A.liqSum([], now, 60000).dom];
if (brk === 'itliqsum') lqs[1].dom = 'mixed';
let fd = [A.fundRead(0.00005311), A.fundRead(-0.0004), A.fundRead(0.000005), A.fundRead(NaN), A.premium(76859.45, 76840.34), A.premium(NaN, 1)];
if (brk === 'itfund') fd[1].side = 'longs';
let bt = A.bybitTick(null, {type: 'snapshot', data: {a: '1', b: '2'}});
bt = A.bybitTick(bt, {type: 'delta', data: {b: '3'}});
let bt2 = A.bybitTick(bt, {type: 'snapshot', data: {c: '1'}});
if (brk === 'itbybit') bt = {b: '3'};
const H = 3600000, b0 = 4 * H * 100;
let fo = A.foldBars([[b0 - H, '9', '9', '9', '9', '1'], [b0, '10', '12', '9', '11', '2'], [b0 + H, '11', '15', '10', '14', '3'], [b0 + 3 * H, '14', '14', '8', '13', '4'], [b0 + 4 * H, '13', '13', '12', '12.5', '5']], 4 * H);
if (brk === 'itfold') fo[1][3] = 9;
const M = 60000;
let nt = ['Tree News: POTENTIAL BINANCE HACK ONGOING - ONCHAIN', 'Binance suspends all deposits and withdrawals', 'SEC approves spot ETF options', 'FOMC holds rates; Powell speaks at 18:30', 'Bitcoin tops $80,000', 'Moonbirds pairs are now live', 'Hackathon winners announced'].map(A.newsTags);
if (brk === 'itnews') nt[0] = [];
const nws = [{_id: 'a', time: now - 10 * M, importance: 7.4}, {_id: 'b', time: now - 20 * M, importance: 8}, {_id: 'c', time: now - 30 * M, importance: 7},
             {_id: 'd', time: now - 120 * M, importance: 9}, {_id: 'e', time: now - 5000, importance: 6.9}, {_id: 'f', time: now + 1000, importance: 9}];
let np = [A.newsPulse(nws, now), A.newsPulse(nws.filter(x => x._id !== 'c'), now), A.newsPulse([], now),
          A.newsMerge([{_id: 'a', time: 1}, {_id: 'b', time: 3}], [{_id: 'b', time: 3}, {_id: 'c', time: 2}], 2).map(x => x._id)];
if (brk === 'itpulse') np[0].level = 'BUSY';
const nowA = Date.parse('2026-10-30T12:00:00Z');
const rost = [{short: 'Krown', channel: '@ECKrown', enabled: true, ingested: true}, {short: 'Rekt', enabled: true, ingested: true},
              {short: 'Bob', enabled: true, ingested: false}, {short: 'Malkan', enabled: false, ingested: false}, {short: 'Michael', enabled: true, ingested: true},
              {short: 'Zed', enabled: true, ingested: true, in_roster: false}];
const arows = [{analyst: 'Krown', published: '2026-10-24', bias: 'BULLISH'}, {analyst: 'Krown', published: '2026-10-27', bias: 'BEARISH'},
               {analyst: 'Michael', published: '2026-10-26', bias: 'NEUTRAL'}, {analyst: 'Zed', published: '2026-10-30', bias: 'NO_VIEW'}];
let an = A.rosterRead(rost, arows, [{analyst: 'Rekt'}, {analyst: 'Krown'}], nowA).map(a => [a.short, a.state, a.rows, a.rejected, a.last, a.bias, a.inRoster]);
if (brk === 'avroster') an[0][1] = 'STALE';
const rd = A.rosterRead(rost, arows, [], nowA);
let avt = [A.analystVote(rd), A.analystVote(A.rosterRead(rost, arows, [], Date.parse('2026-11-20T00:00:00Z'))),
           A.analystVote([{state: 'FRESH', bias: 'BULLISH'}, {state: 'FRESH', bias: 'BULLISH'}, {state: 'FRESH', bias: 'BEARISH'}, {state: 'STALE', bias: 'BEARISH'}])];
const lvs = [{level: 80100, analyst: 'K', said: 'a'}, {level: 79000, analyst: 'M'}, {level: 76000, analyst: 'K'}, {level: 90000, analyst: 'M'}, {level: 78000, analyst: 'K', expired: true}, {level: NaN}];
let lw = A.levelWatch(lvs, 80000).map(x => [x.level, x.zone, x.side, Math.round(x.dist * 1000) / 1000]);
if (brk === 'avwatch') lw.reverse();
let ln = [A.lean([1, 1, -1, null]), A.lean([1, -1, 0, null]), A.lean([1, null, null, null]), A.lean([-1, -1, 0, 0]), A.lean([1, 1, -1, -1])].map(x => [x.call, x.bull, x.bear, x.n]);
if (brk === 'avlean') ln[0][0] = 'MIXED';
const zl = [{level: 80100}, {level: 80150}, {level: 80300}, {level: 79880}, {level: 79000}];
let zn = [A.zones(A.levelWatch(zl, 80000), 80000), A.zones(A.levelWatch(zl, 80200), 80200)].map(zz => zz.map(z => [z.lo, z.hi, z.items.length, z.side, z.zone, Math.round(z.dist * 1000) / 1000]));
if (brk === 'avzone') zn[0][0][1] = 80150;
let ac = A.actions({call: 'BEARISH LEAN'}, A.zones(A.levelWatch(lvs, 80000), 80000), {level: 'EVENT', n: 4}).map(a => [a.when, a.kind, a.w ? a.w.lo : a.n, !!a.withLean]);
if (brk === 'avact') ac[2][3] = false;
let ac2 = A.actions({call: 'MIXED'}, A.zones(A.levelWatch(lvs, 80000), 80000), {level: 'BUSY', n: 1}).map(a => [a.when, !!a.withLean]);
let ac3 = A.actions({call: 'BULLISH LEAN'}, A.zones(A.levelWatch(zl, 80200), 80200), null).map(a => [a.when, a.kind, !!a.withLean]);
process.stdout.write(JSON.stringify({dv, fl, sq, dm, sup, vw, fg, cf, lv2, lqv, lqs, fd, bt: [bt, bt2], fo, nt, np, an, avt, lw, zn, ln, ac, ac2, ac3}));
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


def test_it_flow_live_on_quiet_tape(it):
    # Deribit trades.100ms is sparse (9 messages in 20 s on 2026-10-29): no trade for 60 s while the same socket's
    # ticker is fresh = quiet tape (live); both silent = dead; no trade since connect = not live
    assert it["lv2"] == [True, False, False, True]


def _coil_rows():
    # 60 closed 15m bars alternating 100/101 (constant band width), then a close at 105 with 4x volume and
    # taker buy 300 of 400 (delta share +0.5), then one still-forming bar that must be ignored.
    rows, t0 = [], 1_700_000_000_000
    for i in range(60):
        c = 100.0 if i % 2 == 0 else 101.0
        rows.append([t0 + i * 900_000, c, c + 0.2, c - 0.2, c, 100.0, 0, 0, 0, 50.0])
    rows.append([t0 + 60 * 900_000, 101.0, 105.1, 100.9, 105.0, 400.0, 0, 0, 0, 300.0])
    rows.append([t0 + 61 * 900_000, 105.0, 120.0, 104.0, 119.0, 5.0, 0, 0, 0, 5.0])
    now = t0 + 61 * 900_000 + 60_000
    return rows, now


def test_coil_pierce_hand_case():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    rows, now = _coil_rows()
    runner = ("const A=require(process.argv[1]);let d='';process.stdin.on('data',x=>d+=x).on('end',()=>{const j=JSON.parse(d);"
              "console.log(JSON.stringify(A.coilPierce(j.rows,900000,j.now,105.3,90)))})")
    out = subprocess.run([node, "-e", runner, str(JS)], input=json.dumps({"rows": rows, "now": now}),
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    r = json.loads(out.stdout)
    closes = [x[4] for x in rows[:61]]
    w = closes[-20:]
    m = sum(w) / 20
    sd = (sum((x - m) ** 2 for x in w) / 20) ** 0.5
    assert closes[-1] > m + 2 * sd  # hand check: the 105 close is outside the upper band
    assert r["coil"] is False and r["bwPct"] == 1  # the pierce bar itself widens the band above every earlier width
    p = r["pierce"]
    assert p["coilBefore"] is True  # bar before the pierce: flat 100/101 width, none of the earlier widths is smaller
    assert p["side"] == "up" and p["ageBars"] == 0 and p["close"] == 105.0
    assert abs(p["volRatio"] - 4.0) < 1e-12 and abs(p["deltaShare"] - 0.5) < 1e-12
    assert p["force"] == "strong" and p["byForce"]["reach"] == 39
    assert abs(p["dist"] - 0.3 / 105) < 1e-12 and p["byDist"]["reach"] == 74


# ---------- liquidations (STEPS.md "Liquidation rules"): hand-computed ----------
def test_liq_side_per_venue(it):
    # Deribit T + taker sell = long; M + taker sell = maker bought = short; MT + taker buy = short (taker) and long (maker); no field = none
    # Bybit Buy = long 0.5 x 80000; Sell = short 0.25 x 80000. Binance SELL = long 0.1 x 80000; BUY = short 0.2 x 80000
    assert it["lqv"] == [["long:1000"], ["short:1000"], ["short:500", "long:500"], [],
                         ["long:40000", "short:20000"], ["long:8000", "short:16000"]]


def test_liq_windows_dominance_big(it):
    # 1 min: long 150000 only; 5 min: + short 20000 (2 min ago); 15 min: + long 10000 (6.7 min ago); the future event never counts
    assert it["lqs"][0] == {"long": 150000, "short": 0, "n": 1, "big": 1, "dom": "longs"}
    assert it["lqs"][1] == {"long": 150000, "short": 20000, "n": 2, "big": 1, "dom": "longs"}
    assert it["lqs"][2] == {"long": 160000, "short": 20000, "n": 3, "big": 1, "dom": "longs"}
    assert it["lqs"][3:] == ["mixed", "none"]  # 100 vs 60 is under 2x; nothing = none


# ---------- funding and premium (STEPS.md "Funding rules"): hand-computed ----------
def test_funding_read(it):
    # 0.00005311 per 8h = 0.005311 %; x 3 x 365 = 5.8155 % a year; positive = longs pay; under 0.03 % per 8h = not high
    a, b, c, d = it["fd"][:4]
    assert a["side"] == "longs" and a["high"] is False
    assert a["pct8h"] == pytest.approx(0.005311) and a["annual"] == pytest.approx(5.815545)
    # -0.0004 = -0.04 % per 8h: shorts pay, high (|r| >= 0.0003); -43.8 % a year
    assert b["side"] == "shorts" and b["high"] is True and b["annual"] == pytest.approx(-43.8)
    assert c["side"] == "zero" and d is None  # |r| < 0.00001 = about zero; no number = no read


def test_premium_and_bybit_merge(it):
    # mark 76859.45 - index 76840.34 = 19.11 pts = 19.11 / 76840.34 x 10000 = 2.487 bps
    p = it["fd"][4]
    assert p["pts"] == pytest.approx(19.11) and p["bps"] == pytest.approx(2.48698, abs=1e-4)
    assert it["fd"][5] is None
    # Bybit tickers: a delta carries only changed fields and merges; a snapshot replaces
    assert it["bt"] == [{"a": "1", "b": "3"}, {"c": "1"}]


def test_fold_1h_into_4h(it):
    # 4h buckets open at multiples of 4h from 1970-01-01 00:00Z (= 00/04/08/12/16/20Z). b0 - 1h belongs to the bucket before;
    # b0..b0+3h: open 10 (first), high 15, low 8, close 13 (last), volume 2+3+4 = 9 (b0+2h missing is fine); b0+4h starts a new bucket
    H = 3600000
    b0 = 4 * H * 100
    assert it["fo"] == [[b0 - 4 * H, 9, 9, 9, 9, 1], [b0, 10, 15, 8, 13, 9], [b0 + 4 * H, 13, 13, 12, 12.5, 5]]


def test_news_word_tags(it):
    # Word classes (OURS, research/news_feeds_2026-10-30 N6), checked in order hack, halt, etf, fed, war, delist, btc; whole words only
    assert it["nt"] == [["hack"], ["halt"], ["etf"], ["fed"], ["btc"], [], []]


def test_news_pulse_and_merge(it):
    # Pulse = Tree importance >= 7 (SOURCED score, OURS mark) with now - 60 min < time <= now: a 7.4, b 8, c 7.0 count; d is 2 h old,
    # e scores 6.9, f is in the future. 3 or more = EVENT, 1-2 = BUSY, 0 = QUIET (OURS; normal day 5-9 a day measured 10-26..10-28)
    p = it["np"]
    assert p[0]["n"] == 3 and p[0]["level"] == "EVENT"
    assert p[1]["n"] == 2 and p[1]["level"] == "BUSY"
    assert p[2]["n"] == 0 and p[2]["level"] == "QUIET"
    # merge keeps one copy per _id, newest first, capped
    assert p[3] == ["b", "c"]


# ---------- analysts and verdict board (STEPS.md Verdict rules; thresholds OURS, hand-computed) ----------
def test_analyst_roster_states(it):
    # now 2026-10-30 12:00Z. Krown newest row 10-27 (2 rows): (12:00 + 3 d) / 1 d floors to 3 <= 3 -> FRESH, bias of the newest row.
    # Rekt: enabled + ingested, no row -> NO_ROW (1 rejected). Bob: enabled, not ingested -> NOT_FETCHED. Malkan: disabled -> OFF.
    # Michael newest 10-26: 4 d -> STALE. Zed has a row but is not in the roster file: kept, inRoster false.
    assert it["an"] == [["Krown", "FRESH", 2, 1, "2026-10-27", "BEARISH", True], ["Rekt", "NO_ROW", 0, 1, "", "", True],
                        ["Bob", "NOT_FETCHED", 0, 0, "", "", True], ["Malkan", "OFF", 0, 0, "", "", True],
                        ["Michael", "STALE", 1, 0, "2026-10-26", "NEUTRAL", True], ["Zed", "FRESH", 1, 0, "2026-10-30", "NO_VIEW", False]]


def test_analyst_vote(it):
    # fresh: Krown BEARISH (-1), Zed NO_VIEW skipped -> -1; three weeks later nobody is fresh -> None; +1 +1 -1 (STALE ignored) -> +1
    assert it["avt"] == [-1, None, 1]


def test_level_watch_band_and_zones(it):
    # price 80,000: 80,100 = +0.125 % AT above; 79,000 = -1.25 % NEAR below; 76,000 = -5 % WATCH; 90,000 = +12.5 % outside 6 %;
    # 78,000 expired and NaN dropped. Nearest first.
    assert it["lw"] == [[80100, "AT", "above", 0.125], [79000, "NEAR", "below", -1.25], [76000, "WATCH", "below", -5.0]]


def test_zones_merge_and_inside(it):
    # sorted 79,000 / 79,880 / 80,100 / 80,150 / 80,300: 79,880 -> 80,100 is 0.275 % (> 0.25 %, new zone); 80,100 -> 80,150 0.062 % and
    # 80,150 -> 80,300 0.187 % join one zone 80,100-80,300. Price 80,000: that zone is +0.125 % (AT, above), 79,880 -0.15 % (AT, below),
    # 79,000 -1.25 % (NEAR). Price 80,200 sits inside the zone: side 'at', distance 0.
    assert it["zn"][0] == [[80100, 80300, 3, "above", "AT", 0.125], [79880, 79880, 1, "below", "AT", -0.15], [79000, 79000, 1, "below", "NEAR", -1.25]]
    assert it["zn"][1][0] == [80100, 80300, 3, "at", "AT", 0]


def test_lean_rule(it):
    # needs 3 votes in data; bull >= 2 and bull >= 2 x bear -> BULLISH LEAN (2 vs 1); 1/1/0 -> MIXED; 1 vote -> NOT ENOUGH DATA;
    # -1 -1 0 0 -> BEARISH LEAN; 2 vs 2 -> MIXED
    assert it["ln"] == [["BULLISH LEAN", 2, 1, 3], ["MIXED", 1, 1, 3], ["NOT ENOUGH DATA", 1, 0, 1], ["BEARISH LEAN", 0, 2, 4], ["MIXED", 2, 2, 4]]


def test_actions_order_and_lean_direction(it):
    # news EVENT first (NOW), AT level NOW, NEAR -> NEXT, WATCH -> LATER; bearish lean: levels below are in its direction, above are not
    assert it["ac"] == [["NOW", "news", 4, False], ["NOW", "resistance", 80100, False], ["NEXT", "support", 79000, True], ["LATER", "support", 76000, True]]
    # a BUSY pulse adds no row; MIXED lean marks nothing as in its direction
    assert it["ac2"] == [["NOW", False], ["NEXT", False], ["LATER", False]]
    # price 80,200 inside the 80,100-80,300 zone: kind 'zone', never in the lean's direction; 79,880 = -0.40 % and 79,000 = -1.496 %
    # are both NEAR (<= 1.5 %) supports, against a bullish lean.
    assert it["ac3"] == [["NOW", "zone", False], ["NEXT", "support", False], ["NEXT", "support", False]]


def test_us_open_ladder_hand_case():
    """usOpen: levels above/below a mark from hand-built 5m and daily rows, bucket and rate lookup (LIVE_AID_BREAK=ituo)."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    day0 = 1_800_000_000_000 - (1_800_000_000_000 % 86_400_000)      # a UTC midnight
    open_ms = day0 + 13 * 3_600_000 + 30 * 60_000                       # 13:30Z
    rows5 = []                                                          # 00:00Z..13:30Z box: high 103, low 97; opening range 15 min: high 101.5, low 99.5
    t = day0
    while t < open_ms:
        rows5.append([t, 100, 103 if t == day0 + 3_600_000 else 100.5, 97 if t == day0 + 7_200_000 else 99.5, 100, 1])
        t += 300_000
    for i in range(3):
        rows5.append([open_ms + i * 300_000, 100, 101.5 if i == 1 else 100.2, 99.5 if i == 2 else 99.8, 100, 1])
    daily = [[day0 - k * 86_400_000, 100, 100 + k, 100 - k, 100, 1] for k in range(8, 0, -1)]  # prior 8 days: highs 101..108, lows 99..92
    rates = {"pdh": {"0-0.25": {"n": 40, "touch": 80, "nt": 32, "held": 50}}, "d3h": {"0.5-1": {"n": 90, "touch": 40, "nt": 36, "held": 70}},
             "dayH": {"2+": {"n": 100, "touch": 5, "nt": 5, "held": 30}}, "orH": {}, "orL": {}, "dayL": {}, "pdl": {}, "d3l": {}, "d7h": {}, "d7l": {}}
    now = open_ms + 16 * 60_000
    px = 100.8
    runner = ("const A=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);"
              "console.log(JSON.stringify(A.usOpen(j.rows5,j.daily,j.open,j.now,j.px,j.rates)))})")
    out = subprocess.run([node, "-e", runner, str(JS)], input=json.dumps({"rows5": rows5, "daily": daily, "open": open_ms, "now": now, "px": px, "rates": rates}),
                         capture_output=True, text=True, timeout=60, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    r = json.loads(out.stdout)
    assert r["phase"] == "in" and r["minutes"] == 16 and r["priorDays"] == 8
    assert r["box"] == {"h": 103, "l": 97, "bars": 162} and r["or"] == {"h": 101.5, "l": 99.5, "bars": 3}
    # Independent expectation: up ladder sorted by distance, same-price levels merged (pdh 101 = 3-day? no: d3h = 103 = dayH)
    up = [(x["name"], x["p"], x["bucket"]) for x in r["up"]]
    assert up[0] == ("prev day high", 101, "0-0.25")           # (101-100.8)/100.8 = 0.198 %
    assert up[1] == ("opening range high", 101.5, "0.5-1")     # 0.694 %
    assert up[2] == ("day high so far = 3-day high", 103, "2+")  # 2.18 %, merged
    assert up[3] == ("7-day high", 107, "2+")
    assert [x["name"] for x in r["down"]][:3] == ["opening range low", "prev day low", "day low so far = 3-day low"]   # 99.5, 99, 97 (merged)
    assert r["up"][0]["touch"] == 80 and r["up"][0]["held"] == 50 and r["up"][0]["n"] == 40
    assert r["up"][1]["touch"] is None and r["up"][1]["n"] == 0            # orH has no rates row
    assert r["up"][2]["touch"] == 5 and r["up"][2]["held"] is None        # dayH 2+: nt=5 under 30 -> held hidden
    assert all(x["dist"] > 0 for x in r["up"]) and all(x["dist"] < 0 for x in r["down"])


# ---------- macro calendar strip (card live-aid-macro-calendar): ForexFactory JSON, impact field SOURCED ----------
FF_FIXTURE = HERE / "fixture_ff_calendar.json"


def _next_high(events, now_ms):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = ("const A=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);"
              "console.log(JSON.stringify(A.nextHighEvent(j.events,j.now)))})")
    out = subprocess.run([node, "-e", runner, str(JS)], input=json.dumps({"events": events, "now": now_ms}),
                         capture_output=True, text=True, timeout=60, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def _utc(s):
    import datetime
    return int(datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000)


def test_next_high_event():
    """nextHighEvent on the 6-event real fixture. Expected values worked by hand (feed times are EDT = UTC-4 on 10-28/29):
    Annual Budget Release GBP High (decoy), Federal Funds Rate USD High 10-28 14:00 EDT = 18:00Z, FOMC Press Conference USD High 14:30 EDT = 18:30Z,
    Advance GDP q/q USD High 10-29 08:30 EDT = 12:30Z, Advance GDP Price Index USD Medium (same minute, decoy), Main Refinancing Rate EUR High (decoy)."""
    ev = json.loads(FF_FIXTURE.read_text(encoding="utf-8"))["events"]
    assert len(ev) == 6
    # A: 12:00Z on 10-29: GDP is 30 min away; the two earlier USD High events are results, newest first; GBP/EUR/Medium never count.
    a = _next_high(ev, _utc("2026-10-29T12:00:00Z"))
    assert a["next"]["title"] == "Advance GDP q/q" and a["next"]["t"] == _utc("2026-10-29T12:30:00Z")
    assert a["next"]["countdownMs"] == 1_800_000 and a["next"]["forecast"] == "3.2%" and a["next"]["previous"] == "1.5%"
    assert [r["title"] for r in a["last"]] == ["FOMC Press Conference", "Federal Funds Rate"]
    assert a["last"][1]["forecast"] == "4.00%" and a["last"][1]["actual"] is None     # the feed has no actual field
    # same answer when the feed order is reversed (no reliance on order)
    assert _next_high(ev[::-1], _utc("2026-10-29T12:00:00Z")) == a
    # B: exactly at the GDP minute: event time <= now so it is a result, nothing is next, countdown never negative.
    b = _next_high(ev, _utc("2026-10-29T12:30:00Z"))
    assert b["next"] is None
    assert [r["title"] for r in b["last"]] == ["Advance GDP q/q", "FOMC Press Conference", "Federal Funds Rate"]
    # C: 1 ms before the GDP minute: still next with 1 ms to go, and not yet shown as a result (time honesty).
    c = _next_high(ev, _utc("2026-10-29T12:30:00Z") - 1)
    assert c["next"]["title"] == "Advance GDP q/q" and c["next"]["countdownMs"] == 1
    assert [r["title"] for r in c["last"]] == ["FOMC Press Conference", "Federal Funds Rate"]
    # D: before everything on 10-28 12:00Z: Fed rate is 6 h away; no results yet.
    d = _next_high(ev, _utc("2026-10-28T12:00:00Z"))
    assert d["next"]["title"] == "Federal Funds Rate" and d["next"]["countdownMs"] == 21_600_000 and d["last"] == []
    # E: an actual, when the feed carries one, is passed through (synthetic row); bad rows (no date, wrong impact) are skipped.
    syn = [{"title": "CPI m/m", "country": "USD", "date": "2026-11-12T08:30:00-05:00", "impact": "High", "actual": "0.4%", "forecast": "0.3%", "previous": "0.2%"},
           {"title": "bad", "country": "USD", "date": "not a date", "impact": "High", "forecast": "", "previous": ""},
           {"title": "low", "country": "USD", "date": "2026-11-12T09:00:00-05:00", "impact": "Low", "forecast": "", "previous": ""}]
    e = _next_high(syn, _utc("2026-11-12T14:00:00Z"))      # 08:30 EST = 13:30Z, so 30 min ago
    assert e["next"] is None and len(e["last"]) == 1 and e["last"][0]["actual"] == "0.4%" and e["last"][0]["forecast"] == "0.3%"
    # F: empty input -> no event, no results
    assert _next_high([], 0) == {"next": None, "last": []}
