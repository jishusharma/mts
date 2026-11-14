"""Test 4 engine: capitulation signature (funding<0 + OI unwind + failed breakdown). Rules frozen in PRE_REG.md.
Closed bars only. A swing low at bar i is known only at the close of bar i+K. Data cached outside the repo (see fetch.py)."""
import bisect
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "buyzone_test1_ladder_2026-11-14"))
import ladder as L  # noqa: E402  (phases, wilder_atr, block_ci, in_split reused from Test 1)

K = 3                # swing half-width for the undercut level (OURS)
MAX_AGE = 120        # swing level no older than this (OURS)
RECLAIM = 14         # close back above within 2 weeks (SOURCED)
OI_DROP = -0.05      # OI change over prior 7 days (SOURCED)
OI_LAG = 7
LOCK = 10
HORIZONS = (1, 3, 7)
FEES = {"12": 0.0012, "6": 0.0006}
LOW_K, LOW_FALL, LOW_LOOK, LL_DAYS, LL_PCT = 10, 0.25, 120, 182, 0.97
DAY = 86400000


def load(coin, cache=None):
    """Return dict ts,o,h,l,c,fund,oi (aligned per daily bar; NaN where no data) or None."""
    cache = cache or os.environ.get("BZ4_CACHE", "C:/Users/e-ngineers/mts_cache/buyzone_test4")
    try:
        sp = np.array(json.load(open("%s/%s_spot.json" % (cache, coin))), float)
        fu = json.load(open("%s/%s_fund.json" % (cache, coin)))
        oi = json.load(open("%s/%s_oi.json" % (cache, coin)))
    except (OSError, ValueError):
        return None
    if len(sp) == 0 or not oi or not fu:
        return None
    if sp[-1, 0] + DAY > time.time() * 1000:    # drop the partial current day
        sp = sp[:-1]
    ts = sp[:, 0].astype(np.int64)
    return dict(coin=coin, ts=ts, o=sp[:, 1], h=sp[:, 2], l=sp[:, 3], c=sp[:, 4],
                fund=align_funding(ts, fu), oi=align_oi(ts, oi), oi_start=int(min(t for t, _ in oi)))


def align_funding(ts, prints):
    """Funding of day d = mean of the prints stamped in UTC day d; NaN when none."""
    s, n = {}, {}
    for t, v in prints:
        d = (t // DAY) * DAY
        s[d] = s.get(d, 0.0) + v
        n[d] = n.get(d, 0) + 1
    return np.array([s[t] / n[t] if t in s else np.nan for t in ts])


def align_oi(ts, rows):
    m = {int(t): v for t, v in rows}
    return np.array([m.get(int(t), np.nan) for t in ts])


def swing_idx(l, k):
    out = []
    for i in range(k, len(l) - k):
        if l[i] < min(l[i - k:i].min(), l[i + 1:i + k + 1].min()):
            out.append(i)
    return out


def signatures(l, c, fund, oi, n_avail=None):
    """All (u) with a failed breakdown (B) and the funding / OI flags. Uses only bars < n_avail so causality
    is testable by truncation. Returns list of dict(u, s, S, F, O, B), s the first reclaim close within RECLAIM bars."""
    n = len(c) if n_avail is None else n_avail
    sw = [i for i in swing_idx(l[:n], K) if i + K < n]
    out = []
    for u in range(OI_LAG + 1, n):
        a = bisect.bisect_right(sw, u - K - 1) - 1      # swing index <= u-4 (known at close of u-1)
        if a < 0 or u - sw[a] > MAX_AGE:
            continue
        S = l[sw[a]]
        if not l[u] < S:
            continue
        s = next((t for t in range(u, min(u + RECLAIM, n - 1) + 1) if c[t] > S), None)
        if s is None:
            continue
        F = bool(fund[u] < 0) if not np.isnan(fund[u]) else False
        o0, o1 = oi[u - OI_LAG], oi[u]
        O = bool(o1 / o0 - 1 <= OI_DROP) if not (np.isnan(o0) or np.isnan(o1)) else False
        out.append(dict(u=u, s=s, S=float(S), F=F, O=O, B=True))
    return out


def full_signatures(sigs):
    return sorted([x for x in sigs if x["F"] and x["O"] and x["B"]], key=lambda x: (x["s"], x["u"]))


def lows(h, l, fund, oi, n=None):
    """Ex-post lows population (descriptive only): k=10 swing low after a >=25% fall, OI and funding available."""
    n = len(l) if n is None else n
    out = []
    for i in range(max(LOW_LOOK, LOW_K), n - LOW_K):
        if not l[i] < min(l[i - LOW_K:i].min(), l[i + 1:i + LOW_K + 1].min()):
            continue
        if 1 - l[i] / h[i - LOW_LOOK:i].max() < LOW_FALL:
            continue
        if i < OI_LAG or np.isnan(oi[i]) or np.isnan(oi[i - OI_LAG]) or np.isnan(fund[i]):
            continue
        out.append(i)
    return out


def sim_trade(o, h, l, c, e, stop, hold):
    """Long at Open[e]; stop checked from the entry bar; exit Close[e+hold-1]. None if exit bar not in data."""
    x = e + hold - 1
    if x > len(c) - 1:
        return None
    for t in range(e, x + 1):
        if l[t] <= stop:
            return t, min(o[t], stop)
    return x, c[x]


def build_events(d, hold, n_avail=None):
    """Kept signature trades for one coin and one hold. Phase looked up at the signature bar s (= e-1)."""
    o, h, l, c, ts = d["o"], d["h"], d["l"], d["c"], d["ts"]
    n = len(c) if n_avail is None else n_avail
    atr = L.wilder_atr(h[:n], l[:n], c[:n])
    ph = L.phases(h[:n], l[:n], c[:n])
    sg = full_signatures(signatures(l, c, d["fund"], d["oi"], n))
    ev, last_s, last_x, dropped = [], -10**9, -10**9, 0
    for x in sg:
        u, s = x["u"], x["s"]
        e = s + 1
        if e >= n or s < last_s + LOCK or e <= last_x:
            continue
        m = l[u:s + 1].min()
        if np.isnan(atr[s]):
            continue
        stop = m - max(0.6 * atr[s], 0.005 * m)
        entry = o[e]
        if entry <= stop:
            dropped += 1
            continue
        res = sim_trade(o[:n], h[:n], l[:n], c[:n], e, stop, hold)
        if res is None:
            continue
        xi, px = res
        ev.append(dict(coin=d["coin"], u=u, s=s, e=e, x=xi, ts=int(ts[e]), r=(entry - stop) / entry,
                       gross=px / entry - 1, phase=ph[s] or "NOPHASE", hold=hold))
        last_s, last_x = s, xi
    return ev, dropped


class PlaceboPool:
    """Eligible random entry days per coin: phase at e-1, split, and the lows-like flag, restricted to days where the
    signature is computable (>= first OI stamp + 7 days)."""

    def __init__(self, d):
        self.d = d
        o, h, l, c, ts = d["o"], d["h"], d["l"], d["c"], d["ts"]
        self.ph = L.phases(h, l, c)
        hi90 = pd.Series(h).rolling(90).max().shift(1).values   # max High[e-90..e-1]
        self.cl = np.concatenate([[np.nan], c[:-1]])             # Close[e-1]
        self.lowslike = self.cl <= 0.80 * hi90
        self.first = int(np.searchsorted(ts, d["oi_start"] + OI_LAG * DAY))

    def pool(self, phase, split, hold, lowslike):
        d = self.d
        n = len(d["c"])
        idx = np.arange(max(self.first, 1), n - hold + 1)
        ph_prev = np.array([self.ph[i - 1] or "NOPHASE" for i in idx], dtype=object)
        ok = ph_prev == phase
        if lowslike:
            ok &= self.lowslike[idx]
        ok &= np.array([L.in_split(int(d["ts"][i]), split) for i in idx]) if split != "ALL" else True
        return idx[ok]

    def gross(self, e, r, hold):
        d = self.d
        o, l, c = d["o"], d["l"], d["c"]
        entry = o[e]
        stop = entry * (1 - r)
        k = np.arange(hold)
        lw = l[e[:, None] + k]
        hit = lw <= stop[:, None]
        anyhit = hit.any(1)
        first = hit.argmax(1)
        ox = o[e + first]
        px = np.where(anyhit, np.minimum(ox, stop), c[e + hold - 1])
        return px / entry - 1


def placebo(pools, events, split, hold, fee, lowslike, ndraw=2000, seed=1114):
    """Draw means of mean R. pools: coin -> PlaceboPool. Events with an empty pool are skipped (count returned)."""
    rng = np.random.default_rng(seed)
    cols, skipped = [], 0
    for ev in events:
        pl = pools[ev["coin"]]
        cand = pl.pool(ev["phase"], split, hold, lowslike)
        if len(cand) == 0:
            skipped += 1
            continue
        e = cand[rng.integers(0, len(cand), size=ndraw)]
        r = np.full(ndraw, ev["r"])
        cols.append((pl.gross(e, r, hold) - fee) / ev["r"])
    if not cols:
        return np.array([]), skipped
    return np.mean(np.stack(cols, 1), 1), skipped


def R_of(gross, r, fee):
    return (gross - fee) / r


def block_ci(ts, R, hold):
    return L.block_ci(ts, R, block_days=hold)
