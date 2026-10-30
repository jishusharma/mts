"""'What the money is doing' maths in live_aid_indicators.js (research/eagle_eyes_picture_2026-10-28/OI_COMMENTARY_SPEC.md).

Expected numbers are computed here in Python from the spec's rules and the committed public Bybit fixture, not from the JS.
Set LIVE_AID_BREAK=omstate|omwin|omdis|omflush|ompath to corrupt one output (each must fail one test).
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JS = HERE / "live_aid_indicators.js"
FIX = json.loads((HERE / "fixture_bybit_flush_1030.json").read_text(encoding="utf-8"))
T0 = 1793389500000 - 27 * 300000  # first fixture bar, 2026-10-30 17:30Z
M = 60000

RUNNER = r"""
const A = require(process.argv[1]);
const brk = process.env.LIVE_AID_BREAK || '';
const fx = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = {};
out.st = [[0.002, 0.002], [-0.002, 0.002], [0.002, -0.002], [-0.002, -0.002], [0.0005, 0.0015], [0.0009, -0.001], [0.0009, 0.0009], [NaN, 0.01]]
  .map(x => { const s = A.oiState(x[0], x[1]); return s ? [s.key, s.money, s.text] : null; });
if (brk === 'omstate') out.st[1][0] = 'up/up';
const now = fx.now, h = [];
for (let k = 0; k <= 60; k++) h.push({ t: now - 3600000 + k * 60000, px: 80000 * (1 + 0.0001 * k), oi: 50000 * (1 - 0.00005 * k) });
const w = ms => { const r = A.oiWindow(h, now, ms); return r.err ? r.err : [Math.round(r.dp * 1e6), Math.round(r.doi * 1e6), r.spanMs, r.state.key]; };
out.win = [w(300000), w(900000), w(3600000)];
out.stale = A.oiWindow(h, now + 100000, 300000).err;
out.short = A.oiWindow(h.slice(50), now, 900000).err;
const hz = h.map(x => Object.assign({}, x)); hz[hz.length - 1].oi = 0;
out.zero = A.oiWindow(hz, now, 300000).err;
out.none = A.oiWindow([], now, 300000).err;
if (brk === 'omwin') out.stale = 'ok';
const vs = [{ name: 'Binance', btc: 80000, w: { dp: -0.001, doi: 0.005 } }, { name: 'Bybit', btc: 68000, w: { dp: -0.0012, doi: -0.006 } },
            { name: 'Deribit', btc: 9000, w: { err: 'feed stale' } }];
const net = A.oiNet(vs);
out.net = [Math.round(net.doi * 1e7), Math.round(net.dp * 1e7), net.n, net.of, net.state.key];
out.dis = A.oiDisagree(vs, net.doi);
out.dis2 = A.oiDisagree([{ name: 'Binance', w: { doi: 0.0019 } }, { name: 'Bybit', w: { doi: -0.006 } }], -0.003);
if (brk === 'omdis') out.dis = null;
const bars = A.oiBars(fx.klines, fx.oi);
out.nbars = bars.length;
const zoi = Object.assign({}, fx.oi); zoi[String(fx.klines[3][0])] = 0;
out.nzero = A.oiBars(fx.klines, zoi).length;
const ev = A.oiEvents(bars);
out.ev = ev.map(e => [e.kind, e.t, e.px, Math.round(e.move * 1e6), Math.round(e.doi * 1e6), Math.round(e.close * 1e6)]);
if (brk === 'omflush') out.ev = [];
const e = A.oiLastEvent(bars, Date.UTC(2026, 9, 30, 19, 0));
out.text = A.oiEventText(e, null);
out.text2 = A.oiEventText(e, { long: 4100000, short: 0 });
out.gone = A.oiLastEvent(bars, Date.UTC(2026, 9, 30, 20, 10));
const e2 = A.oiLastEvent(bars, Date.UTC(2026, 9, 30, 19, 10));
out.legs = [e.legs, e2.legs, e2.t, e2.lastT, e2.ext];
out.text3 = A.oiEventText(e2, null);
const last = bars[bars.length - 1], p = A.oiPath(bars, e, last.c, last.oi1);
out.path = [p.done, p.group, Math.round(p.doi * 1e6), p.chop, p.hi];
if (brk === 'ompath') out.path[1] = 'flat';
out.exp = A.oiExpect(e, p);
const early = A.oiPath(bars.slice(0, e.i + 4), e, bars[e.i + 3].c, bars[e.i + 3].oi1);
out.early = [early.done, early.minsLeft, A.oiExpect(e, early).measured];
out.trap = A.oiTrap(e, { hi: 76900 }, 76700, e.oi1 * 1.003);
out.notrap = [A.oiTrap(e, { hi: 76900 }, 76950, e.oi1 * 1.003), A.oiTrap(e, { hi: 76900 }, 76700, e.oi1 * 1.001)];
out.none_exp = A.oiExpect(null, null);
process.stdout.write(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def om():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH")
    fx = dict(FIX, now=1793390000000)
    out = subprocess.run([node, "-e", RUNNER, str(JS)], input=json.dumps(fx), capture_output=True, text=True, timeout=60,
                         env=os.environ.copy())
    assert out.returncode == 0, out.stderr[-2000:]
    return json.loads(out.stdout)


def test_six_states(om):
    # spec table: |x| < 0.1 % = flat; 0.0005 price = flat, 0.0015 OI = up -> building; 0.09 % / -0.1 % -> closing quietly
    assert [s[0] for s in om["st"][:7]] == ["up/up", "down/up", "up/down", "down/down", "flat/up", "flat/down", "flat/flat"]
    assert [s[1] for s in om["st"][:7]] == ["in", "in", "out", "out", "in", "out", "flat"]
    assert om["st"][0][2] == "Money entering on the long side: new longs are buying."
    assert om["st"][1][2] == "Money entering on the short side: new shorts are selling."
    assert om["st"][2][2] == "Money leaving: shorts are covering (a squeeze); the rise is not fed by new buyers."
    assert om["st"][3][2] == "Money leaving: longs are closing or being liquidated (a flush)."
    assert om["st"][4][2] == "Positions building without a move: both sides adding, pressure stored for the next break."
    assert om["st"][5][2] == "Positions closing quietly; interest is fading."
    assert om["st"][7] is None


def test_windows_stale_short_and_zero(om):
    # samples every minute for 60 min: px * (1 + 0.0001 k), oi * (1 - 0.00005 k), k = 0..60; window base = k 55 / 45 / 0
    def exp(k0):
        dp = (1 + 0.0001 * 60) / (1 + 0.0001 * k0) - 1
        doi = (1 - 0.00005 * 60) / (1 - 0.00005 * k0) - 1
        return [round(dp * 1e6), round(doi * 1e6), (60 - k0) * M]
    assert [x[:3] for x in om["win"]] == [exp(55), exp(45), exp(0)]
    assert [x[3] for x in om["win"]] == ["flat/flat", "up/flat", "up/down"]  # 0.05 %/-0.025 %, 0.15 %/-0.075 %, 0.6 %/-0.3 %
    assert om["stale"] == "feed stale, last sample 100 s ago"
    # 11 samples from k 50: oldest 10 min old; the 15 min window needs (10 - 15 + 1) -> 4 more min
    assert om["short"] == "needs 4 min more of samples"
    assert om["zero"] == "0 OI value" and om["none"] == "no samples"


def test_venue_disagreement_and_net(om):
    # net = (80000 x 0.5 % - 68000 x 0.6 %) / 148000 = -0.0054 % -> flat, price -0.11 % -> down/flat; Deribit stale is left out
    assert om["net"] == [round((80000 * 0.005 - 68000 * 0.006) / 148000 * 1e7), round((80000 * -0.001 - 68000 * 0.0012) / 148000 * 1e7), 2, 3, "down/flat"]
    assert om["dis"] == "Binance adding, Bybit closing: positions moving between exchanges, net money about flat."
    assert om["dis2"] is None  # +0.19 % is under the 0.2 % bar


def _py_events():
    k, oi = FIX["klines"], {int(t): v for t, v in FIX["oi"].items()}
    bars = [b for b in k if oi.get(b[0], 0) > 0 and oi.get(b[0] + 300000, 0) > 0]
    out = []
    for i, b in enumerate(bars):
        pc = bars[i - 1][4] if i and bars[i - 1][0] == b[0] - 300000 else b[1]
        doi = oi[b[0] + 300000] / oi[b[0]] - 1
        if doi <= -0.002 and b[3] / pc - 1 <= -0.0025:
            out.append(["FLUSH", b[0], b[3], round((b[3] / pc - 1) * 1e6), round(doi * 1e6), round((b[4] / pc - 1) * 1e6)])
        elif doi <= -0.002 and b[2] / pc - 1 >= 0.0025:
            out.append(["SQUEEZE", b[0], b[2], round((b[2] / pc - 1) * 1e6), round(doi * 1e6), round((b[4] / pc - 1) * 1e6)])
    return bars, out


def test_flush_detector_replays_10_30_1850(om):
    bars, ev = _py_events()
    assert om["nbars"] == len(bars) == 27  # the 19:45 bar has no closing snapshot
    assert om["nzero"] == 25  # a 0 OI snapshot drops both bars that use it
    assert om["ev"] == ev
    # 18:50Z low 76,232 vs prev close 76,651.9; 19:00Z low 76,380.6 vs 76,600.0 = -0.29 % with OI -0.52 %
    assert [e[:3] for e in ev] == [["FLUSH", T0 + 16 * 300000, 76232.0], ["FLUSH", T0 + 18 * 300000, 76380.6]]
    assert om["text"] == "FLUSH 18:50Z, low 76232, price -0.55 %, OI -0.37 % (-256 BTC), longs liquidated"
    assert om["text2"].endswith("longs liquidated 4.1M seen by this page")
    # at 19:00Z the 19:00 bar is still forming: one leg; at 19:10Z two legs, anchored on 18:50 (2 bars apart, under 12)
    assert om["legs"] == [1, 2, T0 + 16 * 300000, T0 + 18 * 300000, 76232.0]
    assert om["text3"].endswith("; 2 bars hit within 60 min, the last 19:00Z, extreme 76232")
    assert om["gone"] is None  # 20:10Z: the last leg closed 19:05Z, more than 60 min ago


def test_path_trap_and_measured_line(om):
    # 8 bars after 18:50 = the 19:30 bar; OI at its close (19:35 stamp) 67,809.29 vs 68,173.621 = -0.53 % -> falling;
    # price 76,434.8 vs 76,617.0 = -0.24 % -> chop holds. Bounce high after the flush = 76,796.9 (18:55 bar).
    oi = {int(t): v for t, v in FIX["oi"].items()}
    flush = T0 + 16 * 300000
    d = oi[flush + 9 * 300000] / oi[flush + 300000] - 1
    assert om["path"] == [True, "falling", round(d * 1e6), True, 76796.9]
    x = om["exp"]
    assert x["measured"] and x["n"] == 22
    assert "4 h drop over 1 %: 14 % vs 6 % base" in x["text"] and "closed -0.05 %" in x["text"]
    assert om["early"] == [False, 25, False]  # 3 bars after the flush: 25 min to the C24 read
    assert om["trap"]["text"] == "shorts trapped above 76900; longs trapped below 76232"
    assert om["notrap"] == [None, None]  # price over the bounce high; OI +0.1 % under the 0.2 % bar
    assert not om["none_exp"]["measured"] and "not measured yet" in om["none_exp"]["text"]
