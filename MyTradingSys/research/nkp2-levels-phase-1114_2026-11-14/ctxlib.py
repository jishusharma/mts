"""Context layers C1-C8 (MTS_BRAINS_SPEC_1114 s2) on a 1h signal grid. A value for 1h bar i is computed at T = open(i)+1h from data CLOSED at or before T.
Buckets are int8: 0 = low / bull-div / unwind / neg / asia / compress, 1 = mid, 2 = high / bear-div / build / hot / us / expand; -1 = no data.
STUDY_BUG=2 env = deliberate look-ahead: higher-timeframe values come from the bar CONTAINING the signal bar (includes its future part)."""
import os
import numpy as np

H1, H4, DAY = 3600000, 4 * 3600000, 86400000
LAYERS = ["C1_rsi4h", "C2_wt1d", "C3_bbpb4h", "C4_oi24h", "C5_funding", "C6_taker_div24h", "C7_rv7_60", "C8_session"]
BUCKET_NAMES = {
    "C1_rsi4h": ["<=40", "mid", ">=60"], "C2_wt1d": ["<=-53", "mid", ">=+53"], "C3_bbpb4h": ["<0.10", "mid", ">0.90"],
    "C4_oi24h": ["<=-3%", "flat", ">=+3%"], "C5_funding": ["<0", "0..0.03%", ">0.03%"], "C6_taker_div24h": ["bull-div", "agree", "bear-div"],
    "C7_rv7_60": ["<0.7", "mid", ">1.3"], "C8_session": ["asia", "eu", "us"],
}


def bug2():
    return os.environ.get("STUDY_BUG") == "2"


def resample(t, o, h, l, c, v, k):
    """group k consecutive 15m bars on the UTC boundary of k*15m; complete groups only."""
    per = 900000 * k
    g = t // per
    idx = np.flatnonzero(np.r_[True, g[1:] != g[:-1]])
    ends = np.r_[idx[1:], len(t)]
    keep = ((ends - idx) == k) & (t[idx] % per == 0)
    return (t[idx][keep], o[idx][keep], np.maximum.reduceat(h, idx)[keep], np.minimum.reduceat(l, idx)[keep], c[ends - 1][keep], np.add.reduceat(v, idx)[keep])


def ema(x, n):
    a = 2.0 / (n + 1)
    out = np.full(len(x), np.nan)
    s = np.nan
    for i, v in enumerate(x):
        if np.isnan(v):
            continue
        s = v if np.isnan(s) else s + a * (v - s)
        out[i] = s
    return out


def wilder_rsi(c, n=14):
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    up, dn = np.maximum(d, 0), np.maximum(-d, 0)
    au, ad = up[:n].mean(), dn[:n].mean()
    out[n] = 100 - 100 / (1 + au / ad) if ad > 0 else 100
    for i in range(n + 1, len(c)):
        au = (au * (n - 1) + up[i - 1]) / n
        ad = (ad * (n - 1) + dn[i - 1]) / n
        out[i] = 100 - 100 / (1 + au / ad) if ad > 0 else 100
    return out


def wavetrend1(h, l, c, warm=200):
    """LazyBear WT1 (FORMULAS s20.1): ap=hlc3, esa=EMA10(ap), d=EMA10(|ap-esa|), ci=(ap-esa)/(0.015 d), wt1=EMA21(ci). NaN for the first `warm` bars."""
    ap = (h + l + c) / 3
    esa = ema(ap, 10)
    d = ema(np.abs(ap - esa), 10)
    with np.errstate(all="ignore"):
        ci = (ap - esa) / (0.015 * d)
    ci[~(d > 1e-9 * np.abs(ap))] = np.nan
    wt = ema(ci, 21)
    wt[:warm] = np.nan
    return wt


def bollinger_pb(c, n=20):
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    w = np.lib.stride_tricks.sliding_window_view(c, n)
    m, sd = w.mean(axis=1), w.std(axis=1)
    up, lo = m + 2 * sd, m - 2 * sd
    with np.errstate(all="ignore"):
        out[n - 1:] = (c[n - 1:] - lo) / (up - lo)
    return out


def _bucket(x, lo, hi, lo_incl=True, hi_incl=True):
    b = np.full(len(x), 1, dtype=np.int8)
    with np.errstate(invalid="ignore"):
        b[(x <= lo) if lo_incl else (x < lo)] = 0
        b[(x >= hi) if hi_incl else (x > hi)] = 2
    b[np.isnan(x)] = -1
    return b


def _htf_index(tk, length, t1):
    """index of the higher-timeframe bar to use for each 1h bar: last bar closed at T=t1+1h (BUG=2: the bar containing the 1h bar)."""
    if bug2():
        return np.searchsorted(tk, t1, side="right") - 1
    return np.searchsorted(tk + length, t1 + H1, side="right") - 1


def _take(x, idx):
    out = np.full(len(idx), np.nan)
    ok = idx >= 0
    out[ok] = x[idx[ok]]
    return out


def _exact_lookup(ts, val, keys):
    """value at exactly `keys` (ms) else nan."""
    out = np.full(len(keys), np.nan)
    if ts is None or len(ts) == 0:
        return out
    j = np.searchsorted(ts, keys)
    jj = np.minimum(j, len(ts) - 1)
    ok = (j < len(ts)) & (ts[jj] == keys)
    out[ok] = val[jj[ok]]
    return out


def compute_context(raw):
    """raw: dict with 15m arrays t,o,h,l,c,v and optional kl (ts,c,v,tbv), fund (ts,rate), oi (ts,oi_value).
    returns dict: t1,o1,h1,l1,c1 (1h bars) and ctx = int8 array (8, n1h) rows in LAYERS order."""
    t1, o1, h1, l1, c1, v1 = resample(raw["t"], raw["o"], raw["h"], raw["l"], raw["c"], raw["v"], 4)
    t4, o4, h4, l4, c4, v4 = resample(raw["t"], raw["o"], raw["h"], raw["l"], raw["c"], raw["v"], 16)
    td, od, hd, ld, cd, vd = resample(raw["t"], raw["o"], raw["h"], raw["l"], raw["c"], raw["v"], 96)
    n = len(t1)
    ctx = np.full((8, n), -1, dtype=np.int8)
    i4 = _htf_index(t4, H4, t1)
    idd = _htf_index(td, DAY, t1)
    ctx[0] = _bucket(_take(wilder_rsi(c4), i4), 40, 60)
    ctx[1] = _bucket(_take(wavetrend1(hd, ld, cd), idd), -53, 53)
    ctx[2] = _bucket(_take(bollinger_pb(c4), i4), 0.10, 0.90, lo_incl=False, hi_incl=False)
    # C4 OI change 24h: hourly series keyed by hour start; hour [t1, t1+1h) is complete at T
    oi = raw.get("oi")
    if oi is not None:
        now = _exact_lookup(oi["ts"], oi["oi_value"], t1)
        prev = _exact_lookup(oi["ts"], oi["oi_value"], t1 - 24 * H1)
        with np.errstate(all="ignore"):
            ctx[3] = _bucket(now / prev - 1, -0.03, 0.03)
    # C5 funding: mean of last 3 settlements at or before T; NO-DATA when the file ends before T-9h
    fu = raw.get("fund")
    if fu is not None and len(fu["ts"]) >= 3:
        T = t1 + H1
        j = np.searchsorted(fu["ts"], T, side="right") - 1
        ok = (j >= 2) & ((T - fu["ts"][np.maximum(j, 0)]) <= 9 * H1)
        jj = np.maximum(j, 2)
        m = (fu["rate"][jj] + fu["rate"][jj - 1] + fu["rate"][jj - 2]) / 3
        m[~ok] = np.nan
        b = np.full(n, 1, dtype=np.int8)
        b[m < 0] = 0
        b[m > 0.0003] = 2
        b[np.isnan(m)] = -1
        ctx[4] = b
    # C6 taker delta vs price, 24 1h bars
    kl = raw.get("kl")
    if kl is not None:
        j = np.searchsorted(kl["ts"], t1)
        jj = np.minimum(j, len(kl["ts"]) - 1)
        ok = (j < len(kl["ts"])) & (kl["ts"][jj] == t1)
        v = np.where(ok, kl["v"][jj], np.nan)
        tb = np.where(ok, kl["tbv"][jj], np.nan)
        cc = np.where(ok, kl["c"][jj], np.nan)
        good = (~np.isnan(v)).astype(float)
        cs = lambda x: np.r_[0, np.cumsum(np.nan_to_num(x))]
        cnt = cs(good)
        sv, st = cs(v), cs(tb)
        td24 = np.full(n, np.nan)
        p24 = np.full(n, np.nan)
        if n > 24:
            k = np.arange(23, n)
            full = (cnt[k + 1] - cnt[k - 23]) == 24
            sv24 = sv[k + 1] - sv[k - 23]
            st24 = st[k + 1] - st[k - 23]
            with np.errstate(all="ignore"):
                td24[k] = np.where(full & (sv24 > 0), (2 * st24 - sv24) / sv24, np.nan)
                p24[24:] = cc[24:] / cc[:-24] - 1
        b = np.full(n, 1, dtype=np.int8)
        b[(p24 < 0) & (td24 > 0)] = 0
        b[(p24 > 0) & (td24 < 0)] = 2
        b[np.isnan(p24) | np.isnan(td24)] = -1
        ctx[5] = b
    # C7 RV7/RV60 of 1h log returns
    lr = np.r_[np.nan, np.diff(np.log(c1))]
    z = np.nan_to_num(lr)
    c1s, c2s = np.r_[0, np.cumsum(z)], np.r_[0, np.cumsum(z * z)]
    def rv(w):
        out = np.full(n, np.nan)
        if n > w + 1:
            k = np.arange(w, n)  # returns k-w+1..k
            s1 = c1s[k + 1] - c1s[k + 1 - w]
            s2 = c2s[k + 1] - c2s[k + 1 - w]
            out[k] = np.sqrt(np.maximum(s2 / w - (s1 / w) ** 2, 0))
        return out
    with np.errstate(all="ignore"):
        ratio = rv(168) / rv(1440)
    ctx[6] = _bucket(ratio, 0.70, 1.30, lo_incl=False, hi_incl=False)
    # C8 session of the signal close hour
    hr = ((t1 + H1) // H1) % 24
    s = np.full(n, 0, dtype=np.int8)
    s[(hr >= 7) & (hr < 13)] = 1
    s[(hr >= 13) & (hr < 21)] = 2
    ctx[7] = s
    return dict(t1=t1, o1=o1, h1=h1, l1=l1, c1=c1, ctx=ctx, td=td, hd=hd, ld=ld, cd=cd)
