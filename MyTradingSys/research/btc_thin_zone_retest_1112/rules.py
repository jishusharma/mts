"""Rule code for PREREG.md (card btc-thin-zone-and-breakdown-retest-prereg-1112). Every number is the PREREG's.

Arrays are a 1m grid starting 2022-01-01 00:00 UTC (index i = minute i); missing bars are NaN.
Functions return trade dicts: side (+1/-1), entry_idx, exit_idx, entry_px, exit_px, stop, target, reason, gross_bp, net_bp.
SHIFT is a test hook only: a non-zero SHIFT feeds the rule bars from the future (a deliberately wrong, look-ahead version).
"""
import math

import numpy as np

DAY = 1440
FEE_BP = 10.0
W = 0.0005                      # bucket width of the log grid (0.05 %)
LNW = math.log(1.0 + W)
THIN_FRAC, NODE_FRAC, SEARCH = 0.25, 0.75, 100
T1_HOLD = 120                   # 24 x 5m bars
T2_HOLD = 2880                  # 48 x 1h bars
SHIFT = 0                       # test hook: look-ahead shift in 1m bars (must stay 0)


def edge(i):
    return math.exp(i * LNW)


def bucket(px):
    return np.floor(np.log(px) / LNW).astype(np.int64)


def walk(o, h, l, c, i0, side, stop, target, hold):
    """Fill walk from 1m bar i0 (entry at its open). Stop before target within a bar. None if the window has a missing bar."""
    j = i0 + hold
    if i0 < 0 or j > len(o):
        return None
    oo, hh, ll, cc = o[i0:j], h[i0:j], l[i0:j], c[i0:j]
    if np.isnan(oo).any() or np.isnan(hh).any() or np.isnan(ll).any() or np.isnan(cc).any():
        return None
    if side > 0:
        sh, th = ll <= stop, hh >= target
        spx = np.minimum(oo, stop)
    else:
        sh, th = hh >= stop, ll <= target
        spx = np.maximum(oo, stop)
    s = int(np.argmax(sh)) if sh.any() else hold + 1
    t = int(np.argmax(th)) if th.any() else hold + 1
    if s <= t and s <= hold:
        return i0 + s, float(spx[s]), "stop"
    if t <= hold and t < s:
        return i0 + t, float(target), "target"
    return j - 1, float(cc[-1]), "time"


def finish(side, i0, entry, res):
    xi, xp, why = res
    gross = side * (xp / entry - 1.0) * 1e4
    return dict(side=side, entry_idx=i0, exit_idx=xi, entry_px=entry, exit_px=xp, reason=why,
                gross_bp=gross, net_bp=gross - FEE_BP)


# ------------------------------------------------------------------ T1
def week_profile(vol, kb, day, kmin, size):
    """Volume per bucket (offset kmin) from days day-7 .. day-1; None before the warm-up is full."""
    a, b = (day - 7) * DAY, day * DAY
    if a < 0:
        return None
    k, v = kb[a:b], vol[a:b]
    ok = ~np.isnan(v) & (k > -(10 ** 9))
    return np.bincount(k[ok] - kmin, weights=v[ok], minlength=size)


def t1_triggers(o, h, l, c, v, first_day, last_day):
    """List of (entry_idx, side, k, stop, target) in time order, with the dropped counts."""
    tp = (h + l + c) / 3.0
    with np.errstate(invalid="ignore"):
        kb = np.where(np.isnan(tp), -(10 ** 9), bucket(np.where(np.isnan(tp), 1.0, tp)))
    good = kb[kb > -(10 ** 9)]
    kmin, kmax = int(good.min()) - 400, int(good.max()) + 400
    size = kmax - kmin + 1
    c5 = c[4::5]                                      # close of the 5m bar b (index 5b+4)
    k5 = np.full(len(c5), -(10 ** 9), dtype=np.int64)
    okc = ~np.isnan(c5)
    k5[okc] = bucket(c5[okc])
    out, drop = [], dict(no_node=0, bad_geometry=0, no_entry_bar=0)
    for day in range(first_day, last_day + 1):
        prof = week_profile(v, kb, day, kmin, size)
        if prof is None or prof.max() <= 0:
            continue
        poc = prof.max()
        thin, node = prof < THIN_FRAC * poc, prof >= NODE_FRAC * poc
        for b in range(day * 288, (day + 1) * 288):
            if b < 1 or b >= len(k5):
                continue
            k, kp = int(k5[b]), int(k5[b - 1])
            if k < -(10 ** 8) or kp < -(10 ** 8):
                continue
            ik, ip = k - kmin, kp - kmin
            if not (0 <= ik < size and 0 <= ip < size):
                continue
            if not (thin[ik] and not thin[ip]) or k == kp:
                continue
            side = 1 if k > kp else -1
            tgt = None
            if side > 0:
                for j in range(k + 1, k + SEARCH + 1):
                    if 0 <= j - kmin < size and node[j - kmin]:
                        tgt = edge(j)
                        break
                stop = edge(k - 1)
            else:
                for j in range(k - 1, k - SEARCH - 1, -1):
                    if 0 <= j - kmin < size and node[j - kmin]:
                        tgt = edge(j + 1)
                        break
                stop = edge(k + 2)
            if tgt is None:
                drop["no_node"] += 1
                continue
            e = 5 * (b + 1) + SHIFT
            if e >= len(o) or np.isnan(o[e]):
                drop["no_entry_bar"] += 1
                continue
            if not (stop < o[e] < tgt if side > 0 else tgt < o[e] < stop):
                drop["bad_geometry"] += 1
                continue
            out.append((e, side, k, stop, tgt))
    return out, drop


def run_t1(o, h, l, c, v, first_day, last_day):
    trig, drop = t1_triggers(o, h, l, c, v, first_day, last_day)
    return sequence(o, h, l, c, trig, T1_HOLD, drop)


def sequence(o, h, l, c, trig, hold, drop):
    """One position at a time, in entry order."""
    trades, busy = [], -1
    drop = dict(drop, busy=0, missing_bar=0)
    for e, side, _k, stop, tgt in sorted(trig, key=lambda x: x[0]):
        if e < busy:
            drop["busy"] += 1
            continue
        res = walk(o, h, l, c, e, side, stop, tgt, hold)
        if res is None:
            drop["missing_bar"] += 1
            continue
        t = finish(side, e, float(o[e]), res)
        t.update(stop=stop, target=tgt, hold=hold)
        trades.append(t)
        busy = res[0] + 1
    return trades, drop


# ------------------------------------------------------------------ T2
def hourly(o, h, l, c, v):
    n = len(o) // 60
    sh = lambda a: a[: n * 60].reshape(n, 60)
    bad = np.isnan(sh(o)).any(1) | np.isnan(sh(h)).any(1) | np.isnan(sh(l)).any(1) | np.isnan(sh(c)).any(1) | np.isnan(sh(v)).any(1)
    ho, hc = sh(o)[:, 0].copy(), sh(c)[:, -1].copy()
    hh, hl, hv = sh(h).max(1), sh(l).min(1), sh(v).sum(1)
    for a in (ho, hc, hh, hl, hv):
        a[bad] = np.nan
    return ho, hh, hl, hc, hv


def t2_triggers(o, h, l, c, v, first_hour, last_hour):
    ho, hh, hl, hc, hv = hourly(o, h, l, c, v)
    n = len(ho)
    out, drop = [], dict(no_retest=0, reclaimed=0, bad_geometry=0, no_entry_bar=0)
    for e in range(max(first_hour, 24), min(last_hour, n - 3) + 1):
        win = slice(e - 24, e)
        rh, rl = np.max(hh[win]), np.min(hl[win])
        med = np.median(hv[win])
        if np.isnan(rh) or np.isnan(rl) or np.isnan(med) or np.isnan(hc[e]) or np.isnan(hv[e]):
            continue
        if (rh - rl) / rl >= 0.025 or hv[e] < 2.0 * med:
            continue
        for side in (-1, 1):
            if side < 0:
                brk = hc[e] < rl and (hc[e + 1] < rl) and (hc[e + 2] < rl)
            else:
                brk = hc[e] > rh and (hc[e + 1] > rh) and (hc[e + 2] > rh)
            if not brk:
                continue
            lvl = rl if side < 0 else rh
            trig = None
            for t in range(e + 3, min(e + 3 + 24, n)):
                if np.isnan(hh[t]) or np.isnan(hl[t]) or np.isnan(hc[t]):
                    break
                touch = hh[t] >= lvl if side < 0 else hl[t] <= lvl
                if touch:
                    trig = t if (hc[t] < lvl if side < 0 else hc[t] > lvl) else -1
                    break
            if trig is None:
                drop["no_retest"] += 1
                continue
            if trig < 0:
                drop["reclaimed"] += 1
                continue
            seg = slice(e, trig + 1)
            ent = (trig + 1) * 60 + SHIFT
            if ent >= len(o) or np.isnan(o[ent]):
                drop["no_entry_bar"] += 1
                continue
            if side < 0:
                stop, tgt = np.max(hh[seg]) * 1.002, np.min(hl[seg])
                okg = tgt < o[ent] < stop
            else:
                stop, tgt = np.min(hl[seg]) * 0.998, np.max(hh[seg])
                okg = stop < o[ent] < tgt
            if not okg:
                drop["bad_geometry"] += 1
                continue
            out.append((ent, side, e, float(stop), float(tgt)))
    return out, drop


def run_t2(o, h, l, c, v, first_hour, last_hour):
    trig, drop = t2_triggers(o, h, l, c, v, first_hour, last_hour)
    return sequence(o, h, l, c, trig, T2_HOLD, drop)
