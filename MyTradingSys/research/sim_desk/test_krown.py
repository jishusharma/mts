"""Krown study on the desk (exploratory, not the pre-registered krown-dev-event-study). Planted-leak test, hand-computed
fee-net trade, plug-in shape and date lock; the end-to-end run needs the 1m bars."""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402
from studies import _bars  # noqa: E402


def study():
    found = desk.load_studies()
    assert 'krown' in found
    return found['krown']


def walk(n=600, seed=3):
    r = np.random.default_rng(seed)
    c = 100 + np.cumsum(r.normal(0, 1, n))
    o = np.r_[c[0], c[:-1]]
    return o, np.maximum(o, c) + r.random(n), np.minimum(o, c) - r.random(n), c


def test_plugged_in_labelled_and_date_locked():
    s = study()
    assert s.ID == 'krown' and 'exploratory' in s.TITLE.lower()
    for f in s.params():
        if f.get('date'):
            continue
        for t in (list(f['choices'].values()) if f.get('choices') else [f['label']]):
            assert '(trader' in t or '(ours' in t or 'fee' in t.lower(), t
    for bad in ({'end': '2024-07-01'}, {'start': '2022-03-31'}, {'setup': 'S9'}, {'tf': '1m'}):
        with pytest.raises(ValueError):
            s.normalize(bad)
    d = s.describe(s.normalize({}))
    for word in ('S1', 'S6', 'S9', 'exploratory', 'NO-RECALL-CLEARANCE', 'not the pre-registered'):
        assert word.lower() in d.lower(), word


@pytest.mark.parametrize('setup', ['S5', 'S8', 'S4'])
def test_planted_leak_signals_use_only_past_bars(setup):
    """Replacing every bar after `cut` with garbage must not change a signal at or before `cut`."""
    s = study()
    o, h, l, c = walk()
    base = s.signals(setup, o, h, l, c)
    assert len(base) > 0
    cut = 400
    o2, h2, l2, c2 = (x.copy() for x in (o, h, l, c))
    for x in (o2, h2, l2, c2):
        x[cut + 1:] = np.random.default_rng(9).normal(500, 300, len(x) - cut - 1)
    again = s.signals(setup, o2, h2, l2, c2)
    assert [x for x in base if x[0] <= cut] == [x for x in again if x[0] <= cut]


def test_hand_checked_fee_net_trade():
    """Long, market entry at 100, stop 98, target 104 (2 x risk) hit: gross +2R, fees (taker*100 + maker*104)/2 R."""
    s = study()
    a = np.zeros((60, 5))
    a[:, 0] = np.arange(60) * 60000.
    a[:, 1:] = 100.
    a[10, 2] = 104.5
    q = {'taker_pct': 0.05, 'slip_pct': 0.0, 'maker_pct': 0.02, 'start': '1970-01-01', 'end': '1970-01-02'}
    res = _bars.collect([0], a, q, lambda _: [1, 0, None, 98., 104., 50 * 60000, None, 50 * 60000, 100.])
    assert res['net'][0] == pytest.approx(2 - (0.0005 * 100 + 0.0002 * 104) / 2)      # 1.96418 R
    assert res['gross'][0] == pytest.approx(2.0)


needs_data = pytest.mark.skipif(not _bars.data_ready(), reason='1m bars not on this machine')


@needs_data
def test_run_end_to_end_ledger_and_consistency(tmp_path):
    s = study()
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    out = desk.run_setting(s, {}, trials_path=trials, cache_dir=tmp_path / 'c', charts=True)
    assert out['n'] >= 10 and out['verdict'] in ('PASSED', 'FAILED', 'NOT ENOUGH DATA')
    assert '| sim-desk krown ' in trials.read_text(encoding='utf-8')
    res = s.run(s.normalize({}), progress=lambda x: None)
    net, gross, fees, filled = (np.asarray(res[k], float) for k in ('net', 'gross', 'fees', 'filled'))
    f = filled.astype(bool)
    assert np.allclose(net[f], gross[f] - fees[f], atol=1e-9) and np.all(net[~f] == 0.0)
    lo, hi = _bars.day_ms('2022-04-01'), _bars.day_ms('2024-06-30') + _bars.DAY
    assert (np.asarray(res['touch_t']) >= lo).all() and (np.asarray(res['touch_t']) < hi).all()


def test_cache_key_follows_the_krown_code():
    assert len(study()._code_hash()) == 10


@needs_data
def test_trade_construction_stop_entry_time_and_target():
    s = study()
    q = s.normalize({})
    res = s.run(q, progress=lambda x: None)
    b = _bars.resample(_bars.load_1m(), 240)
    idx = {int(t): i for i, t in enumerate(b[:, 0])}
    assert res['refs']
    for ref in res['refs'][:10]:
        side, t0, trig, stop, target = ref[:5]
        i = idx[t0 - 240 * _bars.MIN]                       # the signal bar closed exactly at t0
        assert trig is None
        win = b[i - 9:i + 1]
        assert stop == (win[:, 3].min() if side > 0 else win[:, 2].max())
        assert target == pytest.approx(b[i, 4] + side * 2.0 * abs(b[i, 4] - stop))
