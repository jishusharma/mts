"""NK layers + MTS context layers + trade simulation for nkp4 (see PRE_REG.md). Causal: every context value at 15m bar i
uses only bars whose close time <= close time of bar i. STUDY_BUG=1 injects deliberate look-ahead (tests must fail)."""
import os
import numpy as np, pandas as pd
import nkp4_phases as PH

ROOT = PH.ROOT
SLUG = "nkp4-nk-plus-mts-confluence-1114"
SPOT15 = ROOT / "binance_spot"
FUTD = ROOT / "binance" / SLUG
SPOTD = ROOT / "binance_spot" / SLUG
SYMS = "BTC ETH BNB XRP ADA DOGE SOL LTC TRX LINK DOT AVAX ATOM ETC XLM BCH UNI NEAR FIL ALGO".split()
K = 4; HOLD = 24; TGT_R = 2.0
M15, H1, H4, D1 = 900_000, 3_600_000, 14_400_000, 86_400_000
VAL_START = int(pd.Timestamp("2024-01-01", tz="UTC").timestamp() * 1000)
BUG = bool(os.environ.get("STUDY_BUG"))
LAYERS = ["C1_rsi4h", "C2_wt1d", "C3_pctb4h", "C4_oi24h", "C5_fund3", "C6_td24", "C7_rv", "C8_sess"]
BUCKETS = {"C1_rsi4h": ["LOW<=40", "MID", "HIGH>=60"], "C2_wt1d": ["OS<=-53", "MID", "OB>=53"],
           "C3_pctb4h": ["LOW<0.10", "MID", "HIGH>0.90"], "C4_oi24h": ["UNWIND<=-3%", "FLAT", "BUILD>=3%"],
           "C5_fund3": ["NEG<0", "NORMAL", "HOT>0.03%"], "C6_td24": ["BULL-DIV", "AGREE", "BEAR-DIV"],
           "C7_rv": ["COMPRESS<0.7", "NORMAL", "EXPAND>1.3"], "C8_sess": ["ASIA", "EU", "US"]}


# ---------- loading ----------
def load15(sym, end_ts=None):
    d = np.load(SPOT15 / f"{sym}USDT_15m.npz")
    out = {k: d[k] for k in ("o", "h", "l", "c", "v")}
    out["ts"] = d["ts"] if "ts" in d.files else d["t"]
    if end_ts is not None:
        m = out["ts"] < end_ts
        out = {k: v[m] for k, v in out.items()}
    return out


def load_aux(sym, end_ts=None):
    aux = {}
    for key, p in (("h1", SPOTD / f"{sym}USDT_1h.npz"), ("oi", FUTD / f"{sym}USDT_oi_1h.npz"),
                   ("fund", FUTD / f"{sym}USDT_funding.npz")):
        if p.exists():
            d = np.load(p); aux[key] = {k: d[k] for k in d.files}
    if end_ts is not None:
        for k, v in list(aux.items()):
            m = v["ts"] < end_ts
            aux[k] = {kk: vv[m] for kk, vv in v.items()}
    return aux


# ---------- primitives ----------
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
    if a.dtype == bool: fill = False
    out = np.full(len(a), fill, dtype=a.dtype)
    if k > 0: out[k:] = a[:-k]
    else: out[:] = a
    return out


def roll_any(b, n):
    c = np.cumsum(b.astype(np.int32)); out = c.copy()
    out[n:] = c[n:] - c[:-n]
    return out > 0


def pick_by_key(keys, vals, q):
    """vals at keys equal to q (NaN where q is not a key). keys sorted unique."""
    pos = np.clip(np.searchsorted(keys, q), 0, len(keys) - 1)
    ok = keys[pos] == q
    out = np.full(len(q), np.nan)
    out[ok] = vals[pos[ok]]
    return out


def resample(ts, o, h, l, c, step):
    """Complete blocks only, keyed by block index ts//step (block k covers [k*step,(k+1)*step))."""
    k = ts // step
    uk, st, cnt = np.unique(k, return_index=True, return_counts=True)
    full = cnt == step // M15
    en = st + cnt
    H = np.maximum.reduceat(h, st); L = np.minimum.reduceat(l, st)
    return uk[full], o[st][full], H[full], L[full], c[en - 1][full]


def wavetrend(h, l, c, n1=10, n2=21):
    ap = (h + l + c) / 3
    esa = pd.Series(ap).ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    ci = (ap - esa) / (0.015 * d)
    return ci.ewm(span=n2, adjust=False).mean().to_numpy()


def three(x, lo, hi, strict=False):
    """3 buckets, -1 where NaN. strict: < lo / > hi, else <= lo / >= hi."""
    out = np.full(len(x), -1, dtype=np.int8)
    ok = ~np.isnan(x)
    out[ok] = 1
    if strict:
        out[ok & (x < lo)] = 0; out[ok & (x > hi)] = 2
    else:
        out[ok & (x <= lo)] = 0; out[ok & (x >= hi)] = 2
    return out


# ---------- context layers: int8 bucket per 15m bar, -1 = no data ----------
def context(D, aux):
    ts = D["ts"]; n = len(ts)
    tc = ts + M15                       # close time of each 15m bar
    ctx = np.full((8, n), -1, dtype=np.int8)
    # C1 RSI14 / C3 %B on 4h: last COMPLETE 4h bar (BUG: block containing bar i, includes future bars)
    k4, o4, h4, l4, c4 = resample(ts, D["o"], D["h"], D["l"], D["c"], H4)
    r4 = rsi(c4, 14)
    mid = pd.Series(c4).rolling(20).mean(); sd = pd.Series(c4).rolling(20).std(ddof=0)
    pb = ((c4 - (mid - 2 * sd)) / (4 * sd)).to_numpy()
    kk = tc // H4 if BUG else tc // H4 - 1
    ctx[0] = three(pick_by_key(k4, r4, kk), 40, 60)
    ctx[2] = three(pick_by_key(k4, pb, kk), 0.10, 0.90, strict=True)
    # C2 daily WaveTrend: last complete day
    kd, od, hd, ld, cd = resample(ts, D["o"], D["h"], D["l"], D["c"], D1)
    wt = wavetrend(hd, ld, cd)
    ctx[1] = three(pick_by_key(kd, wt, tc // D1 if BUG else tc // D1 - 1), -53, 53)
    hh = tc // H1                        # latest hour boundary <= tc
    # C4 OI 24h change (hourly rows stamped at the hour; row available at its stamp)
    if "oi" in aux and len(aux["oi"]["ts"]):
        oi = aux["oi"]; g = pd.Series(oi["oi"], index=oi["ts"] // H1)
        g = g[~g.index.duplicated()]
        full = np.arange(g.index.min(), g.index.max() + 1)
        g = g.reindex(full)
        ch = (g / g.shift(24) - 1).to_numpy()
        ctx[3] = three(pick_by_key(full, ch, hh + 1 if BUG else hh), -0.03, 0.03)
    # C5 funding: mean of last 3 settlements with settle time <= tc
    if "fund" in aux and len(aux["fund"]["ts"]) >= 3:
        fts, fr = aux["fund"]["ts"], aux["fund"]["fr"]
        c3 = np.convolve(fr, np.ones(3) / 3, "valid")        # c3[j] = mean(fr[j:j+3])
        pos = np.searchsorted(fts, tc + 8 * H1 if BUG else tc, "right")
        x = np.full(n, np.nan); m = pos >= 3
        x[m] = c3[pos[m] - 3]
        ctx[4] = three(x, 0.0, 0.0003, strict=True)
    # C6 taker delta vs price, C7 RV7/RV60 on spot 1h klines: last complete hour
    if "h1" in aux and len(aux["h1"]["ts"]):
        a = aux["h1"]; idx = a["ts"] // H1
        full = np.arange(idx.min(), idx.max() + 1)
        s = lambda key: pd.Series(a[key], index=idx).groupby(level=0).last().reindex(full)
        c1, v1, tb1 = s("c"), s("v"), s("tb")
        td = (2 * tb1 - v1).rolling(24, min_periods=24).sum() / v1.rolling(24, min_periods=24).sum()
        p24 = c1 / c1.shift(24) - 1
        lr = np.log(c1).diff()
        rv = lr.rolling(168, min_periods=168).std() / lr.rolling(1440, min_periods=1440).std()
        kh = hh if BUG else hh - 1
        tdi = pick_by_key(full, td.to_numpy(), kh); pi = pick_by_key(full, p24.to_numpy(), kh)
        out = np.full(n, -1, dtype=np.int8); ok = ~np.isnan(tdi) & ~np.isnan(pi)
        out[ok] = 1; out[ok & (pi < 0) & (tdi > 0)] = 0; out[ok & (pi > 0) & (tdi < 0)] = 2
        ctx[5] = out
        ctx[6] = three(pick_by_key(full, rv.to_numpy(), kh), 0.7, 1.3, strict=True)
    hour = (ts % D1) // H1
    ctx[7] = np.where((hour < 7) | (hour >= 21), 0, np.where(hour < 13, 1, 2)).astype(np.int8)
    return ctx


# ---------- NK layers (from nk6 study; daily ADX phase removed) ----------
def nk_layers(D):
    ts, o, h, l, c, v = (D[k] for k in ("ts", "o", "h", "l", "c", "v"))
    n = len(c); day = ts // D1; tod = (ts % D1) // M15
    ud, st = np.unique(day, return_index=True)
    en = np.r_[st[1:], n]
    dh = np.maximum.reduceat(h, st); dl = np.minimum.reduceat(l, st); dc = c[en - 1]
    ix = np.searchsorted(ud, day)
    P_d = (dh + dl + dc) / 3; R1_d = 2 * P_d - dl; S1_d = 2 * P_d - dh
    P, R1, S1 = (sh(x, 1)[ix] for x in (P_d, R1_d, S1_d))
    fh = tod < 4
    dfh_h = pd.Series(np.where(fh, h, -np.inf)).groupby(day).transform("max").to_numpy()
    dfh_l = pd.Series(np.where(fh, l, np.inf)).groupby(day).transform("min").to_numpy()
    ok1 = tod >= 4
    pc = sh(c, 1)
    L1l = ok1 & (pc <= dfh_l) & (c > dfh_l); L1s = ok1 & (pc >= dfh_h) & (c < dfh_h)
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
    ev = lambda b: roll_any(np.nan_to_num(b).astype(bool), K)
    long = np.stack([ev(L1l), ev(L2l), ev(L3l), np.nan_to_num(L4l).astype(bool), ev(L5l)])
    short = np.stack([ev(L1s), ev(L2s), ev(L3s), np.nan_to_num(L4s).astype(bool), ev(L5s)])
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    atr = pd.Series(np.nan_to_num(tr)).ewm(alpha=1 / 14, adjust=False).mean().to_numpy()
    return long, short, atr


# ---------- rules ----------
RULES = ["N1_firsthour", "N2_pivots", "N3_breakretest", "N4_hilega", "N5_rsi3070", "NN_nkcount2",
         "X1_nk+mts>=1", "X2_nk+mts>=2", "X3_nk+mts>=3"]


def mts_agree(ctx, dirn):
    """Count of MTS context layers in the exhaustion-in-direction bucket (long: LOW/OS/LOW/UNWIND/NEG/BULL-DIV; short: mirror)."""
    b = 0 if dirn > 0 else 2
    return sum((ctx[i] == b).astype(np.int8) for i in range(6))


def rule_signals(nk, ctx, dirn):
    cnt = nk.sum(0)
    ag = mts_agree(ctx, dirn)
    sig = {RULES[i]: nk[i] for i in range(5)}
    sig["NN_nkcount2"] = cnt >= 2
    for k in (1, 2, 3):
        sig[f"X{k}_nk+mts>={k}"] = (cnt >= 1) & (ag >= k)
    return sig


# ---------- simulation ----------
def simulate(D, atr, dirn, maker=False):
    """Signal at bar i. Taker: entry next open. Maker: limit at close[i], filled only if bar i+1 trades through it.
    Stop S = max(1.0 ATR14, 0.5% entry) (>= max(0.6 ATR, 0.5%)); target 2R; time exit 24 bars at close.
    A stop gapped through fills at the open when worse than the stop. Same-bar stop and target = stop."""
    o, h, l, c = D["o"], D["h"], D["l"], D["c"]; n = len(c)
    m = n - HOLD - 2
    i = np.arange(m)
    entry = c[i].copy() if maker else o[i + 1]
    S = np.maximum(1.0 * atr[i], 0.005 * entry)
    sgn = 1.0 if dirn > 0 else -1.0
    stop = entry - sgn * S; tgt = entry + sgn * TGT_R * S
    res = np.full(m, np.nan); ex = np.full(m, -1); done = np.zeros(m, bool)
    for k in range(1, HOLD + 1):
        j = i + k
        hs = (l[j] <= stop) if sgn > 0 else (h[j] >= stop)
        ht = (h[j] >= tgt) if sgn > 0 else (l[j] <= tgt)
        gap = (o[j] <= stop) if sgn > 0 else (o[j] >= stop)
        s_hit = hs & ~done; t_hit = ht & ~hs & ~done
        r_stop = np.where(gap, sgn * (o[j] - entry) / S, -1.0)
        res[s_hit] = r_stop[s_hit]; res[t_hit] = TGT_R
        ex[s_hit | t_hit] = j[s_hit | t_hit]
        done |= hs | ht
    nd = ~done
    res[nd] = sgn * (c[i[nd] + HOLD] - entry[nd]) / S[nd]; ex[nd] = i[nd] + HOLD
    feeR = 1e-4 * entry / S                     # multiply by fee in bp
    filled = np.ones(m, bool)
    if maker:
        filled = (l[i + 1] <= entry) if sgn > 0 else (h[i + 1] >= entry)
    pad = lambda a, f: np.r_[a, np.full(n - m, f)]
    return pad(res, np.nan), pad(feeR, np.nan), pad(ex, n), pad(filled, False)


def pick(sig, ex, elig):
    onset = sig & ~sh(sig, 1) & elig
    idx = np.flatnonzero(onset); keep = []; free = -1
    for i in idx:
        if i >= free:
            keep.append(i); free = ex[i] + 1
    return np.array(keep, dtype=int)


# ---------- phase attach ----------
def phase_arrays(ts, ptab):
    """Phase code (0..5, -1 none) and 40d range bounds per 15m bar, from the daily phase table (lag is inside the table)."""
    day = pd.to_datetime((ts // D1) * D1, unit="ms")
    lab = ptab["label"].reindex(day).to_numpy(dtype=object)
    code = np.full(len(ts), -1, dtype=np.int8)
    for j, nm in enumerate(PH.LABELS):
        code[lab == nm] = j
    return code, ptab["lo40"].reindex(day).to_numpy(float), ptab["hi40"].reindex(day).to_numpy(float)


def appropriate(code, lo, hi, close, dirn):
    """+1 phase-appropriate, -1 opposite, 0 neutral. ACCUM-RANGE: long at lower third of the 40d range, short at upper third."""
    app = np.zeros(len(code), dtype=np.int8)
    for j, nm in enumerate(PH.LABELS):
        d = PH.PHASE_DIR[nm]
        if d != 0:
            app[code == j] = 1 if d == dirn else -1
    m = code == PH.LABELS.index("ACCUM-RANGE")
    with np.errstate(invalid="ignore", divide="ignore"):
        pos = (close - lo) / (hi - lo)
    app[m & (pos <= 1 / 3)] = 1 if dirn > 0 else -1
    app[m & (pos >= 2 / 3)] = 1 if dirn < 0 else -1
    return app


def build_coin(sym, ptab, end_ts=None):
    """Per-bar arrays for both directions and the picked-trade indices for every rule."""
    D = load15(sym, end_ts); aux = load_aux(sym, end_ts)
    nkl, nks, atr = nk_layers(D)
    ctx = context(D, aux)
    code, lo, hi = phase_arrays(D["ts"], ptab)
    out = dict(D=D, ctx=ctx, code=code, bars={}, trades={}, aux_first={k: int(v["ts"][0]) for k, v in aux.items() if len(v["ts"])})
    for dirn, nk in ((1, nkl), (-1, nks)):
        gross, feeR, ex, _ = simulate(D, atr, dirn)
        gm, fm, exm, fill = simulate(D, atr, dirn, maker=True)
        app = appropriate(code, lo, hi, D["c"], dirn)
        valid = ~np.isnan(gross) & (code >= 0)
        out["bars"][dirn] = dict(gross=gross, feeR=feeR, gm=gm, fm=fm, fill=fill, app=app, valid=valid)
        for rn, sg in rule_signals(nk, ctx, dirn).items():
            out["trades"][(rn, dirn)] = pick(sg, ex, valid)
    return out
