"""Synthetic-bar tests for shape_b_census.py (no F:/ dependency). Each test fails on a stub of the function it covers."""
import math
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shape_b_census as sb  # noqa: E402

M15 = 900000
T0 = sb.DEV_START_MS


def mkP(O, H, L, C, w1=None, tr2=None):
    n = len(C)
    return dict(n=n, O=O, H=H, L=L, C=C, w1=w1 or [-60.0] * n, tr2=tr2 or [1] * n, T=[T0 + k * M15 for k in range(n)])


def flat(n, px=100.0):
    return [px] * n


def test_block_of_boundaries():
    d = 86400000
    assert sb.block_of(T0 + 6 * 3600000 + 45 * 60000) == "asia"
    assert sb.block_of(T0 + 7 * 3600000) == "london"
    assert sb.block_of(T0 + 13 * 3600000) == "ny"
    assert sb.block_of(T0 + 21 * 3600000) == "late"
    assert sb.block_of(T0 + d - 1) == "late"


def test_agg_k_drops_incomplete_and_aggregates():
    b = [dict(t=T0 + k * M15, o=k, h=10 + k, l=k, c=k + 0.5) for k in range(10)]   # T0 is 4h aligned
    out = sb.agg_k(b, 8)
    assert len(out) == 1 and out[0]["o"] == 0 and out[0]["h"] == 17 and out[0]["l"] == 0 and out[0]["c"] == 7.5


def test_last_closed_has_no_lookahead():
    b4 = [dict(t=T0, o=1, h=1, l=1, c=1)]
    b15 = [dict(t=T0 + k * M15) for k in range(20)]
    j = sb._last_closed(b4, 4 * 3600000, b15)
    assert j[14] == -1          # bar 14 closes at T0+3h45m: the 4h bar is still open
    assert j[15] == 0           # bar 15 closes at T0+4h: now closed
    assert all(x == 0 for x in j[15:])


def test_maker_fill_needs_trade_through_within_three_bars():
    C = [100.0, 101, 101, 101, 99]
    L = [100.0, 100.5, 100.2, 100.0, 99.0]   # bar 3 touches exactly (no fill); bar 4 would fill but is the 4th bar
    P = mkP(C, C, L, C)
    assert sb.maker_fill(P, 0) is None
    L[2] = 99.9
    assert sb.maker_fill(P, 0) == 2


def test_maker_fill_ignores_signal_bar():
    C = [100.0] * 6
    L = [90.0, 100.0, 100.0, 100.0, 99.0, 99.0]   # low on the signal bar itself must not count
    assert sb.maker_fill(mkP(C, C, L, C), 0) is None


def test_arm_a_stop_first_even_when_exit_signal_on_same_bar():
    n = 8
    L = [100.0] * n
    L[2] = 94.0
    w1 = [-60.0] * n
    w1[2] = 5.0
    r = sb.arm_a(mkP(flat(n), flat(n), L, flat(n), w1=w1), 0, 1, 95.0, "D")
    assert r["kind"] == "stop" and r["k"] == 2
    assert r["gross"] == pytest.approx(-0.05)


def test_arm_a_x1_exit_at_next_open_and_cost_from_fees():
    n = 8
    O = [100, 100, 100, 100, 103, 103, 103, 103]
    w1 = [-60.0] * n
    w1[3] = 1.0           # first closed bar with wt1 > 0 -> exit at open of bar 4
    P = mkP(O, flat(n), flat(n), flat(n), w1=w1)
    r = sb.arm_a(P, 0, 1, 95.0, "D")
    assert r["kind"] == "timeout" and r["k"] == 4
    assert r["gross"] == pytest.approx(0.03)
    exp = 0.03 - (sb.fees.FEES_DERIBIT["entry"] + sb.fees.FEES_DERIBIT["timeout"] + sb.fees.SLIPPAGE_RT_S13)
    assert r["net"] == pytest.approx(exp)
    assert r["net_r"] == pytest.approx(exp / 0.05)
    rt = sb.arm_a(P, 0, 1, 95.0, "T")
    assert rt["net"] < r["net"]    # taker entry costs more than the maker entry


def test_arm_a_trend_turn_exits():
    n = 8
    tr = [1] * n
    tr[2] = -1
    r = sb.arm_a(mkP(flat(n), flat(n), flat(n), flat(n), tr2=tr), 0, 1, 95.0, "D")
    assert r["k"] == 3 and r["kind"] == "timeout"


def test_arm_a_stop_gap_fills_at_open():
    n = 6
    O = [100, 100, 90, 90, 90, 90]
    L = [100, 100, 89, 89, 89, 89]
    r = sb.arm_a(mkP(O, flat(n), L, flat(n)), 0, 1, 95.0, "D")
    assert r["gross"] == pytest.approx(-0.10)


def test_arm_b_skip_when_vah_under_1p5r():
    n = 6
    P = mkP(flat(n), flat(n), flat(n), flat(n))
    assert sb.arm_b(P, 0, 1, 95.0, 107.0, "D") is None      # risk 5, VAH 7 away = 1.4 R
    assert sb.arm_b(P, 0, 1, 95.0, None, "D") is None
    assert sb.arm_b(P, 0, 1, 95.0, 107.6, "D") is not None  # 1.52 R


def test_arm_b_target_hit_is_maker_exit_cost():
    n = 6
    H = [100, 100, 108, 100, 100, 100]
    r = sb.arm_b(mkP(flat(n), H, flat(n), flat(n)), 0, 1, 95.0, 108.0, "D")
    assert r["kind"] == "target" and r["gross"] == pytest.approx(0.08)
    exp = 0.08 - (sb.fees.FEES_DERIBIT["entry"] + sb.fees.FEES_DERIBIT["target"] + sb.fees.SLIPPAGE_RT_S13)
    assert r["net"] == pytest.approx(exp)


def test_arm_b_breakeven_after_1r_then_stop_at_entry():
    n = 8
    H = [100, 100, 106, 100, 100, 100, 100, 100]    # +1R (risk 5) reached on bar 2
    L = [100, 100, 100, 99.0, 100, 100, 100, 100]   # bar 3 trades back through entry 100
    r = sb.arm_b(mkP(flat(n), H, L, flat(n)), 0, 1, 95.0, 120.0, "D")
    assert r["kind"] == "stop" and r["k"] == 3 and r["gross"] == pytest.approx(0.0)


def test_arm_b_be_not_effective_on_same_bar_stop_first():
    n = 6
    H = [100, 100, 106, 100, 100, 100]
    L = [100, 100, 94.0, 100, 100, 100]   # high reaches +1R and low breaks the ORIGINAL stop on one bar -> stop at 95
    r = sb.arm_b(mkP(flat(n), H, L, flat(n)), 0, 1, 95.0, 120.0, "D")
    assert r["kind"] == "stop" and r["gross"] == pytest.approx(-0.05)


def test_arm_b_same_bar_stop_and_target_stop_first():
    n = 6
    H = [100, 100, 120, 100, 100, 100]
    L = [100, 100, 94.0, 100, 100, 100]
    r = sb.arm_b(mkP(flat(n), H, L, flat(n)), 0, 1, 95.0, 120.0, "D")
    assert r["kind"] == "stop"


def test_below_size_rule_flag():
    n = 6
    H = [100, 100, 100.9, 100, 100, 100]
    r = sb.arm_b(mkP(flat(n), H, flat(n), flat(n)), 0, 1, 99.7, 100.9, "D")   # stop 30 bp
    assert r is not None and r["below_rule"] is True
    r2 = sb.arm_b(mkP(flat(n), [100, 100, 108, 100, 100, 100], flat(n), flat(n)), 0, 1, 95.0, 108.0, "D")
    assert r2["below_rule"] is False


def test_stop_for_is_lower_of_pivot_low_and_val():
    L = [100.0] * 20
    L[15] = 97.0
    P = mkP(flat(20), flat(20), L, flat(20))
    assert sb.stop_for(P, 19, {"VAL": 98.0}) == 97.0
    assert sb.stop_for(P, 19, {"VAL": 96.0}) == 96.0
    L2 = [100.0] * 20
    L2[5] = 90.0                       # older than 8 bars: not the second pivot
    assert sb.stop_for(mkP(flat(20), flat(20), L2, flat(20)), 19, {"VAL": 99.0}) == 99.0


def test_holm_and_p_value():
    assert sb.holm([0.01, 0.04]) == [pytest.approx(0.02), pytest.approx(0.04)]
    assert sb.holm([0.04, 0.03]) == [pytest.approx(0.06), pytest.approx(0.06)]
    assert sb.p_one_sided([1.0, 1.1, 0.9, 1.0, 1.05, 0.95]) < 0.001
    assert sb.p_one_sided([-1.0, -1.1, -0.9, -1.0]) > 0.99


def test_stage_counts_are_cumulative():
    evs = [dict(reach=1), dict(reach=3), dict(reach=6)]
    assert sb.stage_counts(evs) == [3, 2, 2, 1, 1, 1]


def test_scan_stages_and_window(monkeypatch):
    n = 130
    C = [100.0] * n
    L = [100.0] * n
    L[106] = 99.0
    P = mkP(C, C, L, C)
    P["T"] = [sb.DEV_START_MS - 50 * M15 + k * M15 for k in range(n)]    # first 50 bars are before DEV
    trig = {20, 60, 105, 110}
    monkeypatch.setattr(sb, "trigger", lambda P_, i: i in trig)
    monkeypatch.setattr(sb, "gates", lambda P_, i: (4 if i == 105 else 1, dict(adx_state="x", phase="p", block="ny"), {"VAL": 1, "POC": 2}))
    evs = sb.scan(P)
    assert [e["i"] for e in evs] == [105, 110]            # bar 60 is before the DEV start; bar 20 is below the 100-bar warm-up
    assert [e["reach"] for e in evs] == [6, 2]
    assert sb.stage_counts(evs)[-1] == 1


def _bars(n, seed=3, start=T0 - 5 * 86400000):
    rng, px, out = random.Random(seed), 20000.0, []
    for k in range(n):
        o = px
        c = o * (1 + rng.uniform(-0.004, 0.004))
        out.append(dict(t=start + k * M15, o=o, h=max(o, c) * 1.001, l=min(o, c) * 0.999, c=c, v=10.0, delta=0.0))
        px = c
    return out


def test_prepare_has_no_lookahead_in_any_array():
    full = _bars(900)
    Pf = sb.prepare(full, lambda t: "BULL")
    for m in (400, 650):
        Pp = sb.prepare(full[:m], lambda t: "BULL")
        for i in range(120, m - 20, 7):
            for key in ("w1", "R", "tr2"):
                assert Pf[key][i] == pytest.approx(Pp[key][i]), (key, m, i)
            jf, jp = Pf["j4"][i], Pp["j4"][i]
            assert jf == jp
            if jf >= 0 and Pf["adx"][jf] is not None:
                assert Pf["adx"][jf] == pytest.approx(Pp["adx"][jp])
            assert sb.trigger(Pf, i) == sb.trigger(Pp, i)


def test_prepare_refuses_sealed_window():
    bad = _bars(50, start=sb.DEV_END_MS - 10 * M15)
    with pytest.raises(AssertionError):
        sb.prepare(bad, lambda t: "BULL")


def test_random_control_deterministic_and_seeded():
    n = 200
    P = mkP(flat(n), flat(n), [99.5] * n, flat(n))
    P["T"] = [sb.DEV_START_MS + k * M15 for k in range(n)]
    P["_lv"] = {sb.ax.day_of(t): {"VAL": 99.0, "VAH": 110.0} for t in P["T"]}
    P["w1"] = [-60.0] * 100 + [1.0] * 100
    a = sb.random_control(P, list(range(100, 150)), 10, "A", draws=5, seed=1111)
    b = sb.random_control(P, list(range(100, 150)), 10, "A", draws=5, seed=1111)
    c = sb.random_control(P, list(range(100, 150)), 10, "A", draws=5, seed=7)
    assert a == b and len(a) == 5 and all(math.isfinite(x) for x in a)
    assert c is not None


def test_verdict_words():
    def r(x):
        return dict(net_r=x, net=x * 0.01)
    tk = [r(1.0), r(1.2), r(0.9), r(1.1)]
    good = dict(maker=[r(1.0), r(1.1), r(0.9)] * 14, taker=tk, ctrl=[0.0] * 30, skip_maker=0, skip_taker=0)
    ev = dict(A=good, B=good, alone=[0.0, 0.001, -0.001, 0.0], holm=dict(p=[0.001, 0.001], adj=[0.002, 0.002]))
    assert sb.verdict(ev)[0] == "PASS-CANDIDATE"
    ev2 = dict(ev, A=dict(good, maker=[r(-0.1), r(-0.2), r(0.0)] * 14))
    assert sb.verdict(ev2)[0] == "FAIL"
    ev3 = dict(ev, holm=dict(p=[0.3, 0.3], adj=[0.6, 0.6]))
    assert sb.verdict(ev3)[0] == "INCONCLUSIVE"
    ev4 = dict(ev, A=dict(good, ctrl=[5.0] * 30))
    assert sb.verdict(ev4)[0] == "FAIL"
