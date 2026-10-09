"""Volume study features and events (PRE_REG_VOLUME_2026-10-09.md sections 3-4). numpy only.

No look-ahead: every value at bar i uses bars <= i, and rolling windows end at i-1 unless the spec says otherwise.
Implementation clarifications (not in the pre-reg text, recorded in the report): warm-up W=150 bars (no event or baseline bar before it);
percentile = numpy linear interpolation; std = population (ddof=0).
"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv

W = 150
STRIDE = {"4h": 6, "1d": 7}      # bars per cycle for the time-adjusted baseline (slots per day / days per week)
KBASE = {"4h": 20, "1d": 8}      # cycles in the baseline (20 days / 8 weeks)


def prior_stat(x, w, fn):
    """fn over x[i-w:i] for i>=w; NaN before. fn is np.median / np.mean / np.max / np.min / np.std."""
    n = len(x)
    out = np.full(n, np.nan)
    if n > w:
        out[w:] = fn(swv(x, w)[:-1], axis=1)
    return out


def rv_plain(v):
    return v / prior_stat(v, 20, np.median)


def rv_adj(v, tf):
    s, k = STRIDE[tf], KBASE[tf]
    n = len(v)
    out = np.full(n, np.nan)
    if n > s * k:
        stack = np.stack([v[s * k - s * j: n - s * j] for j in range(1, k + 1)])   # j-th previous same-cycle bar
        out[s * k:] = v[s * k:] / np.median(stack, axis=0)
    return out


def rsi_wilder(c, period=14):
    """FORMULAS.md section 1: SMA seed over the first `period` deltas at index `period`, Wilder smoothing after; None -> NaN."""
    n = len(c)
    out = np.full(n, np.nan)
    if n <= period:
        return out
    d = np.diff(c)                                   # d[k] = c[k+1] - c[k]
    gain, loss = np.maximum(d, 0.0), np.maximum(-d, 0.0)
    ag, al = gain[:period].mean(), loss[:period].mean()

    def val(a, b):
        if b == 0:
            return 100.0 if a > 0 else 50.0
        return 100.0 - 100.0 / (1.0 + a / b)

    out[period] = val(ag, al)
    for i in range(period + 1, n):
        ag = (ag * (period - 1) + gain[i - 1]) / period
        al = (al * (period - 1) + loss[i - 1]) / period
        out[i] = val(ag, al)
    return out


def bollinger(c, n=20, k=2.0):
    mid = np.full(len(c), np.nan)
    sd = np.full(len(c), np.nan)
    if len(c) >= n:
        w = swv(c, n)
        mid[n - 1:] = w.mean(axis=1)
        sd[n - 1:] = w.std(axis=1)
    return mid, mid + k * sd, mid - k * sd


def squeeze_flags(bbw, win=120, q=20):
    """squeeze[j] = bbw[j] <= q-th percentile of bbw[j-win..j-1]."""
    n = len(bbw)
    out = np.zeros(n, dtype=bool)
    if n > win:
        ref = np.percentile(swv(bbw, win)[:-1], q, axis=1)
        out[win:] = bbw[win:] <= ref
    return out


def any_prev(flag, k):
    """out[i] = any(flag[i-k..i-1])."""
    n = len(flag)
    out = np.zeros(n, dtype=bool)
    if n > k:
        out[k:] = swv(flag.astype(np.int8), k)[:-1].max(axis=1) > 0
    return out


def features(b, tf):
    """Per-bar feature arrays for one timeframe dict (vdata bars)."""
    o, h, l, c, v, tbv = b["o"], b["h"], b["l"], b["c"], b["v"], b["tbv"]
    n = len(c)
    f = {"n": n}
    rng = h - l
    with np.errstate(divide="ignore", invalid="ignore"):
        f["rng"] = rng
        f["clv"] = np.where(rng > 0, (c - l) / rng, np.nan)
        f["dp"] = (2 * tbv - v) / v
        cprev = np.concatenate([[c[0]], c[:-1]])
        tr = np.maximum(h - l, np.maximum(np.abs(h - cprev), np.abs(l - cprev)))
        atr = prior_stat(tr, 14, np.mean)
        f["rr"] = rng / atr
        mu, sdv = prior_stat(f["dp"], 60, np.mean), prior_stat(f["dp"], 60, np.std)
        f["dpz"] = (f["dp"] - mu) / sdv
        f["rv"] = rv_plain(v)
        f["rvadj"] = rv_adj(v, tf)
    f["rsi"] = rsi_wilder(c, 14)
    mid, up, lo = bollinger(c)
    f["bb_up"], f["bb_lo"] = up, lo
    bbw = (up - lo) / mid
    f["bbw"] = bbw
    sq = np.zeros(n, dtype=bool)
    ok = ~np.isnan(bbw)
    first = int(np.argmax(ok)) if ok.any() else n
    s2 = squeeze_flags(bbw[first:])
    sq[first:] = s2
    f["squeeze"] = sq
    f["sq_recent"] = any_prev(sq, 5)
    f["cvd"] = np.cumsum(2 * tbv - v)
    sgn = np.sign(np.diff(c, prepend=c[0]))
    f["obv"] = np.cumsum(sgn * v)
    f["pmax_h"] = prior_stat(h, 20, np.max)
    f["pmin_l"] = prior_stat(l, 20, np.min)
    f["pmax_c"] = prior_stat(c, 20, np.max)
    f["pmin_c"] = prior_stat(c, 20, np.min)
    f["pmax_cvd"] = prior_stat(f["cvd"], 20, np.max)
    f["pmin_cvd"] = prior_stat(f["cvd"], 20, np.min)
    f["pmax_obv"] = prior_stat(f["obv"], 20, np.max)
    f["pmin_obv"] = prior_stat(f["obv"], 20, np.min)
    f["ctx_up"] = np.concatenate([np.zeros(11, dtype=bool), c[10:-1] > c[:-11]]) if n > 11 else np.zeros(n, dtype=bool)
    f["ctx_dn"] = np.concatenate([np.zeros(11, dtype=bool), c[10:-1] < c[:-11]]) if n > 11 else np.zeros(n, dtype=bool)
    # bands as of i-1 for breakout tests
    f["up_prev"] = np.concatenate([[np.nan], up[:-1]])
    f["lo_prev"] = np.concatenate([[np.nan], lo[:-1]])
    return f


def _mean_prev(x, k):
    """mean(x[i-k..i-1])."""
    n = len(x)
    out = np.full(n, np.nan)
    if n > k:
        out[k:] = swv(x, k)[:-1].mean(axis=1)
    return out


# event name -> continuation direction (+1 long-after-event is "continuation"; -1 short)
DIRS = {
    "SP2_UP": 1, "SP2_DN": -1, "SP3_UP": 1, "SP3_DN": -1,
    "BCLX": 1, "SCLX": -1, "BAWAY_UP": 1, "BAWAY_DN": -1,
    "ABS_LOW": -1, "ABS_HIGH": 1, "NODEM_HIGH": 1, "NOSUP_LOW": -1,
    "DBUY": 1, "DSELL": -1, "CVDDIV_BEAR": 1, "CVDDIV_BULL": -1, "OBVDIV_BEAR": 1, "OBVDIV_BULL": -1,
    "BBSQ_UP_V": 1, "BBSQ_UP_N": 1, "BBSQ_DN_V": -1, "BBSQ_DN_N": -1, "BBALL_UP": 1, "BBALL_DN": -1,
    "DON_UP_V": 1, "DON_UP_N": 1, "DON_DN_V": -1, "DON_DN_N": -1,
    "DRY_UP": 1, "DRY_DN": -1,
    "R60U_V": 1, "R60U_N": 1, "R40D_V": -1, "R40D_N": -1, "R40RECL_V": 1, "R60REJ_V": -1,
}
EVENT_NAMES = list(DIRS)
assert len(EVENT_NAMES) == 36


def events(b, f):
    """name -> bool array (False before warm-up W and wherever an input is undefined)."""
    o, h, l, c = b["o"], b["h"], b["l"], b["c"]
    n = f["n"]
    rv = f["rvadj"]
    up_bar, dn_bar = c > o, c < o
    nh, nl = h > f["pmax_h"], l < f["pmin_l"]
    clv, rr = f["clv"], f["rr"]
    with np.errstate(invalid="ignore"):
        e = {}
        e["SP2_UP"], e["SP2_DN"] = (rv >= 2) & up_bar, (rv >= 2) & dn_bar
        e["SP3_UP"], e["SP3_DN"] = (rv >= 3) & up_bar, (rv >= 3) & dn_bar
        e["BCLX"] = (rv >= 2) & nh & (clv <= 1 / 3)
        e["SCLX"] = (rv >= 2) & nl & (clv >= 2 / 3)
        e["BAWAY_UP"] = (rv >= 2) & nh & (clv >= 2 / 3)
        e["BAWAY_DN"] = (rv >= 2) & nl & (clv <= 1 / 3)
        e["ABS_LOW"] = (rv >= 2) & (rr <= 0.8) & f["ctx_dn"]
        e["ABS_HIGH"] = (rv >= 2) & (rr <= 0.8) & f["ctx_up"]
        e["NODEM_HIGH"] = nh & (rv <= 0.8)
        e["NOSUP_LOW"] = nl & (rv <= 0.8)
        e["DBUY"] = (f["dpz"] >= 2) & up_bar
        e["DSELL"] = (f["dpz"] <= -2) & dn_bar
        e["CVDDIV_BEAR"] = (c > f["pmax_c"]) & (f["cvd"] < f["pmax_cvd"])
        e["CVDDIV_BULL"] = (c < f["pmin_c"]) & (f["cvd"] > f["pmin_cvd"])
        e["OBVDIV_BEAR"] = (c > f["pmax_c"]) & (f["obv"] < f["pmax_obv"])
        e["OBVDIV_BULL"] = (c < f["pmin_c"]) & (f["obv"] > f["pmin_obv"])
        sq = f["sq_recent"]
        bup, bdn = c > f["up_prev"], c < f["lo_prev"]
        hi_v, lo_v = rv >= 1.5, rv < 1.5
        e["BBSQ_UP_V"], e["BBSQ_UP_N"] = sq & bup & hi_v, sq & bup & lo_v
        e["BBSQ_DN_V"], e["BBSQ_DN_N"] = sq & bdn & hi_v, sq & bdn & lo_v
        e["BBALL_UP"], e["BBALL_DN"] = bup, bdn
        donup = c > f["pmax_h"]
        dondn = c < f["pmin_l"]
        e["DON_UP_V"], e["DON_UP_N"] = donup & hi_v, donup & lo_v
        e["DON_DN_V"], e["DON_DN_N"] = dondn & hi_v, dondn & lo_v
        dry = _mean_prev(np.nan_to_num(rv, nan=np.inf), 5) <= 0.8
        e["DRY_UP"] = sq & dry & bup & (rv >= 1.5)
        e["DRY_DN"] = sq & dry & bdn & (rv >= 1.5)
        rsi = f["rsi"]
        rprev = np.concatenate([[np.nan], rsi[:-1]])
        e["R60U_V"], e["R60U_N"] = (rprev < 60) & (rsi >= 60) & hi_v, (rprev < 60) & (rsi >= 60) & lo_v
        e["R40D_V"], e["R40D_N"] = (rprev > 40) & (rsi <= 40) & hi_v, (rprev > 40) & (rsi <= 40) & lo_v
        e["R40RECL_V"] = (rprev < 40) & (rsi >= 40) & hi_v
        e["R60REJ_V"] = (rprev > 60) & (rsi <= 60) & hi_v
    valid = np.arange(n) >= W
    out = {}
    for k in EVENT_NAMES:
        a = np.asarray(e[k], dtype=bool) & valid & (f["rng"] > 0)
        out[k] = a
    return out


def plain_rv_spikes(b, f):
    """SP3 events defined with plain RV instead of RVadj (contrast C7)."""
    c, o = b["c"], b["o"]
    rv = f["rv"]
    valid = (np.arange(f["n"]) >= W) & (f["rng"] > 0)
    with np.errstate(invalid="ignore"):
        return {"SP3_UP": (rv >= 3) & (c > o) & valid, "SP3_DN": (rv >= 3) & (c < o) & valid}


def slot_keys(b, tf):
    """slot (0..5 for 4h, else 0), weekday (0=Mon), weekend flag, session group (0=A,1=B,2=C for 4h)."""
    t = b["t"]
    day = t // 86400000
    weekday = ((day + 3) % 7).astype(int)          # 1970-01-01 was a Thursday (=3 with Mon=0)
    slot = ((t % 86400000) // (4 * 3600000)).astype(int) if tf == "4h" else np.zeros(len(t), dtype=int)
    sg = np.where(slot <= 1, 0, np.where(slot <= 3, 1, 2)) if tf == "4h" else np.zeros(len(t), dtype=int)
    return {"slot": slot, "weekday": weekday, "weekend": weekday >= 5, "sg": sg}
