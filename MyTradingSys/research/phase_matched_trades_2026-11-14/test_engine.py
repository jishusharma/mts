import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import engine as E

DAY, H1 = E.DAY, E.H1
LAG = int(os.environ.get("PHASE_LAG", "1"))   # PHASE_LAG=0 is the deliberately wrong (look-ahead) version


def _daily_trend(n=80, step=1.0):
    dt = np.arange(n, dtype=np.int64) * DAY
    c = 100 + np.arange(n) * step
    return dt, c + 0.5, c - 0.5, c


def test_phase_up_in_clean_uptrend_and_down_mirror():
    dt, h, l, c = _daily_trend()
    assert E.daily_phase(h, l, c)[-1] == E.UP
    assert E.daily_phase(1000 - l, 1000 - h, 1000 - c)[-1] == E.DOWN


def test_phase_range_when_flat():
    c = 100 + 0.5 * (-1.0) ** np.arange(120)
    assert E.daily_phase(c + 0.3, c - 0.3, c)[-1] == E.RANGE


def test_phase_decided_with_previous_day_only():
    """Day 60 closes with a huge crash (would flip the label). Every 1h bar of day 60 must carry day 59's label."""
    dt, h, l, c = _daily_trend(61)
    c = c.copy(); h = h.copy(); l = l.copy()
    c[60] = 20.0; l[60] = 19.0
    lab = E.daily_phase(h, l, c)
    assert lab[59] == E.UP and lab[60] != E.UP
    bars = dt[60] + np.arange(24) * H1
    got = E.bar_phase(bars, dt, lab, lag=LAG)
    assert (got == lab[59]).all(), got


def test_adx_pure_uptrend():
    dt, h, l, c = _daily_trend(60)
    adx, p, m = E.adx_di(h, l, c)
    assert abs(m[-1]) < 1e-9 and p[-1] > 0 and abs(adx[-1] - 100) < 1e-6


def test_simulate_stop_first_and_target():
    o = np.array([10, 10, 10, 10.0]); h = np.array([10, 10.5, 11.5, 10]); l = np.array([10, 9.5, 9.0, 10]); c = np.array([10, 10, 10, 10.0])
    r = E.simulate(o, h, l, c, 0, -1, 11.0, "R", 2.0, 3)   # entry 10, stop 11, target 8; bar2 high hits stop
    assert r[0] == 2 and r[1] == 11.0
    l2 = l.copy(); l2[1] = 7.5
    r = E.simulate(o, h, l2, c, 0, -1, 11.0, "R", 2.0, 3)
    assert r[0] == 1 and r[1] == 8.0
    both = E.simulate(o, np.array([10, 11.5, 10, 10.0]), np.array([10, 7.0, 10, 10.0]), c, 0, -1, 11.0, "R", 2.0, 3)
    assert both[1] == 11.0   # stop and target in one bar: stop first


def test_net_r_costs():
    pct, R = E.net_r(-1, 100.0, 98.0, 101.0, 0.0)
    assert abs(pct - (0.02 - 0.0012)) < 1e-12 and abs(R - pct / 0.01) < 1e-9


def test_funding_sign_short_receives():
    ft = np.array([100, 200, 300], np.int64)
    cf = np.concatenate(([0.0], np.cumsum([0.001, 0.001, 0.001])))
    f = E.funding_between(ft, cf, 100, 300)   # settlements 200 and 300 only
    assert abs(f - 0.002) < 1e-12
    pct, _ = E.net_r(-1, 100.0, 100.0, 101.0, f)
    assert pct > -E.COST   # short receives funding
