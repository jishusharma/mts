"""Pure helpers for the HTF RSI extreme study (PRE_REG.md). numpy only. Forward-looking helpers are named fwd_*."""
import numpy as np

HOUR = 3600000
DAY = 86400000


def signal_events(ft, fo, fh, fl, fc, rsi, thr, tf_h, rearm=30.0):
    """Entries for first-touch RSI<=thr episodes whose bar is red and whose NEXT contiguous bar closes above its close.
    Returns list of (s, entry, stop, entry_close_t). Reads only bars <= s+1."""
    out, armed = [], True
    for i, x in enumerate(rsi):
        if np.isnan(x):
            continue
        if armed and x <= thr:
            armed = False
            j = i + 1
            if j < len(ft) and ft[j] - ft[i] == tf_h * HOUR and fc[i] < fo[i] and fc[j] > fc[i]:
                out.append((i, float(fc[j]), float(fl[i]), int(ft[j] + tf_h * HOUR)))
        elif (not armed) and x > rearm:
            armed = True
    return out


def fwd_window(arr, e0, w):
    """w hourly values after entry bar e0. Shape (len(e0), w)."""
    e0 = np.asarray(e0, int)
    return arr[e0[:, None] + 1 + np.arange(w)[None, :]]


def _first(mask):
    return np.where(mask.any(axis=1), mask.argmax(axis=1), 10 ** 6)


def fwd_exit_r(entry, stop, O, H, L, C, kind, param, cap, cost):
    """Net R per trade. kind 'tgt' (param = R multiple, cap hours) or 'time' (exit at close of hour `cap`).
    Stop always active, same-hour stop+target = stop; stop fills at min(stop, open of that hour).
    cost = round-trip fraction of price."""
    n = len(entry)
    risk = entry - stop
    si = _first(L[:, :cap] <= stop[:, None])
    ti = np.full(n, 10 ** 6)
    if kind == "tgt":
        ti = _first(H[:, :cap] >= (entry + param * risk)[:, None])
    first = np.minimum(np.minimum(si, ti), cap - 1)
    rows = np.arange(n)
    hit_stop = si == first
    hit_tgt = (~hit_stop) & (ti == first)
    tgt_fill = entry + (param if kind == "tgt" else 0) * risk
    fill = np.where(hit_stop, np.minimum(stop, O[rows, first]), np.where(hit_tgt, tgt_fill, C[rows, first]))
    return ((fill - entry) / entry - cost) / (risk / entry)


def week_boot(vals, wk, rng, nb=2000):
    """Block bootstrap of the mean over blocks `wk`. Returns (mean, lo, hi, p_le0); nan when empty."""
    if len(vals) == 0:
        return (np.nan,) * 4
    uw, inv = np.unique(wk, return_inverse=True)
    S = np.bincount(inv, weights=vals)
    N = np.bincount(inv).astype(float)
    ix = rng.integers(0, len(uw), (nb, len(uw)))
    m = S[ix].sum(1) / N[ix].sum(1)
    return float(vals.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((np.sum(m <= 0) + 1) / (nb + 1))


def bh(p, q=0.10):
    """Benjamini-Hochberg significance mask at FDR q."""
    p = np.asarray(p, float)
    m = len(p)
    o = np.argsort(p)
    passed = p[o] <= (np.arange(1, m + 1) / m) * q
    k = (np.max(np.where(passed)[0]) + 1) if passed.any() else 0
    sig = np.zeros(m, bool)
    sig[o[:k]] = True
    return sig
