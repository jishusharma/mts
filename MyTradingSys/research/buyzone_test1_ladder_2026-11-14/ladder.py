"""Test 1 engine: causal confirmation ladder, long side. Rules are frozen in PRE_REG.md (read it first).
All indicators use closed bars only. A swing low at bar i is known only at the close of bar i+K.
"""
import numpy as np
import pandas as pd

K = 3            # swing half-width (OURS)
WARM = 400       # warm-up bars: no event, no placebo draw
HOLD = 30        # days
MIN_GAP, MAX_GAP = 10, 60   # bars between the two lows
EXPIRE = 30      # bars after the second low is known
LOCK = 10        # bars between kept signals on a coin
FEES = {"12": 0.0012, "6": 0.0006}
PHASES = ["UP", "BASE", "RANGE", "DOWN", "POSTPEAK_BEAR"]


def wilder_atr(h, l, c, n=14):
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    pc = c[:-1]
    tr[1:] = np.maximum.reduce([h[1:] - l[1:], np.abs(h[1:] - pc), np.abs(l[1:] - pc)])
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def wilder_rsi(c, n=14):
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    up, dn = np.maximum(d, 0), np.maximum(-d, 0)
    au, ad = up[:n].mean(), dn[:n].mean()
    out[n] = 100.0 if ad == 0 else 100 - 100 / (1 + au / ad)
    for i in range(n, len(d)):
        au = (au * (n - 1) + up[i]) / n
        ad = (ad * (n - 1) + dn[i]) / n
        out[i + 1] = 100.0 if ad == 0 else 100 - 100 / (1 + au / ad)
    return out


def phases(h, l, c):
    """Phase label at bar t from bars <= t only (look up at e-1 for entry bar e)."""
    s = lambda a: pd.Series(a)
    sma200 = s(c).rolling(200).mean().values
    sma350 = s(c).rolling(350).mean().values
    hi365 = s(h).rolling(365, min_periods=1).max().values
    dd = 1 - c / hi365
    lo_recent = s(l).rolling(60).min().values
    lo_prior = s(lo_recent).shift(120).values   # min Low[t-179..t-60]
    hl = lo_recent >= lo_prior
    sh = lambda a: s(a).shift(30).values
    up = (c > sma200) & (sma200 > sh(sma200))
    base = ~up & (dd >= 0.40) & hl
    pp = ~up & ~base & (c < sma350) & (sma350 < sh(sma350)) & (dd >= 0.40)
    down = ~up & ~base & ~pp & (c < sma200) & (sma200 < sh(sma200))
    out = np.full(len(c), "RANGE", dtype=object)
    out[down] = "DOWN"
    out[pp] = "POSTPEAK_BEAR"
    out[base] = "BASE"
    out[up] = "UP"
    out[np.isnan(sma350) | np.isnan(lo_prior)] = ""   # not enough history: no phase
    return out


def swing_lows(l):
    """Indices of swing lows (K bars each side strictly higher). Known at close of i+K."""
    out = []
    for i in range(K, len(l) - K):
        w = np.concatenate([l[i - K:i], l[i + 1:i + K + 1]])
        if l[i] < w.min():
            out.append(i)
    return out


def find_signals(o, h, l, c, atr, rsi, mode, n_avail=None):
    """Raw signals (before lockout): list of (c_idx, j, stop0). n_avail: use only bars < n_avail
    (so causality is testable by truncation)."""
    n = len(c) if n_avail is None else n_avail
    sw = [i for i in swing_lows(l[:n]) if i + K < n]   # known by the last available close
    sigs = []
    for a in range(1, len(sw)):
        p, j = sw[a - 1], sw[a]
        if not (MIN_GAP <= j - p <= MAX_GAP):
            continue
        if mode == "A":
            if not l[j] > l[p]:
                continue
        else:
            if not (l[j] < l[p] and not np.isnan(rsi[j]) and not np.isnan(rsi[p]) and rsi[j] > rsi[p]):
                continue
        H = h[p:j + 1].max()
        for cc in range(j + K, min(j + K + EXPIRE, n - 1) + 1):
            if cc > j + K and l[cc] <= l[j]:
                break
            if l[j + 1:cc + 1].min() <= l[j]:
                break
            if c[cc] > H:
                if np.isnan(atr[cc]):
                    break
                stop0 = l[j] - max(0.6 * atr[cc], 0.005 * l[j])
                sigs.append((cc, j, stop0))
                break
    sigs.sort()
    return sigs


def sim_exit(o, h, l, c, atr, e, stop0):
    """Exit of a long entered at Open[e]. Returns (exit_idx, exit_px) or None if still open at the data end."""
    n = len(c)
    mx = -np.inf
    for t in range(e, min(e + HOLD - 1, n - 1) + 1):
        lvl = stop0 if t == e else max(stop0, mx - 2 * atr[t - 1])
        if l[t] <= lvl:
            return t, min(o[t], lvl)
        mx = max(mx, h[t])
        if t == e + HOLD - 1:
            return t, c[t]
    return None


def build_events(coin, ts, o, h, l, c, mode, n_avail=None):
    atr, rsi = wilder_atr(h, l, c), wilder_rsi(c)
    ph = phases(h, l, c)
    n = len(c) if n_avail is None else n_avail
    sigs = find_signals(o, h, l, c, atr, rsi, mode, n_avail)
    ev, last_sig, last_exit, dropped = [], -10**9, -10**9, 0
    for cc, j, stop0 in sigs:
        e = cc + 1
        if cc < WARM or e >= n or cc < last_sig + LOCK or e <= last_exit:
            continue
        entry = o[e]
        if entry <= stop0:
            dropped += 1
            continue
        r = (entry - stop0) / entry
        res = sim_exit(o[:n], h[:n], l[:n], c[:n], atr, e, stop0)
        if res is None:
            continue
        x, px = res
        ev.append(dict(coin=coin, sig=cc, e=e, x=x, ts=int(ts[e]), r=r, gross=px / entry - 1, phase=ph[e - 1]))
        last_sig, last_exit = cc, x
    return ev, dropped


def split_of(ts_ms):
    d = pd.Timestamp(ts_ms, unit="ms")
    return "DEV" if d <= pd.Timestamp("2023-12-31") else "VAL"


def in_split(ts_ms, sp):
    d = pd.Timestamp(ts_ms, unit="ms")
    if sp == "DEV":
        return d <= pd.Timestamp("2023-12-31")
    if sp == "VAL":
        return d >= pd.Timestamp("2024-01-01")
    if sp == "RECENT":
        return d >= pd.Timestamp("2025-07-01")
    return True


def R_of(gross, r, fee):
    return (gross - fee) / r


def block_ci(ts_ms, R, nboot=10000, seed=1114, block_days=30):
    R = np.asarray(R, float)
    if len(R) == 0:
        return (np.nan, np.nan)
    blk = (np.asarray(ts_ms, dtype=np.int64) // 86400000) // block_days
    u, inv = np.unique(blk, return_inverse=True)
    S = np.bincount(inv, weights=R)
    N = np.bincount(inv).astype(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(u), size=(nboot, len(u)))
    m = S[idx].sum(1) / N[idx].sum(1)
    return tuple(np.percentile(m, [2.5, 97.5]))


class PlaceboTable:
    """Per-coin table of trail levels for every possible entry day, so any (entry day, stop distance) can be
    evaluated for many draws at once. Rows past the data end are NaN-padded; a trade still open at the data end is NaN (dropped)."""

    def __init__(self, coins):
        self.rows = {}      # coin -> (start offset in flat arrays, n)
        O, L, T, C29, TS, PH, ECOIN = [], [], [], [], [], [], []
        off = 0
        for coin, (ts, o, h, l, c) in coins.items():
            n = len(c)
            atr = wilder_atr(h, l, c)
            ph = phases(h, l, c)
            pad = lambda a: np.concatenate([a, np.full(HOLD, np.nan)])
            op, hp, lp, cp = pad(o), pad(h), pad(l), pad(c)
            ap = pad(atr)
            ne = n
            Ob = np.full((ne, HOLD), np.nan)
            Lb = np.full((ne, HOLD), np.nan)
            Tb = np.full((ne, HOLD), -np.inf)
            Cb = np.full(ne, np.nan)
            for e in range(ne):
                mx = -np.inf
                for k in range(HOLD):
                    t = e + k
                    Ob[e, k], Lb[e, k] = op[t], lp[t]
                    if k > 0:
                        Tb[e, k] = mx - 2 * ap[t - 1]
                    mx = max(mx, hp[t]) if not np.isnan(hp[t]) else mx
                Cb[e] = cp[e + HOLD - 1]
            O.append(Ob); L.append(Lb); T.append(Tb); C29.append(Cb)
            TS.append(ts[:ne])
            PH.append(np.array(["" if e < WARM + 1 else ph[e - 1] for e in range(ne)], dtype=object))
            ECOIN.append(np.full(ne, coin, dtype=object))
            self.rows[coin] = (off, ne)
            off += ne
        self.O, self.L, self.T, self.C29 = map(np.concatenate, (O, L, T, C29))
        self.TS, self.PH, self.COIN = map(np.concatenate, (TS, PH, ECOIN))

    def pool(self, coin, phase, split):
        off, n = self.rows[coin]
        sl = slice(off, off + n)
        ok = (self.PH[sl] == phase)
        ts = self.TS[sl]
        ok &= np.array([in_split(t, split) for t in ts]) if split != "ALL" else True
        return off + np.nonzero(ok)[0]

    def gross(self, idx, r):
        """idx, r: arrays (N, m). Returns gross return array (N, m), NaN where the trade is still open at the data end."""
        entry = self.O[idx, 0]
        stop0 = entry * (1 - r)
        lvl = np.maximum(stop0[..., None], self.T[idx])
        Lw = self.L[idx]
        hit = Lw <= lvl
        anyhit = hit.any(-1)
        first = hit.argmax(-1)
        lv_f = np.take_along_axis(lvl, first[..., None], -1)[..., 0]
        op_f = np.take_along_axis(self.O[idx], first[..., None], -1)[..., 0]
        px = np.where(anyhit, np.minimum(op_f, lv_f), self.C29[idx])
        g = px / entry - 1
        g[~anyhit & np.isnan(self.C29[idx])] = np.nan
        return g


def placebo(table, events, split, fee, ndraw=2000, seed=1114, chunk=250):
    """Placebo draw means of mean R for the given events (same coin, same split, same phase, same r)."""
    rng = np.random.default_rng(seed)
    pools = [table.pool(ev["coin"], ev["phase"], split) for ev in events]
    keep = [i for i, p in enumerate(pools) if len(p)]
    if not keep:
        return np.array([])
    r = np.array([events[i]["r"] for i in keep])
    out = []
    for s in range(0, ndraw, chunk):
        m = min(chunk, ndraw - s)
        idx = np.stack([pools[i][rng.integers(0, len(pools[i]), size=m)] for i in keep], 1)
        rr = np.broadcast_to(r, idx.shape)
        g = table.gross(idx, rr)
        R = (g - fee) / rr
        out.append(np.nanmean(R, 1))
    return np.concatenate(out)
