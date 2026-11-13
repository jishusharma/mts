"""NK-sourced Hilega Milega state + Supertrap / gap rule study (PRE_REG.md). numpy + pandas only.

All times UTC. 5m grid, 288 bars per day. Bar i opens at grid[i]; an indicator "at bar i" uses data through the close of bar i.
A signal bar m is decided on data <= close of m; the entry is the open of bar m+1.
STUDY_BUG=1 injects a one-bar look-ahead (peek) into the HM states, the Bollinger bands and the closes used in entry tests.
"""
import os
import numpy as np
import pandas as pd

CACHE = r"F:\MTS\data_cache\binance\nk-sourced-hm-supertrap-1114"
WORK = os.path.join(CACHE, "work")
COINS = ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "LTC", "LINK", "TRX", "DOT", "AVAX", "ATOM", "ETC", "BCH", "XLM", "UNI", "NEAR", "FIL", "EOS"]
MS5 = 300000
DAY5 = 288
VAL_START_MS = 1704067200000      # 2024-01-01 00:00 UTC
NY_BAR = 162                      # 13:30 UTC = bar 162 of the day
SUN_BAR = 276                     # Sunday 23:00 UTC reopen proxy
FRI_REF = 263                     # bar 21:55 on Friday; its close = Friday 22:00 UTC close proxy
NYC_REF = 239                     # bar 19:55 of the previous day; its close = 20:00 UTC prior-session close (OURS)
W = 40                            # event window in 5m bars (B part)
CAP_I, CAP_P, HOLD_B = 576, 8640, 72
SIM_WIN, SIM_BLK = 256, 6000
BUF_ATR, SMIN_ATR, SMIN_PCT = 0.1, 0.6, 0.003
POS_ATR, POS_PCT = 1.5, 0.01
THETA = {"cme": (0.5, 1.0), "s0000": (0.5, 1.0), "s1330": (0.75, 1.5)}
PHASES = {1: "UP", 2: "DOWN", 3: "RANGE"}


def BUG():
    return os.environ.get("STUDY_BUG") == "1"


def peek(x):
    """STUDY_BUG look-ahead: the next bar's value (last bar repeats)."""
    return np.concatenate([x[1:], x[-1:]]) if BUG() else x


# ----------------------------------------------------------------------------------------------- data
def load_grid(sym):
    a = np.load(os.path.join(CACHE, sym + "USDT_5m.npz"))["a"]
    ts = a[:, 0].astype(np.int64)
    t0 = (ts[0] // 86400000 + (1 if ts[0] % 86400000 else 0)) * 86400000
    n = int((ts[-1] - t0) // MS5 + 1)
    n -= n % DAY5
    grid = t0 + np.arange(n, dtype=np.int64) * MS5
    pos = np.minimum(np.searchsorted(ts, grid), len(ts) - 1)
    have = ts[pos] == grid
    out = np.full((n, 5), np.nan)
    out[have] = a[pos[have]][:, 1:6]
    df = pd.DataFrame(out, columns=list("ohlcv"))
    df["c"] = df["c"].ffill()
    for k in "ohl":
        df[k] = df[k].fillna(df["c"])
    df["v"] = df["v"].fillna(0.0)
    return grid, df.o.to_numpy(copy=True), df.h.to_numpy(copy=True), df.l.to_numpy(copy=True), df.c.to_numpy(copy=True), df.v.to_numpy(copy=True)


def cycle_by_day(ts_ms, close, smin=1400):
    """BTC daily closes -> (day0, flag per UTC day D from the prior close: 0 NA, 1 BULL close > 200-week (1400-day) SMA, 2 BEAR)."""
    dn = (ts_ms // 86400000).astype(np.int64)
    day0 = int(dn[0])
    full = np.full(int(dn[-1]) - day0 + 1, np.nan)
    full[dn - day0] = close
    full = pd.Series(full).ffill().to_numpy()
    sma = pd.Series(full).rolling(smin).mean().to_numpy()
    f = np.zeros(len(full), dtype=np.int8)
    ok = ~np.isnan(sma)
    f[ok & (full > sma)] = 1
    f[ok & (full <= sma)] = 2
    out = np.concatenate([[0], f]).astype(np.int8)     # index D = flag from close of D-1
    return day0, out, full, sma


# ----------------------------------------------------------------------------------------------- indicators
def resample(o, h, l, c, v, k):
    n = len(c) // k * k
    return (o[:n].reshape(-1, k)[:, 0], h[:n].reshape(-1, k).max(1), l[:n].reshape(-1, k).min(1),
            c[:n].reshape(-1, k)[:, -1], v[:n].reshape(-1, k).sum(1))


def wilder(x, n):
    return np.array(pd.Series(x).ewm(alpha=1.0 / n, adjust=False).mean().values)


def ema(x, span):
    return np.array(pd.Series(x).ewm(span=span, adjust=False).mean().values)


def rsi(c, n):
    d = np.diff(c, prepend=c[0])
    up = wilder(np.maximum(d, 0), n)
    dn = wilder(np.maximum(-d, 0), n)
    with np.errstate(all="ignore"):
        r = np.where(dn == 0, 100.0, 100 - 100 / (1 + up / np.where(dn == 0, 1, dn)))
    r[:n] = np.nan
    return r


def wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    w /= w.sum()
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        out[n - 1:] = np.convolve(x, w[::-1], mode="valid")
    return out


def atr(h, l, c, n=14):
    pc = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    a = wilder(tr, n)
    a[:n] = np.nan
    return a


def hm_lines(C):
    """NK Hilega Milega lines on the closes C: RSI(9), EMA(3) of it, WMA(21) of it (SOURCED Qdug_K_TNHg)."""
    r = rsi(peek(C), 9)
    return r, ema(r, 3), wma(r, 21)


def hm_state(C, h50=False):
    """+1 buy state = WMA21 below BOTH RSI lines; -1 sell state = WMA21 above both; 0 otherwise (NK: a state, not a cross).
    h50=True additionally needs RSI9 > 50 (buy) / < 50 (sell) (NK zone 50/50)."""
    r, e, w = hm_lines(C)
    s = np.zeros(len(C), dtype=np.int8)
    ok = ~(np.isnan(r) | np.isnan(w) | np.isnan(e))
    lo, hi = np.minimum(r, e), np.maximum(r, e)
    buy = ok & (w < lo)
    sell = ok & (w > hi)
    if h50:
        buy &= r > 50
        sell &= r < 50
    s[buy] = 1
    s[sell] = -1
    return s


def bollinger(C, n=20, k=2.0):
    """BB(20, 2) population std, band at bar i includes close i (OURS parameters; NK never spoke them)."""
    s = pd.Series(peek(C))
    m = s.rolling(n).mean()
    sd = s.rolling(n).std(ddof=0)
    return (m + k * sd).to_numpy(), (m - k * sd).to_numpy()


def vwap(tp, v, gid):
    """Anchored VWAP of typical price: cumulative within each anchor group id (non-decreasing); zero volume falls back to tp."""
    pv = pd.Series(tp * v).groupby(gid).cumsum().to_numpy()
    cv = pd.Series(v).groupby(gid).cumsum().to_numpy()
    with np.errstate(all="ignore"):
        return np.where(cv > 0, pv / np.where(cv > 0, cv, 1), tp)


def on5(arr, k, n5, fill=0):
    """value of the tf-k array at 5m index m = last tf bar completed by the close of bar m."""
    b = (np.arange(n5) + 1) // k - 1
    return np.where(b >= 0, arr[np.clip(b, 0, len(arr) - 1)], fill)


def next_change(s):
    """first index > b whose value differs from s[b]; len(s) when none."""
    n = len(s)
    chg = np.flatnonzero(s[1:] != s[:-1]) + 1
    if len(chg) == 0:
        return np.full(n, n)
    pos = np.searchsorted(chg, np.arange(n), side="right")
    return np.where(pos < len(chg), chg[np.minimum(pos, len(chg) - 1)], n)


def daily_arrays(h, l, c):
    nd = len(c) // DAY5
    H = h[:nd * DAY5].reshape(nd, -1).max(1)
    L = l[:nd * DAY5].reshape(nd, -1).min(1)
    C = c[:nd * DAY5].reshape(nd, -1)[:, -1]
    return H, L, C


def daily_phase(h, l, c):
    """Phase for UTC day D from data through the close of D-1 (index nd = the day after the last complete day):
    0 NA, 1 UP (ADX14>=20, DI+>DI-, SMA20 slope>0), 2 DOWN (ADX>=20, DI->DI+, slope<0), 3 RANGE (else). slope = SMA20[D-1]/SMA20[D-6]-1."""
    H, L, C = daily_arrays(h, l, c)
    ma = pd.Series(C).rolling(20).mean().values
    slope = ma / np.concatenate([np.full(5, np.nan), ma[:-5]]) - 1
    up = H - np.concatenate([[H[0]], H[:-1]])
    dn = np.concatenate([[L[0]], L[:-1]]) - L
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = atr(H, L, C, 14)
    sp, sm = wilder(pdm, 14), wilder(mdm, 14)
    with np.errstate(all="ignore"):
        dip = 100 * sp / a
        dim = 100 * sm / a
        dx = 100 * np.abs(dip - dim) / (dip + dim)
    adx = wilder(np.nan_to_num(dx), 14)
    adx[:40] = np.nan
    ph = np.zeros(len(C), dtype=np.int8)
    ok = ~(np.isnan(adx) | np.isnan(slope) | np.isnan(a))
    ph[ok] = 3
    ph[ok & (adx >= 20) & (dip > dim) & (slope > 0)] = 1
    ph[ok & (adx >= 20) & (dim > dip) & (slope < 0)] = 2
    return np.concatenate([[0], ph]).astype(np.int8)


# ----------------------------------------------------------------------------------------------- per-coin preparation
def prep(grid, o, h, l, c, v, cyc=None):
    """All per-coin arrays used by the signal generators. cyc = (day0, flag array) from cycle_by_day or None."""
    n5 = len(c)
    B = dict(grid=grid, o=o, h=h, l=l, c=c, v=v, n5=n5, day0=int(grid[0] // 86400000))
    P = {}
    for k in (6, 288):
        O, H, L, C, V = resample(o, h, l, c, v, k)
        P[k] = dict(C=C, atr=atr(H, L, C))
    O2, H2, L2, C2, V2 = resample(o, h, l, c, v, 2)
    P[1] = dict(C=c)
    B["P"] = P
    raw, st = {}, {}
    for h50 in (0, 1):
        for k in (1, 6, 288):
            s = hm_state(P[k]["C"], bool(h50))
            raw[(h50, k)] = s
            st[(h50, k)] = on5(s, k, n5)
    B["raw"], B["st"] = raw, st
    B["nxt"] = {key: next_change(s) for key, s in raw.items() if key[1] in (6, 288)}
    idx = np.arange(n5)
    tp = (h + l + c) / 3
    B["vw"] = {"U": vwap(tp, v, idx // DAY5), "N": vwap(tp, v, (idx - NY_BAR) // DAY5)}
    B["atr5"] = atr(h, l, c)
    B["atrd5"] = on5(P[288]["atr"], 288, n5, fill=np.nan)
    B["tp"] = tp
    B["bb5u"], B["bb5l"] = bollinger(c)
    B["bb10u"], B["bb10l"] = bollinger(C2)
    B["dH"], B["dL"], _ = daily_arrays(h, l, c)
    ph = daily_phase(h, l, c)
    B["ph_day"] = ph
    B["ph"] = ph[np.minimum(idx // DAY5, len(ph) - 1)]
    if cyc is not None:
        day0, flag = cyc
        di = B["day0"] + idx // DAY5 - day0
        B["cyc"] = np.where((di >= 0) & (di < len(flag)), flag[np.clip(di, 0, len(flag) - 1)], 0).astype(np.int8)
    else:
        B["cyc"] = np.zeros(n5, dtype=np.int8)
    return B


# ----------------------------------------------------------------------------------------------- simulator
def sim(o, h, l, e, d, S, tlen):
    """Entry at open[e]; stop at entry - d*S checked on bars e..e+tlen-1 (stop wins, gap fills at the open); else exit at
    open[e+tlen]. Returns gross R, bars held, entry price. Staged windows so long holds stay cheap."""
    n = len(e)
    entry = o[e]
    stop = entry - d * S
    hit_at = np.full(n, -1, dtype=np.int64)
    active = np.arange(n)
    off, WIN = 0, SIM_WIN
    tmax = int(tlen.max()) if n else 0
    ar0 = np.arange(WIN)[None, :]
    while len(active) and off < tmax:
        nxt = []
        for a in range(0, len(active), SIM_BLK):
            ii = active[a:a + SIM_BLK]
            ar = off + ar0
            mask = ar < tlen[ii][:, None]
            idx = np.minimum(e[ii][:, None] + ar, len(o) - 1)
            dd = d[ii][:, None]
            low = np.where(dd == 1, l[idx], -h[idx])
            st = np.where(dd == 1, stop[ii][:, None], -stop[ii][:, None])
            hit = (low <= st) & mask
            anyh = hit.any(1)
            first = hit.argmax(1)
            hit_at[ii[anyh]] = off + first[anyh]
            nxt.append(ii[~anyh & (tlen[ii] > off + WIN)])
        active = np.concatenate(nxt) if nxt else np.array([], dtype=np.int64)
        off += WIN
    hitm = hit_at >= 0
    ob = np.where(hitm, e + hit_at, e)
    opn = o[ob]
    fill = np.where(d == 1, np.minimum(stop, opn), np.maximum(stop, opn))
    xi = np.minimum(e + tlen, len(o) - 1)
    px = np.where(hitm, fill, o[xi])
    g = d * (px - entry) / S
    held = np.where(hitm, hit_at + 1, tlen)
    return g, held, entry


def no_overlap(e, held):
    keep = np.zeros(len(e), dtype=bool)
    last = -1
    for i in np.argsort(e, kind="stable"):
        if e[i] >= last:
            keep[i] = True
            last = e[i] + held[i]
    return keep


def finish(B, m, d, vw_m, smin_fn, xo, cap):
    """Turn signal bars m (direction d, VWAP at m, exit-open index xo) into trades."""
    n5 = B["n5"]
    m = np.asarray(m, dtype=np.int64)
    d = np.asarray(d, dtype=np.int64)
    e = m + 1
    ok = (e < n5) & ~np.isnan(vw_m) & ~np.isnan(B["atr5"][np.minimum(m, n5 - 1)])
    m, d, e, vw_m, xo = m[ok], d[ok], e[ok], vw_m[ok], np.asarray(xo)[ok]
    entry = B["o"][e]
    buf = BUF_ATR * B["atr5"][m]
    dist = d * (entry - (vw_m - d * buf))
    S = np.maximum(dist, smin_fn(m, entry))
    tlen = np.clip(xo - e, 1, cap).astype(np.int64)
    ok = (e + tlen <= n5 - 1) & (S > 0)
    m, d, e, S, tlen = m[ok], d[ok], e[ok], S[ok], tlen[ok]
    g, held, entry = sim(B["o"], B["h"], B["l"], e, d, S, tlen)
    keep = no_overlap(e, held)
    sel = lambda x: x[keep]
    ts = B["grid"][e]
    day = ts // 86400000
    return dict(e=sel(e), m=sel(m), d=sel(d), g=sel(g), held=sel(held), costu=sel(entry / S), sfrac=sel(S / entry), ts=sel(ts),
                day=sel(day), ph=sel(B["ph"][e]), cyc=sel(B["cyc"][e]))


# ----------------------------------------------------------------------------------------------- Part A
def a_signals(B, anchor, frame, h50):
    """Rising edge of: trend-frame state = d AND entry-frame state = d AND close on the right side of the anchored VWAP.
    frame I = 30m trend, 5m entry; frame P = daily trend, 30m entry. Returns (m, d)."""
    kt, ke = (6, 1) if frame == "I" else (288, 6)
    c = peek(B["c"])
    vw = B["vw"][anchor]
    trend, ent = B["st"][(h50, kt)], B["st"][(h50, ke)]
    ms, ds = [], []
    for d in (1, -1):
        cond = (trend == d) & (ent == d) & ((c > vw) if d == 1 else (c < vw))
        prev = np.concatenate([[False], cond[:-1]])
        m = np.flatnonzero(cond & ~prev)
        ms.append(m)
        ds.append(np.full(len(m), d, dtype=np.int64))
    return np.concatenate(ms), np.concatenate(ds)


def a_trades(B, anchor, frame, h50):
    m, d = a_signals(B, anchor, frame, h50)
    kt = 6 if frame == "I" else 288
    b0 = np.clip((m + 1) // kt - 1, 0, len(B["nxt"][(h50, kt)]) - 1)
    xo = (B["nxt"][(h50, kt)][b0] + 1) * kt
    if frame == "I":
        smin = lambda mm, ent: np.maximum(SMIN_ATR * B["atr5"][mm], SMIN_PCT * ent)
        cap = CAP_I
    else:
        smin = lambda mm, ent: np.maximum(POS_ATR * B["atrd5"][mm], POS_PCT * ent)
        cap = CAP_P
    t = finish(B, m, d, B["vw"][anchor][m], smin, xo, cap)
    return t


# ----------------------------------------------------------------------------------------------- Part B
def b_events(B, src):
    """Session/gap events. q = event open bar, ref = bar whose close is the prior reference price, gap = (open_q - close_ref) / ATRd.
    cme: Sunday 23:00 UTC reopen vs Friday 22:00 UTC close (Binance spot proxy for the CME BTC weekend gap).
    s0000 / s1330: 00:00 / 13:30 UTC open vs the previous day's 20:00 UTC close (OURS prior-session close)."""
    n5 = B["n5"]
    days = np.arange(-(-n5 // DAY5))
    dn = B["day0"] + days
    if src == "cme":
        ds = days[((dn + 3) % 7 == 6) & (days >= 2)]
        q, ref = ds * DAY5 + SUN_BAR, (ds - 2) * DAY5 + FRI_REF
    elif src == "s0000":
        ds = days[days >= 1]
        q, ref = ds * DAY5, (ds - 1) * DAY5 + NYC_REF
    else:
        ds = days[days >= 1]
        q, ref = ds * DAY5 + NY_BAR, (ds - 1) * DAY5 + NYC_REF
    ok = q < n5 - 1                       # windows past the end of data are clipped in _event_matrix; finish() drops unfinished trades
    q, ref = q[ok], ref[ok]
    ad = B["atrd5"][q - 1]
    gap = (B["o"][q] - B["c"][ref]) / ad
    ok = ~np.isnan(gap)
    return dict(q=q[ok], gap=gap[ok])


def _event_matrix(B, q):
    """(idx, window arrays, event-anchored VWAP matrix) for the W bars from each event open."""
    idx = np.minimum(q[:, None] + np.arange(W)[None, :], B["n5"] - 1)
    h, l, c = B["h"][idx], B["l"][idx], peek(B["c"])[idx]
    cr = B["c"][idx]
    v = B["v"][idx]
    tp = B["tp"][idx]
    cv = np.cumsum(v, 1)
    with np.errstate(all="ignore"):
        vwm = np.where(cv > 0, np.cumsum(tp * v, 1) / np.where(cv > 0, cv, 1), tp)
    return h, l, c, cr, vwm


def _first(mask):
    return mask.any(1), mask.argmax(1)


def b_signals(B, ev, th, rule):
    """rule: 'st' Supertrap fade, 'gp' gap rule (breakout >=15 min + retest), 'gd' gap rule + previous-day H/L filter.
    Returns (m, d, vw_at_m). Gap direction g = sign(gap); only |gap| >= th events."""
    sel = np.abs(ev["gap"]) >= th
    q, gap = ev["q"][sel], ev["gap"][sel]
    if len(q) == 0:
        return np.array([], dtype=np.int64), np.array([], dtype=np.int64), np.array([])
    g = np.sign(gap).astype(np.int64)
    hm, lm, cm, crm, vwm = _event_matrix(B, q)
    T = np.arange(W)[None, :]
    if rule == "st":
        q1 = q + 1
        fr5 = _outside_frac(B["h"][q], B["l"][q], B["bb5u"][q], B["bb5l"][q], g)
        h10, l10 = np.maximum(B["h"][q], B["h"][q1]), np.minimum(B["l"][q], B["l"][q1])
        fr10 = _outside_frac(h10, l10, B["bb10u"][q // 2], B["bb10l"][q // 2], g)
        q5, q10 = fr5 >= 0.5, fr10 >= 0.5
        sigoff = np.where(q5, 0, np.where(q10, 1, -1))
        d = -g
        cond = np.where(d[:, None] > 0, cm > vwm, cm < vwm)
        mask = (T > sigoff[:, None]) & (T <= 11) & (sigoff >= 0)[:, None]
        anyh, t = _first(cond & mask)
    else:
        h15, l15 = hm[:, :3].max(1), lm[:, :3].min(1)
        lvl = np.where(g > 0, h15, l15)
        brk = np.where(g[:, None] > 0, cm > lvl[:, None], cm < lvl[:, None]) & (T >= 3) & (T <= 14)
        if rule == "gd":
            di = np.clip(q // DAY5 - 1, 0, len(B["dH"]) - 1)
            brk &= np.where(g[:, None] > 0, cm > B["dH"][di][:, None], cm < B["dL"][di][:, None])
        ab, tb = _first(brk)
        rt = np.where(g[:, None] > 0, (lm <= lvl[:, None]) & (crm > lvl[:, None]), (hm >= lvl[:, None]) & (crm < lvl[:, None]))
        mask = (T > tb[:, None]) & (T <= tb[:, None] + 12) & ab[:, None]
        anyh, t = _first(rt & mask)
        d = g
    m = (q + t)[anyh]
    rows = np.flatnonzero(anyh)
    return m, d[anyh], vwm[rows, t[anyh]]


def _outside_frac(hi, lo, up, dn, g):
    rng = hi - lo
    with np.errstate(all="ignore"):
        out = np.where(g > 0, np.maximum(0, hi - up), np.maximum(0, dn - lo))
        return np.where(rng > 0, out / rng, np.nan)


def b_trades(B, ev, th, rule):
    m, d, vw_m = b_signals(B, ev, th, rule)
    smin = lambda mm, ent: np.maximum(SMIN_ATR * B["atr5"][mm], SMIN_PCT * ent)
    return finish(B, m, d, vw_m, smin, m + 1 + HOLD_B, HOLD_B)


# ----------------------------------------------------------------------------------------------- variants
def variants():
    V = []
    for anchor in ("U", "N"):
        for frame in ("I", "P"):
            for h50 in (0, 1):
                V.append(dict(id="A_%s_%s_h%d" % (anchor, frame, h50), part="A", anchor=anchor, frame=frame, h50=h50))
    for src in ("cme", "s0000", "s1330"):
        for th in THETA[src]:
            for rule in ("st", "gp", "gd"):
                V.append(dict(id="B_%s_t%g_%s" % (src, th, rule), part="B", src=src, th=th, rule=rule))
    return V


def coin_trades(B):
    out = {}
    evs = {}
    for v in variants():
        if v["part"] == "A":
            t = a_trades(B, v["anchor"], v["frame"], v["h50"])
        else:
            if v["src"] not in evs:
                evs[v["src"]] = b_events(B, v["src"])
            t = b_trades(B, evs[v["src"]], v["th"], v["rule"])
        out[v["id"]] = t
    return out
