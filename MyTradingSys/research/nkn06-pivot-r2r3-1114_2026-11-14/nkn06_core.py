"""NKN-06 core: daily floor-pivot R2/R3 (and S2/S3) breakouts, context-conditioned. Pure functions on arrays; no cache access here.
Everything is causal: a value attached to a bar uses only bars CLOSED at or before that bar's close. Labels for UTC day D use data through the close of D-1.
Label convention: SOURCED = a named video quote (see PRE_REG.md), OURS = our choice (single value, no grid)."""
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

DAY, H1, H4, M15 = 86400000, 3600000, 14400000, 900000
SPLIT = 1704067200000  # 2024-01-01 UTC; DEV = SIGNAL bar open before it, VALIDATION = on/after it
STEP = {"15m": M15, "1h": H1, "4h": H4, "1d": DAY}
TFK = {"15m": 1, "1h": 4, "4h": 16, "1d": 96}  # number of 15m bars per bar
UP, DOWN, RANGE, UNK = 1, -1, 0, 9  # coin-day trend codes
MARKDOWN, MARKUP = 2, 5  # cycle ids (mts_phase PH_NAMES); 0 = unknown
BULL, BEAR = 1, -1  # Malkan codes; RANGE=0, UNK=9
# ---- parameters (labels in PRE_REG.md) ----
ATR_N = 14            # standard
ATR_CAP = 1.0         # OURS: at-level = signal close <= R2 + 1.0 x ATR14
MIN_PCT = 0.005       # OURS (common block)
MIN_ATR = 0.6         # OURS (common block)
ROOM_MULT = 1.5       # OURS: skip if distance to target < 1.5 R
PB_MIN = 0.50         # OURS: V2 4h %B threshold
P3_BAND = 0.005       # OURS: three daily closes within 0.5% under R3
P3_HOLD = 5           # OURS: five daily bars
PLACEBO_DIST = 0.3    # OURS: +-0.3 ATR distance match
BP = {"taker": 12.0, "maker": 6.0}


# ------------------------------------------------------------------ data helpers
def check_series(t, name=""):
    """strictly increasing timestamps; every step a multiple of 15 minutes (gaps allowed, counted)."""
    t = np.asarray(t, dtype=np.int64)
    d = np.diff(t)
    assert len(t) > 100, f"{name}: too short"
    assert (d > 0).all(), f"{name}: timestamps not strictly increasing"
    assert (d % M15 == 0).all(), f"{name}: step is not a multiple of 15m"
    assert (t % M15 == 0).all(), f"{name}: not 15m aligned"
    return dict(first=int(t[0]), last=int(t[-1]), n=int(len(t)), min_step=int(d.min()), gaps=int((d > M15).sum()), max_gap_bars=int(d.max() // M15))


def load_15m(path):
    z = np.load(path)
    key = "ts" if "ts" in z.files else ("t" if "t" in z.files else None)
    assert key is not None, f"{path}: neither ts nor t"
    assert "ts" not in z.files or "t" not in z.files or np.array_equal(z["ts"], z["t"]), "both ts and t present and different"
    out = dict(t=z[key].astype(np.int64), o=z["o"].astype(float), h=z["h"].astype(float), l=z["l"].astype(float), c=z["c"].astype(float), v=z["v"].astype(float))
    prov = check_series(out["t"], str(path))
    prov["key"] = key
    return out, prov


def resample(t, o, h, l, c, v, k):
    """group k consecutive 15m bars aligned to the UTC boundary k*15m; complete groups only. bar time = open time."""
    per = M15 * k
    g = t // per
    idx = np.flatnonzero(np.r_[True, g[1:] != g[:-1]])
    ends = np.r_[idx[1:], len(t)]
    keep = ((ends - idx) == k) & (t[idx] % per == 0)
    return dict(t=t[idx][keep], o=o[idx][keep], h=np.maximum.reduceat(h, idx)[keep], l=np.minimum.reduceat(l, idx)[keep], c=c[ends - 1][keep], v=np.add.reduceat(v, idx)[keep])


def lookup(keys, vals, q, default):
    """vals at the row whose key == q, else default. keys sorted unique."""
    keys = np.asarray(keys)
    if len(keys) == 0:
        return np.full(len(q), default)
    j = np.searchsorted(keys, q)
    jj = np.minimum(j, len(keys) - 1)
    ok = (j < len(keys)) & (keys[jj] == q)
    return np.where(ok, np.asarray(vals)[jj], default)


def rowidx(keys, q):
    keys = np.asarray(keys)
    if len(keys) == 0:
        return np.full(len(q), -1)
    j = np.searchsorted(keys, q)
    jj = np.minimum(j, len(keys) - 1)
    return np.where((j < len(keys)) & (keys[jj] == q), jj, -1)


# ------------------------------------------------------------------ indicators
def atr14_simple(h, l, c, n=ATR_N):
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    out = np.full(len(c), np.nan)
    if len(c) >= n:
        cs = np.cumsum(np.r_[0, tr])
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def pivots(h, l, c):
    """classic floor pivots from the previous day H/L/C. R3 = H + 2(P-L), S3 = L - 2(H-P)."""
    p = (h + l + c) / 3.0
    return dict(P=p, R1=2 * p - l, S1=2 * p - h, R2=p + (h - l), S2=p - (h - l), R3=h + 2 * (p - l), S3=l - 2 * (h - p))


def _ewm(x, a=1.0 / 14):
    out = np.empty(len(x))
    s = x[0]
    for i in range(len(x)):
        s = x[i] if i == 0 else a * x[i] + (1 - a) * s
        out[i] = s
    return out


def daily_trend(dh, dl, dc):
    """coin trend phase AT THE CLOSE of each daily row: UP if ADX14>=20 and +DI>-DI and SMA20 slope (5-day lag) > 0; DOWN mirror; else RANGE; first 60 rows UNK.
    ADX = Wilder smoothing (ewm alpha 1/14, adjust=False) of DX, same as the 11-14 studies."""
    n = len(dc)
    if n < 62:
        return np.full(n, UNK, dtype=np.int8)
    pc = np.r_[np.nan, dc[:-1]]
    with np.errstate(all="ignore"):
        tr = np.maximum(dh - dl, np.maximum(abs(dh - pc), abs(dl - pc)))
        tr[0] = dh[0] - dl[0]
        up = np.r_[np.nan, dh[1:] - dh[:-1]]
        dn = np.r_[np.nan, dl[:-1] - dl[1:]]
        pdm = np.where((up > dn) & (up > 0), up, 0.0)
        mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
        atr = _ewm(tr)
        pdi, mdi = 100 * _ewm(pdm) / atr, 100 * _ewm(mdm) / atr
        dx = np.nan_to_num(100 * abs(pdi - mdi) / (pdi + mdi))
        adx = _ewm(dx)
        cs = np.cumsum(np.r_[0, dc])
        sma = np.full(n, np.nan)
        sma[19:] = (cs[20:] - cs[:-20]) / 20
        slope = np.full(n, np.nan)
        slope[5:] = sma[5:] - sma[:-5]
        ph = np.where((adx >= 20) & (pdi > mdi) & (slope > 0), UP, np.where((adx >= 20) & (mdi > pdi) & (slope < 0), DOWN, RANGE)).astype(np.int8)
    ph[:60] = UNK
    return ph


def bb_percent_b(c, n=20, mult=2.0):
    """Bollinger %B at each bar, SMA(n) and `mult` POPULATION standard deviations of the n closes ending at that bar (bar included, so it must be CLOSED). NaN while warming or zero width."""
    c = np.asarray(c, dtype=float)
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    w = np.lib.stride_tricks.sliding_window_view(c, n)
    m, sd = w.mean(axis=1), w.std(axis=1)
    up, lo = m + mult * sd, m - mult * sd
    with np.errstate(all="ignore"):
        pb = (c[n - 1:] - lo) / (up - lo)
    pb[~np.isfinite(pb)] = np.nan
    out[n - 1:] = pb
    return out


def malkan_codes(dc):
    """daily Malkan regime at the close of each daily row: RSI14 (rsi_core) then malkan_regime(40, 60, 20). 40/60/20 SOURCED to the Malkan layer, daily OURS."""
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_regime
    n = len(dc)
    out = np.full(n, UNK, dtype=np.int8)
    if n <= 14:
        return out
    reg = malkan_regime(rsi_core([float(x) for x in dc], 14), 40.0, 60.0, 20)
    m = {"BULL": BULL, "BEAR": BEAR, "RANGE": RANGE}
    for i, r in enumerate(reg):
        if r is not None:
            out[i] = m[r]
    return out


# ------------------------------------------------------------------ cycle state (MTS_BRAINS_SPEC_1114 s1, copied from nkp2 mts_phase.py; thresholds not retuned)
def _roll(x, n, f):
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        w = np.lib.stride_tricks.sliding_window_view(x, n)
        out[n - 1:] = f(w, axis=1)
    return out


def _wilder_rsi(c, n=14):
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


def cycle_labels_from_daily(d, h, l, c):
    """(applicable day numbers, label ids) : the label for UTC day D uses daily closes through D-1 only (lag 1). ids: 1 CAPITULATION 2 MARKDOWN 3 RELIEF 4 ACCUM-RANGE 5 MARKUP 6 DISTRIBUTION 0 warm-up."""
    d, h, l, c = (np.asarray(x) for x in (d, h, l, c))
    n = len(c)
    sma = lambda k: _roll(c, k, np.mean)
    s20, s50, s200, w200 = sma(20), sma(50), sma(200), sma(1400)
    s50_10 = np.full(n, np.nan)
    s50_10[10:] = s50[:-10]
    with np.errstate(all="ignore"):
        S50 = s50 / s50_10 - 1
        R10 = np.full(n, np.nan)
        R10[10:] = c[10:] / c[:-10] - 1
        RB30 = c / _roll(c, 30, np.min) - 1
        DD = c / np.maximum.accumulate(c) - 1
        rsi = _wilder_rsi(c, 14)
        RNG40 = (_roll(h, 40, np.max) - _roll(l, 40, np.min)) / c
        pm60 = np.full(n, np.nan)
        pm60[60:] = _roll(c, 60, np.min)[59:-1]
        newlow = (c < pm60).astype(float)
        nl15 = _roll(newlow, 15, np.max)
        bear = (DD <= -0.20) & (c < s200)
        bull = (c > w200) & (DD > -0.20)
        cap_raw = (~bull) & (R10 <= -0.20) & (rsi <= 30)
        cap = cap_raw.copy()
        cap[1:] |= cap_raw[:-1]
        cap[2:] |= cap_raw[:-2]
        t2 = (c < s50) & (S50 <= -0.01) & (bear | (c < s200))
        t3 = (~bull) & (c > s20) & (RB30 >= 0.12) & (c <= 1.05 * s200)
        t4 = (~bull) & (RNG40 <= 0.30) & (np.abs(c / s50 - 1) <= 0.07) & (nl15 == 0)
        t5 = (c > s50) & (S50 >= 0.01) & ((c > s200) | bull)
    lab = np.full(n, 6, dtype=np.int8)
    for k, t in ((5, t5), (4, t4), (3, t3), (2, t2), (1, cap)):
        lab[t] = k
    warm = np.isnan(w200) | np.isnan(s200) | np.isnan(S50) | np.isnan(RNG40) | np.isnan(nl15)
    lab[warm] = 0
    return d + 1, lab


# ------------------------------------------------------------------ weekly (descriptive stacked-overhead column only)
def weekly_hlc(dn, dh, dl, dc):
    """complete Mon-Sun UTC weeks (7 consecutive daily rows): dict week id -> (H, L, C). week id = (day+3)//7."""
    wk = (dn + 3) // 7
    out = {}
    for w in np.unique(wk):
        m = wk == w
        if m.sum() == 7:
            out[int(w)] = (dh[m].max(), dl[m].min(), dc[m][-1])
    return out


# ------------------------------------------------------------------ per-coin build
def build_coin(t, o, h, l, c, v, cyc_days, cyc_lab, btc_days=None, btc_ok=None):
    """tf bars + daily series + coin-day labels. cyc_days/cyc_lab: BTC cycle label for day D (already lag 1). btc_days/btc_ok: BTC filter for day D (already lag 1), else 0."""
    B = {k: resample(t, o, h, l, c, v, kk) for k, kk in TFK.items()}
    Bd = B["1d"]
    dn = Bd["t"] // DAY
    CB = dict(B=B, dn=dn, cyc_days=np.asarray(cyc_days), cyc_lab=np.asarray(cyc_lab), btc_days=btc_days, btc_ok=btc_ok)
    CB["trend_close"] = daily_trend(Bd["h"], Bd["l"], Bd["c"]) if len(dn) else np.zeros(0, np.int8)
    CB["malk_close"] = malkan_codes(Bd["c"]) if len(dn) else np.zeros(0, np.int8)
    CB["atr_d"] = atr14_simple(Bd["h"], Bd["l"], Bd["c"]) if len(dn) else np.zeros(0)
    CB["pb4"] = bb_percent_b(B["4h"]["c"])
    CB["week"] = weekly_hlc(dn, Bd["h"], Bd["l"], Bd["c"])
    return CB


def day_cummax_min(day, h, l):
    hi, lo = np.empty(len(h)), np.empty(len(l))
    st = np.flatnonzero(np.r_[True, day[1:] != day[:-1]])
    en = np.r_[st[1:], len(day)]
    for a, b in zip(st, en):
        hi[a:b] = np.maximum.accumulate(h[a:b])
        lo[a:b] = np.minimum.accumulate(l[a:b])
    return hi, lo


def tf_ctx(CB, tf):
    """per-bar context for timeframe tf (15m, 1h, 4h). Every field for bar i uses data closed at or before i's close."""
    b = CB["B"][tf]
    t, o, h, l, c = b["t"], b["o"], b["h"], b["l"], b["c"]
    n, step = len(t), STEP[tf]
    day = t // DAY
    bd = CB["B"]["1d"]
    dn = CB["dn"]
    prow = rowidx(dn, day - 1)  # previous complete UTC day
    ok = prow >= 0
    pr = np.where(ok, prow, 0)
    with np.errstate(all="ignore"):
        lv = pivots(bd["h"][pr], bd["l"][pr], bd["c"][pr]) if len(dn) else {k: np.full(n, np.nan) for k in ("R2", "R3", "S2", "S3", "R1")}
    for k in lv:
        lv[k] = np.where(ok, lv[k], np.nan)
    trend = lookup(dn + 1, CB["trend_close"], day, UNK).astype(np.int8)
    malk = lookup(dn + 1, CB["malk_close"], day, UNK).astype(np.int8)
    cycle = lookup(CB["cyc_days"], CB["cyc_lab"], day, 0).astype(np.int8)
    if CB["btc_days"] is not None:
        btcf = lookup(CB["btc_days"], CB["btc_ok"], day, 0).astype(np.int8)
    else:
        btcf = np.zeros(n, np.int8)
    # last CLOSED 4h bar at this bar's close
    t4 = CB["B"]["4h"]["t"]
    Tc = t + step
    r4 = np.searchsorted(t4 + H4, Tc, side="right") - 1
    r4c = np.maximum(r4, 0)
    fresh = (r4 >= 0) & (len(t4) > 0)
    if len(t4):
        fresh &= (Tc - (t4[r4c] + H4)) < H4
        pb = np.where(fresh, CB["pb4"][r4c], np.nan)
    else:
        pb = np.full(n, np.nan)
    # weekly (descriptive): prior complete week R1 and high
    wid = (day + 3) // 7 - 1
    wR1, wH = np.full(n, np.nan), np.full(n, np.nan)
    for w in np.unique(wid):
        if int(w) in CB["week"]:
            H_, L_, C_ = CB["week"][int(w)]
            m = wid == w
            wR1[m] = 2 * (H_ + L_ + C_) / 3.0 - L_
            wH[m] = H_
    hi, lo = day_cummax_min(day, h, l)
    st = np.flatnonzero(np.r_[True, day[1:] != day[:-1]])
    en = np.r_[st[1:], n]
    dayend = np.empty(n, np.int64)
    dcomp = np.empty(n, bool)
    for a, b_ in zip(st, en):
        dayend[a:b_] = b_ - 1
        dcomp[a:b_] = (b_ - a) == DAY // step
    prevok = np.r_[False, np.diff(t) == step]
    atr = atr14_simple(h, l, c)
    atrok = np.zeros(n, bool)
    if n > ATR_N:
        atrok[ATR_N:] = (t[ATR_N:] - t[:-ATR_N]) == ATR_N * step
    atr = np.where(atrok, atr, np.nan)
    return dict(tf=tf, step=step, n=n, t=t, o=o, h=h, l=l, c=c, day=day, atr=atr, prevok=prevok, first=(t % DAY) == 0, hour=((t % DAY) // H1).astype(np.int8),
                R2=lv["R2"], R3=lv["R3"], S2=lv["S2"], S3=lv["S3"], trend=trend, cycle=cycle, malk=malk, pb=pb, btcf=btcf,
                dayhi=hi, daylo=lo, dayend=dayend, dcomp=dcomp, wR1=wR1, wH=wH)


# ------------------------------------------------------------------ signals
def signals(X, d, mode):
    """signal bar indices for side d (+1 long above R2 / -1 short below S2), mode 'cross' (first FRESH close through the level per UTC day, at-level only) or
    'away' (first close of the day beyond level + 1 ATR). The bar opening at 00:00 UTC is skipped. No trigger if the day's extreme so far already reached R3/S3 (long/short).
    Phase / cycle are NOT used here (they are attributes recorded later)."""
    c, atr = X["c"], X["atr"]
    lvl, tgt = (X["R2"], X["R3"]) if d > 0 else (X["S2"], X["S3"])
    pc = np.r_[np.nan, c[:-1]]
    with np.errstate(invalid="ignore"):
        base = X["prevok"] & ~X["first"] & np.isfinite(atr) & np.isfinite(lvl) & np.isfinite(tgt)
        dist = d * (c - lvl)
        if mode == "cross":
            cr = (c > lvl) & (pc <= lvl) if d > 0 else (c < lvl) & (pc >= lvl)
        else:
            cr = dist > ATR_CAP * atr
        cand = np.flatnonzero(cr & base)
        if len(cand) == 0:
            return cand
        _, f = np.unique(X["day"][cand], return_index=True)
        pick = cand[np.sort(f)]
        if mode == "cross":
            pick = pick[(dist[pick] <= ATR_CAP * atr[pick])]
        reach = (X["dayhi"][pick] >= tgt[pick]) if d > 0 else (X["daylo"][pick] <= tgt[pick])
    return pick[~reach]


# ------------------------------------------------------------------ exits and fees
def walk(o, h, l, c, k0, k1, d, stop, tgt, close_lvl=None):
    """walk bars k0..k1 inclusive. Gap through the stop or target fills at the OPEN; stop first if stop and target are inside one bar; target fills at max/min(level, open);
    optional close-based exit: first bar CLOSING beyond close_lvl (long: below) exits at that close (after the intrabar checks of the same bar). Else time exit at c[k1].
    returns (exit price, exit index, kind)."""
    O, Hh, Ll, Cc = o[k0:k1 + 1], h[k0:k1 + 1], l[k0:k1 + 1], c[k0:k1 + 1]
    big = 10 ** 9
    if d > 0:
        se, te = Ll <= stop, Hh >= tgt
        ce = (Cc < close_lvl) if close_lvl is not None else np.zeros(len(Cc), bool)
    else:
        se, te = Hh >= stop, Ll <= tgt
        ce = (Cc > close_lvl) if close_lvl is not None else np.zeros(len(Cc), bool)
    se = se | ((O <= stop) if d > 0 else (O >= stop))
    te = te | ((O >= tgt) if d > 0 else (O <= tgt))
    fs = int(np.argmax(se)) if se.any() else big
    ft = int(np.argmax(te)) if te.any() else big
    fc = int(np.argmax(ce)) if ce.any() else big
    k = min(fs, ft, fc)
    if k == big:
        return c[k1], k1, "time"
    if fs == k:  # stop first on ties
        gap = (O[k] <= stop) if d > 0 else (O[k] >= stop)
        px = O[k] if gap else stop
        return px, k0 + k, "gapstop" if gap else "stop"
    if ft == k:
        gap = (O[k] >= tgt) if d > 0 else (O[k] <= tgt)
        px = O[k] if gap else tgt
        return px, k0 + k, "gaptarget" if gap else "target"
    return Cc[k], k0 + k, "closeexit"


def fee_r(e, x, R, bp):
    """round-trip fee in R: bp/2 basis points of ENTRY notional plus bp/2 of EXIT notional (both legs), divided by the stop distance R (price units).
    fee = (bp/2e4) * (e + x) / R. 12 bp taker = 6 bp per leg."""
    return (bp / 2e4) * (np.asarray(e) + np.asarray(x)) / np.asarray(R)


def sim_bar_trade(X, i, d, skip_room=True, exit_mode="normal"):
    """signal at bar i close; entry at the next bar open (same UTC day only). R = max(0.5% of entry, 0.6 x ATR14 at the signal bar, d*(entry - level)); stop = entry - d*R;
    target = R3 (long) / S3 (short); skip if the room to target < 1.5 R (skip_room); time exit at the close of the last bar of the trigger UTC day."""
    lvl, tgt = (X["R2"][i], X["R3"][i]) if d > 0 else (X["S2"][i], X["S3"][i])
    k0 = i + 1
    if k0 >= X["n"] or not X["dcomp"][i] or k0 > X["dayend"][i] or X["t"][k0] != X["t"][i] + X["step"]:
        return dict(status="no_entry")
    e = X["o"][k0]
    R = max(MIN_PCT * e, MIN_ATR * X["atr"][i], d * (e - lvl))
    stop = e - d * R
    if skip_room and d * (tgt - e) < ROOM_MULT * R:
        return dict(status="room")
    x, xi, kind = walk(X["o"], X["h"], X["l"], X["c"], k0, int(X["dayend"][i]), d, stop, tgt, lvl if exit_mode == "close" else None)
    return dict(status="ok", e=float(e), x=float(x), R=float(R), g=float(d * (x - e) / R), kind=kind, xi=int(xi), hit=kind in ("target", "gaptarget"))


def sim_signals(X, d, mode, skip_room=True, exit_mode="normal"):
    """simulate every signal of (side, mode) irrespective of phase; phase / layer attributes are stored for cell assignment."""
    idx = signals(X, d, mode)
    lvl = X["R2"] if d > 0 else X["S2"]
    rows = []
    for i in idx:
        r = sim_bar_trade(X, int(i), d, skip_room, exit_mode)
        r.update(i=int(i), t=int(X["t"][i]), trend=int(X["trend"][i]), cycle=int(X["cycle"][i]), malk=int(X["malk"][i]), pb=float(X["pb"][i]), btcf=int(X["btcf"][i]),
                 hour=int(X["hour"][i]), dist=float(d * (X["c"][i] - lvl[i]) / X["atr"][i]))
        if r["status"] == "ok":
            tgt = X["R3"][i] if d > 0 else X["S3"][i]
            ws = [w for w in (X["wR1"][i], X["wH"][i]) if np.isfinite(w)]
            r["stacked"] = bool(d > 0 and any(r["e"] < w < tgt for w in ws))  # descriptive: weekly R1 or prior-week high between entry and R3
        rows.append(r)
    return rows


# ------------------------------------------------------------------ daily row P3
def p3_rows(CB, skip_room=True):
    """P3: three consecutive daily closes each within 0.5% UNDER the R3 in force on day 3 (R3 frozen at day 3) and none above; entry next day open; target R3; stop R = max(0.5%, 0.6 x ATR14d);
    time exit at the close of the 5th daily bar after the signal day; skip if room < 1.5 R; one open position per coin. The trend/cycle labels are those of the ENTRY day (known at the signal close)."""
    Bd = CB["B"]["1d"]
    dn, o, h, l, c = CB["dn"], Bd["o"], Bd["h"], Bd["l"], Bd["c"]
    n = len(dn)
    rows, busy = [], -1
    for j in range(2, n - 1):
        if dn[j] - dn[j - 2] != 2 or dn[j - 1] != dn[j] - 1 or np.isnan(CB["atr_d"][j]):
            continue
        pr = j - 1
        R3 = h[pr] + 2 * ((h[pr] + l[pr] + c[pr]) / 3.0 - l[pr])
        cl = c[j - 2:j + 1]
        if not ((cl <= R3).all() and (cl >= R3 * (1 - P3_BAND)).all()):
            continue
        t_sig = int(Bd["t"][j])
        base = dict(i=j, t=t_sig, trend=int(CB["trend_close"][j]), cycle=int(lookup(CB["cyc_days"], CB["cyc_lab"], np.array([dn[j] + 1]), 0)[0]), malk=int(CB["malk_close"][j]), pb=np.nan, btcf=0, hour=0, dist=0.0)
        k0, k1 = j + 1, j + P3_HOLD
        if j <= busy:
            rows.append(dict(base, status="busy"))
            continue
        if k1 >= n or dn[k0] != dn[j] + 1 or dn[k1] - dn[k0] != P3_HOLD - 1:
            rows.append(dict(base, status="no_entry"))
            continue
        e = o[k0]
        R = max(MIN_PCT * e, MIN_ATR * CB["atr_d"][j])
        stop = e - R
        if skip_room and (R3 - e) < ROOM_MULT * R:
            rows.append(dict(base, status="room"))
            continue
        x, xi, kind = walk(o, h, l, c, k0, k1, 1, stop, R3)
        busy = xi
        rows.append(dict(base, status="ok", e=float(e), x=float(x), R=float(R), g=float((x - e) / R), kind=kind, xi=int(xi), hit=kind in ("target", "gaptarget"), stacked=False))
    return rows


# ------------------------------------------------------------------ cells
P1_TREND, P1_CYC = UP, MARKUP


def in_cell(trend, cycle, want_trend, want_cycle):
    """want_cycle: MARKUP, MARKDOWN, or 'not_markup' (a KNOWN label that is not MARKUP). Unknown labels never match."""
    tm = np.asarray(trend) == want_trend
    cy = np.asarray(cycle)
    if want_cycle == "not_markup":
        cm = (cy > 0) & (cy != MARKUP)
    else:
        cm = cy == want_cycle
    return tm & cm


def split_is_val(t_signal):
    """VALIDATION iff the SIGNAL bar open time is on/after 2024-01-01 UTC. Entry and exit times never decide the split."""
    return np.asarray(t_signal) >= SPLIT


# ------------------------------------------------------------------ statistics
def boot_trade_ci_low(R, nb=4000, seed=11):
    R = np.asarray(R, float)
    n = len(R)
    if n < 2:
        return float("nan")
    rng = np.random.default_rng(seed)
    out, chunk, done = [], max(1, int(3e6 // n)), 0
    while done < nb:
        b = min(chunk, nb - done)
        out.append(R[rng.integers(0, n, (b, n))].mean(axis=1))
        done += b
    return float(np.percentile(np.concatenate(out), 2.5))


def boot_day_means(R, day, nb=4000, seed=12):
    R = np.asarray(R, float)
    u, inv = np.unique(day, return_inverse=True)
    sR = np.bincount(inv, weights=R)
    nn = np.bincount(inv).astype(float)
    D = len(u)
    rng = np.random.default_rng(seed)
    out, chunk, done = [], max(1, int(3e6 // D)), 0
    while done < nb:
        b = min(chunk, nb - done)
        ix = rng.integers(0, D, (b, D))
        out.append(sR[ix].sum(axis=1) / nn[ix].sum(axis=1))
        done += b
    return np.concatenate(out)


def ex_best5_days(R, day):
    """mean R after removing the 5 days with the largest summed R."""
    R = np.asarray(R, float)
    u, inv = np.unique(day, return_inverse=True)
    sR = np.bincount(inv, weights=R)
    worst = np.argsort(-sR)[:5]
    m = ~np.isin(inv, worst)
    return float(R[m].mean()) if m.any() else float("nan")


def bh_q(p):
    """Benjamini-Hochberg adjusted q-values."""
    p = np.asarray(p, float)
    m = len(p)
    o = np.argsort(p)
    q = np.empty(m)
    prev = 1.0
    for rank in range(m, 0, -1):
        k = o[rank - 1]
        prev = min(prev, p[k] * m / rank)
        q[k] = prev
    return q


def cell_stats(g, e, x, R, t, split="VAL", full=True):
    """stats for the trades of one cell restricted to a split (by signal bar). arrays: gross R, entry, exit, R, signal bar time."""
    g, e, x, R, t = (np.asarray(a) for a in (g, e, x, R, t))
    m = split_is_val(t) if split == "VAL" else ~split_is_val(t)
    g, e, x, R, t = g[m], e[m], x[m], R[m], t[m]
    n = len(g)
    out = dict(n=int(n))
    if n == 0:
        return dict(out, gross=float("nan"), net12=float("nan"), net6=float("nan"), win=float("nan"), trade_ci_low=float("nan"), day_ci_low=float("nan"), ex5=float("nan"), p_day=1.0)
    n12 = g - fee_r(e, x, R, 12.0)
    n6 = g - fee_r(e, x, R, 6.0)
    out.update(gross=float(g.mean()), net12=float(n12.mean()), net6=float(n6.mean()), win=float((n12 > 0).mean()), days=int(len(np.unique(t // DAY))))
    if full and n >= 2:
        day = t // DAY
        bm = boot_day_means(n12, day)
        out.update(trade_ci_low=boot_trade_ci_low(n12), day_ci_low=float(np.percentile(bm, 2.5)), ex5=ex_best5_days(n12, day), p_day=float((1 + (bm <= 0).sum()) / (len(bm) + 1)))
    else:
        out.update(trade_ci_low=float("nan"), day_ci_low=float("nan"), ex5=float("nan"), p_day=1.0)
    return out


# ------------------------------------------------------------------ placebo (like for like)
def placebo_candidates(X, d, want_trend, want_cycle, hour, dist, rng, kmax=40, exit_mode="normal"):
    """net-R at 12 bp of up to kmax random entries in the SAME coin, same trend x cycle cell (labels of the bar's day), same side, same timeframe, VALIDATION signal bars, same UTC hour,
    distance to the level within +-0.3 ATR of the real trade; same stop / target / exit / skip logic; not the first bar of the day, entry bar in the same day."""
    lvl = X["R2"] if d > 0 else X["S2"]
    with np.errstate(invalid="ignore"):
        dd = d * (X["c"] - lvl) / X["atr"]
        m = (in_cell(X["trend"], X["cycle"], want_trend, want_cycle) & split_is_val(X["t"]) & (X["hour"] == hour) & ~X["first"] & X["prevok"]
             & np.isfinite(dd) & (np.abs(dd - dist) <= PLACEBO_DIST) & np.isfinite(X["R3" if d > 0 else "S3"]))
    idx = np.flatnonzero(m)
    if len(idx) > kmax:
        idx = rng.choice(idx, kmax, replace=False)
    vals = []
    for i in idx:
        r = sim_bar_trade(X, int(i), d, True, exit_mode)
        if r["status"] == "ok":
            vals.append(r["g"] - float(fee_r(r["e"], r["x"], r["R"], 12.0)))
    return vals


def placebo_test(real_net, cand_lists, nd=1000, seed=21):
    """real_net: net R of the real trades (same order as cand_lists). Trades with no candidate are dropped from BOTH sides (matched subset).
    returns dict(matched, real_mean_matched, placebo_mean, p) with p = (1 + #draws with placebo mean >= real mean) / (nd + 1)."""
    keep = [j for j, c in enumerate(cand_lists) if len(c) > 0]
    if not keep:
        return dict(matched=0, real_mean_matched=float("nan"), placebo_mean=float("nan"), p=1.0)
    mx = max(len(cand_lists[j]) for j in keep)
    M = np.zeros((len(keep), mx))
    L = np.zeros(len(keep), int)
    for r, j in enumerate(keep):
        L[r] = len(cand_lists[j])
        M[r, :L[r]] = cand_lists[j]
    rng = np.random.default_rng(seed)
    ix = np.minimum((rng.random((nd, len(keep))) * L).astype(int), L - 1)
    means = M[np.arange(len(keep)), ix].mean(axis=1)
    real = float(np.asarray(real_net)[keep].mean())
    return dict(matched=int(len(keep)), real_mean_matched=real, placebo_mean=float(means.mean()), p=float((1 + (means >= real).sum()) / (nd + 1)))


def cell_verdict(st, placebo_p, q, n_pass=200, n_min=100):
    """PASS needs all gates; n VAL < 100 UNDERPOWERED; 100 <= n < 200: gates are reported and a failing cell is FAIL, a cell that would pass is UNDERPOWERED (cannot PASS)."""
    n = st["n"]
    if n < n_min:
        return "UNDERPOWERED"
    gates = [st["net12"] > 0, st["trade_ci_low"] > 0, st["day_ci_low"] > 0, st["ex5"] > 0, placebo_p < 0.05, q <= 0.10]
    if not all(gates):
        return "FAIL"
    return "PASS" if n >= n_pass else "UNDERPOWERED"


def overall_verdict(verdicts):
    if "PASS" in verdicts:
        return "PASS"
    if "FAIL" in verdicts:
        return "FAIL"
    return "UNDERPOWERED"
