"""
Adapters that turn already-built layer modules into live-runner layer functions `fn(bars) -> [event]`.

Every event returned here has:
  "t"     bar OPEN time (ms) of the signal bar (live_runner_core/alert_emitter turn it into "t_close")
  "event" a name that is unique per (t, distinct signal) - alert_emitter dedups on (t, event)
  "side"  "long" | "short", derived from the layer's own event semantics (mapping documented per adapter)
The auto-trader trades any alert with a "side" field. Alert-only: no orders, no keys, stdlib only.
Bars are closed Binance klines {t,o,h,l,c,v,tbv}. Parameters are the module defaults or the values
the backtests used (cited per adapter).
"""

import json
import urllib.parse
import urllib.request

from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_regime, malkan_setup_bull, malkan_setup_bear
from MyTradingSys.backtest.layers.fabio.fabio_escalation import escalation_events
from MyTradingSys.backtest.layers.fabio.fabio_volume_fvg import (
    swing_legs, build_profile, value_area, lowest_volume_level,
)
from MyTradingSys.backtest.layers.session.session_momentum import session_momentum_events
from MyTradingSys.backtest.layers.positioning.funding_cvd_fade import funding_cvd_fade_events
from MyTradingSys.backtest.layers.cryptocred.cc_setups import (
    setup1_sr_flip, setup2_fib_pullback, setup3_failed_msb_reversal,
)


def escalation_layer(bars):
    """Side = the module's own: breakout in the aggressor's direction (up -> long, down -> short).
    Params: module defaults (left/right 2, tol 0.001, k 2.0, lookback 20; run_backtest ESCALATION_GRID includes them)."""
    out = []
    for e in escalation_events(bars):
        out.append({**e, "t": bars[e["i"]]["t"], "event": "%s_%s_%s" % (e["kind"], e["side"], e["level_price"])})
    return out


def volume_fvg_layer(bars, n_bins=20):
    """Mirrors fabio/run_backtest.py run_fvg (real lowest-volume level in the 70% value area of each swing leg;
    first touch of that level within 200 bars of leg confirmation). Side as in the backtest: price at leg
    confirmation above the level -> "short", else "long". n_bins=20, VA 70% = backtest values."""
    legs = swing_legs(bars, left=2, right=2, use_body=True)
    closes = [b["c"] for b in bars]
    out = []
    for leg in legs:
        a_i, b_i = min(leg["a_i"], leg["b_i"]), max(leg["a_i"], leg["b_i"])
        if b_i - a_i < n_bins:
            continue
        try:
            profile = build_profile(bars, a_i, b_i, n_bins=n_bins)
            lvl = lowest_volume_level(profile, value_area(profile, pct=0.70))
        except ValueError:
            continue
        start = leg["confirmed_i"]
        mid = (lvl["price_lo"] + lvl["price_hi"]) / 2.0
        for i in range(start, min(start + 200, len(bars) - 1)):
            if bars[i]["l"] <= mid <= bars[i]["h"]:
                side = "short" if closes[start] > mid else "long"
                out.append({"t": bars[i]["t"], "side": side, "level": round(mid, 2),
                            "event": "fvg_touch_%s_%s" % (side, round(mid, 2))})
                break
    return sorted(out, key=lambda e: e["t"])


def session_momentum_layer(bars):
    """15m bars. Side = sign of the first-30-min return of the UTC day (>0 long, <0 short), entered on the
    bar closing at +30 min. Params: module defaults (session_start 0, first_min 30, entry_min 30, min_abs 0),
    bar_min=15 to match the tf. Source: Shen/Urquhart/Wang 2022 (module docstring)."""
    out = []
    for e in session_momentum_events(bars, bar_min=15):
        out.append({"t": bars[e["i"]]["t"], "side": e["side"], "r_first": e["r_first"],
                    "event": "session_momentum"})
    return out


def default_fetch_funding(symbol, limit):
    """Public GET fapi/v1/fundingRate -> [(fundingTime_ms, rate_float)] ascending. Real network; not unit-tested."""
    url = "https://fapi.binance.com/fapi/v1/fundingRate?" + urllib.parse.urlencode(
        {"symbol": symbol, "limit": limit})
    with urllib.request.urlopen(url, timeout=10) as resp:
        raw = json.loads(resp.read())
    return sorted((int(r["fundingTime"]), float(r["fundingRate"])) for r in raw)


def make_funding_layer(fetch_funding=None, symbol="BTCUSDT", limit=200):
    """1h bars. Side fades the crowded side: bearish CVD/price divergence + funding percentile >= 0.95 -> short;
    bullish divergence + percentile <= 0.05 -> long. Params: module defaults (lookback 90, n 20, hi .95, lo .05)."""
    fetch = fetch_funding or default_fetch_funding

    def fn(bars):
        funding = fetch(symbol, limit)
        out = []
        for e in funding_cvd_fade_events(bars, funding):
            out.append({"t": bars[e["i"]]["t"], "side": e["side"], "funding_pct": e["funding_pct"],
                        "event": "funding_fade_%s" % e["div"]})
        return out
    return fn


def _malkan_signals(bars, fn, event_name):
    if len(bars) <= 14:  # rsi_core needs period+1 closes; too few bars = no events, not an error
        return []
    rsi = rsi_core([b["c"] for b in bars], period=14)
    regime = malkan_regime(rsi)
    return [{**s, "event": event_name} for s in fn(bars, rsi, regime)]


def malkan_bull_layer(bars):
    """1h. MLK-S1: RSI support bounce at 40 in a BULL regime with a bullish candle -> long. Module defaults
    (tolerance 2.0, regime lookback 20, RSI period 14)."""
    return _malkan_signals(bars, malkan_setup_bull, "malkan_support")


def malkan_bear_layer(bars):
    """1h. MLK-S2: RSI rejection at 60 in a BEAR regime with a bearish candle -> short. Module defaults."""
    return _malkan_signals(bars, malkan_setup_bear, "malkan_resistance")


def _cc_layer(setup_fn, name):
    """1h. Side = the setup's own signal side (long/short); entry_t is the entry trigger bar's open time.
    Params: module defaults (the BACKTEST_L1_REPORT runs used defaults on 1h bars)."""
    def fn(bars):
        try:
            signals = setup_fn(bars)
        except ValueError as exc:
            if "must not be empty" in str(exc):  # no swings yet (too few bars) = no events, not an error
                return []
            raise
        return [{"t": s["entry_t"], "side": s["side"], "event": "%s_%s" % (name, s["side"]),
                 "entry_price": s["entry_price"], "stop": s["stop"]} for s in signals]
    return fn


cc_sr_flip_layer = _cc_layer(setup1_sr_flip, "sr_flip")
cc_fib_pullback_layer = _cc_layer(setup2_fib_pullback, "fib_pullback")
cc_failed_msb_layer = _cc_layer(setup3_failed_msb_reversal, "failed_msb")
