"""Versioned C1 divergence detector, c1-v2 (card wavetrend-c1-v2) — frozen spec compliance.

Corrects the defect DISPOSITION_2026-10-19.md found in the frozen v1 (`count_events.ev_C`):
v1 confirms price pivots only, then compares wt1 VALUES at the price-pivot bars without
confirming the WT pivots. The written spec (ATLAS_STUDY_SPEC s2, C1 row) requires BOTH to be
confirmed pivots: a confirmed price pivot (k right-hand bars, k OURS) paired with the
confirmed WT pivot making a lower/higher extreme, gap <= G bars (OURS), regular first,
hidden later. c1-v2 pairs the two confirmed-pivot lists.

v1 stays frozen and untouched (its frozen atlas results stand). c1-v2 is new code,
count-only, DEV only (< 2024-07-01, the input manifest is sealed by count_events.load_dev).
No return, MFE/MAE, fee, VALIDATION or HOLDOUT read anywhere in this module.

Confirmed-pivot convention (inherited from v1, ATLAS_STUDY_SPEC s2): a pivot at bar p is
KNOWN only at t_conf = p + k, when the k right-hand bars have closed. A paired event is
dated t_ev = the LATER of the two confirmations (max(p + k, q + k)), never earlier, so the
event uses only bars <= t_ev.

Zone guard: both compared WT pivot values must be strictly on the event side
(sgn * wt1 > 0) — the v1 convention (the L band belongs to C2, not C1).

Golden expected values in test_c1_v2.py are hand-derived from the spec above, not from v1.
"""
import numpy as np

VERSION = "c1-v2"


def pivots(x, k, hi=True):
    """Confirmed pivots as (p, t_confirm=p+k): x[p] strictly beyond the k bars to the left,
    not beyond the k bars to the right (hi) or mirror (lo). NaN anywhere in the window ->
    no pivot. Same confirmed-pivot convention as the frozen v1 detector, restated per spec."""
    out = []
    n = len(x)
    for p in range(k, n - k):
        w = x[p - k:p + k + 1]
        if np.isnan(w).any():
            continue
        left, right = w[:k], w[k + 1:]
        if hi:
            if x[p] > left.max() and x[p] >= right.max():
                out.append((p, p + k))
        else:
            if x[p] < left.min() and x[p] <= right.min():
                out.append((p, p + k))
    return out


def _pair(pp, wp, G):
    """Lock-step one-to-one pairing of two confirmed-pivot lists (both left-to-right).

    The next unused price pivot p and the next unused WT pivot q form a pair when
    |p - q| <= G (G, max bars between pivots, OURS); a too-far pivot is skipped on the
    side that trails. Pairs carry both pivot positions; t_ev = max(p + k, q + k) with k
    the confirmed-pivot lag (identical on both lists, so the max of the two confirmations).
    """
    pairs, i, j = [], 0, 0
    while i < len(pp) and j < len(wp):
        p, tp = pp[i]
        q, tq = wp[j]
        if abs(p - q) <= G:
            pairs.append((p, q, max(tp, tq)))
            i += 1; j += 1
        elif p < q:
            i += 1                                        # p is too far before every remaining WT pivot
        else:
            j += 1
    return pairs


def events(B, wt1, k, G):
    """C1 v2 regular divergence, both sides. side +1 = upper zone (bearish): confirmed H
    pivot paired with a confirmed wt1 peak; side -1 = lower zone (long): confirmed L pivot
    paired with a confirmed wt1 trough. A pair fires vs the previous pair when the price
    pivot goes further (upper: higher high; lower: lower low) while the paired WT pivot
    goes less (upper: lower peak; lower: higher trough), with both WT pivot values
    strictly on the event side (sgn * wt1 > 0, v1 zone guard; the L band is C2's, not
    C1's). Returns sorted [(t_ev, side)], t_ev = later confirmation of the firing pair.
    """
    out = []
    for hi, sgn in ((True, 1), (False, -1)):
        px = B["H"] if hi else B["L"]
        pp = pivots(px, k, hi)
        wp = pivots(wt1 * sgn, k, True)                 # peaks of sgn*wt1 = troughs for sgn=-1
        prev = None
        for p, q, t_ev in _pair(pp, wp, G):
            if prev is not None:
                p2, q2, _ = prev
                price_more = (px[p] > px[p2]) if hi else (px[p] < px[p2])
                wq, wpv = sgn * wt1[q], sgn * wt1[q2]
                if price_more and wq < wpv and wpv > 0 and wq > 0:
                    out.append((t_ev, sgn))
            prev = (p, q, t_ev)
    out.sort()
    return out


__all__ = ["VERSION", "pivots", "events"]
