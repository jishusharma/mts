"""Combinatorial edge miner (combo-edge-miner-1114). Library: indicators, causal feature bank, phase labels, trade simulator,
cell statistics. Definitions are frozen in PRE_REG.md. No fee constant is defined here: costs come from MyTradingSys/backtest/fees.py.
STUDY_BUG=1 switches on two deliberate look-aheads (same-day phase, same-day daily flow) so the causality test can prove it bites."""
import os
import sys
import math
import itertools
import datetime as dt
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from MyTradingSys.backtest import fees  # noqa: E402

BUG = bool(os.environ.get("STUDY_BUG"))
DATA = os.environ.get("MINER_DATA", r"F:\MTS\data_cache\binance\combo-edge-miner-1114")
CYCLE_CSV = os.environ.get("MINER_CYCLE", r"F:\MTS\data_cache\btc_cycle_features_1114.csv")
SYMS = "BTC ETH BNB XRP ADA DOGE SOL LTC TRX LINK DOT AVAX ATOM ETC XLM BCH UNI VET ZEC NEO".split()
DAY = 86400000
DATA_END_MS = int(dt.datetime(2026, 11, 13, 20, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)  # only bars closed by then


def day_num(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() // 86400)


START_DAY = day_num(2020, 1, 1)
DEV_END_DAY = day_num(2023, 12, 31)
VAL_START_DAY = day_num(2024, 1, 1)
HALVINGS = [day_num(2012, 11, 28), day_num(2016, 7, 9), day_num(2020, 5, 11), day_num(2024, 4, 20)]
LATE_AFTER = 540  # days since halving: >= 540 is the late half of the cycle (OURS)
PHASES = ["UP_E", "UP_L", "MIX_E", "MIX_L", "DOWN_E", "DOWN_L"]

COST12 = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13   # 12 bp round trip, fees.py
COST6 = COST12 / 2                                       # 6 bp scenario (maker-like), informational

# trade management (frozen in PRE_REG)
STOP_ATR, MIN_STOP, TARGET_R, TRAIL_ATR = 2.5, 0.02, 3.0, 3.0
KINDS = ["T3R", "TRAIL", "RIDE"]          # fixed 3R target / ATR trail / ride until opposite 10d Donchian break
HOLD_DAYS = {"T3R": 30, "TRAIL": 60, "RIDE": 60}

DIR_FEATS = ["BRK20", "BRK5", "RSI_X", "RSI_MOM", "BB_EXT", "SWEEP", "ADX_DI", "TREND_MA", "ABOVE_200", "FLUSH_EXT", "BIGBAR",
             "NB_ABS", "NB_PER"]
NEU_FEATS = ["BB_SQZ", "VOLX", "DD_DEEP", "NEAR_200W", "OI_FLUSH", "OI_BUILD", "OI_HI", "PUOU", "PUOD", "PDOU", "PDOD", "FUND_LO",
             "FUND_HI"]
FEATS = DIR_FEATS + NEU_FEATS
FIDX = {n: i for i, n in enumerate(FEATS)}
NF = len(FEATS)


# ------------------------------------------------------------------ indicators (FORMULAS s1, s12, s22, s30)
def atr_sma(h, l, c, n=14):
    """Plain SMA of true range (FORMULAS s12); NaN until n TRs exist (TR undefined at bar 0)."""
    h, l, c = (np.asarray(a, float) for a in (h, l, c))
    tr = np.full(len(c), np.nan)
    tr[1:] = np.maximum.reduce([h[1:] - l[1:], np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])])
    return pd.Series(tr).rolling(n).mean().to_numpy()


def rsi_wilder(c, n=14):
    """Textbook Wilder RSI with SMA seed (FORMULAS s1); NaN before index n."""
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    g, ls = np.maximum(d, 0), np.maximum(-d, 0)
    ag, al = g[:n].mean(), ls[:n].mean()

    def val(ag, al):
        if al == 0:
            return 100.0 if ag > 0 else 50.0
        return 100 - 100 / (1 + ag / al)
    out[n] = val(ag, al)
    for i in range(n, len(d)):
        ag = (ag * (n - 1) + g[i]) / n
        al = (al * (n - 1) + ls[i]) / n
        out[i + 1] = val(ag, al)
    return out


def adx_di(h, l, c, n=14):
    """Wilder DI+, DI-, ADX (FORMULAS s30.1: sum-seeded smoothing, ADX = mean of first n DX then recursive)."""
    h, l, c = (np.asarray(a, float) for a in (h, l, c))
    m = len(c)
    dip = np.full(m, np.nan)
    dim = np.full(m, np.nan)
    adx = np.full(m, np.nan)
    if m <= 2 * n:
        return dip, dim, adx
    tr = np.maximum.reduce([h[1:] - l[1:], np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])])
    up, dn = h[1:] - h[:-1], l[:-1] - l[1:]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    st, sp, sm = tr[:n].sum(), pdm[:n].sum(), mdm[:n].sum()
    dx = []
    for i in range(n - 1, len(tr)):
        if i >= n:
            st = st - st / n + tr[i]
            sp = sp - sp / n + pdm[i]
            sm = sm - sm / n + mdm[i]
        a = 100 * sp / st if st else 0.0
        b = 100 * sm / st if st else 0.0
        dip[i + 1], dim[i + 1] = a, b
        dx.append(100 * abs(a - b) / (a + b) if (a + b) else 0.0)
        k = len(dx)
        if k == n:
            adx[i + 1] = float(np.mean(dx))
        elif k > n:
            adx[i + 1] = (adx[i] * (n - 1) + dx[-1]) / n
    return dip, dim, adx


def pct_rank(x, w):
    """Share of the PRIOR w values <= x[t] (point in time, excludes the current value); NaN until w prior values exist."""
    x = np.asarray(x, float)
    n = len(x)
    out = np.full(n, np.nan)
    if n <= w:
        return out
    for a in range(w, n, 1500):
        b = min(n, a + 1500)
        win = sliding_window_view(x[a - w:b - 1], w)
        out[a:b] = (win <= x[a:b, None]).mean(1)
    out[np.isnan(x)] = np.nan
    return out


def shift(a, k):
    """Value k bars ago (float arrays), NaN for the first k bars."""
    a = np.asarray(a, float)
    out = np.full(len(a), np.nan)
    if k > 0:
        out[k:] = a[:-k]
    else:
        out[:] = a
    return out


# ------------------------------------------------------------------ data loading
def load_spot(sym, tf, root=None):
    root = root or DATA
    df = pd.read_csv(os.path.join(root, f"spot_{tf}", f"{sym}USDT.csv")).drop_duplicates("ts").sort_values("ts")
    step = {"4h": 4 * 3600000, "1d": DAY}[tf]
    df = df[df.ts + step <= DATA_END_MS]
    return {k: df[k].to_numpy(dtype=np.int64 if k == "ts" else float) for k in ("ts", "o", "h", "l", "c", "v", "tbv")}


def load_funding(sym, root=None):
    df = pd.read_csv(os.path.join(root or DATA, "funding", f"{sym}USDT.csv")).sort_values("ts")
    df = df[df.ts <= DATA_END_MS]
    return df.ts.to_numpy(np.int64), df.rate.to_numpy(float)


def load_oi(sym, root=None):
    df = pd.read_csv(os.path.join(root or DATA, "oi", f"{sym}USDT.csv")).sort_values("ts")
    df = df[df.ts <= DATA_END_MS]
    return df.ts.to_numpy(np.int64), df.oi.to_numpy(float)


def load_cycle():
    d = pd.read_csv(CYCLE_CSV, usecols=["date", "d200w"], parse_dates=["date"])
    days = (d.date - pd.Timestamp("1970-01-01")).dt.days.to_numpy()
    return days.astype(np.int64), d.d200w.to_numpy(float)


# ------------------------------------------------------------------ phase labels (causal)
def phase_table(btc_ts, btc_c, bug=None):
    """Six labels = structure (UP / MIX / DOWN from BTC daily close vs SMA200d and its 20d slope) x cycle clock (days since the
    last halving < 540 early, >= 540 late). The label computed from the close of day d is KEYED to day d+1, so a bar on day D reads
    only closes <= D-1. bug=True keys it to day d (same-day close: look-ahead)."""
    bug = BUG if bug is None else bug
    c = np.asarray(btc_c, float)
    dnum = np.asarray(btc_ts) // DAY
    sma = pd.Series(c).rolling(200).mean().to_numpy()
    slope = sma - shift(sma, 20)
    up = (c > sma) & (slope > 0)
    dn = (c < sma) & (slope < 0)
    st = np.where(up, 0, np.where(dn, 2, 1)).astype(float)
    st[np.isnan(sma) | np.isnan(slope)] = np.nan
    hv = np.array(HALVINGS)
    since = np.array([d - hv[hv <= d].max() if (hv <= d).any() else -1 for d in dnum])
    late = (since >= LATE_AFTER).astype(float)
    lab = st * 2 + late
    keys = dnum if bug else dnum + 1
    return keys, lab


def phase_for_days(table, days):
    keys, lab = table
    ix = np.searchsorted(keys, days, side="right") - 1
    ok = (ix >= 0)
    ixc = np.clip(ix, 0, len(keys) - 1)
    ok &= (days - keys[ixc]) <= 3
    out = np.where(ok, lab[ixc], np.nan)
    return out


# ------------------------------------------------------------------ daily flow context (OI, funding, discount) on the daily grid
def daily_flow(d1, oi, fund, cyc, bug=None):
    """Boolean daily-grid features keyed by day number: OI_FLUSH OI_BUILD OI_HI PUOU PUOD PDOU PDOD FUND_LO FUND_HI DD_DEEP.
    Value on day D uses day-D data (OI last 5m row of D, funding prints on D, close of D): known at the close of D.
    NEAR_200W (BTC close <= 1.10 x 200w SMA, from the cycle file) is added by the caller. Missing input -> False (never 0)."""
    days = d1["ts"] // DAY
    c = d1["c"]
    atr = atr_sma(d1["h"], d1["l"], c, 14)
    ret3 = c / shift(c, 3) - 1
    mv = ret3 / (atr / c)
    oi_s = pd.Series(np.nan, index=days)
    if oi is not None and len(oi[0]):
        o_days = oi[0] // DAY
        oi_s = pd.Series(oi[1], index=o_days)
        oi_s = oi_s[~oi_s.index.duplicated()].reindex(days)
    oiv = oi_s.to_numpy(float).copy()
    oiv[oiv <= 0] = np.nan
    doi2 = oiv / shift(oiv, 2) - 1
    doi3 = oiv / shift(oiv, 3) - 1
    oimax = pd.Series(oiv).rolling(60, min_periods=60).max().to_numpy()
    up, dn = mv >= 1.0, mv <= -1.0
    oup, odn = doi3 >= 0.03, doi3 <= -0.03
    fd = pd.Series(np.nan, index=days)
    if fund is not None and len(fund[0]):
        f = pd.Series(fund[1], index=fund[0] // DAY).groupby(level=0).mean()
        fd = f.reindex(days)
    fd3 = fd.rolling(3, min_periods=3).mean().to_numpy()
    fp = pct_rank(fd3, 90)
    cmax = pd.Series(c).rolling(365, min_periods=365).max().to_numpy()
    out = {
        "OI_FLUSH": doi2 <= -0.05, "OI_BUILD": doi3 >= 0.05, "OI_HI": oiv >= 0.95 * oimax,
        "PUOU": up & oup, "PUOD": up & odn, "PDOU": dn & oup, "PDOD": dn & odn,
        "FUND_LO": fp <= 0.10, "FUND_HI": fp >= 0.90, "DD_DEEP": c <= 0.6 * cmax,
    }
    cd, cv = cyc
    ix = np.searchsorted(cd, days - (0 if (BUG if bug is None else bug) else 1), side="right") - 1
    ok = (ix >= 0) & (np.abs(cd[np.clip(ix, 0, len(cd) - 1)] - (days - (0 if (BUG if bug is None else bug) else 1))) <= 3)
    out["NEAR_200W"] = ok & (cv[np.clip(ix, 0, len(cd) - 1)] <= 0.10)
    return days, {k: np.asarray(v, bool) for k, v in out.items()}


# ------------------------------------------------------------------ feature bank on tf bars
def tf_features(D, tf, flow, bug=None):
    """Return (L, S, atr) where L, S are (NF, n) bool arrays: the long-side and short-side reading of every feature. Directional
    features differ between L and S; neutral features are identical. All windows are in DAYS converted to bars (nb per day)."""
    bug = BUG if bug is None else bug
    nb = 6 if tf == "4h" else 1
    o, h, l, c, v, tbv, ts = (D[k] for k in ("o", "h", "l", "c", "v", "tbv", "ts"))
    n = len(c)
    sr = pd.Series
    hp = lambda N: sr(h).rolling(N).max().shift(1).to_numpy()
    lp = lambda N: sr(l).rolling(N).min().shift(1).to_numpy()
    cp_hi = lambda N: sr(c).rolling(N).max().to_numpy()
    cp_lo = lambda N: sr(c).rolling(N).min().to_numpy()
    atr = atr_sma(h, l, c, 14)
    L = np.zeros((NF, n), bool)
    S = np.zeros((NF, n), bool)

    def setd(name, lo, sh):
        L[FIDX[name]] = np.asarray(lo, bool)
        S[FIDX[name]] = np.asarray(sh, bool)

    def setn(name, x):
        L[FIDX[name]] = np.asarray(x, bool)
        S[FIDX[name]] = np.asarray(x, bool)
    N5, N10, N20, N50, N200 = 5 * nb, 10 * nb, 20 * nb, 50 * nb, 200 * nb
    setd("BRK20", c > hp(N20), c < lp(N20))
    setd("BRK5", c > hp(N5), c < lp(N5))
    rs = rsi_wilder(c, 14)
    setd("RSI_X", rs <= 30, rs >= 70)
    setd("RSI_MOM", rs >= 60, rs <= 40)
    mid = sr(c).rolling(20).mean().to_numpy()
    sd = sr(c).rolling(20).std(ddof=0).to_numpy()
    setd("BB_EXT", c < mid - 2 * sd, c > mid + 2 * sd)
    bbw = 4 * sd / mid
    setn("BB_SQZ", pct_rank(bbw, 365 * nb) <= 0.25)
    setd("SWEEP", (l < lp(N10)) & (c > lp(N10)), (h > hp(N10)) & (c < hp(N10)))
    dip, dim, adx = adx_di(h, l, c, 14)
    setd("ADX_DI", (adx >= 20) & (dip > dim), (adx >= 20) & (dim > dip))
    s50 = sr(c).rolling(N50).mean().to_numpy()
    s200 = sr(c).rolling(N200).mean().to_numpy()
    setd("TREND_MA", (c > s50) & (s50 > shift(s50, N10)), (c < s50) & (s50 < shift(s50, N10)))
    setd("ABOVE_200", c > s200, c < s200)
    setd("FLUSH_EXT", c <= cp_lo(N10), c >= cp_hi(N10))
    rng = h - l
    pos = (c - l) / np.where(rng > 0, rng, np.nan)
    big = rng >= 2 * shift(atr, 1)
    setd("BIGBAR", big & (pos <= 0.25), big & (pos >= 0.75))
    delta = 2 * tbv - v
    nt = delta / v
    bias = sr(nt).rolling(30 * nb).mean().shift(1).to_numpy()
    deb = delta - bias * v

    def nbn(k):
        return sr(deb).rolling(k).sum().to_numpy() / sr(v).rolling(k).sum().to_numpy()
    a3, p10 = nbn(3), nbn(10 * nb)
    setd("NB_ABS", a3 >= 0.08, a3 <= -0.08)
    setd("NB_PER", p10 >= 0.03, p10 <= -0.03)
    setn("VOLX", v >= 2 * sr(v).rolling(30 * nb).median().shift(1).to_numpy())
    # daily-grid flow features mapped to bars; 4h reads the PREVIOUS completed day (lag 1) unless bug
    fdays, ff = flow
    bar_day = ts // DAY - (0 if (tf == "1d" or bug) else 1)
    ix = np.searchsorted(fdays, bar_day)
    ixc = np.clip(ix, 0, len(fdays) - 1)
    ok = (ix < len(fdays)) & (fdays[ixc] == bar_day)
    for name in NEU_FEATS:
        if name in ff and name != "BB_SQZ" and name != "VOLX":
            setn(name, ok & ff[name][ixc])
    return L, S, atr


# ------------------------------------------------------------------ trade simulator
def simulate(o, h, l, c, atr, d, kind, nb):
    """For every signal bar s (entry at open[s+1]) return gross fractional return, risk fraction S/entry, last occupied bar,
    exit-time index (the exit happens at the open of bar xt) and a resolved flag. d=+1 long, -1 short.
    Stop S = max(STOP_ATR*ATR14, MIN_STOP*entry), stop filled at the worse of stop or open, target filled at target.
    T3R: stop and 3R target, time exit at close of the last hold bar. TRAIL: after +1R the stop follows highest close - 3*ATR.
    RIDE: fixed stop, exit at the next open after a close beyond the opposite prior-10d extreme."""
    n = len(c)
    H = HOLD_DAYS[kind] * nb
    sig = np.arange(n - 1)
    e = sig + 1
    entry = o[e]
    S = np.maximum(STOP_ATR * atr[sig], MIN_STOP * entry)
    risk = S / entry
    ret = np.full(n - 1, np.nan)
    xi = np.full(n - 1, -1, dtype=np.int64)
    xt = np.full(n - 1, -1, dtype=np.int64)
    stop = entry - d * S
    tgt = entry + d * TARGET_R * S
    best = entry.copy()
    armed = np.zeros(n - 1, bool)
    sr = pd.Series
    exit_lvl = (sr(l).rolling(10 * nb).min().shift(1).to_numpy() if d > 0 else sr(h).rolling(10 * nb).max().shift(1).to_numpy())
    alive = np.flatnonzero(np.isfinite(S))
    for k in range(H):
        if alive.size == 0:
            break
        jj = e[alive] + k
        keep = jj < n
        alive, jj = alive[keep], jj[keep]
        if alive.size == 0:
            break
        oj, hj, lj, cj = o[jj], h[jj], l[jj], c[jj]
        st = stop[alive]
        adverse = lj if d > 0 else hj
        favour = hj if d > 0 else lj
        hit_s = d * (st - adverse) >= 0
        fill_s = np.where(d * (oj - st) >= 0, st, oj)
        done = np.zeros(alive.size, bool)
        fill = np.zeros(alive.size)
        done |= hit_s
        fill[hit_s] = fill_s[hit_s]
        if kind == "T3R":
            hit_t = ~hit_s & (d * (favour - tgt[alive]) >= 0)
            done |= hit_t
            fill[hit_t] = tgt[alive][hit_t]
        xt_off = np.ones(alive.size, np.int64)
        if kind == "RIDE":
            sg = ~done & (d * (exit_lvl[jj] - cj) >= 0) & np.isfinite(exit_lvl[jj]) & (jj + 1 < n)
            nxt = np.minimum(jj + 1, n - 1)
            done |= sg
            fill[sg] = o[nxt][sg]
        if k == H - 1:
            tm = ~done
            done |= tm
            fill[tm] = cj[tm]
        if done.any():
            a = alive[done]
            ret[a] = d * (fill[done] - entry[a]) / entry[a]
            xi[a] = jj[done]
            xt[a] = jj[done] + xt_off[done]
        rem = ~done
        alive, jj, cj = alive[rem], jj[rem], cj[rem]
        if kind == "TRAIL" and alive.size:
            best[alive] = np.maximum(best[alive], cj) if d > 0 else np.minimum(best[alive], cj)
            armed[alive] |= d * (cj - entry[alive]) >= S[alive]
            cand = best[alive] - d * TRAIL_ATR * atr[jj]
            upd = armed[alive] & np.isfinite(cand)
            a2 = alive[upd]
            stop[a2] = np.maximum(stop[a2], cand[upd]) if d > 0 else np.minimum(stop[a2], cand[upd])
    out_ret = np.full(n, np.nan)
    out_risk = np.full(n, np.nan)
    out_xi = np.full(n, -1, np.int64)
    out_xt = np.full(n, -1, np.int64)
    out_ret[:-1], out_risk[:-1], out_xi[:-1], out_xt[:-1] = ret, risk, xi, xt
    return out_ret, out_risk, out_xi, out_xt


def cum_funding(ts, step, fts, frate):
    """Cumulative funding rate paid per notional at every bar open (n+1 points: the last is the close of the last bar)."""
    grid = np.append(ts, ts[-1] + step)
    cs = np.concatenate([[0.0], np.cumsum(frate)])
    return cs[np.searchsorted(fts, grid, side="right")]


# ------------------------------------------------------------------ frame: all coins of one timeframe concatenated
class Frame:
    pass


def build_frame(tf, syms=None, root=None, bug=None, data=None):
    """data (optional, for tests): dict sym -> dict(spot=<tf bars>, d1=<1d bars>, oi=(ts,v)|None, fund=(ts,r)|None) plus 'cycle'."""
    syms = syms or SYMS
    bug = BUG if bug is None else bug
    step = {"4h": 4 * 3600000, "1d": DAY}[tf]
    nb = 6 if tf == "4h" else 1
    if data is None:
        cyc = load_cycle()
        src = {s: dict(spot=load_spot(s, tf, root), d1=load_spot(s, "1d", root), oi=load_oi(s, root), fund=load_funding(s, root)) for s in syms}
        btc1d = load_spot("BTC", "1d", root)
    else:
        cyc = data["cycle"]
        src = {s: data[s] for s in syms}
        btc1d = data["BTC"]["d1"]
    table = phase_table(btc1d["ts"], btc1d["c"], bug)
    fr = Frame()
    fr.tf, fr.nb, fr.step, fr.syms = tf, nb, step, list(syms)
    parts = {k: [] for k in ("ts", "coin", "o", "c")}
    Ls, Ss, atrs = [], [], []
    sim = {(d, k): [[], [], [], []] for d in (1, -1) for k in KINDS}
    ph, base_ok = [], []
    off = 0
    fr.start, fr.end = [], []
    for ci, s in enumerate(syms):
        D = src[s]["spot"]
        n = len(D["c"])
        flow = daily_flow(src[s]["d1"], src[s]["oi"], src[s]["fund"], cyc, bug)
        L, S, atr = tf_features(D, tf, flow, bug)
        Ls.append(L), Ss.append(S), atrs.append(atr)
        fts, fr_ = src[s]["fund"]
        cf = cum_funding(D["ts"], step, fts, fr_)
        ebar = np.arange(n) + 1
        for d in (1, -1):
            for k in KINDS:
                r, rk, xi, xt = simulate(D["o"], D["h"], D["l"], D["c"], atr, d, k, nb)
                res = xi >= 0
                fund = np.full(n, np.nan)
                idx = np.flatnonzero(res)
                fund[idx] = d * (cf[xt[idx]] - cf[ebar[idx]])
                sim[(d, k)][0].append(r)
                sim[(d, k)][1].append(rk)
                sim[(d, k)][2].append(np.where(res, xi + off, -1))
                sim[(d, k)][3].append(fund)
        entry_day = np.append(D["ts"][1:], D["ts"][-1] + step) // DAY
        pl = phase_for_days(table, entry_day)
        ph.append(pl)
        first_f = fts[0] if len(fts) else np.inf
        ok = (entry_day >= START_DAY) & (np.append(D["ts"][1:], D["ts"][-1] + step) >= first_f) & ~np.isnan(pl)
        base_ok.append(ok)
        parts["ts"].append(D["ts"]), parts["coin"].append(np.full(n, ci)), parts["o"].append(D["o"]), parts["c"].append(D["c"])
        fr.start.append(off)
        off += n
        fr.end.append(off)
    fr.ts = np.concatenate(parts["ts"])
    fr.coin = np.concatenate(parts["coin"])
    fr.o, fr.c = np.concatenate(parts["o"]), np.concatenate(parts["c"])
    fr.L, fr.S = np.concatenate(Ls, axis=1), np.concatenate(Ss, axis=1)
    fr.feat = {1: fr.L, -1: fr.S}
    fr.atr = np.concatenate(atrs)
    fr.phase = np.concatenate(ph)
    fr.base_ok = np.concatenate(base_ok)
    n_tot = len(fr.ts)
    fr.entry_day = np.empty(n_tot, np.int64)
    for a, b in zip(fr.start, fr.end):
        fr.entry_day[a:b] = np.append(fr.ts[a + 1:b], fr.ts[b - 1] + step) // DAY
    fr.first = np.zeros(n_tot, bool)
    fr.first[fr.start] = True
    fr.sim = {}
    for key, v in sim.items():
        fr.sim[key] = dict(ret=np.concatenate(v[0]), risk=np.concatenate(v[1]), xg=np.concatenate(v[2]), fund=np.concatenate(v[3]))
    fr.dev = fr.base_ok & (fr.entry_day <= DEV_END_DAY)
    fr.val = fr.base_ok & (fr.entry_day >= VAL_START_DAY)
    fr.phase_i = np.where(np.isnan(fr.phase), -1, fr.phase).astype(np.int8)
    return fr


def net_r(sm, idx, cost):
    """(gross return - cost - side*funding) / risk fraction, FORMULAS s13 divided by the stop distance."""
    return (sm["ret"][idx] - cost - sm["fund"][idx]) / sm["risk"][idx]


# ------------------------------------------------------------------ selection / statistics
def onsets(frame, d, feats):
    sig = frame.feat[d][feats[0]].copy()
    for f in feats[1:]:
        sig &= frame.feat[d][f]
    prev = np.empty_like(sig)
    prev[1:] = sig[:-1]
    prev[0] = False
    prev[frame.first] = False
    return sig & ~prev


def greedy(idx, xg):
    """Non-overlapping trades: take the first signal, skip signals before its exit bar, repeat (idx sorted ascending)."""
    out = []
    nxt = -1
    for i, x in zip(idx.tolist(), xg.tolist()):
        if i >= nxt:
            out.append(i)
            nxt = x
    return np.array(out, dtype=np.int64)


def cluster_stats(r, day):
    """Mean, day-cluster robust SE (CR1: sqrt(G/(G-1))), number of day clusters."""
    n = len(r)
    m = float(np.mean(r))
    _, inv = np.unique(day, return_inverse=True)
    g = inv.max() + 1
    sums = np.bincount(inv, weights=r)
    cnt = np.bincount(inv)
    dev = sums - cnt * m
    se = math.sqrt((dev ** 2).sum()) / n * (math.sqrt(g / (g - 1)) if g > 1 else 1.0)
    return m, se, g


def norm_sf(t):
    return 0.5 * math.erfc(t / math.sqrt(2))


def bh_qvalues(p, m):
    """Benjamini-Hochberg adjusted q for p-values of a family of total size m (p array holds only the tested subset)."""
    p = np.asarray(p, float)
    order = np.argsort(p)
    ps = p[order]
    q = ps * m / (np.arange(len(ps)) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty_like(q)
    out[order] = np.minimum(q, 1.0)
    return out


def cell_picks(frame, d, feats, kind, phase_mask, window, extra_mask=None):
    """Trade indices of one cell in a window ('dev' or 'val'); phase_mask is a bool[6] array."""
    wmask = frame.dev if window == "dev" else frame.val
    sm = frame.sim[(d, kind)]
    on = onsets(frame, d, feats) & wmask & (sm["xg"] >= 0)
    on &= np.array(phase_mask, bool)[np.clip(frame.phase_i, 0, 5)] & (frame.phase_i >= 0)
    idx = np.flatnonzero(on)
    return greedy(idx, sm["xg"][idx]) if len(idx) else idx
