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
from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events
from MyTradingSys.backtest.layers.turn_of_candle.turn_of_candle import turn_of_candle_events
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
    first touch of that level within 200 bars after leg confirmation, scan from confirmed_i+1 like run_fvg).
    Side = the backtest 'bounce' reading (run_backtest.py:199,202): close at leg confirmation above the level ->
    "long", else "short". n_bins=20, VA 70% = backtest values. Fail closed: fewer than 2*n_bins bars -> []."""
    if len(bars) < 2 * n_bins:
        return []
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
        for i in range(start + 1, min(start + 1 + 200, len(bars) - 1)):
            if bars[i]["l"] <= mid <= bars[i]["h"]:
                side = "long" if closes[start] > mid else "short"
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


RSI_LEVEL = 40.0
RSI_TOL = 0.5


def rsi_level_layer(bars):
    """1h/15m RSI(14) level events at 40 +/- 0.5 (unchanged detector: rsi_events). Side only on "failure":
    a failure is a band run whose resolving bar closed on the OPPOSITE side of the run's entry side
    (rsi_events.py; rsi/TEST_PLAN.md), so the entry side is the opposite of the resolving bar's side, and that side
    is readable from the RSI value at the event bar (t = resolving bar; rsi > level+tol / < level-tol always holds
    there). Resolved below -> the run came from above (support from above failed) -> "short"; resolved above -> came
    from below (resistance from below failed) -> "long". support / rejection / cross keep NO side (alert-only)."""
    closes = [b["c"] for b in bars]
    ts = [b["t"] for b in bars]
    rsi = rsi_core(closes, period=14)
    idx = {t: i for i, t in enumerate(ts)}
    out = []
    for e in rsi_events(rsi, ts, level=RSI_LEVEL, tolerance=RSI_TOL):
        if e["event"] == "failure":
            v = rsi[idx[e["t"]]]
            if v is not None and v < RSI_LEVEL - RSI_TOL:
                e = {**e, "side": "short"}
            elif v is not None and v > RSI_LEVEL + RSI_TOL:
                e = {**e, "side": "long"}
        out.append(e)
    return out


def turn_of_candle_layer(bars):
    """1m bars. Candidate C3 (T055, FORMULAS.md sec 16): one event per quarter hour at minute-of-quarter 14
    (lead_minutes=1, entry at that bar's close, just before the 15m candle opens). Side (operator 2026-09-30,
    data collection): sign of the opening taker-buy imbalance (2*tbv - v)/v of the SAME quarter's minute-0 bar,
    as in run_t055_c3_imbalance.py imbalance_events(window=1, direction="mom"): > 0 long, < 0 short, 0 / no volume /
    missing minute-0 bar -> NO side. "sampling": True marks a no-edge layer traded only to collect fills
    (T055_BT_c3.md: no gross edge); never a Tom filter."""
    out = []
    for e in turn_of_candle_events(bars, lead_minutes=1):
        i = e["i"]
        ev = {"t": bars[i]["t"], "event": "toc_m14", "sampling": True}
        o = i - 14
        if o >= 0 and bars[i]["t"] - bars[o]["t"] == 14 * 60000 and bars[o]["v"] > 0:
            imb = (2 * bars[o]["tbv"] - bars[o]["v"]) / bars[o]["v"]
            ev["imbalance"] = round(imb, 6)
            if imb > 0:
                ev["side"] = "long"
            elif imb < 0:
                ev["side"] = "short"
        out.append(ev)
    return out
