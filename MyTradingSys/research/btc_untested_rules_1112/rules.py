import sys
sys.dont_write_bytecode = True
"""Four untested value-area rules A..D exactly as PREREG.md (frozen). 15m bars, arrays are numpy, t = bar open ms.

Imports profile / day_profiles / simulate from edge_views_2026-11-11/VA_REENTRY_POC_SHIFT/va_poc.py (not copied).
Differs from backtest/vp_return_to_value.py (a 5m touch COUNT with no entry, stop, target or fee): these simulate fee-net trades.
"""
import glob
import gzip
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))  # MyTradingSys
sys.path.insert(0, os.path.join(ROOT, "research", "edge_views_2026-11-11", "VA_REENTRY_POC_SHIFT"))
sys.path.insert(0, os.path.join(ROOT, "backtest"))
import va_poc as V  # noqa: E402

M15 = 900_000
D1 = V.D1
W_BIN_PCT = 0.001    # weekly bin width, 0.10 % of the week close (OURS)
ACC_N = 8            # A: closes beyond the edge that count as acceptance (OURS)
ACC_WAIT = 24        # A: bars after acceptance in which a retest may come (OURS)
A_HOLD = 16          # A: exit at the close of the 16th bar from entry (OURS)
B_WAIT = 24          # B: revisit / cap window, 6 h (OURS)
C_CAP = 96           # C: cap, one day (OURS)
THIN = 0.25          # C: close-bin volume <= 0.25 x POC-bin volume (OURS)
D_MIN_DIST = 0.01    # D: |POC - close| / close >= 1 % (OURS)
D_BARS = 4 * 7 * 96  # 4 weeks of 15m bars = 2688 (OURS)
D_HOLD = 96          # D: exit at the close of the 96th bar after the touch bar (OURS)
MIN_RISK = 0.001     # R/entry floor (OURS)
FEE_BP = V.FEE_BP


def load(dirpath="D:/MTS_data/binance_aggtrades/reduced", last="2024-05"):
    """15m bars from the reduced aggtrades files up to month `last`; returns dict t,o,h,l,c,v."""
    rows = []
    for p in sorted(glob.glob(os.path.join(dirpath, "BTCUSDT-bars15-*.csv.gz"))):
        if p[-14:-7] > last:
            continue
        with gzip.open(p, "rt") as fh:
            next(fh)
            for ln in fh:
                f = ln.split(",")
                rows.append((int(f[0]), float(f[1]), float(f[2]), float(f[3]), float(f[4]), float(f[9])))
    rows.sort()
    a = np.array(rows)
    return dict(t=a[:, 0].astype(np.int64) * M15, o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4], v=a[:, 5])


def groups(key):
    """(start, end) index pairs of consecutive equal key values."""
    cut = np.flatnonzero(np.diff(key)) + 1
    return np.r_[0, cut], np.r_[cut, len(key)]


def day_info(b):
    """{day: dict(poc, val, vah, close, first_i, last_i, thin)} for completed (full 96-bar) UTC days."""
    d = b["t"] // D1
    st, en = groups(d)
    out = {}
    for a, z in zip(st, en):
        if z - a != 96:
            continue
        width = V.BIN_PCT * float(b["c"][z - 1])
        poc, val, vah = V.profile(b["h"][a:z], b["l"][a:z], b["c"][a:z], b["v"][a:z], width)
        tp = (b["h"][a:z] + b["l"][a:z] + b["c"][a:z]) / 3.0
        idx = np.floor(tp / width + 1e-9).astype(np.int64)
        base = int(idx.min())
        vol = np.bincount(idx - base, weights=b["v"][a:z])
        pb = int(np.argmax(vol))
        cb = int(np.floor(float(b["c"][z - 1]) / width + 1e-9)) - base
        cv = float(vol[cb]) if 0 <= cb < len(vol) else 0.0
        thin = bool(cb != pb and cv <= THIN * float(vol[pb]))
        out[int(d[a])] = dict(poc=poc, val=val, vah=vah, close=float(b["c"][z - 1]), first_i=int(a), last_i=int(z - 1), thin=thin)
    return out


def week_info(b):
    """{week: dict(poc, close, birth_i)} for completed (full 672-bar) UTC Monday weeks; birth_i = first bar of the next week."""
    w = (b["t"] // D1 + 3) // 7
    st, en = groups(w)
    out = {}
    for a, z in zip(st, en):
        if z - a != 672 or z >= len(b["t"]):
            continue
        width = W_BIN_PCT * float(b["c"][z - 1])
        poc, _, _ = V.profile(b["h"][a:z], b["l"][a:z], b["c"][a:z], b["v"][a:z], width)
        out[int(w[a])] = dict(poc=poc, close=float(b["c"][z - 1]), birth_i=int(z))
    return out


def net_bp(side, entry, exit_px):
    return side * (exit_px / entry - 1) * 1e4 - FEE_BP


def _trade(b, side, e_i, x_i, entry, x_px, **kw):
    d = dict(side=side, entry_ms=int(b["t"][e_i]), entry_px=float(entry), exit_ms=int(b["t"][x_i]), exit_px=float(x_px),
             entry_i=e_i, exit_i=x_i, ret=net_bp(side, entry, x_px))
    d.update(kw)
    return d


def _first_touch(b, i0, i1, level):
    """First bar in [i0, i1] whose range contains level, else -1."""
    seg = np.flatnonzero((b["l"][i0:i1 + 1] <= level) & (b["h"][i0:i1 + 1] >= level))
    return int(i0 + seg[0]) if len(seg) else -1


def run_a(b, di, start_ms, end_ms):
    """A: acceptance then edge retest. Returns (trades, hold_acc, hold_non) with hold_* = lists of bool per event."""
    c, l, h, t = b["c"], b["l"], b["h"], b["t"]
    n = len(t)
    trades, acc, non = [], [], []
    busy = -1
    for i in range(1, n):
        if not (start_ms <= t[i] <= end_ms):
            continue
        d = int(t[i] // D1)
        if d - 1 not in di:
            continue
        vl, vh = di[d - 1]["val"], di[d - 1]["vah"]
        for side, edge, brk in ((1, vh, c[i] > vh and c[i - 1] <= vh), (-1, vl, c[i] < vl and c[i - 1] >= vl)):
            if not brk:
                continue
            # first bar after i whose range touches the edge from the accepted side
            j = -1
            for k in range(i + 1, min(i + ACC_N + ACC_WAIT, n - 1) + 1):
                if (l[k] <= edge) if side > 0 else (h[k] >= edge):
                    j = k
                    break
            if j < 0:
                continue
            hold = bool(c[j] > edge) if side > 0 else bool(c[j] < edge)
            if j >= i + ACC_N:
                acc.append(hold)
                e_i = j + 1
                x_i = e_i + A_HOLD - 1
                if hold and x_i <= n - 1 and e_i > busy and t[e_i] <= end_ms:
                    trades.append(_trade(b, side, e_i, x_i, b["o"][e_i], c[x_i], hz=A_HOLD))
                    busy = x_i
            else:
                non.append(hold)
    return trades, acc, non


def sim_trade(b, side, e_i, target, cap):
    """Fade/pull trade to `target` with a 1:1 stop; None when skipped. Drops trades whose cap would run past the data."""
    entry = float(b["o"][e_i])
    r = side * (target - entry)
    if r <= 0 or r / entry < MIN_RISK or e_i + cap - 1 > len(b["t"]) - 1:
        return None
    x_i, x_px, kind = V.simulate(b, e_i, side, entry - side * r, target, cap)
    return _trade(b, side, e_i, x_i, entry, x_px, kind=kind, r_pct=r / entry, tp_pct=r / entry, cap=cap)


def run_b(b, di, start_ms, end_ms):
    """B: first close outside prior-day VA per direction per day; fade to prior POC. Returns (trades, revisit flags)."""
    c, t = b["c"], b["t"]
    n = len(t)
    done = set()
    trades, rev = [], []
    busy = -1
    for i in range(1, n - 1):
        if not (start_ms <= t[i] <= end_ms):
            continue
        d = int(t[i] // D1)
        if d - 1 not in di:
            continue
        p = di[d - 1]
        for s, brk in ((-1, c[i] > p["vah"] and c[i - 1] <= p["vah"]), (1, c[i] < p["val"] and c[i - 1] >= p["val"])):
            if not brk or (d, s) in done:
                continue
            done.add((d, s))
            if i + B_WAIT <= n - 1:
                rev.append(_first_touch(b, i + 1, i + B_WAIT, p["poc"]) >= 0)
            if i + 1 > busy:
                tr = sim_trade(b, s, i + 1, p["poc"], B_WAIT)
                if tr is not None:
                    trades.append(tr)
                    busy = tr["exit_i"]
    return trades, rev


def run_c(b, di, start_ms, end_ms):
    """C: thin close pulls to POC. Returns (trades, touch flags thin days, touch flags other days)."""
    t = b["t"]
    trades, thin_t, other_t = [], [], []
    busy = -1
    for d in sorted(di):
        if d + 1 not in di:
            continue
        p, q = di[d], di[d + 1]
        e_i = q["first_i"]
        if not (start_ms <= t[e_i] <= end_ms):
            continue
        touched = _first_touch(b, q["first_i"], q["last_i"], p["poc"]) >= 0
        (thin_t if p["thin"] else other_t).append(touched)
        if p["thin"] and e_i > busy:
            side = 1 if p["close"] < p["poc"] else -1
            tr = sim_trade(b, side, e_i, p["poc"], C_CAP)
            if tr is not None:
                trades.append(tr)
                busy = tr["exit_i"]
    return trades, thin_t, other_t


def run_d(b, wi, start_ms, end_ms):
    """D: naked weekly POC. Returns (trades, touch flags, mirror touch flags, MFE bp list)."""
    t, h, l = b["t"], b["h"], b["l"]
    n = len(t)
    evs = []
    touches, mirror = [], []
    for w in sorted(wi):
        p = wi[w]
        s = p["birth_i"]
        if not (start_ms <= t[s] <= end_ms) or abs(p["poc"] - p["close"]) / p["close"] < D_MIN_DIST or s + D_BARS - 1 > n - 1:
            continue
        k = _first_touch(b, s, s + D_BARS - 1, p["poc"])
        touches.append(k >= 0)
        mirror.append(_first_touch(b, s, s + D_BARS - 1, 2 * p["close"] - p["poc"]) >= 0)
        if k >= 0:
            evs.append((k, 1 if p["close"] > p["poc"] else -1, p["poc"]))
    trades, mfe = [], []
    busy = -1
    for k, side, poc in sorted(evs):
        x_i = k + D_HOLD
        if k <= busy or x_i > n - 1:
            continue
        trades.append(_trade(b, side, k, x_i, poc, b["c"][x_i], hz=D_HOLD + 1))
        busy = x_i
        mfe.append(((h[k:x_i + 1].max() / poc - 1) if side > 0 else (1 - l[k:x_i + 1].min() / poc)) * 1e4)
    return trades, touches, mirror, mfe


def placebo(b, trades, start_ms, end_ms, kind, draws=500, seed=1):
    """kind 'hold': exit at close of bar e+hold-1 (A: 16) / e+hold (D: 96) with hold = trade horizon; 'stop': V.simulate with 1:1 geometry."""
    rng = np.random.default_rng(seed)
    lo = int(np.searchsorted(b["t"], start_ms))
    hi = int(np.searchsorted(b["t"], end_ms))
    means = []
    for _ in range(draws):
        rs = []
        for tr in trades:
            if kind == "stop":
                cap = tr["cap"]
                e_i = int(rng.integers(lo, hi - cap))
                entry = float(b["o"][e_i])
                r = tr["r_pct"] * entry
                s = tr["side"]
                _, x_px, _ = V.simulate(b, e_i, s, entry - s * r, entry + s * tr["tp_pct"] * entry, cap)
            else:
                hz = tr["hz"]
                e_i = int(rng.integers(lo, hi - hz))
                entry = float(b["o"][e_i])
                x_px = float(b["c"][e_i + hz - 1])
                s = tr["side"]
            rs.append(net_bp(s, entry, x_px))
        means.append(float(np.mean(rs)))
    return np.array(means)
