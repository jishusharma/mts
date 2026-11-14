"""T2 washout Supertrap LONG: pure functions (PRE_REG.md is the only source of rules).

Bars live on a full UTC hour grid: index i is the bar starting at t0 + i*HOUR_MS, missing bars are NaN.
Indicators restart inside every contiguous (no NaN) run, so no value ever uses data across a gap.
No function here reads the data cache; loading lives in trades.py / stats.py.
"""
import os
import sys

import numpy as np

sys.dont_write_bytecode = True

_HERE = os.path.dirname(os.path.abspath(__file__))
_BT = os.path.abspath(os.path.join(_HERE, "..", "..", "backtest"))
if _BT not in sys.path:
    sys.path.insert(0, _BT)
from fees import BINANCE_TAKER  # noqa: E402

HOUR_MS = 3_600_000
H4_MS = 4 * HOUR_MS
DAY_MS = 24 * HOUR_MS

SLIPPAGE_SIDE = 0.0001
FEE_RT_12 = 2 * (BINANCE_TAKER + SLIPPAGE_SIDE)  # 12 bp primary
FEE_RT_6 = 0.0006  # sensitivity row only

RSI_GATE = 40.0
TRAP_FRAC = 0.5
MAX_WAIT = 12
HOLD_BARS = 24
ATR_MULT = 1.0
D_FLOOR = 0.012
D_CAP = 0.10
EPISODE_GAP_MS = 72 * HOUR_MS


# ---------------------------------------------------------------- aggregation
def aggregate(t, o, h, l, c, v, base_ms, period_ms):
    """UTC-aligned aggregation of base bars to period bars. A period bar needs all its sub-bars."""
    t = np.asarray(t, dtype=np.int64)
    order = np.argsort(t, kind="stable")
    t = t[order]
    arrs = [np.asarray(x, dtype=float)[order] for x in (o, h, l, c, v)]
    keep = np.concatenate(([True], np.diff(t) != 0))
    t = t[keep]
    o, h, l, c, v = [a[keep] for a in arrs]
    n_sub = period_ms // base_ms
    bucket = t // period_ms
    ub, first, cnt = np.unique(bucket, return_index=True, return_counts=True)
    full = cnt == n_sub
    out_t, out_o, out_h, out_l, out_c, out_v = [], [], [], [], [], []
    for b, f in zip(ub[full], first[full]):
        sl = slice(f, f + n_sub)
        # sub-bars must be the exact expected timestamps (contiguous)
        if t[f] != b * period_ms or t[f + n_sub - 1] != b * period_ms + (n_sub - 1) * base_ms:
            continue
        out_t.append(b * period_ms)
        out_o.append(o[f])
        out_h.append(h[sl].max())
        out_l.append(l[sl].min())
        out_c.append(c[f + n_sub - 1])
        out_v.append(v[sl].sum())
    return (np.array(out_t, dtype=np.int64), np.array(out_o), np.array(out_h),
            np.array(out_l), np.array(out_c), np.array(out_v))


def to_grid(t, o, h, l, c, v, period_ms):
    """Compact bars -> full grid starting at the first bar. Returns dict with t0 and NaN-filled arrays."""
    t = np.asarray(t, dtype=np.int64)
    t0 = int(t[0])
    n = int((t[-1] - t0) // period_ms) + 1
    idx = ((t - t0) // period_ms).astype(int)
    g = {"t0": t0, "period": period_ms, "n": n}
    for name, arr in zip("ohlcv", (o, h, l, c, v)):
        a = np.full(n, np.nan)
        a[idx] = arr
        g[name] = a
    return g


def runs(valid):
    """(start, end_exclusive) of contiguous True runs."""
    valid = np.asarray(valid, dtype=bool)
    if valid.size == 0:
        return []
    d = np.diff(np.concatenate(([0], valid.astype(np.int8), [0])))
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


# ---------------------------------------------------------------- indicators
def wilder_rsi(c, n=14):
    """Wilder RSI, SMA seed over first n deltas (FORMULAS.md section 1). NaN until seeded and across gaps."""
    c = np.asarray(c, dtype=float)
    out = np.full(len(c), np.nan)
    for s, e in runs(~np.isnan(c)):
        x = c[s:e]
        if len(x) < n + 1:
            continue
        d = np.diff(x)
        gain = np.maximum(d, 0.0)
        loss = np.maximum(-d, 0.0)
        ag = gain[:n].mean()
        al = loss[:n].mean()
        out[s + n] = _rsi_val(ag, al)
        for i in range(n, len(d)):
            ag = (ag * (n - 1) + gain[i]) / n
            al = (al * (n - 1) + loss[i]) / n
            out[s + i + 1] = _rsi_val(ag, al)
    return out


def _rsi_val(ag, al):
    if al == 0:
        return 100.0 if ag > 0 else 50.0
    return 100.0 - 100.0 / (1.0 + ag / al)


def wilder_atr(h, l, c, n=14):
    """Wilder ATR: TR from index 1 of a run, SMA seed of first n TRs, then RMA."""
    h = np.asarray(h, float)
    l = np.asarray(l, float)
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    ok = ~(np.isnan(h) | np.isnan(l) | np.isnan(c))
    for s, e in runs(ok):
        if e - s < n + 1:
            continue
        hh, ll, cc = h[s:e], l[s:e], c[s:e]
        tr = np.maximum(hh[1:] - ll[1:], np.maximum(np.abs(hh[1:] - cc[:-1]), np.abs(ll[1:] - cc[:-1])))
        a = tr[:n].mean()
        out[s + n] = a
        for i in range(n, len(tr)):
            a = (a * (n - 1) + tr[i]) / n
            out[s + i + 1] = a
    return out


def bollinger(c, n=20, k=2.0):
    """SMA(n) +- k * population sd (ddof 0), window includes the current close. NaN across gaps."""
    c = np.asarray(c, float)
    mid = np.full(len(c), np.nan)
    sd = np.full(len(c), np.nan)
    for s, e in runs(~np.isnan(c)):
        if e - s < n:
            continue
        w = np.lib.stride_tricks.sliding_window_view(c[s:e], n)
        mid[s + n - 1:e] = w.mean(axis=1)
        sd[s + n - 1:e] = w.std(axis=1, ddof=0)
    return mid, mid - k * sd, mid + k * sd


def trap_fraction(high, low, lower):
    """Share of the candle range below the lower band: (min(lower, high) - low) / (high - low). NaN if no range."""
    rng = high - low
    with np.errstate(invalid="ignore", divide="ignore"):
        return (np.minimum(lower, high) - low) / np.where(rng > 0, rng, np.nan)


def trap_mask(h, l, lower, frac=TRAP_FRAC):
    f = trap_fraction(np.asarray(h, float), np.asarray(l, float), np.asarray(lower, float))
    with np.errstate(invalid="ignore"):
        return (np.asarray(h) > np.asarray(l)) & (f >= frac)


# ---------------------------------------------------------------- causal lookups
def gate_series(hour_starts_ms, h4_starts_ms, h4_rsi):
    """For each 1h bar start, the BTC 4h RSI of the last 4h bar fully closed at or before the 1h bar's close.
    4h bar starting s closes at s + 4h; the 1h bar closes at t + 1h; usable iff s + 4h <= t + 1h."""
    hs = np.asarray(hour_starts_ms, dtype=np.int64)
    h4s = np.asarray(h4_starts_ms, dtype=np.int64)
    h4r = np.asarray(h4_rsi, dtype=float)
    latest_start = np.floor_divide(hs + HOUR_MS - H4_MS, H4_MS) * H4_MS
    pos = np.searchsorted(h4s, latest_start)
    pos_c = np.minimum(pos, len(h4s) - 1)
    hit = (pos < len(h4s)) & (h4s[pos_c] == latest_start)
    return np.where(hit, h4r[pos_c], np.nan)


def lookup_day(day_starts_ms, values, ts_ms):
    """Value of the row whose UTC day contains ts_ms (the day itself, never the next); None if absent."""
    d = int(ts_ms) // DAY_MS * DAY_MS
    days = np.asarray(day_starts_ms, dtype=np.int64)
    i = int(np.searchsorted(days, d))
    if i < len(days) and days[i] == d:
        return values[i]
    return None


# ---------------------------------------------------------------- signal, stop, exit
def anchored_vwap(o, h, l, c, v, j, upto):
    """Cumulative sum(typical*vol)/sum(vol) from bar j through bar upto inclusive."""
    typ = (np.asarray(h[j:upto + 1]) + np.asarray(l[j:upto + 1]) + np.asarray(c[j:upto + 1])) / 3.0
    vol = np.asarray(v[j:upto + 1])
    return (typ * vol).sum() / vol.sum()


def find_signal(o, h, l, c, v, j, window=MAX_WAIT):
    """First bar s in j+1..j+window whose close is above the VWAP anchored at trap bar j through s.
    Returns s or None (also None if a bar is missing or data ends)."""
    n = len(c)
    for s in range(j + 1, j + window + 1):
        if s >= n:
            return None
        seg = (h[j:s + 1], l[j:s + 1], c[j:s + 1], v[j:s + 1])
        if any(np.isnan(x).any() for x in seg):
            return None
        if c[s] > anchored_vwap(o, h, l, c, v, j, s):
            return s
    return None


def compute_D(entry, trap_low, atr):
    """D = max(entry - trap low, ATR14 x 1.0, 0.012 x entry)."""
    return max(entry - trap_low, ATR_MULT * atr, D_FLOOR * entry)


def simulate_trade(o, l, e, D, hold=HOLD_BARS):
    """Entry at open of bar e, stop = entry - D. Stop checked bars e..e+hold-1 (gap below stop fills at the
    open, otherwise stop price; stop first inside a bar). If never hit, exit at open of bar e+hold.
    A stop hit on a present bar resolves the trade even if a LATER bar is missing (PRE_REG says nothing about
    dropping it); a missing bar met before any stop hit, or missing exit bar, = unresolved (None)."""
    n = len(o)
    if e >= n or np.isnan(o[e]):
        return None
    entry = o[e]
    stop = entry - D
    for k in range(e, e + hold):
        if k >= n or np.isnan(o[k]) or np.isnan(l[k]):
            return None
        if o[k] <= stop:
            return k, float(o[k]), "gap_stop"
        if l[k] <= stop:
            return k, float(stop), "stop"
    if e + hold >= n or np.isnan(o[e + hold]):
        return None
    return e + hold, float(o[e + hold]), "time"


def sim_many(o, l, e_idx, stop_frac, hold=HOLD_BARS):
    """Vectorised simulate_trade for placebos: stop = entry*(1-stop_frac). Returns (R_gross, exit_idx, ok).
    ok False where any needed bar is missing."""
    e_idx = np.asarray(e_idx, dtype=int)
    sf = np.asarray(stop_frac, float)
    n = len(o)
    ok = e_idx + hold < n
    e_safe = np.where(ok, e_idx, 0)
    idx = e_safe[:, None] + np.arange(hold + 1)[None, :]
    idx = np.minimum(idx, n - 1)
    O = o[idx]
    L = l[idx][:, :hold]
    ok &= ~np.isnan(O).any(axis=1) & ~np.isnan(L).any(axis=1)
    entry = O[:, 0]
    stop = entry - entry * sf
    hit_open = O[:, :hold] <= stop[:, None]
    hit_low = L <= stop[:, None]
    hit = hit_open | hit_low
    anyhit = hit.any(axis=1)
    kk = hit.argmax(axis=1)
    rows = np.arange(len(e_idx))
    px = np.where(anyhit, np.where(hit_open[rows, kk], O[rows, kk], stop), O[:, hold])
    exit_idx = e_safe + np.where(anyhit, kk, hold)
    D = entry * sf
    R = (px - entry) / D
    return R, exit_idx, ok


def fee_net_r(entry, exit_price, D, fee_rt):
    """R = (exit - entry)/D, fee-net R = R - fee_rt * entry / D."""
    r = (exit_price - entry) / D
    return r, r - fee_rt * entry / D


# ---------------------------------------------------------------- per-coin scan
def scan_coin(g, gate, rsi_gate=RSI_GATE, window=MAX_WAIT, hold=HOLD_BARS):
    """Walk one coin's hourly grid. `gate` = BTC 4h RSI per grid bar (NaN if unknown).
    Returns (trades, skips). Trades hold grid indices; cycle/labels are attached by the caller.
    One position per coin: a trap is ignored while armed or in a trade (first trap wins)."""
    o, h, l, c, v = g["o"], g["h"], g["l"], g["c"], g["v"]
    n = len(c)
    mid, lower, upper = bollinger(c)
    atr = wilder_atr(h, l, c)
    with np.errstate(invalid="ignore"):
        cand = trap_mask(h, l, lower) & (gate <= rsi_gate)
    traps = np.flatnonzero(cand)
    trades = []
    skips = {"no_signal": 0, "atr_nan": 0, "no_entry_bar": 0, "D_over_cap": 0, "unresolved": 0}
    free_from = 0
    for j in traps:
        if j < free_from:
            continue
        s = find_signal(o, h, l, c, v, j, window)
        if s is None:
            skips["no_signal"] += 1
            free_from = j + window + 1
            continue
        e = s + 1
        free_from = s + 1
        if e >= n or np.isnan(o[e]):
            skips["no_entry_bar"] += 1
            continue
        if np.isnan(atr[s]):
            skips["atr_nan"] += 1
            continue
        entry = float(o[e])
        D = compute_D(entry, float(l[j]), float(atr[s]))
        if D > D_CAP * entry:
            skips["D_over_cap"] += 1
            continue
        sim = simulate_trade(o, l, e, D, hold)
        if sim is None:
            skips["unresolved"] += 1
            continue
        x, px, reason = sim
        free_from = x
        trades.append({"trap_idx": int(j), "signal_idx": int(s), "entry_idx": int(e), "exit_idx": int(x),
                       "entry": entry, "stop": entry - D, "D": D, "trap_low": float(l[j]),
                       "exit_price": px, "exit_reason": reason, "btc_rsi4h": float(gate[j])})
    return trades, skips


# ---------------------------------------------------------------- episodes
def assign_episodes(signal_ms, gap_ms=EPISODE_GAP_MS):
    """Episode ids (1..) in the order of the input. Sorted by signal time; a gap of more than gap_ms between
    consecutive signals starts a new episode (chained). Ties keep input order."""
    sig = np.asarray(signal_ms, dtype=np.int64)
    order = np.argsort(sig, kind="stable")
    ids = np.zeros(len(sig), dtype=int)
    eid = 0
    prev = None
    for i in order:
        if prev is None or sig[i] - prev > gap_ms:
            eid += 1
        ids[i] = eid
        prev = sig[i]
    return ids
