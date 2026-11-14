"""Pure helpers for the mined-rules study (PRE_REG.md in this folder). numpy only, no I/O.
Signal builders use only bars <= the signal bar. Forward-looking helpers are named fwd_* (look-ahead lint): they read bars from the
entry bar on. Reuses wilder_rsi / boot_cluster / bh copied in mal_div_lib.py.
"""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from mal_div_lib import wilder_rsi, boot_cluster, bh  # noqa: F401

MIN = 60000
HOUR = 3600000
DAY = 86400000
WIN_MINUTES = (570, 585)  # 09:30 and 09:45 UTC bar opens = 15:00-15:30 IST (SOURCED, NK closing window)


def bollinger_upper(c, n=20, k=2.0):
    """Upper band: SMA(n) + k * population std(n) of closes; nan before n-1."""
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    if len(c) >= n:
        w = sliding_window_view(c, n)
        out[n - 1:] = w.mean(axis=1) + k * w.std(axis=1)
    return out


def nk_signals(t, rsi, side, window):
    """Signal bar indices. side +1 long (RSI <= 30), -1 short (RSI >= 70), measured at the bar close.
    window True: bar opens 09:30/09:45 UTC, first qualifying bar per UTC day. window False: fresh touch (previous bar not in zone)."""
    t = np.asarray(t, np.int64)
    rsi = np.asarray(rsi, float)
    zone = (rsi <= 30.0) if side == 1 else (rsi >= 70.0)
    zone &= ~np.isnan(rsi)
    if window:
        m = (t // MIN) % 1440
        idx = np.where(zone & np.isin(m, WIN_MINUTES))[0]
        if len(idx):
            day = t[idx] // DAY
            keep = np.ones(len(idx), bool)
            keep[1:] = day[1:] != day[:-1]
            idx = idx[keep]
        return idx
    prev = np.zeros(len(zone), bool)
    prev[1:] = zone[:-1]
    return np.where(zone & ~prev)[0]


def nk_entries(t, o, h, l, side, sig, bar_ms):
    """Entry on the NEXT bar open; stop = low (long) / high (short) of the signal bar. Returns idx(e), entry, stop."""
    sig = np.asarray(sig, int)
    sig = sig[sig + 1 < len(t)]
    sig = sig[(t[sig + 1] - t[sig]) == bar_ms]
    e = sig + 1
    entry = o[e]
    stop = l[sig] if side == 1 else h[sig]
    ok = (stop < entry) if side == 1 else (stop > entry)
    return e[ok], entry[ok], stop[ok]


def bb_entries(t, o, h, l, c, bar_ms, arm=4, n=20, k=2.0):
    """NK-R11 long: breakout candle j = first close above the upper band; trigger = high[j]; first bar in j+1..j+arm whose high
    reaches the trigger fills at max(open, trigger); stop = low[j]. Returns idx(e), entry, stop."""
    ub = bollinger_upper(c, n, k)
    c = np.asarray(c, float)
    j = np.where(~np.isnan(ub[1:]) & ~np.isnan(ub[:-1]) & (c[1:] > ub[1:]) & (c[:-1] <= ub[:-1]))[0] + 1
    idx, entry, stop = [], [], []
    for jj in j:
        trig = h[jj]
        for kk in range(jj + 1, min(jj + arm, len(t) - 1) + 1):
            if t[kk] - t[kk - 1] != bar_ms:
                break
            if h[kk] >= trig:
                en = max(o[kk], trig)
                if l[jj] < en:
                    idx.append(kk), entry.append(en), stop.append(l[jj])
                break
    return np.array(idx, int), np.array(entry, float), np.array(stop, float)


def fold_weeks(t, o, h, l, c):
    """Fold daily bars into UTC Monday-anchored weeks; keep complete contiguous 7-day groups. 't' = Monday 00:00 UTC ms."""
    t = np.asarray(t, np.int64)
    g = (t // DAY + 3) // 7
    keys, start, cnt = np.unique(g, return_index=True, return_counts=True)
    ok = cnt == 7
    last = np.minimum(start + 6, len(t) - 1)
    ok &= (t[last] - t[start]) == 6 * DAY
    st = start[ok]
    return dict(t=((keys[ok] * 7 - 3) * DAY).astype(np.int64), o=np.asarray(o, float)[st], c=np.asarray(c, float)[st + 6],
                h=np.array([np.asarray(h, float)[s:s + 7].max() for s in st]), l=np.array([np.asarray(l, float)[s:s + 7].min() for s in st]))


def mal_r05_entries(dt, do, dh, dl, dc, wk, rsi_w, kind, w, divergence_fn):
    """MAL-R05. Weekly close-divergence (known when week i = b+1 closes); signal bar = 3rd daily candle (Wednesday) of week i+1, must be
    red (bearish/short) or green (bullish/long); entry = next daily open; stop = that candle's high/low; target C = lowest (short) /
    highest (long) weekly close between swing A and B. Returns idx(e), entry, stop, tp."""
    ev = divergence_fn(list(wk["c"]), [None if np.isnan(x) else float(x) for x in rsi_w], list(wk["t"]), 3, w, kind)
    side = -1 if kind == "bearish" else 1
    pos = {int(x): k for k, x in enumerate(dt)}
    idx, entry, stop, tp = [], [], [], []
    for e in ev:
        i, a, b = e["i"], e["a_i"], e["b_i"]
        wed = int(wk["t"][i]) + 7 * DAY + 2 * DAY
        s = pos.get(wed)
        if s is None or s + 1 >= len(dt) or dt[s + 1] - dt[s] != DAY:
            continue
        if (side == -1 and not dc[s] < do[s]) or (side == 1 and not dc[s] > do[s]):
            continue
        en = do[s + 1]
        st = dh[s] if side == -1 else dl[s]
        cc = wk["c"][a:b + 1]
        tgt = cc.min() if side == -1 else cc.max()
        if side == -1 and not (tgt < en < st):
            continue
        if side == 1 and not (st < en < tgt):
            continue
        idx.append(s + 1), entry.append(en), stop.append(st), tp.append(tgt)
    return np.array(idx, int), np.array(entry, float), np.array(stop, float), np.array(tp, float)


def fwd_ok(t, bar_ms, hh):
    """True where bar e has hh contiguous bars e..e+hh-1 (entry bar included)."""
    n = len(t)
    ok = np.zeros(n, bool)
    if n >= hh:
        ok[:n - hh + 1] = (t[hh - 1:] - t[:n - hh + 1]) == (hh - 1) * bar_ms
    return ok


def fwd_window(arr, e, hh):
    """hh values from the entry bar e on. Shape (len(e), hh)."""
    e = np.asarray(e, int)
    return arr[e[:, None] + np.arange(hh)[None, :]]


def fwd_walk(side, entry, stop, tp, O, Hh, L, C, trail, cost):
    """Walk forward windows (N,hh) starting AT the entry bar. Stop active on every bar incl. the entry bar; trailing stop ratchets to the
    PREVIOUS bar's low (long) / high (short); same-bar stop + target = stop first; stop fills at the stop or the open if gapped through;
    target (tp array or None) fills at the level; else time exit at the last close. Returns (net R, hold bars, net return fraction)."""
    n, hh = O.shape
    big = 10 ** 6
    sgn = float(side)
    S = np.repeat(np.asarray(stop, float)[:, None], hh, axis=1)
    if trail:
        if side == 1:
            pl = np.concatenate([np.full((n, 1), -np.inf), L[:, :-1]], axis=1)
            S = np.maximum(S, np.maximum.accumulate(pl, axis=1))
        else:
            ph = np.concatenate([np.full((n, 1), np.inf), Hh[:, :-1]], axis=1)
            S = np.minimum(S, np.minimum.accumulate(ph, axis=1))
    stop_hit = (L <= S) if side == 1 else (Hh >= S)
    first = lambda m: np.where(m.any(axis=1), m.argmax(axis=1), big)  # noqa: E731
    si = first(stop_hit)
    if tp is not None:
        tpa = np.asarray(tp, float)
        ti = first((Hh >= tpa[:, None]) if side == 1 else (L <= tpa[:, None]))
    else:
        ti = np.full(n, big)
    fi = np.minimum(np.minimum(si, ti), hh - 1)
    rows = np.arange(n)
    is_stop = (si <= ti) & (si < big)
    s_at = S[rows, fi]
    gap = np.minimum(s_at, O[rows, fi]) if side == 1 else np.maximum(s_at, O[rows, fi])
    tgt_fill = np.asarray(tp, float) if tp is not None else entry
    fill = np.where(is_stop, gap, np.where(ti < big, tgt_fill, C[rows, fi]))
    net = sgn * (fill - entry) / entry - cost
    sd = np.abs(entry - stop) / entry
    return net / sd, fi + 1, net


def placebo_stop(side, entry, sd):
    return entry * (1.0 - side * np.asarray(sd, float))
