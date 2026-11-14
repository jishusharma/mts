"""nkp1: NK1 (first-hour low break + VWAP) and NK5 (session open 15/10/5) re-tested inside 6 MTS phases x 8 context layers.
Implements PRE_REG.md and MTS_BRAINS_SPEC_1114 exactly. Rule machinery is ported from the NK1/NK5 studies (branches
JIS-NB/nk1-first-hour-low-break-vwap-1114, JIS-NB/nk5-session-open-15-10-5-1114), with the changes listed in PRE_REG.md.
STUDY_BUG=1 = deliberate look-ahead (tests only). PHASE_LAG=0 = look-ahead phase (tests only).
Usage: python study.py build   (per-coin candidates -> cache)   |   python study.py analyze (selection on DEV, VAL once)."""
import os, sys, json, datetime as dt
from zoneinfo import ZoneInfo
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phases as PH
import ctx as CX

CACHE = r"F:\MTS\data_cache\binance"
CTXDIR = r"F:\MTS\data_cache"
OUTC = r"F:\MTS\data_cache\mts_brains\nkp1_cache"
NK1_SYMS = "BTC ETH BNB XRP ADA LTC TRX LINK XLM DOGE ETC BCH SOL DOT AVAX ATOM UNI VET NEO ZEC".split()
NK5_SYMS = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX EOS XLM ETC DASH ZEC BCH ATOM NEO IOTA VET".split()
ALL_SYMS = sorted(set(NK1_SYMS) | set(NK5_SYMS))
MS5, DAY = 300000, 86400000
SPLIT_DAY = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000) // DAY
NY = ZoneInfo("America/New_York")
SESS = {0: ("UTC", 144), 1: ("NY", 78)}
NEAR, BIGK, MINR, ATRK = 0.001, 2.5, 0.005, 0.6
FEE_T, FEE_M = 0.0012, 0.0006
BIG = 10 ** 9
VARIANTS = ["NK1-UTC", "NK1-NY", "NK5-NYasia", "NK5-UTC4h"]


def bug():
    return os.environ.get("STUDY_BUG") == "1"


# ------------------------------------------------------------------ data
def load5(sym):
    a = np.load(os.path.join(CACHE, f"{sym}USDT_5m.npz"))["a"]
    _, ix = np.unique(a[:, 0], return_index=True)
    return a[ix]


def df_from(a):
    idx = pd.to_datetime(a[:, 0].astype("int64"), unit="ms", utc=True)
    return pd.DataFrame(a[:, 1:6], index=idx, columns=list("ohlcv"))


def read_ctx_files(sym):
    p = lambda sub, n: os.path.join(CTXDIR, sub, "nkp1", f"{sym}USDT_{n}.csv")
    rd = lambda f: pd.read_csv(f) if os.path.exists(f) else None
    return rd(p("binance_spot", "1d_tbv")), rd(p("binance_futures", "oi_daily")), rd(p("binance_futures", "funding"))


def fund_arrays(fund):
    if fund is None or not len(fund):
        return None
    ts = fund.ts.to_numpy()
    return ts, np.r_[0.0, np.cumsum(fund.rate.to_numpy())]


def fund_sum(fa, t_in, t_out):
    """sum of funding rates for settlements with t_in < ts <= t_out (fraction of notional; long pays positive)."""
    if fa is None:
        return np.zeros(len(t_in))
    ts, cum = fa
    return cum[np.searchsorted(ts, t_out, side="right")] - cum[np.searchsorted(ts, t_in, side="right")]


# ------------------------------------------------------------------ NK1 (ported, E3 session-end exit only)
def daily_hl(a):
    d = (a[:, 0] // DAY).astype(np.int64)
    ud, st = np.unique(d, return_index=True)
    return ud, st


def open_ms(day, kind):
    if kind == 0:
        return day * DAY
    d = dt.datetime.fromtimestamp(day * DAY / 1000, dt.timezone.utc)
    return int(dt.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY).timestamp() * 1000)


def sim_e3(e, entryF, Rd, lowF, openF, closeF, n):
    """long in flipped coordinates, entered at the open of bar e. Stop first; gap fills at the worse price. Returns exit price, exit bar."""
    stop = entryF - Rd
    sh = np.flatnonzero(lowF[e:] <= stop)
    if sh.size:
        k = sh[0]
        return min(stop, openF[e + k]), e + k
    return closeF[n - 1], n - 1


def nk1_coin(sym, a, val_pool=True):
    """returns (signal rows, pool rows). Signal rows: every NK1 signal both sides (phase filter applied later)."""
    t = a[:, 0].astype(np.int64)
    O, H, L, C, V = a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5]
    rg = H - L
    crg = np.r_[0, np.cumsum(rg)]
    pcl = np.r_[C[0], C[:-1]]
    tr = np.maximum(rg, np.maximum(abs(H - pcl), abs(L - pcl)))
    ctr = np.r_[0, np.cumsum(tr)]
    first_day = int(t[0] // DAY) + 40
    last_day = int(t[-1] // DAY)
    sig, pool = [], []
    for day in range(first_day, last_day + 1):
        for kind in (0, 1):
            nb = SESS[kind][1]
            om = open_ms(day, kind)
            i0 = int(np.searchsorted(t, om))
            if i0 < 21 or i0 + nb > len(t) or t[i0] != om or t[i0 + nb - 1] != om + (nb - 1) * MS5:
                continue
            sl = slice(i0, i0 + nb)
            sO, sH, sL, sC, sV = O[sl], H[sl], L[sl], C[sl], V[sl]
            cv = np.cumsum(sV)
            if cv[0] <= 0:
                continue
            typ = (sH + sL + sC) / 3
            vw = np.cumsum(typ * sV) / cv
            mr20 = (crg[i0] - crg[i0 - 20]) / 20
            exit_ms = om + nb * MS5
            var = "NK1-UTC" if kind == 0 else "NK1-NY"
            for side in (1, -1):
                lowF = sL if side > 0 else -sH
                openF, closeF, vwF = side * sO, side * sC, side * vw
                # pool (VAL only, any day, 10 candidate entry bars b3..b12; same structural/min-stop rule)
                if val_pool and day >= SPLIT_DAY:
                    pr, pR, pe = np.empty(10), np.empty(10), np.empty(10, dtype=np.int64)
                    for q, e2 in enumerate(range(3, 13)):
                        en2 = openF[e2]
                        atr2 = (ctr[i0 + e2] - ctr[i0 + e2 - 14]) / 14
                        Rd2 = max(en2 - lowF[:e2].min(), MINR * abs(en2), ATRK * atr2)
                        ex2, _ = sim_e3(e2, en2, Rd2, lowF, openF, closeF, nb)
                        pr[q], pR[q], pe[q] = (ex2 - en2) / abs(en2), Rd2 / abs(en2), om + e2 * MS5
                    pool.append(dict(variant=var, sym=sym, day=day, side=side, anchor_ms=om, exit_ms=exit_ms, pr=pr, pR=pR, pe=pe))
                L0 = lowF[:3].min()
                bk = next((k for k in range(3, 12) if lowF[k] < L0), None)
                if bk is None:
                    continue
                bc = next((k for k in range(bk, 12) if closeF[k] > L0), None)
                if bc is None or sH[bc] - sL[bc] > BIGK * mr20:
                    continue
                j = next((k for k in range(bc, 12) if closeF[k] >= vwF[k] - NEAR * abs(vwF[k]) and closeF[k] > L0), None)
                if j is None:
                    continue
                e = j + 1
                atr = (ctr[i0 + j + 1] - ctr[i0 + j + 1 - 14]) / 14
                struct = lowF[:j + 1].min()
                entT = lowF[e] if bug() else openF[e]   # STUDY_BUG=1: enter at the next bar's best price (look-ahead)
                Rd = max(entT - struct, MINR * abs(entT), ATRK * atr)
                ex, xb = sim_e3(e, entT, Rd, lowF, openF, closeF, nb)
                rec = dict(variant=var, sym=sym, day=day, side=side, anchor_ms=om, entry_ms=om + e * MS5,
                           exit_ms=om + (xb + 1) * MS5 if xb < nb - 1 else exit_ms, ret=(ex - entT) / abs(entT), Rf=Rd / abs(entT),
                           filled_m=False, ret_m=np.nan, Rf_m=np.nan)
                lim = closeF[j]
                if lowF[e] <= lim:
                    enm = min(openF[e], lim)
                    Rm = max(enm - struct, MINR * abs(enm), ATRK * atr)
                    exm, _ = sim_e3(e, enm, Rm, lowF, openF, closeF, nb)
                    rec.update(filled_m=True, ret_m=(exm - enm) / abs(enm), Rf_m=Rm / abs(enm))
                sig.append(rec)
    return sig, pool


# ------------------------------------------------------------------ NK5 (ported; stop gap-aware)
def rsi(c, n):
    return CX.rsi_wilder(c, n)


def wma(x, n):
    w = np.arange(n, 0, -1, dtype=float)
    return sum(w[k] * x.shift(k) for k in range(n)) / w.sum()


def hm_state(c):
    """+1 buy (red<green), -1 sell. green=EMA3(RSI9), red=WMA21(RSI9) [OURS reconstruction]."""
    r = rsi(c, 9)
    g = r.ewm(span=3, adjust=False).mean()
    red = wma(r, 21)
    s = pd.Series(0, index=c.index)
    s[red < g] = 1
    s[red > g] = -1
    s[red.isna() | g.isna()] = 0
    return s


def atr_s(df, n=14):
    pc = df.c.shift()
    tr = pd.concat([df.h - df.l, (df.h - pc).abs(), (df.l - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def nk5_coin(sym, df5):
    grid = pd.date_range(df5.index[0], df5.index[-1], freq="5min", tz="UTC")
    df = df5.reindex(grid)
    df[["o", "h", "l", "c"]] = df[["o", "h", "l", "c"]].ffill()
    df["v"] = df["v"].fillna(0)
    d1 = CX.resample(df, "1D", 288)
    r15 = rsi(CX.resample(df, "15min", 3).c, 14)
    lo4, hi4 = r15.rolling(4).min(), r15.rolling(4).max()
    hm10, hm5 = hm_state(CX.resample(df, "10min", 2).c), hm_state(df.c)
    atr1 = atr_s(CX.resample(df, "1h", 12), 14)
    o5, h5, l5, c5 = df.o.to_numpy(), df.h.to_numpy(), df.l.to_numpy(), df.c.to_numpy()
    t0 = df.index[0]
    five = pd.Timedelta(minutes=5)
    sh = pd.Timedelta(minutes=15) if bug() else pd.Timedelta(0)
    recs = []
    days = d1.index[d1.index >= d1.index[0] + pd.Timedelta(days=30)]
    spec = [("NK5-NYasia", "NY", None), ("NK5-UTC4h", "UTC", 4)]
    for var, kind, hh in spec:
        for d in days:
            T = pd.Timestamp(d.year, d.month, d.day, tz="UTC") if kind == "UTC" else pd.Timestamp(d.year, d.month, d.day, 16, tz=NY).tz_convert("UTC")
            if T < t0 or T > df.index[-1] - pd.Timedelta(hours=14):
                continue
            Tb = T + sh
            lo = lo4.get(Tb - pd.Timedelta(minutes=15), np.nan)
            hi = hi4.get(Tb - pd.Timedelta(minutes=15), np.nan)
            s10 = hm10.get(Tb - pd.Timedelta(minutes=10), 0)
            s5 = hm5.get(Tb - pd.Timedelta(minutes=5), 0)
            a1 = atr1.get(T.floor("1h") - pd.Timedelta(hours=1), np.nan)
            i0 = int((T - t0) / five)
            if np.isnan(a1) or np.isnan(lo) or i0 < 1 or i0 >= len(o5):
                continue
            E = T + pd.Timedelta(hours=hh) if hh else (T.normalize() + pd.Timedelta(days=1, hours=8))
            i1 = int((E - t0) / five)
            if i1 >= len(o5):
                continue
            entry = o5[i0]
            S = max(0.005 * entry, 0.6 * a1)
            sigL, sigS = bool(lo <= 35 and s10 == 1 and s5 == 1), bool(hi >= 65 and s10 == -1 and s5 == -1)
            for side, sg in ((1, sigL), (-1, sigS)):
                # taker: entry at the 5m open at T; stop at entry -/+ S; gap fills at the worse price; time exit at the open of bar i1
                ent = entry
                fillm = None
                for mk in (0, 1):
                    if mk == 1:
                        lim = c5[i0 - 1]   # maker: limit at the prior 5m close; fills if the bar at T trades through it
                        if not ((l5[i0] <= lim) if side > 0 else (h5[i0] >= lim)):
                            break
                        ent = lim
                    stop = ent - side * S
                    seg = l5[i0:i1] if side > 0 else h5[i0:i1]
                    hit = np.flatnonzero(seg <= stop) if side > 0 else np.flatnonzero(seg >= stop)
                    if hit.size:
                        k = hit[0]
                        bo = o5[i0 + k]
                        px = min(stop, bo) if side > 0 else max(stop, bo)
                        xi = i0 + k + 1
                    else:
                        px, xi = o5[i1], i1
                    ret = side * (px - ent) / ent
                    rf = S / ent
                    if mk == 0:
                        r0 = dict(variant=var, sym=sym, day=int(CX.ms_ts(T) // DAY), side=side, sig=sg, anchor_ms=CX.ms_ts(T),
                                  entry_ms=CX.ms_ts(T), exit_ms=CX.ms_ts(t0) + xi * MS5, ret=ret, Rf=rf,
                                  filled_m=False, ret_m=np.nan, Rf_m=np.nan, d_lo=lo, d_hi=hi, d_s10=s10, d_s5=s5)
                    else:
                        r0.update(filled_m=True, ret_m=ret, Rf_m=rf)
                recs.append(r0)
    return recs


# ------------------------------------------------------------------ per-coin job
def attach(df, sym, ctx):
    c = ctx.at(df.anchor_ms.to_numpy())
    for k in c.columns:
        df[k] = c[k].to_numpy()
    return df


def coin_job(sym):
    os.makedirs(OUTC, exist_ok=True)
    out = os.path.join(OUTC, f"{sym}.pkl" if not bug() else f"{sym}_bug.pkl")
    a = load5(sym)
    df5 = df_from(a)
    spot, oi, fund = read_ctx_files(sym)
    ctx = CX.Ctx(df5, spot, oi, fund)
    fa = fund_arrays(fund)
    res = dict(sym=sym, first=ctx.first, funding=fa is not None)
    parts, pools = [], []
    if sym in NK1_SYMS:
        s, p = nk1_coin(sym, a)
        d = pd.DataFrame(s)
        if len(d):
            d["sig"] = True
            parts.append(d)
        pools.extend(p)
    if sym in NK5_SYMS:
        d = pd.DataFrame(nk5_coin(sym, df5))
        if len(d):
            parts.append(d)
    TR = pd.concat(parts, ignore_index=True)
    TR = attach(TR, sym, ctx)
    TR["fund"] = fund_sum(fa, TR.entry_ms.to_numpy(), TR.exit_ms.to_numpy()) * TR.side.to_numpy()
    PL = pd.DataFrame(pools)
    if len(PL):
        PL = attach(PL, sym, ctx)
        pe = np.stack(PL.pe.to_numpy())
        ex = PL.exit_ms.to_numpy()
        side = PL.side.to_numpy()
        PL["pf"] = list(np.stack([fund_sum(fa, pe[:, k], ex) * side for k in range(10)], axis=1))
    res.update(TR=TR, PL=PL)
    pd.to_pickle(res, out)
    return sym, len(TR), len(PL)


def build(syms=ALL_SYMS, workers=4):
    with ProcessPoolExecutor(workers) as ex:
        for r in ex.map(coin_job, syms):
            print(r, flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        build(sys.argv[2].split(",") if len(sys.argv) > 2 else ALL_SYMS)
    elif len(sys.argv) > 1 and sys.argv[1] == "analyze":
        import analyze
        analyze.main()
