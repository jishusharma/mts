"""Accuracy checks for the desk: a reference number per study, counted over FILLED trades only, fee-net.

levels: the expected numbers come from the frozen study's own csv (ladder_ideas_dev.csv), counted independently of
desk.py: an idea that never filled has net R exactly 0.0 and is not a trade. rsi / wavetrend: the trader-setting
trade count is documented in PLUGIN.md (rsi finds 2 trades); wavetrend's count is a regression pin of our own run.
Data tests run only when the 1m bars (and for levels the idea cache) are on this machine."""
import csv
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402
from studies import _bars  # noqa: E402

LEVELS_CSV = HERE.parent / 'levels_confluence_2026-10-14' / 'ladder_ideas_dev.csv'
needs_bars = pytest.mark.skipif(not _bars.data_ready(), reason='1m bars not on this machine')


def _run(sid, tmp_path, p=None):
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    return desk.run_setting(desk.STUDIES[sid], p or {}, trials_path=trials, cache_dir=tmp_path / 'c')


def test_stats_count_filled_trades_only():
    """Fails if never-filled ideas (net 0.0) are averaged in: 2 filled of 4 ideas -> n 2, mean 0.25, not 0.125."""
    import ladder_run  # noqa: F401  (desk.stats uses the study runner's own bootstrap)
    res = {'net': [1.5, 0.0, -1.0, 0.0], 'gross': [1.6, 0.0, -0.9, 0.0], 'fees': [0.1, 0.0, 0.1, 0.0],
           'filled': [True, False, True, False], 'day': [19083, 19084, 19085, 19086], 'touch_t': [1, 2, 3, 4],
           'all_days': [19083, 19084, 19085, 19086]}
    st = desk.stats(res)
    assert st['n'] == 2 and st['nofill'] == 2
    assert st['mean'] == pytest.approx(0.25)


@pytest.mark.skipif(not LEVELS_CSV.exists(), reason='frozen ladder csv not present')
@needs_bars
def test_levels_default_matches_frozen_csv(tmp_path):
    levels = desk.STUDIES['levels']
    if not levels.cache_ready():
        pytest.skip('levels idea cache not built (python desk.py --build)')
    rows = list(csv.DictReader(open(LEVELS_CSV, encoding='utf-8', newline='')))
    sel = [float(r['S2_K5_X0_2R']) for r in rows if r['E1'] == 'True' and r['S2_K5_X0_2R'] not in ('', 'nan')]
    filled = [v for v in sel if v != 0.0]
    assert (len(sel), len(filled)) == (772, 255)          # the number the old page called "trades"
    out = _run('levels', tmp_path, {'slip_pct': 0})           # the frozen csv has no slippage
    assert out['n'] == 255 and out['nofill'] == 517
    assert out['mean'] == pytest.approx(float(np.mean(filled)), abs=2e-3)       # -0.119 R, fee-net
    assert out['win_rate'] == pytest.approx(sum(v > 0 for v in filled) / 255, abs=2e-3)
    k = out['numbers']                                   # strip: +0.22 gross, -0.34 fees, -0.12 net (Fable review)
    assert (k['mean_gross'], k['mean_fee'], k['mean_net']) == pytest.approx((0.217, 0.337, -0.119), abs=2e-3)
    assert k['profit_factor'] == pytest.approx(sum(v for v in filled if v > 0) / -sum(v for v in filled if v < 0), abs=2e-3)


@needs_bars
@pytest.mark.parametrize('sid,n', [('rsi', 2), ('wavetrend', 369)])
def test_bar_studies_default_counts(sid, n, tmp_path):
    out = _run(sid, tmp_path)         # slippage changes R, never the trade count
    assert out['n'] == n


@needs_bars
@pytest.mark.parametrize('sid', ['rsi', 'wavetrend'])
def test_net_is_gross_minus_fees_and_unfilled_is_zero(sid, tmp_path):
    s = desk.STUDIES[sid]
    res = s.run(s.normalize({}), progress=lambda x: None)
    net, gross, fees, filled = (np.asarray(res[k], float) for k in ('net', 'gross', 'fees', 'filled'))
    f = filled.astype(bool)
    assert f.sum() > 0
    assert np.allclose(net[f], gross[f] - fees[f], atol=1e-9)
    assert np.all(net[~f] == 0.0)


@needs_bars
def test_slippage_hits_market_and_stop_legs_only(tmp_path):
    """0.1 % slippage lowers levels net by more than 0.05 R; a limit-only leg set (maker fee, no market fills) is unchanged.
    Hand check: slip s on a market/stop fill costs s * price / risk in R, the same as that much extra fee."""
    levels = desk.STUDIES['levels']
    if not levels.cache_ready():
        pytest.skip('levels idea cache not built')
    a = _run('levels', tmp_path, {'slip_pct': 0})
    b = _run('levels', tmp_path, {'slip_pct': 0.1})
    assert a['n'] == b['n'] and a['mean'] - b['mean'] > 0.05
    assert desk.numbers  # strip exists
    s = desk.STUDIES['wavetrend']
    r0 = s.run(s.normalize({'slip_pct': 0}), progress=lambda x: None)
    r1 = s.run(s.normalize({'slip_pct': 0.1}), progress=lambda x: None)
    f = r0['filled']
    assert (r1['filled'] == f).all() and (r1['gross'][f] == r0['gross'][f]).all()          # prices unchanged
    assert (r1['fees'][f] > r0['fees'][f]).all()                                           # cost enters through the market legs
