"""Instrument / expiry selection. Uses ONLY observations with ts <= decision time (no lookahead)."""
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import bs  # noqa: E402
from instruments import DAY_MS, HOUR_MS, Instrument, parse_instrument  # noqa: E402

DEFAULT_LOOKBACK_MS = 6 * HOUR_MS
DEFAULT_EXPIRY_LOOKBACK_MS = 3 * DAY_MS


def _chain(panel, ts, expiry_ms, lookback_ms):
    """{name: obs} for instruments of this expiry live in (ts-lookback, ts]. Works with a real Panel (fast path)
    or any object exposing live_instruments + last_obs."""
    fast = getattr(panel, "chain_obs", None)
    if fast is not None:
        return fast(ts, expiry_ms, lookback_ms)
    out = {}
    for nm in sorted(panel.live_instruments(ts, lookback_ms)):
        inst = parse_instrument(nm)
        if inst is None or inst.expiry_ms != expiry_ms:
            continue
        ob = panel.last_obs(nm, ts, lookback_ms)
        if ob is not None:
            out[nm] = ob
    return out


def _ok_iv(iv):
    return iv is not None and not math.isnan(iv) and iv > 0.0


def pick_by_delta(panel, ts, expiry_ms, is_call, target_abs_delta, lookback_ms=DEFAULT_LOOKBACK_MS, max_dev=0.10):
    """Instrument (given expiry and type) whose |Black-76 delta| at ts is nearest to target_abs_delta, or None.
    Delta uses the instrument's own last obs (iv, index) and T = (expiry - ts) in years."""
    T = bs.years_to_expiry(ts, expiry_ms)
    if T <= 0.0:
        return None
    best = None
    for nm, ob in _chain(panel, ts, expiry_ms, lookback_ms).items():
        inst = parse_instrument(nm)
        if inst is None or inst.is_call != bool(is_call) or not _ok_iv(ob["iv"]):
            continue
        d = abs(bs.delta(ob["index"], inst.strike, T, ob["iv"], inst.is_call))
        key = (abs(d - target_abs_delta), inst.strike, nm)
        if best is None or key < best:
            best = key
    if best is None or best[0] > max_dev:
        return None
    return best[2]


def pick_by_strike_pct(panel, ts, expiry_ms, pct, is_call=False, lookback_ms=DEFAULT_LOOKBACK_MS, max_dev=0.05):
    """Instrument with strike nearest pct * index (default: puts), or None when |K/index - pct| > max_dev."""
    ch = _chain(panel, ts, expiry_ms, lookback_ms)
    ref = None
    idx_at = getattr(panel, "index_at", None)
    if idx_at is not None:
        ref = idx_at(ts, lookback_ms)
    if ref is None and ch:
        ref = max(ch.values(), key=lambda o: o["ts"])["index"]
    if ref is None:
        return None
    best = None
    for nm in ch:
        inst = parse_instrument(nm)
        if inst is None or inst.is_call != bool(is_call):
            continue
        key = (abs(inst.strike / ref - pct), inst.strike, nm)
        if best is None or key < best:
            best = key
    if best is None or best[0] > max_dev:
        return None
    return best[2]


def pick_by_premium(panel, ts, expiry_ms, is_call, target_premium_btc, min_strike=None,
                    lookback_ms=DEFAULT_LOOKBACK_MS):
    """Instrument whose last-obs premium (BTC) is nearest target_premium_btc; optional strike floor (OTM call)."""
    best = None
    for nm, ob in _chain(panel, ts, expiry_ms, lookback_ms).items():
        inst = parse_instrument(nm)
        if inst is None or inst.is_call != bool(is_call):
            continue
        if min_strike is not None and inst.strike < min_strike:
            continue
        key = (abs(ob["price"] - target_premium_btc), inst.strike, nm)
        if best is None or key < best:
            best = key
    return None if best is None else best[2]


def pick_straddle(panel, ts, expiry_ms, lookback_ms=DEFAULT_LOOKBACK_MS):
    """(call_name, put_name) at the single strike nearest the latest chain index among strikes where both legs
    are live; None if there is no such strike."""
    ch = _chain(panel, ts, expiry_ms, lookback_ms)
    if not ch:
        return None
    ref = max(ch.values(), key=lambda o: o["ts"])["index"]
    calls, puts = {}, {}
    for nm in ch:
        inst = parse_instrument(nm)
        if inst is None:
            continue
        (calls if inst.is_call else puts)[inst.strike] = nm
    both = sorted(set(calls) & set(puts))
    if not both:
        return None
    k = min(both, key=lambda s: (abs(s - ref), s))
    return calls[k], puts[k]


def _expiry_of(x):
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)) or hasattr(x, "__index__") or hasattr(x, "dtype"):
        try:
            return int(x)
        except (TypeError, ValueError):
            return None
    if isinstance(x, Instrument):
        return x.expiry_ms
    if isinstance(x, str):
        inst = parse_instrument(x)
        return None if inst is None else inst.expiry_ms
    return None


def pick_expiry(ts, min_dte_days, instruments=None, tol_days=3.0, panel=None,
                lookback_ms=DEFAULT_EXPIRY_LOOKBACK_MS):
    """Nearest listed expiry (ms) with DTE >= min_dte_days, DTE = (expiry - ts) / 1 day. Listed = expiries of
    `instruments` (names / Instrument / int ms) or, when None, of `panel.live_expiries(ts, lookback_ms)`.
    Returns None if none qualifies or the nearest one is more than tol_days beyond min_dte_days (tol_days=None:
    no upper limit). Deterministic."""
    if instruments is None:
        if panel is None:
            raise ValueError("pick_expiry needs `instruments` or `panel`")
        exps = panel.live_expiries(ts, lookback_ms)
    else:
        exps = {e for e in (_expiry_of(x) for x in instruments) if e is not None}
    best = None
    for e in sorted(exps):
        dte = (e - ts) / float(DAY_MS)
        if dte + 1e-12 >= min_dte_days:
            best = (dte, e)
            break
    if best is None:
        return None
    if tol_days is not None and best[0] > min_dte_days + tol_days + 1e-12:
        return None
    return best[1]
