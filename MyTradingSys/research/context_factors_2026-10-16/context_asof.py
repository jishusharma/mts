"""Point-in-time context factors F1-F7 at a decision time T, built twice (CONTEXT_FACTORS_SPEC.md holds every definition).

  context_at(bars, t, side)     REPLAY: bars[0..t] only (it slices the arrays it is given to t+1 before anything else);
                                every candle, band, level and percentile is recomputed from that prefix.
  context_frame(bars, side)     VECTORISED: full-array builds (pandas/numpy), one row per decision hour.
  load_dev_5m() / load_funding  DEV loader (bar open 2022-01-01 .. 2024-06-30); refuses any bar opening at/after 2024-07-01.

Decision time T = close of a 1h bar = ot[t] + 5 min, where t indexes the 5m bar array and T is a whole UTC hour.
Bars: dict of numpy arrays ot (open ms), o, h, l, c, v (5m klines), optional fund_t / fund_r (settled funding).
No outcome column exists anywhere in this module: nothing after T is read by either build.

`leak=` in context_frame plants one look-ahead per factor (test fixtures only, names in LEAKS); production calls never pass it.
Parameters: SOURCED or OURS per the table in CONTEXT_FACTORS_SPEC.md; the comment on each constant repeats the label.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BT = REPO / "MyTradingSys" / "backtest"
if str(BT) not in sys.path:
    sys.path.insert(0, str(BT))
from vp_pivot_probe import build_profile  # noqa: E402  FORMULAS 18.1 profile (POC/VAH/VAL), reused not copied

# ------------------------------------------------------------------ time
MIN5 = 300_000
HOUR = 3_600_000
DAY = 86_400_000
WEEK = 7 * DAY
MONDAY0 = 4 * DAY                      # 1970-01-05 00:00 UTC is a Monday (FORMULAS 8: Monday-anchored ISO week)
TF = {"1h": HOUR, "4h": 4 * HOUR, "8h": 8 * HOUR, "12h": 12 * HOUR, "D": DAY}
DEV_START_MS = 1_640_995_200_000       # 2022-01-01 00:00 UTC
DEV_END_MS = 1_719_792_000_000         # 2024-07-01 00:00 UTC: VALIDATION starts here, never read

# ------------------------------------------------------------------ parameters (label in the comment)
ATR_N = 14                 # FORMULAS 12 (plain-SMA ATR, operator decision 2026-09-28)
K_EVENT = 1.0              # OURS: "at a level" = nearest same-side level within 1.0 x ATR14(1h) of the close
KZ = 0.5                   # OURS: confluence zone = nearest level +- 0.5 x ATR14(1h)
ROUND_STEP = 1000.0        # OURS: round numbers = multiples of 1,000 USDT
VA_W = 10.0                # FORMULAS 18.1 bin width (NO-SOURCE there, reused)
KROWN_N = 2                # OURS: 4h fractal width (FORMULAS 18.2 strict comparisons)
KROWN_LOOKBACK = 360       # OURS: pivots whose 4h bar opened within the last 360 x 4h (60 days)
KROWN_TOL = 0.25           # OURS: pivots within 0.25 x ATR14(D) chain into one zone
KROWN_MIN = 2              # SOURCED: "where the price turned at least twice" (Krown, extract_qEfES84jwwo.md:65)
ROUND_TOUCH_WIN = 720      # OURS: touch count window for round numbers (720 1h bars = 30 days)
COST_PCT = 0.14            # SOURCED: gross_effect_screen PRE_REG s.1 (all-taker round trip)
COST_R_MAX = 0.25          # OURS: a stop is valid only if cost <= 0.25 R
W_MIN = COST_PCT / COST_R_MAX   # = 0.56 % (derived)
W_MAX_ATRD = 1.0           # OURS: "too much" = stop wider than 1.0 x ATR14(D) in % of price
PIN_WICK, PIN_BODY, DOJI_BODY = 0.6, 0.3, 0.1   # OURS candle thresholds (fractions of the candle range)
BB_N, BB_K = 20, 2.0       # SOURCED: Bollinger 20/2 default (bollinger_2026-10-14/SOURCES.md:10, [1])
WALK_N = 3                 # OURS, anchored on a T3 practitioner habit "3 or more closes" (SOURCES.md:9)
CUSHION = 0.05             # OURS variant: %b <= 0.05 counts as at the band (SOURCES.md:9 "any cushion would be our own")
PH_W_SMA, PH_W_SLOPE = 10, 2    # OURS: phase A = weekly close vs SMA10(W), slope vs 2 weeks earlier
PH_D_RET, PH_D_THR, PH_D_RANGE = 30, 0.075, 90   # phase B: tom_bt.trend_tag 30 d / 0.075 (reused), OURS 90 d range
ER_N, ER_THR = 24, 0.3     # OURS: intraday Kaufman efficiency ratio over 24 1h bars, >= 0.3 = trend
VOL_WIN = 2160             # OURS: ATR%(1h) percentile vs the previous 2,160 1h bars (90 days)
SQ_WIN, SQ_Q = 180, 0.2    # OURS: 4h bandwidth percentile vs the previous 180 4h bars (30 days), <= 0.2 = squeeze
APPROACH_N, APPROACH_FAST = 3, 1.5   # OURS: move over the last 3 1h bars toward the level, >= 1.5 ATR = fast
HTF_SMA = 20               # OURS: D and 4h close vs their SMA20 for alignment
FUND_BASE = 0.0001         # SOURCED: Binance default 0.01 % per 8 h (the base rate in the archive, e.g. 2022-01 rows)

LAYERS = ("prior_dw", "session", "pd_va", "pw_va", "krown", "vwap", "round", "bb4h")   # tie order for equal prices
TAGS = {"prior_dw": ("prior_dw",), "session": ("session",), "pd_va": ("tom", "fabio"), "pw_va": ("tom", "vp"), "krown": ("krown",),
        "vwap": ("vwap",), "round": ("round",), "bb4h": ("operator",)}
DYNAMIC = ("session", "vwap", "bb4h")
VWAP_MIN_D = 4 * 3_600_000   # OURS (angle b/c fix): session VWAP and session high/low count only after 4 h of the session
VWAP_MIN_W = 86_400_000      # OURS (angle b fix): a weekly VWAP only after the first day of the week
TF4 = ("D", "12h", "8h", "4h")
BULL, BEAR = ("bull_engulf", "pin_bull"), ("bear_engulf", "pin_bear")
LEAKS = ("f1_future_close", "f2_future_touches", "f3_final_day", "f4_partial_candle", "f5_next_bar",
         "f6_final_week", "f7_fullsample_vol", "f7_krown_unconfirmed")

REPLAY_DAYS = 120          # replay looks back at most this far (Monday-aligned); every lookback above fits inside it


def week_start(ms):
    return ((ms - MONDAY0) // WEEK) * WEEK + MONDAY0


# ------------------------------------------------------------------ shared small pure helpers (scalar, used by REPLAY)
def _candle_cat(o, h, l, c):
    """Pattern category of the last completed candle (index -1) given the last 3 candles as lists. OURS definitions."""
    o0, h0, l0, c0 = o[-1], h[-1], l[-1], c[-1]
    o1, h1, l1, c1 = o[-2], h[-2], l[-2], c[-2]
    if c1 < o1 and c0 > o0 and c0 > o1:          # operator (MAL-BB-MID-ENGULF M2, mirrored for bull)
        return "bull_engulf"
    if c1 > o1 and c0 < o0 and c0 < o1:
        return "bear_engulf"
    if h0 > h1 and l0 < l1:
        return "outside"
    if h0 <= h1 and l0 >= l1:
        return "inside"
    rng = h0 - l0
    body = abs(c0 - o0)
    if rng > 0:
        lw = min(o0, c0) - l0
        uw = h0 - max(o0, c0)
        if lw >= PIN_WICK * rng and body <= PIN_BODY * rng:
            return "pin_bull"
        if uw >= PIN_WICK * rng and body <= PIN_BODY * rng:
            return "pin_bear"
    if c[-1] > o[-1] and c[-2] > o[-2] and c[-3] > o[-3]:
        return "three_up"
    if c[-1] < o[-1] and c[-2] < o[-2] and c[-3] < o[-3]:
        return "three_down"
    if rng == 0 or body <= DOJI_BODY * rng:
        return "doji"
    return "none"


def _engulf_cls(o, c):
    """Classic body engulf (variant, logged in trials.csv): the body covers the previous body, open included."""
    o0, c0, o1, c1 = o[-1], c[-1], o[-2], c[-2]
    if c1 < o1 and c0 > o0 and o0 <= c1 and c0 >= o1 and (o0 < c1 or c0 > o1):
        return "bull"
    if c1 > o1 and c0 < o0 and o0 >= c1 and c0 <= o1 and (o0 > c1 or c0 < o1):
        return "bear"
    return "none"


def _align(cat, side):
    good, bad = (BULL, BEAR) if side == "long" else (BEAR, BULL)
    return "with" if cat in good else "against" if cat in bad else "none"


def _bb_state(below, above, bw, n):
    """below/above: lists of booleans for the last n+1 bars (index -1 = latest); bw: bandwidths for the same bars."""
    nlow = 0
    for b in reversed(below):
        if not b:
            break
        nlow += 1
    nup = 0
    for b in reversed(above):
        if not b:
            break
        nup += 1
    expanding = bw[-1] > bw[-1 - n]
    if nlow >= n and expanding:
        return "walk_lower"
    if nup >= n and expanding:
        return "walk_upper"
    if below[-1]:
        return "break_lower"
    if above[-1]:
        return "break_upper"
    if below[-2]:
        return "reenter_lower"
    if above[-2]:
        return "reenter_upper"
    return "inside"


def _phase_a(cw, slope):
    if cw >= 0 and slope > 0:          # cw = weekly close minus SMA
        return "markup"
    if cw >= 0:
        return "distribution"
    if slope < 0:
        return "markdown"
    return "accumulation"


def _fund_cat(r):
    if r != r:
        return "na"
    if r < 0:
        return "neg"
    if r < FUND_BASE - 1e-9:
        return "low"
    if r <= FUND_BASE + 1e-9:
        return "base"
    return "high"


def _session(hour):
    return "asia" if hour < 8 else "london" if hour < 13 else "ny" if hour < 21 else "late"


def _touch_cat(n):
    return "untested" if n == 0 else "first" if n == 1 else "retest"


def _cluster(pivots, tol):
    """pivots: list of (price, confirm_ms). Chain on sorted price, gap <= tol. Returns [(mean price, created_ms)] for
    clusters of >= KROWN_MIN; created = the second-earliest confirmation in the cluster."""
    out = []
    if not pivots:
        return out
    ps = sorted(pivots)
    cur = [ps[0]]
    for p in ps[1:]:
        if p[0] - cur[-1][0] <= tol:
            cur.append(p)
        else:
            if len(cur) >= KROWN_MIN:
                out.append(cur)
            cur = [p]
    if len(cur) >= KROWN_MIN:
        out.append(cur)
    res = []
    for cl in out:
        s = 0.0
        for p in cl:
            s += p[0]
        res.append((s / len(cl), sorted(q[1] for q in cl)[1]))
    return res


def _pick_near(levels, side):
    """levels: list of (price, layer, created). Nearest support (long) / resistance (short), ties by LAYERS order."""
    if not levels:
        return None
    if side == "long":
        return sorted(levels, key=lambda x: (-x[0], LAYERS.index(x[1])))[0]
    return sorted(levels, key=lambda x: (x[0], LAYERS.index(x[1])))[0]


# ================================================================== REPLAY (bars[0..t] only)
class _Agg:
    """Candles of one timeframe from a 5m prefix: lists start, o, h, l, c, v (all buckets, last may be partial)."""

    def __init__(self, ot, o, h, l, c, v, keyfn):
        self.start, self.o, self.h, self.l, self.c, self.v = [], [], [], [], [], []
        cur = None
        for i in range(len(ot)):
            k = keyfn(int(ot[i]))
            if k != cur:
                cur = k
                self.start.append(k); self.o.append(float(o[i])); self.h.append(float(h[i]))
                self.l.append(float(l[i])); self.c.append(float(c[i])); self.v.append(float(v[i]))
            else:
                if h[i] > self.h[-1]:
                    self.h[-1] = float(h[i])
                if l[i] < self.l[-1]:
                    self.l[-1] = float(l[i])
                self.c[-1] = float(c[i]); self.v[-1] += float(v[i])

    def completed(self, T, length):
        """Number of buckets whose end <= T (they come first; at most the last bucket is partial)."""
        n = len(self.start)
        if n and self.start[-1] + length > T:
            return n - 1
        return n


def _atr_last(h, l, c, j):
    """Plain-SMA ATR14 at completed index j (FORMULAS 12); NaN if j < ATR_N."""
    if j < ATR_N:
        return float("nan")
    s = 0.0
    for i in range(j - ATR_N + 1, j + 1):
        s += max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    return s / ATR_N


def _bands(c, j):
    """(mid, upper, lower, bw) of BB(20, 2, population SD) at index j; None if j < BB_N - 1."""
    if j < BB_N - 1:
        return None
    w = c[j - BB_N + 1:j + 1]
    m = sum(w) / BB_N
    sd = (sum((x - m) ** 2 for x in w) / BB_N) ** 0.5
    return m, m + BB_K * sd, m - BB_K * sd, (2 * BB_K * sd) / m


def _bb_block(c, j, cushion):
    """BB state at completed index j (needs WALK_N + 1 banded bars)."""
    if j - WALK_N < BB_N - 1:
        return "na"
    below, above, bw = [], [], []
    for i in range(j - WALK_N, j + 1):
        m, up, lo, b = _bands(c, i)
        if cushion:
            pb = (c[i] - lo) / (up - lo) if up > lo else 0.5
            below.append(pb <= CUSHION); above.append(pb >= 1 - CUSHION)
        else:
            below.append(c[i] <= lo); above.append(c[i] >= up)
        bw.append(b)
    return _bb_state(below, above, bw, WALK_N)


def _replay_both(bars, t):
    """Both sides at decision T = ot[t] + 5 min, from bars[0..t] only."""
    ot = np.asarray(bars["ot"][:t + 1])
    T = int(ot[-1]) + MIN5
    if T % HOUR:
        raise ValueError("decision time must be a whole UTC hour (t must be the last 5m bar of an hour)")
    if T > DEV_END_MS:
        raise ValueError("bar at/after 2024-07-01 (VALIDATION) refused")
    w0 = week_start(T - REPLAY_DAYS * DAY)
    i0 = int(np.searchsorted(ot, w0, "left"))
    sl = slice(i0, t + 1)
    o5 = np.asarray(bars["o"][sl], float); h5 = np.asarray(bars["h"][sl], float)
    l5 = np.asarray(bars["l"][sl], float); c5 = np.asarray(bars["c"][sl], float)
    v5 = np.asarray(bars["v"][sl], float); ot5 = ot[i0:]
    A = {"1h": _Agg(ot5, o5, h5, l5, c5, v5, lambda m: (m // HOUR) * HOUR)}
    H1 = A["1h"]     # higher timeframes from the 1h candles (OHLCV aggregation is associative)
    for k in ("4h", "8h", "12h", "D"):
        A[k] = _Agg(H1.start, H1.o, H1.h, H1.l, H1.c, H1.v, (lambda L: (lambda m: (m // L) * L))(TF[k]))
    A["W"] = _Agg(H1.start, H1.o, H1.h, H1.l, H1.c, H1.v, week_start)
    n = {k: A[k].completed(T, TF[k]) for k in TF}
    n["W"] = A["W"].completed(T, WEEK)
    H = A["1h"]
    j = n["1h"] - 1
    c_t = H.c[j]
    atr1 = _atr_last(H.h, H.l, H.c, j)
    D = A["D"]; jd = n["D"] - 1
    atrd = _atr_last(D.h, D.l, D.c, jd)

    # ---- levels (price, layer, created_ms or None)
    lv = []
    if jd >= 0:
        lv += [(D.h[jd], "prior_dw", D.start[jd] + DAY), (D.l[jd], "prior_dw", D.start[jd] + DAY)]
        m = (ot5 >= D.start[jd]) & (ot5 < D.start[jd] + DAY)
        p = build_profile(l5[m], h5[m], v5[m], VA_W)
        if p:
            lv += [(p["poc_price"], "pd_va", D.start[jd] + DAY), (p["vah"], "pd_va", D.start[jd] + DAY),
                   (p["val"], "pd_va", D.start[jd] + DAY)]
    Wk = A["W"]; jw = n["W"] - 1
    if jw >= 0:
        lv += [(Wk.h[jw], "prior_dw", Wk.start[jw] + WEEK), (Wk.l[jw], "prior_dw", Wk.start[jw] + WEEK)]
        m = (ot5 >= Wk.start[jw]) & (ot5 < Wk.start[jw] + WEEK)
        p = build_profile(l5[m], h5[m], v5[m], VA_W)
        if p:
            lv += [(p["poc_price"], "pw_va", Wk.start[jw] + WEEK), (p["vah"], "pw_va", Wk.start[jw] + WEEK),
                   (p["val"], "pw_va", Wk.start[jw] + WEEK)]
    F4h = A["4h"]; j4 = n["4h"] - 1
    if atrd == atrd:
        piv = []
        for i in range(KROWN_N, j4 - KROWN_N + 1):
            if F4h.start[i] < T - KROWN_LOOKBACK * TF["4h"]:
                continue
            conf = F4h.start[i + KROWN_N] + TF["4h"]
            nb = [F4h.h[k] for k in range(i - KROWN_N, i + KROWN_N + 1) if k != i]
            if all(F4h.h[i] > x for x in nb):
                piv.append((F4h.h[i], conf))
            nb = [F4h.l[k] for k in range(i - KROWN_N, i + KROWN_N + 1) if k != i]
            if all(F4h.l[i] < x for x in nb):
                piv.append((F4h.l[i], conf))
        for px, cr in _cluster(piv, KROWN_TOL * atrd):
            lv.append((px, "krown", cr))
    day0 = (T // DAY) * DAY
    m = ot5 >= day0
    if T - day0 >= VWAP_MIN_D and m.any():      # angle c fix: early-session extremes are just the last bars' range
        lv += [(float(h5[m].max()), "session", None), (float(l5[m].min()), "session", None)]
    if T - day0 >= VWAP_MIN_D and m.any() and v5[m].sum() > 0:
        lv.append((float(((h5[m] + l5[m] + c5[m]) / 3 * v5[m]).sum() / v5[m].sum()), "vwap", None))
    m = ot5 >= week_start(T)
    if T - week_start(T) >= VWAP_MIN_W and m.any() and v5[m].sum() > 0:
        lv.append((float(((h5[m] + l5[m] + c5[m]) / 3 * v5[m]).sum() / v5[m].sum()), "vwap", None))
    below = np.floor(c_t / ROUND_STEP) * ROUND_STEP
    if below == c_t:
        below -= ROUND_STEP
    above = np.ceil(c_t / ROUND_STEP) * ROUND_STEP
    if above == c_t:
        above += ROUND_STEP
    lv += [(float(below), "round", None), (float(above), "round", None)]
    if j4 >= BB_N - 1:
        lv.append((sum(F4h.c[j4 - BB_N + 1:j4 + 1]) / BB_N, "bb4h", None))
    c4 = F4h.c[j4] if j4 >= 0 else c_t

    # ---- shared per-T values
    o3 = {}
    for k in TF4:
        jj = n[k] - 1
        if jj >= 2:
            sl3 = slice(jj - 2, jj + 1)
            o3[k] = (A[k].o[sl3], A[k].h[sl3], A[k].l[sl3], A[k].c[sl3])
    bb1 = _bb_block(H.c, j, False)
    bb1c = _bb_block(H.c, j, True)
    bb4 = _bb_block(F4h.c, j4, False) if j4 >= 0 else "na"
    if jw >= PH_W_SMA - 1 + PH_W_SLOPE:
        sma = lambda q: sum(Wk.c[q - PH_W_SMA + 1:q + 1]) / PH_W_SMA  # noqa: E731
        phA = _phase_a(Wk.c[jw] - sma(jw), sma(jw) - sma(jw - PH_W_SLOPE))
    else:
        phA = "na"
    if jd >= PH_D_RANGE - 1 and jd >= PH_D_RET:
        r30 = D.c[jd] / D.c[jd - PH_D_RET] - 1
        if r30 >= PH_D_THR:
            phB = "markup"
        elif r30 <= -PH_D_THR:
            phB = "markdown"
        else:
            lo90 = min(D.l[jd - PH_D_RANGE + 1:jd + 1]); hi90 = max(D.h[jd - PH_D_RANGE + 1:jd + 1])
            pos = (D.c[jd] - lo90) / (hi90 - lo90) if hi90 > lo90 else 0.5
            phB = "distribution" if pos >= 2 / 3 else "accumulation" if pos <= 1 / 3 else "balance"
    else:
        phB = "na"
    if j >= ER_N:
        path = sum(abs(H.c[i] - H.c[i - 1]) for i in range(j - ER_N + 1, j + 1))
        net = H.c[j] - H.c[j - ER_N]
        er = abs(net) / path if path > 0 else 0.0
        intra = ("trend_up" if net > 0 else "trend_down") if er >= ER_THR else "balance"
    else:
        intra = "na"
    if j >= VOL_WIN + ATR_N:
        cur = atr1 / c_t
        prev = [_atr_last(H.h, H.l, H.c, i) / H.c[i] for i in range(j - VOL_WIN, j)]
        pct = sum(1 for x in prev if x < cur) / VOL_WIN
        volreg = "low" if pct < 1 / 3 else "mid" if pct < 2 / 3 else "high"
    else:
        volreg = "na"
    if j4 >= SQ_WIN + BB_N - 1:
        cur = _bands(F4h.c, j4)[3]
        prev = [_bands(F4h.c, i)[3] for i in range(j4 - SQ_WIN, j4)]
        sq = "squeeze" if sum(1 for x in prev if x < cur) / SQ_WIN <= SQ_Q else "normal"
    else:
        sq = "na"
    hr_open = T - HOUR
    session = _session((hr_open % DAY) // HOUR)
    weekend = "weekend" if ((hr_open // DAY) + 3) % 7 >= 5 else "weekday"   # epoch day 0 = Thursday -> Mon = 0
    if "fund_t" in bars:
        ft = np.asarray(bars["fund_t"]); k = int(np.searchsorted(ft, T, "left")) - 1
        fund = _fund_cat(float(bars["fund_r"][k])) if k >= 0 else "na"
    else:
        fund = "na"
    smaD = sum(D.c[jd - HTF_SMA + 1:jd + 1]) / HTF_SMA if jd >= HTF_SMA - 1 else None
    sma4 = sum(F4h.c[j4 - HTF_SMA + 1:j4 + 1]) / HTF_SMA if j4 >= HTF_SMA - 1 else None
    pd_o = D.o[jd] if jd >= 0 else float("nan")
    part = (ot5 >= day0)
    part_h = float(h5[part].max()) if part.any() else c_t
    part_l = float(l5[part].min()) if part.any() else c_t

    out = {}
    for side in ("long", "short"):
        sgn = 1 if side == "long" else -1
        mine = [x for x in lv if (x[0] < c_t if side == "long" else x[0] > c_t)]
        mine4 = [x for x in mine if (x[0] < c4 if side == "long" else x[0] > c4)]
        r = {"T": T, "side": side, "close": c_t, "atr1h": atr1, "f1_n_levels": len(mine), "f1_n_levels_v4h": len(mine4)}
        near = _pick_near(mine, side)
        if near is None or atr1 != atr1:
            r.update(f1_near_px=float("nan"), f1_near_layer="none", f1_dist_atr=float("nan"), f1_at_level=False,
                     f2_conf_obj=0, f2_conf_name=0, f2_age_h=float("nan"), f2_touches=-1, f2_touch_cat="na")
        else:
            L = near[0]
            dist = sgn * (c_t - L) / atr1
            zone = [x for x in mine if abs(x[0] - L) <= KZ * atr1]
            r.update(f1_near_px=L, f1_near_layer=near[1], f1_dist_atr=dist, f1_at_level=bool(dist <= K_EVENT),
                     f2_conf_obj=len({x[1] for x in zone}), f2_conf_name=len({tg for x in zone for tg in TAGS[x[1]]}))
            if near[1] in DYNAMIC:
                r.update(f2_age_h=float("nan"), f2_touches=-1, f2_touch_cat="dynamic")
            else:
                if near[2] is None:
                    lo_i = max(0, j - ROUND_TOUCH_WIN + 1)
                else:
                    lo_i = next((i for i in range(j + 1) if H.start[i] >= near[2]), j + 1)
                nt = sum(1 for i in range(lo_i, j + 1) if H.l[i] <= L <= H.h[i])
                r.update(f2_age_h=float("nan") if near[2] is None else (T - near[2]) / HOUR, f2_touches=nt,
                         f2_touch_cat=_touch_cat(nt))
        # F3
        armA = bool(c_t > pd_o) if side == "long" else bool(c_t < pd_o)
        armB = bool(part_h > pd_o) if side == "long" else bool(part_l < pd_o)
        wmax = W_MAX_ATRD * atrd / c_t * 100 if atrd == atrd else float("nan")
        widths = {}
        for k in ("D", "12h", "8h"):
            jj = n[k] - 1
            if jj < 0:
                widths[k] = float("nan"); continue
            wv = ((c_t - A[k].l[jj]) if side == "long" else (A[k].h[jj] - c_t)) / c_t * 100
            widths[k] = wv if wv > 0 else float("nan")
        stf = "none"
        for k in ("D", "12h", "8h"):          # refine only a stop that is too wide (operator: "if it is too much")
            if widths[k] != widths[k] or wmax != wmax or widths[k] < W_MIN:
                break
            if widths[k] <= wmax:
                stf = k
                break
        r.update(f3_armed=armA, f3_armed_B=armB, f3_w_D=widths["D"], f3_w_12h=widths["12h"], f3_w_8h=widths["8h"],
                 f3_wmax=wmax, f3_stop_tf=stf, f3_stop_pct=widths[stf] if stf != "none" else float("nan"),
                 f3_cost_R=COST_PCT / widths[stf] if stf != "none" else float("nan"))
        # F4
        for k in TF4:
            if k in o3:
                oo, hh, ll, cc = o3[k]
                cat = _candle_cat(oo, hh, ll, cc)
                r[f"f4_{k}_cat"] = cat; r[f"f4_{k}_align"] = _align(cat, side); r[f"f4_{k}_eng_cls"] = _engulf_cls(oo, cc)
            else:
                r[f"f4_{k}_cat"] = "na"; r[f"f4_{k}_align"] = "na"; r[f"f4_{k}_eng_cls"] = "na"
        # F5
        r.update(f5_1h=bb1, f5_1h_cush=bb1c, f5_4h=bb4,
                 f5_veto=bool(bb1 == ("walk_lower" if side == "short" else "walk_upper")),
                 f5_conf=bool(bb1 == ("reenter_lower" if side == "long" else "reenter_upper")))
        # F6
        r.update(f6_phaseA=phA, f6_phaseB=phB, f6_intraday=intra)
        # F7
        if j >= APPROACH_N and atr1 == atr1:
            ap = sgn * (H.c[j - APPROACH_N] - H.c[j]) / atr1
            appr = "fast" if ap >= APPROACH_FAST else "slow" if ap > 0 else "away"
        else:
            appr = "na"
        if j >= 1:
            if side == "long":
                sw = any(H.l[j] < x[0] and H.c[j - 1] > x[0] for x in mine)
            else:
                sw = any(H.h[j] > x[0] and H.c[j - 1] < x[0] for x in mine)
        else:
            sw = False
        if smaD is not None and sma4 is not None:
            al = int(sgn * (D.c[jd] - smaD) > 0) + int(sgn * (F4h.c[j4] - sma4) > 0)
            htf = str(al)
        else:
            htf = "na"
        r.update(f7_volreg=volreg, f7_squeeze=sq, f7_session=session, f7_weekend=weekend, f7_approach=appr,
                 f7_sweep=bool(sw), f7_htf_align=htf, f7_funding=fund)
        out[side] = r
    return out


def context_at(bars, t, side):
    """REPLAY build: dict of every factor for `side` ('long'|'short') at T = ot[t] + 5 min, from bars[0..t] only."""
    return _replay_both(bars, t)[side]


# ================================================================== VECTORISED (full arrays, one row per decision hour)

# ------------------------------------------------------------------ VECTORISED-side helpers (written separately from the
# scalar helpers above so that no factor logic is shared between the two builds; only constants and build_profile are)
_SESSION_OF_HOUR = np.array(["asia"] * 8 + ["london"] * 5 + ["ny"] * 8 + ["late"] * 3, dtype=object)
_ALIGN = {"long": {"bull_engulf": "with", "pin_bull": "with", "bear_engulf": "against", "pin_bear": "against"},
          "short": {"bear_engulf": "with", "pin_bear": "with", "bull_engulf": "against", "pin_bull": "against"}}


def _cluster_np(price, conf, tol):
    """Krown chaining with numpy: split the price-sorted pivots where the gap exceeds tol."""
    if len(price) == 0:
        return []
    order = np.lexsort((conf, price))
    p, cf = np.asarray(price, float)[order], np.asarray(conf, np.int64)[order]
    cuts = np.flatnonzero(np.diff(p) > tol) + 1
    res = []
    for a, b in zip(np.r_[0, cuts], np.r_[cuts, len(p)]):
        if b - a >= KROWN_MIN:
            res.append((sum(p[a:b].tolist()) / (b - a), int(np.partition(cf[a:b], 1)[1])))
    return res


def _near_np(px, layer_rank, side):
    """Index of the nearest level: max price below (long) / min price above (short); ties -> lowest layer rank."""
    px = np.asarray(px, float); lr = np.asarray(layer_rank)
    key = np.lexsort((lr, -px)) if side == "long" else np.lexsort((lr, px))
    return int(key[0])


def _phase_a_np(cw, slope):
    return np.select([(cw >= 0) & (slope > 0), cw >= 0, slope < 0], ["markup", "distribution", "markdown"], "accumulation")


def _fund_np(r):
    r = np.asarray(r, float)
    return np.select([np.isnan(r), r < 0, r < FUND_BASE - 1e-9, r <= FUND_BASE + 1e-9], ["na", "neg", "low", "base"], "high")

def _agg_frame(df5, key):
    g = df5.groupby(key, sort=True)
    a = pd.DataFrame({"o": g["o"].first(), "h": g["h"].max(), "l": g["l"].min(), "c": g["c"].last(), "v": g["v"].sum()})
    a.index.name = "start"
    return a


def _atr_series(a):
    pc = a["c"].shift(1)
    tr = pd.concat([a["h"] - a["l"], (a["h"] - pc).abs(), (a["l"] - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    return tr.rolling(ATR_N, min_periods=ATR_N).mean()


def _bb_frame(c, cushion):
    mid = c.rolling(BB_N, min_periods=BB_N).mean()
    sd = c.rolling(BB_N, min_periods=BB_N).std(ddof=0)
    up, lo = mid + BB_K * sd, mid - BB_K * sd
    bw = (up - lo) / mid
    if cushion:
        pb = ((c - lo) / (up - lo)).where(up > lo, 0.5)
        below, above = pb <= CUSHION, pb >= 1 - CUSHION
    else:
        below, above = c <= lo, c >= up
    below = below & mid.notna(); above = above & mid.notna()
    ok = mid.shift(WALK_N).notna()
    st = pd.Series("inside", index=c.index, dtype=object)
    st[below.shift(1, fill_value=False) & ok] = "reenter_lower"     # lowest priority first; later rows overwrite
    st[above.shift(1, fill_value=False) & ok & ~below.shift(1, fill_value=False)] = "reenter_upper"
    st[above & ok] = "break_upper"
    st[below & ok] = "break_lower"
    run_lo = below.astype(int).rolling(WALK_N, min_periods=WALK_N).sum() == WALK_N
    run_up = above.astype(int).rolling(WALK_N, min_periods=WALK_N).sum() == WALK_N
    exp = bw > bw.shift(WALK_N)
    st[run_up & exp & ok] = "walk_upper"
    st[run_lo & exp & ok] = "walk_lower"
    st[~ok] = "na"
    return st, mid, bw


def _cat_frame(a):
    o, h, l, c = a["o"], a["h"], a["l"], a["c"]
    o1, h1, l1, c1 = o.shift(1), h.shift(1), l.shift(1), c.shift(1)
    rng, body = h - l, (c - o).abs()
    lw, uw = np.minimum(o, c) - l, h - np.maximum(o, c)
    green, red = c > o, c < o
    conds = [
        ("bull_engulf", (c1 < o1) & green & (c > o1)),
        ("bear_engulf", (c1 > o1) & red & (c < o1)),
        ("outside", (h > h1) & (l < l1)),
        ("inside", (h <= h1) & (l >= l1)),
        ("pin_bull", (rng > 0) & (lw >= PIN_WICK * rng) & (body <= PIN_BODY * rng)),
        ("pin_bear", (rng > 0) & (uw >= PIN_WICK * rng) & (body <= PIN_BODY * rng)),
        ("three_up", green & green.shift(1, fill_value=False) & green.shift(2, fill_value=False)),
        ("three_down", red & red.shift(1, fill_value=False) & red.shift(2, fill_value=False)),
        ("doji", (rng == 0) | (body <= DOJI_BODY * rng)),
    ]
    cat = np.select([cv.fillna(False).to_numpy(bool) for _, cv in conds], [k for k, _ in conds], "none").astype(object)
    cat[:2] = "na"
    bull_c = (c1 < o1) & green & (o <= c1) & (c >= o1) & ((o < c1) | (c > o1))
    bear_c = (c1 > o1) & red & (o >= c1) & (c <= o1) & ((o > c1) | (c < o1))
    eng = np.where(bull_c, "bull", np.where(bear_c, "bear", "none")).astype(object)
    eng[:2] = "na"
    return pd.Series(cat, index=a.index), pd.Series(eng, index=a.index)


def _last_completed(starts, length, T):
    """Index into `starts` of the last bucket with start + length <= T (vectorised over T), -1 if none."""
    return np.searchsorted(np.asarray(starts) + length, T, "right") - 1


def _leak_fwd_next(series):
    """PLANTED LEAK helper (tests only): the value of the following row."""
    return series.shift(-1)


def context_frame(bars, side, leak=None, decisions=None, keep_levels=False):
    """VECTORISED build: DataFrame (index = decision time T ms) with the same keys as context_at.
    decisions: optional array of T values (whole hours) to emit; default every 1h bar end."""
    if leak is not None and leak not in LEAKS:
        raise ValueError(f"unknown leak {leak}")
    df5 = pd.DataFrame({k: np.asarray(bars[k]) for k in ("ot", "o", "h", "l", "c", "v")})
    df5[["o", "h", "l", "c", "v"]] = df5[["o", "h", "l", "c", "v"]].astype(float)
    if len(df5) and int(df5["ot"].iloc[-1]) >= DEV_END_MS:
        raise ValueError("bar at/after 2024-07-01 (VALIDATION) refused")
    ot = df5["ot"].to_numpy(np.int64)
    agg = {k: _agg_frame(df5, (ot // L) * L) for k, L in TF.items()}
    agg["W"] = _agg_frame(df5, week_start(ot))
    length = dict(TF); length["W"] = WEEK
    sgn = 1 if side == "long" else -1
    last5_end = int(ot[-1]) + MIN5
    H = agg["1h"]
    Tall = H.index.to_numpy(np.int64) + HOUR
    Tall = Tall[Tall <= last5_end]
    Ts = Tall if decisions is None else np.asarray(decisions, np.int64)
    jh = _last_completed(H.index, HOUR, Ts)
    idx = {k: _last_completed(agg[k].index, length[k], Ts) for k in agg}
    hc, hh, hl = H["c"].to_numpy(), H["h"].to_numpy(), H["l"].to_numpy()
    hstart = H.index.to_numpy(np.int64)
    if leak == "f1_future_close":
        c_role = _leak_fwd_next(H["c"]).to_numpy()
    else:
        c_role = hc
    atr = {k: _atr_series(agg[k]).to_numpy() for k in agg}
    c_t = hc[jh]
    atr1 = atr["1h"][jh]
    atrd = np.where(idx["D"] >= 0, atr["D"][np.maximum(idx["D"], 0)], np.nan)

    # profiles of every completed D and W bucket
    def profiles(key, L):
        g = (ot // L) * L if key != "W" else week_start(ot)
        res = {}
        bounds = np.flatnonzero(np.diff(g)) + 1
        starts = np.concatenate([[0], bounds]); ends = np.concatenate([bounds, [len(g)]])
        lo, hi, vo = df5["l"].to_numpy(), df5["h"].to_numpy(), df5["v"].to_numpy()
        for s, e in zip(starts, ends):
            p = build_profile(lo[s:e], hi[s:e], vo[s:e], VA_W)
            if p:
                res[int(g[s])] = p
        return res
    prof_d, prof_w = profiles("D", DAY), profiles("W", WEEK)

    # Krown pivots on 4h
    F4 = agg["4h"]
    f4h, f4l, f4s = F4["h"].to_numpy(), F4["l"].to_numpy(), F4.index.to_numpy(np.int64)
    n4 = len(F4)
    ph = np.zeros(n4, bool); pl = np.zeros(n4, bool)
    for i in range(KROWN_N, n4 - KROWN_N):
        win_h = np.r_[f4h[i - KROWN_N:i], f4h[i + 1:i + KROWN_N + 1]]
        win_l = np.r_[f4l[i - KROWN_N:i], f4l[i + 1:i + KROWN_N + 1]]
        ph[i] = np.all(f4h[i] > win_h); pl[i] = np.all(f4l[i] < win_l)
    usable_after = np.arange(n4) + (0 if leak == "f7_krown_unconfirmed" else KROWN_N)   # index whose close confirms it
    conf_ms = np.where(usable_after < n4, f4s[np.minimum(usable_after, n4 - 1)] + 4 * HOUR, np.iinfo(np.int64).max)

    # session / weekly VWAP from cumulative sums, sampled at the last 5m bar before T
    tpv = ((df5["h"] + df5["l"] + df5["c"]) / 3 * df5["v"]).to_numpy()
    vv = df5["v"].to_numpy()
    dkey, wkey = ot // DAY, week_start(ot)
    cs_d_tpv = pd.Series(tpv).groupby(dkey).cumsum().to_numpy(); cs_d_v = pd.Series(vv).groupby(dkey).cumsum().to_numpy()
    cs_w_tpv = pd.Series(tpv).groupby(wkey).cumsum().to_numpy(); cs_w_v = pd.Series(vv).groupby(wkey).cumsum().to_numpy()
    i5 = np.searchsorted(ot, Ts, "left") - 1        # last 5m bar with open < T
    part_h_all = pd.Series(df5["h"].to_numpy()).groupby(dkey).cummax().to_numpy()
    part_l_all = pd.Series(df5["l"].to_numpy()).groupby(dkey).cummin().to_numpy()

    # BB, candle categories, phases, volatility
    bb1, _, _ = _bb_frame(H["c"], False)
    bb1c, _, _ = _bb_frame(H["c"], True)
    bb4, mid4, bw4 = _bb_frame(F4["c"], False)
    if leak == "f5_next_bar":
        bb1 = _leak_fwd_next(bb1)
    cats = {k: _cat_frame(agg[k]) for k in TF4}
    Wk = agg["W"]
    smaW = Wk["c"].rolling(PH_W_SMA, min_periods=PH_W_SMA).mean()
    slopeW = smaW - smaW.shift(PH_W_SLOPE)
    Dg = agg["D"]
    r30 = Dg["c"] / Dg["c"].shift(PH_D_RET) - 1
    lo90 = Dg["l"].rolling(PH_D_RANGE, min_periods=PH_D_RANGE).min()
    hi90 = Dg["h"].rolling(PH_D_RANGE, min_periods=PH_D_RANGE).max()
    pos90 = ((Dg["c"] - lo90) / (hi90 - lo90)).where(hi90 > lo90, 0.5)
    smaD = Dg["c"].rolling(HTF_SMA, min_periods=HTF_SMA).mean().to_numpy()
    sma4 = F4["c"].rolling(HTF_SMA, min_periods=HTF_SMA).mean().to_numpy()
    path = H["c"].diff().abs().rolling(ER_N, min_periods=ER_N).sum()
    net = H["c"] - H["c"].shift(ER_N)
    er = (net.abs() / path).where(path > 0, 0.0)
    atrp = pd.Series(atr["1h"] / hc)
    if leak == "f7_fullsample_vol":
        pct_vol = atrp.rank(pct=True).to_numpy()
    else:
        pct_vol = np.full(len(atrp), np.nan)
        a = atrp.to_numpy()
        for i in range(VOL_WIN + ATR_N, len(a)):
            pct_vol[i] = np.count_nonzero(a[i - VOL_WIN:i] < a[i]) / VOL_WIN
    bwa = bw4.to_numpy()
    pct_sq = np.full(n4, np.nan)
    for i in range(SQ_WIN + BB_N - 1, n4):
        pct_sq[i] = np.count_nonzero(bwa[i - SQ_WIN:i] < bwa[i]) / SQ_WIN
    if "fund_t" in bars:
        ft = np.asarray(bars["fund_t"]); fr = np.asarray(bars["fund_r"], float)
        kf = np.searchsorted(ft, Ts, "left") - 1
        fund_all = _fund_np(np.where(kf >= 0, fr[np.maximum(kf, 0)], np.nan))
    cwW, slW = (Wk["c"] - smaW).to_numpy(), slopeW.to_numpy()
    phaseA_all = np.where(np.isnan(slW), "na", _phase_a_np(np.nan_to_num(cwW), np.nan_to_num(slW))).astype(object)
    rows = []
    for q, T in enumerate(Ts):
        T = int(T)
        j = int(jh[q]); c = float(c_t[q]); a1 = float(atr1[q]); ad = float(atrd[q])
        jd, jw, j4 = int(idx["D"][q]), int(idx["W"][q]), int(idx["4h"][q])
        lv = []
        if leak == "f3_final_day":
            jd_f3 = jd + 1 if jd + 1 < len(Dg) else jd       # the current day's final candle
        else:
            jd_f3 = jd
        if jd >= 0:
            ds = int(Dg.index[jd])
            lv += [(float(Dg["h"].iat[jd]), "prior_dw", ds + DAY), (float(Dg["l"].iat[jd]), "prior_dw", ds + DAY)]
            p = prof_d.get(ds)
            if p:
                lv += [(p["poc_price"], "pd_va", ds + DAY), (p["vah"], "pd_va", ds + DAY), (p["val"], "pd_va", ds + DAY)]
        if leak == "f6_final_week":
            jw_ph = jw + 1 if jw + 1 < len(Wk) else jw
        else:
            jw_ph = jw
        if jw >= 0:
            ws = int(Wk.index[jw])
            lv += [(float(Wk["h"].iat[jw]), "prior_dw", ws + WEEK), (float(Wk["l"].iat[jw]), "prior_dw", ws + WEEK)]
            p = prof_w.get(ws)
            if p:
                lv += [(p["poc_price"], "pw_va", ws + WEEK), (p["vah"], "pw_va", ws + WEEK), (p["val"], "pw_va", ws + WEEK)]
        if ad == ad:
            lo_i = int(np.searchsorted(f4s, T - KROWN_LOOKBACK * 4 * HOUR, "left"))
            cand = np.arange(max(lo_i, KROWN_N), max(j4 - KROWN_N + 1, 0))
            if leak == "f7_krown_unconfirmed":
                cand = np.arange(max(lo_i, KROWN_N), max(min(j4 + 1, n4 - KROWN_N), 0))
            piv = [(float(f4h[i]), int(conf_ms[i])) for i in cand if ph[i]] + \
                  [(float(f4l[i]), int(conf_ms[i])) for i in cand if pl[i]]
            if piv:
                pp, cc = zip(*piv)
                for px, cr in _cluster_np(np.array(pp), np.array(cc), KROWN_TOL * ad):
                    lv.append((px, "krown", cr))
        k5 = int(i5[q])
        in_day = bool(T % DAY) and k5 >= 0 and dkey[k5] == T // DAY
        if in_day and T % DAY >= VWAP_MIN_D:
            lv += [(float(part_h_all[k5]), "session", None), (float(part_l_all[k5]), "session", None)]
        if in_day and T % DAY >= VWAP_MIN_D and cs_d_v[k5] > 0:
            lv.append((float(cs_d_tpv[k5] / cs_d_v[k5]), "vwap", None))
        if (T - week_start(T)) >= VWAP_MIN_W and k5 >= 0 and wkey[k5] == week_start(T) and cs_w_v[k5] > 0:
            lv.append((float(cs_w_tpv[k5] / cs_w_v[k5]), "vwap", None))
        rb = np.floor(c / ROUND_STEP) * ROUND_STEP
        rb = rb - ROUND_STEP if rb == c else rb
        ra = np.ceil(c / ROUND_STEP) * ROUND_STEP
        ra = ra + ROUND_STEP if ra == c else ra
        lv += [(float(rb), "round", None), (float(ra), "round", None)]
        if j4 >= 0 and mid4.iat[j4] == mid4.iat[j4]:
            lv.append((float(mid4.iat[j4]), "bb4h", None))
        c_side = float(c_role[j]) if j < len(c_role) and c_role[j] == c_role[j] else c
        c4 = float(F4["c"].iat[j4]) if j4 >= 0 else c
        mine = [x for x in lv if (x[0] < c_side if side == "long" else x[0] > c_side)]
        mine4 = [x for x in mine if (x[0] < c4 if side == "long" else x[0] > c4)]
        r = {"T": T, "side": side, "close": c, "atr1h": a1, "f1_n_levels": len(mine), "f1_n_levels_v4h": len(mine4)}
        if keep_levels:                      # debug output for redteam.py R3 (all levels, both sides)
            r["levels"] = [(x[0], x[1]) for x in lv]
        near = mine[_near_np([x[0] for x in mine], [LAYERS.index(x[1]) for x in mine], side)] if mine else None
        if near is None or a1 != a1:
            r.update(f1_near_px=np.nan, f1_near_layer="none", f1_dist_atr=np.nan, f1_at_level=False,
                     f2_conf_obj=0, f2_conf_name=0, f2_age_h=np.nan, f2_touches=-1, f2_touch_cat="na")
        else:
            L = near[0]
            dist = sgn * (c - L) / a1
            zone = [x for x in mine if abs(x[0] - L) <= KZ * a1]
            r.update(f1_near_px=L, f1_near_layer=near[1], f1_dist_atr=dist, f1_at_level=bool(dist <= K_EVENT),
                     f2_conf_obj=len({x[1] for x in zone}), f2_conf_name=len({tg for x in zone for tg in TAGS[x[1]]}))
            if near[1] in DYNAMIC:
                r.update(f2_age_h=np.nan, f2_touches=-1, f2_touch_cat="dynamic")
            else:
                hi_j = len(hstart) - 1 if leak == "f2_future_touches" else j
                lo_j = max(0, j - ROUND_TOUCH_WIN + 1) if near[2] is None else int(np.searchsorted(hstart, near[2], "left"))
                seg = slice(lo_j, hi_j + 1)
                nt = int(np.count_nonzero((hl[seg] <= L) & (L <= hh[seg])))
                r.update(f2_age_h=np.nan if near[2] is None else (T - near[2]) / HOUR, f2_touches=nt, f2_touch_cat=("untested", "first", "retest")[min(nt, 2)])
        # F3
        pd_o = float(Dg["o"].iat[jd_f3]) if jd_f3 >= 0 else np.nan
        if T % DAY and k5 >= 0 and dkey[k5] == T // DAY:
            ph_, pl_ = float(part_h_all[k5]), float(part_l_all[k5])
        else:
            ph_, pl_ = c, c
        armA = bool(c > pd_o) if side == "long" else bool(c < pd_o)
        armB = bool(ph_ > pd_o) if side == "long" else bool(pl_ < pd_o)
        wmax = W_MAX_ATRD * ad / c * 100 if ad == ad else np.nan
        widths = {}
        for k in ("D", "12h", "8h"):
            jj = jd_f3 if k == "D" else int(idx[k][q])
            if jj < 0:
                widths[k] = np.nan; continue
            wv = ((c - agg[k]["l"].iat[jj]) if side == "long" else (agg[k]["h"].iat[jj] - c)) / c * 100
            widths[k] = float(wv) if wv > 0 else np.nan
        stf, ladder = "none", ["D", "12h", "8h"]
        while ladder and wmax == wmax:
            k = ladder.pop(0)
            wk_ = widths[k]
            if not (wk_ >= W_MIN):           # NaN or too tight: no refinement, no stop
                break
            if wk_ <= wmax:
                stf = k
                break
        r.update(f3_armed=armA, f3_armed_B=armB, f3_w_D=widths["D"], f3_w_12h=widths["12h"], f3_w_8h=widths["8h"],
                 f3_wmax=wmax, f3_stop_tf=stf, f3_stop_pct=widths[stf] if stf != "none" else np.nan,
                 f3_cost_R=COST_PCT / widths[stf] if stf != "none" else np.nan)
        # F4
        for k in TF4:
            jj = int(idx[k][q]) + (1 if leak == "f4_partial_candle" and int(idx[k][q]) + 1 < len(agg[k]) else 0)
            if jj >= 2:
                cat = cats[k][0].iat[jj]
                r[f"f4_{k}_cat"] = cat; r[f"f4_{k}_align"] = _ALIGN[side].get(cat, "none"); r[f"f4_{k}_eng_cls"] = cats[k][1].iat[jj]
            else:
                r[f"f4_{k}_cat"] = "na"; r[f"f4_{k}_align"] = "na"; r[f"f4_{k}_eng_cls"] = "na"
        # F5
        s1 = bb1.iat[j] if isinstance(bb1.iat[j], str) else "na"
        r.update(f5_1h=s1, f5_1h_cush=bb1c.iat[j], f5_4h=bb4.iat[j4] if j4 >= 0 else "na",
                 f5_veto=bool(s1 == ("walk_lower" if side == "short" else "walk_upper")),
                 f5_conf=bool(s1 == ("reenter_lower" if side == "long" else "reenter_upper")))
        # F6
        phA = phaseA_all[jw_ph] if jw_ph >= 0 else "na"
        if jd >= PH_D_RANGE - 1 and jd >= PH_D_RET:
            rr = float(r30.iat[jd])
            phB = "markup" if rr >= PH_D_THR else "markdown" if rr <= -PH_D_THR else \
                ("distribution" if pos90.iat[jd] >= 2 / 3 else "accumulation" if pos90.iat[jd] <= 1 / 3 else "balance")
        else:
            phB = "na"
        if j >= ER_N:
            intra = ("trend_up" if net.iat[j] > 0 else "trend_down") if er.iat[j] >= ER_THR else "balance"
        else:
            intra = "na"
        r.update(f6_phaseA=phA, f6_phaseB=phB, f6_intraday=intra)
        # F7
        pv = pct_vol[j]
        volreg = "na" if pv != pv else "low" if pv < 1 / 3 else "mid" if pv < 2 / 3 else "high"
        ps = pct_sq[j4] if j4 >= 0 else np.nan
        sq = "na" if ps != ps else "squeeze" if ps <= SQ_Q else "normal"
        hr_open = T - HOUR
        if j >= APPROACH_N and a1 == a1:
            ap = sgn * (hc[j - APPROACH_N] - hc[j]) / a1
            appr = "fast" if ap >= APPROACH_FAST else "slow" if ap > 0 else "away"
        else:
            appr = "na"
        if j >= 1:
            sw = any((hl[j] < x[0] and hc[j - 1] > x[0]) if side == "long" else (hh[j] > x[0] and hc[j - 1] < x[0]) for x in mine)
        else:
            sw = False
        if jd >= HTF_SMA - 1 and j4 >= HTF_SMA - 1:
            htf = str(int(sgn * (Dg["c"].iat[jd] - smaD[jd]) > 0) + int(sgn * (F4["c"].iat[j4] - sma4[j4]) > 0))
        else:
            htf = "na"
        fund = fund_all[q] if "fund_t" in bars else "na"
        r.update(f7_volreg=volreg, f7_squeeze=sq, f7_session=_SESSION_OF_HOUR[(hr_open % DAY) // HOUR],
                 f7_weekend="weekend" if ((hr_open // DAY) + 3) % 7 >= 5 else "weekday", f7_approach=appr,
                 f7_sweep=bool(sw), f7_htf_align=htf, f7_funding=fund)
        rows.append(r)
    return pd.DataFrame(rows).set_index("T", drop=False)


# ================================================================== comparison helper
FLOAT_KEYS = ("close", "atr1h", "f1_near_px", "f1_dist_atr", "f2_age_h", "f3_w_D", "f3_w_12h", "f3_w_8h", "f3_wmax",
              "f3_stop_pct", "f3_cost_R")


def row_diff(a, b, rtol=1e-9):
    """Keys where two factor rows differ (floats: relative tolerance rtol, NaN == NaN; everything else exact)."""
    bad = []
    for k in a:
        x, y = a[k], b[k]
        if k in FLOAT_KEYS:
            x, y = float(x), float(y)
            if x != x and y != y:
                continue
            if not (abs(x - y) <= rtol * max(1.0, abs(x), abs(y))):
                bad.append(k)
        elif k in ("f1_n_levels", "f1_n_levels_v4h", "f2_conf_obj", "f2_conf_name", "f2_touches", "T"):
            if int(x) != int(y):
                bad.append(k)
        elif isinstance(x, (bool, np.bool_)) or isinstance(y, (bool, np.bool_)):
            if bool(x) != bool(y):
                bad.append(k)
        elif str(x) != str(y):
            bad.append(k)
    return bad


# ================================================================== DEV loader (real data; never used by the tests)
KLINE_DIR = Path("F:/MTS/data/tom_raw/klines")
FUND_DIR = Path("F:/MTS/data/candle_close_dev_2022_2024")
CACHE = Path("C:/Users/E-NGIN~1/AppData/Local/Temp/claude/context_factors_cache")


def _months():
    for y in (2022, 2023, 2024):
        for m in range(1, 13):
            if y == 2024 and m > 6:
                return
            yield f"{y}-{m:02d}"


def load_dev_5m():
    """5m bars (dict of arrays) from the 1m archive, bar open 2022-01-01 .. 2024-06-30 only (FORMULAS 8 aggregation)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    cp = CACHE / "btcusdt_5m_dev.npz"
    if cp.exists():
        z = np.load(cp)
        return {k: z[k] for k in z.files}
    parts = []
    for ym in _months():
        f = KLINE_DIR / f"BTCUSDT-1m-{ym}.csv"
        first = f.open().readline()
        df = pd.read_csv(f, header=0 if first.startswith("open_time") else None, usecols=range(6))
        df.columns = ["ot", "o", "h", "l", "c", "v"]
        parts.append(df)
    m = pd.concat(parts, ignore_index=True).drop_duplicates("ot").sort_values("ot")
    m = m[(m["ot"] >= DEV_START_MS) & (m["ot"] < DEV_END_MS)]
    if len(m) and int(m["ot"].max()) >= DEV_END_MS:
        raise ValueError("VALIDATION bar in the DEV load")
    k = (m["ot"].to_numpy(np.int64) // MIN5) * MIN5
    a = _agg_frame(m.assign(key=k), "key")
    out = {"ot": a.index.to_numpy(np.int64), "o": a["o"].to_numpy(), "h": a["h"].to_numpy(), "l": a["l"].to_numpy(),
           "c": a["c"].to_numpy(), "v": a["v"].to_numpy()}
    np.savez(cp, **out)
    return out


def load_funding():
    import zipfile
    rows = []
    for ym in _months():
        z = zipfile.ZipFile(FUND_DIR / f"BTCUSDT-fundingRate-{ym}.zip")
        rows.append(pd.read_csv(z.open(z.namelist()[0])))
    f = pd.concat(rows, ignore_index=True).sort_values("calc_time")
    f = f[f["calc_time"] < DEV_END_MS]
    return f["calc_time"].to_numpy(np.int64), f["last_funding_rate"].to_numpy(float)


def load_dev():
    b = load_dev_5m()
    b["fund_t"], b["fund_r"] = load_funding()
    return b


def decision_index(bars, T):
    """t (5m index) whose bar closes at T; -1 if that bar is missing."""
    i = int(np.searchsorted(bars["ot"], T - MIN5, "left"))
    return i if i < len(bars["ot"]) and int(bars["ot"][i]) == T - MIN5 else -1
