"""Pitchfork study on the desk (Andrews / Schiff / Modified Schiff).

Verifies:
- Plug-in discovery, parameter labelling ('(trader' / '(ours' / 'fee'), and DEV date lock.
- Planted-leak causality test: replacing every bar after `cut` with garbage must not alter any signal at or before `cut`.
- Hand-checked fee-net trade calculation via `_bars.collect`.
- End-to-end DEV window run (when 1m bars are available on disk), TRIALS.md ledger row, chart SVG generation, and trade construction invariants.
"""
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
    assert 'pitchfork' in found
    return found['pitchfork']


def walk(n=500, seed=7):
    r = np.random.default_rng(seed)
    # Generate realistic 4H-like percentage swings so 3% ZigZag pivots trigger cleanly
    rets = r.normal(0.0005, 0.018, n)
    c = 20000.0 * np.exp(np.cumsum(rets))
    o = np.r_[c[0], c[:-1]]
    span = c * r.uniform(0.004, 0.015, n)
    h = np.maximum(o, c) + span
    l = np.minimum(o, c) - span
    return o, h, l, c


def test_plugged_in_labelled_and_date_locked():
    s = study()
    assert s.ID == 'pitchfork' and 'pitchfork' in s.TITLE.lower()
    for f in s.params():
        if f.get('date'):
            continue
        for t in (list(f['choices'].values()) if f.get('choices') else [f['label']]):
            assert '(trader' in t or '(ours' in t or 'fee' in t.lower(), t
    for bad in (
        {'end': '2024-07-01'},
        {'start': '2022-03-31'},
        {'variant': 'unknown_fork'},
        {'setup': 'INVALID'},
        {'vp_filter': 'BAD'},
        {'tf': '1m'},
    ):
        with pytest.raises(ValueError):
            s.normalize(bad)
    d = s.describe(s.normalize({}))
    for word in ('Pitchfork', 'Modified Schiff', 'development window only'):
        assert word.lower() in d.lower(), word


@pytest.mark.parametrize('variant', ['modified_schiff', 'schiff', 'standard'])
@pytest.mark.parametrize('setup', ['BOUNCE', 'HAGOPIAN', 'BOTH'])
def test_planted_leak_signals_use_only_past_bars(variant, setup):
    """Replacing every bar after `cut` with extreme garbage must not change any signal at or before `cut`."""
    s = study()
    o, h, l, c = walk(n=500, seed=11)
    base = s.signals(variant, setup, 'ALL', '4h', h, l, c)
    assert len(base) > 0
    cut = 350
    rng = np.random.default_rng(99)
    rem = len(c) - cut - 1
    g_c = rng.uniform(5000.0, 90000.0, rem)
    g_h = g_c * 1.10
    g_l = g_c * 0.90
    h2 = np.concatenate([h[:cut + 1], g_h])
    l2 = np.concatenate([l[:cut + 1], g_l])
    c2 = np.concatenate([c[:cut + 1], g_c])
    again = s.signals(variant, setup, 'ALL', '4h', h2, l2, c2)
    assert [x for x in base if x['bar_index'] <= cut] == [x for x in again if x['bar_index'] <= cut]


def test_hand_checked_fee_net_trade():
    """Long, market entry at 100, stop 98.5 (1.5% stop), target 103 (2 x risk) hit: gross +2R, fees (taker*100 + maker*103)/1.5 R."""
    a = np.zeros((60, 5))
    a[:, 0] = np.arange(60) * 60000.0
    a[:, 1:] = 100.0
    a[10, 2] = 103.5
    q = {'taker_pct': 0.05, 'slip_pct': 0.0, 'maker_pct': 0.02, 'start': '1970-01-01', 'end': '1970-01-02'}
    res = _bars.collect([0], a, q, lambda _: [1, 0, None, 98.5, 103.0, 50 * 60000, None, 50 * 60000, 100.0])
    assert res['net'][0] == pytest.approx(2.0 - (0.0005 * 100.0 + 0.0002 * 103.0) / 1.5)
    assert res['gross'][0] == pytest.approx(2.0)


def test_cache_key_follows_pitchfork_code():
    assert len(study()._code_hash()) == 10


needs_data = pytest.mark.skipif(not _bars.data_ready(), reason='1m bars not on this machine')


@needs_data
def test_run_end_to_end_ledger_and_consistency(tmp_path):
    s = study()
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    out = desk.run_setting(s, {}, trials_path=trials, cache_dir=tmp_path / 'c', charts=True)
    assert out['n'] >= 15 and out['verdict'] in ('PASSED', 'FAILED', 'NOT ENOUGH DATA')
    assert '| sim-desk pitchfork ' in trials.read_text(encoding='utf-8')
    assert 1 <= len(out['charts']) <= 6
    q = s.normalize({})
    for ch in out['charts']:
        tr = s.chart_trade(ch['ref'], q)
        assert tr['stop'] == ch['ref'][3] and 'UTC' in ch['svg']
    res = s.run(q, progress=lambda x: None)
    net, gross, fees, filled = (np.asarray(res[k], float) for k in ('net', 'gross', 'fees', 'filled'))
    f = filled.astype(bool)
    assert np.allclose(net[f], gross[f] - fees[f], atol=1e-9) and np.all(net[~f] == 0.0)
    lo, hi = _bars.day_ms('2022-04-01'), _bars.day_ms('2024-06-30') + _bars.DAY
    assert (np.asarray(res['touch_t']) >= lo).all() and (np.asarray(res['touch_t']) < hi).all()
