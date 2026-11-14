"""NKN-04 study: higher-timeframe daily SMA20 level, 15m SMA20 counter-cross, context-conditioned.
Frozen design: PRE_REG.md in this folder (copy of nkn_design/NKN-04.md). Every parameter below is labelled SOURCED or OURS there.
Causal by construction: every value at 15m bar i uses data CLOSED at or before bar i (daily/weekly/4h values use completed bars only).
Usage: python study.py counts   (DEV-only event counts, no outcome is computed)
       python study.py run      (DEV + VALIDATION, writes results.json and RESULT.md)
numpy only. Helper functions (resample, wilder_rsi, bollinger_pb, ema) are re-written from research/nkp2-levels-phase-1114 ctxlib.py."""
import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CACHE = Path(r"F:\MTS\data_cache")
VENUE = CACHE / "binance"
PHASE_CSV = CACHE / "mts_brains" / "phase_daily.csv"
M15, H1, H4, DAY = 900000, 3600000, 4 * 3600000, 86400000
SPLIT = 1704067200000  # 2024-01-01 UTC; split by SIGNAL bar open time
COINS = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
# ---- parameters (labels in PRE_REG.md) ----
APPROACH_BARS, WIN_BARS = 8, 8          # OURS: 2h approach side lookback, at-level window
BAND_AT, BAND_CLOSE = 0.5, 0.25         # OURS: x ATRd
STOP_PCT, STOP_ATR, TGT_R = 0.012, 1.0, 2.0   # OURS (stop floor 1.2% / 1.0 x ATR14 15m, half at 2R)
CAP_BARS = 96                           # OURS: time cap for a trade (24 h)
PB_SHORT, PB_LONG, RSI4_SHORT, RSI4_LONG = 0.90, 0.10, 55.0, 45.0   # OURS cutoffs; Bollinger period 20 sourced to SPEC C3
ADX_MIN, SLOPE_LAG = 20.0, 5            # common block of NK55_RULES_1114.md
RT_BP = {12: 12.0, 6: 6.0}              # round trip taker / maker; half on entry notional, half on exit notional
UP, DOWN, RANGE = 1, 2, 3
LAB_OTHER, LAB_MARKUP, LAB_MARKDOWN, LAB_NONE = 0, 1, 2, -1
B_TRADE, B_DAY, B_PLACEBO, SEED = 5000, 5000, 1000, 20261114
MIN_VAL, THIN_VAL = 100, 200


# ------------------------------------------------------------------ data
def load_coin(sym, path=None):
    """15m bars from the shared cache (key `a` = [t,o,h,l,c,v], or `t`/`ts` keys). Asserts key, strict increase, multiple-of-15m steps.
    Gaps (exchange outages) are filled flat with `filled=True` so every bar index is a 15m slot."""
    p = Path(path) if path else VENUE / f"{sym}USDT_15m.npz"
    z = np.load(p)
    if "a" in z.files:
        a = z["a"]
        t, o, h, l, c, v = (a[:, k] for k in range(6))
        key = "a[:,0]"
    else:
        key = "ts" if "ts" in z.files else "t"
        assert key in z.files, f"{p}: no time key in {z.files}"
        t, o, h, l, c, v = z[key], z["o"], z["h"], z["l"], z["c"], z["v"]
    t = t.astype(np.int64)
    return fill_grid(t, o.astype(float), h.astype(float), l.astype(float), c.astype(float), v.astype(float), str(p), key)


def fill_grid(t, o, h, l, c, v, src="memory", key="t"):
    d = np.diff(t)
    assert (d > 0).all(), f"{src}: timestamps not strictly increasing"
    assert (d % M15 == 0).all(), f"{src}: step is not a multiple of 15m"
    assert t[0] % M15 == 0, f"{src}: first timestamp off the 15m grid"
    n = int((t[-1] - t[0]) // M15) + 1
    pos = ((t - t[0]) // M15).astype(np.int64)
    filled = np.ones(n, bool)
    filled[pos] = False
    tt = t[0] + M15 * np.arange(n, dtype=np.int64)
    out = {}
    for name, x in (("o", o), ("h", h), ("l", l), ("c", c), ("v", v)):
        y = np.full(n, np.nan)
        y[pos] = x
        out[name] = y
    last = np.maximum.accumulate(np.where(~filled, np.arange(n), -1))
    for name in ("c",):
        out[name] = out[name][last]
    for name in ("o", "h", "l"):
        out[name] = np.where(filled, out["c"], out[name])
    out["v"] = np.where(filled, 0.0, out["v"])
    out.update(t=tt, filled=filled, prov=dict(src=src, key=key, first=int(t[0]), last=int(t[-1]), rows=int(len(t)), gaps=int(((d // M15) > 1).sum()), filled_bars=int(filled.sum())))
    return out


def ts_str(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


# ------------------------------------------------------------------ indicators
def resample(t, o, h, l, c, k):
    """group k consecutive 15m bars on the UTC boundary of k*15m; complete groups only (start, o, h, l, c)."""
    per = M15 * k
    g = t // per
    idx = np.flatnonzero(np.r_[True, g[1:] != g[:-1]])
    ends = np.r_[idx[1:], len(t)]
    keep = ((ends - idx) == k) & (t[idx] % per == 0)
    return t[idx][keep], o[idx][keep], np.maximum.reduceat(h, idx)[keep], np.minimum.reduceat(l, idx)[keep], c[ends - 1][keep]


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


def wma(x, n):
    """linear weighted MA, newest weight n; NaN until n valid values."""
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    w = np.arange(n, 0, -1, dtype=float)
    win = np.lib.stride_tricks.sliding_window_view(x, n)[:, ::-1]
    out[n - 1:] = (win * w).sum(axis=1) / w.sum()
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


def bollinger_pb(c, n=20):
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    w = np.lib.stride_tricks.sliding_window_view(c, n)
    m, sd = w.mean(axis=1), w.std(axis=1)
    with np.errstate(all="ignore"):
        out[n - 1:] = (c[n - 1:] - (m - 2 * sd)) / (4 * sd)
    return out


def sma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        cs = np.cumsum(np.r_[0.0, x])
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def wilder_atr(h, l, c, n=14):
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def adx_di(h, l, c, n=14):
    """Wilder DI+/DI-/ADX, same algorithm as backtest/layers/adx/adx.py (FORMULAS s30); NaN where undefined."""
    m = len(c)
    dip, dim, adx = (np.full(m, np.nan) for _ in range(3))
    if m < n + 1:
        return dip, dim, adx
    tr = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    up, dn = h[1:] - h[:-1], l[:-1] - l[1:]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    s_tr, s_p, s_m = tr[:n].sum(), pdm[:n].sum(), mdm[:n].sum()
    dx = []
    for k in range(n - 1, m - 1):
        if k >= n:
            s_tr = s_tr - s_tr / n + tr[k]
            s_p = s_p - s_p / n + pdm[k]
            s_m = s_m - s_m / n + mdm[k]
        i = k + 1
        if s_tr <= 0:
            dip[i], dim[i] = 0.0, 0.0
        else:
            dip[i], dim[i] = 100.0 * s_p / s_tr, 100.0 * s_m / s_tr
        tot = dip[i] + dim[i]
        dx.append(100.0 * abs(dip[i] - dim[i]) / tot if tot > 0 else 0.0)
        if len(dx) == n:
            adx[i] = sum(dx) / n
        elif len(dx) > n:
            adx[i] = (adx[i - 1] * (n - 1) + dx[-1]) / n
    return dip, dim, adx


def coin_day_phase(hd, ld, cd):
    """phase at the CLOSE of each daily bar: UP / DOWN / RANGE (0 = not enough history).
    UP: SMA20 now > SMA20 5 days ago, ADX14 >= 20, DI+ > DI-.  DOWN: mirror.  Else RANGE."""
    s20 = sma(cd, 20)
    prev = np.full(len(cd), np.nan)
    prev[SLOPE_LAG:] = s20[:-SLOPE_LAG]
    dip, dim, adx = adx_di(hd, ld, cd, 14)
    with np.errstate(invalid="ignore"):
        up = (s20 > prev) & (adx >= ADX_MIN) & (dip > dim)
        dn = (s20 < prev) & (adx >= ADX_MIN) & (dim > dip)
    ph = np.where(up, UP, np.where(dn, DOWN, RANGE)).astype(np.int8)
    ph[np.isnan(s20) | np.isnan(prev) | np.isnan(adx)] = 0
    return ph


# ------------------------------------------------------------------ BTC cycle label (phase_daily.csv, lag 1 already applied by its builder)
def load_labels(path=PHASE_CSV):
    """(day_numbers, code, close_used, sha256). code: MARKUP 1, MARKDOWN 2, other label 0; blank label and provisional rows are dropped (excluded, not defaulted)."""
    raw = Path(path).read_bytes()
    days, codes, cu = [], [], []
    for r in csv.DictReader(raw.decode().splitlines()):
        if str(r.get("provisional", "False")).lower() == "true" or r["label"] == "":
            continue
        days.append(dt.date.fromisoformat(r["date"]).toordinal() - 719163)
        codes.append(LAB_MARKUP if r["label"] == "MARKUP" else LAB_MARKDOWN if r["label"] == "MARKDOWN" else LAB_OTHER)
        cu.append(float(r["close_used"]) if r["close_used"] else np.nan)
    return np.array(days), np.array(codes, dtype=np.int8), np.array(cu), hashlib.sha256(raw).hexdigest()


def check_label_lag(ld, btc):
    """label row for day D must have close_used == BTC close of day D-1 (lag 1, no look-ahead). Returns (checked, matched)."""
    td, _, _, _, cd = resample(btc["t"], btc["o"], btc["h"], btc["l"], btc["c"], 96)
    dn = td // DAY
    days, _, cu, _ = ld
    ok = chk = 0
    for d, x in zip(days, cu):
        j = np.searchsorted(dn, d - 1)
        if j < len(dn) and dn[j] == d - 1 and not np.isnan(x):
            chk += 1
            ok += abs(cd[j] - x) <= 1e-6 * abs(x) + 1e-9
    return chk, int(ok)


def label_for_days(days_needed, ld):
    days, codes = ld[0], ld[1]
    j = np.searchsorted(days, days_needed)
    jj = np.minimum(j, len(days) - 1)
    ok = (j < len(days)) & (days[jj] == days_needed)
    return np.where(ok, codes[jj], LAB_NONE).astype(np.int8)


# ------------------------------------------------------------------ per-bar state (all closed-bar, causal)
def _prior_day_lookup(dn, day):
    """position in the daily arrays of day-1 for each bar day, -1 if absent. Value for UTC day d is the state at the close of d-1."""
    pos = np.searchsorted(dn, day - 1)
    posc = np.minimum(pos, len(dn) - 1)
    ok = (pos < len(dn)) & (dn[posc] == day - 1)
    return np.where(ok, posc, -1)


def _take(x, pos):
    out = np.full(len(pos), np.nan)
    ok = pos >= 0
    out[ok] = x[pos[ok]]
    return out


def bar_state(a, label_data):
    """per-15m-bar arrays used by the rule; label_data = (days, codes, ...) from load_labels()."""
    t, o, h, l, c = a["t"], a["o"], a["h"], a["l"], a["c"]
    n = len(t)
    day = t // DAY
    td, _, hd, ld_, cd = resample(t, o, h, l, c, 96)
    dn = td // DAY
    if len(dn) > 1:
        assert (np.diff(dn) == 1).all(), "daily bars not contiguous"
    S = dict(n=n, t=t, o=o, h=h, l=l, c=c, filled=a["filled"], day=day)
    pos = _prior_day_lookup(dn, day) if len(dn) else np.full(n, -1)
    s20d = sma(cd, 20)
    atrd = wilder_atr(hd, ld_, cd, 14)
    phd = coin_day_phase(hd, ld_, cd)
    S["L"] = _take(s20d, pos)
    S["atrd"] = _take(atrd, pos)
    S["phase"] = np.where(pos >= 0, phd[np.maximum(pos, 0)], 0).astype(np.int8)
    S["label"] = label_for_days(day, label_data)
    # weekly SMA20 of the last 20 COMPLETED weeks (Monday-aligned UTC weeks), value for the week before the bar's week
    wk = (dn + 3) // 7
    if len(dn):
        w0, w1 = wk[0], wk[-1]
        wclose = np.full(w1 - w0 + 1, np.nan)
        for w in np.unique(wk):
            m = wk == w
            if m.sum() == 7 and (dn[m][0] + 3) % 7 == 0:
                wclose[w - w0] = cd[m][-1]
        wsma = np.full(len(wclose), np.nan)
        if len(wclose) >= 20:
            win = np.lib.stride_tricks.sliding_window_view(wclose, 20)
            wsma[19:] = win.mean(axis=1)  # NaN if any week missing
        bw = (day + 3) // 7 - 1 - w0
        S["wsma"] = np.where((bw >= 0) & (bw < len(wsma)), wsma[np.clip(bw, 0, len(wsma) - 1)], np.nan)
    else:
        S["wsma"] = np.full(n, np.nan)
    # 15m indicators
    S["sma15"] = sma(c, 20)
    rsi9 = wilder_rsi(c, 9)
    g, red = ema(rsi9, 3), wma(rsi9, 21)
    hm = np.where(red < g, 1, np.where(red > g, -1, 0)).astype(np.int8)
    hm[np.isnan(red) | np.isnan(g)] = 99  # 99 = undefined, excluded
    S["hm"] = hm
    S["atr15"] = wilder_atr(h, l, c, 14)
    # 4h layers at the last CLOSED 4h bar whose end <= the trigger bar open
    t4, _, _, _, c4 = resample(t, o, h, l, c, 16)
    i4 = np.searchsorted(t4 + H4, t, side="right") - 1
    S["pb4"] = _take(bollinger_pb(c4, 20), i4)
    S["rsi4"] = _take(wilder_rsi(c4, 14), i4)
    # window features ending at bar i
    sw = np.lib.stride_tricks.sliding_window_view
    hmax, lmin = np.full(n, np.nan), np.full(n, np.nan)
    if n >= WIN_BARS:
        hmax[WIN_BARS - 1:] = sw(h, WIN_BARS).max(axis=1)
        lmin[WIN_BARS - 1:] = sw(l, WIN_BARS).min(axis=1)
    S["hmax8"], S["lmin8"] = hmax, lmin
    cl8 = np.full(n, np.nan)
    cl8[APPROACH_BARS:] = c[:-APPROACH_BARS]
    cl1 = np.full(n, np.nan)
    cl1[1:] = c[:-1]
    cl9 = np.full(n, np.nan)
    cl9[APPROACH_BARS + 1:] = c[:-(APPROACH_BARS + 1)]
    S["mv"] = cl1 - cl9
    s15p = np.full(n, np.nan)
    s15p[1:] = S["sma15"][:-1]
    L, A = S["L"], S["atrd"]
    with np.errstate(invalid="ignore"):
        S["x_dn"] = (c < S["sma15"]) & (cl1 >= s15p)
        S["x_up"] = (c > S["sma15"]) & (cl1 <= s15p)
        S["app_s"], S["app_l"] = cl8 < L, cl8 > L
        S["at_s"] = (hmax >= L - BAND_AT * A) & (c < L + BAND_CLOSE * A)
        S["at_l"] = (lmin <= L + BAND_AT * A) & (c > L - BAND_CLOSE * A)
        S["away_s"] = hmax < L - BAND_AT * A
        S["away_l"] = lmin > L + BAND_AT * A
        S["wc"] = np.abs(S["wsma"] - L) <= BAND_AT * A
    # failed pattern: a 1h close (last 15m bar of an hour) beyond L within the last 8 bars, trigger close back on the approach side
    he = ((t + M15) % H1) == 0
    fp_s, fp_l = np.zeros(n, bool), np.zeros(n, bool)
    if n >= WIN_BARS:
        wc_, wh = sw(c, WIN_BARS), sw(he, WIN_BARS)
        with np.errstate(invalid="ignore"):
            fp_s[WIN_BARS - 1:] = ((wc_ > L[WIN_BARS - 1:, None]) & wh).any(axis=1) & (c[WIN_BARS - 1:] < L[WIN_BARS - 1:])
            fp_l[WIN_BARS - 1:] = ((wc_ < L[WIN_BARS - 1:, None]) & wh).any(axis=1) & (c[WIN_BARS - 1:] > L[WIN_BARS - 1:])
    S["fp_s"], S["fp_l"] = fp_s, fp_l
    # no filled (gap) bar from i-30 to i+1
    cf = np.r_[0, np.cumsum(a["filled"])]
    lo = np.maximum(np.arange(n) - 30, 0)
    hi = np.minimum(np.arange(n) + 2, n)
    S["clean"] = (cf[hi] - cf[lo]) == 0
    return S


# ------------------------------------------------------------------ trade simulation
def fee_r(e, xa, xb, dist, rt_bp):
    """fee in R: (rt/2) x entry notional + (rt/2) x exit notional (two halves), per unit; divided by the stop distance."""
    half = rt_bp / 2.0 * 1e-4
    return (half * e + half * (0.5 * xa + 0.5 * xb)) / dist


def stop_dist(side, e, ext, atr15):
    """R in price units = max(structural distance to the 8-bar extreme, 1.2% of entry, 1.0 x ATR14 of 15m). ext = 8-bar high (short) / low (long)."""
    struct = (ext - e) if side < 0 else (e - ext)
    return max(struct, STOP_PCT * e, STOP_ATR * atr15)


def simulate(o, h, l, c, i, side, L, e, dist, cap=CAP_BARS):
    """signal at bar i, entry at o[i+1] (= e passed in). Returns dict(xa, xb, xi, reason, tgt_hit).
    Pre-target: stop (touch, gap fills at the open, stop wins a same-bar tie). Half exits at 2R (gap fills at the open). Runner: stop = max(initial stop,
    the highest prior candle low since the target bar (short: lowest high)), gap fills at the open. Two consecutive 15m closes through L (against the trade)
    from the entry bar on exit everything left at the second close. Time cap `cap` bars: exit at the close."""
    n = len(c)
    j0 = i + 1
    end = min(n - 1, j0 + cap)
    sl = slice(j0, end + 1)
    if side > 0:
        O, H, Lo, C, LL = o[sl], h[sl], l[sl], c[sl], L
    else:  # mirror: negate prices so the long logic applies
        O, H, Lo, C, LL = -o[sl], -l[sl], -h[sl], -c[sl], -L
    ee = e * side
    stop = ee - dist
    tgt = ee + TGT_R * dist
    xa = None
    trail = -np.inf
    prev_below = False
    m = len(C)
    for k in range(m):
        if xa is None:
            if Lo[k] <= stop:
                px = min(stop, O[k])
                return dict(xa=px * side, xb=px * side, xi=j0 + k, reason="stop", tgt_hit=False)
            if H[k] >= tgt:
                xa = max(tgt, O[k])
                trail = Lo[k]  # runner floor from the NEXT bar on is the highest low since this bar
                prev_below = False
                # the target bar's own close counts for the two-close rule only for the runner from the next bar; keep it simple: reset
                continue
        else:
            fl = max(stop, trail)
            if Lo[k] <= fl:
                px = min(fl, O[k])
                return dict(xa=xa * side, xb=px * side, xi=j0 + k, reason="runner", tgt_hit=True)
            trail = max(trail, Lo[k])
        below = C[k] < LL
        if below and prev_below:
            px = C[k]
            return dict(xa=(xa if xa is not None else px) * side, xb=px * side, xi=j0 + k, reason="close_through", tgt_hit=xa is not None)
        prev_below = below
    px = C[m - 1]
    return dict(xa=(xa if xa is not None else px) * side, xb=px * side, xi=j0 + m - 1, reason="time", tgt_hit=xa is not None)


def trade_net(e, res, side, dist, rt_bp):
    gross = side * (0.5 * (res["xa"] - e) + 0.5 * (res["xb"] - e)) / dist
    return gross, gross - fee_r(e, res["xa"], res["xb"], dist, rt_bp)


# ------------------------------------------------------------------ candidates
def candidates(S, sym):
    """every trigger (both sides, any phase, any at/away) with the context flags attached. No outcome is computed here."""
    n = S["n"]
    base = (S["clean"] & (S["phase"] > 0) & ~np.isnan(S["L"]) & ~np.isnan(S["atrd"]) & ~np.isnan(S["atr15"]) & (S["hm"] != 99)
            & ~np.isnan(S["mv"]) & ~np.isnan(S["sma15"]))
    base[max(n - 2, 0):] = False  # need bar i+1 for the entry
    out = []
    for side in (-1, 1):
        if side < 0:
            trig = S["x_dn"] & (S["mv"] > 0) & S["app_s"] & (S["hm"] != 1)
            at, away, fp = S["at_s"], S["away_s"], S["fp_s"]
            v1 = S["pb4"] >= PB_SHORT
            v2 = v1 & (S["rsi4"] >= RSI4_SHORT)
        else:
            trig = S["x_up"] & (S["mv"] < 0) & S["app_l"] & (S["hm"] != -1)
            at, away, fp = S["at_l"], S["away_l"], S["fp_l"]
            v1 = S["pb4"] <= PB_LONG
            v2 = v1 & (S["rsi4"] <= RSI4_LONG)
        idx = np.flatnonzero(base & trig & (at | away))
        for i in idx:
            out.append((sym, int(i), side, int(S["t"][i]), int(S["phase"][i]), int(S["label"][i]), bool(at[i]), bool(v1[i]), bool(v2[i]), bool(fp[i]), bool(S["wc"][i])))
    return out


FIELDS = ("coin", "i", "side", "t", "phase", "label", "at", "v1", "v2", "fp", "wc")


# ------------------------------------------------------------------ cells (frozen, 22)
def _cells():
    c = []
    for k, (side, ph, lab) in enumerate(((-1, DOWN, LAB_MARKDOWN), (1, UP, LAB_MARKUP))):
        for lvl in ("at", "away"):
            for v in (0, 1, 2):
                c.append(dict(side=side, ph=ph, lab=("eq", lab), v=v, lvl=lvl, role="PRIMARY" if lvl == "at" else "CONTROL", extra=None,
                              name=f"{'short' if side < 0 else 'long'} {'DOWN' if ph == DOWN else 'UP'}x{'MARKDOWN' if lab == LAB_MARKDOWN else 'MARKUP'} V{v} {lvl}"))
    # ordering: cells 1-3 short at, 4-6 long at, 7-12 away: reorder to match the frozen table
    at_s, at_l = [x for x in c if x["lvl"] == "at" and x["side"] < 0], [x for x in c if x["lvl"] == "at" and x["side"] > 0]
    aw = [x for x in c if x["lvl"] == "away"]
    aw = [x for x in aw if x["side"] < 0] + [x for x in aw if x["side"] > 0]
    cells = at_s + at_l + aw
    cells += [dict(side=-1, ph=DOWN, lab=("ne", LAB_MARKDOWN), v=0, lvl="at", role="CONTROL C1", extra=None, name="short DOWNx!MARKDOWN V0 at"),
              dict(side=1, ph=UP, lab=("ne", LAB_MARKUP), v=0, lvl="at", role="CONTROL C2", extra=None, name="long UPx!MARKUP V0 at"),
              dict(side=-1, ph=UP, lab=("eq", LAB_MARKUP), v=0, lvl="at", role="CONTROL C3", extra=None, name="short UPxMARKUP V0 at"),
              dict(side=1, ph=DOWN, lab=("eq", LAB_MARKDOWN), v=0, lvl="at", role="CONTROL C4", extra=None, name="long DOWNxMARKDOWN V0 at"),
              dict(side=-1, ph=RANGE, lab=("any", 0), v=0, lvl="at", role="CONTROL C5", extra=None, name="short RANGEx* V0 at"),
              dict(side=1, ph=RANGE, lab=("any", 0), v=0, lvl="at", role="CONTROL C6", extra=None, name="long RANGEx* V0 at"),
              dict(side=-1, ph=DOWN, lab=("eq", LAB_MARKDOWN), v=0, lvl="at", role="CONTROL FP", extra="fp", name="cell1 + FP split"),
              dict(side=1, ph=UP, lab=("eq", LAB_MARKUP), v=0, lvl="at", role="CONTROL FP", extra="fp", name="cell4 + FP split"),
              dict(side=-1, ph=DOWN, lab=("eq", LAB_MARKDOWN), v=0, lvl="at", role="CONTROL WC", extra="wc", name="cell1 + weekly confluence"),
              dict(side=1, ph=UP, lab=("eq", LAB_MARKUP), v=0, lvl="at", role="CONTROL WC", extra="wc", name="cell4 + weekly confluence")]
    for k, x in enumerate(cells):
        x["id"] = k + 1
    return cells


CELLS = _cells()
PRIMARY = [x["id"] for x in CELLS if x["role"] == "PRIMARY"]


def cell_mask(C, cell):
    """C = dict of numpy arrays keyed by FIELDS. A trade lands in a cell only when side, coin-day phase, BTC label and level flag all match."""
    m = (C["side"] == cell["side"]) & (C["phase"] == cell["ph"])
    kind, val = cell["lab"]
    if kind == "eq":
        m &= C["label"] == val
    elif kind == "ne":
        m &= (C["label"] != val) & (C["label"] != LAB_NONE)
    m &= C["at"] if cell["lvl"] == "at" else ~C["at"]
    if cell["v"] >= 1:
        m &= C["v1"]
    if cell["v"] == 2:
        m &= C["v2"]
    if cell["extra"]:
        m &= C[cell["extra"]]
    return m


def to_cols(cands):
    C = {k: np.array([x[j] for x in cands]) for j, k in enumerate(FIELDS)} if cands else {k: np.array([]) for k in FIELDS}
    for k in ("at", "v1", "v2", "fp", "wc"):
        C[k] = C[k].astype(bool)
    return C


def split_of(t_signal):
    return np.where(np.asarray(t_signal) < SPLIT, 0, 1)  # 0 = DEV, 1 = VALIDATION, by SIGNAL bar open time


# ------------------------------------------------------------------ statistics
def boot_ci_low(x, rng, b=B_TRADE):
    n = len(x)
    if n == 0:
        return np.nan
    idx = rng.integers(0, n, (b, n))
    return float(np.percentile(x[idx].mean(axis=1), 2.5))


def day_cluster(x, days, rng, b=B_DAY):
    """(CI low 2.5%, one-sided p of mean <= 0) from resampling whole UTC signal days."""
    if len(x) == 0:
        return np.nan, 1.0
    u, inv = np.unique(days, return_inverse=True)
    s, k = np.bincount(inv, weights=x), np.bincount(inv).astype(float)
    idx = rng.integers(0, len(u), (b, len(u)))
    mean = s[idx].sum(axis=1) / k[idx].sum(axis=1)
    return float(np.percentile(mean, 2.5)), float((1 + (mean <= 0).sum()) / (b + 1))


def ex_best5(x):
    if len(x) <= 5:
        return np.nan
    return float(np.sort(x)[:-5].mean())


def bh_q(p):
    """Benjamini-Hochberg adjusted q-values."""
    p = np.asarray(p, float)
    m = len(p)
    order = np.argsort(p)
    q = np.empty(m)
    prev = 1.0
    for rank in range(m, 0, -1):
        j = order[rank - 1]
        prev = min(prev, p[j] * m / rank)
        q[j] = prev
    return q


def dedupe(coin, i, xi):
    """one open position per coin and cell: keep a candidate only if its entry bar (i+1) is after the previous kept trade's exit bar."""
    keep = np.zeros(len(i), bool)
    for c in np.unique(coin):
        last = -1
        for k in np.flatnonzero(coin == c):
            if i[k] + 1 > last:
                keep[k] = True
                last = xi[k]
    return keep


# ------------------------------------------------------------------ run
def build(coins=COINS, only_dev=False, log=print):
    """returns (cands columns, per-coin state dict for placebo) ; simulation of outcomes happens in run()."""
    ld = load_labels()
    all_c, states, prov = [], {}, []
    for sym in coins:
        a = load_coin(sym)
        if sym == "BTC":
            chk = check_label_lag(ld, a)
            log(f"label lag check (close_used == prior-day BTC close): {chk[1]}/{chk[0]} rows")
            assert chk[0] > 1000 and chk[1] >= 0.99 * chk[0], "phase_daily.csv label lag check failed"
        S = bar_state(a, ld)
        prov.append((sym, a["prov"]))
        log(f"{sym}: {ts_str(a['prov']['first'])} .. {ts_str(a['prov']['last'])} rows {a['prov']['rows']} gaps {a['prov']['gaps']} filled {a['prov']['filled_bars']}")
        cs = candidates(S, sym)
        all_c += cs
        states[sym] = S
    return to_cols(all_c), states, prov, ld[3]


def run_sims(C, states):
    """outcome of every candidate once (shared by all cells)."""
    n = len(C["i"])
    e, dist, xi = np.zeros(n), np.zeros(n), np.zeros(n, dtype=np.int64)
    g = {12: np.zeros(n), 6: np.zeros(n)}
    nt = {12: np.zeros(n), 6: np.zeros(n)}
    gross = np.zeros(n)
    reason = np.empty(n, dtype=object)
    for k in range(n):
        S = states[C["coin"][k]]
        i, side = int(C["i"][k]), int(C["side"][k])
        ee = S["o"][i + 1]
        ext = S["hmax8"][i] if side < 0 else S["lmin8"][i]
        dd = stop_dist(side, ee, ext, S["atr15"][i])
        res = simulate(S["o"], S["h"], S["l"], S["c"], i, side, S["L"][i], ee, dd)
        e[k], dist[k], xi[k], reason[k] = ee, dd, res["xi"], res["reason"]
        for bp in (12, 6):
            gr, net = trade_net(ee, res, side, dd, RT_BP[bp])
            gross[k], nt[bp][k] = gr, net
    C.update(e=e, dist=dist, xi=xi, gross=gross, net12=nt[12], net6=nt[6], reason=reason)
    return C


def cell_stats(C, cell, which, rng):
    m = cell_mask(C, cell)
    sp = split_of(C["t"])
    keep_all = np.zeros(len(m), bool)
    idx = np.flatnonzero(m)
    if len(idx):
        order = idx[np.lexsort((C["i"][idx], C["coin"][idx]))]
        kk = dedupe(C["coin"][order], C["i"][order], C["xi"][order])
        keep_all[order[kk]] = True
    out = {}
    for name, s in (("dev", 0), ("val", 1)):
        sel = np.flatnonzero(keep_all & (sp == s))
        x, x6 = C["net12"][sel], C["net6"][sel]
        days = C["t"][sel] // DAY
        d = dict(n=int(len(sel)), cand_all=int((m & (sp == s)).sum()), episodes=int(len(np.unique(days))) if len(sel) else 0)
        d["gross"] = float(C["gross"][sel].mean()) if len(sel) else np.nan
        d["net12"] = float(x.mean()) if len(sel) else np.nan
        d["net6"] = float(x6.mean()) if len(sel) else np.nan
        d["win"] = float((x > 0).mean()) if len(sel) else np.nan
        if name == "val":
            d["ci_trade_low"] = boot_ci_low(x, rng)
            d["ci_day_low"], d["p_day"] = day_cluster(x, days, rng) if len(sel) else (np.nan, 1.0)
            d["ex5"] = ex_best5(x)
        out[name] = d
    out["sel_val"] = np.flatnonzero(keep_all & (sp == 1))
    return out


def placebo(C, states, cell, rng, per_pool=60):
    """random entries in the same coin, same phase x BTC label cell, same side, same stop/exit/fee, hour-of-day matched, matched count; VALIDATION bars only.
    Returns pool dict coin -> hour -> array of net12."""
    pool = {}
    kind, val = cell["lab"]
    for sym, S in states.items():
        base = (S["clean"] & (S["phase"] == cell["ph"]) & (S["t"] >= SPLIT) & ~np.isnan(S["L"]) & ~np.isnan(S["atr15"]))
        base[max(S["n"] - 2, 0):] = False
        base &= (S["label"] == val) if kind == "eq" else True
        idx = np.flatnonzero(base)
        hours = (S["t"][idx] // H1) % 24
        pool[sym] = {}
        for hr in range(24):
            cand = idx[hours == hr]
            if len(cand) == 0:
                pool[sym][hr] = np.array([])
                continue
            pick = rng.choice(cand, size=min(per_pool, len(cand)), replace=False)
            vals = []
            for i in pick:
                side = cell["side"]
                ee = S["o"][i + 1]
                ext = S["hmax8"][i] if side < 0 else S["lmin8"][i]
                dd = stop_dist(side, ee, ext, S["atr15"][i])
                res = simulate(S["o"], S["h"], S["l"], S["c"], int(i), side, S["L"][i], ee, dd)
                vals.append(trade_net(ee, res, side, dd, RT_BP[12])[1])
            pool[sym][hr] = np.array(vals)
    return pool


def placebo_p(C, sel, pool, rng, b=B_PLACEBO):
    if len(sel) == 0:
        return np.nan, np.nan
    real = float(C["net12"][sel].mean())
    allpool = np.concatenate([v for d in pool.values() for v in d.values() if len(v)] or [np.array([0.0])])
    draws = np.empty((len(sel), b))
    for r, k in enumerate(sel):
        p = pool[C["coin"][k]][int((C["t"][k] // H1) % 24)]
        if len(p) == 0:
            p = np.concatenate([v for v in pool[C["coin"][k]].values() if len(v)] or [allpool])
        draws[r] = p[rng.integers(0, len(p), b)]
    pm = draws.mean(axis=0)
    return float((1 + (pm >= real).sum()) / (b + 1)), float(pm.mean())


def verdict_cell(d, p_place, q):
    n = d["n"]
    if n < MIN_VAL:
        return "UNDERPOWERED"
    gates = (d["net12"] > 0 and d["ci_trade_low"] > 0 and d["ci_day_low"] > 0 and (d["ex5"] > 0) and p_place < 0.05 and q <= 0.10)
    if not gates:
        return "FAIL"
    return "PASS" if n >= THIN_VAL else "THIN"


def overall(rows):
    if any(r["verdict"] == "PASS" for r in rows):
        return "PASS"
    if any(r["verdict"] == "THIN" for r in rows) or all(r["verdict"] == "UNDERPOWERED" for r in rows):
        return "UNDERPOWERED"
    return "FAIL"


def regime_mix(states):
    out = {}
    for name, lo, hi in (("DEV", 0, SPLIT), ("VAL", SPLIT, 10 ** 15)):
        cnt = np.zeros(4)
        lab = np.zeros(4)
        for S in states.values():
            m = (S["t"] % DAY == 0) & (S["t"] >= lo) & (S["t"] < hi) & (S["phase"] > 0)
            cnt += np.bincount(S["phase"][m], minlength=4)[:4]
            if len(states) and S is states.get("BTC"):
                mm = (S["t"] % DAY == 0) & (S["t"] >= lo) & (S["t"] < hi)
                lab += np.bincount(np.clip(S["label"][mm] + 1, 0, 3), minlength=4)[:4]
        tot = cnt[1:].sum()
        out[name] = dict(UP=cnt[1] / tot, DOWN=cnt[2] / tot, RANGE=cnt[3] / tot, days=int(tot),
                         btc_none=lab[0] / max(lab.sum(), 1), btc_other=lab[1] / max(lab.sum(), 1), btc_markup=lab[2] / max(lab.sum(), 1), btc_markdown=lab[3] / max(lab.sum(), 1))
    return out


def counts_only():
    C, states, prov, sha = build()
    sp = split_of(C["t"])
    print("DEV-only event counts (candidates before de-overlap, no outcome computed)")
    for cell in CELLS:
        m = cell_mask(C, cell) & (sp == 0)
        eps = len(set(zip((C["t"][m] // DAY).tolist(), C["coin"][m].tolist())))
        print(f"{cell['id']:>2} {cell['role']:<11} {cell['name']:<34} DEV candidates {int(m.sum())} coin-days {eps}")


def run():
    C, states, prov, sha = build()
    C = run_sims(C, states)
    rng = np.random.default_rng(SEED)
    stats = {}
    for cell in CELLS:
        stats[cell["id"]] = cell_stats(C, cell, "both", rng)
    prim = PRIMARY
    pools = {}
    for cid in prim:
        cell = CELLS[cid - 1]
        key = (cell["side"], cell["ph"], cell["lab"])
        if key not in pools:
            pools[key] = placebo(C, states, cell, np.random.default_rng(SEED + cid))
    pp = {}
    for cid in prim:
        cell = CELLS[cid - 1]
        pp[cid] = placebo_p(C, stats[cid]["sel_val"], pools[(cell["side"], cell["ph"], cell["lab"])], np.random.default_rng(SEED + 100 + cid))
    q = bh_q([stats[c]["val"].get("p_day", 1.0) if stats[c]["val"]["n"] else 1.0 for c in prim])
    rows = []
    for k, cid in enumerate(prim):
        v = stats[cid]["val"]
        v["placebo_p"], v["placebo_mean"] = pp[cid]
        v["bh_q"] = float(q[k])
        v["verdict"] = verdict_cell(v, pp[cid][0] if not np.isnan(pp[cid][0]) else 1.0, q[k])
        rows.append(dict(cell=cid, verdict=v["verdict"], **{a: b for a, b in v.items() if a != "verdict"}))
    ov = overall(rows)
    res = dict(overall=ov, total_cells=len(CELLS), primary_cells=len(PRIMARY), regime_mix=regime_mix(states), phase_csv_sha256=sha,
               provenance=[dict(coin=s, **{k: (ts_str(v) if k in ("first", "last") else v) for k, v in p.items()}) for s, p in prov],
               cells=[dict(id=c["id"], role=c["role"], name=c["name"], side=c["side"], variant=c["v"], level=c["lvl"], dev=stats[c["id"]]["dev"], val={k: v for k, v in stats[c["id"]]["val"].items()}) for c in CELLS],
               exit_reasons={r: int((C["reason"] == r).sum()) for r in set(C["reason"].tolist())}, candidates=int(len(C["i"])))
    (HERE / "results.json").write_text(json.dumps(res, indent=1, default=lambda o: None if (isinstance(o, float) and np.isnan(o)) else float(o) if isinstance(o, (np.floating, np.integer)) else str(o)), encoding="utf-8")
    write_result(res, stats)
    print("overall", ov)
    return res


def f(x, d=3):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def write_result(res, stats):
    rm = res["regime_mix"]
    best = max((c for c in res["cells"] if c["role"] == "PRIMARY" and c["val"]["n"] > 0), key=lambda c: c["val"]["net12"], default=None)
    L = [f"**Verdict: {res['overall']}. NKN-04 (daily SMA20 level + 15m SMA20 counter-cross), 6 primary cells on VALIDATION (2024+), fee-net 12 bp, "
         f"best primary cell {best['id'] if best else 'none'} net R {f(best['val']['net12']) if best else 'n/a'} (n VAL {best['val']['n'] if best else 0}).**", ""]
    L.append(f"Regime mix: coin-days DEV UP {rm['DEV']['UP']:.1%} / DOWN {rm['DEV']['DOWN']:.1%} / RANGE {rm['DEV']['RANGE']:.1%} ({rm['DEV']['days']} coin-days); "
             f"VAL UP {rm['VAL']['UP']:.1%} / DOWN {rm['VAL']['DOWN']:.1%} / RANGE {rm['VAL']['RANGE']:.1%} ({rm['VAL']['days']}). "
             f"BTC cycle label share DEV: MARKUP {rm['DEV']['btc_markup']:.1%}, MARKDOWN {rm['DEV']['btc_markdown']:.1%}, other {rm['DEV']['btc_other']:.1%}, blank {rm['DEV']['btc_none']:.1%}; "
             f"VAL: MARKUP {rm['VAL']['btc_markup']:.1%}, MARKDOWN {rm['VAL']['btc_markdown']:.1%}, other {rm['VAL']['btc_other']:.1%}, blank {rm['VAL']['btc_none']:.1%}.")
    L += ["", "## PRIMARY cells (VALIDATION, signal bar >= 2024-01-01, 15m trigger, level = daily SMA20 at-level, HM gate on)", "",
          "| cell | phase tested | context conditions | crypto translation | layer agreement | level type | TF | side | n DEV | n VAL | gross R | net R 12bp | net R 6bp | win % | trade CI low | day-cluster CI low | ex-best-5 | placebo p | BH q | verdict |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in res["cells"]:
        if c["role"] != "PRIMARY":
            continue
        v, dv = c["val"], c["dev"]
        ph = "DOWN x MARKDOWN" if c["side"] < 0 else "UP x MARKUP"
        L.append(f"| {c['id']} | {ph} | PRE_REG conds 1-8 (SMA20 SOURCED; windows, bands OURS) | BTC cycle label replaces index filter; no session/gap | V{c['variant']} | daily SMA20 at-level | 15m | "
                 f"{'short' if c['side'] < 0 else 'long'} | {dv['n']} | {v['n']} | {f(v['gross'])} | {f(v['net12'])} | {f(v['net6'])} | {f(v['win'] * 100 if v['win'] == v['win'] else v['win'], 1)} | "
                 f"{f(v.get('ci_trade_low'))} | {f(v.get('ci_day_low'))} | {f(v.get('ex5'))} | {f(v.get('placebo_p'))} | {f(v.get('bh_q'))} | {v.get('verdict')} |")
    L += ["", "Placebo p = random same-coin, same phase x label, same side, hour-matched entries with identical stop/exit/fee (1000 draws). "
          "A low placebo p means 'beats random', not 'profitable'. Gates need net R > 0 AND both CI lows > 0 AND ex-best-5 > 0 AND placebo p < 0.05 AND BH q <= 0.10 AND n VAL >= 200 "
          "(n 100-199 = THIN, cannot PASS; n < 100 = UNDERPOWERED).", "",
          "## CONTROL cells (never pooled with the primaries, descriptive; no gate or placebo)", "",
          "| cell | role | description | n DEV | net R 12bp DEV | n VAL | gross R | net R 12bp | net R 6bp | win % | trade CI low | day-cluster CI low | ex-best-5 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in res["cells"]:
        if c["role"] == "PRIMARY":
            continue
        v, dv = c["val"], c["dev"]
        L.append(f"| {c['id']} | {c['role']} | {c['name']} | {dv['n']} | {f(dv['net12'])} | {v['n']} | {f(v['gross'])} | {f(v['net12'])} | {f(v['net6'])} | "
                 f"{f(v['win'] * 100 if v['win'] == v['win'] else v['win'], 1)} | {f(v.get('ci_trade_low'))} | {f(v.get('ci_day_low'))} | {f(v.get('ex5'))} |")
    # at vs away comparison
    L += ["", "## At-level vs away-from-level, same cell (VALIDATION net R 12bp, n)", "", "| variant | cell at | at-level | cell away | away-level |", "|---|---|---|---|---|"]
    for k in range(6):
        a, b = res["cells"][k], res["cells"][6 + k]
        L.append(f"| {'short' if a['side'] < 0 else 'long'} V{a['variant']} | {a['id']} | {f(a['val']['net12'])} (n {a['val']['n']}) | {b['id']} | {f(b['val']['net12'])} (n {b['val']['n']}) |")
    L += ["", f"Total cells tried: {res['total_cells']}. Primary cells: {res['primary_cells']} (BH family m = 6). Placebo rows (6) are gate components.",
          f"Candidates simulated (all cells, before de-overlap): {res['candidates']}. Exit reasons: {res['exit_reasons']}.", "",
          "## Provenance", "", f"phase_daily.csv sha256 {res['phase_csv_sha256']}. Source: F:/MTS/data_cache/binance/<SYM>USDT_15m.npz (key `a`, [t,o,h,l,c,v]); every higher timeframe is resampled from that one 15m series per coin.", "",
          "| coin | first bar (UTC) | last bar (UTC) | rows | gaps | filled bars |", "|---|---|---|---|---|---|"]
    for p in res["provenance"]:
        L.append(f"| {p['coin']} | {p['first']} | {p['last']} | {p['rows']} | {p['gaps']} | {p['filled_bars']} |")
    (HERE / "RESULT_AUTO.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    {"counts": counts_only, "run": run}[sys.argv[1]]()
