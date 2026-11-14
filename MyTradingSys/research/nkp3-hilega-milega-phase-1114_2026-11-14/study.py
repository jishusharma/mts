"""nkp3 study core (PRE_REG.md). numpy+pandas only. All paths via pathlib."""
import os
from pathlib import Path
import numpy as np
import pandas as pd
import phases as PH

SLUG = "nkp3-hilega-milega-phase-1114"
ROOT = Path(r"F:/MTS/data_cache")
MS5, H1, D1 = 300000, 3600000, 86400000
VAL_START = 1704067200000  # 2024-01-01 by SIGNAL bar close time
COINS = ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "LTC", "LINK", "TRX", "DOT", "AVAX", "ATOM", "ETC", "BCH", "XLM", "UNI", "NEAR", "FIL", "EOS"]
STOP_ATR, STOP_PCT = 1.5, 0.005   # >= max(0.6 ATR, 0.5%) spec floor; NK4 recon used 1.5 ATR
LAYERS = ["C1_rsi4h", "C2_wt1d", "C3_pctb4h", "C4_oi24h", "C5_fund", "C6_takerdiv", "C7_rvratio", "C8_session"]
BUCKETS = {"C1_rsi4h": ("<=40", "mid", ">=60"), "C2_wt1d": ("<=-53", "mid", ">=+53"), "C3_pctb4h": ("<0.10", "mid", ">0.90"),
           "C4_oi24h": ("<=-3%", "flat", ">=+3%"), "C5_fund": ("<0", "0-0.03%", ">0.03%"),
           "C6_takerdiv": ("bull-div", "agree", "bear-div"), "C7_rvratio": ("<0.7", "mid", ">1.3"), "C8_session": ("ASIA", "EU", "US")}
# variants: name -> (family, tf as multiple of 5m, cap bars)
VARIANTS = {"HM15": ("HM", 3, 48), "HM1h": ("HM", 12, 48), "HM4h": ("HM", 48, 48),
            "BO1h": ("BO", 12, 24), "BO4h": ("BO", 48, 24), "FO1h": ("FO", 12, 24), "FO4h": ("FO", 48, 24)}


def BUG():
    return os.environ.get("STUDY_BUG") == "1"


# ---------------- data ----------------
def load_grid(sym):
    a = np.load(ROOT / "binance" / (sym + "USDT_5m.npz"))["a"]
    ts = a[:, 0].astype(np.int64)
    t0 = (ts[0] // D1 + (1 if ts[0] % D1 else 0)) * D1
    n = int((ts[-1] - t0) // MS5 + 1)
    n -= n % 288
    grid = t0 + np.arange(n, dtype=np.int64) * MS5
    pos = np.minimum(np.searchsorted(ts, grid), len(ts) - 1)
    have = ts[pos] == grid
    out = np.full((n, 4), np.nan)
    out[have] = a[pos[have]][:, 1:5]
    df = pd.DataFrame(out, columns=list("ohlc"))
    df["c"] = df["c"].ffill()
    for k in "ohl":
        df[k] = df[k].fillna(df["c"])
    return dict(sym=sym, start5=grid, o=df.o.to_numpy(copy=True), h=df.h.to_numpy(copy=True), l=df.l.to_numpy(copy=True), c=df.c.to_numpy(copy=True))


def load_aux(sym):
    out = {}
    p = ROOT / "binance_spot" / SLUG / (sym + "USDT_1h_taker.npz")
    out["taker"] = np.load(p)["a"] if p.exists() else None
    p = ROOT / "binance" / SLUG / (sym + "USDT_oi_1h.npz")
    out["oi"] = np.load(p)["a"] if p.exists() else None
    p = ROOT / "binance" / SLUG / (sym + "USDT_funding.npz")
    out["fund"] = np.load(p)["a"] if p.exists() else None
    return out


def tfbars(cd, k):
    n = len(cd["c"]) // k * k
    o = cd["o"][:n].reshape(-1, k)[:, 0]
    c = cd["c"][:n].reshape(-1, k)[:, -1]
    h = cd["h"][:n].reshape(-1, k).max(1)
    l = cd["l"][:n].reshape(-1, k).min(1)
    return o, h, l, c, cd["start5"][:n:k]


# ---------------- indicators ----------------
def wilder(x, n):
    return np.array(pd.Series(x).ewm(alpha=1.0 / n, adjust=False).mean().values)


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


def hm_state(c):
    """+1 buy / -1 sell / 0. RSI9, EMA3 of RSI, WMA21 of RSI (OURS, NK4 recon). STUDY_BUG peeks one bar ahead."""
    cc = np.concatenate([c[1:], c[-1:]]) if BUG() else c
    r = rsi(cc, 9)
    e = np.array(pd.Series(r).ewm(span=3, adjust=False).mean().values)
    w = wma(r, 21)
    s = np.zeros(len(c), dtype=np.int8)
    ok = ~(np.isnan(r) | np.isnan(w) | np.isnan(e))
    s[ok & (r > e) & (r > w) & (e > w)] = 1
    s[ok & (r < e) & (r < w) & (e < w)] = -1
    return s


def bollinger(c, n=20, k=2.0):
    s = pd.Series(c)
    m = s.rolling(n).mean().values
    sd = s.rolling(n).std(ddof=0).values
    return m, m + k * sd, m - k * sd


def wavetrend(h, l, c):
    ap = pd.Series((h + l + c) / 3.0)
    esa = ap.ewm(span=10, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=10, adjust=False).mean()
    ci = (ap - esa) / (0.015 * d)
    return ci.ewm(span=21, adjust=False).mean().values


# ---------------- causal context ----------------
def lastclosed(start_h, bar_ms, tc):
    """index of the last bar of the higher tf whose CLOSE (start+bar_ms) <= tc. STUDY_BUG: one bar into the future."""
    i = np.searchsorted(start_h + bar_ms, tc, side="right") - 1
    if BUG():
        i = np.minimum(i + 1, len(start_h) - 1)
    return i


def look(arr, idx):
    out = np.full(len(idx), np.nan)
    m = (idx >= 0) & (idx < len(arr))
    out[m] = arr[idx[m]]
    return out


def bucket(x, lo, hi, strict=False):
    b = np.full(len(x), 1, dtype=np.int8)
    if strict:
        b[x < lo] = 0
        b[x > hi] = 2
    else:
        b[x <= lo] = 0
        b[x >= hi] = 2
    b[np.isnan(x)] = 3
    return b


def hourly(arr_ts, arr_val):
    s = pd.Series(arr_val, index=(arr_ts // H1).astype(np.int64))
    s = s[~s.index.duplicated(keep="last")]
    return s.reindex(np.arange(s.index.min(), s.index.max() + 1))


def build_ctx(cd, aux, k):
    """(n_bars, 8) int8 buckets for signal tf k (x5m); 3 = NA. Uses only bars closed at or before the signal bar close."""
    O, H, L, C, start = tfbars(cd, k)
    tc = start + k * MS5
    n = len(C)
    out = np.full((n, 8), 3, dtype=np.int8)
    o4, h4, l4, c4, s4 = tfbars(cd, 48)
    i4 = lastclosed(s4, 48 * MS5, tc)
    out[:, 0] = bucket(look(rsi(c4, 14), i4), 40, 60)
    m, up, lo = bollinger(c4)
    with np.errstate(all="ignore"):
        pb = (c4 - lo) / (up - lo)
    out[:, 2] = bucket(look(pb, i4), 0.10, 0.90, strict=True)
    o1, h1, l1, c1, s1 = tfbars(cd, 288)
    id1 = lastclosed(s1, 288 * MS5, tc)
    out[:, 1] = bucket(look(wavetrend(h1, l1, c1), id1), -53, 53)
    oh, hh, lh, ch, sh = tfbars(cd, 12)
    lr = pd.Series(np.diff(np.log(ch), prepend=np.nan))
    with np.errstate(all="ignore"):
        rv = (lr.rolling(168).std() / lr.rolling(1440).std()).values
    ih = lastclosed(sh, H1, tc)
    out[:, 6] = bucket(look(rv, ih), 0.7, 1.3, strict=True)
    hr = (tc // H1) % 24
    out[:, 7] = np.where((hr >= 7) & (hr < 13), 1, np.where((hr >= 13) & (hr < 21), 2, 0)).astype(np.int8)
    hq = tc // H1 + (1 if BUG() else 0)
    if aux.get("oi") is not None and len(aux["oi"]):
        s = hourly(aux["oi"][:, 0], aux["oi"][:, 1]).ffill(limit=6)
        chg = (s / s.shift(24) - 1).values
        out[:, 3] = bucket(look(chg, (hq - s.index.min()).astype(np.int64)), -0.03, 0.03)
    if aux.get("fund") is not None and len(aux["fund"]):
        ft, fr = aux["fund"][:, 0], aux["fund"][:, 1]
        m3 = pd.Series(fr).rolling(3).mean().values
        j = np.searchsorted(ft, tc, side="right") - 1
        if BUG():
            j = np.minimum(j + 1, len(ft) - 1)
        v = look(m3, j)
        stale = (tc - look(ft.astype(float), j)) > 9 * H1
        if not BUG():
            v[stale] = np.nan
        out[:, 4] = bucket(v, 0.0, 0.0003, strict=True)
    if aux.get("taker") is not None and len(aux["taker"]):
        a = aux["taker"]
        v = pd.Series(a[:, 5], index=(a[:, 0] // H1).astype(np.int64))
        tb = pd.Series(a[:, 6], index=v.index)
        cl = pd.Series(a[:, 4], index=v.index)
        full = np.arange(v.index.min(), v.index.max() + 1)
        v, tb, cl = v.reindex(full), tb.reindex(full), cl.reindex(full)
        with np.errstate(all="ignore"):
            td = ((2 * tb - v).rolling(24).sum() / v.rolling(24).sum()).values
            p24 = (cl / cl.shift(24) - 1).values
        hb = (tc // H1 - 1 + (1 if BUG() else 0) - full[0]).astype(np.int64)
        tdv, pv = look(td, hb), look(p24, hb)
        b6 = np.full(n, 1, dtype=np.int8)
        b6[(pv < 0) & (tdv > 0)] = 0
        b6[(pv > 0) & (tdv < 0)] = 2
        b6[np.isnan(tdv) | np.isnan(pv)] = 3
        out[:, 5] = b6
    return out


# ---------------- signals ----------------
def hm_signals(O, H, L, C):
    s = hm_state(C)
    prev = np.concatenate([[0], s[:-1]]).astype(np.int8)
    j = np.nonzero((s != 0) & (s != prev))[0]
    d = s[j].astype(int)
    ex = {1: s != 1, -1: s != -1}
    return j, d, ex


def bb_signals(O, H, L, C, kind):
    m, up, lo = bollinger(C)
    pc = np.concatenate([[np.nan], C[:-1]])
    pu = np.concatenate([[np.nan], up[:-1]])
    pl = np.concatenate([[np.nan], lo[:-1]])
    with np.errstate(invalid="ignore"):
        if kind == "BO":
            lg = (C > up) & (pc <= pu)
            sh = (C < lo) & (pc >= pl)
            ex = {1: C <= m, -1: C >= m}
        else:  # FO: previous close outside the band, this close back inside -> fade
            sh = (pc > pu) & (C <= up)
            lg = (pc < pl) & (C >= lo)
            ex = {1: C >= m, -1: C <= m}
    jl, js = np.nonzero(lg)[0], np.nonzero(sh)[0]
    j = np.concatenate([jl, js])
    d = np.concatenate([np.ones(len(jl), int), -np.ones(len(js), int)])
    o = np.argsort(j, kind="stable")
    return j[o], d[o], ex


def nextexit(cond):
    n = len(cond)
    idx = np.where(cond, np.arange(n), n + 10**6)
    return np.minimum.accumulate(idx[::-1])[::-1]


def signals(variant, O, H, L, C):
    fam = VARIANTS[variant][0]
    return hm_signals(O, H, L, C) if fam == "HM" else bb_signals(O, H, L, C, fam)


# ---------------- trade simulation ----------------
def sim(o, h, l, e, d, S, tlen, entry):
    """stop at entry-d*S checked on bars e..e+tlen-1 (stop wins ties; a gap through the stop fills at the worse of stop and
    that bar's open); else exit at open[e+tlen]. returns gross R, held bars."""
    n = len(e)
    gR = np.zeros(n)
    held = np.zeros(n, dtype=int)
    order = np.argsort(tlen)
    CH = 4000
    for a in range(0, n, CH):
        ii = order[a:a + CH]
        Lm = int(tlen[ii].max())
        ar = np.arange(Lm)[None, :]
        idx = np.minimum(e[ii][:, None] + ar, len(l) - 1)
        mask = ar < tlen[ii][:, None]
        dd = d[ii]
        stop = entry[ii] - dd * S[ii]
        lo = np.where(dd[:, None] == 1, l[idx], -h[idx])
        st = np.where(dd == 1, stop, -stop)[:, None]
        hit = (lo <= st) & mask
        anyh = hit.any(1)
        first = hit.argmax(1)
        opn = o[e[ii] + first]
        fill = np.where(dd == 1, np.minimum(stop, opn), np.maximum(stop, opn))
        ex = o[e[ii] + tlen[ii]]
        px = np.where(anyh, fill, ex)
        gR[ii] = dd * (px - entry[ii]) / S[ii]
        held[ii] = np.where(anyh, first + 1, tlen[ii])
    return gR, held


def phase_for(tc, table):
    """phase label of the UTC day containing the signal bar close (table already lagged by PHASE_LAG)."""
    dn = (tc // D1).astype(np.int64)
    lab = table["label"]
    arr = np.zeros(int(max(dn.max(), lab.index.max())) + 2, dtype=np.int8)
    arr[lab.index.values.astype(int)] = lab.values
    return arr[dn]


class Univ:
    """all coins concatenated for one tf: o,h,l,c,atr,tc,coin,ctx,phase; cend = last global index of the coin."""

    def __init__(self, k, ph_table, coins=COINS):
        self.k = k
        parts = []
        off = 0
        self.off = {}
        for ci, c in enumerate(coins):
            cd = load_grid(c)
            aux = load_aux(c)
            O, H, L, C, start = tfbars(cd, k)
            ctx = build_ctx(cd, aux, k)
            parts.append((ci, O, H, L, C, start, atr(H, L, C), ctx))
            self.off[c] = off
            off += len(C)
        cat = lambda i: np.concatenate([p[i] for p in parts])
        self.o, self.h, self.l, self.c, self.start, self.atr, self.ctx = cat(1), cat(2), cat(3), cat(4), cat(5), cat(6), cat(7)
        self.coin = np.concatenate([np.full(len(p[1]), p[0], dtype=np.int8) for p in parts])
        ends = np.cumsum([len(p[1]) for p in parts]) - 1
        self.cend = np.concatenate([np.full(len(p[1]), ends[i], dtype=np.int64) for i, p in enumerate(parts)])
        self.tc = self.start + k * MS5
        self.parts = [(p[1], p[2], p[3], p[4]) for p in parts]
        self.coins = list(coins)
        self.phase = phase_for(self.tc, ph_table)


def make_trades(U, variant):
    fam, k, cap = VARIANTS[variant]
    rec = []
    for ci, c in enumerate(U.coins):
        O, H, L, C = U.parts[ci]
        off = U.off[c]
        n = len(C)
        j, d, ex = signals(variant, O, H, L, C)
        ne = {1: nextexit(ex[1]), -1: nextexit(ex[-1])}
        a = U.atr[slice(off, off + n)]  # this coin's own ATR block (no forward index)
        e = j + 1
        ok = (e + cap + 1 < n) & ~np.isnan(a[j]) & (j >= 60)
        j, d, e = j[ok], d[ok], e[ok]
        nx = np.where(d == 1, ne[1][e], ne[-1][e])
        tlen = np.clip(nx + 1 - e, 1, cap)
        ok2 = e + tlen < n
        j, d, e, tlen = j[ok2], d[ok2], e[ok2], tlen[ok2]
        S = np.maximum(STOP_ATR * a[j], STOP_PCT * O[e])
        rec.append((j + off, d, S, tlen))
    gj = np.concatenate([r[0] for r in rec])
    d = np.concatenate([r[1] for r in rec])
    S = np.concatenate([r[2] for r in rec])
    tlen = np.concatenate([r[3] for r in rec])
    e = gj + 1
    entry = U.o[e]
    g, held = sim(U.o, U.h, U.l, e, d, S, tlen, entry)
    t = dict(gj=gj, d=d, S=S, tlen=tlen, g=g, held=held, costu=entry / S)
    t["tc"] = U.tc[gj]
    t["day"] = U.tc[gj] // D1
    t["phase"] = U.phase[gj]
    t["coin"] = U.coin[gj]
    t["hour"] = (U.tc[gj] // H1) % 24
    t["ctx"] = U.ctx[gj]
    return t


# ---------------- statistics ----------------
def day_stats(x, day, rng, boot=2000):
    n = len(x)
    out = dict(n=int(n))
    if n == 0:
        return out
    ud, inv = np.unique(day, return_inverse=True)
    sums = np.bincount(inv, weights=x)
    cnt = np.bincount(inv).astype(float)
    D = len(ud)
    out.update(days=int(D), mean=float(x.mean()), win=float((x > 0).mean()))
    if D < 2:
        return out
    idx = rng.integers(0, D, (boot, D))
    md = sums[idx].sum(1) / cnt[idx].sum(1)
    out["ci_lo"] = float(np.quantile(md, 0.025))
    out["ci_hi"] = float(np.quantile(md, 0.975))
    out["lo90"] = float(np.quantile(md, 0.05))
    out["p"] = float((np.sum(md <= 0) + 1) / (boot + 1))
    top = np.argsort(-sums)[:5]
    rest = n - cnt[top].sum()
    out["ex5"] = float((x.sum() - sums[top].sum()) / rest) if rest > 0 else float("nan")
    return out


def cluster_se(x, day):
    n = len(x)
    if n < 2:
        return float("nan")
    ud, inv = np.unique(day, return_inverse=True)
    sums = np.bincount(inv, weights=x)
    cnt = np.bincount(inv).astype(float)
    m = x.mean()
    return float(np.sqrt(np.sum((sums - m * cnt) ** 2)) / n)


def bh(ps, q=0.10):
    ps = np.array(ps, dtype=float)
    m = len(ps)
    if m == 0:
        return np.array([], dtype=float)
    o = np.argsort(ps)
    adj = np.empty(m)
    prev = 1.0
    for r in range(m - 1, -1, -1):
        prev = min(prev, ps[o[r]] * m / (r + 1))
        adj[o[r]] = prev
    return adj
