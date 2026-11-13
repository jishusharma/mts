"""NK confluence combos. Self-contained; see PRE_REG.md. Layers + trade simulation."""
import os, itertools
import numpy as np, pandas as pd

CACHE = r"F:\MTS\data_cache\binance_spot"
SYMS = "BTC ETH BNB XRP ADA DOGE SOL LTC TRX LINK DOT AVAX ATOM ETC XLM BCH UNI NEAR FIL ALGO".split()
K = 4; HOLD = 24; TGT_R = 2.0
BUG = bool(os.environ.get("STUDY_BUG"))


def load(sym):
    d = np.load(f"{CACHE}\\{sym}USDT_15m.npz")
    return {k: d[k] for k in ("ts", "o", "h", "l", "c", "v")}


def rsi(c, n):
    s = pd.Series(c); d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn.replace(0, np.nan))).to_numpy()


def wma(x, n):
    w = np.arange(1, n + 1, dtype=float); out = np.full(len(x), np.nan)
    if len(x) >= n:
        out[n - 1:] = np.convolve(np.nan_to_num(x), w[::-1], "valid") / w.sum()
    return out


def sh(a, k, fill=np.nan):
    """value k bars ago."""
    if a.dtype == bool: fill = False
    out = np.full(len(a), fill, dtype=a.dtype)
    if k > 0: out[k:] = a[:-k]
    else: out[:] = a
    return out


def roll_any(b, n):
    c = np.cumsum(b.astype(np.int32)); out = c.copy()
    out[n:] = c[n:] - c[:-n]
    return out > 0


def daily_phase(day, h, l, c):
    """phase per unique day from that day's own close: 1 UP, -1 DOWN, 0 RANGE, nan warmup."""
    ud, st = np.unique(day, return_index=True)
    en = np.r_[st[1:], len(day)]
    dh = np.maximum.reduceat(h, st); dl = np.minimum.reduceat(l, st); dc = c[en - 1]
    pc = sh(dc, 1)
    tr = np.maximum(dh - dl, np.maximum(abs(dh - pc), abs(dl - pc)))
    up = dh - sh(dh, 1); dn = sh(dl, 1) - dl
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    e = lambda x: pd.Series(x).ewm(alpha=1 / 14, adjust=False).mean().to_numpy()
    atr = e(np.nan_to_num(tr)); pdi = 100 * e(pdm) / atr; mdi = 100 * e(mdm) / atr
    dx = 100 * abs(pdi - mdi) / (pdi + mdi); adx = e(np.nan_to_num(dx))
    sma = pd.Series(dc).rolling(20).mean().to_numpy(); slope = sma - sh(sma, 5)
    ph = np.where((adx >= 20) & (pdi > mdi) & (slope > 0), 1.0,
                  np.where((adx >= 20) & (mdi > pdi) & (slope < 0), -1.0, 0.0))
    ph[:60] = np.nan
    return ud, ph, dict(dh=dh, dl=dl, dc=dc, adx=adx, pdi=pdi, mdi=mdi, sma=sma)


def features(D):
    ts, o, h, l, c, v = (D[k] for k in ("ts", "o", "h", "l", "c", "v"))
    n = len(c); day = ts // 86400000; tod = (ts % 86400000) // 900000
    ud, ph_d, dd = daily_phase(day, h, l, c)
    ph_use = ph_d if BUG else sh(ph_d, 1)          # BUG: same-day close = look-ahead
    ix = np.searchsorted(ud, day)
    phase = ph_use[ix]
    P_d = (dd["dh"] + dd["dl"] + dd["dc"]) / 3; R1_d = 2 * P_d - dd["dl"]; S1_d = 2 * P_d - dd["dh"]
    P, R1, S1 = (sh(x, 1)[ix] for x in (P_d, R1_d, S1_d))
    fh = tod < 4
    dfh_h = pd.Series(np.where(fh, h, -np.inf)).groupby(day).transform("max").to_numpy()
    dfh_l = pd.Series(np.where(fh, l, np.inf)).groupby(day).transform("min").to_numpy()
    # first-hour range is only known once the 4th bar closes: ok1 enforces tod>=4
    ok1 = tod >= 4
    pc = sh(c, 1)
    L1l = ok1 & (pc <= dfh_l) & (c > dfh_l)
    L1s = ok1 & (pc >= dfh_h) & (c < dfh_h)
    xup = lambda x: (pc <= x) & (c > x)
    xdn = lambda x: (pc >= x) & (c < x)
    L2l = xup(P) | xup(S1) | xup(R1) | ((l <= S1) & (c > S1))
    L2s = xdn(P) | xdn(S1) | xdn(R1) | ((h >= R1) & (c < R1))
    U = sh(pd.Series(h).rolling(20).max().to_numpy(), 7); Dn = sh(pd.Series(l).rolling(20).min().to_numpy(), 7)
    bu = (c > U) & (pc <= sh(U, 1)); bd = (c < Dn) & (pc >= sh(Dn, 1))
    L3l = np.zeros(n, bool); L3s = np.zeros(n, bool)
    for k in range(1, 7):
        Uk, Dk = sh(U, k), sh(Dn, k); buk = sh(bu, k); bdk = sh(bd, k)
        L3l |= (buk & (l <= Uk * 1.001) & (c > Uk)) | (bdk & (c > Dk))
        L3s |= (bdk & (h >= Dk * 0.999) & (c < Dk)) | (buk & (c < Uk))
    r9 = rsi(c, 9); e3 = pd.Series(r9).ewm(span=3, adjust=False).mean().to_numpy(); w21 = wma(r9, 21)
    L4l = (r9 > e3) & (e3 > w21); L4s = (r9 < e3) & (e3 < w21)
    r14 = rsi(c, 14); pr = sh(r14, 1)
    L5l = (pr < 30) & (r14 >= 30); L5s = (pr > 70) & (r14 <= 70)
    if BUG:  # deliberate look-ahead: RSI event also fires if the NEXT bar closes up
        L5l = L5l | (np.r_[c[1:], np.nan] > c * 1.01)
    ev = lambda b: roll_any(np.nan_to_num(b).astype(bool), K)
    long = np.stack([ev(L1l), ev(L2l), ev(L3l), np.nan_to_num(L4l).astype(bool), ev(L5l)])
    short = np.stack([ev(L1s), ev(L2s), ev(L3s), np.nan_to_num(L4s).astype(bool), ev(L5s)])
    tp = (h + l + c) / 3
    vw = (pd.Series(tp * v).groupby(day).cumsum() / pd.Series(v).groupby(day).cumsum()).to_numpy()
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    atr = pd.Series(np.nan_to_num(tr)).ewm(alpha=1 / 14, adjust=False).mean().to_numpy()
    return dict(long=long, short=short, phase=phase, vwap=vw, atr=atr, day=day, ud=ud, dd=dd, P=P, R1=R1, S1=S1)


def simulate(D, atr, direction):
    """Gross R, fee_R per 1bp... (feeR = 1e-4*entry/S), exit index; entry at open[i+1] after signal at bar i."""
    o, h, l, c = D["o"], D["h"], D["l"], D["c"]; n = len(c)
    m = n - HOLD - 2
    i = np.arange(m)
    entry = o[i + 1]; S = np.maximum(1.0 * atr[i], 0.005 * entry)
    sgn = 1.0 if direction > 0 else -1.0
    stop = entry - sgn * S; tgt = entry + sgn * TGT_R * S
    res = np.full(m, np.nan); ex = np.full(m, -1)
    done = np.zeros(m, bool)
    for k in range(1, HOLD + 1):
        j = i + k
        hs = (l[j] <= stop) if sgn > 0 else (h[j] >= stop)
        ht = (h[j] >= tgt) if sgn > 0 else (l[j] <= tgt)
        s_hit = hs & ~done; t_hit = ht & ~hs & ~done
        res[s_hit] = -1.0; res[t_hit] = TGT_R; ex[s_hit | t_hit] = j[s_hit | t_hit]
        done |= hs | ht
    nd = ~done
    res[nd] = sgn * (c[i[nd] + HOLD] - entry[nd]) / S[nd]; ex[nd] = i[nd] + HOLD
    feeR = 1e-4 * entry / S
    pad = lambda a, f: np.r_[a, np.full(n - m, f)]
    return pad(res, np.nan), pad(feeR, np.nan), pad(ex, n)


def combos():
    L = {}
    for a in range(5): L[f"L{a + 1}"] = [a]
    for r in (2, 3):
        for p in itertools.combinations(range(5), r): L["&".join(f"L{x + 1}" for x in p)] = list(p)
    return L


def combo_masks(act):
    cnt = act.sum(0); out = {}
    for nm, idx in combos().items(): out[nm] = act[idx].all(0)
    out["n=1"] = cnt == 1; out["n=2"] = cnt == 2; out["n=3"] = cnt == 3; out["n>=4"] = cnt >= 4
    return out


def pick(sig, ex, elig):
    onset = sig & ~sh(sig, 1) & elig
    idx = np.flatnonzero(onset); keep = []; free = -1
    for i in idx:
        if i >= free:
            keep.append(i); free = ex[i] + 1
    return np.array(keep, dtype=int)


def build_coin(sym):
    D = load(sym); F = features(D)
    out = {}
    for dirn, key in ((1, "long"), (-1, "short")):
        gross, feeR, ex = simulate(D, F["atr"], dirn)
        ph = F["phase"]
        valid = ~np.isnan(gross) & ~np.isnan(ph)
        prim = ((ph == dirn) | (ph == 0)) & valid
        ctl = (ph == -dirn) & valid
        al = (D["c"] > F["vwap"]) if dirn > 0 else (D["c"] < F["vwap"])
        masks = combo_masks(F[key])
        for nm in ("n=1", "n=2", "n=3", "n>=4"): masks[nm + "+VWAP"] = masks[nm] & al
        trades = {(nm, kind): pick(sg, ex, el) for nm, sg in masks.items() for kind, el in (("prim", prim), ("ctl", ctl))}
        out[dirn] = dict(gross=gross, feeR=feeR, ex=ex, trades=trades, prim=prim)
    return D, F, out
