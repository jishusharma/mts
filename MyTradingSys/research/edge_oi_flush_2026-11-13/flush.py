"""Liquidation-flush reversal: event detection and trade outcome (PRE_REG.md). Pure functions; no I/O."""
import bisect
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backtest"))
import fees  # noqa: E402

RT_FEE = fees.BINANCE_TAKER * 2
HOUR = 3600_000


def agg(kl, tf):
    """1h klines [(t,o,h,l,c)] -> TF-hour UTC-aligned bars, only complete groups."""
    if tf == 1:
        return [tuple(k) for k in kl]
    by = {}
    for t, o, h, l, c in kl:
        by.setdefault(t // (tf * HOUR), []).append((t, o, h, l, c))
    out = []
    for g in sorted(by):
        r = by[g]
        if len(r) == tf and all(r[i][0] - r[0][0] == i * HOUR for i in range(tf)):
            out.append((r[0][0], r[0][1], max(x[2] for x in r), min(x[3] for x in r), r[-1][4]))
    return out


def atr_series(bars, n=14):
    """Wilder ATR ending at bar i-1 for each i (value[i] uses bars < i only)."""
    out = [None] * len(bars)
    a = None
    trs = []
    for i in range(1, len(bars)):
        h, l, pc = bars[i][2], bars[i][3], bars[i - 1][4]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        if a is None:
            trs.append(tr)
            if len(trs) == n:
                a = sum(trs) / n
        else:
            a = (a * (n - 1) + tr) / n
        if i + 1 < len(bars):
            out[i + 1] = a
    return out


def pct1(window):
    s = sorted(window)
    return s[max(0, int(math.floor(0.01 * (len(s) - 1))))]


def doi_series(bars, oi_map, tf):
    """dOI_i = OI(T+TF)/OI(T)-1 or None."""
    out = []
    for b in bars:
        a, z = oi_map.get(b[0]), oi_map.get(b[0] + tf * HOUR)
        out.append(z / a - 1 if a and z else None)
    return out


def events(bars, doi, atr, tf, k_atr=2.0, win_days=30):
    """Return per-bar flags: list of dict(i, side, move_atr, q, dOI, drop). side +1 long (after down move), -1 short.
    Also returns all bars' (dOI<q) flag via 'cand' for placebo selection."""
    w = win_days * 24 // tf
    rows = []
    for i in range(len(bars)):
        if i < w or atr[i] is None or doi[i] is None:
            continue
        hist = [x for x in doi[i - w:i] if x is not None]
        if len(hist) < 0.8 * w:
            continue
        q = pct1(hist)
        mv = (bars[i][4] - bars[i][1]) / atr[i]
        rows.append(dict(i=i, q=q, d=doi[i], mv=mv, drop=doi[i] < q))
    return rows


def dedup(evs, bars, hours=24):
    out, last = [], None
    for e in evs:
        t = bars[e["i"]][0]
        if last is None or t - last >= hours * HOUR:
            out.append(e)
            last = t
    return out


def funding_sum(fund_t, fund_r, t0, t1):
    a, b = bisect.bisect_right(fund_t, t0), bisect.bisect_right(fund_t, t1)
    return sum(fund_r[a:b])


def fwd_fixed(kl1h_t, kl1h, ft, fr, t_entry, side, hold_h):
    """Fixed hold: entry at 1h-bar open t_entry, exit at open t_entry+hold. Net return % of entry, direction-signed."""
    j = bisect.bisect_left(kl1h_t, t_entry)
    if j >= len(kl1h_t) or kl1h_t[j] != t_entry:
        return None
    jx = bisect.bisect_left(kl1h_t, t_entry + hold_h * HOUR)
    if jx >= len(kl1h_t) or kl1h_t[jx] != t_entry + hold_h * HOUR:
        return None
    e, x = kl1h[j][1], kl1h[jx][1]
    gross = side * (x / e - 1)
    fund = side * funding_sum(ft, fr, t_entry, t_entry + hold_h * HOUR)
    return gross - fund - RT_FEE


def fwd_bracket(kl1h_t, kl1h, ft, fr, t_entry, side, stop, rr=2.0, max_h=72):
    """Bracket on 1h bars from the entry bar: stop at flush extreme, target rr*R; stop wins ties; timeout at open after max_h."""
    j = bisect.bisect_left(kl1h_t, t_entry)
    if j >= len(kl1h_t) or kl1h_t[j] != t_entry:
        return None
    e = kl1h[j][1]
    R = side * (e - stop)
    if R <= 0:
        return None
    tgt = e + side * rr * R
    for m in range(max_h):
        if j + m >= len(kl1h):
            return None
        t, o, h, l, c = kl1h[j + m]
        hit_stop = l <= stop if side > 0 else h >= stop
        hit_tgt = h >= tgt if side > 0 else l <= tgt
        if hit_stop or hit_tgt:
            x = stop if hit_stop else tgt
            return side * (x / e - 1) - side * funding_sum(ft, fr, t_entry, t + HOUR) - RT_FEE
    if j + max_h >= len(kl1h):
        return None
    x = kl1h[j + max_h][1]
    return side * (x / e - 1) - side * funding_sum(ft, fr, t_entry, kl1h[j + max_h][0]) - RT_FEE
