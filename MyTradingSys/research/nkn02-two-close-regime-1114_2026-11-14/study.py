"""NKN-02 two-close regime switch, context-conditioned. Protocol: PRE_REG.md (frozen design). `python study.py run` computes everything once and writes
results.json + RESULT.md; it refuses while the code / PRE_REG.md have uncommitted changes. Daily bars from cached spot 15m (one source per coin).
No look-ahead: every signal at day t uses data through the close of day t; phase / cycle are read at the close of the day BEFORE the first confirming close."""
import os, sys, json, subprocess, datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest.layers.adx.adx import adx_di  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402
from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_regime  # noqa: E402

CACHE = Path(r"F:\MTS\data_cache")
SPOT = CACHE / "binance_spot"
HTF = CACHE / "binance_spot_htf"
FUT = CACHE / "binance_futures" / "nkp1"
PHASE_CSV = CACHE / "mts_brains" / "phase_daily.csv"
COINS = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
SPLIT = 1704067200000  # 2024-01-01 UTC, compared with the SIGNAL bar open time
DAY, H1, M15 = 86400000, 3600000, 900000
CODE_FILES = ["PRE_REG.md", "study.py", "test_study.py"]
# parameters (labels in PRE_REG.md)
SMA_FAST, SMA_MID, SMA_SLOW = 20, 50, 200       # SOURCED
HOLD_N = 10                                      # SOURCED (10-12, use 10)
ARM_WIN, ARM_MIN = 30, 10                        # OURS
ADX_N, ADX_MIN = 14, 20.0                        # OURS
AT_D = 1.5                                       # OURS
TIME_STOP_D, TIME_STOP_H = 60, 1440              # OURS
STRUCT_N, FLOOR_PCT, ATR_MULT = 10, 0.005, 0.6   # OURS
EP_GAP, EP_MIN = 10, 15                          # OURS
N_POWER, N_PASS = 100, 200
NB_TRADE, NB_DAY, NB_PLACEBO = 5000, 5000, 1000
BAD_CYC, BAD_PH = 9, 2
CYC = {"BEAR": -1, "BASE": 0, "BULL": 1}


# ---------------- loading and resampling ----------------
def load_15m(coin):
    z = np.load(SPOT / f"{coin}USDT_15m.npz")
    key = "ts" if "ts" in z.files else ("t" if "t" in z.files else None)
    assert key is not None, f"{coin}: no time key in {z.files}"
    return check_series(z[key].astype(np.int64), z["o"], z["h"], z["l"], z["c"], coin)


def check_series(t, o, h, l, c, name="", step=M15, max_gap=12 * H1):
    """assert strictly increasing, bar-aligned, minimum step == bar step, every gap <= max_gap; return arrays and the gap list."""
    t = np.asarray(t, dtype=np.int64)
    assert len(t) > 10, f"{name}: too short"
    d = np.diff(t)
    assert (d > 0).all(), f"{name}: timestamps not strictly increasing"
    assert (t % step == 0).all(), f"{name}: timestamps not aligned to {step}"
    assert d.min() == step, f"{name}: minimum step {d.min()} != {step}"
    assert d.max() <= max_gap, f"{name}: gap {d.max()} ms > {max_gap}"
    gaps = int((d != step).sum())
    return dict(t=t, o=np.asarray(o, float), h=np.asarray(h, float), l=np.asarray(l, float), c=np.asarray(c, float), gaps=gaps)


def resample(raw, bucket, last_bar_offset):
    """aggregate bars to buckets of `bucket` ms (UTC aligned). The final bucket is kept only if its LAST sub-bar (open time bucket_start+last_bar_offset) is present (else it is partial and dropped);
    interior buckets with downtime gaps are kept. Result is checked contiguous."""
    t = raw["t"]
    b = t // bucket
    starts = np.flatnonzero(np.r_[True, b[1:] != b[:-1]])
    last = np.r_[starts[1:], len(t)] - 1
    u = b[starts]
    ok = np.ones(len(u), bool)
    ok[-1] = (t[last[-1]] - u[-1] * bucket) == last_bar_offset   # only the final bucket can be partial; interior buckets with exchange-downtime gaps are kept
    hh = np.maximum.reduceat(raw["h"], starts)
    ll = np.minimum.reduceat(raw["l"], starts)
    u, first, last, hh, ll = u[ok], starts[ok], last[ok], hh[ok], ll[ok]
    assert (np.diff(u) == 1).all(), "resampled series not contiguous"
    return dict(t=u * bucket, o=raw["o"][first], h=hh, l=ll, c=raw["c"][last])


def daily_from_15m(raw):
    return resample(raw, DAY, DAY - M15)


def hourly_from_15m(raw):
    return resample(raw, H1, H1 - M15)


# ---------------- indicators (all causal) ----------------
def sma(x, n):
    return pd.Series(x).rolling(n).mean().to_numpy()


def atr_wilder(h, l, c, n=14):
    pc = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    tr[0] = np.nan
    a = pd.Series(tr).ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean().to_numpy()
    return a


def nanarr(v):
    return np.array([np.nan if x is None else x for x in v], float)


def trend_phase(h, l, c):
    """per-day state from data through that day's close: 1 UP, -1 DOWN, 0 RANGE, 2 not computable.
    UP = SMA20 slope over 5 days > 0 and ADX14 >= 20 and +DI > -DI; DOWN mirror; else RANGE."""
    dip, dim, adx = adx_di(list(h), list(l), list(c), ADX_N)
    dip, dim, adx = nanarr(dip), nanarr(dim), nanarr(adx)
    s20 = sma(c, SMA_FAST)
    slope = s20 / np.r_[np.full(5, np.nan), s20[:-5]] - 1.0
    ph = np.full(len(c), BAD_PH, dtype=np.int8)
    valid = ~np.isnan(adx) & ~np.isnan(slope)
    ph[valid] = 0
    with np.errstate(invalid="ignore"):
        ph[valid & (adx >= ADX_MIN) & (dip > dim) & (slope > 0)] = 1
        ph[valid & (adx >= ADX_MIN) & (dim > dip) & (slope < 0)] = -1
    return ph, dip, dim, adx


def rsi_regime_codes(c):
    """daily RSI14 -> Malkan 40/60 regime (lookback 20): 1 BULL, -1 BEAR, 0 RANGE, 9 undefined."""
    r = rsi_core(list(c), 14)
    reg = malkan_regime(r, 40.0, 60.0, 20)
    m = {"BULL": 1, "BEAR": -1, "RANGE": 0}
    return np.array([m.get(x, 9) for x in reg], dtype=np.int8)


def make_D(t, o, h, l, c):
    """daily indicator pack for one coin."""
    D = dict(t=np.asarray(t, np.int64), o=np.asarray(o, float), h=np.asarray(h, float), l=np.asarray(l, float), c=np.asarray(c, float))
    D["s20"], D["s50"], D["s200"] = sma(c, SMA_FAST), sma(c, SMA_MID), sma(c, SMA_SLOW)
    D["atr"] = atr_wilder(D["h"], D["l"], D["c"], 14)
    D["phase"], D["dip"], D["dim"], D["adx"] = trend_phase(D["h"], D["l"], D["c"])
    D["rsireg"] = rsi_regime_codes(D["c"])
    D["ll"] = pd.Series(D["l"]).rolling(STRUCT_N).min().to_numpy()
    D["hh"] = pd.Series(D["h"]).rolling(STRUCT_N).max().to_numpy()
    n = len(c)
    D["cyc"] = np.full(n, BAD_CYC, np.int8)        # BTC cycle state at the close of day d (attach_ctx)
    D["btcmd"] = np.zeros(n, bool)                 # BTC phase label MARKDOWN at the close of day d
    D["btc200"] = np.zeros(n, bool)                # BTC close > BTC SMA200 at the close of day d
    D["fund3"] = np.full(n, np.nan)
    D["fhi"] = np.full(n, np.nan)
    D["flo"] = np.full(n, np.nan)
    D["oi5"] = np.full(n, np.nan)
    D["is_btc"] = False
    return D


def lagk(x, k, fill):
    out = np.full(len(x), fill, dtype=x.dtype)
    if k > 0:
        out[k:] = x[:-k]
    else:
        out[:] = x
    return out


def roll_sum(x, n):
    return pd.Series(x.astype(float)).rolling(n).sum().to_numpy()


# ---------------- signal masks (index = signal day t) ----------------
def build_masks(D):
    """every cell's boolean signal mask over signal days t, plus pool masks for the placebo. All reads use data <= t (phase / cycle at t-2 or t-1)."""
    c, s20, s50, s200, atr = D["c"], D["s20"], D["s50"], D["s200"], D["atr"]
    with np.errstate(invalid="ignore"):
        Al = (c > s20) & (c > s50)
        Au = c > s20
        Bs = c < s20
        above200 = c > s200
        below200 = c < s200
    hold = roll_sum(below200, HOLD_N) == HOLD_N
    arm = roll_sum(below200, ARM_WIN) >= ARM_MIN
    F = False
    long2 = Al & lagk(Al, 1, F) & ~lagk(Al, 2, F) & above200 & lagk(arm, 2, F)
    long1 = Al & ~lagk(Al, 1, F) & above200 & lagk(arm, 1, F)
    short2 = Bs & lagk(Bs, 1, F) & ~lagk(Bs, 2, F) & hold
    short1 = Bs & ~lagk(Bs, 1, F) & hold
    draftL = Au & lagk(Au, 1, F) & above200
    draftS = Bs & lagk(Bs, 1, F) & hold
    ph2, cy2 = lagk(D["phase"], 2, BAD_PH), lagk(D["cyc"], 2, BAD_CYC)
    ph1, cy1 = lagk(D["phase"], 1, BAD_PH), lagk(D["cyc"], 1, BAD_CYC)

    def cellL(ph, cy):
        return (ph != BAD_PH) & (cy != BAD_CYC) & (cy != 1) & ((ph == -1) | (ph == 0))

    def cellS(ph, cy):
        return (ph != BAD_PH) & (cy != BAD_CYC) & (cy == 1) & ((ph == 1) | (ph == 0))

    L2, L1, S2, S1 = cellL(ph2, cy2), cellL(ph1, cy1), cellS(ph2, cy2), cellS(ph1, cy1)
    with np.errstate(invalid="ignore"):
        v1L = (D["adx"] >= ADX_MIN) & (D["dip"] > D["dim"])
        v1S = (D["adx"] >= ADX_MIN) & (D["dim"] > D["dip"])
        dist = np.abs(c - s200) / atr
        at = dist <= AT_D
        away = dist > AT_D
        fok_l = ~np.isnan(D["fund3"]) & ~np.isnan(D["fhi"]) & (D["fund3"] <= D["fhi"])
        fok_s = ~np.isnan(D["fund3"]) & ~np.isnan(D["flo"]) & (D["fund3"] >= D["flo"])
    M = {}
    M[1] = long2 & L2
    M[2] = M[1] & v1L
    M[3] = M[2] & (D["rsireg"] == 1)
    M[4] = short2 & S2
    M[5] = M[4] & v1S
    M[6] = M[5] & (D["rsireg"] == -1)
    M[7] = long1 & L1
    M[8] = short1 & S1
    M[9] = draftL & (cy2 == 1) & (ph2 == 1)
    M[10] = draftS & (cy2 == -1) & (ph2 == -1)
    M[11] = short2 & L2
    M[12] = long2 & S2
    M[15] = short2 & lagk(D["btcmd"], 2, F)
    M[16], M[17] = M[1] & at, M[1] & away
    M[18], M[19] = M[4] & at, M[4] & away
    M[20], M[21] = M[1] & fok_l, M[7] & fok_l
    M[22], M[23] = M[4] & fok_s, M[8] & fok_s
    M[24] = M[1] & D["btc200"] & (not D["is_btc"])
    M[25], M[26] = draftL, draftS
    valid = ~np.isnan(s200) & ~np.isnan(atr)
    pools = {"L": L2 & valid, "S": S2 & valid}
    return M, pools, dict(dist=dist, L2=L2, S2=S2)


# ---------------- trade simulation ----------------
def next_true(cond):
    """nxt[k] = smallest j >= k with cond[j], else len(cond) (used only to find the EXIT bar of a trade already entered)."""
    n = len(cond)
    pos = np.flatnonzero(cond)
    return np.append(pos, n)[np.searchsorted(pos, np.arange(n + 1))]


def exit_cond_daily(D, side):
    """two consecutive closes against the position vs SMA20 (SOURCED lmhqooBqJWU 00:07:26). Evaluated at the close of day j."""
    c, s = D["c"], D["s20"]
    with np.errstate(invalid="ignore"):
        a = (c < s) if side > 0 else (c > s)
    return a & lagk(a, 1, False)


def sim(D, idx, side, exit_cond, min_off, time_stop):
    """vectorised primary P&L (close-based exit, no intraday stop). Entry = open of bar t+1, exit = open of the bar after the exit signal, or the time stop,
    or (unresolved at data end) the last close. R = max(structural distance, 0.5% of entry, 0.6 x ATR14). Returns dict of arrays."""
    o, h, l, c, atr = D["o"], D["h"], D["l"], D["c"], D["atr"]
    n = len(c)
    idx = np.asarray(idx, np.int64)
    idx = idx[(idx <= n - 2) & ~np.isnan(atr[np.minimum(idx, n - 1)]) & ~np.isnan(D["ll"][np.minimum(idx, n - 1)])]
    e = idx + 1
    entry = o[e]
    st = (entry - D["ll"][idx]) if side > 0 else (D["hh"][idx] - entry)
    fl = np.maximum(FLOOR_PCT * entry, ATR_MULT * atr[idx])
    R = np.maximum(np.maximum(st, 0.0), fl)
    floor_won = fl >= np.maximum(st, 0.0)
    nxt = next_true(exit_cond)
    k = e + min_off
    j = np.where(k <= n - 1, nxt[np.minimum(k, n - 1)], n)
    X = np.minimum(j + 1, e + time_stop)
    unres = X > n - 1
    X = np.where(unres, n - 1, X)
    x = np.where(unres, c[n - 1], o[X])
    g = side * (x - entry) / R
    return dict(t=idx, e=e, X=X, entry=entry, x=x, R=R, g=g, floor=floor_won, unres=unres, side=np.full(len(idx), side, np.int8))


def fee_r(entry, x, R, bp):
    """round-trip fee in R: bp/2 charged on entry notional and bp/2 on exit notional, divided by the stop distance R (price units, per unit)."""
    return (bp / 2e4) * (entry + x) / R


def deoverlap(T):
    """one open trade per coin: keep a signal only if its entry bar e >= the previous kept trade's exit bar X."""
    keep = np.zeros(len(T["t"]), bool)
    last = -1
    for i in np.argsort(T["t"], kind="stable"):
        if T["e"][i] >= last:
            keep[i] = True
            last = T["X"][i]
    return {k: v[keep] for k, v in T.items()}


def stop_fill(o, h, l, k, stop, side):
    """intraday hard-stop fill on bar k: touch fills at the stop, a gap through it fills at the open (worse of the two). None if not hit."""
    if side > 0:
        return min(stop, o[k]) if l[k] <= stop else None
    return max(stop, o[k]) if h[k] >= stop else None


def stop_path_x(D, T):
    """secondary (non-gating) column: exit price with an intraday hard stop at 1R, same entries."""
    o, h, l = D["o"], D["h"], D["l"]
    xs = T["x"].copy()
    for i in range(len(T["t"])):
        side, stop = int(T["side"][i]), T["entry"][i] - T["side"][i] * T["R"][i]
        end = T["X"][i] - 1 if not T["unres"][i] else T["X"][i]
        for k in range(T["e"][i], end + 1):
            f = stop_fill(o, h, l, k, stop, side)
            if f is not None:
                xs[i] = f
                break
    return xs


# ---------------- statistics ----------------
def boot_means(R, day, nb, seed):
    """day-cluster bootstrap of the mean: resample days, ratio of sums."""
    u, inv = np.unique(day, return_inverse=True)
    sR = np.bincount(inv, weights=R)
    nn = np.bincount(inv).astype(float)
    D = len(u)
    rng = np.random.default_rng(seed)
    out, done = [], 0
    chunk = max(1, int(4e6 // D))
    while done < nb:
        b = min(chunk, nb - done)
        ix = rng.integers(0, D, (b, D))
        out.append(sR[ix].sum(axis=1) / nn[ix].sum(axis=1))
        done += b
    return np.concatenate(out)


def boot_trades(R, nb, seed):
    rng = np.random.default_rng(seed)
    n = len(R)
    out, done = [], 0
    chunk = max(1, int(4e6 // n))
    while done < nb:
        b = min(chunk, nb - done)
        out.append(R[rng.integers(0, n, (b, n))].mean(axis=1))
        done += b
    return np.concatenate(out)


def ex_best5(R, day):
    """mean R of the trades left after removing the 5 days with the highest summed R."""
    u, inv = np.unique(day, return_inverse=True)
    sR = np.bincount(inv, weights=R)
    worst = np.argsort(-sR)[:5]
    m = ~np.isin(inv, worst)
    return float(R[m].mean()) if m.any() else float("nan")


def bh_q(p):
    p = np.asarray(p, float)
    m = len(p)
    o = np.argsort(p)
    q = np.empty(m)
    prev = 1.0
    for rank in range(m, 0, -1):
        i = o[rank - 1]
        prev = min(prev, p[i] * m / rank)
        q[i] = prev
    return q


def episodes(days, gap=EP_GAP):
    """independent turn episodes: entry days (any coin) sorted; a new episode starts when the gap to the previous entry exceeds `gap` days."""
    d = np.unique(np.asarray(days))
    if len(d) == 0:
        return 0
    return int(1 + (np.diff(d) > gap).sum())


def cell_stats(T, bp=12.0):
    n = len(T["t"])
    if n == 0:
        return dict(n=0)
    f = fee_r(T["entry"], T["x"], T["R"], bp)
    net = T["g"] - f
    return dict(n=n, gross=float(T["g"].mean()), net=float(net.mean()), win=float((net > 0).mean()), days=int(len(np.unique(T["day"]))))


def sel(T, m):
    return {k: v[m] for k, v in T.items()}


def cat(Ts):
    Ts = [x for x in Ts if len(x["t"])]
    if not Ts:
        return None
    return {k: np.concatenate([x[k] for x in Ts]) for k in Ts[0]}


def empty_T():
    z = np.zeros(0)
    return {k: z for k in ["t", "e", "X", "entry", "x", "R", "g", "floor", "unres", "side", "ts", "day", "coin", "dist", "gapatr", "dcross", "oi5", "xs"]}


# ---------------- study driver ----------------
def load_cycle_tables():
    p = pd.read_csv(PHASE_CSV)
    p["ep"] = (pd.to_datetime(p["date"]) - pd.Timestamp("1970-01-01")).dt.days.to_numpy()
    ser_c = pd.Series(p["cycle"].map(CYC).to_numpy(np.int8), index=p["ep"].to_numpy())
    ser_m = pd.Series((p["label"] == "MARKDOWN").to_numpy(), index=p["ep"].to_numpy())
    return ser_c, ser_m, p


def attach_ctx(D, ser_c, ser_m, btc200_map, coin, fund_days):
    """state at the close of day d = csv row dated d+1 (the csv label day d uses data through d-1)."""
    ep = D["t"] // DAY
    D["cyc"] = ser_c.reindex(ep + 1).fillna(BAD_CYC).to_numpy(np.int8)
    D["btcmd"] = ser_m.reindex(ep + 1).fillna(False).to_numpy(bool)
    D["btc200"] = btc200_map.reindex(ep).fillna(False).to_numpy(bool)
    D["is_btc"] = coin == "BTC"
    if fund_days is not None:
        fd = fund_days.reindex(ep)                      # daily mean funding (nan on missing days)
        f3 = fd.rolling(3).mean()
        D["fund3"] = f3.to_numpy()
        prior = f3.shift(1)
        D["fhi"] = prior.rolling(90, min_periods=90).quantile(0.9).to_numpy()
        D["flo"] = prior.rolling(90, min_periods=90).quantile(0.1).to_numpy()
    return D


def load_funding(coin):
    p = FUT / f"{coin}USDT_funding.csv"
    if not p.exists():
        return None
    f = pd.read_csv(p)
    f["ep"] = f["ts"] // DAY
    return f.groupby("ep")["rate"].mean()


def load_oi(coin):
    p = FUT / f"{coin}USDT_oi_daily.csv"
    if not p.exists():
        return None
    f = pd.read_csv(p)
    f["ep"] = f["ts"] // DAY
    return f.groupby("ep")["oi"].last()


def descr(D, idx):
    c, s20, s200, atr = D["c"], D["s20"], D["s200"], D["atr"]
    sg = np.sign(np.nan_to_num(c - s200))
    ch = np.r_[False, (sg[1:] != sg[:-1]) & (sg[1:] != 0) & (sg[:-1] != 0)]
    lastc = np.maximum.accumulate(np.where(ch, np.arange(len(c)), -1))
    dcross = np.where(lastc[idx] >= 0, idx - lastc[idx], np.nan)
    return (np.abs(c[idx] - s200[idx]) / atr[idx], (s20[idx] - s200[idx]) / atr[idx], dcross)


def trades_for(D, coin_i, side, mask, want_stop=True):
    idx = np.flatnonzero(mask)
    T = sim(D, idx, side, exit_cond_daily(D, side), 1, TIME_STOP_D)
    if len(T["t"]) == 0:
        return empty_T()
    T = deoverlap(T)
    i = T["t"]
    T["ts"] = D["t"][i]
    T["day"] = D["t"][i] // DAY
    T["coin"] = np.full(len(i), coin_i)
    T["dist"], T["gapatr"], T["dcross"] = descr(D, i)
    oi = D.get("oi")
    T["oi5"] = np.full(len(i), np.nan) if oi is None else D["oi5"][i]
    T["xs"] = stop_path_x(D, T) if want_stop else T["x"]
    return T


def pool_net(D, coin_i, side, pool_mask, bp=12.0):
    """independent (no de-overlap) simulated trades for every pool day: used for the like-for-like placebo."""
    idx = np.flatnonzero(pool_mask)
    T = sim(D, idx, side, exit_cond_daily(D, side), 1, TIME_STOP_D)
    if len(T["t"]) == 0:
        return np.zeros(0), np.zeros(0, np.int64)
    return T["g"] - fee_r(T["entry"], T["x"], T["R"], bp), D["t"][T["t"]]


def placebo(real_coin, real_net_mean, pools, nb=NB_PLACEBO, seed=77):
    """random entries in the same coin, same cell pool, same side, matched count. Returns (p, mean of placebo means, 2.5/97.5 percentiles)."""
    rng = np.random.default_rng(seed)
    cs, cnt = np.unique(real_coin, return_counts=True)
    means = np.zeros(nb)
    for c_, k in zip(cs, cnt):
        arr = pools.get(int(c_))
        if arr is None or len(arr) == 0:
            return float("nan"), float("nan"), (float("nan"), float("nan"))
        means += arr[rng.integers(0, len(arr), (nb, k))].sum(axis=1)
    means /= cnt.sum()
    p = (1 + int((means >= real_net_mean).sum())) / (nb + 1)
    return float(p), float(means.mean()), (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


def row_stats(T, split, full=True, seed=1):
    """stats for one cell on one split ('DEV' or 'VAL'); T has fields ts (signal bar open time)."""
    m = (T["ts"] < SPLIT) if split == "DEV" else (T["ts"] >= SPLIT)
    S = sel(T, m)
    n = len(S["t"])
    out = dict(n=n)
    if n == 0:
        return out, S
    net12 = S["g"] - fee_r(S["entry"], S["x"], S["R"], 12.0)
    net6 = S["g"] - fee_r(S["entry"], S["x"], S["R"], 6.0)
    out.update(gross=float(S["g"].mean()), net12=float(net12.mean()), net6=float(net6.mean()), win=float((net12 > 0).mean()),
               days=int(len(np.unique(S["day"]))), episodes=episodes(S["day"]),
               floor_share=float(S["floor"].mean()), unresolved=int(S["unres"].sum()),
               med_gap_atr=float(np.nanmedian(S["gapatr"])), med_dcross=float(np.nanmedian(S["dcross"])) if np.isfinite(S["dcross"]).any() else None,
               oi5_med=float(np.nanmedian(S["oi5"])) if np.isfinite(S["oi5"]).any() else None,
               net12_stop1R=float((S["side"] * (S["xs"] - S["entry"]) / S["R"] - fee_r(S["entry"], S["xs"], S["R"], 12.0)).mean()))
    if full and n >= 5:
        bt = boot_trades(net12, NB_TRADE, seed)
        bd = boot_means(net12, S["day"], NB_DAY, seed + 1)
        out.update(trade_ci_low=float(np.percentile(bt, 2.5)), day_ci_low=float(np.percentile(bd, 2.5)), day_ci_high=float(np.percentile(bd, 97.5)),
                   ex5=ex_best5(net12, S["day"]), p_day=(1 + int((bd <= 0).sum())) / (NB_DAY + 1))
    return out, S


CELLS = [  # (id, label, variant, level, tf, side, trigger, role, phase tested, side int)
    (1, "L-TURN", "V0", "all", "1d", "long", "2-close", "PRIMARY"),
    (2, "L-TURN", "V1", "all", "1d", "long", "2-close", "PRIMARY"),
    (3, "L-TURN", "V2", "all", "1d", "long", "2-close", "PRIMARY"),
    (4, "S-TURN", "V0", "all", "1d", "short", "2-close", "PRIMARY"),
    (5, "S-TURN", "V1", "all", "1d", "short", "2-close", "PRIMARY"),
    (6, "S-TURN", "V2", "all", "1d", "short", "2-close", "PRIMARY"),
    (7, "L-TURN", "V0", "all", "1d", "long", "1-close", "CONTROL (key, trap claim)"),
    (8, "S-TURN", "V0", "all", "1d", "short", "1-close", "CONTROL (key, trap claim)"),
    (9, "continuation UP x BULL (draft original, no drop-arming)", "V0", "all", "1d", "long", "2-close", "CONTROL"),
    (10, "continuation DOWN x BEAR (draft original short)", "V0", "all", "1d", "short", "2-close", "CONTROL"),
    (11, "L-TURN cell, mismatched direction", "V0", "all", "1d", "short", "2-close", "CONTROL"),
    (12, "S-TURN cell, mismatched direction", "V0", "all", "1d", "long", "2-close", "CONTROL"),
    (13, "random same-cell placebo (matched cycle + phase)", "n/a", "all", "1d", "long", "none", "CONTROL"),
    (14, "random same-cell placebo", "n/a", "all", "1d", "short", "none", "CONTROL"),
    (15, "MARKDOWN (BRAINS spec), descriptive", "V0", "all", "1d", "short", "2-close", "CONTROL"),
    (16, "L-TURN", "V0", "AT", "1d", "long", "2-close", "CONTROL"),
    (17, "L-TURN", "V0", "AWAY", "1d", "long", "2-close", "CONTROL"),
    (18, "S-TURN", "V0", "AT", "1d", "short", "2-close", "CONTROL"),
    (19, "S-TURN", "V0", "AWAY", "1d", "short", "2-close", "CONTROL"),
    (20, "L-TURN + funding veto", "V0", "all", "1d", "long", "2-close", "CONTROL"),
    (21, "L-TURN + funding veto", "V0", "all", "1d", "long", "1-close", "CONTROL"),
    (22, "S-TURN + funding veto", "V0", "all", "1d", "short", "2-close", "CONTROL"),
    (23, "S-TURN + funding veto", "V0", "all", "1d", "short", "1-close", "CONTROL"),
    (24, "L-TURN alts + BTC>SMA200", "V0", "all", "1d", "long", "2-close", "CONTROL"),
    (25, "unconditioned draft (no phase/cycle)", "V0", "all", "1d", "long", "2-close", "CONTROL"),
    (26, "unconditioned draft (no phase/cycle)", "V0", "all", "1d", "short", "2-close", "CONTROL"),
    (27, "1h SMA200 switch", "V0", "all", "1h", "long", "1h close > SMA200", "CONTROL"),
    (28, "weekly-close re-entry (>SMA200 and >SMA50)", "V0", "all", "1w", "long", "1 weekly close", "CONTROL"),
]
PRIMARY = [1, 2, 3, 4, 5, 6]
SIDE = {c[0]: (1 if c[5] == "long" else -1) for c in CELLS}
POOL_OF = {1: "L", 2: "L", 3: "L", 4: "S", 5: "S", 6: "S", 13: "L", 14: "S"}


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()


def code_dirty():
    return git("status", "--porcelain", "--", *[str((HERE / f).relative_to(REPO)).replace("\\", "/") for f in CODE_FILES])


def hourly_cell27(raw15, coin_i):
    H = hourly_from_15m(raw15)
    o, h, l, c = H["o"], H["h"], H["l"], H["c"]
    D = dict(t=H["t"], o=o, h=h, l=l, c=c, atr=atr_wilder(h, l, c, 14))
    D["ll"] = pd.Series(l).rolling(STRUCT_N).min().to_numpy()
    s = sma(c, 200)
    with np.errstate(invalid="ignore"):
        up = c > s
        trig = up & ~lagk(up, 1, True) & ~np.isnan(lagk(s, 1, np.nan))
        under = c < s
    idx = np.flatnonzero(trig)
    T = sim(D, idx, 1, under, 0, TIME_STOP_H)
    if len(T["t"]) == 0:
        return empty_T()
    T = deoverlap(T)
    i = T["t"]
    T["ts"], T["day"], T["coin"] = H["t"][i], H["t"][i] // DAY, np.full(len(i), coin_i)
    for k in ("dist", "gapatr", "dcross", "oi5"):
        T[k] = np.full(len(i), np.nan)
    T["xs"] = T["x"]
    return T


def weekly_cell28(D, coin_i):
    ep = D["t"] // DAY
    sat = ((ep + 3) % 7) == 5   # weekday Monday=0; Saturday's close = Sunday 00:00 UTC (weekly close)
    with np.errstate(invalid="ignore"):
        A = (D["c"] > D["s50"]) & (D["c"] > D["s200"])
    trig = sat & A & ~lagk(A, 7, True) & ~np.isnan(lagk(D["s200"], 7, np.nan))
    return trades_for(D, coin_i, 1, trig, want_stop=False)


def run():
    if code_dirty() and not os.environ.get("NKN_ALLOW_DIRTY"):
        sys.exit("code / PRE_REG.md have uncommitted changes: commit them before running")
    ser_c, ser_m, pcsv = load_cycle_tables()
    prov, raws = [], {}
    for coin in COINS:
        raws[coin] = load_15m(coin)
    # BTC SMA200 flag
    Db = daily_from_15m(raws["BTC"])
    b200 = pd.Series(Db["c"] > sma(Db["c"], 200), index=Db["t"] // DAY)
    Ds, perD = [], {}
    for ci, coin in enumerate(COINS):
        r = raws[coin]
        d = daily_from_15m(r)
        D = make_D(d["t"], d["o"], d["h"], d["l"], d["c"])
        fund = load_funding(coin)
        D = attach_ctx(D, ser_c, ser_m, b200, coin, fund)
        oi = load_oi(coin)
        if oi is not None:
            o_ = oi.reindex(D["t"] // DAY)
            D["oi"] = True
            D["oi5"] = (o_ / o_.shift(5) - 1).to_numpy()
        D["coin"] = coin
        Ds.append(D)
        prov.append(dict(coin=coin, first=int(r["t"][0]), last=int(r["t"][-1]), bars15=int(len(r["t"])), gaps15=r["gaps"], days=int(len(D["t"])),
                         first_day=str(dt.datetime.fromtimestamp(D["t"][0] / 1000, dt.UTC).date()), last_day=str(dt.datetime.fromtimestamp(D["t"][-1] / 1000, dt.UTC).date()),
                         funding=fund is not None, oi=oi is not None, key="ts" if "ts" in np.load(SPOT / f"{coin}USDT_15m.npz").files else "t"))
    # cross-check daily aggregation vs the htf 1d json on the majors
    xcheck = {}
    for coin in ["BTC", "ETH", "BNB", "SOL"]:
        p = HTF / f"{coin}USDT_1d.json"
        if p.exists():
            J = np.array(json.load(open(p)), float)
            jd = pd.Series(J[:, 4], index=(J[:, 0] // DAY).astype(int))
            D = Ds[COINS.index(coin)]
            mine = pd.Series(D["c"], index=D["t"] // DAY)
            both = pd.concat([mine, jd], axis=1, join="inner").dropna()
            rel = (both.iloc[:, 0] / both.iloc[:, 1] - 1).abs()
            xcheck[coin] = dict(days=int(len(both)), max_rel=float(rel.max()), share_gt_0_5pct=float((rel > 0.005).mean()))
    # trades per cell
    cellT = {k: [] for k, *_ in CELLS}
    poolsD = {s: {"DEV": {}, "VAL": {}} for s in ("L", "S")}
    mix = {"DEV": dict(UP=0, DOWN=0, RANGE=0, above200=0, n=0), "VAL": dict(UP=0, DOWN=0, RANGE=0, above200=0, n=0)}
    cyc_mix = {"DEV": dict(BEAR=0, BASE=0, BULL=0), "VAL": dict(BEAR=0, BASE=0, BULL=0)}
    for ci, D in enumerate(Ds):
        M, pools, _ = build_masks(D)
        for k, m in M.items():
            T = trades_for(D, ci, SIDE[k], m)
            cellT[k].append(T)
        for s in ("L", "S"):
            net, tsig = pool_net(D, ci, 1 if s == "L" else -1, pools[s])
            for nm, mm in (("DEV", tsig < SPLIT), ("VAL", tsig >= SPLIT)):
                poolsD[s][nm][ci] = net[mm]
        for nm, mm in (("DEV", D["t"] < SPLIT), ("VAL", D["t"] >= SPLIT)):
            v = mm & (D["phase"] != BAD_PH)
            mix[nm]["UP"] += int((v & (D["phase"] == 1)).sum()); mix[nm]["DOWN"] += int((v & (D["phase"] == -1)).sum())
            mix[nm]["RANGE"] += int((v & (D["phase"] == 0)).sum()); mix[nm]["n"] += int(v.sum())
            mix[nm]["above200"] += int((v & (D["c"] > D["s200"])).sum())
        if D["coin"] == "BTC":
            for nm, mm in (("DEV", D["t"] < SPLIT), ("VAL", D["t"] >= SPLIT)):
                for lab, code in CYC.items():
                    cyc_mix[nm][lab] = int((mm & (D["cyc"] == code)).sum())
        cellT[27].append(hourly_cell27(raws[D["coin"]], ci))
        cellT[28].append(weekly_cell28(D, ci))
        print("done", D["coin"], flush=True)
    results = dict(cells={}, mix=mix, cycle_mix_btc=cyc_mix, provenance=prov, xcheck=xcheck, commit=git("rev-parse", "HEAD"))
    rows = {}
    for (k, label, var, lvl, tf, side, trig, role) in CELLS:
        T = cat(cellT[k]) or empty_T()
        r = dict(id=k, label=label, variant=var, level=lvl, tf=tf, side=side, trigger=trig, role=role)
        for split in ("DEV", "VAL"):
            if k in (13, 14):
                continue
            r[split], S = row_stats(T, split, full=True, seed=100 + k)
        if k in (13, 14):
            ref = 1 if k == 13 else 4
            Tref = cat(cellT[ref])
            sd = "L" if k == 13 else "S"
            for split in ("DEV", "VAL"):
                m = (Tref["ts"] < SPLIT) if split == "DEV" else (Tref["ts"] >= SPLIT)
                pp, pm, ci95 = placebo(Tref["coin"][m], 0.0, poolsD[sd][split], seed=500 + k)
                r[split] = dict(n=int(m.sum()), net12=pm, placebo_ci=ci95)
        rows[k] = (r, T)
        if k in PRIMARY:
            pool = poolsD[POOL_OF[k]]["VAL"]
            S = sel(T, T["ts"] >= SPLIT)
            if len(S["t"]):
                netv = S["g"] - fee_r(S["entry"], S["x"], S["R"], 12.0)
                pp, pm, ci95 = placebo(S["coin"], float(netv.mean()), pool, seed=900 + k)
                r["placebo_p"], r["placebo_mean"], r["placebo_ci"] = pp, pm, ci95
        results["cells"][k] = r
    pv = []
    for k in PRIMARY:
        r = results["cells"][k]
        pv.append(r["VAL"].get("p_day", 1.0) if r["VAL"]["n"] >= 5 else 1.0)
    q = bh_q(pv)
    for k, qq in zip(PRIMARY, q):
        results["cells"][k]["bh_q"] = float(qq)
    for k in PRIMARY:
        r = results["cells"][k]
        v, dv = r["VAL"], r["DEV"]
        why = []
        if v["n"] < N_POWER:
            r["verdict"] = "UNDERPOWERED"; why.append(f"n VAL {v['n']} < {N_POWER}")
        elif dv.get("episodes", 0) < EP_MIN:
            r["verdict"] = "UNDERPOWERED"; why.append(f"DEV episodes {dv.get('episodes', 0)} < {EP_MIN}")
        else:
            gates = dict(mean_pos=bool(v["net12"] > 0), trade_ci=bool(v["trade_ci_low"] > 0), day_ci=bool(v["day_ci_low"] > 0), ex5=bool(v["ex5"] > 0),
                         placebo=bool(r.get("placebo_p", 1) < 0.05), bh=bool(r["bh_q"] <= 0.10), n200=bool(v["n"] >= N_PASS))
            r["gates"] = gates
            r["verdict"] = "PASS" if all(gates.values()) else "FAIL"
            why = [g for g, ok in gates.items() if not ok]
        r["why"] = why
    vs = [results["cells"][k]["verdict"] for k in PRIMARY]
    results["verdict"] = "PASS" if "PASS" in vs else ("UNDERPOWERED" if all(x == "UNDERPOWERED" for x in vs) else "FAIL")
    # claim test: 2-close vs 1-close day-cluster CI low
    claim = {}
    for nm, two, one in (("L-TURN", 1, 7), ("S-TURN", 4, 8)):
        claim[nm] = {s: dict(two=results["cells"][two][s].get("day_ci_low"), one=results["cells"][one][s].get("day_ci_low"),
                             n_two=results["cells"][two][s]["n"], n_one=results["cells"][one][s]["n"]) for s in ("DEV", "VAL")}
    results["claim"] = claim
    json.dump(results, open(HERE / "results.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    write_result(results)
    print("verdict", results["verdict"])


def f(x, d=3):
    return "n/a" if x is None or (isinstance(x, float) and x != x) else f"{x:.{d}f}"


def write_result(R):
    C = R["cells"]
    L = []
    L.append(f"**Verdict: {R['verdict']}** (NKN-02 two-close regime switch, 6 primary cells of 28 tried; daily, 20 spot coins, fee-net, VALIDATION = signal bar on/after 2024-01-01)")
    L.append("")
    mx = R["mix"]
    L.append("Regime mix: " + " | ".join(f"{s}: UP {mx[s]['UP'] / mx[s]['n']:.1%}, DOWN {mx[s]['DOWN'] / mx[s]['n']:.1%}, RANGE {mx[s]['RANGE'] / mx[s]['n']:.1%} (coin-days, trend phase), above own SMA200 {mx[s]['above200'] / mx[s]['n']:.1%}" for s in ("DEV", "VAL"))
          + " | BTC cycle days " + "; ".join(f"{s}: " + ", ".join(f"{a} {b}" for a, b in R["cycle_mix_btc"][s].items()) for s in ("DEV", "VAL")))
    L.append("")
    L.append(f"Code commit (study.py run): {R['commit']}. Total cells tried: 28. Primary cells: 6. Controls (22) are descriptive, never pooled, not in BH. Episodes (VAL): " +
             ", ".join(f"cell {k}: {C[k]['VAL'].get('episodes', 0)}" for k in PRIMARY) + ".")
    L.append("")
    L.append("## PRIMARY table (VALIDATION unless stated; net R at 12 bp taker is the verdict basis)")
    L.append("")
    L.append("| cell | phase tested | context conditions (S=SOURCED, O=OURS) | crypto translation | layer agreement | level type | timeframe | side | n DEV | n VAL | gross R | net R 12bp | net R 6bp | win % | trade CI low | day-cluster CI low | ex-best-5 | placebo p | BH q | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in PRIMARY:
        r = C[k]; v = r["VAL"]; d = r["DEV"]
        ctx = ("S: 2 closes vs SMA20/SMA50/SMA200 (a8RP5ftOfGo, PLJda-dtBIc); O: 10-of-30 drop-arming, cycle not BULL + coin DOWN/RANGE at prior close; S: stop = 2 closes back (lmhqooBqJWU)" if r["side"] == "long"
               else "S: 2 closes under SMA20 + all 10 closes < SMA200 (a8RP5ftOfGo, IjU9PpqvrI8); O: cycle BULL + coin UP/RANGE at prior close; S: stop = 2 closes back")
        lay = {"V0": "V0 rule alone", "V1": "V1 = V0 + ADX14>=20 & DI sign (O)", "V2": "V2 = V1 + RSI14 Malkan BULL/BEAR (S 40/60, O 20-bar)"}[r["variant"]]
        L.append(f"| {k} {r['label']} {r['variant']} | regime TURN (counter-trend entry into new trend) | {ctx} | UTC daily bar, signal 00:00 UTC close, entry next open (O) | {lay} | SMA200 (all distances; AT/AWAY in controls) | 1d | {r['side']} | {d['n']} | {v['n']} | "
                 f"{f(v.get('gross'))} | {f(v.get('net12'))} | {f(v.get('net6'))} | {f(100 * v['win'], 1) if 'win' in v else 'n/a'} | {f(v.get('trade_ci_low'))} | {f(v.get('day_ci_low'))} | {f(v.get('ex5'))} | {f(r.get('placebo_p'))} | {f(r.get('bh_q'))} | {r['verdict']} ({', '.join(r['why'])}) |")
    L.append("")
    L.append("Placebo (same coin, same phase/cycle pool, same side, matched count, same exit and fee): mean placebo net R at 12 bp per primary cell on VAL: " +
             ", ".join(f"cell {k}: {f(C[k].get('placebo_mean'))}" for k in PRIMARY) + ". \"Beats placebo\" and \"profitable\" are separate columns above (placebo p and net R).")
    L.append("")
    L.append("## Claim test (NK: a 1-close flip is a trap; 2 closes are safer): day-cluster CI low, 2-close V0 vs 1-close V0")
    L.append("")
    L.append("| cell | split | n 2-close | CI low 2-close | n 1-close | CI low 1-close | 2-close higher? |")
    L.append("|---|---|---|---|---|---|---|")
    for nm, c in R["claim"].items():
        for s in ("DEV", "VAL"):
            a, b = c[s]["two"], c[s]["one"]
            L.append(f"| {nm} | {s} | {c[s]['n_two']} | {f(a)} | {c[s]['n_one']} | {f(b)} | {('yes' if a > b else 'no') if a is not None and b is not None else 'n/a'} |")
    L.append("")
    L.append("## CONTROL table (descriptive; never pooled with primary, not in BH)")
    L.append("")
    L.append("| cell | variant | level | tf | side | trigger | n DEV | n VAL | gross R VAL | net R 12bp DEV | net R 12bp VAL | net R 6bp VAL | win % VAL | day CI low VAL | stop1R net12 VAL | floor beat structural VAL | med SMA20-SMA200 (ATR) | med days since SMA200 cross | VAL episodes |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for (k, label, var, lvl, tf, side, trig, role) in CELLS:
        if k in PRIMARY:
            continue
        r = C[k]; v = r["VAL"]; d = r["DEV"]
        L.append(f"| {k} {label} | {var} | {lvl} | {tf} | {side} | {trig} | {d['n']} | {v['n']} | {f(v.get('gross'))} | {f(d.get('net12'))} | {f(v.get('net12'))} | {f(v.get('net6'))} | {f(100 * v['win'], 1) if 'win' in v else 'n/a'} | {f(v.get('day_ci_low'))} | {f(v.get('net12_stop1R'))} | {f(v.get('floor_share'), 2)} | {f(v.get('med_gap_atr'), 2)} | {f(v.get('med_dcross'), 0)} | {v.get('episodes', 'n/a')} |")
    L.append("")
    L.append("Cells 13/14: n = matched count of cells 1/4 on the split, net R = mean of 1000 placebo means (random entries in the same coin and same phase/cycle pool).")
    L.append("")
    L.append("## DEV detail of the primary cells (selection-free: DEV is descriptive)")
    L.append("")
    L.append("| cell | n DEV | episodes DEV | net R 12bp DEV | day CI low DEV | median SMA20-SMA200 gap (ATR) VAL | median days since SMA200 cross VAL | floor beat structural VAL | OI 5d change median VAL |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for k in PRIMARY:
        r = C[k]; d = r["DEV"]; v = r["VAL"]
        L.append(f"| {k} | {d['n']} | {d.get('episodes', 0)} | {f(d.get('net12'))} | {f(d.get('day_ci_low'))} | {f(v.get('med_gap_atr'), 2)} | {f(v.get('med_dcross'), 0)} | {f(v.get('floor_share'), 2)} | {f(v.get('oi5_med'), 3)} |")
    L.append("")
    L.append("## Provenance (loader asserts the time key, strictly increasing timestamps, 15m alignment, min step 15m, gaps <= 12 h; gaps are exchange downtime and are kept as short days)")
    L.append("")
    L.append("| coin | key | first 15m bar (UTC ms) | last 15m bar | 15m bars | gaps | daily bars | first day | last complete day | funding file | OI file |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for p in R["provenance"]:
        L.append(f"| {p['coin']} | {p['key']} | {p['first']} | {p['last']} | {p['bars15']} | {p['gaps15']} | {p['days']} | {p['first_day']} | {p['last_day']} | {p['funding']} | {p['oi']} |")
    L.append("")
    L.append("Daily close cross-check against `binance_spot_htf/<COIN>_1d.json` (other source, majors only): " + "; ".join(f"{k}: {v['days']} days, max |rel diff| {v['max_rel']:.4f}, share > 0.5%: {v['share_gt_0_5pct']:.3f}" for k, v in R["xcheck"].items()) + ".")
    L.append("")
    dev_path = HERE / "DEVIATIONS.txt"
    L.append("## Deviations")
    L.append("")
    L.append(dev_path.read_text(encoding="utf-8").strip() if dev_path.exists() else "None recorded.")
    L.append("")
    L.append("## Parameter labels")
    L.append("")
    L.append("See PRE_REG.md section Parameters (SOURCED = video id + time; OURS = one value, no grid). No parameter here is NK's unless marked SOURCED.")
    (HERE / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run()
    else:
        print(__doc__)
