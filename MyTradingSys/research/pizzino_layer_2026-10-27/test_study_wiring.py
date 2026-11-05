"""Wiring tests for study.py (hand-computed numbers). On the pre-change tree (no study.py) all fail at import."""
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import study as S  # noqa: E402


def _walk(n, seed=7):
    rnd, p, H, L = random.Random(seed), 100.0, [], []
    for _ in range(n):
        p += rnd.uniform(-2, 2)
        H.append(p + rnd.uniform(0, 1)); L.append(p - rnd.uniform(0, 1))
    return H, L


@pytest.mark.parametrize("n", [1, 2, 3, 5])
def test_incremental_pivots_equal_pivots_known(n):
    H, L = _walk(300)
    inc = S.Pivots(H, L, n)
    for i in range(len(H)):
        assert list(inc.at(i)) == S.pz.pivots_known(H, L, n, i)


def _bars(rows):
    return [dict(t=k * S.DAY, o=o, h=h, l=l, c=c) for k, (o, h, l, c) in enumerate(rows)]


PRM = dict(S.DEFAULT, TS=3)


def test_target_hit_gross_and_cost():
    # entry 100 at bar 1 open, stop 95 (risk 5), target 110: bar 2 reaches 111 -> exit 110, gross 10/5 = 2.0
    b = _bars([(99, 100, 98, 99), (100, 105, 97, 104), (104, 111, 103, 108), (108, 109, 107, 108), (108, 108, 108, 108)])
    t = S.simulate(b, [(0, "long", 1, 95.0, 110.0)], PRM)[0]
    assert t["why"] == "target" and t["gross_R"] == pytest.approx(2.0)
    assert t["cost_R"] == pytest.approx(0.0014 * 100 / 5)       # 0.028
    assert t["net_R"] == pytest.approx(2.0 - 0.028)


def test_stop_wins_same_bar_and_gap_through_stop():
    b = _bars([(99, 100, 98, 99), (100, 112, 94, 100), (100, 100, 100, 100), (100, 100, 100, 100), (100, 100, 100, 100)])
    assert S.simulate(b, [(0, "long", 1, 95.0, 110.0)], PRM)[0]["gross_R"] == pytest.approx(-1.0)
    g = _bars([(99, 100, 98, 99), (100, 101, 99, 100), (94, 95, 93, 94), (94, 94, 94, 94), (94, 94, 94, 94)])
    t = S.simulate(g, [(0, "long", 1, 95.0, 110.0)], PRM)[0]
    assert t["why"] == "stop_gap" and t["gross_R"] == pytest.approx((94 - 100) / 5)   # -1.2


def test_time_stop_short_and_open_end_dropped():
    # short entry 100, stop 105, target 90; nothing touches; TS = 3 -> exit at bar 4 open 98: gross (100-98)/5 = 0.4
    b = _bars([(101, 102, 100, 101), (100, 101, 99, 100), (99, 100, 98, 99), (99, 100, 98, 98), (98, 99, 97, 98)])
    t = S.simulate(b, [(0, "short", 1, 105.0, 90.0)], PRM)[0]
    assert t["why"] == "time" and t["gross_R"] == pytest.approx(0.4)
    assert S.simulate(b[:4], [(0, "short", 1, 105.0, 90.0)], PRM) == []
