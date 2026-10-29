"""Hand-built 12-day fixture for run_div (TOM-CTX-DIV). Expected values derived by hand from EXTRACT.md s4.

Mover closes (idx 0-11): 100,101,100,101,100,101,100,101,106,107,105,104
Basket A closes:         100 x8, 98, 97, 99, 99
Params: L=2, window=5 (trailing |R2| values), cut=0.8 (nearest rank: 4th smallest of 5), hold=1.
Hand derivation:
 - R2(t)=0 for t=2..7, so thr=0 at t=8; R2(8)=+0.06 > 0 -> mover top-quintile up, basket R2(8)=-0.02 <0: DIVERGENCE day D=8, dir=+1.
 - D=9: R2=+0.0594 > thr(0) and basket R2<0 -> second divergence day, but inside the same episode (D <= prior exit) -> skipped.
 - t=10: R2=-0.0094 <= thr(.0594) -> no event; t=11 likewise.
 - Trigger after D=8: t=9 basket 1d=97/98-1<0 (not toward dir) -> no; t=10 basket 1d=99/97-1>0 (toward dir),
   mover 105 <= max(106,107) (fails new extreme) -> ENTRY idx 10, short (fade). Exit idx 11: 104. Gross = -(104/105-1)=+0.0095238.
 - Control (a): no sign condition, trigger = mover 1d return against dir AND fails new extreme: t=9 mover 107>106 up, no;
   t=10 105/107-1<0 and 105<=107 -> entry idx 10 as well (D=8 same).
"""
import importlib.util
import pathlib

import pytest

spec = importlib.util.spec_from_file_location("run_div", pathlib.Path(__file__).parent / "run_div.py")
rd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd)

MOVER = [100, 101, 100, 101, 100, 101, 100, 101, 106, 107, 105, 104]
A = [100] * 8 + [98, 97, 99, 99]


def test_events_primary():
    ev = rd.find_events(MOVER, {"A": A}, {"A": 1}, L=2, window=5, cut=0.8, hold=1, mode="basket")
    assert ev == [(8, 10, 1)]


def test_events_control_no_sign_condition():
    # basket moving WITH the mover on day 8 would kill the primary event but not control (a)
    up = [100] * 8 + [102, 103, 104, 104]
    assert rd.find_events(MOVER, {"A": up}, {"A": 1}, L=2, window=5, cut=0.8, hold=1, mode="basket") == []
    ev = rd.find_events(MOVER, {"A": up}, {"A": 1}, L=2, window=5, cut=0.8, hold=1, mode="control")
    assert ev == [(8, 10, 1)]


def test_trade_return_short_fade_net_of_cost():
    r = rd.trade_returns(MOVER, [(8, 10, 1)], hold=1, cost=0.0004)
    assert r[0] == pytest.approx(-(104 / 105 - 1) - 0.0004)


def test_mirror_long_when_mover_down():
    m = [200 - x for x in MOVER]          # mirrored mover: falls on day 8
    a = [200 - x for x in A]              # basket mirrored: rises
    ev = rd.find_events(m, {"A": a}, {"A": 1}, L=2, window=5, cut=0.8, hold=1, mode="basket")
    assert ev == [(8, 10, -1)]
    assert rd.trade_returns(m, ev, hold=1, cost=0)[0] == pytest.approx(96 / 95 - 1)


def test_flip_member_sign():
    # DXY-style member with flip=-1: basket A falling is treated as rising -> same direction as mover up -> no event
    assert rd.find_events(MOVER, {"A": A}, {"A": -1}, L=2, window=5, cut=0.8, hold=1, mode="basket") == []


def test_asof_never_uses_bar_after_cutoff():
    dates = ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-06"]
    closes = [10, 11, 12, 13]
    # grid cutoff 2020-01-03 with lag 1 day -> 2020-01-02 value (11); cutoff 2020-01-05 (weekend) lag 0 -> 12
    assert rd.asof(dates, closes, ["2020-01-03", "2020-01-05", "2020-01-06"], lag_days=[1, 0, 1]) == [11, 12, 12]
    # before first bar -> None
    assert rd.asof(dates, closes, ["2019-12-31"], lag_days=[0]) == [None]


def test_no_exit_beyond_data():
    # entry on last index cannot exit -> event dropped
    ev = rd.find_events(MOVER, {"A": A}, {"A": 1}, L=2, window=5, cut=0.8, hold=2, mode="basket")
    assert ev == []   # entry idx 10 + hold 2 = 12 > last idx 11


def test_cluster_stats_hand_values():
    # two month clusters: [0.02, 0.02] and [-0.01]; mean=0.01 ; residuals .01,.01,-.02 ; cluster sums .02,-.02
    mean, se = rd.cluster_mean_se([0.02, 0.02, -0.01], ["2020-01", "2020-01", "2020-02"])
    assert mean == pytest.approx(0.01)
    assert se == pytest.approx((0.02 ** 2 + 0.02 ** 2) ** 0.5 / 3)
