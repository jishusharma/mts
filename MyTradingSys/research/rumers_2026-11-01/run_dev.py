"""Rumers DEV runner: the 5 FROZEN rules of PRE_REG.md on BTCUSDT 1m, DEV 2022-04-01..2024-06-30, fee-net.

Conventions (HARNESS.md s.1): closed bars only, entry = open of the 1m bar after the signal bar closes, stop counted first on
a same-bar hit, fees = BINANCE_TAKER * 2 (stress TAKER_RT_PCT), day-clustered SE, two-sided p, Holm over m = 5.
VALIDATION / HOLDOUT months are never opened: only 2022-01..2024-06 files are read (2022-01..03 = indicator warm-up only,
entries start 2022-04-01). Exits that would run past 2024-06-30 23:59Z are closed at the last DEV bar (OURS).

Parameters not fixed by PRE_REG.md are labelled OURS in code comments and in DEV_CHECK.md.

CLI: python run_dev.py [--count-only] [--shift -1|0|1] [--out DIR] [--data-dir DIR]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest.fees import BINANCE_TAKER  # noqa: E402
from MyTradingSys.backtest.research_kit import TAKER_RT_PCT, cluster_mean_se, holm, norm_p_two  # noqa: E402

MIN_MS, DAY_MS, HOUR_MS = 60_000, 86_400_000, 3_600_000
START_MS = 1648771200000        # 2022-04-01 00:00Z
END_MS = 1719792000000          # 2024-07-01 00:00Z (exclusive)
FEE_RT = BINANCE_TAKER * 2      # 0.10 % round trip (SOURCED fees.py)
FEE_RT_STRESS = TAKER_RT_PCT / 100.0
M_RULES = 5
TICK = 0.1                      # OURS: Binance BTCUSDT perp tick
ATR_N = 14
SESSIONS_MS = (0, 13 * HOUR_MS + 30 * MIN_MS)   # 00:00 and 13:30 UTC (PRE_REG R1 SOURCED)
CAP_BARS = 7 * 1440             # OURS: time stop at 7 days, close at the bar close
REV_WIN, TRIG_WIN = 12, 6       # OURS: 5m bars allowed for the reversal bar, then for the break
PIN_WICK = 0.5                  # OURS: pin = wick >= 50 % of bar range
N_GATE = 100                    # OURS: DEV pass needs n >= 100
N_MIN = 30                      # OURS: n < 30 = NOT ENOUGH DATA
BAR_MS = {"R1": 5 * MIN_MS, "R2": 5 * MIN_MS, "R3": 5 * MIN_MS, "R4": 5 * MIN_MS, "R5": 15 * MIN_MS}


# ------------------------------------------------------------------ data
def load_months(data_dir, months):
    """Read 1m csv files; returns (ts, o, h, l, c, v, {file: sha256})."""
    parts, shas = [], {}
    for ym in months:
        f = Path(data_dir) / f"BTCUSDT-1m-{ym}.csv"
        shas[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
        with open(f, "r", newline="") as fh:
            first = fh.readline()
        skip = 1 if first.lower().startswith("open_time") else 0
        a = np.loadtxt(f, delimiter=",", skiprows=skip, usecols=(0, 1, 2, 3, 4, 5))
        parts.append(a)
    a = np.vstack(parts)
    ts = a[:, 0].astype(np.int64)
    ts = np.where(ts > 10 ** 14, ts // 1000, ts)
    order = np.argsort(ts, kind="stable")
    a, ts = a[order], ts[order]
    keep = np.r_[True, np.diff(ts) > 0]
    return ts[keep], a[keep, 1], a[keep, 2], a[keep, 3], a[keep, 4], a[keep, 5], shas


def dev_months():
    out = []
    for y in (2022, 2023, 2024):
        for m in range(1, 13):
            if (y, m) <= (2024, 6):
                out.append(f"{y}-{m:02d}")
    return out


def agg(ts, o, h, l, c, v, tf_ms):
    """Epoch-aligned resample of 1m to tf_ms (same buckets as tf_resample 'seconds' unit). Only complete buckets survive."""
    b = ts // tf_ms
    idx = np.flatnonzero(np.r_[True, b[1:] != b[:-1]])
    cnt = np.diff(np.r_[idx, len(ts)])
    last = np.r_[idx[1:] - 1, len(ts) - 1]
    full = cnt == tf_ms // MIN_MS
    t = b[idx] * tf_ms
    return {"t": t[full], "o": o[idx][full], "h": np.maximum.reduceat(h, idx)[full], "l": np.minimum.reduceat(l, idx)[full],
            "c": c[last][full], "v": np.add.reduceat(v, idx)[full], "tf": tf_ms}


def build_views(ts, o, h, l, c, v):
    V = {"ts": ts, "o": o, "h": h, "l": l, "c": c, "v": v}
    for name, tf in (("m5", 5 * MIN_MS), ("m15", 15 * MIN_MS), ("h1", HOUR_MS), ("d1", DAY_MS)):
        V[name] = agg(ts, o, h, l, c, v, tf)
    d = V["d1"]
    n = len(d["t"])
    tr = np.full(n, np.nan)
    for i in range(1, n):
        if d["t"][i] - d["t"][i - 1] == DAY_MS:
            tr[i] = max(d["h"][i] - d["l"][i], abs(d["h"][i] - d["c"][i - 1]), abs(d["l"][i] - d["c"][i - 1]))
    atr, sma = np.full(n, np.nan), np.full(n, np.nan)
    for i in range(n):
        if i >= ATR_N - 1 and np.isfinite(tr[i - ATR_N + 1:i + 1]).all():
            atr[i] = tr[i - ATR_N + 1:i + 1].mean()           # plain SMA of true range (FORMULAS s.12)
        if i >= 49 and (np.diff(d["t"][i - 49:i + 1]) == DAY_MS).all():
            sma[i] = d["c"][i - 49:i + 1].mean()
    d["atr"], d["sma50"] = atr, sma
    return V


def prev_day_idx(V, t):
    """Index of the daily bar of the day BEFORE the day of each timestamp in t; -1 where the prior day is missing."""
    d = V["d1"]["t"]
    di = np.searchsorted(d, (t // DAY_MS) * DAY_MS, side="left")
    ok = (di > 0) & (di < len(d))
    ok &= d[np.clip(di, 0, len(d) - 1)] == (t // DAY_MS) * DAY_MS
    prev = np.where(ok, di - 1, -1)
    ok2 = prev >= 0
    ok2 &= (d[np.clip(di, 0, len(d) - 1)] - d[np.clip(prev, 0, None)]) == DAY_MS
    return np.where(ok2, prev, -1)


def sig(close_ms, side, stop, target, partial=False, note=""):
    return {"sig_ms": int(close_ms), "side": int(side), "stop": float(stop), "target": float(target), "partial": partial,
            "note": note}


# ------------------------------------------------------------------ rules (PRE_REG.md, frozen)
def _session_setups(V, atr_frac, mode):
    """R1 / R4 shared: first 15m candle of a session (00:00, 13:30 UTC) with range >= atr_frac * prior-day ATR(14).
    mode 'R1': both directions, reversal = pin bar (OURS), stop = manipulation extreme, target = candle midpoint.
    mode 'R4': direction by prior daily close vs SMA50, reversal = first bar closing with the trend (OURS), stop = day extreme
    so far, target = open of the 15m candle."""
    m5, m15, d1 = V["m5"], V["m15"], V["d1"]
    out = []
    t15 = m15["t"]
    dpos = {int(t): i for i, t in enumerate(d1["t"])}
    for day0 in range(int(m15["t"][0] // DAY_MS), int(m15["t"][-1] // DAY_MS) + 1):
        dms = day0 * DAY_MS
        di = dpos.get(dms)
        if di is None or di < 1 or d1["t"][di - 1] != dms - DAY_MS:
            continue
        atr, sma, pclose = d1["atr"][di - 1], d1["sma50"][di - 1], d1["c"][di - 1]
        if not np.isfinite(atr):
            continue
        if mode == "R4" and not np.isfinite(sma):
            continue
        for off in SESSIONS_MS:
            s0 = dms + off
            j = np.searchsorted(t15, s0)
            if j >= len(t15) or t15[j] != s0:
                continue
            o15, h15, l15, c15 = m15["o"][j], m15["h"][j], m15["l"][j], m15["c"][j]
            if (h15 - l15) < atr_frac * atr or c15 == o15:
                continue
            up = c15 > o15
            if mode == "R1":
                side = -1 if up else 1          # fade the manipulation move
            else:
                side = 1 if pclose > sma else -1
                if (side == 1 and up) or (side == -1 and not up):
                    continue                    # 15m move must be counter-trend
            k0 = np.searchsorted(m5["t"], s0 + 15 * MIN_MS)
            if k0 >= len(m5["t"]):
                continue
            rev = None
            for k in range(k0, min(k0 + REV_WIN, len(m5["t"]))):
                if m5["t"][k] != s0 + 15 * MIN_MS + (k - k0) * 5 * MIN_MS:
                    break
                bo, bh, bl, bc = m5["o"][k], m5["h"][k], m5["l"][k], m5["c"][k]
                rng = bh - bl
                if rng <= 0:
                    continue
                if mode == "R1":
                    wick = (bh - max(bo, bc)) if side == -1 else (min(bo, bc) - bl)
                    ok = wick >= PIN_WICK * rng and ((bc < bo) if side == -1 else (bc > bo))
                else:
                    ok = (bc > bo) if side == 1 else (bc < bo)
                if ok:
                    rev = k
                    break
            if rev is None:
                continue
            for k in range(rev + 1, min(rev + 1 + TRIG_WIN, len(m5["t"]))):
                if m5["t"][k] != m5["t"][rev] + (k - rev) * 5 * MIN_MS:
                    break
                hit = (m5["c"][k] < m5["l"][rev]) if side == -1 else (m5["c"][k] > m5["h"][rev])
                if hit:
                    if mode == "R1":
                        stop = h15 if side == -1 else l15
                        target = (h15 + l15) / 2.0
                    else:
                        ds = np.searchsorted(m5["t"], dms)
                        stop = m5["l"][ds:k + 1].min() if side == 1 else m5["h"][ds:k + 1].max()
                        target = o15
                    out.append(sig(m5["t"][k] + 5 * MIN_MS, side, stop, target, note=f"{mode}@{s0}"))
                    break
    return out


def rule_r1(V):
    return _session_setups(V, 0.20, "R1")


def rule_r4(V):
    return _session_setups(V, 0.25, "R4")


def rule_r2(V):
    """PDH/PDL sweep fade on 5m: pierce by >= 1 tick and close back inside the prior day range in the same 5m bar."""
    m5, d1 = V["m5"], V["d1"]
    pi = prev_day_idx(V, m5["t"])
    ok = pi >= 0
    pdh = np.where(ok, d1["h"][np.clip(pi, 0, None)], np.nan)
    pdl = np.where(ok, d1["l"][np.clip(pi, 0, None)], np.nan)
    with np.errstate(invalid="ignore"):
        up = (m5["h"] >= pdh + TICK) & (m5["c"] < pdh) & (m5["c"] > pdl)
        dn = (m5["l"] <= pdl - TICK) & (m5["c"] > pdl) & (m5["c"] < pdh)
    both = up & dn
    up, dn = up & ~both, dn & ~both
    out = []
    day = m5["t"] // DAY_MS
    for mask, side in ((up, -1), (dn, 1)):
        idx = np.flatnonzero(mask)
        if len(idx) == 0:
            continue
        _, first = np.unique(day[idx], return_index=True)       # first sweep per day and side (OURS)
        for k in idx[first]:
            mid = (pdh[k] + pdl[k]) / 2.0                        # Target 1 (OURS pick of T1 vs T2)
            stop = m5["h"][k] + 2 * TICK if side == -1 else m5["l"][k] - 2 * TICK
            out.append(sig(m5["t"][k] + 5 * MIN_MS, side, stop, mid, note="R2"))
    out.sort(key=lambda s: s["sig_ms"])
    return out


def _rsi_wilder(c, n=14):
    r = np.full(len(c), np.nan)
    if len(c) <= n:
        return r
    d = np.diff(c)
    up, dn = np.maximum(d, 0), np.maximum(-d, 0)
    au, ad = up[:n].mean(), dn[:n].mean()
    r[n] = 100.0 if ad == 0 else 100 - 100 / (1 + au / ad)
    for k in range(n + 1, len(c)):             # bar k uses its own close-to-close change d[k - 1]
        au = (au * (n - 1) + up[k - 1]) / n
        ad = (ad * (n - 1) + dn[k - 1]) / n
        r[k] = 100.0 if ad == 0 else 100 - 100 / (1 + au / ad)
    return r


def rule_r3(V):
    """Daily-VWAP separator fade: |close - VWAP| > 1.5 x ATR14(5m) and RSI14 >= 70 / <= 30, then first reversal bar."""
    m5 = V["m5"]
    n = len(m5["t"])
    if n < 50:
        return []
    h, l, c, o = m5["h"], m5["l"], m5["c"], m5["o"]
    tp = (h + l + c) / 3.0
    day = m5["t"] // DAY_MS
    cv, cpv = np.cumsum(m5["v"]), np.cumsum(tp * m5["v"])
    first = np.flatnonzero(np.r_[True, day[1:] != day[:-1]])
    base_i = np.repeat(first, np.diff(np.r_[first, n]))
    base_v = np.where(base_i > 0, cv[np.clip(base_i - 1, 0, None)], 0.0)
    base_pv = np.where(base_i > 0, cpv[np.clip(base_i - 1, 0, None)], 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        vwap = (cpv - base_pv) / (cv - base_v)
    tr = np.r_[h[0] - l[0], np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))]
    cs = np.cumsum(tr)
    atr5 = np.full(n, np.nan)
    atr5[ATR_N - 1:] = (cs[ATR_N - 1:] - np.r_[0.0, cs[:-ATR_N]]) / ATR_N
    rsi = _rsi_wilder(c)
    with np.errstate(invalid="ignore"):
        shortc = (c - vwap > 1.5 * atr5) & (rsi >= 70)
        longc = (vwap - c > 1.5 * atr5) & (rsi <= 30)
    out, i = [], 0
    cand = np.flatnonzero(shortc | longc)
    ci = 0
    while ci < len(cand):
        i = cand[ci]
        side = -1 if shortc[i] else 1
        r = None
        for k in range(i + 1, min(i + 1 + TRIG_WIN, n)):
            if m5["t"][k] - m5["t"][i] != (k - i) * 5 * MIN_MS:
                break
            if (c[k] < o[k]) if side == -1 else (c[k] > o[k]):    # first reversal candle toward VWAP (OURS)
                r = k
                break
        if r is None:
            ci += 1
            continue
        peak = h[i:r + 1].max() if side == -1 else l[i:r + 1].min()
        stop = peak + 2 * TICK if side == -1 else peak - 2 * TICK
        out.append(sig(m5["t"][r] + 5 * MIN_MS, side, stop, vwap[r], note="R3"))
        ci = np.searchsorted(cand, r + 1)
    return out


def rule_r5(V):
    """1h 5-bar-fractal range, 15m sucker move into the outer 25 % band, confirmation candle, close-break entry."""
    h1, m15 = V["h1"], V["m15"]
    n1 = len(h1["t"])
    ph, pl = [], []
    for q in range(4, n1):                                       # q = last closed 1h bar; the fractal centre is bar q-2
        if not (np.diff(h1["t"][q - 4:q + 1]) == HOUR_MS).all():
            continue
        win_h, win_l = h1["h"][q - 4:q + 1], h1["l"][q - 4:q + 1]
        if win_h[2] == win_h.max() and (win_h == win_h.max()).sum() == 1:
            ph.append((h1["t"][q] + HOUR_MS, win_h[2]))          # known at the close of bar q
        if win_l[2] == win_l.min() and (win_l == win_l.min()).sum() == 1:
            pl.append((h1["t"][q] + HOUR_MS, win_l[2]))
    if not ph or not pl:
        return []
    cth, vh = np.array([x[0] for x in ph]), np.array([x[1] for x in ph])
    ctl, vl = np.array([x[0] for x in pl]), np.array([x[1] for x in pl])
    t, o, h, l, c = m15["t"], m15["o"], m15["h"], m15["l"], m15["c"]
    n = len(t)
    ih = np.searchsorted(cth, t, side="right") - 1
    il = np.searchsorted(ctl, t, side="right") - 1
    sh = np.where(ih >= 0, vh[np.clip(ih, 0, None)], np.nan)
    sl = np.where(il >= 0, vl[np.clip(il, 0, None)], np.nan)
    out, cf = [], 2                                          # cf = current (confirmation) candle; s1 = last sucker candle
    while cf < n - 2:
        s1, s2 = cf - 1, cf - 2
        rng_ = sh[s1] - sl[s1]
        if not (np.isfinite(rng_) and rng_ > 0) or t[cf] - t[s2] != 30 * MIN_MS:
            cf += 1
            continue
        side = 0
        if c[s1] < o[s1] and c[s2] < o[s2] and l[s1] <= sl[s1] + 0.25 * rng_:
            side = 1
        elif c[s1] > o[s1] and c[s2] > o[s2] and h[s1] >= sh[s1] - 0.25 * rng_:
            side = -1
        # confirmation candle: first reversal candle (opposite colour) right after the sucker run
        if side == 0 or not ((c[cf] > o[cf]) if side == 1 else (c[cf] < o[cf])):
            cf += 1
            continue
        a = s1
        while a - 1 >= 0 and ((c[a - 1] < o[a - 1]) if side == 1 else (c[a - 1] > o[a - 1])):
            a -= 1
        trig = None
        for j in range(cf + 1, min(cf + 5, n)):
            if t[j] - t[cf] != (j - cf) * 15 * MIN_MS:
                break
            if (c[j] > h[cf]) if side == 1 else (c[j] < l[cf]):
                trig = j
                break
        if trig is None:
            cf += 1
            continue
        stop = l[a:cf + 1].min() - 2 * TICK if side == 1 else h[a:cf + 1].max() + 2 * TICK
        target = sh[s1] if side == 1 else sl[s1]
        out.append(sig(t[trig] + 15 * MIN_MS, side, stop, target, partial=True, note="R5"))
        cf = trig + 2
    return out


RULES = {"R1": rule_r1, "R2": rule_r2, "R3": rule_r3, "R4": rule_r4, "R5": rule_r5}
NAMES = {"R1": "RUMERS-ORB-MANIP-REVERSAL", "R2": "RUMERS-BOX-PDH-PDL-FADE", "R3": "RUMERS-VWAP-SEPARATOR-MEAN-REVERSION",
         "R4": "RUMERS-ORR-25PCT-ATR-SWEEP", "R5": "RUMERS-MAGIC-LINE-PITCHFORK-REVERSAL"}


# ------------------------------------------------------------------ simulation
def _first(mask):
    return int(np.argmax(mask)) if mask.any() else -1


def simulate(V, s, shift, bar_ms, start_ms=START_MS, end_ms=END_MS, outcome=True):
    """One trade. Returns dict or None (outside window / gap / invalid geometry). Gross R before fees; stop first on ties."""
    ts = V["ts"]
    want = s["sig_ms"] + shift * bar_ms
    i0 = int(np.searchsorted(ts, want))
    if i0 >= len(ts) or ts[i0] != want or want < start_ms or s["sig_ms"] >= end_ms or want >= end_ms:
        return None
    side, stop, target = s["side"], s["stop"], s["target"]
    entry = V["o"][i0]
    if not ((stop < entry < target) if side == 1 else (target < entry < stop)):
        return None
    if not outcome:                    # count-only: geometry of the entry open, no outcome read
        return {"entry_ms": int(ts[i0])}
    risk = abs(entry - stop)
    end = min(i0 + CAP_BARS, len(ts))
    hs, ls, os_ = V["h"][i0:end], V["l"][i0:end], V["o"][i0:end]
    if side == 1:
        sk, tk = ls <= stop, hs >= target
    else:
        sk, tk = hs >= stop, ls <= target
    fs, ft = _first(sk), _first(tk)
    big = 10 ** 9
    fs_, ft_ = (fs if fs >= 0 else big), (ft if ft >= 0 else big)

    def stop_px(k):
        px = os_[k]
        return min(stop, px) if side == 1 else max(stop, px)

    def r_of(px):
        return side * (px - entry) / risk

    tgt_r = abs(target - entry) / risk
    kind, exit_k, gross = None, None, None
    if s["partial"] and tgt_r > 1.0:
        p1 = entry + side * risk
        pk = (hs >= p1) if side == 1 else (ls <= p1)
        fp = _first(pk)
        fp_ = fp if fp >= 0 else big
        if fs_ < big and fs_ <= min(fp_, ft_):
            kind, exit_k, gross = "S", fs_, r_of(stop_px(fs_))
        elif fp_ < big:
            # partial 1R filled at bar fp; remaining half: break-even stop (stop first from the same bar), target
            be_hit = (ls[fp_:] <= entry) if side == 1 else (hs[fp_:] >= entry)
            tg_hit = tk[fp_:]
            fb, ftg = _first(be_hit), _first(tg_hit)
            fb_, ftg_ = (fb if fb >= 0 else big), (ftg if ftg >= 0 else big)
            if fb_ <= ftg_ and fb_ < big:
                kind, exit_k, gross = "P_BE", fp_ + fb_, 0.5 * 1.0
            elif ftg_ < big:
                kind, exit_k, gross = "P_T", fp_ + ftg_, 0.5 * 1.0 + 0.5 * tgt_r
            else:
                kind, exit_k = "TO", end - i0 - 1
                gross = 0.5 + 0.5 * r_of(V["c"][end - 1])
        else:
            kind, exit_k, gross = "TO", end - i0 - 1, r_of(V["c"][end - 1])
    else:
        if fs_ <= ft_ and fs_ < big:
            kind, exit_k, gross = "S", fs_, r_of(stop_px(fs_))
        elif ft_ < big:
            kind, exit_k, gross = "T", ft_, tgt_r
        else:
            kind, exit_k, gross = "TO", end - i0 - 1, r_of(V["c"][end - 1])
    stop_pct = risk / entry
    return {"entry_ms": int(ts[i0]), "exit_ms": int(ts[i0 + exit_k]), "side": side, "entry": float(entry), "stop_pct": stop_pct,
            "kind": kind, "gross_r": float(gross), "net_r": float(gross - FEE_RT / stop_pct),
            "net_r_stress": float(gross - FEE_RT_STRESS / stop_pct), "day": int(ts[i0] // DAY_MS)}


def run_rule(V, rule, shift, sigs=None, start_ms=START_MS, end_ms=END_MS):
    sigs = RULES[rule](V) if sigs is None else sigs
    trades, free_at, invalid = [], -1, 0
    for s in sigs:
        if s["sig_ms"] < start_ms or s["sig_ms"] >= end_ms:
            continue
        tr = simulate(V, s, shift, BAR_MS[rule], start_ms, end_ms)
        if tr is None:
            invalid += 1
            continue
        if tr["entry_ms"] < free_at:       # one open position per rule (OURS)
            continue
        free_at = tr["exit_ms"] + MIN_MS
        trades.append(tr)
    return trades, invalid


# ------------------------------------------------------------------ stats
def stats(trades):
    n = len(trades)
    if n == 0:
        return {"n": 0, "hit_rate": float("nan"), "mean_net_r": float("nan"), "se": float("nan"), "p": float("nan"),
                "mean_net_r_stress": float("nan"), "mean_gross_r": float("nan"), "median_stop_pct": float("nan")}
    g = np.array([t["net_r"] for t in trades])
    gs = np.array([t["net_r_stress"] for t in trades])
    day = [t["day"] for t in trades]
    m, se = cluster_mean_se(g, day)
    ms, ses = cluster_mean_se(gs, day)
    p = norm_p_two(m / se) if se == se and se > 0 else float("nan")
    kinds = {}
    for t in trades:
        kinds[t["kind"]] = kinds.get(t["kind"], 0) + 1
    return {"n": n, "hit_rate": float((g > 0).mean()), "mean_net_r": m, "se": se, "p": p, "mean_net_r_stress": ms,
            "mean_gross_r": float(np.mean([t["gross_r"] for t in trades])),
            "median_stop_pct": float(np.median([t["stop_pct"] for t in trades]) * 100), "exit_kinds": kinds,
            "longs": int(sum(1 for t in trades if t["side"] == 1))}


def verdict(st, holm_p):
    if st["n"] < N_MIN:
        return "NOT ENOUGH DATA"
    if st["mean_net_r"] > 0 and holm_p == holm_p and holm_p < 0.05 and st["n"] >= N_GATE:
        return "PASS-DEV"
    if st["mean_net_r"] <= 0 and st["n"] >= N_GATE:
        return "FAIL"
    return "INCONCLUSIVE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count-only", action="store_true")
    ap.add_argument("--shift", type=int, default=0, choices=(-1, 0, 1))
    ap.add_argument("--data-dir", default="F:/MTS/Dumps/backtest/raw_1m_2022/klines")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "run_out"))
    a = ap.parse_args()
    ts, o, h, l, c, v, shas = load_months(a.data_dir, dev_months())
    print(f"loaded {len(ts)} 1m bars {ts[0]}..{ts[-1]} from {len(shas)} month files")
    for k, s in shas.items():
        print(f"sha256 {k} {s}")
    V = build_views(ts, o, h, l, c, v)
    out = {"shift": a.shift, "count_only": a.count_only, "sha256": shas, "bars_1m": int(len(ts)), "rules": {}}
    Path(a.out).mkdir(parents=True, exist_ok=True)
    allp = []
    for r in RULES:
        sigs = RULES[r](V)
        dev = [s for s in sigs if START_MS <= s["sig_ms"] < END_MS]
        if a.count_only:
            valid = sum(1 for s in dev if simulate(V, s, a.shift, BAR_MS[r], outcome=False) is not None)
            out["rules"][r] = {"name": NAMES[r], "triggers": len(dev), "valid_geometry_before_overlap": valid}
            print(r, out["rules"][r])
            continue
        tr, inval = run_rule(V, r, a.shift, sigs)
        st = stats(tr)
        st.update({"name": NAMES[r], "triggers": len(dev), "invalid_geometry": inval})
        out["rules"][r] = st
        allp.append(st["p"] if st["p"] == st["p"] else 1.0)
        print(r, {k: (round(x, 5) if isinstance(x, float) else x) for k, x in st.items()})
    if not a.count_only:
        hp = holm(allp, M_RULES)
        for (r, st), p in zip(out["rules"].items(), hp):
            st["holm_p"] = float(p)
            st["verdict"] = verdict(st, p)
            print(r, "holm_p", round(float(p), 5), st["verdict"])
    tag = "count" if a.count_only else f"shift{a.shift:+d}"
    (Path(a.out) / f"dev_{tag}.json").write_text(json.dumps(out, indent=1, default=float) + "\n", newline="\n")


if __name__ == "__main__":
    main()
