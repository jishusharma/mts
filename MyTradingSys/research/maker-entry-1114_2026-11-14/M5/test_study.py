import sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import study as st            # noqa: E402
import maker_fill as mf       # noqa: E402


def m1_from(rows, t0=0):
    a = np.array(rows, float)   # o,h,l,c
    t = t0 + 60_000 * np.arange(len(a))
    return dict(t_ms=t, o=a[:, 0], h=a[:, 1], l=a[:, 2], c=a[:, 3])


def mkev():
    # short; VAH=101, VAL=99, POC=99.5; session high through signal bar 101.5 -> stop 101.5*1.0001
    H = np.array([101.5, 100.5, 100.8, 100, 100, 100, 100, 100.0])
    C = np.array([100.5, 100.2, 100.0, 100, 100, 100, 100, 100.0])
    return dict(side=-1, vah=101.0, val=99.0, poc=99.5, H=H, L=C - 0.1, C=C)


def test_limit_is_value_edge_not_close():
    ev = mkev()
    assert st.limit_level(ev) == 101.0
    assert st.limit_level(dict(ev, side=1)) == 99.0


def test_signal_bar_not_used_and_touch_not_fill():
    ev = mkev()
    tick = 0.01
    # bar 2 is the signal bar: its high pierces VAH+tick -- must NOT count; later bars only touch 101.0 exactly.
    rows = [(100, 101.5, 100, 100.5)] * 2 + [(100.5, 101.2, 100.0, 100.0)] + [(100, 101.0, 99.9, 100.0)] * 5
    m1 = m1_from(rows)
    r = st.maker_signal(ev, 2, int(m1["t_ms"][2]), m1, tick, int(m1["t_ms"][-1]) + 60_000)
    assert not r["filled"]
    # the naive variant that starts at the signal bar itself WOULD fill, so this test discriminates
    naive = mf.simulate_maker(-1, 101.0, 101.5 * 1.0001, 99.5, int(m1["t_ms"][2]), st.TF_MS,
                              int(m1["t_ms"][-1]) + 60_000, False, m1, tick=tick)
    assert naive["filled"]


def test_fills_at_limit_one_tick_through_and_fee_by_exit():
    ev = mkev()
    tick = 0.01
    rows = [(100, 101.5, 100, 100.5)] * 2 + [(100.5, 100.9, 100.0, 100.0)] + [(100, 101.01, 99.9, 100.0)] + \
           [(100.0, 100.0, 99.4, 99.6)] + [(99.6, 99.7, 99.5, 99.6)] * 3
    m1 = m1_from(rows)
    r = st.maker_signal(ev, 2, int(m1["t_ms"][2]), m1, tick, int(m1["t_ms"][-1]) + 60_000)
    assert r["filled"] and r["entry_px"] == 101.0 and r["exit_type"] == "target"
    risk = 101.5 * 1.0001 - 101.0
    assert abs(r["fee_R"] - (0.0003 + 0.0003) * 101.0 / risk) < 1e-9     # maker entry + maker target
    assert r["gross_R"] > 0
