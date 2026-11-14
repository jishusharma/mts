"""Pure helpers for the deep-RSI-extreme grid study (PRE_REG.md in this folder). numpy only, no I/O.

Time axis: everything is on UTC epoch milliseconds. Hourly bars are the base series; 4h/8h/12h are folded from them.
Forward-looking helpers are named fwd_* (look-ahead lint): they only ever read bars strictly after the entry bar.
"""
import numpy as np

HOUR = 3600000
DAY = 86400000
WIN = 168  # forward window in 1h bars (7 days)


def wilder_rsi(c, n=14):
    """Wilder RSI (RMA), seeded with the SMA of the first n changes (TradingView convention); nan before index n."""
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


def fold(t, o, h, l, c, v, tf_h):
    """Fold 1h bars into UTC-anchored tf_h-hour bars (anchor = epoch, so 8h opens 00/08/16, 12h 00/12).
    Only groups with all tf_h consecutive hourly bars are kept. Returns dict of arrays (t = open time)."""
    t = np.asarray(t, np.int64)
    o, h, l, c, v = (np.asarray(x, float) for x in (o, h, l, c, v))
    if tf_h == 1:
        return dict(t=t, o=o, h=h, l=l, c=c, v=v)
    g = t // (tf_h * HOUR)
    keys, start, cnt = np.unique(g, return_index=True, return_counts=True)
    ok = cnt == tf_h
    last = np.minimum(start + tf_h - 1, len(t) - 1)
    ok &= (t[last] - t[start]) == (tf_h - 1) * HOUR
    st = start[ok]
    ft = keys[ok] * tf_h * HOUR
    return dict(t=ft.astype(np.int64), o=o[st], c=c[st + tf_h - 1],
                h=np.array([h[s:s + tf_h].max() for s in st]), l=np.array([l[s:s + tf_h].min() for s in st]),
                v=np.array([v[s:s + tf_h].sum() for s in st]))


def episodes(rsi, thr, rearm=30.0):
    """First-touch episode starts: index i where rsi[i] <= thr while armed; re-armed once rsi closes above `rearm`."""
    armed, out = True, []
    for i, x in enumerate(rsi):
        if np.isnan(x):
            continue
        if armed and x <= thr:
            out.append(i)
            armed = False
        elif (not armed) and x > rearm:
            armed = True
    return np.array(out, dtype=int)


def confirm_info(ft, fo, fh, fl, fc, s, tf_h):
    """Confirmation = the NEXT tf bar (index s+1, contiguous) is green and closes above the signal bar's close.
    Returns None when s+1 does not exist yet / is not contiguous; else dict(confirm, entry, stop, entry_close_t, undercut, stopdist).
    Reads only bars <= s+1 (entry is the close of bar s+1)."""
    if s + 1 >= len(ft) or ft[s + 1] - ft[s] != tf_h * HOUR:
        return None
    j = s + 1
    entry = fc[j]
    stop = fl[s]
    return dict(confirm=bool(fc[j] > fo[j] and fc[j] > fc[s]), entry=float(entry), stop=float(stop),
                entry_close_t=int(ft[j] + tf_h * HOUR), undercut=bool(fl[j] < fl[s]),
                stopdist=float((entry - stop) / entry))


def rsi_at_hours(ft, rsi, tf_h, ht):
    """Map TF-bar RSI onto the hourly axis: value sits on the hourly bar that closes the TF bar, nan elsewhere."""
    out = np.full(len(ht), np.nan)
    pos = {int(x): i for i, x in enumerate(ht)}
    for j in range(len(ft)):
        i = pos.get(int(ft[j]) + (tf_h - 1) * HOUR)
        if i is not None:
            out[i] = rsi[j]
    return out


def fwd_window(arr, e0, w=WIN):
    """The w hourly values AFTER entry bar e0 (entry bar excluded: it closed at the entry). Shape (len(e0), w)."""
    e0 = np.asarray(e0, int)
    return arr[e0[:, None] + 1 + np.arange(w)[None, :]]


def fwd_first(mask):
    """Index of first True per row, or -1."""
    anyv = mask.any(axis=1)
    return np.where(anyv, mask.argmax(axis=1), -1)


def fwd_exit(entry, stop, O, H, L, C, R50, kind, param, taker):
    """Vectorised exit walk. entry/stop (N,), O/H/L/C/R50 are (N,WIN) forward windows (bars after entry).
    kind 'tgt' (param k in R, cap 72h), 'rsi50' (cap 168h), 'time' (param hours). Stop is always active; same-bar stop+target = stop.
    Stop fills at min(stop, open) (gap), target at the target price. Returns dict: net_pct, net_r, hold, reason(0 stop/1 tgt/2 rsi/3 time)."""
    n = len(entry)
    risk = entry - stop
    stopdist = risk / entry
    cap = {"tgt": 72, "rsi50": WIN}.get(kind, int(param) if kind == "time" else 72)
    big = 10 ** 6
    si = fwd_first(L[:, :cap] <= stop[:, None])
    si = np.where(si < 0, big, si)
    ti = np.full(n, big)
    ri = np.full(n, big)
    if kind == "tgt":
        tp = entry + param * risk
        ti = fwd_first(H[:, :cap] >= tp[:, None])
        ti = np.where(ti < 0, big, ti)
    elif kind == "rsi50":
        ri = fwd_first(R50[:, :cap] > 50.0)
        ri = np.where(ri < 0, big, ri)
    ci = np.full(n, cap - 1)
    first = np.minimum.reduce([si, ti, ri, ci])
    rows = np.arange(n)
    fi = np.minimum(first, WIN - 1)
    reason = np.where(si == first, 0, np.where(ti == first, 1, np.where(ri == first, 2, 3)))  # ties: stop > target > rsi > time
    tgt_fill = entry + (param if kind == "tgt" else 0) * risk
    fill = np.where(reason == 0, np.minimum(stop, O[rows, fi]), np.where(reason == 1, tgt_fill, C[rows, fi]))
    net_pct = (fill - entry) / entry - 2 * taker
    return dict(net_pct=net_pct, net_r=net_pct / stopdist, hold=first + 1, reason=reason)


def sma(c, n):
    """Simple moving average of the last n values; nan before index n-1."""
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    if len(c) >= n:
        cs = np.cumsum(np.insert(c, 0, 0.0))
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def adx_di(h, l, c, n=14):
    """Wilder ADX, +DI, -DI (bar i uses bars <= i only). nan before warm-up."""
    h, l, c = (np.asarray(x, float) for x in (h, l, c))
    m = len(c)
    adx, pdi, mdi = (np.full(m, np.nan) for _ in range(3))
    if m < 2 * n + 1:
        return adx, pdi, mdi
    tr = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    up, dn = h[1:] - h[:-1], l[:-1] - l[1:]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    st, sp, sm = tr[:n].sum(), pdm[:n].sum(), mdm[:n].sum()
    dx = np.full(m, np.nan)
    for i in range(n, m):
        if i > n:
            st = st - st / n + tr[i - 1]
            sp = sp - sp / n + pdm[i - 1]
            sm = sm - sm / n + mdm[i - 1]
        pdi[i] = 100.0 * sp / st
        mdi[i] = 100.0 * sm / st
        s = pdi[i] + mdi[i]
        dx[i] = 0.0 if s == 0 else 100.0 * abs(pdi[i] - mdi[i]) / s
    a = np.nanmean(dx[n:2 * n])
    adx[2 * n - 1] = a
    for i in range(2 * n, m):
        a = (a * (n - 1) + dx[i]) / n
        adx[i] = a
    return adx, pdi, mdi
