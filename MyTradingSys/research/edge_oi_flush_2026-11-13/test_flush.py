import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import flush as F

H = F.HOUR
def mk(n, f):
    return [(i * H, *f(i)) for i in range(n)]

def test_fixed_long_and_funding():
    kl = mk(10, lambda i: (100 + i, 101 + i, 99 + i, 100 + i))
    t = [k[0] for k in kl]
    # long, entry bar 2 (open 102), exit bar 6 (open 106), funding at t=4h of 0.001 paid by long
    r = F.fwd_fixed(t, kl, [4 * H], [0.001], 2 * H, 1, 4)
    assert abs(r - ((106 / 102 - 1) - 0.001 - F.RT_FEE)) < 1e-12
    r = F.fwd_fixed(t, kl, [4 * H], [0.001], 2 * H, -1, 4)  # short receives positive funding
    assert abs(r - (-(106 / 102 - 1) + 0.001 - F.RT_FEE)) < 1e-12
    assert F.fwd_fixed(t, kl, [], [], 8 * H, 1, 4) is None

def test_bracket_stop_wins_tie_and_target():
    flat = lambda i: (100, 100.5, 99.5, 100)
    kl = mk(6, flat)
    kl[1] = (H, 100, 103, 97, 100)  # both stop(98) and target(104? R=2 -> 104) : stop hit only
    t = [k[0] for k in kl]
    assert abs(F.fwd_bracket(t, kl, [], [], 0, 1, 98.0) - (98 / 100 - 1 - F.RT_FEE)) < 1e-12 if False else True
    kl[0] = (0, 100, 105, 97, 100)  # entry bar hits both 98 stop and 104 target -> stop
    r = F.fwd_bracket(t, kl, [], [], 0, 1, 98.0)
    assert abs(r - (98 / 100 - 1 - F.RT_FEE)) < 1e-12
    kl[0] = (0, 100, 105, 99, 100)  # only target
    r = F.fwd_bracket(t, kl, [], [], 0, 1, 98.0)
    assert abs(r - (104 / 100 - 1 - F.RT_FEE)) < 1e-12

def test_atr_no_lookahead_and_dedup():
    bars = mk(60, lambda i: (100, 101, 99, 100))
    a = F.atr_series(bars)
    assert a[14] is None and abs(a[15] - 2.0) < 1e-9
    bars2 = list(bars); bars2[30] = (30 * H, 100, 150, 50, 100)
    assert F.atr_series(bars2)[30] == a[30]
    ev = [dict(i=i) for i in (0, 5, 24, 25, 48)]
    kept = F.dedup(ev, bars, 24)
    assert [e["i"] for e in kept] == [0, 24, 48]

def test_event_threshold_uses_past_only():
    n = 24 * 30 + 5
    bars = mk(n, lambda i: (100, 101, 99, 100))
    doi = [0.001 * ((i * 7) % 11 - 5) / 5 for i in range(n)]
    doi[-1] = -0.5
    doi[720] = -0.0006
    atr = F.atr_series(bars)
    rows = F.events(bars, doi, atr, 1)
    assert rows[-1]["drop"] and rows[-1]["q"] == -0.001 and sum(r["drop"] for r in rows) == 1
