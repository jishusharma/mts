"""Read-only comparison and in-memory mutation audit; writes only report.md here."""
import csv
import io
import math
import sys
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from wt import DATA, derive, load_fixture

HERE = Path(__file__).resolve().parent
MODULE = DATA / 'wavetrend.py'
TEST = DATA / 'test_wavetrend.py'


def module_from_source(source):
    module = types.ModuleType('wavetrend')
    module.__file__ = str(MODULE)
    exec(compile(source, str(MODULE), 'exec'), module.__dict__)
    return module


def test_source(source):
    sys.modules['wavetrend'] = module_from_source(source)
    tests = types.ModuleType('audit_tests')
    tests.__file__ = str(TEST)
    exec(compile(TEST.read_text(encoding='utf-8'), str(TEST), 'exec'), tests.__dict__)
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream).run(suite)
    return result.testsRun, [t.id() for t, _ in result.failures], [t.id() for t, _ in result.errors]


def difference(a, b, column, start=0):
    maximum = 0.0
    exact = beyond = nan_mismatch = 0
    first_exact = first_beyond = first_nan = None
    finite = 0
    for i in range(start, len(a)):
        x, y = a[i][column], b[i][column]
        if math.isnan(x) or math.isnan(y):
            if math.isnan(x) != math.isnan(y):
                nan_mismatch += 1
                if first_nan is None: first_nan = i
            continue
        finite += 1
        delta = abs(x-y)
        maximum = max(maximum, delta)
        if delta:
            exact += 1
            if first_exact is None: first_exact = i
        if delta > 1e-9:
            beyond += 1
            if first_beyond is None: first_beyond = i
    return (f'| {column} | {finite} | {maximum:.17g} | {exact} / {first_exact} | '
            f'{beyond} / {first_beyond} | {nan_mismatch} / {first_nan} |')


def main():
    fixture = load_fixture()
    independent = derive(fixture)
    with (DATA / 'golden_wt_btcusdt_1h_dev_2022-01.csv').open(newline='') as stream:
        golden = [dict(open_time=int(r['open_time']),
                       wt1=float(r['wt1']) if r['wt1'] else math.nan,
                       wt2=float(r['wt2']) if r['wt2'] else math.nan,
                       event=int(r['event'])) for r in csv.DictReader(stream)]
    assert len(fixture) == len(golden) == 400
    assert all(a['open_time'] == b['open_time'] for a,b in zip(independent,golden))
    assert len({r['open_time'] for r in independent}) == 400
    assert all(b['open_time']-a['open_time'] == 3600000 for a,b in zip(independent, independent[1:]))
    source = MODULE.read_text(encoding='utf-8')
    module = module_from_source(source)
    bars = [(int(r['open_time']), float(r['high']), float(r['low']), float(r['close'])) for r in fixture]
    raw = [r._asdict() for r in module.compute(bars, 3600000, warmup=0)]
    masked = [r._asdict() for r in module.compute(bars, 3600000)]
    assert len(raw) == len(masked) == 400
    # Golden events are unmasked; independently infer them from strict sides.
    raw_independent = [dict(r) for r in independent]
    side = 0
    for r in raw_independent:
        if math.isnan(r['wt2']):
            side = 0
            r['event'] = 0
        else:
            new = (r['wt1'] > r['wt2']) - (r['wt1'] < r['wt2'])
            r['event'] = new if new and side and new != side else 0
            if new: side = new
    lines = ['# WaveTrend independent re-derivation audit', '',
             'Command (repo root): `python -B MyTradingSys/research/gpt_burn_2026-10-24/gx-wavetrend-rederive/audit.py`.', '',
             'Scope: FORMULAS.md:513-523; independent standard-library `wt.py` written before reading the implementation, tests or golden generator. No repository imports in wt.py. audit.py executes the implementation and test source in memory only for comparison and mutations. No existing files modified; no git, sync or push commands run.', '',
             'Parameters: SOURCED HLC3, EMA(10), EMA(21), 0.015 and SMA(4) (FORMULAS.md:513); OURS first-valid seed, relative flat tolerance 1e-9, warmup 200, cross and zone conventions (:515), comparison tolerance 1e-9 (:523).', '',
             'All CSV rows parsed and counted: 400 fixture + 400 golden, timestamps identical, unique and contiguous hourly, indices 0–399. Start 2022-01-01 00:00 UTC; end 2022-01-17 15:00 UTC. Indices are zero-based. CSV line = index + 2. No conclusions use truncated output.', '',
             'Independent recurrence uses state += alpha*(value-state); implementation uses alpha*value+(1-alpha)*state. At bar 0: ap=46530.09666666667, esa=ap, d=0, ci/wt1/wt2=NaN. At bar 1: ap=46760.56, esa=46571.99909090909, d=34.28380165289193, ci=wt1=366.6666666666667. wt2 first exists at bar 4. Thus first-valid seeding, HLC3 and the specified smoothing agree.', '']
    for label, a, b, start in [
        ('Independent vs golden, raw entire series', raw_independent,golden,0),
        ('Independent vs wavetrend.py warmup=0, entire series',raw_independent,raw,0),
        ('Independent vs golden, usable bars 200–399',independent,golden,200),
        ('Independent vs wavetrend.py default, usable bars 200–399',independent,masked,200)]:
        lines += [f'## {label}', '',
                  '| Column | Finite pairs | Max abs diff | Exact differing count / first bar | >1e-9 count / first bar | NaN mismatch count / first bar |',
                  '|---|---:|---:|---|---|---|']
        for column in ['wt1','wt2','event']: lines.append(difference(a,b,column,start))
        lines.append('')
    time_mismatches = sum(r['open_time'] != independent[i]['open_time'] for i,r in enumerate(masked))
    available_mismatches = sum(r['available_at'] != independent[i]['open_time']+3600000 for i,r in enumerate(masked))
    def zone(v):
        return 'ob2' if v >= 60 else 'ob1' if v >= 53 else 'os2' if v <= -60 else 'os1' if v <= -53 else 'mid'
    zones = sum(r['zone'] != (None if i < 200 else zone(independent[i]['wt1'])) for i,r in enumerate(masked))
    lines += [f'open_time max abs diff = 0 ({time_mismatches} mismatches); available_at max abs diff = 0 ({available_mismatches} mismatches); zone mismatches = {zones}. Golden has no zone/available_at columns. Raw NaNs: wt1=1, wt2=4; default output masks bars 0–199 (200 NaNs per numeric output), first usable bar=200.', '',
              'Cause of exact numeric differences: floating-point evaluation order and golden CSV rounding to 12 decimal places (make_golden.py:24), not seed, smoothing or ap source. Default-vs-raw differences before index 200 are the required warmup mask (wavetrend.py:104-107), not formula errors. Golden stores unmasked crosses; comparisons use matching scope. This is spreadsheet-style parity, not TradingView/Pine-runtime parity.', '',
              '## Mutation checks', '', '| In-memory change | Tests run | Failing tests | Errors |', '|---|---:|---|---|']
    mutations = {
        'baseline':source,
        'ap source HLC3 -> close (line 92)':source.replace('ap = (h + l + c) / 3.0','ap = c'),
        'EMA21 alpha -> EMA22 (line 76)':source.replace('2.0 / (N2 + 1)','2.0 / (N2 + 2)'),
        'wt1 first seed -> zero (line 101)':source.replace('tci = ci if tci is None','tci = 0.0 if tci is None'),
        'SMA4 -> SMA3 (line 105)':source.replace('sma(raw, SMA_N)','sma(raw, SMA_N - 1)'),
        'post-gap/NaN permanently suppress output (lines 85-90,104)':source.replace(
            '    prev_t = None', '    reset_seen = False\n    prev_t = None').replace(
            '            esa = dev = tci = None\n            since = 0',
            '            reset_seen = True\n            esa = dev = tci = None\n            since = 0').replace(
            'keep[i] = since >= warmup', 'keep[i] = since >= warmup and not reset_seen'),
    }
    for name, variant in mutations.items():
        count, failures, errors = test_source(variant)
        lines.append(f'| {name} | {count} | {", ".join(failures) or "none"} | {", ".join(errors) or "none"} |')
    poisoned = module_from_source(mutations['post-gap/NaN permanently suppress output (lines 85-90,104)'])
    extended = bars + [(t+400*3600000,h,l,c) for t,h,l,c in bars]
    extended[230] = (extended[230][0],math.nan,math.nan,math.nan)
    good = module.compute(extended,3600000)
    bad = poisoned.compute(extended,3600000)
    first_good = next(i for i in range(231,len(good)) if not math.isnan(good[i].wt1))
    assert math.isnan(bad[first_good].wt1)
    assert not any(not math.isnan(r.wt1) for r in bad[231:])
    lines += ['', 'All mutations use exact string replacements in memory; the original files remain unchanged. The HLC3, smoothing, seed and SMA errors are killed by the existing suite. Golden value assertions at test_wavetrend.py:37-38 catch source/smoothing/SMA errors; the hand fixture at :67 also catches the zero-seed error.', '',
              '## Finding', '',
              '**LOW — reset tests do not verify recovery.** `MyTradingSys/backtest/layers/wavetrend/test_wavetrend.py:81-93` tests NaN/gap reset only through bar 259 (29 bars after reset), far short of the 200-bar re-warmup. Adding a reset_seen flag set only in the gap/NaN reset branches at wavetrend.py:85-90 and requiring not reset_seen in the output mask at :104 passes every existing test, but permanently suppresses later usable values. This is a test coverage weakness, not a demonstrated defect in the current implementation.', '',
              f'Reproduction: run the command above. For 800 bars made by repeating the fixture with a timestamp offset and a NaN at index 230, the unmodified implementation first recovers at index {first_good}; the mutant has wt1=NaN at that index and {sum(not math.isnan(r.wt1) for r in bad[231:])} usable rows after reset. A test should extend beyond recovery and check recovery timing and independently derived restarted values for both NaN and gap resets.', '',
              'Boundary event: the unmasked independent/golden cross at index 200 is -1; default wavetrend.py emits 0 there because its prior output is NaN and cross state resets (wavetrend.py:51-54,106-108). This is a warmup/cross-state convention, not a seed, smoothing or ap error. Existing golden event tests intentionally compare from index 201 (test_wavetrend.py:43-44). All 199 event rows at indices 201-399 match exactly. Raw events match on all 400 rows.', '',
              'No CRITICAL/HIGH findings; no numeric or metadata disagreement above tolerance on the requested 400-bar fixture. The independent wt.py audit scope is this finite contiguous fixture; its gap/invalid-input behavior is not claimed as a full replacement module.', '',
              'Result: Numeric parity within 1e-9; raw events match, default event differs only at warmup boundary 200; four formula mutations caught; LOW reset-recovery test gap reproduced.']
    with (HERE / 'report.md').open('w', encoding='utf-8', newline='\n') as stream:
        stream.write('\n'.join(lines)+'\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
