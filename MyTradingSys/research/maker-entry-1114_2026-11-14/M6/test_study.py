"""Tests for M6 study.py (synthetic 1m bars, hand-computed expectations). Each 'naive_*' variant is the wrong behaviour the
tests are designed to catch: the tests assert the study differs from it, so they fail on a naive implementation."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study as S
import maker_fill as MF

M1 = 60000
TICK = 0.01


def mk_m1(n=1440, px=100.0):
    t = np.arange(n) * M1
    return dict(t_ms=t.astype(float), o=np.full(n, px), h=np.full(n, px + 0.05), l=np.full(n, px - 0.05), c=np.full(n, px))


# event: reclaim bar j = 170 (5m slot) -> signal close = slot 171 start = minute 855. Day starts t0=0, d0=0.
EV = dict(i0=168, j=170, S=98.0, EL=99.0, EH=101.0)
SIG_MIN = (170 + 1) * 5            # first 1m bar after the signal bar


def run(m1, ev=EV, **kw):
    return S.maker_trade(ev, 0, 0, m1, TICK, **kw)


def naive_touch_and_signal_bar(m1, ev=EV):
    """WRONG: fills on touch (tick=0) and reads the signal bar itself (starts one 5m bar early)."""
    return MF.simulate_maker(1, ev["EL"], ev["S"], ev["EH"], (ev["j"]) * S.M5, 2 * S.M5, S.US1 * S.M5, False, m1, tick=0.0)


def test_touch_is_not_a_fill():
    m1 = mk_m1()
    m1["l"][SIG_MIN + 1] = 99.0                       # touches L exactly
    assert run(m1)["filled"] is False
    assert naive_touch_and_signal_bar(m1)["filled"] is True          # naive would fill -> test discriminates


def test_signal_bar_itself_never_fills():
    m1 = mk_m1()
    m1["l"][SIG_MIN - 3] = 98.5                        # dip through L inside the signal bar (before it closed)
    assert run(m1)["filled"] is False
    assert naive_touch_and_signal_bar(m1)["filled"] is True


def test_fill_at_L_never_better_even_on_gap_through():
    m1 = mk_m1()
    m1["o"][SIG_MIN + 1] = 98.6; m1["l"][SIG_MIN + 1] = 98.5; m1["h"][SIG_MIN + 1] = 98.7; m1["c"][SIG_MIN + 1] = 98.6
    m1["h"][SIG_MIN + 2:] = 98.9; m1["l"][SIG_MIN + 2:] = 98.6; m1["o"][SIG_MIN + 2:] = 98.7; m1["c"][SIG_MIN + 2:] = 98.7
    r = run(m1)
    assert r["filled"] and r["entry_px"] == 99.0       # filled at L, not at the better 98.6 open


def test_order_life_is_one_5m_bar_and_60m_variant_fills_later():
    m1 = mk_m1()
    m1["l"][SIG_MIN + 7] = 98.9                        # through L but 7 minutes after the signal bar closed
    assert run(m1)["filled"] is False
    assert run(m1, life_ms=12 * S.M5)["filled"] is True


def test_stop_level_trade_is_fill_and_stop_same_bar_not_a_cancel():
    # a long stop sits below L, so any bar touching the stop also trades through L: PRE_REG says the fill bar may stop out (stop wins)
    m1 = mk_m1()
    m1["l"][SIG_MIN] = 97.9
    m1["l"][SIG_MIN + 2] = 98.9
    r = run(m1)
    assert r["filled"] and r["exit_type"] == "stop" and r["gross_R"] < -0.999


def test_target_exit_maker_fees_and_R():
    m1 = mk_m1()
    m1["l"][SIG_MIN + 1] = 98.9                        # fill at 99.0
    m1["h"][SIG_MIN + 30] = 101.02                     # target 101.0 needs +1 tick -> 101.01
    r = run(m1)
    assert r["filled"] and r["exit_type"] == "target"
    risk = 1.0
    assert abs(r["gross_R"] - 2.0 / risk) < 1e-12
    assert abs(r["fee_R"] - (0.0003 + 0.0003) * 99.0 / risk) < 1e-12
    m1["h"][SIG_MIN + 30] = 101.00                     # touch only: no target
    assert run(m1)["exit_type"] == "time"


def test_stop_exit_taker_fee_and_same_bar_fill_stop():
    m1 = mk_m1()
    m1["l"][SIG_MIN + 1] = 97.5                        # one bar: fills through L and runs the stop (stop wins)
    r = run(m1)
    assert r["filled"] and r["exit_type"] == "stop"
    assert abs(r["gross_R"] + 1.0) < 1e-12
    assert abs(r["fee_R"] - (0.0003 + 0.0006) * 99.0 / 1.0) < 1e-12


def test_min_risk_miss():
    m1 = mk_m1()
    ev = dict(EV, S=98.9)                              # (99-98.9)/99 = 0.10 % < 0.15 %
    assert run(m1, ev)["reason_missed"] == "min_risk"


def test_find_event_and_original_taker_baseline():
    n = 288
    o = np.full(n, 100.0); h = np.full(n, 100.1); l = np.full(n, 99.9); c = np.full(n, 100.0)
    l[100] = 99.0; h[120] = 101.0
    l[170] = 98.5; c[170] = 98.8
    l[171] = 98.7; c[171] = 98.9
    c[172] = 99.2; l[172] = 98.9
    o[173] = 99.3
    EL, EH = S.day_levels(h, l, 0)
    ev = S.find_event_long(o, h, l, c, 0, EL, EH)
    assert (ev["i0"], ev["j"], ev["S"]) == (170, 172, 98.5)
    h[180] = 101.0                                     # entry 99.3, stop 98.5, risk 0.8, target EH 101.0 -> +1.7/0.8 R
    tk = S.taker_baseline(ev, o, h, l, c, 0)
    gross = (101.0 - 99.3) / 0.8
    assert abs(tk["gross_R"] - gross) < 1e-12
    assert abs(tk["net_R"] - (gross - 0.0006 * (99.3 + 101.0) / 0.8)) < 1e-12


def test_agg5_aligned_and_ohlc():
    m1 = mk_m1(1440)
    m1["h"][7] = 105.0; m1["l"][2] = 95.0; m1["c"][4] = 101.0; m1["o"][0] = 99.5
    t0, o, h, l, c = S.agg5(m1, 0)
    assert t0 == 0 and o[0] == 99.5 and l[0] == 95.0 and c[0] == 101.0 and h[1] == 105.0
