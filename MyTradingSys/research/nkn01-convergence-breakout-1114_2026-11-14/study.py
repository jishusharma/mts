"""NKN-01 convergence breakout (long; mirrored short control), context-conditioned study. See PRE_REG.md (frozen design).
Usage: python study.py counts | run | report      (counts = signal counts per cell, NO outcome computed)
Causal by construction: indicators are forward recursions or trailing windows; phase / cycle / level / WT / funding are read at a closed bar
before the signal. STUDY_BUG=1 env turns on a deliberate look-ahead (phase and cycle read at the SAME day), used only by the failing test.
Short side = long logic on mirrored prices (o,h,l,c -> -o,-l,-h,-c); EMAs mirror exactly (linear), fees use absolute prices."""
import os
import sys
import csv
import json
import subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CACHE = Path(r"F:\MTS\data_cache")
SPOT = CACHE / "binance_spot"
FRESH = CACHE / "binance_fresh" / "nk5_nyasia"
FUND = CACHE / "binance_futures" / "nkp1"
PHASE_CSV = CACHE / "mts_brains" / "phase_daily.csv"
sys.path.insert(0, str(REPO / "MyTradingSys" / "backtest" / "layers" / "wavetrend"))

DAY, H4 = 86400000, 4 * 3600000
SPLIT = 1704067200000  # 2024-01-01 UTC; applied to the SIGNAL bar open time
COINS = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
FRESH_COINS = "AAVE ENJ GRT HBAR MANA SAND THETA XTZ".split()
# parameters (labels in PRE_REG.md)
EMA_LENS = (20, 50, 100, 200)
EMA_WARM = 200          # first 200 bars of every series carry no signal (EMA seed)
FALL_BARS, DEPTH_BARS, DEPTH_ATR = 10, 50, 1.5
TGT_R, MIN_ATR_MULT = 2.0, 0.6
FLOOR = {"1d": 0.005, "4h": 0.012}
LEVEL_WEEKS, AT_ATR = 12, 1.0
WT_OB2, FUND_MAX, LIM_BARS = 53.0, 0.0003, 5
ADX_N, ADX_MIN, SLOPE_LAG = 14, 20.0, 5
BP = {"taker": 12.0, "maker": 6.0}
PH_UP, PH_RANGE, PH_DOWN, PH_NA = 1, 0, -1, 9
CYC_NAMES = ["CAPITULATION", "MARKDOWN", "RELIEF", "ACCUM-RANGE", "MARKUP", "DISTRIBUTION"]
CYC = {n: i for i, n in enumerate(CYC_NAMES)}
B_TRADE, B_CLUSTER, N_PLACEBO = 2000, 5000, 1000


def bug():
    return os.environ.get("STUDY_BUG", "")


# ------------------------------------------------------------------ cells (frozen in PRE_REG)
def cell(i, status, ph, cyc, lvl, var, tf, sd, W, entry="mkt", c8=False, note=""):
    return dict(id=i, status=status, ph=ph, cyc=cyc, lvl=lvl, var=var, tf=tf, sd=sd, W=W, entry=entry, c8=c8, note=note)


ACC = ("ACCUM-RANGE",)
CELLS = [
    cell("P1", "PRIMARY", PH_RANGE, ACC, "at", "V0", "1d", 1, .03),
    cell("P2", "PRIMARY", PH_RANGE, ACC, "at", "V1", "1d", 1, .03),
    cell("P3", "PRIMARY", PH_RANGE, ACC, "at", "V2", "1d", 1, .03),
    cell("C1", "CONTROL", PH_RANGE, ACC, "away", "V0", "1d", 1, .03, note="level comparison"),
    cell("C2", "CONTROL", PH_RANGE, ("MARKUP",), "at", "V0", "1d", 1, .03, note="a pause, not a turn"),
    cell("C3", "CONTROL", PH_DOWN, ("MARKDOWN",), "at", "V0", "1d", 1, .03, note="falling knife"),
    cell("C4", "CONTROL", PH_UP, None, "at", "V0", "1d", 1, .03, note="continuation (any BTC label)"),
    cell("C5", "CONTROL", PH_RANGE, ("CAPITULATION", "RELIEF"), "at", "V0", "1d", 1, .03, note="episodes only"),
    cell("C6", "CONTROL", PH_RANGE, ACC, "at", "V0", "4h", 1, .015, note="timeframe 4h, R floor 1.2%"),
    cell("C7", "CONTROL", PH_DOWN, ("MARKDOWN",), "at", "V0", "1d", -1, .03, note="mirrored short, NK forbids shorts"),
    cell("C8", "CONTROL", PH_RANGE, ACC, "at", "V0", "1d", 1, .03, c8=True, note="NK index filter: BTC > SMA20 and SMA50 (BTC itself excluded)"),
    cell("C9", "CONTROL", PH_RANGE, ACC, "at", "V0", "1d", 1, .03, entry="lim", note="limit at SMA20 within 5 bars"),
    cell("C10", "CONTROL", PH_RANGE, ACC, "at", "V0", "1d", 1, .05, note="stack width 5%, power check"),
]
SETKEYS = sorted({(c["tf"], c["sd"], c["W"], c["entry"]) for c in CELLS})
POOLKEYS = sorted({(c["tf"], c["sd"], c["entry"]) for c in CELLS})


# ------------------------------------------------------------------ data
def load_base(path, step):
    """Load a base npz (t or ts key, or one unnamed array 'a' = rows [t,o,h,l,c,v]); assert key, strictly increasing t, step multiples.
    Returns (arrays, provenance). Raw series have known intraday exchange gaps: counted, not hidden."""
    z = np.load(path, allow_pickle=False)
    if "a" in z.files:
        a = z["a"]
        t, o, h, l, c = (a[:, k] for k in range(5))
        key = "a[:,0]"
    else:
        keys = [k for k in ("t", "ts") if k in z.files]
        assert len(keys) == 1, f"{path}: time key must be exactly one of t/ts, got {z.files}"
        key = keys[0]
        t, o, h, l, c = z[key], z["o"], z["h"], z["l"], z["c"]
    t = np.asarray(t).astype(np.int64)
    assert (np.diff(t) > 0).all(), f"{path}: timestamps not strictly increasing"
    d = np.diff(t)
    assert (d % step == 0).all(), f"{path}: step not a multiple of {step}"
    gaps = int((d != step).sum())
    prov = dict(file=Path(path).name, key=key, n=int(len(t)), first=int(t[0]), last=int(t[-1]), step_ms=step, gap_events=gaps,
                missing_bars=int((d // step - 1).sum()))
    return dict(t=t, o=np.asarray(o, float), h=np.asarray(h, float), l=np.asarray(l, float), c=np.asarray(c, float)), prov


def resample(base, period, step):
    """Bucket the base bars into UTC-aligned `period` bars from ONE source. Incomplete first/last buckets are dropped. n = base bars in the bucket."""
    t = base["t"]
    b = t // period
    ub, idx, cnt = np.unique(b, return_index=True, return_counts=True)
    out = dict(t=ub * period, o=base["o"][idx], h=np.maximum.reduceat(base["h"], idx), l=np.minimum.reduceat(base["l"], idx),
               c=base["c"][idx + cnt - 1], n=cnt)
    full = cnt == period // step
    keep = np.ones(len(ub), bool)
    if len(keep):
        keep[0] &= full[0]
        keep[-1] &= full[-1]
    return {k: v[keep] for k, v in out.items()}


def build_tfs(base, step):
    d1 = resample(base, DAY, step)
    assert (np.diff(d1["t"]) == DAY).all(), "daily series has a missing calendar day"
    return d1, resample(base, H4, step)


# ------------------------------------------------------------------ indicators
def ema(x, n):
    a = 2.0 / (n + 1)
    out = np.empty(len(x))
    out[0] = x[0]
    xs = x.tolist()
    p = xs[0]
    for i in range(1, len(xs)):
        p = a * xs[i] + (1 - a) * p
        out[i] = p
    return out


def sma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        cs = np.cumsum(np.r_[0.0, x])
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def wilder_atr(h, l, c, n=14):
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    out = np.full(len(c), np.nan)
    if len(c) >= n:
        out[n - 1] = tr[:n].mean()
        for i in range(n, len(c)):
            out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def adx_di(h, l, c, n=14):
    """Wilder DI+, DI-, ADX (FORMULAS s30.1: sum-seeded smoothing, ADX = mean of first n DX then recursive). Value at index j uses bars <= j."""
    h, l, c = (np.asarray(a, float) for a in (h, l, c))
    m = len(c)
    dip, dim, adx = (np.full(m, np.nan) for _ in range(3))
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


def coin_phase(d1):
    """State at the CLOSE of each daily bar j: UP = ADX14>=20, DI+>DI-, SMA20 slope (SMA20[j]/SMA20[j-5]-1) > 0; DOWN mirror; else RANGE; NA while warming."""
    c = d1["c"]
    dip, dim, adx = adx_di(d1["h"], d1["l"], c, ADX_N)
    s20 = sma(c, 20)
    slope = np.full(len(c), np.nan)
    slope[SLOPE_LAG:] = s20[SLOPE_LAG:] / s20[:-SLOPE_LAG] - 1
    with np.errstate(invalid="ignore"):
        up = (adx >= ADX_MIN) & (dip > dim) & (slope > 0)
        dn = (adx >= ADX_MIN) & (dim > dip) & (slope < 0)
    ph = np.where(up, PH_UP, np.where(dn, PH_DOWN, PH_RANGE)).astype(np.int8)
    ph[np.isnan(adx) | np.isnan(slope)] = PH_NA
    return ph


def roll(x, w, fn):
    out = np.full(len(x), np.nan)
    if len(x) >= w:
        out[w - 1:] = fn(np.lib.stride_tricks.sliding_window_view(x, w), axis=1)
    return out


def prior_day_idx(dt, T):
    """index of the last daily bar CLOSED at or before the start of the UTC day containing time T (the 'prior daily close'); -1 if none.
    STUDY_BUG=1: the bar of the SAME day (its close is in the future)."""
    ds = (np.asarray(T) // DAY) * DAY
    lim = ds if bug() == "1" else ds - DAY
    return np.searchsorted(dt, lim, side="right") - 1


def weekly_low12(dt, dl):
    """12-week trailing minimum of the weekly lowest daily low-prime. Weeks Monday 00:00 to Sunday 23:59 UTC, complete weeks only.
    Returns (week_end_ms, value): value[k] known once week k closed (end <= query time)."""
    day = dt // DAY
    ws = day - ((day + 3) % 7)
    uw, idx, cnt = np.unique(ws, return_index=True, return_counts=True)
    wl = np.minimum.reduceat(dl, idx)
    keep = cnt == 7
    ends, wl = (uw[keep] + 7) * DAY, wl[keep]
    return ends, roll(wl, LEVEL_WEEKS, np.min)


def level_at(ends, w12, Tq):
    k = np.searchsorted(ends, Tq, side="right") - 1
    out = np.where(k >= 0, w12[np.maximum(k, 0)], np.nan)
    return out


def find_signals(c, h, l, mx, mn, atr, W):
    """Long-logic signals on (possibly mirrored) arrays. s = SECOND close above the stack max; f = s-1 = first close above.
    Conditions at closed bars <= s: width at s, close[f-10] under the stack, fall depth (50-bar high before f minus the 10-bar low F) >= 1.5 ATR14[f-1].
    Returns (s indices, F)."""
    n = len(c)
    s = np.arange(EMA_WARM + FALL_BARS + 1, n)
    if len(s) == 0:
        return s, np.array([])
    f = s - 1
    with np.errstate(invalid="ignore"):
        above = c > mx
        rmin, rmax = roll(l, FALL_BARS, np.min), roll(h, DEPTH_BARS, np.max)
        m = above[s] & above[f] & ~above[f - 1]
        shape = c[f - FALL_BARS] < mn[f - FALL_BARS]
        width = (mx[s] - mn[s]) / np.abs(c[s]) <= W
        F = rmin[f - 1]
        depth = (rmax[f - 1] - F) >= DEPTH_ATR * atr[f - 1]
        ok = m & shape & width & depth
    return s[ok], F[ok]


def pool_bars(c, mx, l):
    """placebo pool: bars b whose close AND previous close are above the stack (trigger state, without the tight/fall conditions). Returns (b, F)."""
    n = len(c)
    b = np.arange(EMA_WARM + FALL_BARS + 2, n)
    with np.errstate(invalid="ignore"):
        above = c > mx
        rmin = roll(l, FALL_BARS, np.min)
        ok = above[b] & above[b - 1]
    return b[ok], rmin[b[ok] - 2]


# ------------------------------------------------------------------ simulation (long logic on possibly mirrored arrays)
def sim_long(o, h, l, c, mx, mn, i0, e, dist, limit_fill=False):
    """Entry price e at bar i0 (market: the open of i0; limit: filled inside i0). Stop = e-dist (checked first), half off at e+2*dist (fills at the
    bar open on a gap through), remainder trailed under the lowest EMA (applied from the bar after it is known), all out at the second consecutive close
    <= stack max. A gap through the stop fills at the open. On a limit-fill bar the target is not allowed. Position open at the data end exits at the
    last close (censored). Returns (g_R, x1, x2, half, exit_idx, censored)."""
    n = len(c)
    stop, tgt = e - dist, e + TGT_R * dist
    half, px1, trail, inside = False, 0.0, -1e300, 0
    for t in range(i0, n):
        se = stop if stop > trail else trail
        if l[t] <= se:
            x2 = o[t] if o[t] < se else se
            return _g(e, dist, half, px1, x2), px1, x2, half, t, False
        if not half and not (limit_fill and t == i0) and h[t] >= tgt:
            px1 = o[t] if o[t] > tgt else tgt
            half = True
        inside = inside + 1 if c[t] <= mx[t] else 0
        if inside >= 2:
            return _g(e, dist, half, px1, c[t]), px1, c[t], half, t, False
        if half and mn[t] > trail:
            trail = mn[t]
    return _g(e, dist, half, px1, c[n - 1]), px1, c[n - 1], half, n - 1, True


def _g(e, dist, half, px1, x2):
    return (0.5 * (px1 - e) + 0.5 * (x2 - e)) / dist if half else (x2 - e) / dist


def fee_r(bp, e, x1, x2, half, dist):
    """round-trip fee in R. bp/2 of the notional on each leg: entry notional |e|, exit notional (half at x1, half at x2, or all at x2)."""
    legs = abs(e) + ((0.5 * abs(x1) + 0.5 * abs(x2)) if half else abs(x2))
    return (bp / 2e4) * legs / dist


def split_of(t_signal):
    """0 = DEV (signal bar open before 2024-01-01 UTC), 1 = VALIDATION. By SIGNAL bar, never entry or exit."""
    return (np.asarray(t_signal) >= SPLIT).astype(np.int8)


# ------------------------------------------------------------------ per-coin context
class Coin:
    def __init__(self, sym, d1, h4):
        self.sym, self.B = sym, {"1d": d1, "4h": h4}
        self.ind, self._view, self._lvl = {}, {}, {}
        for tf, B in self.B.items():
            em = np.array([ema(B["c"], n) for n in EMA_LENS])
            self.ind[tf] = dict(em=em, atr=wilder_atr(B["h"], B["l"], B["c"]), s20=sma(B["c"], 20))
        self.ph = coin_phase(d1)
        self.atrD = self.ind["1d"]["atr"]
        self.wt1 = self.wt2 = None
        self.fund = None

    def view(self, tf, sd):
        k = (tf, sd)
        if k not in self._view:
            B, I = self.B[tf], self.ind[tf]
            mxo, mno = I["em"].max(axis=0), I["em"].min(axis=0)
            if sd > 0:
                a = dict(o=B["o"], h=B["h"], l=B["l"], c=B["c"], mx=mxo, mn=mno, s20=I["s20"])
            else:
                a = dict(o=-B["o"], h=-B["l"], l=-B["h"], c=-B["c"], mx=-mno, mn=-mxo, s20=-I["s20"])
            a["atr"], a["t"] = I["atr"], B["t"]
            a["lists"] = {x: a[x].tolist() for x in ("o", "h", "l", "c", "mx", "mn")}
            self._view[k] = a
        return self._view[k]

    def level(self, sd):
        if sd not in self._lvl:
            d1 = self.B["1d"]
            self._lvl[sd] = weekly_low12(d1["t"], d1["l"] if sd > 0 else -d1["h"])
        return self._lvl[sd]

    def add_wt(self):
        from wavetrend import compute
        d1 = self.B["1d"]
        rows = compute(list(zip(d1["t"].tolist(), d1["h"].tolist(), d1["l"].tolist(), d1["c"].tolist())), DAY)
        self.wt1 = np.array([r.wt1 for r in rows])
        self.wt2 = np.array([r.wt2 for r in rows])

    def add_funding(self, path):
        if not Path(path).exists():
            return
        rows = list(csv.reader(open(path)))
        assert rows[0] == ["ts", "rate"], f"funding header {rows[0]}"
        ts = np.array([int(r[0]) for r in rows[1:]], np.int64)
        assert (np.diff(ts) > 0).all()
        self.fund = (ts, np.array([float(r[1]) for r in rows[1:]]))


def fund_flag(fund, Td):
    """1 = mean of the last 3 settled prints (ts <= Td) <= 0.03% per 8h; 0 = crowded; -1 = no data."""
    Td = np.asarray(Td)
    if fund is None:
        return np.full(len(Td), -1, np.int8)
    ts, r = fund
    k = np.searchsorted(ts, Td, side="right") - 1
    cs = np.cumsum(np.r_[0.0, r])
    kk = np.maximum(k, 2)
    mean = (cs[kk + 1] - cs[kk - 2]) / 3
    return np.where(k < 2, -1, np.where(mean <= FUND_MAX, 1, 0)).astype(np.int8)


class Market:
    """BTC-derived context shared by all coins: cycle label per date (phase_daily.csv, lag 1 inside the file) and BTC SMA20/SMA50."""

    def __init__(self, btc_d1, cyc_days, cyc_codes):
        self.cd, self.cc = cyc_days, cyc_codes
        c = btc_d1["c"]
        self.bt = btc_d1["t"]
        self.c8 = ((c > sma(c, 20)) & (c > sma(c, 50))).astype(np.int8)
        self.above200 = (c > sma(c, 200)).astype(np.int8)

    def cycle_at(self, T):
        d = np.asarray(T) // DAY + (1 if bug() == "1" else 0)
        k = np.searchsorted(self.cd, d)
        kk = np.minimum(k, len(self.cd) - 1)
        return np.where((k < len(self.cd)) & (self.cd[kk] == d), self.cc[kk], -1).astype(np.int8)

    def c8_at(self, T):
        k = prior_day_idx(self.bt, T)
        return np.where(k >= 0, self.c8[np.maximum(k, 0)], -1).astype(np.int8)


def load_cycle():
    days, codes = [], []
    for r in csv.DictReader(open(PHASE_CSV)):
        if r["provisional"] == "True" or r["label"] == "":
            continue
        import datetime as dt
        days.append(dt.date.fromisoformat(r["date"]).toordinal() - 719163)
        codes.append(CYC[r["label"]])
    return np.array(days, np.int64), np.array(codes, np.int8)


def attrs(co, mk, tf, sd, s, F, is_btc):
    """context attributes of signal bars s (first close = s-1), all read from closed bars before the first close."""
    V = co.view(tf, sd)
    t = V["t"]
    step = H4 if tf == "4h" else DAY
    f = s - 1
    Tf, Ts = t[f], t[s]
    d1t = co.B["1d"]["t"]
    kp = prior_day_idx(d1t, Tf)
    ph = np.where(kp >= 0, co.ph[np.maximum(kp, 0)], PH_NA).astype(np.int8)
    ends, w12 = co.level(sd)
    L = level_at(ends, w12, Ts)
    ka = prior_day_idx(d1t, Ts)
    atrD = np.where(ka >= 0, co.atrD[np.maximum(ka, 0)], np.nan)
    with np.errstate(invalid="ignore"):
        lvl = np.where(np.isnan(L) | np.isnan(atrD) | np.isnan(F), -1, (np.abs(F - L) <= AT_ATR * atrD).astype(np.int8)).astype(np.int8)
    Td = Ts + step
    if sd > 0 and co.wt1 is not None:
        jd = np.searchsorted(d1t + DAY, Td, side="right") - 1
        w1, w2 = co.wt1[np.maximum(jd, 0)], co.wt2[np.maximum(jd, 0)]
        with np.errstate(invalid="ignore"):
            wt = ((jd >= 0) & (w1 < WT_OB2) & (w1 > w2)).astype(np.int8)
    else:
        wt = np.zeros(len(s), np.int8)
    fl = fund_flag(co.fund, Td) if sd > 0 else np.full(len(s), -1, np.int8)
    return dict(s=s, t=Ts, ph=ph, cyc=mk.cycle_at(Tf), lvl=lvl, wt=wt, fund=fl, c8=np.where(is_btc, -1, mk.c8_at(Tf)).astype(np.int8),
                split=split_of(Ts), day=(Ts // DAY).astype(np.int64))


def entries(co, tf, sd, entry, s):
    """entry bar and price per signal (valid flag). market: next open; limit: SMA20 (fixed at s) filled within s+1..s+5."""
    V = co.view(tf, sd)
    n = len(V["c"])
    i0 = np.full(len(s), -1, np.int64)
    e = np.full(len(s), np.nan)
    o, l = V["o"], V["l"]
    for j, si in enumerate(s):
        if entry == "mkt":
            if si + 1 < n:
                i0[j], e[j] = si + 1, o[si + 1]
        else:
            lim = V["s20"][si]
            for t in range(si + 1, min(si + LIM_BARS, n - 1) + 1):
                if l[t] <= lim:
                    i0[j], e[j] = t, min(o[t], lim)
                    break
    return i0, e


def run_trades(co, tf, sd, entry, s, i0, e):
    V = co.view(tf, sd)
    L_ = V["lists"]
    fl = FLOOR[tf]
    out = {k: np.full(len(s), np.nan) for k in ("g", "f12", "f6", "dist", "cens")}
    for j, si in enumerate(s):
        if i0[j] < 0:
            continue
        ej = float(e[j])
        d = max(ej - L_["mn"][si], fl * abs(ej), MIN_ATR_MULT * V["atr"][si])
        if not d > 0:
            continue
        g, x1, x2, half, xi, cens = sim_long(L_["o"], L_["h"], L_["l"], L_["c"], L_["mx"], L_["mn"], int(i0[j]), ej, d, entry == "lim")
        out["g"][j], out["dist"][j], out["cens"][j] = g, d, cens
        out["f12"][j] = fee_r(BP["taker"], ej, x1, x2, half, d)
        out["f6"][j] = fee_r(BP["maker"], ej, x1, x2, half, d)
    return out


def cell_mask(A, cl, btc_excl=True):
    """boolean mask of rows of attribute dict A that belong to cell cl. Controls and primary cells are disjoint by phase/cycle/level/variant fields."""
    m = (A["ph"] == cl["ph"]) & (A["lvl"] == (1 if cl["lvl"] == "at" else 0))
    if cl["cyc"] is not None:
        m &= np.isin(A["cyc"], [CYC[x] for x in cl["cyc"]])
    if cl["var"] in ("V1", "V2"):
        m &= A["wt"] == 1
    if cl["var"] == "V2":
        m &= A["fund"] == 1
    if cl["c8"]:
        m &= A["c8"] == 1
    return m


# ------------------------------------------------------------------ statistics
def boot_ci_low(x, B, seed):
    x = np.asarray(x, float)
    n = len(x)
    if n < 2:
        return np.nan
    rng = np.random.default_rng(seed)
    means = []
    step = max(1, 4_000_000 // n)
    for a in range(0, B, step):
        k = min(step, B - a)
        means.append(x[rng.integers(0, n, (k, n))].mean(axis=1))
    return float(np.percentile(np.concatenate(means), 2.5))


def cluster_boot(x, key, B, seed):
    """returns (ci_low, p_one_sided for mean<=0) by resampling clusters."""
    x = np.asarray(x, float)
    if len(x) < 2:
        return np.nan, np.nan
    u, inv = np.unique(key, return_inverse=True)
    S, N = np.bincount(inv, weights=x), np.bincount(inv).astype(float)
    K = len(u)
    rng = np.random.default_rng(seed)
    m = np.empty(B)
    step = max(1, 4_000_000 // K)
    for a in range(0, B, step):
        k = min(step, B - a)
        d = rng.integers(0, K, (k, K))
        m[a:a + k] = S[d].sum(axis=1) / N[d].sum(axis=1)
    return float(np.percentile(m, 2.5)), float((1 + (m <= 0).sum()) / (B + 1))


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


def placebo_p(real_net, real_coin, pool_net, pool_coin, seed):
    """real trades vs random pool entries of the SAME coin (pool already restricted to the same cell attributes), matched count per coin.
    Returns (matched real mean, placebo mean, p = (1+#placebo>=real)/(N+1), matched n, coverage)."""
    rng = np.random.default_rng(seed)
    tot = np.zeros(N_PLACEBO)
    n_used, real_sum = 0, 0.0
    for cname in np.unique(real_coin):
        r = real_net[real_coin == cname]
        pl = pool_net[pool_coin == cname]
        if len(pl) == 0:
            continue
        n_used += len(r)
        real_sum += r.sum()
        tot += pl[rng.integers(0, len(pl), (N_PLACEBO, len(r)))].sum(axis=1)
    if n_used == 0:
        return np.nan, np.nan, np.nan, 0, 0.0
    rm, pm = real_sum / n_used, tot / n_used
    return float(rm), float(pm.mean()), float((1 + (pm >= rm).sum()) / (N_PLACEBO + 1)), n_used, n_used / len(real_net)


def stats_block(g, f12, f6, day, seed, full=True):
    n = len(g)
    net12, net6 = g - f12, g - f6
    st = dict(n=int(n))
    if n == 0:
        return st
    st.update(gross=float(g.mean()), net12=float(net12.mean()), net6=float(net6.mean()), win=float((net12 > 0).mean() * 100),
              ex5=float(np.sort(net12)[:-5].mean()) if n > 5 else np.nan)
    if full:
        st["ci_trade"] = boot_ci_low(net12, B_TRADE, seed)
        st["ci_72h"], st["p72"] = cluster_boot(net12, day // 3, B_CLUSTER, seed + 1)
        st["ci_day"], _ = cluster_boot(net12, day, B_CLUSTER, seed + 2)
    return st


def verdict_cell(st, primary, q):
    n = st.get("n", 0)
    if not primary:
        return "CONTROL"
    if n < 100:
        return "UNDERPOWERED"
    gates = [st["net12"] > 0, st["ci_trade"] > 0, st["ci_72h"] > 0, st["ci_day"] > 0, st["ex5"] > 0,
             st.get("plc_beaten", False), q is not None and q <= 0.10]
    if all(gates):
        return "PASS" if n >= 200 else "UNDERPOWERED (n 100-199, cannot pass)"
    return "FAIL"


# ------------------------------------------------------------------ build and run
def git(*a):
    return subprocess.run(["git", "-C", str(REPO)] + list(a), capture_output=True, text=True).stdout.strip()


def committed_check():
    rel = HERE.relative_to(REPO).as_posix()
    dirty = [x for x in git("status", "--porcelain", "--", rel).splitlines() if not x.split()[-1].endswith(("results.json", "RESULT.md", "counts.json"))]
    if dirty:
        raise SystemExit("refusing: uncommitted study files: " + "; ".join(dirty))
    return git("log", "-1", "--format=%H", "--", rel + "/study.py", rel + "/PRE_REG.md")


def build_universe(coins, spot_dir, step, tag, with_funding):
    out, prov = [], []
    for sym in coins:
        base, p = load_base(Path(spot_dir) / (f"{sym}USDT_15m.npz" if step == 900000 else f"{sym}USDT_5m.npz"), step)
        d1, h4 = build_tfs(base, step)
        co = Coin(sym, d1, h4)
        co.add_wt()
        if with_funding:
            co.add_funding(FUND / f"{sym}USDT_funding.csv")
        p.update(coin=sym, set=tag, daily_first=int(d1["t"][0]), daily_last=int(d1["t"][-1]), h4_bars=int(len(h4["t"])),
                 funding=co.fund is not None)
        prov.append(p)
        out.append(co)
        print("loaded", sym, tag, len(d1["t"]), "days", flush=True)
    return out, prov


def collect(cos, mk, simulate):
    """per set key: dict of concatenated arrays over coins (attributes, and results if simulate)."""
    res = {}
    for key in SETKEYS:
        tf, sd, W, entry = key
        parts = []
        for ci, co in enumerate(cos):
            V = co.view(tf, sd)
            s, F = find_signals(V["c"], V["h"], V["l"], V["mx"], V["mn"], V["atr"], W)
            if len(s) == 0:
                continue
            A = attrs(co, mk, tf, sd, s, F, co.sym == "BTC")
            i0, e = entries(co, tf, sd, entry, s)
            A["valid"] = i0 >= 0
            A["coin"] = np.full(len(s), ci, np.int16)
            if simulate:
                A.update(run_trades(co, tf, sd, entry, s, i0, e))
            parts.append(A)
        res[key] = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]} if parts else {}
    return res


def collect_pool(cos, mk):
    """placebo pools (VALIDATION signal bars only): bars with two closes above the stack, any width, any fall; simulated with the same stop/exit/fee."""
    res = {}
    for key in POOLKEYS:
        tf, sd, entry = key
        parts = []
        for ci, co in enumerate(cos):
            V = co.view(tf, sd)
            b, F = pool_bars(V["c"], V["mx"], V["l"])
            keep = V["t"][b] >= SPLIT
            b, F = b[keep], F[keep]
            if len(b) == 0:
                continue
            A = attrs(co, mk, tf, sd, b, F, co.sym == "BTC")
            i0, e = entries(co, tf, sd, entry, b)
            A["valid"] = i0 >= 0
            A["coin"] = np.full(len(b), ci, np.int16)
            A.update(run_trades(co, tf, sd, entry, b, i0, e))
            parts.append(A)
        res[key] = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]} if parts else {}
        print("pool", key, len(res[key].get("s", [])), flush=True)
    return res


def usable(T):
    return (T["valid"]) & np.isfinite(T["g"]) if "g" in T else T["valid"]


def counts_only(T_by_key, cos):
    rows = {}
    for cl in CELLS:
        T = T_by_key[(cl["tf"], cl["sd"], cl["W"], cl["entry"])]
        m = cell_mask(T, cl) & T["valid"]
        rows[cl["id"]] = dict(dev=int((m & (T["split"] == 0)).sum()), val=int((m & (T["split"] == 1)).sum()))
    # at-level share of V0 signals in the primary phase/cycle (counts only)
    T = T_by_key[("1d", 1, .03, "mkt")]
    base = (T["ph"] == PH_RANGE) & np.isin(T["cyc"], [CYC["ACCUM-RANGE"]]) & T["valid"]
    share = {}
    for sp, nm in ((0, "dev"), (1, "val")):
        mm = base & (T["split"] == sp)
        share[nm] = dict(n=int(mm.sum()), at=int((mm & (T["lvl"] == 1)).sum()), away=int((mm & (T["lvl"] == 0)).sum()), na=int((mm & (T["lvl"] == -1)).sum()))
    p1 = rows["P1"]
    v1 = {}
    for sp, nm in ((0, "dev"), (1, "val")):
        mm = cell_mask(T, CELLS[0]) & T["valid"] & (T["split"] == sp)
        v1[nm] = dict(v0=int(mm.sum()), v1_removes=int((mm & (T["wt"] != 1)).sum()), v2_nodata=int((mm & (T["fund"] == -1)).sum()),
                      v2_crowded=int((mm & (T["fund"] == 0)).sum()))
    return dict(cells=rows, at_level_share=share, v1_v2_effect=v1, p1_val=p1["val"])


def regime_mix(cos, mk):
    out = {}
    for sp, nm in ((0, "DEV"), (1, "VAL")):
        cnt = np.zeros(4)
        for co in cos:
            d1 = co.B["1d"]
            k = prior_day_idx(d1["t"], d1["t"])  # phase read at prior close for each coin-day
            ph = np.where(k >= 0, co.ph[np.maximum(k, 0)], PH_NA)
            ok = (ph != PH_NA) & (split_of(d1["t"]) == sp) & (d1["t"] >= 1609459200000 + 59 * DAY)  # from 2021-03-01
            for j, p in enumerate((PH_UP, PH_DOWN, PH_RANGE)):
                cnt[j] += ((ph == p) & ok).sum()
            cnt[3] += ok.sum()
        sh = (cnt[:3] / cnt[3] * 100).round(1).tolist()
        d = np.arange(1614556800000, 1799999999999, DAY)
        d = d[(split_of(d) == sp) & (d < cos[0].B["1d"]["t"][-1])]
        cyc = mk.cycle_at(d)
        cs = {n: round(float((cyc == i).mean() * 100), 1) for i, n in enumerate(CYC_NAMES)}
        kb = prior_day_idx(mk.bt, d)
        ab = float(np.mean(mk.above200[kb[kb >= 0]]) * 100)
        mixed = max(sh) <= 50
        out[nm] = dict(coin_days=int(cnt[3]), UP=sh[0], DOWN=sh[1], RANGE=sh[2], mixed=bool(mixed), btc_cycle=cs, btc_above_sma200=round(ab, 1))
    return out


def cell_results(T, P, cos, universe_names):
    """full stats for every cell on VAL (gated) and DEV (descriptive)."""
    res = {}
    prim_p = []
    for cl in CELLS:
        key = (cl["tf"], cl["sd"], cl["W"], cl["entry"])
        Tk = T[key]
        m = cell_mask(Tk, cl) & usable(Tk)
        row = dict(id=cl["id"], status=cl["status"], note=cl["note"], n_signals_dev=int((cell_mask(Tk, cl) & Tk["valid"] & (Tk["split"] == 0)).sum()),
                   n_signals_val=int((cell_mask(Tk, cl) & Tk["valid"] & (Tk["split"] == 1)).sum()))
        for sp, nm in ((0, "dev"), (1, "val")):
            mm = m & (Tk["split"] == sp)
            st = stats_block(Tk["g"][mm], Tk["f12"][mm], Tk["f6"][mm], Tk["day"][mm], 100 + 10 * CELLS.index(cl) + sp, full=(sp == 1))
            row[nm] = st
        vm = m & (Tk["split"] == 1)
        # placebo (VAL)
        Pk = P[(cl["tf"], cl["sd"], cl["entry"])]
        pm = cell_mask(Pk, cl) & usable(Pk)
        if vm.sum() > 0 and pm.sum() > 0:
            rm, plm, p, nu, cov = placebo_p((Tk["g"] - Tk["f12"])[vm], Tk["coin"][vm], (Pk["g"] - Pk["f12"])[pm], Pk["coin"][pm], 900 + CELLS.index(cl))
            row["placebo"] = dict(real_matched=rm, placebo_mean=plm, p=p, n_matched=nu, coverage=cov, pool_n=int(pm.sum()))
            row["val"]["plc_beaten"] = bool(p < 0.05 and rm > plm)
        else:
            row["placebo"] = dict(p=None, pool_n=int(pm.sum()))
            row["val"]["plc_beaten"] = False
        row["censored_val"] = int(np.nansum(Tk["cens"][vm])) if vm.any() else 0
        row["coins_val"] = int(len(np.unique(Tk["coin"][vm])))
        res[cl["id"]] = row
        if cl["status"] == "PRIMARY":
            prim_p.append((cl["id"], row["val"].get("p72", np.nan) if row["val"]["n"] > 1 else 1.0))
    q = bh_q([p if p == p else 1.0 for _, p in prim_p])
    for (cid, p), qq in zip(prim_p, q):
        res[cid]["val"]["bh_q"], res[cid]["val"]["p_bh"] = float(qq), float(p)
    for cl in CELLS:
        r = res[cl["id"]]
        r["verdict"] = verdict_cell(r["val"], cl["status"] == "PRIMARY", r["val"].get("bh_q"))
    return res


def extra_tables(T, cos):
    """descriptive: C4 broken down by BTC cycle label (VAL); level comparison at vs away for the primary phase/cycle (VAL and DEV); by-coin n."""
    out = {}
    Tk = T[("1d", 1, .03, "mkt")]
    c4 = CELLS[6]
    base = cell_mask(Tk, c4) & usable(Tk)
    sub = {}
    for i, nm in enumerate(CYC_NAMES):
        for sp, sn in ((0, "dev"), (1, "val")):
            mm = base & (Tk["cyc"] == i) & (Tk["split"] == sp)
            sub.setdefault(nm, {})[sn] = stats_block(Tk["g"][mm], Tk["f12"][mm], Tk["f6"][mm], Tk["day"][mm], 7, full=False)
    out["c4_by_cycle"] = sub
    lv = {}
    for sp, sn in ((0, "dev"), (1, "val")):
        a = {}
        for nm, lvl in (("at", 1), ("away", 0)):
            mm = (Tk["ph"] == PH_RANGE) & np.isin(Tk["cyc"], [CYC["ACCUM-RANGE"]]) & (Tk["lvl"] == lvl) & usable(Tk) & (Tk["split"] == sp)
            a[nm] = stats_block(Tk["g"][mm], Tk["f12"][mm], Tk["f6"][mm], Tk["day"][mm], 8, full=False)
        lv[sn] = a
    out["level_comparison"] = lv
    return out


def main(mode):
    if mode == "run" and not os.environ.get("NKN_ALLOW_DIRTY"):
        pre_hash = committed_check()
    else:
        pre_hash = git("log", "-1", "--format=%H", "--", HERE.relative_to(REPO).as_posix())
    cos, prov = build_universe(COINS, SPOT, 900000, "gated", True)
    assert cos[0].sym == "BTC"
    cd, cc = load_cycle()
    mk = Market(cos[0].B["1d"], cd, cc)
    if mode == "counts":
        T = collect(cos, mk, False)
        out = counts_only(T, cos)
        out["regime_mix"] = regime_mix(cos, mk)
        (HERE / "counts.json").write_text(json.dumps(out, indent=1))
        print(json.dumps(out["cells"]))
        print(json.dumps(out["at_level_share"]))
        print(json.dumps(out["v1_v2_effect"]))
        print(json.dumps(out["regime_mix"], indent=1))
        return
    T = collect(cos, mk, True)
    P = collect_pool(cos, mk)
    res = cell_results(T, P, cos, COINS)
    extra = extra_tables(T, cos)
    # fresh holdout: descriptive, never pooled
    fcos, fprov = build_universe(FRESH_COINS, FRESH, 300000, "fresh", False)
    FT = collect(fcos, mk, True)
    fresh = {}
    for cl in CELLS:
        Tk = FT[(cl["tf"], cl["sd"], cl["W"], cl["entry"])]
        m = cell_mask(Tk, cl) & usable(Tk) & (Tk["split"] == 1)
        fresh[cl["id"]] = stats_block(Tk["g"][m], Tk["f12"][m], Tk["f6"][m], Tk["day"][m], 55, full=True) if m.any() else dict(n=0)
    best = None
    for cid in ("P1", "P2", "P3"):
        v = res[cid]["val"]
        if v["n"] > 0 and (best is None or v["net12"] > res[best]["val"]["net12"]):
            best = cid
    prim = [res[c]["verdict"] for c in ("P1", "P2", "P3")]
    overall = "PASS" if "PASS" in prim else ("UNDERPOWERED" if all(v.startswith("UNDERPOWERED") for v in prim) else "FAIL")
    out = dict(overall=overall, best_primary=best, prereg_code_commit=pre_hash, head=git("rev-parse", "HEAD"), cells=res, extra=extra,
               fresh_val_descriptive=fresh, regime_mix=regime_mix(cos, mk), provenance=prov + fprov, total_cells=len(CELLS),
               primary_cells=3, universe=COINS, fresh_universe=FRESH_COINS)
    (HERE / "results.json").write_text(json.dumps(out, indent=1, default=lambda x: None if x != x else float(x)))
    print("overall", overall, "best", best)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "counts")
