"""Pure helpers for the Malkan MAL-R03/R04 divergence study (PRE_REG.md in this folder). numpy only, no I/O.
Forward-looking helpers are named fwd_* (look-ahead lint): they read only bars strictly after the entry bar.
"""
import numpy as np

HOUR = 3600000
H = 12  # time-exit / forward window in TF bars (OURS, card)


def wilder_rsi(c, n=14):
    """Wilder RSI (RMA) seeded with the SMA of the first n changes; nan before index n."""
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    up, dn = np.maximum(d, 0.0), np.maximum(-d, 0.0)
    au, ad = up[:n].mean(), dn[:n].mean()
    out[n] = 100.0 if ad == 0 else 100.0 - 100.0 / (1.0 + au / ad)
    for i in range(n + 1, len(c)):
        au = (au * (n - 1) + up[i - 1]) / n
        ad = (ad * (n - 1) + dn[i - 1]) / n
        out[i] = 100.0 if ad == 0 else 100.0 - 100.0 / (1.0 + au / ad)
    return out


def fold(t, o, h, l, c, tf_h):
    """Fold 1h bars into UTC epoch-anchored tf_h-hour bars; keep only complete, contiguous groups."""
    t = np.asarray(t, np.int64)
    o, h, l, c = (np.asarray(x, float) for x in (o, h, l, c))
    if tf_h == 1:
        return dict(t=t, o=o, h=h, l=l, c=c)
    g = t // (tf_h * HOUR)
    keys, start, cnt = np.unique(g, return_index=True, return_counts=True)
    ok = cnt == tf_h
    last = np.minimum(start + tf_h - 1, len(t) - 1)
    ok &= (t[last] - t[start]) == (tf_h - 1) * HOUR
    st = start[ok]
    return dict(t=(keys[ok] * tf_h * HOUR).astype(np.int64), o=o[st], c=c[st + tf_h - 1],
                h=np.array([h[s:s + tf_h].max() for s in st]), l=np.array([l[s:s + tf_h].min() for s in st]))


def build_trades(bars, rsi, kind, w, tf_h, divergence_fn):
    """Trades for one coin/TF/kind/window. kind 'bearish' (R03 short) or 'bullish' (R04 long).
    Event bar i = bar after swing B (the pivot-confirming bar); it must be red (short) / green (long) and contiguous with B.
    Entry = close[i]; stop = extreme (incl. shadow) of swing-B bar and bar i. Returns dict of arrays (idx, entry, stop, side)."""
    ev = divergence_fn(list(bars["c"]), [None if np.isnan(x) else float(x) for x in rsi], list(bars["t"]), 3, w, kind)
    side = -1 if kind == "bearish" else 1
    idx, entry, stop = [], [], []
    t, o, h, l, c = bars["t"], bars["o"], bars["h"], bars["l"], bars["c"]
    for e in ev:
        i, b = e["i"], e["b_i"]
        if t[i] - t[b] != tf_h * HOUR:
            continue
        if side == -1:
            if not c[i] < o[i]:
                continue
            s = max(h[b], h[i])
            if not s > c[i]:
                continue
        else:
            if not c[i] > o[i]:
                continue
            s = min(l[b], l[i])
            if not s < c[i]:
                continue
        idx.append(i), entry.append(c[i]), stop.append(s)
    return dict(idx=np.array(idx, int), entry=np.array(entry, float), stop=np.array(stop, float), side=side)


def fwd_ok(t, tf_h, hh=H):
    """True where bar j has hh contiguous forward bars (j+1..j+hh)."""
    n = len(t)
    ok = np.zeros(n, bool)
    if n > hh:
        ok[:n - hh] = (t[hh:] - t[:n - hh]) == hh * tf_h * HOUR
    return ok


def fwd_window(arr, e0, hh=H):
    """The hh values AFTER entry bar e0 (entry bar excluded). Shape (len(e0), hh)."""
    e0 = np.asarray(e0, int)
    return arr[e0[:, None] + 1 + np.arange(hh)[None, :]]


def fwd_exit(side, entry, stop, O, Hh, L, C, kind, k, cost):
    """Exit walk over forward windows (N,hh). kind 'tgt' (k in R) or 'time'. Stop always active; same-bar stop+target = stop.
    Stop fills at the stop or the bar open if gapped through; time exit at the last window close. cost = round-trip fraction.
    Returns net R per trade."""
    n, hh = O.shape
    risk = np.abs(entry - stop)
    sd = risk / entry
    big = 10 ** 6
    sgn = float(side)
    stop_hit = (L <= stop[:, None]) if side == 1 else (Hh >= stop[:, None])
    first = lambda m: np.where(m.any(axis=1), m.argmax(axis=1), big)  # noqa: E731
    si = first(stop_hit)
    if kind == "tgt":
        tp = entry + sgn * k * risk
        ti = first((Hh >= tp[:, None]) if side == 1 else (L <= tp[:, None]))
    else:
        tp = entry
        ti = np.full(n, big)
    fi = np.minimum(np.minimum(si, ti), hh - 1)
    rows = np.arange(n)
    is_stop = si <= ti
    is_stop &= si < big
    gap = np.minimum(stop, O[rows, fi]) if side == 1 else np.maximum(stop, O[rows, fi])
    fill = np.where(is_stop, gap, np.where(ti < big, tp, C[rows, fi]))
    net = sgn * (fill - entry) / entry - cost
    return net / sd


def boot_cluster(vals, blocks, nb=2000, seed=7):
    """Block bootstrap of the mean. blocks = integer block id per trade. Returns (mean, lo, hi, p_le0)."""
    vals = np.asarray(vals, float)
    _, inv = np.unique(blocks, return_inverse=True)
    bs = np.bincount(inv, weights=vals)
    bc = np.bincount(inv).astype(float)
    rng = np.random.default_rng(seed)
    m = len(bs)
    res = np.empty(nb)
    for s in range(0, nb, 250):
        e = min(nb, s + 250)
        ix = rng.integers(0, m, size=(e - s, m))
        res[s:e] = bs[ix].sum(1) / bc[ix].sum(1)
    return float(vals.mean()), float(np.percentile(res, 2.5)), float(np.percentile(res, 97.5)), float((res <= 0).mean())


def bh(p, q=0.10):
    """Benjamini-Hochberg: boolean significant per p."""
    p = np.asarray(p, float)
    n = len(p)
    o = np.argsort(p)
    thr = q * (np.arange(1, n + 1) / n)
    ok = p[o] <= thr
    kmax = np.max(np.where(ok)[0]) + 1 if ok.any() else 0
    sig = np.zeros(n, bool)
    sig[o[:kmax]] = True
    return sig


def placebo_stop(side, entry, sd):
    """Stop at the same fractional distance on the losing side: below entry for a long (side 1), above for a short (side -1)."""
    return entry * (1.0 - side * np.asarray(sd, float))
