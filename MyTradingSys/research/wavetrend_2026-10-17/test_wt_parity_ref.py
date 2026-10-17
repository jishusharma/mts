"""Contract checks for wt_parity_ref (run: python test_wt_parity_ref.py). Exit 0 = pass."""
import math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wt_parity_ref import wavetrend, cross_events, ema, NAN

def synth(n, seed=7):
    r = random.Random(seed); p = 30000.0; H = []; L = []; C = []
    for _ in range(n):
        o = p; p *= 1 + r.gauss(0, 0.004); hi = max(o, p) * 1.001; lo = min(o, p) * 0.999
        H.append(hi); L.append(lo); C.append(p)
    return H, L, C


def test_contract():
    # 1. flat input: d == 0 everywhere -> every output NaN, no event (fail closed)
    f = [100.0] * 80
    w1, w2 = wavetrend(f, f, f)
    assert all(math.isnan(v) for v in w1 + w2), "flat input must give NaN, not 0 or inf"
    assert not any(cross_events(w1, w2))
    f2 = [100.3] * 120   # non-representable flat price: EMA residue must still be treated as d == 0
    w1, w2 = wavetrend(f2, f2, f2)
    assert all(math.isnan(v) for v in w1 + w2), "float residue must not become a huge ci"

    # 2. seed sensitivity: first-value seed vs SMA seed converge; report the bar after which |diff| < 1e-3 WT points
    H, L, C = synth(1500)
    a1, _ = wavetrend(H, L, C, seed="first"); b1, _ = wavetrend(H, L, C, seed="sma")
    bad = [i for i, (x, y) in enumerate(zip(a1, b1)) if not (math.isnan(x) or math.isnan(y)) and abs(x - y) > 1e-3]
    SETTLE = (max(bad) + 1) if bad else 0
    print("seed-difference settles (<1e-3 WT pts) after bar", SETTLE)
    WARMUP = 200
    assert SETTLE < WARMUP, "WARMUP=200 bars must remove the seed choice"

    # 3. cross equality conventions differ only on ties
    t1 = [-5.0, -1.0, 0.0, 1.0, 1.0, 0.5]
    t2 = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    assert cross_events(t1, t2, "le") ==     [0, 0, 0, 1, 0, 0]   # tie at t2 skipped, first strict bar above fires once
    assert cross_events(t1, t2, "strict") == [0, 0, 0, 0, 0, 0]   # touch at t2 breaks the strict rule: no cross
    # touch-and-bounce on the same side is NOT a cross (above, tie, above)
    assert cross_events([1.0, 0.0, 1.0], [0.0, 0.0, 0.0], "le") == [0, 0, 0]
    # tie then move to the other side counts once
    assert cross_events([-1.0, 0.0, 1.0, 2.0], [0.0] * 4, "le") == [0, 0, 1, 0]
    # a sign flip with no tie is identical under both
    u1, u2 = [-1.0, 1.0, -1.0], [0.0, 0.0, 0.0]
    assert cross_events(u1, u2, "le") == cross_events(u1, u2, "strict") == [0, 1, -1]

    # 4. causality: planting a future spike must not change any earlier value or event
    H2, L2, C2 = list(H), list(L), list(C)
    H2[-1] *= 3; C2[-1] *= 2.5
    x1, x2 = wavetrend(H, L, C); y1, y2 = wavetrend(H2, L2, C2)
    assert x1[:-1] == y1[:-1] and x2[:-1] == y2[:-1]
    assert cross_events(x1, x2)[:-1] == cross_events(y1, y2)[:-1]

    # 5. NaN in the middle: the bar is NaN and ema state is dropped (no carry-forward / bridging).
    #    The reference re-seeds at once; the CONTRACT (not this file) additionally suppresses output for WARMUP=200 bars after a gap.
    Hn, Ln, Cn = list(H[:300]), list(L[:300]), list(C[:300])
    Hn[150] = Ln[150] = Cn[150] = NAN
    z1, z2 = wavetrend(Hn, Ln, Cn)
    assert math.isnan(z1[150]) and z1[149] == z1[149], "gap bar must be NaN; earlier bars untouched"
    assert z1[:150] == x1[:150], "bars before the gap must equal the gap-free run"
    assert all(math.isnan(v) for v in z2[150:153]), "wt2 (SMA 4) must be NaN for the 3 bars after the NaN bar"
    assert cross_events(z1, z2)[150] == 0 and cross_events(z1, z2)[151] == 0, "no event on or right after a NaN bar"
    print("OK")


if __name__ == "__main__":
    test_contract()
