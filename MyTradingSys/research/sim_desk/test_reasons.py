"""Exit-reason columns (Fable card 'entry/exit reason columns'): every result array carries a per-idea 'exit'
reason as a string, aligned with 'net'; the breakdown and trade list surface it only when it is present.
Data-free: planted bars/signals and faked per-month parts, no 1m klines or idea cache needed."""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import conditions  # noqa: E402
import desk  # noqa: E402
from studies import _bars  # noqa: E402
from studies import levels  # noqa: E402
from test_conditions import SideStudy  # noqa: E402

MIN = _bars.MIN


def _make_bars(n=450):
    """Flat 1m bars at 100, with two bars overridden to trigger a stop and a target."""
    a = np.column_stack([np.arange(n, dtype=float) * MIN,
                          np.full(n, 100.0), np.full(n, 100.0), np.full(n, 100.0), np.full(n, 100.0)])
    a[1] = [a[1, 0], 100.0, 101.0, 98.0, 99.0]      # low 98 breaches stop 99 (trade "stop")
    a[101] = [a[101, 0], 100.0, 111.0, 99.0, 105.0]  # high 111 reaches target 110 (trade "t1")
    return a


# (side, t_from, trig, stop, target, t_window_end, t_exit, t_hold_end, level); one position at a time, well spaced
TRADES = {
    'stop':   (1, 0 * MIN,   None,  99.0, 110.0, None,      None,     5 * MIN,  0),
    't1':     (1, 100 * MIN, None,  90.0, 110.0, None,      None,     105 * MIN, 0),
    'signal': (1, 200 * MIN, None,  90.0, 200.0, None,      205 * MIN, 220 * MIN, 0),
    'hold':   (1, 300 * MIN, None,  90.0, 200.0, None,      None,     305 * MIN, 0),
    'nofill': (1, 400 * MIN, 150.0, 90.0, 200.0, 405 * MIN, None,     420 * MIN, 0),
}
ORDER = ['stop', 't1', 'signal', 'hold', 'nofill']


def _make(sig):
    return list(TRADES[sig])


def test_bars_collect_exit_is_strings_not_floats():
    """run_trade's own labels (STOP, T1, SIGNAL, HOLD) land in collect()'s result as strings; a never-filled idea
    reads NOFILL. Before the fix this crashed: np.array(['STOP', ...], dtype=float)."""
    a = _make_bars()
    q = {'start': '1970-01-01', 'end': '1970-01-01', 'taker_pct': 0.0, 'slip_pct': 0.0, 'maker_pct': 0.0}
    res = _bars.collect(ORDER, a, q, _make)
    assert res['exit'].dtype.kind == 'U'                                   # string dtype, not float coercion
    assert res['exit'].tolist() == ['STOP', 'T1', 'SIGNAL', 'HOLD', 'NOFILL']
    assert res['filled'].tolist() == [True, True, True, True, False]
    assert len(res['exit']) == len(res['net'])                             # exit counts sum to n (one per idea)


def test_conditions_apply_keeps_exit_aligned_with_mask():
    res = {'net': [1.0, -1.0, 0.5], 'touch_t': [10, 20, 30], 'side': [1, -1, 1], 'filled': [True, True, True],
           'exit': np.array(['STOP', 'T1', 'TIME'], dtype='U8'), 'refs': [0, 1, 2], 'all_days': np.array([0])}
    keep = np.array([True, False, True])
    out = conditions.apply(res, keep)
    assert out['exit'].tolist() == ['STOP', 'TIME']                        # the planted mask drops index 1 only


def test_trade_list_carries_exit_in_time_order():
    res = {'net': [-0.5, 0.0, 2.0, 1.0], 'touch_t': [20, 15, 10, 30], 'side': [-1, 1, 1, -1],
           'filled': [True, False, True, True], 'exit': ['STOP', 'NOFILL', 'T1', 'TIME']}
    L = desk.trade_list(res)
    assert L['i'] == [2, 0, 3] and L['t'] == [10, 20, 30]
    assert L['exit'] == ['T1', 'STOP', 'TIME']                             # never-filled row is not in the list


def test_breakdown_exit_group_counts_sum_to_filled_n():
    res = {'net': [1.0, -1.0, 0.5, -0.2], 'touch_t': [1, 2, 3, 4], 'side': [1, -1, 1, 1],
           'filled': [True, True, True, True], 'exit': ['STOP', 'T1', 'STOP', 'TIME']}
    b = desk.breakdown(res)
    assert 'exit' in b
    assert sum(row['n'] for row in b['exit']) == 4
    assert {row['k'] for row in b['exit']} == {'STOP', 'T1', 'TIME'}


def test_breakdown_without_exit_key_has_no_exit_group():
    """Extends test_build2.py:40 (does not loosen it): a result that carries no 'exit' array, filled trades or
    not, keeps exactly the three original groups."""
    res = {'net': [1.0, -1.0, 0.5, -0.5], 'touch_t': [1, 2, 3, 4], 'side': [1, -1, 1, 1], 'filled': [True] * 4}
    b = desk.breakdown(res)
    assert set(b) == {'year', 'side', 'hour'}
    assert 'exit' not in b


def _exit_reason_result(*exits):
    return {'exits': list(exits)}


def test_levels_exit_reason_maps_ladder_legs_to_canonical_codes():
    """simulate()'s own exit-leg codes collapse to the desk's four plus NOFILL for an idea never filled."""
    assert levels._exit_reason(_exit_reason_result()) == 'NOFILL'
    assert levels._exit_reason(_exit_reason_result((100.0, 1.0, 'TIME'))) == 'TIME'
    assert levels._exit_reason(_exit_reason_result((100.0, 1.0, 'STOP'))) == 'STOP'
    assert levels._exit_reason(_exit_reason_result((100.0, 1.0, 'STOP_LATE'))) == 'STOP'
    assert levels._exit_reason(_exit_reason_result((100.0, 1.0, 'X0'))) == 'T1'
    assert levels._exit_reason(_exit_reason_result((100.0, 0.5, 'T1'), (100.0, 0.5, 'T2'))) == 'T2'
    assert levels._exit_reason(_exit_reason_result((100.0, 0.5, 'T1'), (100.0, 0.5, 'BAND'))) == 'STOP'
    assert levels._exit_reason(_exit_reason_result((100.0, 0.5, 'T1'), (100.0, 0.5, 'CVD_AGAINST'))) == 'STOP'


class _FakeExecutor:
    """Runs map() in-process so levels.run()'s merge logic can be tested without multiprocessing or real data."""
    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def map(self, fn, items):
        return [fn(x) for x in items]


def test_levels_run_merges_per_month_exit_into_canonical_u8_array(monkeypatch):
    """levels.run() merges faked per-month parts; the merged 'exit' array is string-typed and in {STOP, T1, T2,
    TIME, NOFILL}, never the float coercion that used to crash on a string value."""
    parts = [
        {'day': [1], 'touch_t': [1 * 86_400_000], 'side': [1], 'net': [1.0], 'gross': [1.1], 'fees': [0.1],
         'filled': [True], 'refs': [[1 * 86_400_000, 0]], 'all_days': {1}, 'exit': ['STOP']},
        {'day': [2], 'touch_t': [2 * 86_400_000], 'side': [1], 'net': [0.0], 'gross': [0.0], 'fees': [0.0],
         'filled': [False], 'refs': [[2 * 86_400_000, 0]], 'all_days': {2}, 'exit': ['NOFILL']},
    ]
    it = iter(parts)
    monkeypatch.setattr(levels, 'cache_ready', lambda: True)
    monkeypatch.setattr(levels, '_months', lambda: [(1 * 86_400_000, 2 * 86_400_000), (2 * 86_400_000, 3 * 86_400_000)])
    monkeypatch.setattr(levels, '_run_month', lambda args: next(it))
    monkeypatch.setattr(levels, 'ProcessPoolExecutor', _FakeExecutor)
    out = levels.run({'start': '1970-01-02', 'end': '1970-01-03'}, progress=lambda s: None)
    assert out['exit'].dtype.kind == 'U'
    assert out['exit'].tolist() == ['STOP', 'NOFILL']
    assert set(out['exit'].tolist()) <= {'STOP', 'T1', 'T2', 'TIME', 'NOFILL'}


def test_v3_cache_is_rejected_not_served(tmp_path, monkeypatch):
    """Bumping RESULT_VERSION changes the cache key: a result cached under the old version is never read back."""
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    kw = dict(trials_path=trials, cache_dir=tmp_path / 'c')
    SideStudy.calls = 0
    monkeypatch.setattr(desk, 'RESULT_VERSION', 3)
    desk.run_setting(SideStudy, {}, **kw)
    assert SideStudy.calls == 1
    monkeypatch.setattr(desk, 'RESULT_VERSION', 4)
    out = desk.run_setting(SideStudy, {}, **kw)
    assert SideStudy.calls == 2 and not out['cached']          # different key: the v3 cache file is not served
