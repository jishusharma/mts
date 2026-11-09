"""Spec tests for study.py, written from the module docstring and PRE_REG.md (contract), not from the code body.

Expected numbers are computed here independently (numpy / hand arithmetic). Every threshold is OURS per PRE_REG.md.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study as st  # noqa: E402


def test_contract_constants():
    # PRE_REG: |z|>=3, trailing 30 days, flat < 0.2 %, band 10 %, THIN n<30, horizons 1h/4h/24h in 5m bars
    assert st.Z_BIG == 3.0 and st.TRAIL_DAYS == 30 and st.TT_FLAT == 0.002 and st.BAND == 0.10 and st.THIN == 30
    assert dict(st.HORIZONS) == {'1h': 12, '4h': 48, '24h': 288}


def test_tt_class_flat_band_is_strict_and_symmetric():
    # |change| < 0.2 % = FLAT; exactly 0.2 % is NOT flat
    assert st.tt_class(0.00199, 0.05) == 'FLAT' and st.tt_class(0.05, -0.00199) == 'FLAT'
    assert st.tt_class(0.002, 0.002) == 'BU'
    assert st.tt_class(-0.002, -0.002) == 'BD'
    assert st.tt_class(0.01, -0.01) == 'SL' and st.tt_class(-0.01, 0.01) == 'SS'


def test_wilson_95_matches_hand_values():
    lo, hi = st.wilson(5, 10)                      # textbook Wilson 95 %: 0.2366 .. 0.7634
    assert abs(lo - 0.2366) < 5e-4 and abs(hi - 0.7634) < 5e-4
    assert st.wilson(0, 0) == (0.0, 0.0)
    lo, hi = st.wilson(10, 10)
    assert hi == 1.0 and abs(lo - 0.7225) < 5e-4
    lo, hi = st.wilson(0, 10)
    assert lo == 0.0 and abs(hi - 0.2775) < 5e-4


def test_trailing_z_uses_prior_bars_only_and_needs_80_percent():
    rng = np.random.default_rng(7)
    x = rng.normal(size=60)
    w = 20
    z = st.trailing_z(x, w)
    assert np.all(np.isnan(z[:w]))
    i = 40
    prior = x[i - w:i]                              # excludes x[i] itself
    assert abs(z[i] - (x[i] - prior.mean()) / prior.std()) < 1e-9
    x2 = x.copy()
    x2[i + 1:] += 100.0                             # future bars must not move z[i]
    assert abs(st.trailing_z(x2, w)[i] - z[i]) < 1e-12
    x3 = x.copy()
    x3[i - w:i - w + 5] = np.nan                    # 15/20 = 75 % valid < 80 % -> NaN
    assert np.isnan(st.trailing_z(x3, w)[i])
    x4 = x.copy()
    x4[i - w:i - w + 4] = np.nan                    # 16/20 = 80 % valid -> defined
    assert np.isfinite(st.trailing_z(x4, w)[i])


def _S(c):
    c = np.asarray(c, float)
    return {'c': c, 'n': len(c)}


def test_outcomes_continue_and_undone_by_direction():
    n = 300
    c = np.full(n, 100.0)
    c[10] = 110.0                                   # event close
    c[22] = 120.0                                   # +1h: beyond event close (up)
    c[58] = 95.0                                    # +4h: back past the start price 100
    c[298] = 100.0                                  # +24h: below the event close, not past start
    up = st.outcomes(_S(c), 10, 100.0, 1)
    assert up['1h'] == (True, False)
    assert up['4h'] == (False, True)
    assert up['24h'] == (False, False)
    # mirrored down event: start 100, event close 90, continues = lower, undone = above 100
    d = 200.0 - c
    dn = st.outcomes(_S(d), 10, 100.0, -1)
    assert dn == up


def test_outcomes_none_when_horizon_runs_off_data():
    c = np.full(100, 100.0)
    r = st.outcomes(_S(c), 10, 100.0, 1)
    assert r['1h'] == (False, False) and r['4h'] == (False, False) and r['24h'] is None
    c[22] = np.nan
    assert st.outcomes(_S(c), 10, 100.0, 1)['1h'] is None
