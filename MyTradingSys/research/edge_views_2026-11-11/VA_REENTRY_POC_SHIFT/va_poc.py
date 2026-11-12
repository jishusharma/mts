import sys
sys.dont_write_bytecode = True
"""Prior-day value-area re-entry (R1) and two consecutive daily POC shifts (R2). Rules exactly as PREREG.md (frozen).

Arrays are numpy; t = bar open ms. A bar is usable only after it closes (t + width). Daily profiles come from completed UTC days only.
"""
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "backtest"))
from fees import BINANCE_TAKER  # 2 x taker = 0.10 % round trip

M15 = 15 * 60_000
D1 = 24 * 60 * 60_000
BIN_PCT = 0.0005     # bin width = 0.05 % of the day close (OURS)
VA_SHARE = 0.70      # value-area share (OURS, standard rule)
WAIT = 24            # 15m bars allowed between break and re-entry (OURS)
CAP = 96             # 15m bars, 24 h (OURS)
MIN_RISK = 0.001     # R/entry floor (OURS)
FEE = BINANCE_TAKER * 2
FEE_BP = FEE * 1e4


def profile(h, l, c, v, width):
    """(poc_price, val, vah) of one day. Typical price (h+l+c)/3 picks the bin floor(tp/width); POC ties -> lowest bin."""
    tp = (np.asarray(h, float) + l + c) / 3.0
    idx = np.floor(tp / width + 1e-9).astype(np.int64)
    base = int(idx.min())
    vol = np.bincount(idx - base, weights=np.asarray(v, float))
    n = len(vol)
    poc = int(np.argmax(vol))
    lo = hi = poc
    acc = float(vol[poc])
    goal = VA_SHARE * float(vol.sum())
    while acc < goal and (lo > 0 or hi < n - 1):
        up = float(vol[hi + 1:hi + 3].sum())
        dn = float(vol[max(lo - 2, 0):lo].sum())
        if hi < n - 1 and (up >= dn or lo == 0):
            acc += up
            hi = min(hi + 2, n - 1)
        else:
            acc += dn
            lo = max(lo - 2, 0)
    return (base + poc + 0.5) * width, (base + lo) * width, (base + hi + 1) * width


def day_profiles(t, h, l, c, v):
    """{day_number: (poc, val, vah)} for every UTC day present; width = BIN_PCT x that day last close."""
    d = t // D1
    cut = np.flatnonzero(np.diff(d)) + 1
    st = np.r_[0, cut]
    en = np.r_[cut, len(t)]
    return {int(d[a]): profile(h[a:b], l[a:b], c[a:b], v[a:b], BIN_PCT * float(c[b - 1])) for a, b in zip(st, en)}


def resample15(t, o, h, l, c):
    b = t // M15
    idx = np.flatnonzero(np.diff(b)) + 1
    st = np.r_[0, idx]
    en = np.r_[idx, len(t)]
    return dict(t=b[st] * M15, o=o[st], h=np.maximum.reduceat(h, st), l=np.minimum.reduceat(l, st), c=c[en - 1])


def levels_for_days(profiles):
    """{day D: (val, vah)} from day D-1 only."""
    return {d + 1: (p[1], p[2]) for d, p in profiles.items()}


def simulate(b, i0, side, stop, tp, cap=CAP):
    """Walk 15m bars from i0; the stop wins a tie. Returns (exit_idx, exit_px, kind)."""
    n = len(b["t"])
    last = min(i0 + cap - 1, n - 1)
    for j in range(i0, last + 1):
        hi, lo = b["h"][j], b["l"][j]
        if side > 0:
            if lo <= stop:
                return j, stop, "stop"
            if hi >= tp:
                return j, tp, "tp"
        else:
            if hi >= stop:
                return j, stop, "stop"
            if lo <= tp:
                return j, tp, "tp"
    return last, float(b["c"][last]), "cap"


def run_r1(b, levels, start_ms, end_ms):
    """All R1 trades with entry bar open in [start_ms, end_ms]. levels = {day: (val, vah)}."""
    n = len(b["t"])
    c, h, l, o, t = b["c"], b["h"], b["l"], b["o"], b["t"]
    trades = []
    state = None  # (side, i_break, excursion extreme, day)
    i = max(1, int(np.searchsorted(t, start_ms)))
    while i < n - 1:
        day = int(t[i] // D1)
        if state is not None:
            side, ib, ext, sday = state
            vl, vh = levels[sday]
            if day != sday or i - ib > WAIT or ((c[i] < vl) if side < 0 else (c[i] > vh)):
                state = None  # window over, next day, or closed through the far edge
            else:
                ext = max(ext, h[i]) if side < 0 else min(ext, l[i])
                inside = (c[i] <= vh) if side < 0 else (c[i] >= vl)
                if not inside:
                    state = (side, ib, ext, sday)
                else:
                    state = None
                    e_i = i + 1
                    entry = float(o[e_i])
                    stop = float(ext)
                    tgt = float(vl if side < 0 else vh)
                    r = (stop - entry) if side < 0 else (entry - stop)
                    td = (entry - tgt) if side < 0 else (tgt - entry)
                    if r > 0 and r / entry >= MIN_RISK and td > 0 and t[e_i] <= end_ms:
                        x_i, x_px, kind = simulate(b, e_i, side, stop, tgt)
                        gross = side * (x_px - entry) / r
                        net = gross - FEE * entry / r
                        trades.append(dict(side=side, entry_ms=int(t[e_i]), entry_px=entry, exit_ms=int(t[x_i]), exit_px=float(x_px),
                                           entry_i=e_i, exit_i=x_i, kind=kind, r_pct=r / entry, tp_pct=td / entry,
                                           gross_r=gross, ret=net, net_bp=net * r / entry * 1e4))
                        i = x_i  # flat again after the exit bar
        else:
            lv = levels.get(day)
            if lv is not None:
                vl, vh = lv
                if c[i] > vh and c[i - 1] <= vh:
                    state = (-1, i, h[i], day)
                elif c[i] < vl and c[i - 1] >= vl:
                    state = (1, i, l[i], day)
        i += 1
    return trades


def placebo_r1(b, trades, start_ms, end_ms, draws=500, seed=1):
    """Per real trade a random 15m entry bar in the span, same side, same stop % and target %, same cap."""
    rng = np.random.default_rng(seed)
    lo = int(np.searchsorted(b["t"], start_ms))
    hi = int(np.searchsorted(b["t"], end_ms))
    means = []
    for _ in range(draws):
        rs = []
        for tr in trades:
            e_i = int(rng.integers(lo, hi))
            entry = float(b["o"][e_i])
            r = tr["r_pct"] * entry
            s = tr["side"]
            _, x_px, _ = simulate(b, e_i, s, entry - s * r, entry + s * tr["tp_pct"] * entry)
            rs.append(s * (x_px - entry) / r - FEE * entry / r)
        means.append(float(np.mean(rs)))
    return np.array(means)


def day_table(t, o):
    """(day_numbers, first_open_ms, first_open_px) per UTC day present."""
    d = t // D1
    cut = np.flatnonzero(np.diff(d)) + 1
    st = np.r_[0, cut]
    return d[st], t[st], o[st]


def poc_signals(profiles, days):
    """[(day d, side)] where POC_d, POC_{d-1}, POC_{d-2} are strictly monotone (all three days present)."""
    out = []
    for d in days:
        d = int(d)
        if d in profiles and d - 1 in profiles and d - 2 in profiles:
            a, b, c = profiles[d - 2][0], profiles[d - 1][0], profiles[d][0]
            if c > b > a:
                out.append((d, 1))
            elif c < b < a:
                out.append((d, -1))
    return out


def run_r2(profiles, days, ms0, px0, horizon, start_ms, end_ms):
    """Return-study trades: entry = open of day d+1, exit = open of day d+1+horizon. ret = net bp."""
    pos = {int(d): k for k, d in enumerate(days)}
    out = []
    nxt_ok = -10 ** 9
    for d, side in poc_signals(profiles, days):
        en, ex = d + 1, d + 1 + horizon
        if en not in pos or ex not in pos:
            continue
        if not (start_ms <= ms0[pos[en]] <= end_ms):
            continue
        if horizon > 1 and en < nxt_ok:
            continue  # non-overlapping: previous exit day not reached yet
        nxt_ok = ex
        e, x = float(px0[pos[en]]), float(px0[pos[ex]])
        net = side * (x / e - 1) * 1e4 - FEE_BP
        out.append(dict(side=side, entry_ms=int(ms0[pos[en]]), entry_px=e, exit_ms=int(ms0[pos[ex]]), exit_px=x, ret=net, net_bp=net))
    return out


def placebo_r2(days, ms0, px0, trades, horizon, start_ms, end_ms, draws=500, seed=1):
    rng = np.random.default_rng(seed)
    pos = {int(d): k for k, d in enumerate(days)}
    ok = [int(d) for d in days if start_ms <= ms0[pos[int(d)]] <= end_ms and int(d) + horizon in pos]
    means = []
    for _ in range(draws):
        rs = []
        for tr in trades:
            en = ok[int(rng.integers(0, len(ok)))]
            e, x = float(px0[pos[en]]), float(px0[pos[en + horizon]])
            rs.append(tr["side"] * (x / e - 1) * 1e4 - FEE_BP)
        means.append(float(np.mean(rs)))
    return np.array(means)
