"""Test 2 (multi-timeframe context rule, both sides) rule library. Every rule is in PRE_REG.md; labels there.
All indicators are computed on CLOSED bars only; pivots are used only from their confirmation bar on."""
import os

import numpy as np

CACHE = os.environ.get("BZ2_CACHE", "C:/Users/e-ngineers/mts_cache/buyzone_test2")
H4, DAY = 4 * 3600_000, 86_400_000
UP, BASE, DOWN, BEAR, RANGE = 1, 2, 3, 4, 5
PHASE_NAME = {0: "n/a", 1: "UP", 2: "BASE", 3: "DOWN", 4: "BEAR", 5: "RANGE"}
HOLD_BARS = 60            # 10 days of 4H bars
LOCKOUT_MS = 10 * DAY
CTX_MS = 28 * DAY
K4H, KHTF = 3, 2          # pivot half-widths (4H, HTF)
MAX_RISK = 0.10           # skip setups with stop farther than 10% of entry


def load(sym, tf):
    a = np.load(f"{CACHE}/{sym}USDT_{tf}.npy")
    return a[:-1]  # drop the still-forming last bar


# ---------- indicators ----------
def sma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        c = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def rma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    out[n - 1] = np.mean(x[:n])
    for i in range(n, len(x)):
        out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return out


def ema(x, n):
    out = np.full(len(x), np.nan)
    a = 2.0 / (n + 1)
    s = np.nan
    for i, v in enumerate(x):
        if np.isnan(v):
            continue
        s = v if np.isnan(s) else a * v + (1 - a) * s
        out[i] = s
    return out


def rsi(c, n=14):
    d = np.diff(c)
    au, ad = rma(np.where(d > 0, d, 0.0), n), rma(np.where(d < 0, -d, 0.0), n)
    au, ad = np.insert(au, 0, np.nan), np.insert(ad, 0, np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 100 - 100 / (1 + au / ad)


def wavetrend(h, l, c, n1=10, n2=21):
    ap = (h + l + c) / 3
    esa = ema(ap, n1)
    d = ema(np.abs(ap - esa), n1)
    with np.errstate(divide="ignore", invalid="ignore"):
        ci = (ap - esa) / (0.015 * d)
    return ema(ci, n2)


def atr(h, l, c, n=14):
    pc = np.roll(c, 1)
    pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return rma(tr, n)


def dmi(h, l, c, n=14):
    up = h - np.roll(h, 1)
    dn = np.roll(l, 1) - l
    up[0] = dn[0] = 0
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = atr(h, l, c, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 100 * rma(pdm, n) / a, 100 * rma(mdm, n) / a


# ---------- daily phase (value at index d uses data through the close of day d) ----------
def phases(d):
    h, l, c = d[:, 2], d[:, 3], d[:, 4]
    n = len(c)
    s200, s350 = sma(c, 200), sma(c, 350)
    rising = np.zeros(n, bool)
    with np.errstate(invalid="ignore"):
        rising[20:] = s200[20:] > s200[:-20]
    pdi, mdi = dmi(h, l, c)
    hi540 = np.full(n, np.nan)
    for i in range(349, n):
        hi540[i] = h[max(0, i - 539):i + 1].max()
    with np.errstate(invalid="ignore"):
        above = c > s200
        deep = c <= 0.6 * hi540
        a20 = np.zeros(n, bool)
        for i in range(19, n):
            a20[i] = above[i - 19:i + 1].all()
        up = above & rising & (pdi > mdi)
        base = ~up & deep & a20
        bear = ~up & ~base & deep & (c < s350)
        down = ~up & ~base & ~bear & (c < s200) & (mdi > pdi)
    ok = ~np.isnan(s350) & ~np.isnan(hi540) & ~np.isnan(pdi)
    ph = np.where(up, UP, np.where(base, BASE, np.where(bear, BEAR, np.where(down, DOWN, RANGE))))
    return np.where(ok, ph, 0).astype(np.int8)


def phase_for_4h(d4, dd, ph):
    """Phase for each 4H bar = phase of the daily bar of the day BEFORE the bar's open day."""
    prev = (d4[:, 0] // DAY) * DAY - DAY
    pos = np.clip(np.searchsorted(dd[:, 0], prev), 0, len(dd) - 1)
    return np.where(dd[pos, 0] == prev, ph[pos], 0).astype(np.int8)


# ---------- pivots ----------
def pivots(h, l, k):
    """Bar indexes of pivot highs/lows. Pivot i is KNOWN only from bar i+k (its close)."""
    phs, pls = [], []
    for i in range(k, len(h) - k):
        if h[i] > h[i - k:i].max() and h[i] >= h[i + 1:i + k + 1].max():
            phs.append(i)
        if l[i] < l[i - k:i].min() and l[i] <= l[i + 1:i + k + 1].min():
            pls.append(i)
    return np.array(phs, int), np.array(pls, int)


def last_pivot_level(n, piv_idx, level, k):
    """Level of the most recent pivot CONFIRMED at or before each bar (pivot p known at bar p+k); NaN before the first."""
    out = np.full(n, np.nan)
    for p in piv_idx:
        if p + k < n:
            out[p + k] = level[p]
    m = ~np.isnan(out)
    idx = np.where(m, np.arange(n), 0)
    np.maximum.accumulate(idx, out=idx)
    res = out[idx]
    res[np.cumsum(m) == 0] = np.nan
    return res


# ---------- HTF divergence context ----------
def divergence_times(a, period_ms, osc="rsi", k=KHTF, gap=(3, 30)):
    """Availability times (ms; close of the confirming bar) of bullish and bearish divergences on an HTF array."""
    h, l, c = a[:, 2], a[:, 3], a[:, 4]
    o = rsi(c) if osc == "rsi" else wavetrend(h, l, c)
    phs, pls = pivots(h, l, k)
    bull, bear = [], []
    for x, y in zip(pls[:-1], pls[1:]):
        if gap[0] <= y - x <= gap[1] and l[y] < l[x] and o[y] > o[x]:
            bull.append(a[y + k, 0] + period_ms)
    for x, y in zip(phs[:-1], phs[1:]):
        if gap[0] <= y - x <= gap[1] and h[y] > h[x] and o[y] < o[x]:
            bear.append(a[y + k, 0] + period_ms)
    return np.sort(np.array(bull, float)), np.sort(np.array(bear, float))


def active(avail, tc):
    """True where at least one signal became available in (tc-28d, tc]."""
    if len(avail) == 0:
        return np.zeros(len(tc), bool)
    return (np.searchsorted(avail, tc, "right") - np.searchsorted(avail, tc - CTX_MS, "right")) > 0


# ---------- per-coin 4H structure ----------
class Coin:
    def __init__(self, sym, osc="rsi"):
        self.sym = sym
        a = self.a = load(sym, "4h")
        self.t, self.o, self.h, self.l, self.c = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        n = self.n = len(a)
        dd = load(sym, "1d")
        self.phase = phase_for_4h(a, dd, phases(dd))
        self.atr = atr(self.h, self.l, self.c)
        phs, pls = pivots(self.h, self.l, K4H)
        self.PH = last_pivot_level(n, phs, self.h, K4H)
        self.PL = last_pivot_level(n, pls, self.l, K4H)
        tc = self.t + H4
        b3, s3 = divergence_times(load(sym, "3d"), 3 * DAY, osc)
        b1, s1 = divergence_times(load(sym, "1w"), 7 * DAY, osc)
        self.ctx_long = active(np.sort(np.r_[b3, b1]), tc)
        self.ctx_short = active(np.sort(np.r_[s3, s1]), tc)
        c, pc = self.c, np.roll(self.c, 1)
        with np.errstate(invalid="ignore"):
            self.brk_up = (c > self.PH) & ~(pc > self.PH)
            self.brk_dn = (c < self.PL) & ~(pc < self.PL)
        self.brk_up[0] = self.brk_dn[0] = False


def setup(co, j, side):
    """(entry, stop, risk) for a signal decided at the close of bar j, entry at the open of j+1; None if invalid."""
    if j + 1 + HOLD_BARS >= co.n:
        return None
    e = co.o[j + 1]
    piv = co.PL[j] if side > 0 else co.PH[j]
    if np.isnan(piv):
        return None
    buf = max(0.6 * co.atr[j], 0.005 * e)
    stop = piv - buf if side > 0 else piv + buf
    risk = (e - stop) if side > 0 else (stop - e)
    if np.isnan(risk) or risk <= 0 or risk / e > MAX_RISK:
        return None
    return e, stop, risk


def planned_hold(co, ent, side):
    """Bars from entry to exit open ignoring the stop: first opposite raw 4H break (exit at next open) or 10 days."""
    opp = co.brk_dn if side > 0 else co.brk_up
    for k in range(ent, ent + HOLD_BARS):
        if opp[k]:
            return k + 1 - ent
    return HOLD_BARS


def simulate(co, j, side, hold=None):
    """Run a trade decided at bar j. hold=None: real exit rule; hold=int: fixed time exit (placebo).
    Stop is checked on every bar from the entry bar, stop first inside a bar; a gap through the stop fills at the open."""
    s = setup(co, j, side)
    if s is None:
        return None
    e, stop, risk = s
    ent = j + 1
    planned = planned_hold(co, ent, side) if hold is None else hold
    for k in range(ent, ent + planned):
        if side > 0 and co.l[k] <= stop:
            fill = min(stop, co.o[k]) if k > ent else stop
            return dict(entry_bar=ent, exit_bar=k, gross_R=(fill - e) / risk, planned=planned, stopped=True, entry=e, risk=risk)
        if side < 0 and co.h[k] >= stop:
            fill = max(stop, co.o[k]) if k > ent else stop
            return dict(entry_bar=ent, exit_bar=k, gross_R=(e - fill) / risk, planned=planned, stopped=True, entry=e, risk=risk)
    x = co.o[ent + planned]
    return dict(entry_bar=ent, exit_bar=ent + planned, gross_R=side * (x - e) / risk, planned=planned, stopped=False, entry=e, risk=risk)


def net(r, fee_bp):
    return r["gross_R"] - fee_bp / 1e4 * r["entry"] / r["risk"]


SIDES = ((1, "brk_up", (UP, BASE), "ctx_long"), (-1, "brk_dn", (DOWN, BEAR), "ctx_short"))


def real_trades(co, ctx="on"):
    """Gated trades for one coin. ctx='on': HTF divergence context required; 'off': control without context."""
    out, last_entry_t = [], -1e18
    for j in range(1, co.n - HOLD_BARS - 2):
        for side, brk, phs, cx in SIDES:
            if not getattr(co, brk)[j] or co.phase[j] not in phs:
                continue
            if ctx == "on" and not getattr(co, cx)[j]:
                continue
            if co.t[j + 1] - last_entry_t < LOCKOUT_MS:
                continue
            r = simulate(co, j, side)
            if r is None:
                continue
            last_entry_t = co.t[j + 1]
            r.update(side=side, phase=int(co.phase[j]), coin=co.sym, t=int(co.t[j + 1]))
            out.append(r)
    return out
