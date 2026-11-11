"""Synthetic checks for clocks.py: delta injected only at 08:00Z must make hour 8 the top delta bucket; shuffled labels must not."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clocks  # noqa: E402

DAYS = 120
START = 31 * clocks.DAY_MIN


def synth(seed=7):
    rng = np.random.default_rng(seed)
    n = (31 + DAYS + 1) * clocks.DAY_MIN
    o = 100 + np.cumsum(rng.normal(0, .01, n))
    c = o + rng.normal(0, .01, n)
    v = np.full(n, 10.0)
    tb = 5 + rng.normal(0, .2, n)
    minute = np.arange(n) % clocks.DAY_MIN
    tb[(minute >= 480) & (minute < 540)] += 3.0  # delta only in the 08:00Z hour
    return o, c, v, tb


def test_top_bucket_is_hour8_and_placebo_is_not():
    o, c, v, tb = synth()
    arr = clocks.build_instances(o, c, v, tb, START, DAYS)['hour']
    assert len(arr) == DAYS * 24
    lab = arr[:, 0].astype(int)
    cnt, obs, z = clocks.placebo_z(lab, arr[:, 2:], 24, nperm=200)
    assert int(np.argmax(obs[:, 0])) == 8 and z[8, 0] > 5
    cnt2, obs2, z2 = clocks.placebo_z(lab, arr[:, 2:], 24, nperm=200, shuffle_obs=True)
    assert int(np.argmax(obs2[:, 0])) != 8 and np.abs(z2[:, 0]).max() < 4


def test_missing_bar_drops_instance_and_fwd_math():
    o, c, v, tb = synth()
    v[START + 5] = np.nan
    inst = clocks.build_instances(o, c, v, tb, START, DAYS)
    assert len(inst['hour']) == DAYS * 24 - 1
    e = START + 60
    j60, j15 = e + 59, e + 14
    row = inst['hour'][0]
    assert row[0] == 1 and abs(row[5] - (c[j60] / o[e] - 1) * 1e4) < 1e-9
    assert abs(row[4] - (c[j15] / o[e] - 1) * 1e4) < 1e-9


def test_funding_entry_is_one_minute_after_settlement():
    o, c, v, tb = synth()
    row = clocks.build_instances(o, c, v, tb, START, DAYS)['fund'][1]  # day 0, 08Z
    e = START + 8 * 60 + 1
    j60 = e + 59
    assert row[0] == 1 and abs(row[5] - (c[j60] / o[e] - 1) * 1e4) < 1e-9


def test_only_dev_split_allowed():
    try:
        clocks.main(['--split', 'validation'])
    except SystemExit as e:
        assert 'dev' in str(e)
    else:
        raise AssertionError('validation split was accepted')
