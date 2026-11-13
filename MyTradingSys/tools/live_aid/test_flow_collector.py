"""Tests for flow_collector.py (requirement R25): Python classification against the same fixture as the JS (flow_fixture.json), digest format,
trade parsing, footprint arithmetic. Expected numbers are worked out by hand in the comments."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import flow_collector as F

HERE = Path(__file__).resolve().parent
FIX = json.loads((HERE / "flow_fixture.json").read_text(encoding="utf-8"))
NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def mk(rows, step=60000):
    return [{"t": i * step, "c": r[0], "oi": r[1], "cvd": r[2] if len(r) > 2 else None} for i, r in enumerate(rows)]


@pytest.mark.parametrize("case", FIX["bar_state"], ids=lambda c: str(c["in"]))
def test_bar_state_matches_fixture(case):
    assert F.bar_state(*case["in"]) == case["out"]


@pytest.mark.parametrize("case", FIX["oi_runs"], ids=lambda c: c["name"])
def test_oi_runs_matches_fixture(case):
    assert F.oi_runs(mk(case["bars"])) == case["out"]


def test_window_matches_fixture():
    w = FIX["window"]
    assert F.window_state(mk(w["bars"]), w["n"]) == w["out"]


def test_python_and_js_agree_on_fixture():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not installed")
    runner = ("const P=require(process.argv[1]);const f=JSON.parse(require('fs').readFileSync(process.argv[2],'utf8'));"
              "const mk=r=>r.map((x,i)=>({t:i*60000,c:x[0],oi:x[1],cvd:x.length>2?x[2]:null}));"
              "console.log(JSON.stringify({s:f.bar_state.map(c=>P.barState(...c.in)),r:f.oi_runs.map(c=>P.oiRuns(mk(c.bars))),w:P.windowState(mk(f.window.bars),f.window.n)}))")
    out = subprocess.run([node, "-e", runner, str(HERE / "flow_chart.js"), str(HERE / "flow_fixture.json")],
                         capture_output=True, text=True, timeout=60, creationflags=NOWIN)
    assert out.returncode == 0, out.stderr[-800:]
    j = json.loads(out.stdout)
    assert j["s"] == [F.bar_state(*c["in"]) for c in FIX["bar_state"]]
    assert j["r"] == [F.oi_runs(mk(c["bars"])) for c in FIX["oi_runs"]]
    assert j["w"] == F.window_state(mk(FIX["window"]["bars"]), FIX["window"]["n"])


def test_parse_trades():
    msg = {"topic": "publicTrade.BTCUSDT", "type": "snapshot", "ts": 1,
           "data": [{"T": 1000, "s": "BTCUSDT", "S": "Buy", "v": "0.5", "p": "70000", "i": "a"},
                    {"T": 2000, "s": "BTCUSDT", "S": "Sell", "v": "2", "p": "69990.5", "i": "b"},
                    {"T": 3000, "S": "Buy", "v": "bad", "p": "1"}, {"T": 4000, "S": "Hold", "v": "1", "p": "1"}]}
    assert F.parse_trades(msg) == [(1000, "buy", 0.5, 70000.0, "a"), (2000, "sell", 2.0, 69990.5, "b")]
    assert F.parse_trades({"op": "pong"}) == [] and F.parse_trades({"topic": "publicTrade.ETHUSDT", "data": msg["data"]}) == []


def test_build_bars_spot_cvd_and_closed_only():
    H = 3_600_000
    kl = [[str(2 * H), "1", "1", "1", "1", "0", "0"], [str(H), "10", "12", "9", "11", "5", "0"], ["0", "1", "1", "1", "1", "0", "0"]]
    oi = [{"openInterest": "500", "timestamp": str(H)}]
    spot = [[0, "0", "0", "0", "0", "0", 0, 0, 0, "0"], [H, "0", "0", "0", "0", "10", 0, 0, 0, "7"], [2 * H, "0", "0", "0", "0", "0", 0, 0, 0, "0"]]
    # delta = 2 x takerBuy - volume = 2 x 7 - 10 = 4
    bars = F.build_bars(kl, oi, spot, H, 2 * H + 1)
    assert [b["t"] for b in bars] == [0, H] and bars[1]["cvd"] == 4 and bars[1]["oi"] == 500 and bars[0]["oi"] is None
    assert F.build_bars(kl, oi, None, H, 2 * H + 1)[1]["cvd"] is None


def test_footprint_hand_arithmetic():
    fp = F.Footprint()
    fp.first_t = 0                                           # collector was already running at the bucket start: not partial
    t0 = 900_000 * 4                                         # 3,600,000: start of a 15 m bucket and of an hour
    fp.add(t0 + 1, "buy", 1.0, 70001.0)                      # price bucket 70000
    fp.add(t0 + 2, "buy", 2.0, 70004.0)                      # 70000 -> 3.0 BTC there
    fp.add(t0 + 3, "sell", 5.0, 69995.0)                     # bucket 69990 -> 5.0 BTC; 5 x 69,995 = 349,975 USD: not large
    fp.add(t0 + 4, "sell", 8.0, 70010.0)                     # 8 x 70,010 = 560,080 USD >= 500,000: large sell, biggest print
    fp.add(t0 + 5, "buy", 8.0, 70020.0)                      # 560,160 USD: large buy
    s = fp.summary(t0, 900_000)
    # delta = 1 + 2 - 5 - 8 + 8 = -2 ; buckets 69990:5, 70000:3, 70010:8, 70020:8 ; tie 70010 / 70020 -> lower price wins
    assert s["delta"] == -2.0 and s["poc"] == 70010 and s["big_btc"] == 8.0 and s["big_side"] == "sell"
    assert (s["large_buy"], s["large_sell"], s["n"]) == (1, 1, 5) and s["partial"] is False
    assert fp.summary(t0 - 900_000, 900_000) is None
    assert fp.summary(t0, 3_600_000)["delta"] == -2.0        # the 1 h window merges its four 15 m buckets
    late = F.Footprint()
    late.first_t = t0 + 10                                   # collector started mid bucket
    late.add(t0 + 10, "buy", 1.0, 70000.0)
    assert late.summary(t0, 900_000)["partial"] is True


def test_fp_line_and_feed_lines():
    fp = F.Footprint()
    fp.add(3_600_000 + 5, "buy", 8.0, 70020.0)
    allfp = F.fp_all(fp, 3_600_000 + 20 * 60000)             # 01:20Z: cur 15 m bucket (01:15) empty, last (01:00) holds the print
    assert allfp["15m"]["cur"] is None and allfp["15m"]["last"]["delta"] == 8.0
    assert allfp["1h"]["cur"]["delta"] == 8.0 and allfp["1h"]["last"] is None
    assert F.fp_line("15m", allfp["15m"]["last"]) == "15m 01:00Z delta +8.0 BTC, POC 70020, biggest 8.00 BTC BUY, large 1 buy / 0 sell (partial)"   # first print came after the bucket start
    feed = F.build_feed(5, [], None, allfp)
    assert feed["fp"]["lines"]["15m"].startswith("15m 01:00Z delta +8.0") and feed["fp"]["t"] == 5 and feed["perp"] is None
    assert F.build_feed(5, [], None, None)["fp"] is None


def _frames(now):
    H = 3_600_000
    rows = FIX["oi_runs"][0]["bars"]
    bars = [{"t": now - (len(rows) - i) * H, "o": r[0], "h": r[0], "l": r[0], "c": r[0], "oi": r[1], "cvd": -1.0} for i, r in enumerate(rows)]
    return {"1h": {"bars": bars, "err": {}}, "30m": {"bars": [], "err": {"spot_kline": "boom"}}, "5m": {"bars": bars[-3:], "err": {}}}


def test_digest_format_fixed_keys_and_limit():
    now = 1_794_600_000_000 // 3_600_000 * 3_600_000 + 60000
    big = [{"t": now - 5 * 60000 * i, "side": "sell" if i % 2 else "buy", "btc": 10, "px": 68410.4, "usd": 1_200_000 + i} for i in range(14)]
    st = F.build_state(_frames(now), big, None, now, False)
    lines = F.digest(st).rstrip("\n").split("\n")
    assert len(lines) <= 30 and all(len(ln) < 200 for ln in lines)
    assert re.fullmatch(r"T \d{4}-\d\d-\d\dT\d\d:\d\dZ \| PX \d+", lines[0])
    last = [ln for ln in lines if ln.startswith("1H LAST")][0]
    assert re.fullmatch(r"1H LAST state=\w+ dpx=[+-]\d+\.\d\d doi=[+-]\d+\.\d\d cvd=[+-]\d+ taker=\w+ bar=\d\d:\d\dZ", last)
    # last bar: price 99.6 -> 99.5 = -0.1004 % -> -0.10, OI 990 -> 985 = -0.5051 % -> -0.51 (hand figures); CVD -1 with price down = agree
    assert "state=FORCED_SELLING" in last and "dpx=-0.10" in last and "doi=-0.51" in last and "taker=agree" in last
    run = [ln for ln in lines if ln.startswith("1H RUN")][0]
    assert re.fullmatch(r"1H RUN kind=UNWIND dir=down bars=6 doi=-2\.7 dpx=-1\.4 from=\d\d:\d\dZ active=1", run)
    assert "30M LAST NOT_IN_DATA" in lines and "30M RUN none" in lines                    # no bars: a dash, never a guess
    bigs = [ln for ln in lines if ln.startswith("BIG ")]
    assert len(bigs) == 10 and re.fullmatch(r"BIG \d\d:\d\dZ (BUY|SELL) \d+\.\dM @68410", bigs[0])
    assert "FP 15M cur NOT_IN_DATA" in lines and "FP 1H last NOT_IN_DATA" in lines
    assert any(ln.startswith("STALE spot_kline_30m ERR") for ln in lines) and "STALE trades_ws not_running" in lines
    assert lines[-1].startswith("NOTE descriptive only")


def test_digest_has_fp_lines_when_collector_runs():
    now = 3_600_000 + 20 * 60000
    fp = F.Footprint()
    fp.add(3_600_000 + 5, "buy", 8.0, 70020.0)
    st = F.build_state({}, [], F.fp_all(fp, now), now, True)
    lines = F.digest(st).split("\n")
    assert any(ln.startswith("FP 15M last 01:00Z delta +8.0 BTC, POC 70020") for ln in lines) and any(ln.startswith("FP 1H cur 01:00Z") for ln in lines)


def test_stale_feed_reads_not_in_data():
    now = 1_794_600_000_000
    old = [{"t": now - 20 * 3_600_000, "c": 100, "oi": 1000, "cvd": 1}, {"t": now - 19 * 3_600_000, "c": 101, "oi": 1010, "cvd": 1}]
    st = F.build_state({"1h": {"bars": old, "err": {}}}, [], None, now, True)
    assert st["tf"]["1h"]["stale"] is True and st["tf"]["1h"]["last"] is None
    assert any(s.startswith("1h last_bar=") for s in st["stale"])
    assert "1H LAST NOT_IN_DATA" in F.digest(st)


def test_runtime_outputs_are_gitignored():
    for p in (F.STATE, F.DIGEST, F.TRADES, F.FEED):
        r = subprocess.run(["git", "check-ignore", "-q", str(p)], cwd=HERE, capture_output=True, creationflags=NOWIN)
        assert r.returncode == 0, p
