"""Strategies R1 R2 R3 R4 R7 S7 (BT_SPEC). Each returns (trades, skipped). Deterministic, no lookahead:
selection uses obs with ts <= decision time; fills use prints with ts >= decision time."""
import math
import os
import re
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import bs  # noqa: E402
from bs import MS_PER_YEAR, payoff_btc  # noqa: E402
from fees import delivery_fee_btc, perp_fee_btc, trade_fee_btc  # noqa: E402
from instruments import DAY_MS, HOUR_MS, ms_to_ymd, parse_instrument, weekday_of_ms, ymd_to_ms  # noqa: E402
from selection import (pick_by_delta, pick_by_premium, pick_by_strike_pct, pick_expiry,  # noqa: E402
                       pick_straddle)

DEFAULT_FILL_WINDOW_MS = 2 * HOUR_MS
DEFAULT_LOOKBACK_MS = 6 * HOUR_MS
LONG_LOOKBACK_MS = 24 * HOUR_MS
ROLL_HOUR_MS = 9 * HOUR_MS  # expiry 08:00 UTC + 1 h
_DOW = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


# ---------------------------------------------------------------------------------------------- helpers
def default_tol_days(tenor):
    return max(2.0, 0.25 * float(tenor))


def next_expiry_ms(ts_ms, spec="next_sunday_0800"):
    """'next_<weekday>_HHMM': first such weekday at HH:MM UTC strictly after ts_ms."""
    m = re.match(r"^next_([a-z]+)_(\d{2})(\d{2})$", spec)
    if not m or m.group(1)[:3] not in _DOW:
        raise ValueError("bad expiry spec %r" % (spec,))
    w = _DOW[m.group(1)[:3]]
    off = int(m.group(2)) * HOUR_MS + int(m.group(3)) * 60000
    d0 = int(ts_ms // DAY_MS)
    for k in range(0, 9):
        cand = (d0 + k) * DAY_MS + off
        if cand > ts_ms and weekday_of_ms(cand) == w:
            return cand
    raise ValueError("unreachable")


def _range_ms(panel, start, end):
    """(first ms, last ms inclusive) of the evaluated date range; defaults to the panel's shard range."""
    d0, d1 = panel.date_range()
    s = start or d0
    e = end or d1
    if s is None or e is None:
        return None
    return ymd_to_ms(s), ymd_to_ms(e) + DAY_MS - 1


def dvol_filter_ok(panel, ts_ms, n=90):
    """True if the latest CLOSED daily DVOL close (candle stamped 00:00 UTC of D-1, known from D 00:00) is above the
    mean of the n daily closes before it. None if history is insufficient or stale (caller treats as fail)."""
    dv = panel.dvol_daily
    t = dv.get("ts")
    if t is None or t.size == 0:
        return None
    k = int(np.searchsorted(t, ts_ms - DAY_MS, side="right")) - 1
    if k < n or (ts_ms - (int(t[k]) + DAY_MS)) >= 2 * DAY_MS:
        return None
    c = dv["close"]
    return bool(c[k] > c[k - n:k].mean())


def _skip(strategy, ts, reason, detail=None):
    return {"ts": int(ts), "date": ms_to_ymd(ts), "reason": reason, "strategy": strategy, "detail": detail}


def _entry_iv(panel, name, fill_ts):
    o = panel.obs_range(name, fill_ts, fill_ts)
    if o["ts"].size:
        v = float(o["iv"][0])
        if v > 0.0 and not math.isnan(v):
            return v
    return float("nan")


def _execute(panel, strategy, ts, specs, expiry_ms, fill_window_ms, size, slip_pct, extra=None):
    """specs = [(instrument_name, our_side)]. All legs must fill (package). Returns (trade|None, skip|None)."""
    win = min(fill_window_ms, expiry_ms - ts - 1)
    fills = []
    for name, side in specs:
        f = panel.first_fill(name, side, ts, win, size, slip_pct) if win >= 0 else None
        if f is None:
            return None, _skip(strategy, ts, "no_fill", name)
        fills.append(f)
    S = panel.settlement_price(ms_to_ymd(expiry_ms))
    if S is None:
        return None, _skip(strategy, ts, "no_settlement", ms_to_ymd(expiry_ms))
    legs, pnl, fees = [], 0.0, 0.0
    for (name, side), f in zip(specs, fills):
        inst = parse_instrument(name)
        pay = payoff_btc(inst.is_call, inst.strike, S)
        fee_e = trade_fee_btc(f["price"], f["ts"])
        fee_d = delivery_fee_btc(pay, inst.expiry_ms)
        sign = 1.0 if side == "sell" else -1.0
        pnl += sign * (f["price"] - pay) - fee_e - fee_d
        fees += fee_e + fee_d
        legs.append({"name": name, "side": side, "entry_px": f["price"], "fee_entry": fee_e, "payoff_btc": pay,
                     "fee_delivery": fee_d, "fill_ts": f["ts"], "strike": inst.strike, "is_call": inst.is_call,
                     "entry_iv": _entry_iv(panel, name, f["ts"]), "entry_index": f["index"]})
    last = max(fills, key=lambda f: f["ts"])
    trade = {"strategy": strategy, "decision_ts": int(ts), "entry_ts": int(last["ts"]), "exit_ts": int(expiry_ms),
             "legs": legs, "pnl_btc": pnl, "spot_entry": last["index"], "spot_exit": S, "fees_btc": fees}
    if extra:
        trade.update(extra)
    return trade, None


def _roll(panel, strategy, start, end, decide):
    """Sequential roll: first decision at start-date 09:00 UTC; after a trade the next decision is expiry + 1 h;
    after a skip the decision is retried 24 h later."""
    rng = _range_ms(panel, start, end)
    trades, skipped = [], []
    if rng is None:
        return trades, skipped
    s_ms, e_ms = rng
    ts = s_ms + ROLL_HOUR_MS
    while ts <= e_ms:
        tr, sk = decide(ts)
        if tr is not None:
            trades.append(tr)
            ts = tr["exit_ts"] + HOUR_MS
        else:
            skipped.append(sk)
            ts += DAY_MS
    return trades, skipped


# ---------------------------------------------------------------------------------------------- R1
def weekend_strangle(panel, dow_entry=4, hour=16, expiry="next_sunday_0800", delta=0.15, *, start=None, end=None,
                     fill_window_ms=DEFAULT_FILL_WINDOW_MS, size=1.0, slip_pct=0.0, max_dev=0.10,
                     lookback_ms=DEFAULT_LOOKBACK_MS):
    """Sell put + call at target |delta| on weekday dow_entry (Mon=0) at `hour` UTC, hold to expiry."""
    rng = _range_ms(panel, start, end)
    trades, skipped = [], []
    if rng is None:
        return trades, skipped
    s_ms, e_ms = rng
    d = s_ms // DAY_MS
    while d * DAY_MS <= e_ms:
        ts = d * DAY_MS + hour * HOUR_MS
        d += 1
        if weekday_of_ms(ts) != dow_entry or ts > e_ms:
            continue
        exp = next_expiry_ms(ts, expiry)
        put = pick_by_delta(panel, ts, exp, False, delta, lookback_ms, max_dev)
        call = pick_by_delta(panel, ts, exp, True, delta, lookback_ms, max_dev)
        if put is None or call is None:
            skipped.append(_skip("R1", ts, "no_instrument", "put=%s call=%s" % (put, call)))
            continue
        tr, sk = _execute(panel, "R1", ts, [(put, "sell"), (call, "sell")], exp, fill_window_ms, size, slip_pct)
        (trades if tr else skipped).append(tr or sk)
    return trades, skipped


# ---------------------------------------------------------------------------------------------- R2 / R4
def _single_leg(panel, strategy, is_call, delta, tenor_days, dvol_filter, tol_days, start, end, fill_window_ms,
                size, slip_pct, max_dev, lookback_ms):
    tol = default_tol_days(tenor_days) if tol_days is None else tol_days

    def decide(ts):
        if dvol_filter:
            ok = dvol_filter_ok(panel, ts)
            if not ok:
                return None, _skip(strategy, ts, "filter", "dvol_insufficient" if ok is None else "dvol_below_mean90")
        exp = pick_expiry(ts, tenor_days, tol_days=tol, panel=panel)
        name = None if exp is None else pick_by_delta(panel, ts, exp, is_call, delta, lookback_ms, max_dev)
        if name is None:
            return None, _skip(strategy, ts, "no_instrument", "expiry=%s" % exp)
        return _execute(panel, strategy, ts, [(name, "sell")], exp, fill_window_ms, size, slip_pct)

    return _roll(panel, strategy, start, end, decide)


def covered_call(panel, delta=0.20, tenor_days=7, *, dvol_filter=False, tol_days=None, start=None, end=None,
                 fill_window_ms=DEFAULT_FILL_WINDOW_MS, size=1.0, slip_pct=0.0, max_dev=0.10,
                 lookback_ms=DEFAULT_LOOKBACK_MS):
    """R2: sell 1 call at target |delta| and tenor, hold to expiry, roll at expiry + 1 h (pnl = option leg only)."""
    return _single_leg(panel, "R2", True, delta, tenor_days, dvol_filter, tol_days, start, end, fill_window_ms,
                       size, slip_pct, max_dev, lookback_ms)


def cash_secured_put(panel, delta=0.20, tenor_days=7, *, dvol_filter=False, tol_days=None, start=None, end=None,
                     fill_window_ms=DEFAULT_FILL_WINDOW_MS, size=1.0, slip_pct=0.0, max_dev=0.10,
                     lookback_ms=DEFAULT_LOOKBACK_MS):
    """R4: as R2 with puts."""
    return _single_leg(panel, "R4", False, delta, tenor_days, dvol_filter, tol_days, start, end, fill_window_ms,
                       size, slip_pct, max_dev, lookback_ms)


# ---------------------------------------------------------------------------------------------- S7
def long_straddle(panel, tenor_days=7, *, tol_days=None, start=None, end=None,
                  fill_window_ms=DEFAULT_FILL_WINDOW_MS, size=1.0, slip_pct=0.0, lookback_ms=DEFAULT_LOOKBACK_MS):
    """S7 control: buy the ATM straddle (strike nearest index), hold to expiry, roll."""
    tol = default_tol_days(tenor_days) if tol_days is None else tol_days

    def decide(ts):
        exp = pick_expiry(ts, tenor_days, tol_days=tol, panel=panel)
        pair = None if exp is None else pick_straddle(panel, ts, exp, lookback_ms)
        if pair is None:
            return None, _skip("S7", ts, "no_instrument", "expiry=%s" % exp)
        return _execute(panel, "S7", ts, [(pair[0], "buy"), (pair[1], "buy")], exp, fill_window_ms, size, slip_pct)

    return _roll(panel, "S7", start, end, decide)


# ---------------------------------------------------------------------------------------------- R3
def _carry_iv_fn(panel, leg, expiry_ms):
    o = panel.obs_range(leg["name"], leg["fill_ts"], expiry_ms)
    ok = np.isfinite(o["iv"]) & (o["iv"] > 0.0)
    ots, oiv = o["ts"][ok], o["iv"][ok]
    entry = leg["entry_iv"]

    def f(t):
        k = int(np.searchsorted(ots, t, side="right")) - 1
        return float(oiv[k]) if k >= 0 else entry
    return f


def _hedge_run(panel, legs, entry_ts, expiry_ms, rule):
    """Hourly (or band) perp hedge of the straddle's Black-76 delta. Returns dict in BTC, or None without bars."""
    perp = panel.perp_1h
    if perp["ts"].size == 0:
        return None
    tclose = perp["ts"] + HOUR_MS
    t0 = -(-entry_ts // HOUR_MS) * HOUR_MS
    sel = (tclose >= t0) & (tclose <= expiry_ms)
    times, px = tclose[sel], perp["close"][sel]
    if times.size < 2:
        return None
    fund = panel.funding
    if fund["ts"].size:
        fi = np.minimum(np.searchsorted(fund["ts"], times), fund["ts"].size - 1)
        have = fund["ts"][fi] == times
        rates = np.where(have, fund["interest_1h"][fi], 0.0)
    else:
        have = np.zeros(times.size, dtype=bool)
        rates = np.zeros(times.size)
    band = None
    if rule != "hourly":
        m = re.match(r"^band([0-9.]+)$", rule)
        if not m:
            raise ValueError("hedge_rule must be 'hourly' or 'band<x>'")
        band = float(m.group(1))
    ivf = [_carry_iv_fn(panel, lg, expiry_ms) for lg in legs]
    q = 0.0
    p_prev = None
    hedge = fund_btc = fees = 0.0
    n_reb = 0
    for t, p, r in zip(times.tolist(), px.tolist(), rates.tolist()):
        if p_prev is not None and q != 0.0:
            hedge += q * (p - p_prev) / p
            fund_btc -= q * r
        if t >= expiry_ms:
            if q != 0.0:
                fees += perp_fee_btc(q * p, p)
                n_reb += 1
                q = 0.0
            p_prev = p
            break
        T = (expiry_ms - t) / MS_PER_YEAR
        net = 0.0
        for lg, f in zip(legs, ivf):
            pos = -1.0 if lg["side"] == "sell" else 1.0
            net += pos * bs.delta(p, lg["strike"], T, f(t), lg["is_call"])
        tgt = -net
        if (band is None and tgt != q) or (band is not None and abs(tgt - q) > band):
            fees += perp_fee_btc((tgt - q) * p, p)
            q = tgt
            n_reb += 1
        p_prev = p
    if q != 0.0 and p_prev is not None:  # perp data ended before expiry: flatten at last bar
        fees += perp_fee_btc(q * p_prev, p_prev)
        n_reb += 1
    return {"hedge": hedge, "funding": fund_btc, "fees": fees, "n_rebalances": n_reb,
            "n_bars": int(times.size), "funding_missing": int((~have).sum())}


def delta_hedged_short_straddle(panel, tenor_days=7, hedge_rule="hourly", *, tol_days=None, start=None, end=None,
                                fill_window_ms=DEFAULT_FILL_WINDOW_MS, size=1.0, slip_pct=0.0,
                                lookback_ms=DEFAULT_LOOKBACK_MS):
    """R3: sell the ATM straddle (strike nearest index), hedge with BTC-PERPETUAL on perp_1h closes. pnl_btc =
    options (premium - payoff) + hedge + funding - fees (option, delivery, perp). Split is in pnl_*_btc keys."""
    tol = default_tol_days(tenor_days) if tol_days is None else tol_days

    def decide(ts):
        exp = pick_expiry(ts, tenor_days, tol_days=tol, panel=panel)
        pair = None if exp is None else pick_straddle(panel, ts, exp, lookback_ms)
        if pair is None:
            return None, _skip("R3", ts, "no_instrument", "expiry=%s" % exp)
        tr, sk = _execute(panel, "R3", ts, [(pair[0], "sell"), (pair[1], "sell")], exp, fill_window_ms, size,
                          slip_pct)
        if tr is None:
            return None, sk
        h = _hedge_run(panel, tr["legs"], tr["entry_ts"], exp, hedge_rule)
        if h is None:
            return None, _skip("R3", ts, "no_hedge_data", ms_to_ymd(ts))
        opt = sum((1.0 if lg["side"] == "sell" else -1.0) * (lg["entry_px"] - lg["payoff_btc"]) for lg in tr["legs"])
        fees = tr["fees_btc"] + h["fees"]
        tr.update({"pnl_options_btc": opt, "pnl_hedge_btc": h["hedge"], "pnl_funding_btc": h["funding"],
                   "pnl_fees_btc": -fees, "fees_btc": fees, "n_rebalances": h["n_rebalances"],
                   "funding_missing": h["funding_missing"], "hedge_rule": hedge_rule})
        tr["pnl_btc"] = opt + h["hedge"] + h["funding"] - fees
        return tr, None

    return _roll(panel, "R3", start, end, decide)


# ---------------------------------------------------------------------------------------------- R7
def protective_put_overlay(panel, strike_pct=0.90, tenor_days=30, *, collar=False, tol_days=None, start=None,
                           end=None, fill_window_ms=DEFAULT_FILL_WINDOW_MS, size=1.0, slip_pct=0.0, max_dev=0.05,
                           lookback_ms=LONG_LOOKBACK_MS):
    """R7: account = 1 BTC + options. Buy the put nearest strike_pct*index; collar=True also sells the OTM call
    whose last-obs premium is nearest the put's last-obs premium (selected at decision time, no lookahead)."""
    tol = default_tol_days(tenor_days) if tol_days is None else tol_days

    def decide(ts):
        exp = pick_expiry(ts, tenor_days, tol_days=tol, panel=panel, lookback_ms=3 * DAY_MS)
        put = None if exp is None else pick_by_strike_pct(panel, ts, exp, strike_pct, False, lookback_ms, max_dev)
        if put is None:
            return None, _skip("R7", ts, "no_instrument", "expiry=%s put" % exp)
        specs = [(put, "buy")]
        if collar:
            ob = panel.last_obs(put, ts, lookback_ms)
            ref = panel.index_at(ts, lookback_ms)
            call = pick_by_premium(panel, ts, exp, True, ob["price"], min_strike=ref, lookback_ms=lookback_ms)
            if call is None:
                return None, _skip("R7", ts, "no_instrument", "expiry=%s call" % exp)
            specs.append((call, "sell"))
        return _execute(panel, "R7", ts, specs, exp, fill_window_ms, size, slip_pct,
                        extra={"strike_pct": strike_pct, "collar": bool(collar)})

    return _roll(panel, "R7", start, end, decide)


def collar(panel, strike_pct=0.90, tenor_days=30, **kw):
    return protective_put_overlay(panel, strike_pct, tenor_days, collar=True, **kw)


def overlay_equity_series(panel, trades, start=None, end=None):
    """Daily marks at 08:00 UTC on every date with a delivery price in [start, end]. Account = 1 BTC +
    realised option pnl + Black-76 mark of open legs (last-obs iv carried forward, fallback entry iv, F = that
    day's delivery price as spot). Returns dict of numpy arrays: dates, spot, equity_btc, equity_usd, hodl_usd,
    covered (a position is open over the following 24 h)."""
    prices = panel.delivery_prices
    if trades:
        s0 = start or ms_to_ymd(min(t["entry_ts"] for t in trades))
        e0 = end or ms_to_ymd(max(t["exit_ts"] for t in trades))
    else:
        s0, e0 = start, end
    dates = sorted(d for d in prices if (s0 is None or d >= s0) and (e0 is None or d <= e0))
    t_arr = np.asarray([ymd_to_ms(d) + 8 * HOUR_MS for d in dates], dtype=np.int64)
    spot = np.asarray([prices[d] for d in dates], dtype=np.float64)
    eq = np.ones(len(dates))
    cov = np.zeros(len(dates), dtype=bool)
    for tr in trades:
        eq[t_arr >= tr["exit_ts"]] += tr["pnl_btc"]
        cov |= (t_arr >= tr["entry_ts"]) & (t_arr < tr["exit_ts"])
        open_idx = np.nonzero((t_arr > tr["entry_ts"]) & (t_arr < tr["exit_ts"]))[0]
        if not open_idx.size:
            continue
        fns = [_carry_iv_fn(panel, lg, tr["exit_ts"]) for lg in tr["legs"]]
        for i in open_idx.tolist():
            t, F = int(t_arr[i]), float(spot[i])
            T = (tr["exit_ts"] - t) / MS_PER_YEAR
            c = 0.0
            for lg, f in zip(tr["legs"], fns):
                v = bs.price_btc(F, lg["strike"], T, f(t), lg["is_call"])
                sgn = 1.0 if lg["side"] == "sell" else -1.0
                c += sgn * (lg["entry_px"] - v) - lg["fee_entry"]
            eq[i] += c
    return {"dates": dates, "spot": spot, "equity_btc": eq, "equity_usd": eq * spot, "hodl_usd": spot.copy(),
            "covered": cov}
