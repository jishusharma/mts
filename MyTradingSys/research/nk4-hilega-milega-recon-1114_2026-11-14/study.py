"""NK Hilega Milega reconstruction study (PRE_REG.md). numpy+pandas only."""
import os
import numpy as np
import pandas as pd

CACHE = r"F:\MTS\data_cache\binance"
COINS = ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "LTC", "LINK", "TRX", "DOT", "AVAX", "ATOM", "ETC", "BCH", "XLM", "UNI", "NEAR", "FIL", "EOS"]
MS5 = 300000
DAY5 = 288
CAP = 48            # signal-tf bars
VAL_START_MS = 1704067200000  # 2024-01-01
STOP_ATR, STOP_PCT = 1.5, 0.005


def BUG():
    return os.environ.get("STUDY_BUG") == "1"


def load_grid(sym):
    a = np.load(os.path.join(CACHE, sym + "USDT_5m.npz"))["a"]
    ts = a[:, 0].astype(np.int64)
    t0 = (ts[0] // 86400000 + (1 if ts[0] % 86400000 else 0)) * 86400000
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
    return grid, df.o.to_numpy(copy=True), df.h.to_numpy(copy=True), df.l.to_numpy(copy=True), df.c.to_numpy(copy=True)


def resample(o, h, l, c, k):
    n = len(c) // k * k
    O = o[:n].reshape(-1, k)[:, 0]
    C = c[:n].reshape(-1, k)[:, -1]
    H = h[:n].reshape(-1, k).max(1)
    L = l[:n].reshape(-1, k).min(1)
    return O, H, L, C


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
    """+1 buy, -1 sell, 0 neutral. RSI9, EMA3 of RSI, WMA21 of RSI (OURS). STUDY_BUG: peeks one bar ahead."""
    cc = np.concatenate([c[1:], c[-1:]]) if BUG() else c
    r = rsi(cc, 9)
    e = np.array(pd.Series(r).ewm(span=3, adjust=False).mean().values)
    w = wma(r, 21)
    s = np.zeros(len(c), dtype=np.int8)
    ok = ~(np.isnan(r) | np.isnan(w) | np.isnan(e))
    s[ok & (r > e) & (r > w) & (e > w)] = 1
    s[ok & (r < e) & (r < w) & (e < w)] = -1
    return s


def daily_phase(h, l, c):
    """phase per day (0 NA,1 UP,2 DOWN,3 RANGE) for day D from data through D-1 close."""
    nd = len(c) // DAY5
    H = h[:nd * DAY5].reshape(nd, -1).max(1)
    L = l[:nd * DAY5].reshape(nd, -1).min(1)
    C = c[:nd * DAY5].reshape(nd, -1)[:, -1]
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
    ph = np.zeros(nd, dtype=np.int8)
    ok = ~(np.isnan(adx) | np.isnan(slope) | np.isnan(a))
    ph[ok] = 3
    ph[ok & (adx >= 20) & (dip > dim) & (slope > 0)] = 1
    ph[ok & (adx >= 20) & (dim > dip) & (slope < 0)] = 2
    out = np.zeros(nd, dtype=np.int8)
    out[1:] = ph[:-1]
    return out


def tf_pack(o, h, l, c, k):
    O, H, L, C = resample(o, h, l, c, k)
    return dict(s=hm_state(C), atr=atr(H, L, C), C=C)


def on5(arr, k, n5, fill=0):
    """value of tf-k array at 5m index m = last completed tf bar (m+1)//k-1."""
    b = (np.arange(n5) + 1) // k - 1
    return np.where(b >= 0, arr[np.clip(b, 0, len(arr) - 1)], fill)


def build_coin(sym):
    grid, o, h, l, c = load_grid(sym)
    n5 = len(c)
    P = {k: tf_pack(o, h, l, c, k) for k in (1, 2, 3)}
    r14 = rsi(P[3]["C"], 14)
    zl = pd.Series((r14 <= 30).astype(float)).rolling(3, min_periods=1).max().values > 0
    zs = pd.Series((r14 >= 70).astype(float)).rolling(3, min_periods=1).max().values > 0
    st = {k: on5(P[k]["s"], k, n5) for k in (1, 2, 3)}
    zl5 = on5(zl.astype(np.int8), 3, n5).astype(bool)
    zs5 = on5(zs.astype(np.int8), 3, n5).astype(bool)
    ph = daily_phase(h, l, c)
    return dict(sym=sym, grid=grid, o=o, h=h, l=l, c=c, P=P, st=st, zl=zl5, zs=zs5, ph=ph, r14=r14)


def signals(B, k):
    """flip signals on tf k (state becomes buy/sell from something else)."""
    s = B["P"][k]["s"]
    prev = np.concatenate([[0], s[:-1]])
    flip = (s != 0) & (s != prev)
    j = np.nonzero(flip)[0]
    d = s[j].astype(int)
    chg = np.nonzero(s[1:] != s[:-1])[0] + 1
    pos = np.searchsorted(chg, j + 1)
    nxt = np.where(pos < len(chg), chg[np.minimum(pos, len(chg) - 1)], len(s))
    m = j * k + k - 1
    mm = np.minimum(m, len(B["c"]) - 1)
    conf = np.where(d == 1, B["zl"][mm], B["zs"][mm]) & (B["st"][1][mm] == d) & (B["st"][2][mm] == d) & (B["st"][3][mm] == d)
    return dict(m=m, j=j, d=d, conf=conf, runend_m=nxt * k + k - 1)


def sim(o, h, l, e, d, S, tlen):
    """Vectorised trade sim. entry at open[e]; stop at entry-d*S checked on bars e..e+tlen-1 (stop wins, gap fills at open);
    else exit at open[e+tlen]. Returns gross R, held bars, entry price."""
    n = len(e)
    gR = np.zeros(n)
    held = np.zeros(n, dtype=int)
    entry = o[e]
    order = np.argsort(tlen)
    CH = 3000
    for a in range(0, n, CH):
        ii = order[a:a + CH]
        L = int(tlen[ii].max())
        ar = np.arange(L)[None, :]
        idx = e[ii][:, None] + ar
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
    return gR, held, entry


def trades_for(B, k):
    sg = signals(B, k)
    n5 = len(B["c"])
    e = sg["m"] + 1
    cap_t = CAP * k
    at_all = B["P"][k]["atr"][sg["j"]]
    ok = (e + cap_t + 1 < n5) & ~np.isnan(at_all)
    idx = np.nonzero(ok)[0]
    e = e[idx]; d = sg["d"][idx]; at = at_all[idx]; conf = sg["conf"][idx]
    tmax = np.minimum(sg["runend_m"][idx] + 1, e + cap_t)
    tlen = np.maximum(tmax - e, 1)
    S = np.maximum(STOP_ATR * at, STOP_PCT * B["o"][e])
    g, held, entry = sim(B["o"], B["h"], B["l"], e, d, S, tlen)
    ts = B["grid"][e]
    dayi = ((ts - B["grid"][0]) // 86400000).astype(int)
    ph = B["ph"][np.minimum(dayi, len(B["ph"]) - 1)]
    return dict(e=e, d=d, conf=conf, g=g, held=held, costu=entry / S, S=S, ts=ts, day=ts // 86400000, ph=ph, k=k)
