"""Published rule-based strategies on BTCUSDT perp. Frozen design: PRE_REG.md. Numpy only.

python run_pub.py dev            -> DEV for all variants, prints advancers
python run_pub.py val            -> VAL for DEV advancers
python run_pub.py hold           -> HOLD for VAL advancers
"""
import sys, glob, json, csv, os, datetime as dt
import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
DUMPS = os.environ.get("MTS_DUMPS", r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\Dumps\backtest")
SYMBOL = os.environ.get("PUB_SYMBOL", "BTCUSDT")
ONLY = [x for x in os.environ.get("PUB_ONLY", "").split(",") if x]
FEE = float(os.environ.get("PUB_FEE", "0.001"))  # per side per leg
K = 2000
SEALED_FROM = int(dt.datetime(2025, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)


def ms(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000)


WIN = {"DEV": (ms(2021, 1, 1), ms(2023, 7, 1)), "VAL": (ms(2023, 7, 1), ms(2024, 7, 1)), "HOLD": (ms(2024, 7, 1), ms(2025, 7, 1))}
HOUR = 3600_000
TFMS = {"1h": HOUR, "4h": 4 * HOUR, "1d": 24 * HOUR}
BPY = {"1h": 8760, "4h": 2190, "1d": 365}


# ---------------------------------------------------------------- data
def _loadcsv(f, cols):
    with open(f) as fh:
        first = fh.readline()
    skip = 0 if first[:1].isdigit() or first[:1] == "-" else 1  # some monthly files carry a header, some do not
    return np.loadtxt(f, delimiter=",", skiprows=skip, usecols=cols)


def load_1h():
    rows = [_loadcsv(f, (0, 1, 2, 3, 4, 5)).reshape(-1, 6)
            for f in sorted(glob.glob(f"{DUMPS}/raw_1h/klines/{SYMBOL}-1h-*.csv"))]
    a = np.vstack(rows)
    a = a[np.unique(a[:, 0], return_index=True)[1]]
    assert (np.diff(a[:, 0]) == HOUR).all(), "gap in 1h data"
    return a


def resample(a, tf):
    if tf == "1h":
        return a
    w = TFMS[tf]
    key = (a[:, 0] // w).astype(np.int64)
    idx = np.r_[0, np.nonzero(np.diff(key))[0] + 1]
    n = HOUR and w // HOUR
    keep = [i for i in idx if i + n <= len(a) and key[i + n - 1] == key[i]]
    out = np.empty((len(keep), 6))
    for j, i in enumerate(keep):
        s = a[i:i + n]
        out[j] = (s[0, 0], s[0, 1], s[:, 2].max(), s[:, 3].min(), s[-1, 4], s[:, 5].sum())
    return out


def load_funding():
    rows = [_loadcsv(f, None).reshape(-1, 3)
            for f in sorted(glob.glob(f"{DUMPS}/raw_fund/fundingRate/{SYMBOL}-fundingRate-*.csv"))]
    a = np.vstack(rows)
    return a[np.argsort(a[:, 0])]


class Bars:
    def __init__(self, a, fund, tf):
        self.tf = tf
        self.t, self.o, self.h, self.l, self.c = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        w = TFMS[tf]
        self.fund = np.zeros(len(a))  # sum of settled rates inside each bar
        j = np.searchsorted(self.t, fund[:, 0] - fund[:, 0] % 1, side="right") - 1
        # settlement time T belongs to the bar with open <= T < open + w
        ok = (j >= 0) & (fund[:, 0] < self.t[np.clip(j, 0, len(a) - 1)] + w)
        np.add.at(self.fund, j[ok], fund[ok, 2])
        self.dt = [dt.datetime.fromtimestamp(x / 1000, dt.timezone.utc) for x in self.t] if tf != "1h" or True else None
        self.n = len(a)


# ---------------------------------------------------------------- indicators
def sma(x, n):
    out = np.full(len(x), np.nan)
    cs = np.cumsum(np.insert(x, 0, 0.0))
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def rmax(x, n, lag=0):  # max of x[t-lag-n+1..t-lag]
    out = np.full(len(x), np.nan)
    v = np.lib.stride_tricks.sliding_window_view(x, n).max(axis=1)
    out[n - 1 + lag:] = v[:len(x) - n + 1 - lag] if lag else v
    return out


def rmin(x, n, lag=0):
    return -rmax(-x, n, lag)


def rstd(x, n):
    out = np.full(len(x), np.nan)
    out[n - 1:] = np.lib.stride_tricks.sliding_window_view(x, n).std(axis=1)
    return out


def rsi(c, n):
    out = np.full(len(c), np.nan)
    d = np.diff(c)
    up, dn = np.maximum(d, 0), np.maximum(-d, 0)
    au, ad = up[:n].mean(), dn[:n].mean()
    out[n] = 100 if ad == 0 else 100 - 100 / (1 + au / ad)
    for i in range(n, len(d)):
        au = (au * (n - 1) + up[i]) / n
        ad = (ad * (n - 1) + dn[i]) / n
        out[i + 1] = 100 if ad == 0 else 100 - 100 / (1 + au / ad)
    return out


def ewma_vol(c, com=60, ann=365):
    r = np.r_[np.nan, c[1:] / c[:-1] - 1]
    a = 1 / (1 + com)
    var = np.full(len(c), np.nan)
    v = None
    for i in range(1, len(c)):
        if v is None:
            v = r[i] ** 2
        else:
            v = (1 - a) * v + a * r[i - 1 + 1] ** 2
        var[i] = v
    sig = np.sqrt(var * ann)
    sig[:30] = np.nan
    return sig


# ---------------------------------------------------------------- strategies: return dict(pos, kind, off)
# kind 'sig': pos[t] decided at close t, held over bar t+1.  'held': pos[t] held during bar t.
# 'intra': pos[t] entered inside bar t at open*(1+off[t]) and closed at bar close.  'carry': delta-neutral.
def S_tsmom(b, L, mode):
    c = b.c
    ret = np.full(len(c), np.nan)
    ret[L:] = c[L:] / c[:-L] - 1
    s = np.sign(ret)
    s[np.isnan(ret)] = 0
    if mode == "lf":
        s = np.maximum(s, 0)
    if mode == "lsvs":
        sig = ewma_vol(c)
        w = np.where(np.isnan(sig), 0, np.minimum(3.0, 0.40 / np.where(sig > 0, sig, np.nan)))
        s = s * np.nan_to_num(w)
    return dict(pos=s, kind="sig")


def S_donchian(b, nin, nout, ls):
    n = b.n
    pos = np.zeros(n)
    hi = rmax(b.h, nin, lag=1)
    lo_e = rmin(b.l, nin, lag=1)
    hi_x = rmax(b.h, nout, lag=1)
    lo_x = rmin(b.l, nout, lag=1)
    p = 0
    for t in range(n):
        c = b.c[t]
        if p == 0:
            if hi[t] == hi[t] and c > hi[t]:
                p = 1
            elif ls and lo_e[t] == lo_e[t] and c < lo_e[t]:
                p = -1
        elif p == 1:
            if lo_x[t] == lo_x[t] and c < lo_x[t]:
                p = -1 if (ls and lo_e[t] == lo_e[t] and c < lo_e[t]) else 0
        else:
            if hi_x[t] == hi_x[t] and c > hi_x[t]:
                p = 1 if (hi[t] == hi[t] and c > hi[t]) else 0
        pos[t] = p
    return dict(pos=pos, kind="sig")


def S_ma(b, n, ls, cross=None):
    if cross:
        f, s_ = sma(b.c, cross[0]), sma(b.c, cross[1])
        up = f > s_
        dn = f < s_
        valid = ~(np.isnan(f) | np.isnan(s_))
    else:
        m = sma(b.c, n)
        up, dn, valid = b.c > m, b.c < m, ~np.isnan(m)
    pos = np.where(valid & up, 1.0, 0.0)
    if ls:
        pos = np.where(valid & dn, -1.0, pos)
    return dict(pos=pos, kind="sig")


def S_rsi2(b, thr, ls):
    r = rsi(b.c, 2)
    m200, m5 = sma(b.c, 200), sma(b.c, 5)
    pos = np.zeros(b.n)
    p = 0
    for t in range(b.n):
        if np.isnan(r[t]) or np.isnan(m200[t]):
            continue
        c = b.c[t]
        if p == 0:
            if r[t] < thr and c > m200[t]:
                p = 1
            elif ls and r[t] > 100 - thr and c < m200[t]:
                p = -1
        elif p == 1 and c > m5[t]:
            p = 0
        elif p == -1 and c < m5[t]:
            p = 0
        pos[t] = p
    return dict(pos=pos, kind="sig")


def S_double7(b, ls):
    m200 = sma(b.c, 200)
    lo7, hi7 = rmin(b.c, 7), rmax(b.c, 7)
    pos = np.zeros(b.n)
    p = 0
    for t in range(b.n):
        if np.isnan(m200[t]) or np.isnan(lo7[t]):
            continue
        c = b.c[t]
        if p == 0:
            if c > m200[t] and c <= lo7[t]:
                p = 1
            elif ls and c < m200[t] and c >= hi7[t]:
                p = -1
        elif p == 1 and c >= hi7[t]:
            p = 0
        elif p == -1 and c <= lo7[t]:
            p = 0
        pos[t] = p
    return dict(pos=pos, kind="sig")


def S_ibs(b, ls):
    rng = b.h - b.l
    ibs = np.where(rng > 0, (b.c - b.l) / np.where(rng > 0, rng, 1), 0.5)
    pos = np.zeros(b.n)
    p = 0
    for t in range(1, b.n):
        if p == 0:
            if ibs[t] < 0.2:
                p = 1
            elif ls and ibs[t] > 0.8:
                p = -1
        elif p == 1 and b.c[t] > b.h[t - 1]:
            p = 0
        elif p == -1 and b.c[t] < b.l[t - 1]:
            p = 0
        pos[t] = p
    return dict(pos=pos, kind="sig")


ONE_H = {}


def S_williams(b, k, ls):
    """Entry at the first touch of open +/- k*prior range, exit at bar close. First touch is read from the 1h bars inside
    the bar; if both triggers sit in the same 1h bar the worse side is taken (close-direction opposite). No lookahead."""
    h1, l1, t1 = ONE_H["h"], ONE_H["l"], ONE_H["t"]
    w = TFMS[b.tf]
    pr = np.r_[np.nan, (b.h - b.l)[:-1]]
    lt = b.o + k * pr
    st = b.o - k * pr
    pos = np.zeros(b.n)
    off = np.zeros(b.n)
    i0 = np.searchsorted(t1, b.t)
    i1 = np.searchsorted(t1, b.t + w)
    for t in range(b.n):
        if np.isnan(pr[t]) or pr[t] <= 0:
            continue
        hh, ll = h1[i0[t]:i1[t]], l1[i0[t]:i1[t]]
        up = np.nonzero(hh >= lt[t])[0]
        dn = np.nonzero(ll <= st[t])[0] if ls else np.array([], int)
        fu = up[0] if len(up) else 10**9
        fd = dn[0] if len(dn) else 10**9
        if fu == 10**9 and fd == 10**9:
            continue
        if fu < fd:
            side = 1
        elif fd < fu:
            side = -1
        else:  # same 1h bar: take the side that loses
            side = -1 if b.c[t] > b.o[t] else 1
        pos[t] = side
        off[t] = (lt[t] if side > 0 else st[t]) / b.o[t] - 1
    return dict(pos=pos, kind="intra", off=off)


def S_boll(b, ls):
    m, sd = sma(b.c, 20), rstd(b.c, 20)
    pos = np.zeros(b.n)
    p = 0
    for t in range(b.n):
        if np.isnan(m[t]):
            continue
        c = b.c[t]
        if p == 0:
            if c > m[t] + 2 * sd[t]:
                p = 1
            elif ls and c < m[t] - 2 * sd[t]:
                p = -1
        elif p == 1 and c < m[t]:
            p = 0
        elif p == -1 and c > m[t]:
            p = 0
        pos[t] = p
    return dict(pos=pos, kind="sig")


def S_dow(b, d):
    return dict(pos=np.array([1.0 if x.weekday() == d else 0.0 for x in b.dt]), kind="held")


def S_tom(b):
    out = np.zeros(b.n)
    for i, x in enumerate(b.dt):
        nxt = x + dt.timedelta(days=1)
        out[i] = 1.0 if (x.day <= 3 or nxt.month != x.month) else 0.0
    return dict(pos=out, kind="held")


def S_session(b, h0, h1):
    return dict(pos=np.array([1.0 if h0 <= x.hour < h1 else 0.0 for x in b.dt]), kind="held")


def S_carry(b, switch):
    if not switch:
        return dict(pos=np.ones(b.n), kind="carry")
    f = b.fund
    f3 = np.convolve(f, np.ones(3), mode="full")[:b.n]  # trailing 3 daily sums ~ 9 settlements
    pos = np.where(f3 > 0, 1.0, 0.0)
    pos[:3] = 0
    return dict(pos=pos, kind="sig_carry")


def S_fund_dir(b, sign):
    f = b.fund / 3.0  # mean per settlement on a daily bar
    s = np.where(f > 0.00011, -1.0, np.where(f < 0.00009, 1.0, 0.0)) * sign
    return dict(pos=s, kind="sig")


def S_vt(b, cap):
    r = np.r_[np.nan, b.c[1:] / b.c[:-1] - 1]
    sd = rstd(np.nan_to_num(r), 20) * np.sqrt(365)
    w = np.where(sd > 0, np.minimum(cap, 0.40 / np.where(sd > 0, sd, np.nan)), 0)
    return dict(pos=np.nan_to_num(w), kind="sig")


def S_bh(b):
    return dict(pos=np.ones(b.n), kind="held")


def variants():
    V = []  # (id, family, tf, fn, args, note)
    for L in (30, 90, 180, 365):
        for mode in ("ls", "lf", "lsvs"):
            V.append((f"TSMOM_{L}d_{mode}", "TSMOM", "1d", S_tsmom, (L, mode), "MOP2012"))
    for tf in ("1d", "4h"):
        for nin, nout in ((20, 10), (55, 20)):
            for ls in (0, 1):
                V.append((f"DON_{tf}_{nin}_{nout}_{'ls' if ls else 'lf'}", "DONCHIAN", tf, S_donchian, (nin, nout, ls), "Turtle"))
    for n in (50, 100, 200):
        for ls in (0, 1):
            V.append((f"MA_P>SMA{n}_{'ls' if ls else 'lf'}", "MA", "1d", S_ma, (n, ls), "Faber/BLL"))
    for ls in (0, 1):
        V.append((f"MA_X50_200_{'ls' if ls else 'lf'}", "MA", "1d", S_ma, (0, ls, (50, 200)), "golden cross"))
        V.append((f"MA_P>SMA7_{'ls' if ls else 'lf'}", "MA", "1d", S_ma, (7, ls), "Detzel PMA1"))
    for thr in (10, 5):
        for ls in (0, 1):
            V.append((f"RSI2_{thr}_1d_{'ls' if ls else 'lf'}", "MEANREV", "1d", S_rsi2, (thr, ls), "Connors"))
    for ls in (0, 1):
        V.append((f"DOUBLE7_{'ls' if ls else 'lf'}", "MEANREV", "1d", S_double7, (ls,), "Connors"))
        V.append((f"IBS_{'ls' if ls else 'lf'}", "MEANREV", "1d", S_ibs, (ls,), "Pagonidis"))
        V.append((f"RSI2_10_4h_{'ls' if ls else 'lf'}", "MEANREV", "4h", S_rsi2, (10, ls), "Connors, 4h adaptation"))
    V.append(("WILL_k0.5_1d_lf", "VOLBRK", "1d", S_williams, (0.5, 0), "Williams"))
    V.append(("WILL_k0.5_1d_ls", "VOLBRK", "1d", S_williams, (0.5, 1), "Williams"))
    V.append(("WILL_k0.5_4h_ls", "VOLBRK", "4h", S_williams, (0.5, 1), "Williams, 4h adaptation"))
    V.append(("BOLL20_2_1d_lf", "VOLBRK", "1d", S_boll, (0,), "Bollinger"))
    V.append(("BOLL20_2_1d_ls", "VOLBRK", "1d", S_boll, (1,), "Bollinger"))
    for d, nm in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        V.append((f"DOW_{nm}", "CALENDAR", "1d", S_dow, (d,), "Caporale-Plastun"))
    V.append(("TOM_last_to_d3", "CALENDAR", "1d", S_tom, (), "Lakonishok-Smidt"))
    for h0, h1 in ((0, 8), (8, 16), (16, 24)):
        V.append((f"SESS_{h0:02d}_{h1:02d}", "CALENDAR", "1h", S_session, (h0, h1), "exploratory"))
    V.append(("CARRY_always", "CARRY", "1d", S_carry, (0,), "SST2023, basis not modelled"))
    V.append(("CARRY_switch", "CARRY", "1d", S_carry, (1,), "SST2023, basis not modelled"))
    V.append(("FUND_contrarian", "FUNDING", "1d", S_fund_dir, (1,), "exploratory"))
    V.append(("FUND_momentum", "FUNDING", "1d", S_fund_dir, (-1,), "exploratory"))
    V.append(("VT_cap1", "VOLTARGET", "1d", S_vt, (1.0,), "Moreira-Muir"))
    V.append(("VT_cap2", "VOLTARGET", "1d", S_vt, (2.0,), "Moreira-Muir"))
    return V


# ---------------------------------------------------------------- engine
def net_series(b, pos, kind, off, fee=FEE):
    """per-bar net simple return; pos already aligned to the bar in which it is held (off applies to intra)."""
    prev = np.r_[0.0, pos[:-1]]
    if kind == "carry":
        return pos * b.fund - 4 * fee * np.abs(pos - prev)
    if kind == "intra":
        entry = b.o * (1 + off)
        gross = pos * (b.c / np.where(entry > 0, entry, 1) - 1)
        return gross - 2 * fee * np.abs(pos) - pos * b.fund
    gross = pos * (b.c / b.o - 1)
    return gross - fee * np.abs(pos - prev) - pos * b.fund


def held_from(s, kind):
    if kind in ("sig", "sig_carry"):
        return np.r_[0.0, s["pos"][:-1]]
    return s["pos"]


def trades_of(pos):
    p = np.sign(pos)
    prev = np.r_[0.0, p[:-1]]
    return int(((p != 0) & (p != prev)).sum())


def stats(r, bpy):
    r = r[np.isfinite(r)]
    if len(r) < 10:
        return dict(n=len(r), mean_bps=np.nan, ann=np.nan, sharpe=np.nan, mdd=np.nan)
    eq = np.cumprod(1 + r)
    mdd = float((eq / np.maximum.accumulate(eq) - 1).min())
    sd = r.std()
    return dict(n=len(r), mean_bps=float(r.mean() * 1e4), ann=float(r.mean() * bpy * 100),
                sharpe=float(r.mean() / sd * np.sqrt(bpy)) if sd > 0 else np.nan, mdd=mdd)


def window_mask(b, w):
    lo, hi = WIN[w]
    assert hi <= SEALED_FROM, "sealed holdout"
    return (b.t >= lo) & (b.t < hi)


def placebo_p(b, held, kind, off, mask, actual, rng, always_on=False):
    n = b.n
    if always_on:  # stationary-ish block bootstrap on the windowed series
        r = net_series(b, held, kind, off)[mask]
        blk = 10
        nb = int(np.ceil(len(r) / blk))
        cnt = 0
        for _ in range(K):
            st = rng.integers(0, len(r) - blk, nb)
            samp = np.concatenate([r[s:s + blk] for s in st])[:len(r)]
            if samp.mean() <= 0:
                cnt += 1
        return (cnt + 1) / (K + 1)
    minlag = int(30 * (BPY[b.tf] / 365))
    cnt = 0
    lags = rng.integers(minlag, n - minlag, K)
    for lag in lags:
        p = np.roll(held, lag)
        o = np.roll(off, lag) if off is not None else None
        m = net_series(b, p, kind, o)[mask].mean()
        if m >= actual:
            cnt += 1
    return (cnt + 1) / (K + 1)


def run_variant(v, data, fund, wname, rng):
    vid, fam, tf, fn, args, note = v
    b = data[tf]
    s = fn(b, *args)
    kind = s["kind"]
    off = s.get("off")
    held = held_from(s, kind)
    k2 = "carry" if kind in ("carry", "sig_carry") else kind
    r = net_series(b, held, k2, off)
    mask = window_mask(b, wname)
    st = stats(r[mask], BPY[tf])
    bh = stats(net_series(b, np.ones(b.n), "held", None)[mask], BPY[tf])
    gross = stats(net_series(b, held, k2, off, fee=0.0)[mask], BPY[tf]) if True else None
    actual = r[mask].mean()
    st["trades"] = trades_of(held[mask]) if k2 != "intra" else int((np.abs(held[mask]) > 0).sum())
    st["p"] = placebo_p(b, held, k2, off, mask, actual, rng, always_on=(vid == "CARRY_always"))
    st["bh_ann"] = bh["ann"]
    st["bh_sharpe"] = bh["sharpe"]
    st["gross_ann"] = gross["ann"]
    st["expo"] = float(np.mean(np.abs(held[mask])))
    return st


def bh_q(p):
    p = np.asarray(p)
    n = len(p)
    o = np.argsort(p)
    q = np.empty(n)
    prev = 1.0
    for rank in range(n, 0, -1):
        i = o[rank - 1]
        prev = min(prev, p[i] * n / rank)
        q[i] = prev
    return q


def holm(p):
    p = np.asarray(p)
    n = len(p)
    o = np.argsort(p)
    out = np.empty(n)
    run = 0.0
    for rank, i in enumerate(o):
        run = max(run, min(1.0, (n - rank) * p[i]))
        out[i] = run
    return out


def main():
    stage = sys.argv[1]
    a = load_1h()
    fund = load_funding()
    data = {tf: Bars(resample(a, tf), fund, tf) for tf in ("1h", "4h", "1d")}
    ONE_H.update(h=data['1h'].h, l=data['1h'].l, t=data['1h'].t)
    V = variants()
    if ONLY:
        V = [v for v in V if v[0] in ONLY]
    state_f = os.path.join(HERE, "state.json" if SYMBOL == "BTCUSDT" else f"state_{SYMBOL}.json")
    state = json.load(open(state_f)) if os.path.exists(state_f) else {}
    rng = np.random.default_rng(20261013)
    wname = {"dev": "DEV", "val": "VAL", "hold": "HOLD"}[stage]
    ids = [v[0] for v in V]
    if stage == "val":
        ids = state["dev_advance"]
    if stage == "hold":
        ids = state["val_advance"]
    res = {}
    for v in V:
        if v[0] in ids:
            res[v[0]] = run_variant(v, data, fund, wname, rng)
    out = []
    if stage == "dev":
        pv = np.array([res[i]["p"] for i in ids])
        q, hp = bh_q(pv), holm(pv)
        for i, qq, hh in zip(ids, q, hp):
            res[i]["q"], res[i]["holm"] = float(qq), float(hh)
        adv = [i for i in ids if res[i]["mean_bps"] > 0 and res[i]["q"] <= 0.10 and res[i]["trades"] >= 20]
        state["dev_advance"] = adv
    elif stage == "val":
        state["val_advance"] = [i for i in ids if res[i]["mean_bps"] > 0 and res[i]["p"] < 0.10]
    else:
        state["survivors"] = [i for i in ids if res[i]["mean_bps"] > 0 and res[i]["p"] < 0.10]
    state[f"res_{stage}"] = {k: {kk: (None if (isinstance(vv, float) and np.isnan(vv)) else vv) for kk, vv in v.items()} for k, v in res.items()}
    json.dump(state, open(state_f, "w"), indent=1)
    fam = {v[0]: (v[1], v[2]) for v in V}
    print(f"{wname}: net ann %, sharpe, trades, placebo p" + (", BH q, holm" if stage == "dev" else ""))
    for i in ids:
        r = res[i]
        print(f"{i:24s} {fam[i][0]:9s} {fam[i][1]} ann={r['ann']:8.1f} gross={r['gross_ann']:8.1f} sh={r['sharpe']:6.2f} mdd={r['mdd']*100:6.1f} "
              f"n={r['trades']:5d} expo={r['expo']:.2f} p={r['p']:.4f}" + (f" q={r['q']:.3f} holm={r['holm']:.3f}" if stage == "dev" else "")
              + f" | BH ann={r['bh_ann']:.1f}")
    print("advance:" if stage != "hold" else "survivors:", state["dev_advance"] if stage == "dev" else state.get("val_advance") if stage == "val" else state["survivors"])


if __name__ == "__main__":
    main()
