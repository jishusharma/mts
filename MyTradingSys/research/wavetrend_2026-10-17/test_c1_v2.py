"""Fail-first tests for c1_v2.py (card wavetrend-c1-v2). Run: python -m pytest <this file>.

The card gate: the unmodified frozen detector (count_events.ev_C) FAILS a hand-built
fixture, while the versioned detector (c1_v2.events) PASSES. The defect DISPOSITION_2026-10-19.md
documented: v1 confirms PRICE pivots, then compares wt1 VALUES at the price-pivot bars without
confirming the WT pivots. The written spec (ATLAS_STUDY_SPEC s2, C1 row) requires BOTH paired
points to be confirmed pivots (price pivot + confirmed WT pivot, gap <= G).

Every v2 expectation below is HAND-DERIVED from the spec (confirmed-pivot lists computed by
eye from the bar arrays), not read from v1. k=2 throughout, G=20, t_ev = later of the two
confirmations.
"""
import numpy as np
import pytest

import c1_v2        # noqa: E402 versioned detector (this card)
import count_events as ce  # noqa: E402 frozen v1, untouched


def _arr(n, **specs):
    """length-n zero array with named ranges set: _arr(40, h1=(7,[0,11,13,12,11]))."""
    a = np.zeros(n, float)
    for name, (i, vals) in specs.items():
        a[i:i + len(vals)] = vals
    return a


# ------------------------------------------------------------------ 1. the card gate
def test_v1_fails_fixture_v2_passes():
    """The false-positive fixture: price pivots exist (H[9]=13 < H[19]=15, a higher high) but
    wt1 is MONOTONICALLY DECREASING, so there are NO confirmed WT pivots anywhere. Per the
    frozen spec, no pair is two confirmed pivots -> NO C1 event. The unmodified v1 compares
    wt1 AT the price-pivot bars (91 vs 81) and fires anyway.
    Hand: H pivots [(9,11),(19,21)]; wt1 strictly decreasing -> upper peak list empty,
    lower trough list empty -> v2 pairs nothing -> []. v1 fires [(21,1)]."""
    n = 30
    H = _arr(n, h8=(7, [0, 11, 13, 12, 11]), h2=(17, [0, 13, 15, 14, 12]))
    L = _arr(n)
    wt1 = np.array([100 - i for i in range(n)])        # strictly decreasing, all positive
    # v1's false positive (the defect): it fires on non-pivot wt1 values at the price-pivot bars.
    c1_v1, _ = ce.ev_C({"H": H, "L": L}, wt1, k=2, G=20, L=53)
    assert (21, 1) in c1_v1, "v1 must fire the false positive (this is the defect being corrected)"
    # v2 is correct: no confirmed WT pivot exists, so no pair, so no event.
    assert c1_v2.events({"H": H, "L": L}, wt1, k=2, G=20) == []


# ------------------------------------------------------------------ 2. the documented repro
def test_repro_c1_spec_mismatch_locations():
    """Byte-for-byte repro_c1_spec_mismatch case. v1 reports [(22,1)] by comparing wt1 at the
    PRICE-pivot bars (10, 20). The confirmed WT peaks actually sit at 12 and 18 -- the values
    v1 compared are NOT pivots. This test records that fact (v1's own pivot math, not v2's)."""
    n = 30
    H = _arr(n, h10=(10, [10.0]), h20=(20, [12.0]))   # H[10]=10, H[20]=12, rest 0
    L = _arr(n)
    wt1 = _arr(n, r1=(8, [8.0, 9.0, 10.0, 11.0, 12.0]), r2=(18, [10.0, 9.0, 8.0, 7.0, 6.0]))
    c1_v1, _ = ce.ev_C({"H": H, "L": L}, wt1, k=2, G=20, L=53)
    assert c1_v1 == [(22, 1)], c1_v1                     # v1 event at confirmation of price pivot p=20
    # the compared WT values (at bars 10 and 20) are NOT confirmed WT pivots:
    wt_peaks = c1_v2.pivots(wt1, 2, True)
    assert wt_peaks == [(12, 14), (18, 20)], wt_peaks    # peaks confirmed at 12 and 18, not 10 and 20
    assert not any(q in (10, 20) for q, _ in wt_peaks)


# ------------------------------------------------------------------ 3. positive cases (hand-derived)
def test_v2_upper_regular_divergence():
    """Higher high (H[9]=13 -> H[19]=15) with a LOWER confirmed WT peak (70 -> 68), both peaks
    strictly positive. One clean bearish (side +1) C1 at the later confirmation t_ev=21.
    Hand: H pivots [(9,11),(19,21)]; wt1 peaks [(9,11),(19,21)]; pair (19,19,21) vs (9,9,11):
    H higher, wt1 68<70, both>0 -> fire (21,+1). L all 0 -> no lower event."""
    n = 40
    H = _arr(n, h1=(7, [0, 11, 13, 12, 11]), h2=(17, [0, 13, 15, 14, 12]))
    L = _arr(n)
    wt1 = _arr(n, p1=(8, [60, 70, 65, 55]), p2=(18, [60, 68, 62, 55]))
    assert c1_v2.events({"H": H, "L": L}, wt1, k=2, G=20) == [(21, 1)]


def test_v2_lower_regular_divergence():
    """Lower low (L[9]=118 -> L[19]=116) with a HIGHER confirmed WT trough (-70 -> -68, both in
    the lower zone). One clean bullish (side -1) C1 at t_ev=21.
    Hand: L pivots [(9,11),(19,21)]; wt1 troughs [-wt1 peaks] [(9,11),(19,21)]; pair (19,19,21):
    L lower, -wt1 68<70, both>0 -> fire (21,-1). H all 0 -> no upper event."""
    n = 40
    H = _arr(n)
    L = np.full(n, 121.0)
    L[7:12] = [121, 120, 118, 119, 120]                 # p=9 (118)
    L[17:22] = [121, 120, 116, 118, 119]                # p=19 (116), lower low
    wt1 = _arr(n, t1=(8, [-60, -70, -65, -55]), t2=(18, [-60, -68, -62, -55]))
    assert c1_v2.events({"H": H, "L": L}, wt1, k=2, G=20) == [(21, -1)]


def test_v2_both_sides():
    """Both-side case: a bearish (side +1) upper divergence and a bullish (side -1) lower
    divergence on the same arrays -> two events, one per side. Verified hand-derivation
    (n=80, k=2, G=20):
      H pivots [(9,11),(19,21)]; wt1 upper peaks [(9,11) val 70, (19,21) val 68]
        -> pair (19,19): higher high 15>13, lower WT peak 68<70, both>0 -> fire t_ev=21 (21,+1).
      L pivots [(45,47),(55,57)]; -wt1 peaks [(45,47) val 70, (55,57) val 68]
        -> pair (55,55): lower low 116<118, higher WT trough -68 > -70, both in lower zone
        -> fire t_ev=57 (57,-1).
    L baseline 121 and a single 0..100 descent between regions keep each side's pivot lists
    from cross-sequencing the other side's features."""
    n = 80
    H = _arr(n, h1=(7, [0, 11, 13, 12, 11]), h2=(17, [0, 13, 15, 14, 12]))
    L = np.full(n, 121.0)
    L[43:48] = [121, 120, 118, 119, 120]                 # p=45 (118)
    L[53:58] = [121, 120, 116, 118, 119]                 # p=55 (116), lower low
    wt1 = np.zeros(n)
    wt1[7:12] = [55, 65, 70, 66, 60]                     # upper peak q=9 (70)
    wt1[17:22] = [63, 64, 68, 63, 55]                    # upper peak q=19 (68)
    wt1[43:48] = [-60, -66, -70, -66, -60]                # lower trough q=45 (-70)
    wt1[48:53] = [-55, -50, -45, -50, -55]
    wt1[53:58] = [-60, -66, -68, -66, -60]                # lower trough q=55 (-68)
    assert c1_v2.events({"H": H, "L": L}, wt1, k=2, G=20) == [(21, 1), (57, -1)]


def test_v2_confirmation_delay():
    """Pivot-confirmation delay: the second price pivot confirms at p2+k=21, the second (paired)
    WT peak confirms LATER at q2+k=27. t_ev must be the LATER confirmation (27), never the price
    bar's own 21. Hand: H pivots [(9,11),(19,21)]; wt1 peaks [(9,11),(25,27)]; G=20 pairs
    (19,25) -> t_ev=max(21,27)=27; H[19]>H[9], wt1[25]=65<wt1[9]=70 both>0 -> fire (27,+1)."""
    n = 44
    H = _arr(n, h1=(7, [0, 11, 13, 12, 11]), h2=(17, [0, 13, 15, 14, 12]))
    L = _arr(n)
    wt1 = _arr(n, p1=(8, [60, 70, 64, 60]), valley=(12, [40] * 12), p2=(24, [63, 65, 62, 60]))
    evs = c1_v2.events({"H": H, "L": L}, wt1, k=2, G=20)
    assert evs == [(27, 1)], evs
    assert 27 > 19 + 2                                    # later than the price pivot's own confirmation


def test_v2_no_divergence_when_wt_peak_not_lower():
    """Same higher-high price structure, but the second confirmed WT peak is HIGHER (70 -> 80):
    no upper divergence -> no event (v2 must not fire just because a higher high occurred).
    Hand: peaks [(9,11) val 70, (21,23) val 80]; pair (19? ) -> wt1[21]=80 not < wt1[9]=70 -> no fire."""
    n = 40
    H = _arr(n, h1=(7, [0, 11, 13, 12, 11]), h2=(17, [0, 13, 15, 14, 12]))
    L = _arr(n)
    wt1 = _arr(n, p1=(8, [60, 70, 65, 55]), p2=(20, [70, 80, 74, 70]))   # second peak 80 > 70
    assert c1_v2.events({"H": H, "L": L}, wt1, k=2, G=20) == []


def test_v2_causal_future_spike():
    """Causal: a huge price spike planted AFTER t_ev=21 must not move or kill the (21,+1) event
    (and no new event may carry t_ev < 21). Spiking H only adds H pivots, never WT pivots."""
    n = 40
    H = _arr(n, h1=(7, [0, 11, 13, 12, 11]), h2=(17, [0, 13, 15, 14, 12]))
    L = _arr(n)
    wt1 = _arr(n, p1=(8, [60, 70, 65, 55]), p2=(18, [60, 68, 62, 55]))
    base = c1_v2.events({"H": H, "L": L}, wt1, k=2, G=20)
    assert base == [(21, 1)]
    S = dict(H=H.copy(), L=L.copy())
    S["H"][30:33] = [40.0, 55.0, 40.0]                    # future spike, well past confirmation 21
    spiked = c1_v2.events(S, wt1, k=2, G=20)
    assert (21, 1) in spiked                                # the past event is untouched
    assert all(t >= 21 for t, _ in spiked)                  # nothing regressed earlier


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
