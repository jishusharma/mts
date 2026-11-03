"""Spec tests for live_aid flow feeds and indicators (REQUIREMENTS.md R08, R17).

Functions tested:
  - liqDeribit(x, t)
  - liqBybit(x)
  - liqBinance(m)
  - liqSum(ev, now, ms)
  - fundRead(r)
  - premium(mark, idx)
  - bybitTick(prev, msg)
  - foldBars(rows, ms, dayAlign)

Node-backed spec tests execute live_aid_indicators.js directly through node.
Supports LIVE_AID_JS_PATH env var to verify scratch mutations against copies.
"""
import json
import os
import shutil
from pathlib import Path
import pytest
import subprocess

HERE = Path(__file__).resolve().parent
DEFAULT_JS = HERE / "live_aid_indicators.js"


def get_js_path():
    override = os.environ.get("LIVE_AID_JS_PATH")
    if override:
        return Path(override)
    return DEFAULT_JS


def run_js_calls(calls, js_path=None):
    """Execute a list of function calls against the JS file via node.
    Each call is a dict: {'fn': '<name>', 'args': [<arg1>, ...]}
    Returns list of return values.
    """
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed or not on PATH")

    target = js_path or get_js_path()
    assert target.exists(), f"Target JS file not found: {target}"

    runner_js = r"""
const fs = require('fs');
const jsCode = fs.readFileSync(process.argv[1], 'utf8');
const m = {exports: {}};
new Function('module', 'exports', jsCode)(m, m.exports);
const api = m.exports;

const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const results = payload.map(call => {
    const fn = api[call.fn];
    if (typeof fn !== 'function') {
        throw new Error('Function not found: ' + call.fn);
    }
    return fn.apply(null, call.args || []);
});
process.stdout.write(JSON.stringify(results));
"""
    proc = subprocess.run(
        [node, "-e", runner_js, str(target)],
        input=json.dumps(calls),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Node execution failed (code {proc.returncode}):\n{proc.stderr}")
    return json.loads(proc.stdout)


def call_js(fn, *args, js_path=None):
    return run_js_calls([{"fn": fn, "args": list(args)}], js_path=js_path)[0]


def test_liq_binance_side_and_usd():
    """Binance SELL indicates long liquidated; BUY indicates short liquidated.
    USD is computed as quantity * average price (+o.q * +o.ap).
    """
    # SELL -> long liquidated
    m_sell = {"o": {"T": 1700000001000, "S": "SELL", "q": "2.5", "ap": "60000.0"}}
    res_sell = call_js("liqBinance", m_sell)
    assert res_sell["venue"] == "BINANCE"
    assert res_sell["side"] == "long"
    assert res_sell["t"] == 1700000001000
    assert res_sell["px"] == 60000.0
    assert res_sell["usd"] == 150000.0

    # BUY -> short liquidated
    m_buy = {"o": {"T": 1700000002000, "S": "BUY", "q": "1.2", "ap": "50000.0"}}
    res_buy = call_js("liqBinance", m_buy)
    assert res_buy["venue"] == "BINANCE"
    assert res_buy["side"] == "short"
    assert res_buy["t"] == 1700000002000
    assert res_buy["px"] == 50000.0
    assert res_buy["usd"] == 60000.0


def test_liq_bybit_side_and_usd():
    """Bybit Buy indicates long liquidated; Sell indicates short liquidated
    (per live_aid_indicators.js and STEPS.md line 60 SOURCED venue docs).
    USD is computed as volume * price (+x.v * +x.p).
    """
    # Buy -> long liquidated
    x_buy = {"T": 1700000003000, "S": "Buy", "v": "3.0", "p": "40000.0"}
    res_buy = call_js("liqBybit", x_buy)
    assert res_buy["venue"] == "BYBIT"
    assert res_buy["side"] == "long"
    assert res_buy["t"] == 1700000003000
    assert res_buy["px"] == 40000.0
    assert res_buy["usd"] == 120000.0

    # Sell -> short liquidated
    x_sell = {"T": 1700000004000, "S": "Sell", "v": "0.5", "p": "70000.0"}
    res_sell = call_js("liqBybit", x_sell)
    assert res_sell["venue"] == "BYBIT"
    assert res_sell["side"] == "short"
    assert res_sell["t"] == 1700000004000
    assert res_sell["px"] == 70000.0
    assert res_sell["usd"] == 35000.0


def test_liq_deribit_side_mapping_and_types():
    """Deribit liquidation trade mapping:
    - Liquidation T (taker): direction 'sell' -> long liquidated; 'buy' -> short liquidated.
    - Liquidation M (maker): direction 'sell' -> short liquidated; 'buy' -> long liquidated.
    - Liquidation MT: produces two events (taker then maker).
    - Amount is already in USD.
    - Missing or non-liquidation returns empty array.
    """
    ts = 1700000005000
    # Taker sell -> long
    t_sell = {"liquidation": "T", "direction": "sell", "amount": 50000, "price": 68000}
    res_t_sell = call_js("liqDeribit", t_sell, ts)
    assert len(res_t_sell) == 1
    assert res_t_sell[0]["venue"] == "DERIBIT"
    assert res_t_sell[0]["side"] == "long"
    assert res_t_sell[0]["usd"] == 50000
    assert res_t_sell[0]["px"] == 68000
    assert res_t_sell[0]["t"] == ts

    # Taker buy -> short
    t_buy = {"liquidation": "T", "direction": "buy", "amount": 25000, "price": 68500}
    res_t_buy = call_js("liqDeribit", t_buy, ts)
    assert len(res_t_buy) == 1
    assert res_t_buy[0]["side"] == "short"
    assert res_t_buy[0]["usd"] == 25000

    # Maker sell -> short
    m_sell = {"liquidation": "M", "direction": "sell", "amount": 10000, "price": 69000}
    res_m_sell = call_js("liqDeribit", m_sell, ts)
    assert len(res_m_sell) == 1
    assert res_m_sell[0]["side"] == "short"

    # Maker buy -> long
    m_buy = {"liquidation": "M", "direction": "buy", "amount": 15000, "price": 69100}
    res_m_buy = call_js("liqDeribit", m_buy, ts)
    assert len(res_m_buy) == 1
    assert res_m_buy[0]["side"] == "long"

    # Dual MT sell -> 2 events: taker (long) and maker (short)
    mt_sell = {"liquidation": "MT", "direction": "sell", "amount": 30000, "price": 68000}
    res_mt = call_js("liqDeribit", mt_sell, ts)
    assert len(res_mt) == 2
    assert res_mt[0]["side"] == "long"
    assert res_mt[1]["side"] == "short"

    # Normal trade without liquidation flag
    normal = {"direction": "sell", "amount": 50000, "price": 68000}
    assert call_js("liqDeribit", normal, ts) == []
    assert call_js("liqDeribit", {}, ts) == []


def test_liq_sum_window_edges():
    """liqSum window inclusion: e.t <= now && now - e.t <= ms.
    Includes events strictly at now and exact boundary (now - ms),
    excludes events older than now - ms and future events.
    """
    now = 1000000
    ms = 60000

    events = [
        {"t": now, "side": "long", "usd": 1000},          # at now -> included
        {"t": now - ms, "side": "short", "usd": 2000},    # at lower boundary -> included
        {"t": now - ms - 1, "side": "long", "usd": 5000}, # 1ms outside -> excluded
        {"t": now + 1, "side": "short", "usd": 8000},     # future -> excluded
    ]
    res = call_js("liqSum", events, now, ms)
    assert res["n"] == 2
    assert res["long"] == 1000
    assert res["short"] == 2000


def test_liq_sum_dominance_and_big_threshold():
    """liqSum computes dominance (longs, shorts, mixed, none) and counts big orders (>= 100000 USD)."""
    now = 1000000
    ms = 60000

    # 1. Empty events -> dom = none
    assert call_js("liqSum", [], now, ms) == {"long": 0, "short": 0, "n": 0, "big": 0, "dom": "none"}

    # 2. Big threshold (LQ.bigUsd = 100000)
    ev_big = [
        {"t": now - 10, "side": "long", "usd": 99999},   # sub-threshold
        {"t": now - 20, "side": "long", "usd": 100000},  # exact threshold
        {"t": now - 30, "side": "long", "usd": 250000},  # above threshold
    ]
    res_big = call_js("liqSum", ev_big, now, ms)
    assert res_big["n"] == 3
    assert res_big["big"] == 2

    # 3. Dominance ratios (LQ.domRatio = 2)
    # Long dominance: long >= 2 * short
    ev_long_dom = [
        {"t": now - 10, "side": "long", "usd": 200000},
        {"t": now - 20, "side": "short", "usd": 100000},
    ]
    assert call_js("liqSum", ev_long_dom, now, ms)["dom"] == "longs"

    # Short dominance: short >= 2 * long
    ev_short_dom = [
        {"t": now - 10, "side": "long", "usd": 100000},
        {"t": now - 20, "side": "short", "usd": 200000},
    ]
    assert call_js("liqSum", ev_short_dom, now, ms)["dom"] == "shorts"

    # Mixed: neither >= 2x the other
    ev_mixed = [
        {"t": now - 10, "side": "long", "usd": 150000},
        {"t": now - 20, "side": "short", "usd": 100000},
    ]
    assert call_js("liqSum", ev_mixed, now, ms)["dom"] == "mixed"


def test_fund_read_pct_annual_and_side():
    """fundRead converts 8h rate to pct8h and annual, classifies side and high flags."""
    # Positive rate: 0.0001 (0.01% per 8h)
    r1 = call_js("fundRead", 0.0001)
    assert pytest.approx(r1["pct8h"], rel=1e-5) == 0.01
    assert pytest.approx(r1["annual"], rel=1e-5) == 10.95  # 0.0001 * 1095 * 100
    assert r1["side"] == "longs"
    assert r1["high"] is False

    # High positive rate: 0.0003 (0.03% threshold)
    r_high = call_js("fundRead", 0.0003)
    assert pytest.approx(r_high["pct8h"], rel=1e-5) == 0.03
    assert pytest.approx(r_high["annual"], rel=1e-5) == 32.85
    assert r_high["side"] == "longs"
    assert r_high["high"] is True

    # Negative rate: -0.0002 (-0.02% per 8h)
    r_neg = call_js("fundRead", -0.0002)
    assert pytest.approx(r_neg["pct8h"], rel=1e-5) == -0.02
    assert pytest.approx(r_neg["annual"], rel=1e-5) == -21.9
    assert r_neg["side"] == "shorts"
    assert r_neg["high"] is False

    # Near zero rate: |r| < 0.00001 (FD.zero)
    r_zero = call_js("fundRead", 0.000005)
    assert r_zero["side"] == "zero"
    assert r_zero["high"] is False

    r_flat = call_js("fundRead", 0)
    assert r_flat["side"] == "zero"
    assert r_flat["pct8h"] == 0
    assert r_flat["annual"] == 0


def test_fund_read_falsy_and_malformed():
    """fundRead returns null for null, undefined, empty string, or non-finite inputs."""
    assert call_js("fundRead", None) is None
    assert call_js("fundRead", "") is None
    assert call_js("fundRead", "invalid_num") is None
    # String numbers are parsed correctly
    r_str = call_js("fundRead", "0.0001")
    assert pytest.approx(r_str["pct8h"], rel=1e-5) == 0.01
    assert r_str["side"] == "longs"


def test_premium_pts_and_bps():
    """premium calculates mark-index difference in points (pts) and basis points (bps)."""
    # Premium: mark > index
    p_pos = call_js("premium", 68100, 68000)
    assert pytest.approx(p_pos["pts"], rel=1e-6) == 100.0
    assert pytest.approx(p_pos["bps"], rel=1e-6) == 14.70588235  # (100 / 68000) * 10000

    # Discount: mark < index
    p_neg = call_js("premium", 67500, 68000)
    assert pytest.approx(p_neg["pts"], rel=1e-6) == -500.0
    assert pytest.approx(p_neg["bps"], rel=1e-6) == -73.52941176

    # Parity: mark == index
    p_flat = call_js("premium", 68000, 68000)
    assert p_flat["pts"] == 0
    assert p_flat["bps"] == 0


def test_premium_zero_and_invalid():
    """premium returns null when mark or idx is not finite, or when idx is 0."""
    assert call_js("premium", 68000, 0) is None
    assert call_js("premium", "not_a_number", 68000) is None
    assert call_js("premium", 68000, "not_a_number") is None
    assert call_js("premium", None, 68000) is not None  # Note: In JS +null is 0, pts is -68000, but idx != 0
    assert call_js("premium", 68000, None) is None      # +null is 0, !+idx triggers null return


def test_bybit_tick_snapshot_vs_delta():
    """bybitTick replaces state entirely on snapshot; merges fields on delta."""
    prev_state = {
        "symbol": "BTCUSDT",
        "lastPrice": "68000",
        "turnover24h": "1000000",
        "openInterest": "5000",
    }

    # Snapshot ignores prev_state and returns exactly new payload data
    msg_snap = {
        "type": "snapshot",
        "data": {
            "symbol": "BTCUSDT",
            "lastPrice": "68500",
        },
    }
    snap_res = call_js("bybitTick", prev_state, msg_snap)
    assert snap_res == {"symbol": "BTCUSDT", "lastPrice": "68500"}
    assert "openInterest" not in snap_res

    # Delta overlays new fields on top of prev_state
    msg_delta = {
        "type": "delta",
        "data": {
            "lastPrice": "68100",
            "openInterest": "5050",
        },
    }
    delta_res = call_js("bybitTick", prev_state, msg_delta)
    assert delta_res["symbol"] == "BTCUSDT"
    assert delta_res["turnover24h"] == "1000000"
    assert delta_res["lastPrice"] == "68100"
    assert delta_res["openInterest"] == "5050"

    # Delta with empty prev
    assert call_js("bybitTick", None, msg_delta) == {"lastPrice": "68100", "openInterest": "5050"}

    # Missing msg.data
    assert call_js("bybitTick", prev_state, {"type": "delta"}) == prev_state


def test_fold_bars_ohlcv_aggregation():
    """foldBars aggregates 1m bars into longer timeframe buckets (OHLCV)."""
    # Base timestamp divisible by 120000 (2m)
    t0 = 1700006400000  # 2023-11-14 20:00:00 UTC (divisible by 86400000, 120000, etc.)
    ms_2m = 120000

    # Two 1m bars within the first 2m bucket
    bar1 = [t0, 100.0, 105.0, 98.0, 102.0, 10.0]
    bar2 = [t0 + 60000, 102.0, 110.0, 95.0, 108.0, 15.0]

    # One 1m bar in the second 2m bucket
    bar3 = [t0 + 120000, 108.0, 112.0, 107.0, 111.0, 20.0]

    rows = [bar1, bar2, bar3]
    folded = call_js("foldBars", rows, ms_2m, False)

    assert len(folded) == 2

    # First bucket check [t, o, h, l, c, v]
    b1 = folded[0]
    assert b1[0] == t0
    assert b1[1] == 100.0   # open from bar1
    assert b1[2] == 110.0   # max(105, 110)
    assert b1[3] == 95.0    # min(98, 95)
    assert b1[4] == 108.0   # close from bar2
    assert b1[5] == 25.0    # 10 + 15

    # Second bucket check
    b2 = folded[1]
    assert b2[0] == t0 + 120000
    assert b2[1] == 108.0
    assert b2[2] == 112.0
    assert b2[3] == 107.0
    assert b2[4] == 111.0
    assert b2[5] == 20.0

    # Empty rows input
    assert call_js("foldBars", [], ms_2m, True) == []


def test_fold_bars_day_align_utc_midnight():
    """foldBars dayAlign ensures buckets align to UTC midnight (00:00:00 UTC).
    Critical for 7m folding (1440 min / 7 is not an integer).
    """
    DAY = 86400000
    ms_7m = 7 * 60000  # 420000 ms

    # t_mid is an exact UTC midnight: 1700006400000 % 86400000 == 0
    t_mid = 1700006400000
    assert t_mid % DAY == 0

    # If dayAlign is True: bucket at t_mid starts exactly at t_mid
    row_at_mid = [t_mid, 100, 101, 99, 100, 5]
    row_plus_6m = [t_mid + 360000, 100, 102, 98, 101, 8]  # still in 0-7m bucket
    row_plus_7m = [t_mid + 420000, 101, 103, 100, 102, 12] # starts 7-14m bucket

    folded_aligned = call_js("foldBars", [row_at_mid, row_plus_6m, row_plus_7m], ms_7m, True)
    assert len(folded_aligned) == 2
    assert folded_aligned[0][0] == t_mid
    assert folded_aligned[1][0] == t_mid + ms_7m

    # If dayAlign is False: bucket counts from 1970 Unix epoch, so t_mid is not a bucket start
    # because t_mid % 420000 != 0 (remainder is 120000)
    assert t_mid % ms_7m != 0
    folded_unaligned = call_js("foldBars", [row_at_mid], ms_7m, False)
    assert folded_unaligned[0][0] != t_mid
    assert folded_unaligned[0][0] == t_mid - (t_mid % ms_7m)
