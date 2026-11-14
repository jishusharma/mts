"""Tests for M3: limit at signal-bar close; no fill on touch; only bars after the signal bar; orig signals unchanged."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import study, maker_fill as MF

BAR = study.BAR


def m1(lows, highs, t0, closes=None):
    n = len(lows); t = t0 + np.arange(n) * 60000.0
    c = np.array(closes if closes is not None else [(a + b) / 2 for a, b in zip(lows, highs)], float)
    return dict(t_ms=t, o=c.copy(), h=np.array(highs, float), l=np.array(lows, float), c=c)


def make(sig_low_through=False, touch_only=False, tsig=0.0):
    # signal bar (1 x 15m) occupies [tsig, tsig+BAR); order placed at tsig+BAR. Include 1m bars INSIDE the signal bar that
    # dip through L=100 (a naive variant that uses the signal bar itself would fill there).
    n_in, n_after = 15, 40
    lows = [99.0] * n_in + [100.0 if touch_only else 99.9] * 3 + [100.0] * (n_after - 3)
    highs = [101.0] * (n_in + n_after)
    return m1(lows, highs, tsig)


def test_no_fill_on_touch():
    m = make(touch_only=True)
    r = study.run_signal(0.0, 100.0, 0.2, 1, m, tick=0.1)   # S=max(0.2,0.5)=0.5
    assert not r["filled"] and r["reason_missed"] == "no_through"


def test_fill_needs_one_tick_through_and_fills_at_L():
    m = make()
    r = study.run_signal(0.0, 100.0, 0.2, 1, m, tick=0.1)
    assert r["filled"] and r["entry_px"] == 100.0           # never better than L
    assert r["fill_ms"] >= BAR                               # not inside the signal bar (which dips to 99 from minute 0)


def test_signal_bar_itself_not_used():
    """A naive variant that searched from the signal bar open would fill at minute 0; the real one cannot."""
    m = make(touch_only=True)    # after the signal bar there is only a touch; inside the signal bar low=99 through L
    r = study.run_signal(0.0, 100.0, 0.2, 1, m, tick=0.1)
    assert not r["filled"]
    naive = MF.simulate_maker(1, 100.0, 99.5, 101.0, 0.0, BAR, 24 * BAR, False, m, tick=0.1)   # signal_close_ms = bar open (bug)
    assert naive["filled"]       # proves the test discriminates


def test_limit_level_is_signal_close_and_stop_target():
    L, stop, tgt = study.level_and_levels(100.0, 0.2, 1)
    assert L == 100.0 and abs(stop - 99.5) < 1e-12 and abs(tgt - 101.0) < 1e-12   # S floor 0.5% of L
    L, stop, tgt = study.level_and_levels(100.0, 2.0, -1)
    assert abs(stop - 102.0) < 1e-12 and abs(tgt - 96.0) < 1e-12


def test_order_expires_after_one_bar():
    lows = [100.0] * 15 + [100.0] * 15 + [99.0] * 20   # through L only in the 2nd bar after the signal
    m = m1(lows, [101.0] * 50, 0.0)
    r = study.run_signal(0.0, 100.0, 0.2, 1, m, tick=0.1)
    assert not r["filled"]


def test_original_baseline_signals_unchanged():
    import orig_study as O
    assert O.K == 4 and O.HOLD == 24 and O.TGT_R == 2.0
