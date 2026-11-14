"""Test 3 engine: bear-phase 4H bearish-divergence short. Rules are frozen in PRE_REG.md (read it first).
All indicators use closed bars only. A swing high at bar i is known only at the close of bar i+K.
Re-uses indicators and the block bootstrap from the Test 1 engine (ladder.py).
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "buyzone_test1_ladder_2026-11-14"))
import ladder as L1  # noqa: E402
from numpy.lib.stride_tricks import sliding_window_view  # noqa: E402

K = 3                  # swing half-width (OURS)
WARM4 = 100            # 4H warm-up bars
HOLD = 42              # 7 days of 4H bars (SOURCED, Test 3)
MIN_GAP, MAX_GAP = 6, 60
LOCK = 60              # 10 days of 4H bars (SOURCED, Shared rule)
BB_N, BB_K = 20, 2.0
BAR = 4 * 3600 * 1000
DAY = 86400000
FEES = {"12": 0.0012, "6": 0.0006}
VAL_START = 1704067200000      # 2024-01-01 UTC
RECENT_START = 1751328000000   # 2025-07-01 UTC
T1_PHASES = ["UP", "BASE", "RANGE", "DOWN", "POSTPEAK_BEAR"]


def daily_flags(h, l, c):
    """Per daily bar t (bars <= t only): (bear flag, Test 1 label). BEAR = Close < SMA350 and label not UP/BASE (no base reclaim)."""
    lab = L1.phases(h, l, c)
    sma350 = pd.Series(c).rolling(350).mean().values
    bear = np.array([bool(x not in ("", "UP", "BASE")) for x in lab]) & (c < sma350)
    return bear, lab


def map_prev_day(ts4, dts, arr, fill):
    """For each 4H bar, the daily value of the PREVIOUS UTC day (previous day only)."""
    target = (ts4 // DAY - 1) * DAY
    idx = np.searchsorted(dts, target)
    ok = (idx < len(dts)) & (dts[np.minimum(idx, len(dts) - 1)] == target)
    out = np.full(len(ts4), fill, dtype=arr.dtype)
    out[ok] = arr[idx[ok]]
    return out


def funding_cum(ts4, fund):
    """Cumulative funding per 4H bar: G[b] = sum of settlement rates in bars 0..b (rate is paid to a short when positive).
    Returns (G, first_ts). A funding record belongs to the bar that contains its timestamp."""
    n = len(ts4)
    f = np.zeros(n)
    if not fund:
        return np.cumsum(f), None
    for s, r in fund:
        b = int(np.searchsorted(ts4, s, side="right")) - 1
        if 0 <= b < n and s < ts4[b] + BAR:
            f[b] += r
    return np.cumsum(f), int(fund[0][0])


def bollinger_upper(c):
    s = pd.Series(c)
    return (s.rolling(BB_N).mean() + BB_K * s.rolling(BB_N).std(ddof=0)).values


def swing_highs(h):
    out = []
    for i in range(K, len(h) - K):
        w = np.concatenate([h[i - K:i], h[i + 1:i + K + 1]])
        if h[i] > w.max():
            out.append(i)
    return out


def find_signals(o, h, l, c, atr, rsi, n_avail=None):
    """Raw signals (before lockout): list of (c_idx, j, stop0). Only bars < n_avail used (causality testable by truncation)."""
    n = len(c) if n_avail is None else n_avail
    bb = bollinger_upper(c[:n])
    sw = [i for i in swing_highs(h[:n]) if i + K < n]
    sigs = []
    for a in range(1, len(sw)):
        p, j = sw[a - 1], sw[a]
        cc = j + K
        if not (MIN_GAP <= j - p <= MAX_GAP):
            continue
        if np.isnan(rsi[j]) or np.isnan(rsi[p]) or np.isnan(bb[j]) or np.isnan(atr[cc]):
            continue
        if h[j] > h[p] and rsi[j] < rsi[p] and h[j] > bb[j]:
            sigs.append((cc, j, h[j] + max(0.6 * atr[cc], 0.005 * h[j])))
    sigs.sort()
    return sigs


def sim_exit(o, h, l, c, atr, e, stop0):
    """Exit of a short entered at Open[e]. Returns (exit_idx, exit_px) or None if still open at the data end."""
    n = len(c)
    mn = np.inf
    for t in range(e, min(e + HOLD - 1, n - 1) + 1):
        lvl = stop0 if t == e else min(stop0, mn + 2 * atr[t - 1])
        if h[t] >= lvl:
            return t, max(o[t], lvl)
        mn = min(mn, l[t])
        if t == e + HOLD - 1:
            return t, c[t]
    return None


def build_events(coin, ts, o, h, l, c, bearA, labA, G, first_fund, n_avail=None):
    """bearA/labA: per 4H bar, the daily flag/label read at the previous UTC day. Returns (events, dropped_entry_ge_stop)."""
    atr, rsi = L1.wilder_atr(h, l, c), L1.wilder_rsi(c)
    n = len(c) if n_avail is None else n_avail
    sigs = find_signals(o, h, l, c, atr, rsi, n_avail)
    ev, last_e, last_exit, dropped = [], -10**9, -10**9, 0
    for cc, j, stop0 in sigs:
        e = cc + 1
        if e < WARM4 or e >= n or labA[e] == "" or e < last_e + LOCK or e <= last_exit:
            continue
        entry = o[e]
        if entry >= stop0:
            dropped += 1
            continue
        res = sim_exit(o[:n], h[:n], l[:n], c[:n], atr, e, stop0)
        if res is None:
            continue
        x, px = res
        covered = first_fund is not None and ts[e] >= first_fund
        ev.append(dict(coin=coin, sig=cc, e=e, x=x, ts=int(ts[e]), r=(stop0 - entry) / entry, gross=(entry - px) / entry,
                       fund=float(G[x] - G[e]) if covered else 0.0, covered=bool(covered), bear=bool(bearA[e]), label=labA[e]))
        last_e, last_exit = e, x
    return ev, dropped


def gkey(bear, label):
    return "BEAR" if bear else label


def in_split(ts_ms, sp):
    ts_ms = np.asarray(ts_ms)
    if sp == "DEV":
        return ts_ms < VAL_START
    if sp == "VAL":
        return ts_ms >= VAL_START
    if sp == "RECENT":
        return ts_ms >= RECENT_START
    return np.ones(ts_ms.shape, bool)


def R_of(ev, fee, funding):
    return (ev["gross"] - fee + (ev["fund"] if funding else 0.0)) / ev["r"]


class PlaceboTable:
    """Per-coin windows for every possible 4H entry bar so any (entry bar, stop distance) is evaluated for many draws at once.
    A trade still open at the data end is NaN (dropped), as in build_events."""

    def __init__(self, coins):
        # coins: coin -> dict(ts,o,h,l,c,bearA,labA,G,first)
        self.rows = {}
        O, H, T, G, C, TS, KEY, COV = [], [], [], [], [], [], [], []
        off = 0
        for coin, d in coins.items():
            ts, o, h, l, c = d["ts"], d["o"], d["h"], d["l"], d["c"]
            n = len(c)
            atr = L1.wilder_atr(h, l, c)
            nanp = np.full(HOLD, np.nan)
            op, hp, lp, cp, ap = [np.concatenate([a, nanp]) for a in (o, h, l, c, atr)]
            Gp = np.concatenate([d["G"], nanp])
            sw = lambda a: sliding_window_view(a, HOLD)[:n]
            Ow, Hw, Lw, Aw = sw(op), sw(hp), sw(lp), sw(ap)
            cm = np.minimum.accumulate(Lw, axis=1)
            Tw = np.full((n, HOLD), np.inf)
            Tw[:, 1:] = cm[:, :-1] + 2 * Aw[:, :-1]
            Gw = sw(Gp) - d["G"][:, None]
            O.append(Ow.astype(np.float32)); H.append(Hw.astype(np.float32)); T.append(Tw.astype(np.float32))
            G.append(Gw.astype(np.float32)); C.append(cp[HOLD - 1:HOLD - 1 + n])
            TS.append(ts)
            keys = np.array([gkey(b, lab) if lab != "" else "" for b, lab in zip(d["bearA"], d["labA"])], dtype=object)
            keys[:WARM4] = ""
            KEY.append(keys)
            first = d["first"]
            COV.append(np.full(n, False) if first is None else ts >= first)
            self.rows[coin] = (off, n)
            off += n
        self.O, self.H, self.T, self.G = map(np.concatenate, (O, H, T, G))
        self.C, self.TS, self.KEY, self.COV = map(np.concatenate, (C, TS, KEY, COV))

    def pool(self, coin, key, split):
        off, n = self.rows[coin]
        sl = slice(off, off + n)
        ok = (self.KEY[sl] == key) & in_split(self.TS[sl], split)
        return off + np.nonzero(ok)[0]

    def outcome(self, idx, r):
        """idx, r arrays (N, m). Returns (gross, funding) arrays, NaN where the trade is still open at the data end."""
        entry = self.O[idx][..., 0].astype(float)
        stop0 = entry * (1 + r)
        lvl = np.minimum(stop0[..., None], self.T[idx].astype(float))
        hit = self.H[idx].astype(float) >= lvl
        anyhit = hit.any(-1)
        first = hit.argmax(-1)
        lv_f = np.take_along_axis(lvl, first[..., None], -1)[..., 0]
        op_f = np.take_along_axis(self.O[idx], first[..., None], -1)[..., 0].astype(float)
        fk = np.where(anyhit, first, HOLD - 1)
        gk = np.take_along_axis(self.G[idx], fk[..., None], -1)[..., 0].astype(float)
        px = np.where(anyhit, np.maximum(op_f, lv_f), self.C[idx])
        g = (entry - px) / entry
        g[~anyhit & np.isnan(self.C[idx])] = np.nan
        fund = np.where(self.COV[idx], gk, 0.0)
        return g, fund


def placebo(table, events, split, ndraw=2000, seed=1114, chunk=50):
    """Draw means of mean R for same coin / same split / same group key / same r. Returns dict (fee, funding) -> array of draw means."""
    rng = np.random.default_rng(seed)
    pools = [table.pool(ev["coin"], gkey(ev["bear"], ev["label"]), split) for ev in events]
    keep = [i for i, p in enumerate(pools) if len(p)]
    out = {(f, w): [] for f in FEES for w in (False, True)}
    if not keep:
        return {k: np.array([]) for k in out}
    r = np.array([events[i]["r"] for i in keep])
    for s in range(0, ndraw, chunk):
        m = min(chunk, ndraw - s)
        idx = np.stack([pools[i][rng.integers(0, len(pools[i]), size=m)] for i in keep], 1)
        rr = np.broadcast_to(r, idx.shape)
        g, fu = table.outcome(idx, rr)
        for f, fee in FEES.items():
            out[(f, False)].append(np.nanmean((g - fee) / rr, 1))
            out[(f, True)].append(np.nanmean((g - fee + fu) / rr, 1))
    return {k: np.concatenate(v) for k, v in out.items()}
