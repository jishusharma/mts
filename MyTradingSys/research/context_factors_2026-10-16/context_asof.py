"""Point-in-time CONTEXT FACTORS for backtesting (DEV only, BTCUSDT 1m klines). Two independent builds of every factor:

  * REPLAY  (`Replay`): a state machine that is fed one 1m bar at a time and has only ever seen bars[0..t].
  * VEC     (`VecTables`): an all-at-once build on the full arrays with explicit "last closed bucket" indexing.

`context_at(bars, t, side, impl)` returns the same dict from either build. Decision time = the close of 1m bar t
(open_time + 60 s). Level fields (F1/F2) refresh at 1h closes (the decision grid, t % 60 == 59); candle, ladder,
Bollinger, phase and the F7 fields are as of bar t itself.

Every parameter is labelled in CONTEXT_FACTORS_SPEC.md (SOURCED file:line / operator quote, or OURS). No outcome
column exists anywhere in this module. Any bar opening at/after 2024-07-01 is refused by the loader (VALIDATION and
HOLDOUT are sealed).

Bucket convention (FORMULAS.md s.8, closed bars only): a bucket of period P minutes with offset `off` (0 for 4h/8h/12h/1d,
Monday 2022-01-03 00:00 UTC = minute 2880 for 1w) covers 1m bars [off + k P, off + (k+1) P). At bar t:
  cur_k    = (t - off) // P                      the bucket holding bar t ("partial" candle, complete at its last bar)
  complete = (t + 1 - off) % P == 0              bar t is the bucket's last bar
  last closed candle (F4, F5, ATR, pivots) = cur_k if complete else cur_k - 1
  ledger "prior" day/week and ladder "prior" candle (F1, F3) = the same last closed bucket (PRIOR_RULE = "last_closed").
  Red-team finding RT-1 (ANGLES.md): the first draft used cur_k - 1 for the ledger and the ladder, which at a bucket-close
  grid point (23:59 for the day) ignores the candle that has just closed although the fill happens at the open of the
  next bar, i.e. inside the next bucket. PRIOR_RULE = "cur_k_minus_1" keeps the old rule for the count in trials.csv.
"""
import csv
import glob
import os
from collections import deque

import numpy as np

TS0 = 1640995200000            # 2022-01-01 00:00 UTC (Saturday), bar index i opens at TS0 + 60000 i
DEV_END_MS = 1719792000000     # 2024-07-01 00:00 UTC
MS = 60000
NDAYS_DEV = 912
N_DEV = NDAYS_DEV * 1440
WEEK_OFF = 2880                # minutes from TS0 to Monday 2022-01-03 00:00 UTC
ARCH = "F:/MTS/data/tom_raw/klines"
FUND_ARCH = "F:/MTS/Dumps/backtest/raw/fundingRate"

TF_P = {"1h": 60, "4h": 240, "8h": 480, "12h": 720, "1d": 1440, "1w": 10080}
TF_OFF = {"1h": 0, "4h": 0, "8h": 0, "12h": 0, "1d": 0, "1w": WEEK_OFF}
CANDLE_TFS = ("4h", "8h", "12h", "1d")

# ---- parameters (labels in CONTEXT_FACTORS_SPEC.md) ----
ATR_N = 14                 # plain-SMA ATR on closed 4h bars (FORMULAS.md s.12: SMA, not Wilder)
BB_N, BB_K = 20, 2.0       # SMA20 of closes +/- 2 population SD (bollinger SOURCES.md s.5 "Bands")
WALK_N = 3                 # band walk: >= 3 consecutive closes at/beyond the band (SOURCES.md s.1 "three or more", OURS N)
K_ZONE = 0.5               # confluence zone = K_ZONE x ATR14(4h) (OURS); K_ZONE_ALT counted only
K_ZONE_ALT = 1.0
W_LADDER_PCT = 2.5         # ladder: a stop wider than W % of price is "too much" (OURS)
STOP_FLOOR_PCT = 0.56      # cost 0.14 % <= 0.25 R  =>  stop >= 0.56 % (OURS tie to cost in R)
PIVOT_N = 3                # fractal width on closed 4h (Krown zones) and closed 1d (phase A) bars (OURS)
KROWN_MAX_AGE = 360        # closed 4h bars (60 days) a Krown pivot stays on the map (OURS)
VP_BIN = 10.0              # volume-profile bin width USD (FORMULAS.md 18.1)
VA_PCT = 0.70              # value area (FORMULAS.md 18.1, Tom "70 % of the trades")
ROUND_STEP = 1000.0        # round numbers (opr_weekly_low_round_sweep PRE_REG: round-1000)
RET30_THR = 0.075          # phase B: tom_bt.trend_tag threshold on the 30-day return (backtest/tom_bt.py:270-271)
SMA_PHASE = 50             # phase B: range split by close vs SMA50 of daily closes (OURS)
BAL_K = 1.5                # intraday balance: 24h range <= BAL_K x ATR14(4h) (OURS)
PCT_WIN = 180              # trailing window (closed 4h bars = 30 days) for ATR terciles and the squeeze percentile (OURS)
SQUEEZE_PCT = 10           # bandwidth at/below its 10th trailing percentile (SOURCES.md s.5 "Squeeze")
APPROACH_BARS = 4          # approach speed over the last 4 closed 1h bars (OURS)
APPROACH_FAST = 1.0        # >= 1 ATR14(4h) toward the level = fast (OURS)
SWEEP_BARS = 6             # liquidity sweep window: last 6 closed 1h bars (OURS)
FUND_HIGH = 0.0001         # Binance baseline funding rate per 8h (SOURCED: exchange default); above it = high (OURS)
WEEKLY_TREND_BARS = 4      # HTF alignment: weekly close vs 4 weeks earlier (OURS)
TOUCH_LOOKBACK = 720       # touch count over at most the last 720 closed 1h bars (30 days) (OURS)

SOURCES = ("prior_d_hl", "prior_w_hl", "fabio_vp_day", "tom_vp_week", "krown_zone", "malkan_bb_d",
           "vwap_session", "vwap_week", "round_1k")

PLANT = {}   # name -> True plants that look-ahead in the VEC build (tests only; see leak_plants.py)
PRIOR_RULE = "last_closed"   # or "cur_k_minus_1" (RT-1 alternative, counted only); honoured by BOTH builds


# ================================================================= data
def dev_files():
    out = []
    for y, m in [(2022, i) for i in range(1, 13)] + [(2023, i) for i in range(1, 13)] + [(2024, i) for i in range(1, 7)]:
        out.append(os.path.join(ARCH, f"BTCUSDT-1m-{y}-{m:02d}.csv"))
    return out


def load_dev(files=None, cache=None):
    """1m arrays indexed by minutes since TS0 (O,H,L,C,V,TBV), DEV only. Refuses any bar at/after 2024-07-01."""
    if cache and os.path.exists(cache):
        z = np.load(cache)
        return {k: z[k] for k in ("O", "H", "L", "C", "V", "TBV")}
    files = files or dev_files()
    n = N_DEV
    A = {k: np.full(n, np.nan) for k in ("O", "H", "L", "C", "V", "TBV")}
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                if t >= DEV_END_MS:
                    raise ValueError(f"bar {t} >= 2024-07-01 refused (VALIDATION/HOLDOUT are sealed): {f}")
                i = (t - TS0) // MS
                if 0 <= i < n:
                    A["O"][i], A["H"][i], A["L"][i], A["C"][i] = float(r[1]), float(r[2]), float(r[3]), float(r[4])
                    A["V"][i], A["TBV"][i] = float(r[5]), float(r[9])
    if cache:
        np.savez(cache, **A)
    return A


def load_funding(files=None):
    """(calc_time_ms, rate) sorted; DEV months only. Known at calc_time (the settlement instant)."""
    files = files or sorted(glob.glob(os.path.join(FUND_ARCH, "BTCUSDT-fundingRate-202[234]-*.csv")))
    rows = []
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t >= DEV_END_MS:
                    continue
                rows.append((t, float(r[2])))
    rows.sort()
    return np.array([r[0] for r in rows], dtype=np.int64), np.array([r[1] for r in rows])


def slice_bars(bars, n):
    """bars[0..n-1] (the truncation used by the tests)."""
    return {k: v[:n] for k, v in bars.items()}


# ================================================================= shared pure helpers (used by BOTH builds on
# single candles; no time indexing happens here, so sharing them cannot hide a look-ahead)
def candle_patterns(a, b, c):
    """Patterns of the last closed candle a given the two before it (b = previous, c = before b). Each candle is
    (o, h, l, c). Returns a sorted tuple of names; OURS definitions with SOURCED anchors in the spec."""
    out = []
    ao, ah, al, ac = a
    bo, bh, bl, bc = b
    a_green, a_red = ac > ao, ac < ao
    b_green, b_red = bc > bo, bc < bo
    if b_red and a_green and ac > bo and ao <= bc:
        out.append("bull_engulf")
    if b_green and a_red and ac < bo and ao >= bc:
        out.append("bear_engulf")
    rng = ah - al
    if rng > 0:
        body = abs(ac - ao)
        lower = min(ao, ac) - al
        upper = ah - max(ao, ac)
        if lower >= 0.6 * rng and body <= 0.3 * rng:
            out.append("bull_pin")
        if upper >= 0.6 * rng and body <= 0.3 * rng:
            out.append("bear_pin")
    if ah < bh and al > bl:
        out.append("inside")
    if ah > bh and al < bl:
        out.append("outside")
    if c is not None:
        co, ch, cl, cc = c
        if a_green and b_green and cc > co:
            out.append("three_up")
        if a_red and b_red and cc < co:
            out.append("three_down")
    return tuple(sorted(out)) if out else ("none",)


def pat_str(p):
    return "|".join(p)


def bb_state_from(closes, uppers, lowers, bws, n_walk=WALK_N):
    """Bollinger state of the last closed bar given lists aligned at the end (index -1 = last closed bar).
    closes/uppers/lowers/bws need >= n_walk + 1 entries. OURS state names; the walk needs n_walk consecutive closes
    at/beyond one band AND bandwidth wider than n_walk bars earlier."""
    c, u, l = closes[-1], uppers[-1], lowers[-1]
    pc, pu, pl = closes[-2], uppers[-2], lowers[-2]
    above = c >= u
    below = c <= l
    p_above = pc >= pu
    p_below = pc <= pl
    if not above and not below:
        if p_below:
            return "reenter_from_lower"
        if p_above:
            return "reenter_from_upper"
        return "inside"
    # at/beyond a band
    run_ok = True
    for k in range(1, n_walk + 1):
        ck, uk, lk = closes[-k], uppers[-k], lowers[-k]
        if above and not (ck >= uk):
            run_ok = False
        if below and not (ck <= lk):
            run_ok = False
    expanding = bws[-1] > bws[-1 - n_walk]
    if run_ok and expanding:
        return "walk_up" if above else "walk_down"
    if above and not p_above:
        return "break_up"
    if below and not p_below:
        return "break_down"
    return "outside_up" if above else "outside_down"


def ladder(side, price, prior_d, prior_12, prior_8):
    """The operator's stop ladder. prior_x = (o, h, l, c) of the candle before the one holding bar t, or None.
    Long: stop below the prior low; short: above the prior high. Returns (rung, stop_pct, cost_r_taker, below_floor,
    stop_d_pct, stop_12_pct, stop_8_pct); stop_pct is NaN when no rung is valid."""
    def w(cndl):
        if cndl is None:
            return float("nan")
        o, h, l, c = cndl
        if side == "long":
            return (price - l) / price * 100.0 if l < price else float("nan")
        return (h - price) / price * 100.0 if h > price else float("nan")
    sd, s12, s8 = w(prior_d), w(prior_12), w(prior_8)
    valid = [(name, s) for name, s in (("1d", sd), ("12h", s12), ("8h", s8)) if s == s]
    under = [x for x in valid if x[1] <= W_LADDER_PCT]
    if under:
        rung, stop = under[0]                      # the first rung (D, then 12h, then 8h) that is not "too much"
    elif valid:
        rung, stop = min(valid, key=lambda x: x[1])   # every rung too wide: the tightest valid one
    else:
        rung, stop = "none", float("nan")
    cost_r = 0.14 / stop if stop == stop and stop > 0 else float("nan")
    below = bool(stop == stop and stop < STOP_FLOOR_PCT)
    return rung, stop, cost_r, below, sd, s12, s8


def ladder_cond(side, price, prior_d, partial_d=None):
    """Operator: 'If a daily candle has moved past the opening of the previous daily candle ...'. Primary (close rule):
    long = the current close is above the prior daily open; short = below it. Alternative (touch rule, counted only,
    partial_d given): the partial daily candle's high (long) / low (short) has moved past the prior open."""
    if prior_d is None:
        return False
    if partial_d is not None:
        return bool(partial_d[1] > prior_d[0]) if side == "long" else bool(partial_d[2] < prior_d[0])
    return bool(price > prior_d[0]) if side == "long" else bool(price < prior_d[0])


def session_of(t):
    h = (t % 1440) // 60
    return "asia" if h < 8 else "london" if h < 13 else "ny" if h < 21 else "late"


def is_weekend(t):
    # TS0 is a Saturday: day index d -> weekday (d + 5) % 7 with Monday = 0
    return ((t // 1440) + 5) % 7 >= 5


def vol_regime_of(vals_sorted_window, x):
    """Tercile of x within the trailing window values (inclusive); OURS."""
    n = len(vals_sorted_window)
    rank = np.searchsorted(vals_sorted_window, x, side="right")   # count <= x
    f = rank / n
    return "low" if f <= 1.0 / 3 else "mid" if f <= 2.0 / 3 else "high"


def value_area(bins_lo_k, vol):
    """FORMULAS.md 18.1 value area on a dense bin array `vol` whose first bin is index k = bins_lo_k.
    Returns (poc_price, val, vah) or None."""
    tot = float(vol.sum()) if hasattr(vol, "sum") else float(sum(vol))
    if tot <= 0:
        return None
    n = len(vol)
    kp = int(np.argmax(vol))                 # lowest bin holding the maximum (argmax keeps the first)
    lo = hi = kp
    acc = float(vol[kp])
    target = VA_PCT * tot
    while acc < target and (lo > 0 or hi < n - 1):
        vl = float(vol[lo - 1]) if lo > 0 else -1.0
        vh = float(vol[hi + 1]) if hi < n - 1 else -1.0
        if vl >= vh and lo > 0:
            lo -= 1
            acc += vl
        elif hi < n - 1:
            hi += 1
            acc += vh
        else:
            lo -= 1
            acc += vl
    w = VP_BIN
    return ((bins_lo_k + kp) * w + w / 2, (bins_lo_k + lo) * w, (bins_lo_k + hi + 1) * w)


def profile_replay(L, H, V):
    """Pure-Python volume profile (18.1, uniform spread over [l, h]) of lists L, H, V -> (poc, val, vah)."""
    w = VP_BIN
    k0 = int(np.floor(min(L) / w))
    k1 = int(np.floor(max(H) / w))
    vol = [0.0] * (k1 - k0 + 1)
    for l, h, v in zip(L, H, V):
        if h > l:
            ka, kb = int(np.floor(l / w)), int(np.floor(h / w))
            for k in range(ka, kb + 1):
                ov = min(h, (k + 1) * w) - max(l, k * w)
                if ov > 0:
                    vol[k - k0] += v * ov / (h - l)
        else:
            vol[int(np.floor(l / w)) - k0] += v
    return value_area(k0, np.array(vol))


def profile_vec(L, H, V):
    """numpy volume profile of arrays L, H, V (same definition as profile_replay, different code path)."""
    w = VP_BIN
    L = np.asarray(L, float)
    H = np.asarray(H, float)
    V = np.asarray(V, float)
    k0 = int(np.floor(L.min() / w))
    k1 = int(np.floor(H.max() / w))
    ka = np.floor(L / w).astype(np.int64)
    kb = np.floor(H / w).astype(np.int64)
    cnt = kb - ka + 1
    rep_l = np.repeat(L, cnt)
    rep_h = np.repeat(H, cnt)
    rep_v = np.repeat(V, cnt)
    rep_ka = np.repeat(ka, cnt)
    offs = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
    k = rep_ka + offs
    flat = rep_h <= rep_l
    ov = np.minimum(rep_h, (k + 1) * w) - np.maximum(rep_l, k * w)
    share = np.where(flat, rep_v, np.where(ov > 0, rep_v * ov / np.where(flat, 1.0, rep_h - rep_l), 0.0))
    vol = np.zeros(k1 - k0 + 1)
    np.add.at(vol, k - k0, share)
    return value_area(k0, vol)


# ================================================================= level ledger helpers (both builds)
def nearest_side(levels, side, price, c1h_role, c4h_role):
    """levels: list of (price, source, avail_min). Role = support iff the last closed 1h close > level (rule A) or
    the last closed 4h close > level (rule B, counted only). Long: supports strictly below price; short: resistances
    strictly above. Returns dict of nearest-level fields for rule A and the rule-B source."""
    def pick(cref):
        best = None
        for lp, src, av in levels:
            if side == "long":
                ok = (cref > lp) and (lp < price)
            else:
                ok = (cref < lp) and (lp > price)
            if not ok:
                continue
            d = price - lp if side == "long" else lp - price
            if best is None or d < best[0] or (d == best[0] and (src, av) < (best[2], best[3])):
                best = (d, lp, src, av)
        return best
    a = pick(c1h_role)
    b = pick(c4h_role)
    return a, b


def layers_in_zone(levels, side, price, cref, width):
    """Distinct source layers with a level in (price - width, price) for a long, (price, price + width) for a short,
    with the role rule (last closed close on the far side)."""
    srcs = set()
    for lp, src, av in levels:
        if side == "long":
            ok = (cref > lp) and (lp < price) and (round(price - lp, 6) <= round(width, 6))
        else:
            ok = (cref < lp) and (lp > price) and (round(lp - price, 6) <= round(width, 6))
        if ok:
            srcs.add(src)
    return len(srcs)


# ================================================================= VEC build
class VecTables:
    """All factors at once from the full arrays. Everything indexed through 'last closed bucket' tables."""

    def __init__(self, bars, funding=None):
        self.b = bars
        self.n = len(bars["C"])
        self.tf = {}
        for tf, P in TF_P.items():
            self.tf[tf] = self._closed(tf, P, TF_OFF[tf])
        self._partials()
        self._atr()
        self._bb("4h")
        self._bb("1d")
        self._pivots_4h()
        self._pivots_1d()
        self._profiles()
        self._vwap()
        self._phase()
        self._f7()
        self.fund_t, self.fund_r = funding if funding is not None else (np.array([], dtype=np.int64), np.array([]))

    # ---- buckets
    def _closed(self, tf, P, off):
        n = self.n
        K = (n - off) // P                      # complete buckets
        if K <= 0:
            z = np.zeros(0)
            return {"K": 0, "O": z, "H": z, "L": z, "C": z, "V": z, "start": np.zeros(0, dtype=np.int64)}
        s = off
        e = off + K * P
        O = self.b["O"][s:e].reshape(K, P)
        H = self.b["H"][s:e].reshape(K, P)
        L = self.b["L"][s:e].reshape(K, P)
        C = self.b["C"][s:e].reshape(K, P)
        V = self.b["V"][s:e].reshape(K, P)
        return {"K": K, "O": O[:, 0].copy(), "H": H.max(1), "L": L.min(1), "C": C[:, -1].copy(), "V": V.sum(1),
                "start": off + np.arange(K) * P}

    def _partials(self):
        """Partial (developing) candle at every 1m bar for the candle TFs: open, running high/low, close."""
        self.part = {}
        n = self.n
        for tf in CANDLE_TFS:
            P, off = TF_P[tf], TF_OFF[tf]
            K = (n - off + P - 1) // P
            pad = off + K * P - n
            H = np.concatenate((self.b["H"][off:], np.full(pad, np.nan))).reshape(K, P)
            L = np.concatenate((self.b["L"][off:], np.full(pad, np.nan))).reshape(K, P)
            O = np.concatenate((self.b["O"][off:], np.full(pad, np.nan))).reshape(K, P)
            ph = np.maximum.accumulate(H, axis=1).reshape(-1)[:n - off]
            pl = np.minimum.accumulate(L, axis=1).reshape(-1)[:n - off]
            po = np.repeat(O[:, 0], P)[:n - off]
            self.part[tf] = {"o": np.concatenate((np.full(off, np.nan), po)),
                             "h": np.concatenate((np.full(off, np.nan), ph)),
                             "l": np.concatenate((np.full(off, np.nan), pl))}

    @staticmethod
    def cur_k(t, tf):
        return (t - TF_OFF[tf]) // TF_P[tf]

    @staticmethod
    def complete(t, tf):
        return (t + 1 - TF_OFF[tf]) % TF_P[tf] == 0

    def prior_k(self, t, tf):
        """The ledger/ladder 'prior' bucket at bar t (PRIOR_RULE)."""
        if PRIOR_RULE == "cur_k_minus_1":
            return self.cur_k(t, tf) - 1
        return self.last_closed(t, tf)

    def last_closed(self, t, tf):
        k = self.cur_k(t, tf)
        j = k if self.complete(t, tf) else k - 1
        if PLANT.get("candle_partial"):
            j = k                       # PLANT: treats the bucket holding bar t as closed (its final OHLC leaks)
        return j if 0 <= j < self.tf[tf]["K"] else -1

    def candle(self, tf, j):
        T = self.tf[tf]
        return (T["O"][j], T["H"][j], T["L"][j], T["C"][j])

    # ---- ATR14 on closed 4h bars (index j = the bar the value is valid from, inclusive)
    def _atr(self):
        T = self.tf["4h"]
        K = T["K"]
        atr = np.full(K, np.nan)
        if K > ATR_N:
            tr = np.maximum(T["H"][1:] - T["L"][1:], np.maximum(abs(T["H"][1:] - T["C"][:-1]), abs(T["L"][1:] - T["C"][:-1])))
            sma = np.lib.stride_tricks.sliding_window_view(tr, ATR_N).mean(axis=1)   # sma[m] = mean tr[m..m+13] = bars m+1..m+14
            atr[ATR_N:] = sma
        self.atr4 = atr

    # ---- Bollinger on closed bars of tf
    def _bb(self, tf):
        T = self.tf[tf]
        K = T["K"]
        C = T["C"]
        mid = np.full(K, np.nan)
        sd = np.full(K, np.nan)
        if K >= BB_N:
            # two-pass per window (BUG-1, angle a: the cumsum-of-squares form lost ~8 digits at BTC price levels)
            win = np.lib.stride_tricks.sliding_window_view(C, BB_N)
            m = win.mean(axis=1)
            v = ((win - m[:, None]) ** 2).mean(axis=1)
            mid[BB_N - 1:] = m
            sd[BB_N - 1:] = np.sqrt(v)
        up = mid + BB_K * sd
        lo = mid - BB_K * sd
        bw = (up - lo) / mid
        pctb = np.where(up > lo, (C - lo) / (up - lo), np.nan)
        state = np.array(["na"] * K, dtype=object)
        for j in range(BB_N - 1 + WALK_N, K):
            closes = [C[j - k] for k in range(WALK_N, -1, -1)]
            ups = [up[j - k] for k in range(WALK_N, -1, -1)]
            los = [lo[j - k] for k in range(WALK_N, -1, -1)]
            bws = [bw[j - k] for k in range(WALK_N, -1, -1)]
            state[j] = bb_state_from(closes, ups, los, bws)
        setattr(self, "bb_" + tf, {"mid": mid, "up": up, "lo": lo, "bw": bw, "pctb": pctb, "state": state})

    # ---- fractal pivots on closed 4h bars -> Krown zone levels (price = wick extreme, avail = bar i+n closed)
    def _pivots_4h(self):
        T = self.tf["4h"]
        K = T["K"]
        n = PIVOT_N
        self.piv4 = []    # (closed-4h index i, kind, price, avail_j)
        if K < 2 * n + 1:
            return
        H, L = T["H"], T["L"]
        hi = np.ones(K, bool)
        lo = np.ones(K, bool)
        for k in range(1, n + 1):
            hi[n:K - n] &= (H[n:K - n] > H[n - k:K - n - k]) & (H[n:K - n] > H[n + k:K - n + k])
            lo[n:K - n] &= (L[n:K - n] < L[n - k:K - n - k]) & (L[n:K - n] < L[n + k:K - n + k])
        hi[:n] = lo[:n] = False
        hi[K - n:] = lo[K - n:] = False
        for i in np.nonzero(hi)[0]:
            self.piv4.append((int(i), "H", float(H[i]), int(i) + n - (1 if PLANT.get("pivot_unconfirmed") else 0)))
        for i in np.nonzero(lo)[0]:
            self.piv4.append((int(i), "L", float(L[i]), int(i) + n - (1 if PLANT.get("pivot_unconfirmed") else 0)))
        self.piv4.sort(key=lambda r: (r[3], r[0], r[1]))

    # ---- fractal pivots on closed daily bars -> phase A per closed daily index j
    def _pivots_1d(self):
        T = self.tf["1d"]
        K = T["K"]
        n = PIVOT_N
        H, L = T["H"], T["L"]
        piv = []
        for i in range(n, K - n):
            if all(H[i] > H[i - k] and H[i] > H[i + k] for k in range(1, n + 1)):
                piv.append((i + n, i, "H", H[i]))
            if all(L[i] < L[i - k] and L[i] < L[i + k] for k in range(1, n + 1)):
                piv.append((i + n, i, "L", L[i]))
        piv.sort()
        trend = np.array(["range"] * K, dtype=object)
        phase = np.array(["na"] * K, dtype=object)
        hs, ls = [], []
        p = 0
        last_dir = None
        for j in range(K):
            while p < len(piv) and piv[p][0] <= j:
                _, i, kind, px = piv[p]
                (hs if kind == "H" else ls).append(px)
                p += 1
            if len(hs) >= 2 and len(ls) >= 2:
                up = hs[-1] > hs[-2] and ls[-1] > ls[-2]
                dn = hs[-1] < hs[-2] and ls[-1] < ls[-2]
                st = "up" if up else "down" if dn else "range"
                trend[j] = st
                if st != "range":
                    last_dir = st
                    phase[j] = "markup" if st == "up" else "markdown"
                else:
                    phase[j] = "distribution" if last_dir == "up" else "accumulation" if last_dir == "down" else "range_initial"
        self.phase_a = phase
        self.trend_a = trend

    # ---- prior-day / prior-week profiles
    def _profiles(self):
        b = self.b
        self.vp_day = {}
        T = self.tf["1d"]
        for k in range(T["K"]):
            s = k * 1440
            self.vp_day[k] = profile_vec(b["L"][s:s + 1440], b["H"][s:s + 1440], b["V"][s:s + 1440])
        self.vp_week = {}
        T = self.tf["1w"]
        for k in range(T["K"]):
            s = WEEK_OFF + k * 10080
            self.vp_week[k] = profile_vec(b["L"][s:s + 10080], b["H"][s:s + 10080], b["V"][s:s + 10080])

    # ---- developing VWAPs (session 00:00 UTC, week Monday 00:00 UTC), value at every 1m bar
    def _vwap(self):
        b = self.b
        tp = (b["H"] + b["L"] + b["C"]) / 3.0
        pv = tp * b["V"]
        n = self.n

        def dev(off, P):
            if n <= off:
                return np.full(n, np.nan)
            K = (n - off + P - 1) // P
            pad = off + K * P - n
            a = np.concatenate((pv[off:], np.zeros(pad))).reshape(K, P)
            v = np.concatenate((b["V"][off:], np.zeros(pad))).reshape(K, P)
            ca = np.cumsum(a, axis=1).reshape(-1)[:n - off]
            cv = np.cumsum(v, axis=1).reshape(-1)[:n - off]
            out = np.where(cv > 0, ca / np.where(cv > 0, cv, 1.0), np.nan)
            return np.concatenate((np.full(off, np.nan), out))
        self.vwap_s = dev(0, 1440)
        self.vwap_w = dev(WEEK_OFF, 10080)

    # ---- phase B (daily closes) and weekly trend
    def _phase(self):
        T = self.tf["1d"]
        K = T["K"]
        C = T["C"]
        ph = np.array(["na"] * K, dtype=object)
        if K > SMA_PHASE:
            cs = np.concatenate(([0.0], np.cumsum(C)))
            sma = np.full(K, np.nan)
            sma[SMA_PHASE - 1:] = (cs[SMA_PHASE:] - cs[:-SMA_PHASE]) / SMA_PHASE
            for j in range(max(30, SMA_PHASE - 1), K):
                r = C[j] / C[j - 30] - 1.0
                if r >= RET30_THR:
                    ph[j] = "markup"
                elif r <= -RET30_THR:
                    ph[j] = "markdown"
                else:
                    ph[j] = "distribution" if C[j] > sma[j] else "accumulation"
        self.phase_b = ph
        W = self.tf["1w"]
        wt = np.array(["na"] * W["K"], dtype=object)
        for j in range(WEEKLY_TREND_BARS, W["K"]):
            wt[j] = "up" if W["C"][j] > W["C"][j - WEEKLY_TREND_BARS] else "down"
        self.weekly_trend = wt

    # ---- F7 per closed 4h bar: ATR tercile and squeeze over the trailing PCT_WIN bars (inclusive)
    def _f7(self):
        K = self.tf["4h"]["K"]
        self.vol_reg = np.array(["na"] * K, dtype=object)
        self.squeeze = np.zeros(K, bool)
        bw = self.bb_4h["bw"]
        for j in range(K):
            if j - PCT_WIN + 1 < ATR_N or not (self.atr4[j] == self.atr4[j]):
                continue
            if PLANT.get("pct_fullsample"):
                win = np.sort(self.atr4[ATR_N:])          # PLANT: full-sample terciles
            else:
                win = np.sort(self.atr4[j - PCT_WIN + 1:j + 1])
            self.vol_reg[j] = vol_regime_of(win, self.atr4[j])
            if bw[j] == bw[j]:
                wb = bw[j - PCT_WIN + 1:j + 1]
                wb = wb[wb == wb]
                if len(wb) == PCT_WIN:
                    self.squeeze[j] = bw[j] <= np.percentile(wb, SQUEEZE_PCT)

    # ---- level ledger at a 1h-grid point t (levels refresh at 1h closes)
    def levels_at(self, t):
        """List of (price, source, avail_min) available at bar t (t on the 1h grid)."""
        out = []
        jd = self.prior_k(t, "1d")
        if jd >= 0:
            T = self.tf["1d"]
            av = (jd + 1) * 1440 - 1
            out.append((float(T["H"][jd]), "prior_d_hl", av))
            out.append((float(T["L"][jd]), "prior_d_hl", av))
            vp = self.vp_day.get(jd + (1 if PLANT.get("vp_include_today") else 0))
            if vp:
                for px in vp:
                    out.append((float(px), "fabio_vp_day", av))
        jw = self.prior_k(t, "1w")
        if jw >= 0:
            T = self.tf["1w"]
            av = WEEK_OFF + (jw + 1) * 10080 - 1
            out.append((float(T["H"][jw]), "prior_w_hl", av))
            out.append((float(T["L"][jw]), "prior_w_hl", av))
            vp = self.vp_week.get(jw)
            if vp:
                for px in vp:
                    out.append((float(px), "tom_vp_week", av))
        j4 = self.last_closed(t, "4h")
        if j4 >= 0:
            for i, kind, px, avj in self.piv4:
                if avj > j4:
                    break
                if j4 - i > KROWN_MAX_AGE:
                    continue
                out.append((px, "krown_zone", (avj + 1) * 240 - 1))
        jdc = self.last_closed(t, "1d")
        if jdc >= 0 and self.bb_1d["mid"][jdc] == self.bb_1d["mid"][jdc]:
            av = (jdc + 1) * 1440 - 1
            for px in (self.bb_1d["mid"][jdc], self.bb_1d["up"][jdc], self.bb_1d["lo"][jdc]):
                out.append((float(px), "malkan_bb_d", av))
        if self.vwap_s[t] == self.vwap_s[t]:
            out.append((float(self.vwap_s[t]), "vwap_session", (t // 1440) * 1440))
        if self.vwap_w[t] == self.vwap_w[t]:
            out.append((float(self.vwap_w[t]), "vwap_week", WEEK_OFF + ((t - WEEK_OFF) // 10080) * 10080))
        price = float(self.b["C"][t])
        below = np.floor(price / ROUND_STEP) * ROUND_STEP
        if below == price:
            below -= ROUND_STEP
        out.append((float(below), "round_1k", 0))
        out.append((float(below + ROUND_STEP), "round_1k", 0))
        if price == below + ROUND_STEP:
            out.append((float(below + 2 * ROUND_STEP), "round_1k", 0))
        return out

    def touches_before(self, level, avail_min, t):
        """Completed 1h bars from avail to the bar before the one holding t whose range covers the level."""
        T = self.tf["1h"]
        j1 = t // 60                                   # the current 1h bar (excluded)
        j0 = max(0, (avail_min + 1 + 59) // 60, j1 - TOUCH_LOOKBACK)   # first 1h bar after avail, capped lookback
        if j1 <= j0:
            return 0
        H, L = T["H"][j0:j1], T["L"][j0:j1]
        return int(np.count_nonzero((L <= level) & (level <= H)))

    def side_fields(self, t, side):
        price = float(self.b["C"][t])
        T1 = self.tf["1h"]
        j1 = self.last_closed(t, "1h")
        c1 = float(T1["C"][j1]) if j1 >= 0 else float("nan")
        j4 = self.last_closed(t, "4h")
        c4 = float(self.tf["4h"]["C"][j4]) if j4 >= 0 else float("nan")
        atr = float(self.atr4[j4]) if j4 >= 0 else float("nan")
        levels = self.levels_at(t)
        a, bsel = nearest_side(levels, side, price, c1, c4)
        f = {"n_levels": len(levels), "n_krown": sum(1 for lv in levels if lv[1] == "krown_zone")}   # ledger size (counts)
        if a is None or atr != atr:
            f.update(near_price=float("nan"), near_src="none", near_dist_atr=float("nan"), level_age_h=float("nan"),
                     touch_count=-1, first_touch=False, at_level=False, n_layers=0, n_layers_k1=0, n_layers_4hrule=0)
        else:
            d, lp, src, av = a
            f["near_price"] = lp
            f["near_src"] = src
            f["near_dist_atr"] = d / atr
            f["level_age_h"] = (t + 1 - av) / 60.0
            tc = self.touches_before(lp, av, t)
            f["touch_count"] = tc
            f["first_touch"] = tc == 0
            f["at_level"] = bool(round(d / atr, 9) <= K_ZONE)
            f["n_layers"] = layers_in_zone(levels, side, price, c1, K_ZONE * atr)
            f["n_layers_k1"] = layers_in_zone(levels, side, price, c1, K_ZONE_ALT * atr)
            f["n_layers_4hrule"] = layers_in_zone(levels, side, price, c4, K_ZONE * atr)
        f["near_src_4hrule"] = bsel[2] if bsel is not None else "none"
        # approach speed and sweep (1h closed bars)
        if a is not None and atr == atr and j1 >= APPROACH_BARS:
            mv = float(T1["C"][j1 - APPROACH_BARS]) - float(T1["C"][j1])
            if side == "short":
                mv = -mv
            f["approach"] = "fast" if mv >= APPROACH_FAST * atr else "slow" if mv > 0 else "away"
            lp = a[1]
            lo = T1["L"][max(0, j1 - SWEEP_BARS + 1):j1 + 1]
            hi = T1["H"][max(0, j1 - SWEEP_BARS + 1):j1 + 1]
            f["sweep"] = bool((lo < lp).any()) if side == "long" else bool((hi > lp).any())
        else:
            f["approach"] = "na"
            f["sweep"] = False
        # ladder
        pd = self.prior_k(t, "1d")
        p12 = self.prior_k(t, "12h")
        p8 = self.prior_k(t, "8h")
        cd = self.candle("1d", pd) if pd >= 0 else None
        if PLANT.get("ladder_final_day"):
            k = self.cur_k(t, "1d")
            cd = self.candle("1d", k) if k < self.tf["1d"]["K"] else cd      # PLANT: today's final OHLC
        c12 = self.candle("12h", p12) if p12 >= 0 else None
        c8 = self.candle("8h", p8) if p8 >= 0 else None
        rung, stop, cost_r, below, sd, s12, s8 = ladder(side, price, cd, c12, c8)
        pdp = (float(self.part["1d"]["o"][t]), float(self.part["1d"]["h"][t]), float(self.part["1d"]["l"][t]), price)
        f.update(ladder_cond=ladder_cond(side, price, cd), ladder_cond_alt=ladder_cond(side, price, cd, pdp),
                 ladder_rung=rung, ladder_stop_pct=stop, ladder_cost_r=cost_r,
                 ladder_below_floor=below, stop_d_pct=sd, stop_12_pct=s12, stop_8_pct=s8)
        # bollinger side rules (4h)
        st = self.bb_4h["state"][j4] if j4 >= 0 else "na"
        pb = float(self.bb_4h["pctb"][j4]) if j4 >= 0 else float("nan")
        f["bb_long_conf"] = bool(side == "long" and st == "reenter_from_lower")
        f["bb_short_veto_walk"] = bool(side == "short" and st == "walk_down")
        f["bb_short_veto_band"] = bool(side == "short" and pb == pb and pb <= 0.0)
        # HTF alignment
        jw = self.last_closed(t, "1w")
        wt = self.weekly_trend[jw] if jw >= 0 else "na"
        f["htf_align"] = bool((side == "long" and wt == "up") or (side == "short" and wt == "down"))
        return f

    def common_fields(self, t):
        b = self.b
        f = {"t": int(t), "price": float(b["C"][t])}
        for tf in CANDLE_TFS:
            j = self.last_closed(t, tf)
            if j >= 0:
                o, h, l, c = self.candle(tf, j)
                f[f"c_{tf}"] = (float(o), float(h), float(l), float(c))
                b_ = self.candle(tf, j - 1) if j >= 1 else None
                c_ = self.candle(tf, j - 2) if j >= 2 else None
                f[f"pat_{tf}"] = pat_str(candle_patterns((o, h, l, c), b_, c_)) if b_ is not None else "na"
            else:
                f[f"c_{tf}"] = None
                f[f"pat_{tf}"] = "na"
            k = self.cur_k(t, tf)
            if t >= TF_OFF[tf]:
                f[f"p_{tf}"] = (float(self.part[tf]["o"][t]), float(self.part[tf]["h"][t]), float(self.part[tf]["l"][t]), float(b["C"][t]))
            else:
                f[f"p_{tf}"] = None
        jw = self.last_closed(t, "1w")
        f["c_1w_hl"] = (float(self.tf["1w"]["H"][jw]), float(self.tf["1w"]["L"][jw])) if jw >= 0 else None
        j4 = self.last_closed(t, "4h")
        f["atr4"] = float(self.atr4[j4]) if j4 >= 0 else float("nan")
        for tf in ("4h", "1d"):
            j = self.last_closed(t, tf)
            B = getattr(self, "bb_" + tf)
            if PLANT.get("bb_partial_close") and tf == "4h":
                # PLANT: bands/state of the bucket holding bar t (its final close leaks)
                k = self.cur_k(t, tf)
                j = k if k < self.tf[tf]["K"] else j
            if j >= 0:
                f[f"bb_{tf}_state"] = B["state"][j]
                f[f"bb_{tf}_pctb"] = float(B["pctb"][j])
                f[f"bb_{tf}_bw"] = float(B["bw"][j])
            else:
                f[f"bb_{tf}_state"] = "na"
                f[f"bb_{tf}_pctb"] = float("nan")
                f[f"bb_{tf}_bw"] = float("nan")
        jd = self.last_closed(t, "1d")
        f["phase_a"] = self.phase_a[jd] if jd >= 0 else "na"
        f["phase_b"] = self.phase_b[jd] if jd >= 0 else "na"
        # intraday balance / trend from the last 24 closed 1h bars
        j1 = self.last_closed(t, "1h")
        T1 = self.tf["1h"]
        if j1 >= 24 and f["atr4"] == f["atr4"]:
            H24 = T1["H"][j1 - 23:j1 + 1].max()
            L24 = T1["L"][j1 - 23:j1 + 1].min()
            if H24 - L24 <= BAL_K * f["atr4"]:
                f["intraday"] = "balance"
            else:
                f["intraday"] = "trend_up" if T1["C"][j1] > T1["C"][j1 - 24] else "trend_down"
            # alternative definition (counted only): last 12 closes inside the range of the 12 bars before
            hb = T1["H"][j1 - 23:j1 - 11].max()
            lb = T1["L"][j1 - 23:j1 - 11].min()
            cl = T1["C"][j1 - 11:j1 + 1]
            f["intraday_alt"] = "balance" if bool(((cl <= hb) & (cl >= lb)).all()) else ("trend_up" if T1["C"][j1] > T1["C"][j1 - 24] else "trend_down")
        else:
            f["intraday"] = "na"
            f["intraday_alt"] = "na"
        f["vol_regime"] = self.vol_reg[j4] if j4 >= 0 else "na"
        f["squeeze"] = bool(self.squeeze[j4]) if j4 >= 0 else False
        f["session"] = session_of(t)
        f["weekend"] = bool(is_weekend(t))
        # funding: last settlement with calc_time <= close time of bar t
        close_ms = TS0 + (t + 1) * MS
        if len(self.fund_t):
            i = int(np.searchsorted(self.fund_t, close_ms, side="right")) - 1
            if PLANT.get("funding_next"):
                i = min(i + 1, len(self.fund_t) - 1)      # PLANT: the next settlement
            if i >= 0:
                r = float(self.fund_r[i])
                f["funding"] = "neg" if r < 0 else "low" if r <= FUND_HIGH else "high"
            else:
                f["funding"] = "na"
        else:
            f["funding"] = "na"
        return f

    def context(self, t, side):
        if not (0 <= t < self.n):
            raise IndexError("t outside the bars")
        f = self.common_fields(t)
        tg = t if t % 60 == 59 else (t // 60) * 60 - 1          # level fields refresh at the last 1h close <= t
        if tg >= 59:
            f.update(self.side_fields(tg, side))
        else:
            f.update(near_src="none")
        f["levels_grid_t"] = int(tg)
        return f


# ================================================================= REPLAY build
class _Bucket:
    __slots__ = ("P", "off", "o", "h", "l", "c", "v", "closed", "cur_k")

    def __init__(self, P, off, keep):
        self.P, self.off = P, off
        self.o = self.h = self.l = self.c = None
        self.v = 0.0
        self.closed = deque(maxlen=keep)   # (o, h, l, c, v)
        self.cur_k = -1

    def feed(self, t, o, h, l, c, v):
        if t < self.off:
            return False
        k = (t - self.off) // self.P
        if k != self.cur_k:
            self.cur_k = k
            self.o, self.h, self.l, self.c, self.v = o, h, l, c, v
        else:
            self.h = h if h > self.h else self.h
            self.l = l if l < self.l else self.l
            self.c = c
            self.v += v
        if (t + 1 - self.off) % self.P == 0:
            self.closed.append((self.o, self.h, self.l, self.c, self.v))
            return True
        return False

    def partial(self):
        return None if self.o is None else (self.o, self.h, self.l, self.c)

    def last(self, back=0):
        """Closed candle `back` steps before the last closed one, or None."""
        n = len(self.closed)
        return self.closed[n - 1 - back] if n - 1 - back >= 0 else None


class Replay:
    """Sequential build. feed(t, o, h, l, c, v) once per 1m bar in order; context(side) after feeding bar t."""

    def __init__(self, funding=None):
        self.t = -1
        self.bk = {tf: _Bucket(TF_P[tf], TF_OFF[tf], keep=800 if tf == "1h" else 400) for tf in TF_P}
        self.price = float("nan")
        # 4h-derived state
        self.tr4 = deque(maxlen=ATR_N)
        self.prev_c4 = None
        self.atr4 = float("nan")
        self.atr_hist = deque(maxlen=PCT_WIN)
        self.bw4_hist = deque(maxlen=PCT_WIN)
        self.c4 = deque(maxlen=BB_N)
        self.bb4 = deque(maxlen=WALK_N + 1)   # (close, up, lo, bw, pctb)
        self.bb4_state = "na"
        self.piv4 = []                         # (price, kind, formed_j, avail_j)
        self.n4 = 0                            # closed 4h count
        self.h4 = deque(maxlen=2 * PIVOT_N + 1)
        self.l4 = deque(maxlen=2 * PIVOT_N + 1)
        self.vol_reg = "na"
        self.squeeze = False
        # daily-derived state
        self.cd = deque(maxlen=max(BB_N, SMA_PHASE, 31))
        self.bb1d = deque(maxlen=WALK_N + 1)
        self.bb1d_state = "na"
        self.bb1d_levels = None
        self.nd = 0
        self.hd = deque(maxlen=2 * PIVOT_N + 1)
        self.ld = deque(maxlen=2 * PIVOT_N + 1)
        self.ph_hs, self.ph_ls = [], []
        self.last_dir = None
        self.phase_a = "na"
        self.phase_b = "na"
        self.day_L, self.day_H, self.day_V = [], [], []
        self.vp_day = None                     # profile of the last completed day
        self.vp_day_avail = -1
        self.week_L, self.week_H, self.week_V = [], [], []
        self.vp_week = None
        self.vp_week_avail = -1
        self.cw = deque(maxlen=WEEKLY_TREND_BARS + 1)
        self.weekly_trend = "na"
        # vwap accumulators
        self.s_pv = self.s_v = 0.0
        self.w_pv = self.w_v = 0.0
        self.s_day = -1
        self.w_week = -1
        # funding
        self.fund = list(zip(*funding)) if funding is not None and len(funding[0]) else []
        self.fi = -1
        # level snapshot (refreshed at 1h closes)
        self.levels = []
        self.levels_t = -1
        self.grid_cache = {}

    # ---- feeding
    def feed(self, t, o, h, l, c, v):
        assert t == self.t + 1, "bars must be fed in order"
        self.t = t
        self.price = c
        tp = (h + l + c) / 3.0
        d = t // 1440
        if d != self.s_day:
            self.s_day = d
            self.s_pv = self.s_v = 0.0
        self.s_pv += tp * v
        self.s_v += v
        if t >= WEEK_OFF:
            w = (t - WEEK_OFF) // 10080
            if w != self.w_week:
                self.w_week = w
                self.w_pv = self.w_v = 0.0
            self.w_pv += tp * v
            self.w_v += v
            self.week_L.append(l)
            self.week_H.append(h)
            self.week_V.append(v)
        self.day_L.append(l)
        self.day_H.append(h)
        self.day_V.append(v)
        for tf, bk in self.bk.items():
            closed = bk.feed(t, o, h, l, c, v)
            if closed:
                if tf == "4h":
                    self._on_4h(bk.last())
                elif tf == "1d":
                    self._on_1d(bk.last(), t)
                elif tf == "1w":
                    self._on_1w(bk.last(), t)
        while self.fi + 1 < len(self.fund) and self.fund[self.fi + 1][0] <= TS0 + (t + 1) * MS:
            self.fi += 1
        if t % 60 == 59:
            self._refresh_levels(t)

    def _on_4h(self, cndl):
        o, h, l, c, v = cndl
        self.n4 += 1
        j = self.n4 - 1
        if self.prev_c4 is not None:
            tr = max(h - l, abs(h - self.prev_c4), abs(l - self.prev_c4))
            self.tr4.append(tr)
            if len(self.tr4) == ATR_N:
                self.atr4 = sum(self.tr4) / ATR_N
                self.atr_hist.append(self.atr4)
        self.prev_c4 = c
        self.c4.append(c)
        if len(self.c4) == BB_N:
            m = sum(self.c4) / BB_N
            var = sum((x - m) ** 2 for x in self.c4) / BB_N
            sd = var ** 0.5
            up, lo = m + BB_K * sd, m - BB_K * sd
            bw = (up - lo) / m
            pb = (c - lo) / (up - lo) if up > lo else float("nan")
            self.bb4.append((c, up, lo, bw, pb))
            self.bw4_hist.append(bw)
            if len(self.bb4) == WALK_N + 1:
                self.bb4_state = bb_state_from([x[0] for x in self.bb4], [x[1] for x in self.bb4],
                                               [x[2] for x in self.bb4], [x[3] for x in self.bb4])
        # fractal pivots: the candidate is the bar PIVOT_N back; confirmed now (avail_j = j)
        self.h4.append(h)
        self.l4.append(l)
        n = PIVOT_N
        if len(self.h4) == 2 * n + 1:
            mh, ml = self.h4[n], self.l4[n]
            if all(mh > self.h4[k] for k in range(2 * n + 1) if k != n):
                self.piv4.append((mh, "H", j - n, j))
            if all(ml < self.l4[k] for k in range(2 * n + 1) if k != n):
                self.piv4.append((ml, "L", j - n, j))
        # F7 regimes over the trailing window (inclusive of this bar)
        if len(self.atr_hist) == PCT_WIN:
            self.vol_reg = vol_regime_of(np.sort(np.array(self.atr_hist)), self.atr4)
        if len(self.bw4_hist) == PCT_WIN:
            self.squeeze = bool(self.bw4_hist[-1] <= np.percentile(np.array(self.bw4_hist), SQUEEZE_PCT))

    def _on_1d(self, cndl, t):
        o, h, l, c, v = cndl
        self.nd += 1
        j = self.nd - 1
        self.cd.append(c)
        if len(self.cd) >= BB_N:
            xs = list(self.cd)[-BB_N:]
            m = sum(xs) / BB_N
            sd = (sum((x - m) ** 2 for x in xs) / BB_N) ** 0.5
            up, lo = m + BB_K * sd, m - BB_K * sd
            self.bb1d_levels = (m, up, lo)
            self.bb1d.append((c, up, lo, (up - lo) / m, (c - lo) / (up - lo) if up > lo else float("nan")))
            if len(self.bb1d) == WALK_N + 1:
                self.bb1d_state = bb_state_from([x[0] for x in self.bb1d], [x[1] for x in self.bb1d],
                                                [x[2] for x in self.bb1d], [x[3] for x in self.bb1d])
        # phase A pivots on daily bars
        self.hd.append(h)
        self.ld.append(l)
        n = PIVOT_N
        if len(self.hd) == 2 * n + 1:
            mh, ml = self.hd[n], self.ld[n]
            if all(mh > self.hd[k] for k in range(2 * n + 1) if k != n):
                self.ph_hs.append(mh)
            if all(ml < self.ld[k] for k in range(2 * n + 1) if k != n):
                self.ph_ls.append(ml)
        if len(self.ph_hs) >= 2 and len(self.ph_ls) >= 2:
            up = self.ph_hs[-1] > self.ph_hs[-2] and self.ph_ls[-1] > self.ph_ls[-2]
            dn = self.ph_hs[-1] < self.ph_hs[-2] and self.ph_ls[-1] < self.ph_ls[-2]
            st = "up" if up else "down" if dn else "range"
            if st != "range":
                self.last_dir = st
                self.phase_a = "markup" if st == "up" else "markdown"
            else:
                self.phase_a = "distribution" if self.last_dir == "up" else "accumulation" if self.last_dir == "down" else "range_initial"
        # phase B
        cds = list(self.cd)
        if len(cds) >= SMA_PHASE and len(cds) >= 31:
            r = cds[-1] / cds[-31] - 1.0
            sma = sum(cds[-SMA_PHASE:]) / SMA_PHASE
            self.phase_b = "markup" if r >= RET30_THR else "markdown" if r <= -RET30_THR else ("distribution" if cds[-1] > sma else "accumulation")
        # day profile (keep the previous one for the old PRIOR_RULE)
        self._vp_day_prior = self.vp_day
        self.vp_day = profile_replay(self.day_L, self.day_H, self.day_V)
        self.vp_day_avail = t
        self.day_L, self.day_H, self.day_V = [], [], []

    def _on_1w(self, cndl, t):
        o, h, l, c, v = cndl
        self.cw.append(c)
        if len(self.cw) == WEEKLY_TREND_BARS + 1:
            self.weekly_trend = "up" if self.cw[-1] > self.cw[0] else "down"
        self._vp_week_prior = self.vp_week
        self.vp_week = profile_replay(self.week_L, self.week_H, self.week_V)
        self.vp_week_avail = t
        self.week_L, self.week_H, self.week_V = [], [], []

    # ---- levels (at a 1h close)
    def _refresh_levels(self, t):
        out = []
        bd = self.bk["1d"]
        complete_d = (t + 1) % 1440 == 0
        old = PRIOR_RULE == "cur_k_minus_1"
        # last closed day = bd.last(0) (when the day is complete at t, that IS the day holding t); the old rule skips it then
        prior_d = bd.last(1) if (old and complete_d) else bd.last(0)
        if prior_d is not None:
            jd = (t // 1440) - 1 if old else (t + 1) // 1440 - 1
            av = (jd + 1) * 1440 - 1
            out.append((prior_d[1], "prior_d_hl", av))
            out.append((prior_d[2], "prior_d_hl", av))
            # the profile of that day: _on_1d has already run for a day that completed at t (feed order), so vp_day is
            # the just-closed day's; the old rule wants the one before it -> vp_day_prior
            vp = self.vp_day_prior if (old and complete_d) else self.vp_day
            if vp:
                for px in vp:
                    out.append((px, "fabio_vp_day", av))
        bw = self.bk["1w"]
        if t >= WEEK_OFF:
            complete_w = (t + 1 - WEEK_OFF) % 10080 == 0
            prior_w = bw.last(1) if (old and complete_w) else bw.last(0)
            if prior_w is not None:
                jw = (t - WEEK_OFF) // 10080 - 1 if old else (t + 1 - WEEK_OFF) // 10080 - 1
                av = WEEK_OFF + (jw + 1) * 10080 - 1
                out.append((prior_w[1], "prior_w_hl", av))
                out.append((prior_w[2], "prior_w_hl", av))
                vp = self.vp_week_prior if (old and complete_w) else self.vp_week
                if vp:
                    for px in vp:
                        out.append((px, "tom_vp_week", av))
        j4 = self.n4 - 1
        for px, kind, fj, aj in self.piv4:
            if j4 - fj > KROWN_MAX_AGE:
                continue
            out.append((px, "krown_zone", (aj + 1) * 240 - 1))
        if self.bb1d_levels is not None:
            jdc = self.nd - 1
            av = (jdc + 1) * 1440 - 1
            for px in self.bb1d_levels:
                out.append((px, "malkan_bb_d", av))
        if self.s_v > 0:
            out.append((self.s_pv / self.s_v, "vwap_session", (t // 1440) * 1440))
        if t >= WEEK_OFF and self.w_v > 0:
            out.append((self.w_pv / self.w_v, "vwap_week", WEEK_OFF + ((t - WEEK_OFF) // 10080) * 10080))
        price = self.price
        below = float(np.floor(price / ROUND_STEP) * ROUND_STEP)
        if below == price:
            below -= ROUND_STEP
        out.append((below, "round_1k", 0))
        out.append((below + ROUND_STEP, "round_1k", 0))
        if price == below + ROUND_STEP:
            out.append((below + 2 * ROUND_STEP, "round_1k", 0))
        self.levels = out
        self.levels_t = t
        self.side_snap = {"long": self._side_fields("long"), "short": self._side_fields("short")}

    @property
    def vp_day_prior(self):
        return getattr(self, "_vp_day_prior", None)

    @property
    def vp_week_prior(self):
        return getattr(self, "_vp_week_prior", None)

    # ---- snapshot
    def _closed_candle(self, tf, back=0):
        bk = self.bk[tf]
        # bk.last(0) is the last closed bucket; when the bucket holding t is complete it IS that bucket
        r = bk.last(back)
        return None if r is None else r[:4]

    def _prior_candle(self, tf):
        """The ladder's 'prior' candle (PRIOR_RULE): the last closed one, or under the old rule the candle before the
        one holding bar t (which skips a candle that completes at t)."""
        bk = self.bk[tf]
        t = self.t
        if t < bk.off:
            return None
        complete = (t + 1 - bk.off) % bk.P == 0
        r = bk.last(1) if (PRIOR_RULE == "cur_k_minus_1" and complete) else bk.last(0)
        return None if r is None else r[:4]

    def context(self, side):
        t = self.t
        f = {"t": int(t), "price": float(self.price)}
        for tf in CANDLE_TFS:
            a = self._closed_candle(tf, 0)
            b = self._closed_candle(tf, 1)
            c = self._closed_candle(tf, 2)
            f[f"c_{tf}"] = tuple(float(x) for x in a) if a else None
            f[f"pat_{tf}"] = pat_str(candle_patterns(a, b, c)) if (a and b) else "na"
            p = self.bk[tf].partial()
            f[f"p_{tf}"] = tuple(float(x) for x in p) if p else None
        w = self._closed_candle("1w", 0)
        f["c_1w_hl"] = (float(w[1]), float(w[2])) if w else None
        f["atr4"] = float(self.atr4)
        f["bb_4h_state"] = self.bb4_state
        f["bb_4h_pctb"] = float(self.bb4[-1][4]) if self.bb4 else float("nan")
        f["bb_4h_bw"] = float(self.bb4[-1][3]) if self.bb4 else float("nan")
        f["bb_1d_state"] = self.bb1d_state
        f["bb_1d_pctb"] = float(self.bb1d[-1][4]) if self.bb1d else float("nan")
        f["bb_1d_bw"] = float(self.bb1d[-1][3]) if self.bb1d else float("nan")
        f["phase_a"] = self.phase_a
        f["phase_b"] = self.phase_b
        b1 = self.bk["1h"]
        if len(b1.closed) >= 25 and self.atr4 == self.atr4:
            last24 = [b1.last(k) for k in range(24)]           # last(0) = most recent
            H24 = max(x[1] for x in last24)
            L24 = min(x[2] for x in last24)
            c_now = b1.last(0)[3]
            c_24 = b1.last(24)[3]
            if H24 - L24 <= BAL_K * self.atr4:
                f["intraday"] = "balance"
            else:
                f["intraday"] = "trend_up" if c_now > c_24 else "trend_down"
            before = last24[12:]      # bars 13..24 back
            hb = max(x[1] for x in before)
            lb = min(x[2] for x in before)
            inside = all(lb <= x[3] <= hb for x in last24[:12])
            f["intraday_alt"] = "balance" if inside else ("trend_up" if c_now > c_24 else "trend_down")
        else:
            f["intraday"] = "na"
            f["intraday_alt"] = "na"
        f["vol_regime"] = self.vol_reg
        f["squeeze"] = bool(self.squeeze)
        f["session"] = session_of(t)
        f["weekend"] = bool(is_weekend(t))
        if self.fund and self.fi >= 0:
            r = self.fund[self.fi][1]
            f["funding"] = "neg" if r < 0 else "low" if r <= FUND_HIGH else "high"
        else:
            f["funding"] = "na"
        # side fields at the last 1h close
        if self.levels_t >= 59:
            f.update(self.side_snap[side])
        else:
            f["near_src"] = "none"
        f["levels_grid_t"] = int(self.levels_t)
        return f

    def _side_fields(self, side):
        tg = self.levels_t
        price = float(self.price)
        b1 = self.bk["1h"]
        c1 = b1.last(0)[3]
        c4 = self.bk["4h"].last(0)[3] if self.bk["4h"].last(0) else float("nan")
        atr = self.atr4
        levels = self.levels
        a, bsel = nearest_side(levels, side, price, c1, c4)
        f = {"n_levels": len(levels), "n_krown": sum(1 for lv in levels if lv[1] == "krown_zone")}   # ledger size (counts)
        if a is None or atr != atr:
            f.update(near_price=float("nan"), near_src="none", near_dist_atr=float("nan"), level_age_h=float("nan"),
                     touch_count=-1, first_touch=False, at_level=False, n_layers=0, n_layers_k1=0, n_layers_4hrule=0)
        else:
            d, lp, src, av = a
            f["near_price"] = float(lp)
            f["near_src"] = src
            f["near_dist_atr"] = d / atr
            f["level_age_h"] = (tg + 1 - av) / 60.0
            # touches: completed 1h bars that start after avail and end before the bar holding tg
            j_cur = tg // 60
            j_first = max(0, (av + 1 + 59) // 60, j_cur - TOUCH_LOOKBACK)
            tc = 0
            for jj in range(j_first, j_cur):
                back = j_cur - jj          # last(0) is bar j_cur (closed at tg); bar jj = last(j_cur - jj)
                r = b1.last(back)
                if r is None:
                    continue
                if r[2] <= lp <= r[1]:
                    tc += 1
            f["touch_count"] = tc
            f["first_touch"] = tc == 0
            f["at_level"] = bool(round(d / atr, 9) <= K_ZONE)
            f["n_layers"] = layers_in_zone(levels, side, price, c1, K_ZONE * atr)
            f["n_layers_k1"] = layers_in_zone(levels, side, price, c1, K_ZONE_ALT * atr)
            f["n_layers_4hrule"] = layers_in_zone(levels, side, price, c4, K_ZONE * atr)
        f["near_src_4hrule"] = bsel[2] if bsel is not None else "none"
        if a is not None and atr == atr and len(b1.closed) > APPROACH_BARS:
            mv = b1.last(APPROACH_BARS)[3] - b1.last(0)[3]
            if side == "short":
                mv = -mv
            f["approach"] = "fast" if mv >= APPROACH_FAST * atr else "slow" if mv > 0 else "away"
            lp = a[1]
            win = [b1.last(k) for k in range(min(SWEEP_BARS, len(b1.closed)))]
            f["sweep"] = any(x[2] < lp for x in win) if side == "long" else any(x[1] > lp for x in win)
        else:
            f["approach"] = "na"
            f["sweep"] = False
        cd = self._prior_candle("1d")
        c12 = self._prior_candle("12h")
        c8 = self._prior_candle("8h")
        rung, stop, cost_r, below, sd, s12, s8 = ladder(side, price, cd, c12, c8)
        pdp = self.bk["1d"].partial()
        f.update(ladder_cond=ladder_cond(side, price, cd), ladder_cond_alt=ladder_cond(side, price, cd, pdp),
                 ladder_rung=rung, ladder_stop_pct=stop, ladder_cost_r=cost_r,
                 ladder_below_floor=below, stop_d_pct=sd, stop_12_pct=s12, stop_8_pct=s8)
        st = self.bb4_state
        pb = self.bb4[-1][4] if self.bb4 else float("nan")
        f["bb_long_conf"] = bool(side == "long" and st == "reenter_from_lower")
        f["bb_short_veto_walk"] = bool(side == "short" and st == "walk_down")
        f["bb_short_veto_band"] = bool(side == "short" and pb == pb and pb <= 0.0)
        wt = self.weekly_trend
        f["htf_align"] = bool((side == "long" and wt == "up") or (side == "short" and wt == "down"))
        return f


# ================================================================= public API
_VEC_CACHE = {}


def context_at(bars, t, side, impl="vec", funding=None):
    """All factors as of the close of 1m bar t for `side` in {long, short}, built only from bars[0..t].
    impl = 'vec' (all-at-once on bars[:t+1]) or 'replay' (state machine fed bars 0..t)."""
    assert side in ("long", "short")
    n = len(bars["C"])
    assert 0 <= t < n
    if funding is not None and len(funding[0]):
        # the funding archive is point-in-time too: only settlements at/before the close of the LAST bar given exist
        # (bar t's own PIT-ness is the VEC build's job: it must not read past t whatever the array holds)
        end_ms = TS0 + n * MS
        m = funding[0] <= end_ms
        funding = (funding[0][m], funding[1][m])
    if impl == "vec":
        # the VEC build sees the WHOLE array passed in; a look-ahead would read bars after t. The truncation tests
        # compare context_at(bars[0..t], t) with context_at(bars[0..t+N], t): they are only meaningful because of this.
        key = (id(bars), n, float(bars["C"][0]), float(bars["C"][-1]), tuple(sorted(PLANT.items())))
        V = _VEC_CACHE.get(key)
        if V is None:
            V = VecTables(bars, funding)
            _VEC_CACHE.clear()
            _VEC_CACHE[key] = V
        return V.context(t, side)
    sub = slice_bars(bars, t + 1)       # the replay is truncated by construction: it is fed bars 0..t and nothing else
    R = Replay(funding)
    for i in range(t + 1):
        R.feed(i, float(sub["O"][i]), float(sub["H"][i]), float(sub["L"][i]), float(sub["C"][i]), float(sub["V"][i]))
    return R.context(side)
