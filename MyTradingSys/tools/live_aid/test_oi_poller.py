"""Tests for oi_poller.py (per-venue parse to BTC, stale snapshot, one venue timing out, no leftover state) and doh_http.py.

Recorded replies are trimmed copies of real public replies captured 2026-11-10 (JIS-NB). BitMEX answers 403 from India, so its
reply is the documented XBTUSDT instrument shape with round numbers (not a recording). Expected BTC numbers are worked out by hand
in the comments from the venue's contract-size rule, not computed by the code under test.
"""
import json
import shutil
import subprocess
import threading
import time
from pathlib import Path

import pytest

import oi_poller as P

HERE = Path(__file__).resolve().parent
IND = HERE / "live_aid_indicators.js"

# url substring -> recorded reply
REPLIES = {
    "fapi.binance.com/fapi/v1/openInterest": {"symbol": "BTCUSDT", "openInterest": "98848.170", "time": 1794293105787},
    "fapi.binance.com/fapi/v1/premiumIndex": {"symbol": "BTCUSDT", "markPrice": "74665.20915217", "indexPrice": "74697.47"},
    "okx.com/api/v5/public/open-interest": {"code": "0", "data": [{"instId": "BTC-USDT-SWAP", "oi": "3498616.08", "oiCcy": "34986.1608", "ts": "1794293112316"}], "msg": ""},
    "okx.com/api/v5/market/ticker": {"code": "0", "data": [{"instId": "BTC-USDT-SWAP", "last": "74659.2", "askPx": "74659.2"}], "msg": ""},
    "bitget.com/api/v2/mix/market/open-interest": {"code": "00000", "data": {"openInterestList": [{"symbol": "BTCUSDT", "size": "37338.0005"}], "ts": "1794293113340"}},
    "bitget.com/api/v2/mix/market/ticker": {"code": "00000", "data": [{"symbol": "BTCUSDT", "lastPr": "74656.5", "markPrice": "74658.1"}]},
    "bitmex.com/api/v1/instrument": [{"symbol": "XBTUSD", "openInterest": 5, "markPrice": 1.0, "underlyingToPositionMultiplier": None},
                                     {"symbol": "XBTUSDT", "openInterest": 123456789, "underlyingToPositionMultiplier": 1000000, "markPrice": 74600.5}],
    "futures.kraken.com/derivatives/api/v3/tickers": {"result": "success", "tickers": [{"symbol": "PF_ETHUSD", "openInterest": 99999.0, "markPrice": 2000.0},
                                                       {"symbol": "PF_XBTUSD", "openInterest": 2523.3389, "markPrice": 74595.18885718715}]},
    "bingx.com/openApi/swap/v2/quote/openInterest": {"code": 0, "msg": "", "data": {"openInterest": "1066922682.0", "symbol": "BTC-USDT", "time": 1794293115133}},
    "bingx.com/openApi/swap/v2/quote/price": {"code": 0, "msg": "", "data": {"symbol": "BTC-USDT", "price": "74657.2", "time": 1794293115334}},
    "hbdm.com/linear-swap-api/v1/swap_open_interest": {"status": "ok", "data": [{"volume": 15189125, "amount": 15189.125, "symbol": "BTC", "contract_code": "BTC-USDT"}]},
    "hbdm.com/linear-swap-ex/market/detail/merged": {"status": "ok", "tick": {"close": "74684.1", "vol": "6026244"}},
    "contract.mexc.com/api/v1/contract/ticker": {"success": True, "data": {"symbol": "BTC_USDT", "lastPrice": 74660.6, "holdVol": 650786003}},
    "contract.mexc.com/api/v1/contract/detail": {"success": True, "data": {"symbol": "BTC_USDT", "contractSize": 0.0001, "baseCoin": "BTC"}},
}

# Hand-computed BTC open interest and the price each parser must return
EXPECT = {
    "BINANCE": (98848.170, 74665.20915217),             # openInterest is already BTC
    "OKX": (34986.1608, 74659.2),                       # oiCcy is BTC (3498616.08 contracts x ctVal 0.01 = 34986.1608)
    "BITGET": (37338.0005, 74656.5),                    # size is BTC
    "BITMEX": (123.456789, 74600.5),                    # 123456789 contracts / 1,000,000 per BTC
    "KRAKEN": (2523.3389, 74595.18885718715),           # PF_XBTUSD OI is BTC; the ETH row must be ignored
    "BINGX": (14290.954951, 74657.2),                   # 1,066,922,682 USDT / 74,657.2 = 14,290.95495...
    "HTX": (15189.125, 74684.1),                        # amount is BTC (15,189,125 contracts x 0.001)
    "MEXC": (65078.6003, 74660.6),                      # 650,786,003 contracts x 0.0001 BTC
}


def fake_fetch(overrides=None):
    overrides = overrides or {}

    def f(url, pinned):
        for frag, r in list(overrides.items()) + [kv for kv in REPLIES.items() if kv[0] not in overrides]:
            if frag in url:
                if callable(r):
                    return r()
                return json.loads(json.dumps(r))
        raise AssertionError("unexpected url " + url)
    return f


@pytest.mark.parametrize("name", sorted(EXPECT))
def test_each_venue_reply_parses_to_hand_computed_btc(name):
    out = P.poll_venue(name, fake_fetch(), lambda: 1000.0)
    btc, px = EXPECT[name]
    assert out["err"] == ""
    assert out["btc"] == pytest.approx(btc, rel=1e-9, abs=1e-6)
    assert out["px"] == pytest.approx(px, rel=1e-12)
    assert out["t"] == 1000000


def test_all_eight_venues_are_covered():
    assert set(P.VENUES) == set(EXPECT) == {"BINANCE", "OKX", "BITGET", "BITMEX", "KRAKEN", "BINGX", "HTX", "MEXC"}
    for _pinned, urls, _p in P.VENUES.values():
        for u in urls.values():
            assert u.startswith("https://")
            for bad in ("order", "account", "balance", "position/", "apiKey", "signature"):
                assert bad not in u


def test_garbage_or_zero_reply_is_not_a_number():
    z = {"fapi.binance.com/fapi/v1/openInterest": {"openInterest": "0"}}
    o = P.poll_venue("BINANCE", fake_fetch(z), lambda: 1.0)
    assert o["btc"] is None and o["t"] is None and "implausible" in o["err"]
    g = {"okx.com/api/v5/public/open-interest": {"code": "50011", "data": [], "msg": "rate limit"}}
    o = P.poll_venue("OKX", fake_fetch(g), lambda: 1.0)
    assert o["btc"] is None and o["err"].startswith("IndexError")


def test_one_venue_timing_out_does_not_kill_the_poll():
    gate = threading.Event()
    slow = {"api.bitget.com/api/v2/mix/market/open-interest": lambda: gate.wait(30) and {}}
    boom = {"okx.com/api/v5/public/open-interest": lambda: (_ for _ in ()).throw(TimeoutError("timed out"))}
    t0 = time.time()
    try:
        snap = P.poll_once(fetch=fake_fetch({**slow, **boom}), deadline=1.0)
    finally:
        gate.set()
    assert time.time() - t0 < 5
    v = snap["venues"]
    assert v["BITGET"]["btc"] is None and "timeout" in v["BITGET"]["err"]
    assert v["OKX"]["btc"] is None and "TimeoutError" in v["OKX"]["err"]
    for n in ("BINANCE", "BITMEX", "KRAKEN", "BINGX", "HTX", "MEXC"):
        assert v[n]["btc"] == pytest.approx(EXPECT[n][0], abs=1e-6), n


def test_write_is_atomic_and_leaves_no_temp_file(tmp_path):
    out = tmp_path / "live_aid" / "oi_snapshot.js"
    snap = P.poll_once(fetch=fake_fetch(), now=lambda: 2000.0)
    P.write_snapshot(snap, out)
    txt = out.read_text(encoding="utf-8")
    assert txt.startswith("window.LIVEAID_OI_SNAP = ") and txt.rstrip().endswith(";")
    body = json.loads(txt[len("window.LIVEAID_OI_SNAP = "):].rstrip().rstrip(";"))
    assert body["t"] == 2000000 and body["venues"]["MEXC"]["btc"] == pytest.approx(65078.6003)
    # a failing write keeps the old file and leaves nothing behind
    with pytest.raises(TypeError):
        P.write_snapshot({"t": object()}, out)
    assert out.read_text(encoding="utf-8") == txt
    assert [p.name for p in out.parent.iterdir()] == ["oi_snapshot.js"]


def test_restart_carries_no_state_from_the_previous_run(tmp_path):
    out = tmp_path / "oi_snapshot.js"
    P.write_snapshot(P.poll_once(fetch=fake_fetch(), now=lambda: 1.0), out)
    dead = {"contract.mexc.com/api/v1/contract/ticker": lambda: (_ for _ in ()).throw(OSError("down"))}
    s2 = P.poll_once(fetch=fake_fetch(dead), now=lambda: 99.0)   # same out file exists, must not be read back
    assert s2["venues"]["MEXC"]["btc"] is None and s2["venues"]["MEXC"]["t"] is None
    assert s2["venues"]["OKX"]["t"] == 99000
    assert not any(p.suffix == ".tmp" for p in tmp_path.iterdir())


NODE = shutil.which("node")


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_page_maths_ignores_a_stale_or_broken_snapshot():
    js = r"""
const A = require(process.argv[1]); const now = 1000000;
const v = (t, btc, px) => ({ t: t, btc: btc, px: px, err: '' });
const snap = { t: now, venues: { OKX: v(now - 59000, 100, 70000), HTX: v(now - 60000, 100, 70000), MEXC: v(now - 120000, 100, 70000),
  BITGET: v(now - 1000, 0, 70000), BINGX: v(now - 1000, 5, null), KRAKEN: { t: null, btc: null, px: null, err: 'down' },
  BINANCE: v(now + 600000, 100, 70000), BITMEX: v(now - 2000, 7, 71000) } };
console.log(JSON.stringify({ fresh: A.oiSnapFresh(snap, now, 60000), none: A.oiSnapFresh(null, now, 60000), bad: A.oiSnapFresh({}, now, 60000), junk: A.oiSnapFresh('x', now, 60000) }));
"""
    r = subprocess.run([NODE, "-e", js, str(IND)], capture_output=True, text=True, check=True)
    o = json.loads(r.stdout)
    assert o["fresh"] == {"OKX": {"btc": 100, "px": 70000, "t": 941000}, "BITMEX": {"btc": 7, "px": 71000, "t": 998000}}
    assert o["none"] == {} and o["bad"] == {} and o["junk"] == {}


# ---- doh_http: host-agnostic resolver ----------------------------------------------------------------------------------
def test_doh_resolves_any_host_and_rejects_block_and_private_ips():
    from MyTradingSys.runtime import doh_http as D
    D.clear_cache()
    calls = []

    def fetch(provider, host):
        calls.append((provider, host))
        return [("49.44.79.236", 60), ("10.0.0.5", 60), ("127.0.0.1", 60), ("104.18.2.3", 60)] if provider == "cloudflare" else [("104.18.9.9", 60)]
    assert D.resolve_any("open-api.bingx.com", fetch=fetch, system=lambda h: []) == ["104.18.2.3"]
    assert D.resolve_any("open-api.bingx.com", fetch=fetch, system=lambda h: []) == ["104.18.2.3"]   # cached
    assert len(calls) == 1

    D.clear_cache()
    only_bad = lambda p, h: [("49.44.79.236", 60)]   # noqa: E731
    with pytest.raises(D.DohError):
        D.resolve_any("www.okx.com", fetch=only_bad, system=lambda h: ["49.44.79.236"])
    D.clear_cache()


def test_binance_doh_public_api_is_unchanged():
    from MyTradingSys.runtime import binance_doh as B
    for n in ("resolve", "urlopen", "is_binance_host", "clear_cache", "parse_dns_json", "DohError", "DohHTTPSConnection"):
        assert hasattr(B, n), n
    assert B.is_binance_host("fapi.binance.com") and not B.is_binance_host("www.okx.com")
