"""Tests for the cross-exchange liquidation row (xliq_collector.py, xliq.js, served feed URL).

Sample payloads: the OKX reply shape is a trimmed copy of a real public reply (2026-11-13, JIS-NB); the Bybit and Binance messages are the
documented shapes (docs urls in xliq_collector.py) with round numbers: Bybit's own feed was seen live on 2026-11-13 but this test uses a
round-number copy so hand arithmetic stays checkable; Binance sent no print during the live window, so its sample is the docs example.
Expected numbers are worked out by hand in the comments, not computed by the code under test.
"""
import json
import shutil
import subprocess
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

import pytest

import xliq_collector as X

HERE = Path(__file__).resolve().parent
JS = HERE / "xliq.js"
HTML = HERE / "live_aid.html"
H = 3_600_000
NOW = 1_794_600_000_000

BYBIT_MSG = {"topic": "allLiquidation.BTCUSDT", "type": "snapshot", "ts": NOW,
             "data": [{"T": NOW - 1000, "s": "BTCUSDT", "S": "Buy", "v": "0.5", "p": "71000"},      # long liquidated: 0.5 x 71,000 = 35,500
                      {"T": NOW - 500, "s": "BTCUSDT", "S": "Sell", "v": "0.002", "p": "71100"},   # short liquidated: 142.2
                      {"T": NOW, "s": "BTCUSDT", "S": "Buy", "v": "bad", "p": "71000"}]}           # junk row skipped
BINANCE_MSG = {"e": "forceOrder", "E": 1568014460893, "o": {"s": "BTCUSDT", "S": "SELL", "o": "LIMIT", "f": "IOC", "q": "0.014", "p": "9910", "ap": "9910",
                                                          "X": "FILLED", "l": "0.014", "z": "0.014", "T": 1568014460893}}   # SELL = long liquidated: 0.014 x 9,910 = 138.74
OKX_REPLY = {"code": "0", "data": [{"details": [
    {"bkLoss": "0", "bkPx": "71994.2", "ccy": "", "posSide": "short", "side": "buy", "sz": "10.33", "time": "1794504466008", "ts": "1794504466008"},
    {"bkLoss": "0", "bkPx": "71717.2", "ccy": "", "posSide": "long", "side": "sell", "sz": "1.91", "time": "1794509167426", "ts": "1794509167426"}]}], "msg": ""}


def test_bybit_parse():
    r = X.parse_bybit(BYBIT_MSG)
    assert r == [(NOW - 1000, "long", pytest.approx(35500.0), 71000.0), (NOW - 500, "short", pytest.approx(142.2), 71100.0)]
    assert X.parse_bybit({"op": "pong"}) == [] and X.parse_bybit({"topic": "allLiquidation.ETHUSDT", "data": BYBIT_MSG["data"]}) == []


def test_binance_parse():
    assert X.parse_binance(BINANCE_MSG) == [(1568014460893, "long", pytest.approx(138.74), 9910.0)]
    buy = json.loads(json.dumps(BINANCE_MSG))
    buy["o"]["S"] = "BUY"
    assert X.parse_binance(buy)[0][1] == "short"                       # BUY = short liquidated
    eth = json.loads(json.dumps(BINANCE_MSG))
    eth["o"]["s"] = "ETHUSDT"
    assert X.parse_binance(eth) == [] and X.parse_binance({"e": "aggTrade"}) == []


def test_okx_parse():
    r = X.parse_okx(OKX_REPLY)
    # 10.33 contracts x 0.01 BTC x 71,994.2 = 7,436.99886 ; 1.91 x 0.01 x 71,717.2 = 1,369.80...
    assert r[0] == (1794504466008, "short", pytest.approx(7436.99886, rel=1e-6), 71994.2)
    assert r[1][1] == "long" and r[1][2] == pytest.approx(1.91 * 0.01 * 71717.2, rel=1e-9)
    assert X.parse_okx({"code": "51000"}) == [] and X.parse_okx(None) == []


def test_p99_nearest_rank():
    assert X.p99(list(range(1, 101))) == 99          # n=100: rank ceil(99) = 99
    assert X.p99(list(range(1, 102))) == 100         # n=101: rank ceil(99.99) = 100
    assert X.p99([]) is None


def _ev(n, usd, t0, side="long"):
    return [(t0 - i, side, usd, 71000.0) for i in range(n)]


def test_baseline_building_never_big():
    ev = _ev(300, 100.0, NOW - 20 * 60000) + [(NOW - 60000, "long", 5_000_000.0, 71200.0)]
    s = X.venue_summary(ev, NOW - 3 * 86400_000, NOW)                  # only 3 days of history
    assert s["baseline"] == "building" and s["big"] == 0 and s["p99"] is None and s["have_days"] == 3.0
    assert s["long15"] == 5_000_000 and s["n15"] == 1 and s["max15"] == 5_000_000     # raw sum still shown
    thin = X.venue_summary(_ev(50, 100.0, NOW - 60000), NOW - 8 * 86400_000, NOW)      # 8 days but only 50 prints
    assert thin["baseline"] == "building" and thin["big"] == 0


def test_baseline_ready_marks_big_and_15m_sum():
    old = _ev(150, 100.0, NOW - 2 * 86400_000)                           # 150 prints of $100, 2 days ago
    win = [(NOW - 14 * 60000, "long", 10_000.0, 71000.0), (NOW - 5 * 60000, "short", 40.0, 71050.0), (NOW - 16 * 60000, "long", 99_999.0, 70000.0)]   # last one is outside 15 m
    s = X.venue_summary(old + win, NOW - 8 * 86400_000, NOW)
    # 153 prints in 7 d: sorted = 40, 150 x 100, 10,000, 99,999 -> n=153, rank ceil(151.47)=152 -> 10,000 -> p99 = 10,000
    assert s["baseline"] == "ready" and s["p99"] == 10_000 and s["n7d"] == 153
    assert s["long15"] == 10_000 and s["short15"] == 40 and s["n15"] == 2
    assert s["big"] == 0                                                 # 10,000 is not ABOVE p99 (equal)
    win2 = win + [(NOW - 2 * 60000, "long", 250_000.0, 71234.0)]
    s2 = X.venue_summary(old + win2 + [(NOW - 3 * 60000, "long", 300.0, 71000.0)], NOW - 8 * 86400_000, NOW)
    assert s2["big"] == 1 and s2["bigside"] == "long" and s2["bigpx"] == 71234 and s2["max15"] == 250_000
    assert s2["long15"] == 10_000 + 250_000 + 300


def test_storage_roundtrip_and_dedupe(tmp_path):
    t = [NOW / 1000]
    c = X.Collector(tmp_path / "e.jsonl", tmp_path / "m.json", tmp_path / "f.js", now=lambda: t[0])
    ev = X.parse_okx(OKX_REPLY)
    c.add("OKX", ev)
    c.add("OKX", ev)                                                     # a repeat poll returns the same prints: stored once
    assert len(c.by["OKX"]) == 2
    c.mark_connected("OKX")
    c2 = X.Collector(tmp_path / "e.jsonl", tmp_path / "m.json", tmp_path / "f.js", now=lambda: t[0])   # restart: rebuilt from disk
    assert len(c2.by["OKX"]) == 2 and c2.since["OKX"] == NOW
    X.write_feed(c2.snapshot(), tmp_path / "f.js")
    txt = (tmp_path / "f.js").read_text(encoding="utf-8")
    assert txt.startswith("window.LIVEAID_XLIQ = ") and json.loads(txt[len("window.LIVEAID_XLIQ = "):].rstrip(";\n"))["venues"]["OKX"]["baseline"] == "building"


def test_feed_url_resolves_from_served_root(tmp_path):
    """The :8765 server's root is the live_aid folder: the collector's output and the page's script URL must live inside it (no ../)."""
    assert X.OUT.parent == HERE and "/" not in X.OUT.name
    html = HTML.read_text(encoding="utf-8")
    assert 'src="xliq.js"' in html and 'id="xl-rows"' in html and 'id="xl-sowhat"' in html
    assert "xliq_feed.js" in JS.read_text(encoding="utf-8") and "../" not in JS.read_text(encoding="utf-8").split("s.src = '")[1].split("'")[0]
    existed = X.OUT.exists()
    if not existed:
        X.write_feed({"t": NOW, "venues": {}}, X.OUT)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(HERE)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        base = f"http://127.0.0.1:{srv.server_address[1]}/"
        assert urlopen(base + "xliq_feed.js", timeout=10).status == 200
        assert urlopen(base + "xliq.js", timeout=10).status == 200
    finally:
        srv.shutdown()
        if not existed:
            X.OUT.unlink()


def test_feed_file_is_gitignored_runtime_data():
    out = subprocess.run(["git", "check-ignore", "-q", str(X.OUT)], cwd=HERE, capture_output=True)
    assert out.returncode == 0, "xliq_feed.js must be gitignored (runtime output, public repo)"
    out = subprocess.run(["git", "check-ignore", "-q", str(X.EVENTS)], cwd=HERE, capture_output=True)
    assert out.returncode == 0


# ---- page rules in node ----------------------------------------------------------------------------------------------
NODE = shutil.which("node")
RUNNER = "const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(P[j.fn].apply(null,j.a)))})"


def _js(fn, *a):
    out = subprocess.run([NODE, "-e", RUNNER, str(JS)], input=json.dumps({"fn": fn, "a": list(a)}), capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert out.returncode == 0, out.stderr[-1500:]
    return json.loads(out.stdout)


def _v(**k):
    d = {"long15": 0, "short15": 0, "n15": 0, "max15": 0, "maxside": None, "p99": None, "baseline": "building", "have_days": 1.5, "n7d": 40,
         "big": 0, "bigside": None, "bigpx": None, "err": ""}
    d.update(k)
    return d


US = 1_794_661_800_000   # 2026-11-14 12:30Z -> not US; use 15Z below
US15 = 1_794_668_400_000


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_building_never_shows_big_even_if_feed_claims_it():
    feed = {"t": US15, "venues": {"BYBIT": _v(big=3, bigside="long", bigpx=71234, long15=9e6), "BINANCE": _v(), "OKX": _v()}}
    rs = _js("rows", feed, US15)
    assert [r["big"] for r in rs] == [0, 0, 0] and "baseline building (1.5 of 7 d, 40 prints)" == rs[0]["bigNote"]
    sw = _js("soWhat", feed, US15)
    assert "BIG" not in sw.replace("marked BIG", "") and "baseline building" in sw and "Read: WAIT" in sw


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_big_long_liquidations_so_what_names_venues_price_and_us_session():
    big = dict(baseline="ready", have_days=7.2, n7d=900, p99=20000, big=2, bigside="long", bigpx=71234, long15=3_100_000, n15=40, max15=900_000)
    feed = {"t": US15, "venues": {"BYBIT": _v(**big), "BINANCE": _v(baseline="ready", have_days=7.2, n7d=500, p99=50000), "OKX": _v(**dict(big, bigpx=71290))}}
    rs = _js("rows", feed, US15 + 5000)
    assert rs[0]["big"] == 2 and rs[0]["bigNote"] == "BIG x2" and rs[1]["bigNote"] == "no (p99 $50k)"
    sw = _js("soWhat", feed, US15 + 5000)
    assert sw.startswith("So what: big long liquidations on Bybit+OKX at 71,2xx (US session) = forced selling, watch for absorption")
    assert _js("usd", 3_100_000) == "$3.10M" and _js("pxLabel", 71234.9) == "71,2xx"


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_stale_or_missing_feed_fails_closed():
    feed = {"t": US15 - 200_000, "venues": {"BYBIT": _v(baseline="ready", big=1, bigside="long")}}
    rs = _js("rows", feed, US15)
    assert rs[0]["state"] == "stale" and "big" not in rs[0]
    assert "no liquidation data" in _js("soWhat", feed, US15) and "no liquidation data" in _js("soWhat", None, US15)
