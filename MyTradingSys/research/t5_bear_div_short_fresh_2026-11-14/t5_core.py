"""T5 core: bear-phase 4h bearish-divergence short, re-implemented from the frozen PRE_REG.md (read it first).

Source cell: buyzone_test3_bear4h_2026-11-14 (PRE_REG.md, bear4h.py). Nothing is imported from it.
All indicators use closed bars only. A swing high at bar i is known only at the close of bar i+K.
numpy only (no pandas), pure functions, no file or cache access here.
Parameter labels: SOURCED = copied unchanged from the source cell named in PRE_REG.md; OURS = stated there as ours.
"""
import datetime as _dt
import os
import sys

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, _ROOT)
from MyTradingSys.backtest import fees  # noqa: E402

K = 3                      # swing half-width (SOURCED, bear4h.py K)
WARM4 = 100                # first 100 4h bars give no event and no placebo draw (SOURCED)
HOLD = 42                  # 7 days of 4h bars (SOURCED)
MIN_GAP, MAX_GAP = 6, 60   # bars between the two swing highs (SOURCED)
LOCK = 60                  # 10 days of 4h bars (SOURCED)
BB_N, BB_SD = 20, 2.0      # Bollinger (SOURCED)
ATR_N, RSI_N = 14, 14
STOP_ATR, STOP_MIN_FRAC, TRAIL_ATR = 0.6, 0.005, 2.0   # SOURCED
BAR = 4 * 3600 * 1000
DAY = 86400000
VAL_START = 1704067200000      # 2024-01-01 00:00 UTC (OURS, as the source)
RECENT_START = 1751328000000   # 2025-07-01 00:00 UTC (OURS)
RT_COST = fees.BINANCE_TAKER * 2 + fees.SLIPPAGE_RT_S13   # round trip, imported constants only
RT_COST_HALF = RT_COST / 2                                 # descriptive 6 bp row, arithmetic on the imported constant
T1_PHASES = ("UP", "BASE", "RANGE", "DOWN", "POSTPEAK_BEAR")


# ---------------------------------------------------------------- indicators (FORMULAS.md)
def wilder_atr(h, l, c, n=ATR_N):
    """ATR Wilder: seed = mean of first n true ranges (TR[0] = H-L), then (prev*(n-1)+TR)/n."""
    h, l, c = (np.asarray(a, float) for a in (h, l, c))
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    if len(c) > 1:
        pc = c[:-1]
        tr[1:] = np.maximum.reduce([h[1:] - l[1:], np.abs(h[1:] - pc), np.abs(l[1:] - pc)])
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def wilder_rsi(c, n=RSI_N):
    """RSI Wilder per FORMULAS.md section 1: seed = mean of first n gains / losses, then Wilder smoothing.
    avg_loss == 0: 100 if avg_gain > 0 else 50 (flat series)."""
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    up, dn = np.maximum(d, 0.0), np.maximum(-d, 0.0)
    au, ad = up[:n].mean(), dn[:n].mean()

    def val(a, b):
        if b == 0:
            return 100.0 if a > 0 else 50.0
        return 100.0 - 100.0 / (1.0 + a / b)

    out[n] = val(au, ad)
    for k in range(n + 1, len(c)):          # bar k uses the change c[k] - c[k-1] = d[k-1]
        au = (au * (n - 1) + up[k - 1]) / n
        ad = (ad * (n - 1) + dn[k - 1]) / n
        out[k] = val(au, ad)
    return out


def _roll(a, n, fn):
    """Trailing window of n values ending at each index; NaN until n values exist."""
    a = np.asarray(a, float)
    out = np.full(len(a), np.nan)
    if len(a) >= n:
        out[n - 1:] = fn(sliding_window_view(a, n), axis=1)
    return out


def _shift(a, k):
    out = np.full(len(a), np.nan)
    if k < len(a):
        out[k:] = a[:len(a) - k]
    return out


def sma(a, n):
    return _roll(a, n, np.mean)


def bollinger_upper(c):
    """SMA20(Close) + 2 x population sd20(Close), closed bars through each index."""
    return _roll(c, BB_N, np.mean) + BB_SD * _roll(c, BB_N, np.std)   # np.std default ddof=0


# ---------------------------------------------------------------- daily phase labels and BEAR flag
def base_lows(l):
    """(min Low[t-59..t], min Low[t-179..t-60]) per daily bar; NaN until 180 bars exist. The prior window is 120 bars wide
    (PRE_REG), i.e. a 120-bar rolling min shifted by 60."""
    l = np.asarray(l, float)
    return _roll(l, 60, np.min), _shift(_roll(l, 120, np.min), 60)


def daily_labels(h, l, c):
    """Test 1 phase label at daily bar t from bars <= t only. '' = not enough history (no phase)."""
    h, l, c = (np.asarray(a, float) for a in (h, l, c))
    sma200, sma350 = sma(c, 200), sma(c, 350)
    hi365 = np.empty(len(h))
    for i in range(len(h)):
        hi365[i] = h[max(0, i - 364):i + 1].max()           # min_periods = 1
    dd = 1 - c / hi365
    lo_recent, lo_prior = base_lows(l)
    hl = lo_recent >= lo_prior
    up = (c > sma200) & (sma200 > _shift(sma200, 30))
    base = ~up & (dd >= 0.40) & hl
    pp = ~up & ~base & (c < sma350) & (sma350 < _shift(sma350, 30)) & (dd >= 0.40)
    down = ~up & ~base & ~pp & (c < sma200) & (sma200 < _shift(sma200, 30))
    out = np.full(len(c), "RANGE", dtype=object)
    out[down] = "DOWN"
    out[pp] = "POSTPEAK_BEAR"
    out[base] = "BASE"
    out[up] = "UP"
    out[np.isnan(sma350) | np.isnan(lo_prior)] = ""
    return out


def daily_bear(h, l, c):
    """(bear flag, label) per daily bar. BEAR = Close < SMA350 and NOT base reclaim (label not UP/BASE); undefined = False."""
    c = np.asarray(c, float)
    lab = daily_labels(h, l, c)
    sma350 = sma(c, 350)
    bear = np.array([x not in ("", "UP", "BASE") for x in lab], dtype=bool) & (c < sma350)
    return bear, lab


def map_day_flag(ts4, dts, arr, fill, lag_days=1):
    """For each 4h bar, the daily value of UTC day (D - lag_days). lag_days = 1 is the frozen rule (previous closed day only);
    lag_days = 0 would read the entry day's own, not yet closed, daily bar and is a look-ahead."""
    ts4 = np.asarray(ts4)
    dts = np.asarray(dts)
    target = (ts4 // DAY - lag_days) * DAY
    idx = np.searchsorted(dts, target)
    ok = (idx < len(dts)) & (dts[np.minimum(idx, len(dts) - 1)] == target)
    out = np.full(len(ts4), fill, dtype=arr.dtype)
    out[ok] = arr[idx[ok]]
    return out


# ---------------------------------------------------------------- funding
def funding_cum(ts4, prints):
    """G[b] = sum of funding rates in bars 0..b. A print belongs to the 4h bar that contains its timestamp.
    prints: list of (ts_ms, rate). Returns (G, first_ts, last_ts); first/last None when there are no prints.
    A short held entry bar e .. exit bar x receives G[x] - G[e] (bars e+1..x)."""
    ts4 = np.asarray(ts4)
    n = len(ts4)
    f = np.zeros(n)
    if not len(prints):
        return np.cumsum(f), None, None
    for s, r in prints:
        b = int(np.searchsorted(ts4, s, side="right")) - 1
        if 0 <= b < n and s < ts4[b] + BAR:
            f[b] += r
    return np.cumsum(f), int(prints[0][0]), int(prints[-1][0])


# ---------------------------------------------------------------- signal
def swing_highs(h):
    """Indices i with High[i] > High[i-K..i-1] and High[i] > High[i+1..i+K] (strict). Known only at the close of bar i+K."""
    h = np.asarray(h, float)
    if len(h) < 2 * K + 1:
        return []
    w = sliding_window_view(h, 2 * K + 1)
    others = np.delete(w, K, axis=1).max(axis=1)
    return [int(i) + K for i in np.nonzero(w[:, K] > others)[0]]


def find_signals(o, h, l, c, n_avail=None):
    """Raw signals before lockout: sorted list of (c_idx, j_idx, stop0), using only bars < n_avail.
    Divergence: adjacent swing highs p < j (adjacent in the full swing list), 6 <= j-p <= 60, High[j] > High[p],
    RSI14[j] < RSI14[p], High[j] > upper Bollinger[j]. Signal bar c = j + K. stop0 = High[j] + max(0.6 ATR[c], 0.005 High[j])."""
    n = len(c) if n_avail is None else n_avail
    o, h, l, c = (np.asarray(a, float)[:n] for a in (o, h, l, c))
    atr, rsi, bb = wilder_atr(h, l, c), wilder_rsi(c), bollinger_upper(c)
    sw = [i for i in swing_highs(h) if i + K < n]
    sigs = []
    for a in range(1, len(sw)):
        p, j = sw[a - 1], sw[a]
        cc = j + K
        if not (MIN_GAP <= j - p <= MAX_GAP):
            continue
        if np.isnan(rsi[j]) or np.isnan(rsi[p]) or np.isnan(bb[j]) or np.isnan(atr[cc]):
            continue
        if h[j] > h[p] and rsi[j] < rsi[p] and h[j] > bb[j]:
            sigs.append((cc, j, float(h[j] + max(STOP_ATR * atr[cc], STOP_MIN_FRAC * h[j]))))
    sigs.sort()
    return sigs


# ---------------------------------------------------------------- exit simulation
def sim_exit(o, h, l, c, atr, e, stop0):
    """Exit of a short entered at Open[e]. Returns (exit_idx, exit_px, reason) or None if still open at the data end.
    Level at bar t > e = min(stop0, min Low[e..t-1] + 2 ATR[t-1]); on bar e only stop0. If High[t] >= level: exit at
    max(Open[t], level) (stop is checked first, so it wins any tie with the time exit). Time exit: Close[e+HOLD-1]."""
    n = len(c)
    mn = np.inf
    for t in range(e, min(e + HOLD - 1, n - 1) + 1):
        lvl = stop0 if t == e else min(stop0, mn + TRAIL_ATR * atr[t - 1])
        if h[t] >= lvl:
            return t, float(max(o[t], lvl)), ("stop" if (t == e or lvl == stop0) else "trail")
        mn = min(mn, l[t])
        if t == e + HOLD - 1:
            return t, float(c[t]), "time"
    return None


def trade_R(gross, cost, fund, r, with_funding):
    """R = (gross - cost + funding) / r on the with-funding row, (gross - cost) / r without."""
    return (gross - cost + (fund if with_funding else 0.0)) / r


# ---------------------------------------------------------------- events
def build_events(coin, ts, o, h, l, c, bearA, labA, G, first_fund, last_fund=None, sigs=None, n_avail=None):
    """bearA / labA: per 4h bar, the daily flag / label read at the previous UTC day.
    Lockout runs over ALL labelled events of the coin (BEAR true and false), as the source's single event list does; the
    BEAR column then selects the claim sample. Returns (events, counts)."""
    m = len(c) if n_avail is None else n_avail
    ts, o, h, l, c = (np.asarray(a)[:m] for a in (ts, o, h, l, c))
    n = len(c)
    atr = wilder_atr(h, l, c)
    if sigs is None:
        sigs = find_signals(o, h, l, c)
    cnt = dict(n_signals=len(sigs), drop_warmup_end_nophase=0, drop_lockout=0, drop_entry_ge_stop=0, drop_open_at_end=0)
    ev, last_e, last_exit = [], -10**9, -10**9
    for cc, j, stop0 in sigs:
        e = cc + 1
        if e < WARM4 or e >= n or labA[e] == "":
            cnt["drop_warmup_end_nophase"] += 1
            continue
        if e < last_e + LOCK or e <= last_exit:
            cnt["drop_lockout"] += 1
            continue
        entry = float(o[e])
        if entry >= stop0:
            cnt["drop_entry_ge_stop"] += 1
            continue
        res = sim_exit(o, h, l, c, atr, e, stop0)
        if res is None:
            cnt["drop_open_at_end"] += 1
            continue
        x, px, reason = res
        covered = first_fund is not None and ts[e] >= first_fund
        gap = bool(covered and last_fund is not None and ts[x] + BAR > last_fund)
        ev.append(dict(coin=coin, sig=int(cc), j=int(j), e=int(e), x=int(x), stop0=float(stop0), entry=entry, px=px, reason=reason,
                       r=(stop0 - entry) / entry, gross=(entry - px) / entry, bars_held=int(x - e + 1),
                       fund=float(G[x] - G[e]), covered=bool(covered), fund_gap=gap,
                       bear=bool(bearA[e]), label=str(labA[e]), sig_ts=int(ts[cc]), entry_ts=int(ts[e]), exit_ts=int(ts[x])))
        last_e, last_exit = e, x
    return ev, cnt


# ---------------------------------------------------------------- split and calendar helpers
def split_of(sig_ts):
    """Split by the SIGNAL bar (open time ts of bar c): DEV = bar closed by 2023-12-31 23:59 UTC, i.e. opens before 2024-01-01;
    VAL = signal bar opens on or after 2024-01-01 00:00 UTC. RECENT (>= 2025-07-01) is a descriptive subset of VAL."""
    return "DEV" if sig_ts < VAL_START else "VAL"


def in_recent(sig_ts):
    return sig_ts >= RECENT_START


def iso_week(ts_ms):
    d = _dt.datetime.fromtimestamp(ts_ms / 1000.0, _dt.timezone.utc).isocalendar()
    return "%04d-W%02d" % (d[0], d[1])


def utc_year(ts_ms):
    return _dt.datetime.fromtimestamp(ts_ms / 1000.0, _dt.timezone.utc).year
