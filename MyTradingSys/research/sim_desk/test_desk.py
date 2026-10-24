"""Simulator desk core tests. Expected numbers come from the study's own frozen record (frozen_rule.json, written by
ladder_run.py before the desk existed) and an independent Haiku re-derivation from ladder_ideas_dev.csv, never from desk code.

The data tests (real re-simulation) run only when the local idea cache is built (first desk Run, or
`python MyTradingSys/research/sim_desk/desk.py --build`); the rest need no market data.
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
STUDY_DIR = HERE.parent / 'levels_confluence_2026-10-14'
FROZEN = json.loads((STUDY_DIR / 'frozen_rule.json').read_text(encoding='utf-8'))

import desk  # noqa: E402
from studies import levels as study_levels  # noqa: E402

FROZEN_P = {'entry': 'E1', 'scale': 'S2', 'stop': 'K5', 'exit': 'X0_2R'}


# ---- verdict (the study runner's rule order) ----
def test_verdict_frozen_reads_failed_by_sample_spread():
    st = dict(FROZEN['dev'])
    st['power_plausible'] = FROZEN['power']['power_plausible_0.10R']
    st['power_mde'] = FROZEN['power']['power_mde']
    word, reason = desk.verdict(st)
    assert word == 'FAILED'
    assert '+0.10 R' in reason and '50 %' not in reason and 'chance to detect' not in reason


def test_verdict_passed_and_wide():
    assert desk.verdict({'n': 500, 'mean': .2, 'lo': .05, 'hi': .35, 'power_plausible': .2})[0] == 'PASSED'
    assert 'DEV only' in desk.verdict({'n': 500, 'mean': .2, 'lo': .05, 'hi': .35, 'power_plausible': .2})[1]
    # the two-point model no longer decides: weak power_mde but a ruled-out edge still reads FAILED
    assert desk.verdict({'n': 900, 'mean': -.1, 'lo': -.2, 'hi': .0, 'power_mde': {'power': .1}, 'power_plausible': .9})[0] == 'FAILED'
    assert desk.verdict({'n': 900, 'mean': .0, 'lo': -.1, 'hi': .2, 'power_plausible': .9})[0] == 'NOT ENOUGH DATA'
    assert desk.verdict({'n': 0})[0] == 'NOT ENOUGH DATA'


def test_verdict_few_trades_and_range_below_zero():
    # 2 trades never decide anything, however narrow their range
    assert desk.verdict({'n': 2, 'mean': -1.04, 'lo': -1.042, 'hi': -1.03, 'power_plausible': .9})[0] == 'NOT ENOUGH DATA'
    assert '30' in desk.verdict({'n': 2, 'mean': -1.04, 'lo': -1.042, 'hi': -1.03, 'power_plausible': .9})[1]
    # the whole range below zero is a loser even when the sample could not see +0.10 R
    assert desk.verdict({'n': 369, 'mean': -.158, 'lo': -.288, 'hi': -.023, 'power_plausible': .3})[0] == 'FAILED'


def test_no_two_point_model_on_screen(tmp_path):
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    r = desk.run_setting(FakeStudy, {'x': 5}, trials_path=trials, cache_dir=tmp_path / 'c')
    assert 'power_mde' not in r['stats'] and not r.get('footnote')


# ---- date lock ----
@pytest.mark.parametrize('start,end', [('2022-04-01', '2024-07-01'), ('2022-04-01', '2025-01-31'), ('2022-03-31', '2024-06-30'),
                                       ('2024-07-01', '2024-08-01'), ('2023-05-01', '2023-04-01')])
def test_date_lock_refuses_outside_dev(start, end):
    with pytest.raises(ValueError):
        desk.check_dates(start, end)


def test_date_lock_accepts_dev():
    assert desk.check_dates('2022-04-01', '2024-06-30') == ('2022-04-01', '2024-06-30')


def test_study_normalize_refuses_validation_dates():
    with pytest.raises(ValueError):
        study_levels.normalize({**FROZEN_P, 'end': '2024-12-31'})


# ---- ledger and cache, with a fake study (no market data) ----
class FakeStudy:
    ID = 'fake'
    calls = 0

    @staticmethod
    def normalize(p):
        out = {'x': float(p.get('x', 1)), 'start': '2022-04-01', 'end': '2024-06-30'}
        return out

    @staticmethod
    def label(p):
        return f"x {p['x']}"

    @staticmethod
    def describe(p):
        return 'fake'

    @classmethod
    def run(cls, p, progress=None):
        cls.calls += 1
        rng = np.random.default_rng(1)
        days = np.repeat(np.arange(100), 3)
        net = rng.normal(0, 1, days.size) * p['x']
        return {'day': days, 'touch_t': np.arange(days.size), 'net': net, 'gross': net + .1,
                'fees': np.full(days.size, .1), 'all_days': np.arange(100), 'refs': [None] * days.size,
                'filled': np.ones(days.size, bool)}


def _rows(path):
    return [ln for ln in path.read_text(encoding='utf-8').split('\n') if '| sim-desk ' in ln]


def test_one_ledger_row_per_new_setting_none_for_repeat(tmp_path):
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('| date | trial |\n', encoding='utf-8')
    r1 = desk.run_setting(FakeStudy, {'x': 1}, trials_path=trials, cache_dir=tmp_path / 'c')
    assert len(_rows(trials)) == 1 and not r1['cached']
    r2 = desk.run_setting(FakeStudy, {'x': 1}, trials_path=trials, cache_dir=tmp_path / 'c')
    assert len(_rows(trials)) == 1 and r2['cached']
    assert r2['n'] == r1['n'] and r2['mean'] == r1['mean']
    r3 = desk.run_setting(FakeStudy, {'x': 2}, trials_path=trials, cache_dir=tmp_path / 'c')
    assert len(_rows(trials)) == 2 and r3['try_no'] == 2
    assert 'x 2' in _rows(trials)[-1]


def test_row_written_before_result_shows(tmp_path):
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    r = desk.run_setting(FakeStudy, {'x': 3}, trials_path=trials, cache_dir=tmp_path / 'c')
    assert r['try_no'] == len(_rows(trials)) == 1


def test_losing_streak():
    assert desk.worst_streak(np.array([1., -1, -1, 2, -1, -1, -1, 0.5])) == 3
    assert desk.worst_streak(np.array([1., 2])) == 0


# ---- stats against the stored per-idea CSV (fee-net R rounded to 3 decimals) ----
def test_stats_count_only_filled_trades_csv():
    """A no-fill idea pays no fee, so its stored net R is exactly 0; filled trades always pay a fee (Fable review C1)."""
    with (STUDY_DIR / 'ladder_ideas_dev.csv').open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    all_days = np.array(sorted({int(r['day']) for r in rows}))
    sel = [r for r in rows if r['E1'] == 'True' and r['S2_K5_X0_2R'] != '']
    net = np.array([float(r['S2_K5_X0_2R']) for r in sel])
    filled = net != 0
    res = {'day': np.array([int(r['day']) for r in sel]), 'touch_t': np.array([int(r['touch_t']) for r in sel]),
           'net': net, 'gross': net, 'fees': np.zeros(net.size), 'all_days': all_days, 'filled': filled}
    st = desk.stats(res)
    assert st['n'] == 255 and st['nofill'] == 517
    assert abs(st['mean'] - (-0.119)) < 1e-3


# ---- plain words ----
def test_labels_are_plain_words():
    text = study_levels.describe(study_levels.normalize(FROZEN_P))
    for code in ('E1', 'S2', 'K5', 'X0_2R', 'LC3', 'KEEP', 'arm P'):
        assert code not in text
    assert 'stop' in text and 'target' in text


def test_unused_target_box_does_not_block_a_run():
    assert study_levels.normalize({**FROZEN_P, 'target_r': 0})['target_r'] is None
    with pytest.raises(ValueError):
        study_levels.normalize({**FROZEN_P, 'exit': 'R', 'target_r': 0})


def test_non_number_gives_plain_message():
    with pytest.raises(ValueError) as e:
        study_levels.normalize({**FROZEN_P, 'stop_pct': 'abc'})
    assert 'could not convert' not in str(e.value) and 'number' in str(e.value)


def test_already_tried_is_keyed_on_trials_not_cache(tmp_path):
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    desk.run_setting(FakeStudy, {'x': 7}, trials_path=trials, cache_dir=tmp_path / 'tree1')
    r = desk.run_setting(FakeStudy, {'x': 7}, trials_path=trials, cache_dir=tmp_path / 'tree2')
    assert len(_rows(trials)) == 1 and r['already_tried']


def test_params_cover_free_form_fields():
    names = {f['name'] for f in study_levels.params()}
    assert {'entry', 'scale', 'stop', 'stop_pct', 'exit', 'target_r', 'maker_pct', 'taker_pct', 'start', 'end'} <= names


# ---- real re-simulation (needs the local idea cache) ----
needs_cache = pytest.mark.skipif(not study_levels.cache_ready(), reason='idea cache not built (desk.py --build)')


@needs_cache
def test_frozen_setup_filled_trades_and_verdict(tmp_path):
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    r = desk.run_setting(study_levels, FROZEN_P, trials_path=trials, cache_dir=tmp_path / 'c')
    assert r['n'] == 255 and r['nofill'] == 517 and r['n'] + r['nofill'] == FROZEN['dev']['n']
    # all-ideas mean (no-fills as 0) still equals the study's frozen number
    assert abs(r['mean'] * r['n'] / 772 - FROZEN['dev']['mean']) < 1e-9
    assert abs(r['mean'] - (-0.119)) < 1e-3
    # on filled trades the spread is wide (sd about 1.57 R): +0.10 R is NOT ruled out, so the honest verdict is
    # NOT ENOUGH DATA; the review's FAILED came from the 517 zero rows shrinking the spread (lead check 2026-10-21)
    assert r['verdict'] == 'NOT ENOUGH DATA' and r['hi'] > 0.10 and r['lo'] < -0.3


@needs_cache
def test_free_form_target_2r_equals_grid_and_stop_pct_changes_result(tmp_path):
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    a = desk.run_setting(study_levels, FROZEN_P, trials_path=trials, cache_dir=tmp_path / 'c')
    b = desk.run_setting(study_levels, {**FROZEN_P, 'exit': 'R', 'target_r': 2.0}, trials_path=trials, cache_dir=tmp_path / 'c')
    assert b['n'] == a['n'] and abs(b['mean'] - a['mean']) < 1e-12
    c = desk.run_setting(study_levels, {**FROZEN_P, 'stop_pct': 0.25}, trials_path=trials, cache_dir=tmp_path / 'c')
    assert not math.isclose(c['mean'], a['mean'])
    assert len(_rows(trials)) == 3
