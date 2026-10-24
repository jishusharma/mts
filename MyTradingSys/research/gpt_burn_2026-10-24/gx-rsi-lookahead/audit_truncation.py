"""Read-only RSI audit. Run with python -B; writes no files, emits counted JSON.

Expected RSI is independently calculated from FORMULAS.md section 1 with Decimal.
Parameters used to exercise paths (levels, windows, tolerance) are OURS audit cases.
"""
import argparse
import ast
import csv
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))


def independent_wilder(closes, period):
    """FORMULAS s1: SMA of p changes, recursive Wilder smoothing, flat=50."""
    with localcontext() as ctx:
        ctx.prec = 50
        prices = [Decimal(str(x)) for x in closes]
        out = [None] * len(prices)
        if len(prices) <= period:
            return out
        changes = [b - a for a, b in zip(prices, prices[1:])]
        up = sum((max(x, Decimal(0)) for x in changes[:period]), Decimal(0)) / period
        down = sum((max(-x, Decimal(0)) for x in changes[:period]), Decimal(0)) / period
        for i in range(period, len(prices)):
            if i > period:
                delta = prices[i] - prices[i - 1]
                up = (up * (period - 1) + max(delta, Decimal(0))) / period
                down = (down * (period - 1) + max(-delta, Decimal(0))) / period
            out[i] = float(Decimal(100) * up / (up + down)) if up + down else 50.0
        return out


from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.rsi_ma import rsi_ma
from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events
from MyTradingSys.backtest.layers.rsi.rsi_ma_events import rsi_ma_events
from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence
from MyTradingSys.backtest.layers.rsi.rsi_reclaim import rsi_reclaim_events, rsi_retest
from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_regime, malkan_setup_bull, malkan_setup_bear
from MyTradingSys.backtest.layers.rsi.malkan_mtf import malkan_mtf_bull, malkan_mtf_bear
from MyTradingSys.backtest.layers.rsi.run_divergence_mtf import long_range_divergence
from MyTradingSys.backtest.layers.rsi.run_rsi_backtest import malkan_events, rsi_ma_family_events
from MyTradingSys.backtest.layers.alerts.live_rsi_divergence import rsi_divergence_layer


def snapshots(bars):
    c, ts = [b['c'] for b in bars], [b['t'] for b in bars]
    r = rsi_core(c, 14) if len(c) > 14 else [None] * len(c)
    series, events = {'rsi14': r}, {}
    for p in (2, 9, 21):
        series[f'rsi{p}'] = rsi_core(c, p) if len(c) > p else [None] * len(c)
    for typ in ('SMA', 'EMA', 'RMA', 'WMA'):
        series['ma_' + typ] = rsi_ma(r, typ, 14)
        events['ma_' + typ] = rsi_ma_events(r, series['ma_' + typ], ts, 1)
    for level in (30, 40, 50, 60, 70):
        events[f'level{level}'] = rsi_events(r, ts, level, 2)
    for kind in ('bullish', 'bearish'):
        events[kind] = rsi_divergence(c, r, ts, 3, 10, kind)
        events[kind + '_long'] = long_range_divergence(c, r, ts, 11, 60, kind)
    for direction, level in (('up', 40), ('down', 60)):
        ev = rsi_reclaim_events(r, ts, level, 1, direction)
        events['reclaim_' + direction] = ev
        retests = rsi_retest(r, ev, level, 1, 5, direction)
        # Raw return rows are keyed to the reclaim. This is deliberately tested
        # separately from events stamped at their true availability.
        events['retest_raw_' + direction] = [dict(x, t=ts[x['reclaim_i']]) for x in retests]
        known = []
        for x in retests:
            at = x['resolve_i'] if x['resolve_i'] is not None else x['reclaim_i'] + 5
            if at < len(bars):
                known.append(dict(x, t=ts[at]))
        events['retest_available_' + direction] = known
    series['regime'] = malkan_regime(r, lookback=20)
    events['malkan_bull'] = malkan_setup_bull(bars, r, series['regime'])
    events['malkan_bear'] = malkan_setup_bear(bars, r, series['regime'])
    # Supplied availability times are used here; open-time misuse has a separate repro.
    gates = [ts, ['BULL'] * len(ts), ts, ['BULL'] * len(ts)]
    events['mtf_bull_closed_inputs'] = malkan_mtf_bull(bars, r, series['regime'], *gates)
    gates = [ts, ['BEAR'] * len(ts), ts, ['BEAR'] * len(ts)]
    events['mtf_bear_closed_inputs'] = malkan_mtf_bear(bars, r, series['regime'], *gates)
    events['live_divergence'] = rsi_divergence_layer(bars)
    p = {'period': 14, 'lookback': 20, 'tolerance': 2}
    for name, ev in [('driver_malkan', malkan_events(bars, p))] + [
        ('driver_ma_' + mode, rsi_ma_family_events(bars, dict(p, ma_length=14, mode=mode)))
        for mode in ('touch', 'cross')
    ]:
        events[name] = [dict(x, t=ts[x['i']]) for x in ev]
    return series, events


def truncation(bars):
    full_s, full_e = snapshots(bars)
    counts = {k: {'events': len(v), 'cuts': 0, 'mismatch_cuts': 0, 'changed_rows': 0}
              for k, v in full_e.items()}
    first = {}
    series_checks = 0
    series_failures = 0
    for n in range(1, len(bars) + 1):
        cut_s, cut_e = snapshots(bars[:n])
        t = bars[n - 1]['t']
        for k, v in full_s.items():
            series_checks += 1
            series_failures += cut_s[k] != v[:n]
        for k, v in full_e.items():
            expected = [e for e in v if e['t'] <= t]
            actual = cut_e[k]
            counts[k]['cuts'] += 1
            if actual != expected:
                counts[k]['mismatch_cuts'] += 1
                a = {json.dumps(e, sort_keys=True) for e in actual}
                b = {json.dumps(e, sort_keys=True) for e in expected}
                counts[k]['changed_rows'] += len(a ^ b)
                if k not in first:
                    changed_a, changed_b = sorted(a - b), sorted(b - a)
                    first[k] = {'cut_index': n - 1, 'cut_t': t,
                                'actual_changed': [json.loads(x) for x in changed_a],
                                'full_changed': [json.loads(x) for x in changed_b]}
    return {'series_checks': series_checks, 'series_failures': series_failures,
            'events': counts, 'first_mismatches': first}


def mtf_repro():
    # Audit-owned inputs, no source-code test expectations reused. Both sides mirror.
    result = {}
    for label, values, state, setup in (
        ('bull', [50, 40, 45], 'BULL', malkan_mtf_bull),
        ('bear', [50, 60, 55], 'BEAR', malkan_mtf_bear),
    ):
        bars = [{'t': t, 'o': 100, 'c': 101 if label == 'bull' else 99} for t in (10, 11, 12)]
        kw = dict(level=40 if label == 'bull' else 60, tolerance=1)
        full = setup(bars, values, [state] * 3, [10], [state], [0], [state], **kw)
        closed = setup(bars, values, [state] * 3, [], [], [], [], **kw)
        # Hypothetical weekly open 10 / close 17, monthly open 0 / close 30;
        # daily bar 12 closes 13, both gates are still unavailable then.
        result[label] = {'signal_bar': 12, 'known_at_daily_close': 13,
                         'weekly_close': 17, 'monthly_close': 30,
                         'full_open_time_input_count': len(full),
                         'closed_only_input_count': len(closed), 'full_signal': full}
        assert len(full) == 1 and not closed
    return result


def formula_check(closes):
    result = {}
    for p in (1, 2, 3, 5, 9, 14, 21):
        expected = independent_wilder(closes, p)
        actual = rsi_core(closes, p)
        errs = [abs(a - b) for a, b in zip(actual, expected) if b is not None]
        result[str(p)] = {'compared': len(errs), 'max_abs_error': max(errs),
                          'none_prefix_matches': actual[:p] == expected[:p],
                          'over_1e-10': sum(x > 1e-10 for x in errs)}
    worked = []
    for c, p in (([10, 12, 11, 14], 3), ([10, 11, 10, 12, 11, 13], 2),
                 ([7] * 20, 14), (list(range(20)), 14), (list(range(20, 0, -1)), 14)):
        a, b = rsi_core(c, p), independent_wilder(c, p)
        worked.append({'closes': c, 'period': p, 'expected': b, 'actual': a})
        assert all(x is None and y is None or x is not None and y is not None and abs(x-y) < 1e-12
                   for x, y in zip(a, b))
    return {'fixture_periods': result, 'worked': worked}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='MyTradingSys/backtest/layers/wavetrend/fixture_btcusdt_1h_dev_2022-01.csv')
    args = ap.parse_args()
    path = ROOT / args.csv
    with path.open(newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    # Fixture contains h/l/c but no open. o=c is a synthetic audit convention,
    # giving no candle-filtered malkan signals; additional candle cases below.
    bars = [{'t': int(x['open_time']), 'o': float(x['close']), 'h': float(x['high']),
             'l': float(x['low']), 'c': float(x['close'])} for x in rows]
    assert len({b['t'] for b in bars}) == len(bars)
    assert all(a['t'] < b['t'] for a, b in zip(bars, bars[1:]))
    result = {'fixture': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'parsed_rows': len(rows), 'first_t': bars[0]['t'], 'last_t': bars[-1]['t'],
              'formula': formula_check([b['c'] for b in bars]), 'fixture_truncation': truncation(bars),
              'mtf_open_time_repro': mtf_repro()}
    # Re-exercise candle gates on the same fixture with explicitly synthetic
    # up candles then down candles (does not alter RSI closes or prices).
    for sign, name in ((-1, 'synthetic_up_candles'), (1, 'synthetic_down_candles')):
        altered = [dict(b, o=b['c'] + sign) for b in bars]
        summary = truncation(altered)
        result[name] = {k: v for k, v in summary['events'].items() if 'malkan' in k or 'mtf' in k}
    mirrored = [dict(b, c=100000-b['c'], o=100000-b['o'],
                     h=100000-b['l'], l=100000-b['h']) for b in bars]
    result['mirrored_fixture_truncation'] = truncation(mirrored)
    dirty = [dict(b) for b in bars]
    dirty[100]['c'] = float('nan')
    dirty[200]['h'] = float('inf')
    full_dirty = rsi_divergence_layer(dirty)
    result['live_nonfinite_bars'] = {'dropped_indices': [100, 200], 'events': len(full_dirty),
        'cuts': len(dirty), 'mismatch_cuts': sum(
            rsi_divergence_layer(dirty[:n]) != [e for e in full_dirty if e['t'] <= dirty[n-1]['t']]
            for n in range(1, len(dirty)+1))}
    _, original_events = snapshots(bars)
    result['divergence_evidence'] = original_events['bullish']
    files = sorted((ROOT / 'MyTradingSys/backtest/layers/rsi').glob('*.py'))
    result['scope_inventory'] = [{'file': str(p.relative_to(ROOT)), 'lines': len(p.read_text(encoding='utf-8').splitlines()),
                                  'functions': sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                                                   for n in ast.walk(ast.parse(p.read_text(encoding='utf-8'))))} for p in files]
    # Treat forward-labelled retest rows separately: this script detects and reports
    # them but does not pretend outcome annotations are causal entry events.
    bad = [k for k, v in result['fixture_truncation']['events'].items()
           if v['mismatch_cuts'] and not k.startswith('retest_raw_')]
    result['unexpected_causal_failures'] = bad
    print(json.dumps(result, indent=2))
    assert not bad
    assert result['fixture_truncation']['series_failures'] == 0
    assert all(x['over_1e-10'] == 0 for x in result['formula']['fixture_periods'].values())
    assert result['live_nonfinite_bars']['mismatch_cuts'] == 0
    assert result['mirrored_fixture_truncation']['series_failures'] == 0
    assert not [k for k, v in result['mirrored_fixture_truncation']['events'].items()
                if v['mismatch_cuts'] and not k.startswith('retest_raw_')]


if __name__ == '__main__':
    main()
