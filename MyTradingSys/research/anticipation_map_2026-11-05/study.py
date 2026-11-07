"""Anticipation map base rates: price x OI x taker delta over 60 min, and what followed (card anticipation-map-from-current-layer-stat).

Descriptive, fee-free: no entries, no costs, no edge claim. DEV window only (bars before 2024-07-01).
Data SOURCED: Binance USD-M BTCUSDT 1m klines (F:/MTS/data/tom_raw/klines), Binance metrics 5m sum_open_interest
(F:/MTS/data/binance_metrics). Every threshold below = OURS, fixed in PRE_REG.md before the run.
Writes MyTradingSys/tools/live_aid/anticipation_rates.js and prints the RESULT table.
"""
import csv
import glob
import json
import os
from datetime import datetime, timezone

KLINES = 'F:/MTS/data/tom_raw/klines'
METRICS = 'F:/MTS/data/binance_metrics'
DEV_END_MS = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)  # DEV only; VALIDATION/HOLDOUT never read
WIN = 60          # OURS: minutes in the state window and in the follow-up window
FLAT = 0.001      # OURS: |price change| or |OI change| under 0.1 % = flat (same as live_aid OM.flat)
REGIME = 0.10     # OURS: trailing 30-day return > +10 % bull, < -10 % bear, else range
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JS = os.path.join(HERE, '..', '..', 'tools', 'live_aid', 'base_rates_input', 'anticipation_rates.js')


def load_klines(symbol='BTCUSDT'):
    """1m close, volume, taker buy volume by open_time ms; refuses rows at or after DEV_END_MS."""
    bars = {}
    for f in sorted(glob.glob(os.path.join(KLINES, symbol + '-1m-*.csv'))):
        with open(f, newline='') as fh:
            for r in csv.reader(fh):
                if not r or not r[0].isdigit():
                    continue
                t = int(r[0])
                if t >= DEV_END_MS:
                    continue
                bars[t] = (float(r[4]), float(r[5]), float(r[9]))
    return bars


def load_oi(symbol='BTCUSDT'):
    oi = {}
    for f in sorted(glob.glob(os.path.join(METRICS, symbol + '-metrics-*.csv'))):
        with open(f, newline='') as fh:
            for r in csv.DictReader(fh):
                t = int(datetime.strptime(r['create_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp() * 1000)
                if t >= DEV_END_MS or not r['sum_open_interest'] or float(r['sum_open_interest']) <= 0:
                    continue  # zero OI rows = feed gaps, treated as missing (post-freeze fix, noted in RESULT.md)
                oi[t] = float(r['sum_open_interest'])
    return oi


def sgn(x, flat):
    return 'FLAT' if abs(x) < flat else ('UP' if x > 0 else 'DOWN')


def key(p, o, d):
    return p + '|' + o + '|' + d


def events(bars, oi):
    """One event per hour close t: state over [t-60, t), follow-up over [t, t+60). Price = 1m close before t."""
    out = []
    m = 60000
    hours = sorted(t for t in oi if t % 3600000 == 0)
    for t in hours:
        t0, t2 = t - WIN * m, t + WIN * m
        if t0 not in oi or t2 not in oi or t2 >= DEV_END_MS:
            continue
        win = [bars.get(t0 + i * m) for i in range(WIN)]
        fwd = [bars.get(t + i * m) for i in range(WIN)]
        prev = bars.get(t0 - m)
        if prev is None or any(b is None for b in win) or any(b is None for b in fwd):
            continue
        p0, p1, p2 = prev[0], win[-1][0], fwd[-1][0]
        delta = sum(2 * b[2] - b[1] for b in win)
        dp, doi = p1 / p0 - 1, oi[t] / oi[t0] - 1
        out.append({'t': t, 'dp': dp, 'doi': doi, 'delta': delta, 'p0': p0, 'p1': p1,
                    'fdp': p2 / p1 - 1, 'fdoi': oi[t2] / oi[t] - 1})
    return out


def regime_of(bars_close_by_day, t):
    day = t // 86400000
    a, b = bars_close_by_day.get(day - 30), bars_close_by_day.get(day)
    if a is None or b is None:
        return 'range'
    r = b / a - 1
    return 'bull' if r > REGIME else 'bear' if r < -REGIME else 'range'


def table(evs):
    rates, states = {}, {}
    for e in evs:
        p, o = sgn(e['dp'], FLAT), sgn(e['doi'], FLAT)
        if p == 'FLAT' or o == 'FLAT':
            continue
        d = 'BUY' if e['delta'] > 0 else 'SELL'
        states[p + '|' + o] = states.get(p + '|' + o, 0) + 1
        k = key(p, o, d)
        r = rates.setdefault(k, {'n': 0, 'cont': 0, 'kill': 0, 'oiCont': 0})
        r['n'] += 1
        up = p == 'UP'
        r['cont'] += (e['fdp'] > 0) == up
        # kill = within the follow-up hour the close is back past the window's start price (the move undone)
        r['kill'] += (e['p1'] * (1 + e['fdp']) < e['p0']) if up else (e['p1'] * (1 + e['fdp']) > e['p0'])
        r['oiCont'] += (e['fdoi'] > 0) == (o == 'UP')
    for k, r in rates.items():
        s = states[k.rsplit('|', 1)[0]]
        r['share'] = round(100 * r['n'] / s)
        for f in ('cont', 'kill', 'oiCont'):
            r[f] = round(100 * r[f] / r['n'])
    return rates, states


def main():
    bars = load_klines()
    oi = load_oi()
    assert max(bars) < DEV_END_MS and max(oi) < DEV_END_MS
    evs = events(bars, oi)
    by_day = {}
    for t in sorted(bars):
        by_day[t // 86400000] = bars[t][0]
    reg = {'bull': 0, 'bear': 0, 'range': 0}
    for e in evs:
        reg[regime_of(by_day, e['t'])] += 1
    rates, states = table(evs)
    first = datetime.fromtimestamp(evs[0]['t'] / 1000, timezone.utc).strftime('%Y-%m-%d')
    last = datetime.fromtimestamp(evs[-1]['t'] / 1000, timezone.utc).strftime('%Y-%m-%d')
    meta = {'source': 'Binance USD-M BTCUSDT 1m klines + metrics 5m OI', 'range': [first, last], 'events': len(evs),
            'window_min': WIN, 'flat': FLAT, 'note': 'DEV window, fee-free descriptive; OURS thresholds in study.py'}
    os.makedirs(os.path.dirname(OUT_JS), exist_ok=True)
    with open(OUT_JS, 'w', newline='\n') as fh:
        fh.write('// built by research/anticipation_map_2026-11-05/study.py; do not edit\n')
        fh.write('var ANTICIPATION_RATES = ' + json.dumps({'meta': meta, 'rates': rates}, sort_keys=True) + ';\n')
    tot = sum(reg.values())
    print('events', len(evs), first, last, 'states', json.dumps(states, sort_keys=True))
    print('Regime mix: bull %d%% / bear %d%% / range %d%%' % tuple(round(100 * reg[x] / tot) for x in ('bull', 'bear', 'range')))
    print('| State price/OI/delta | n | share of state | price continues next 60m | move undone next 60m | OI keeps its sign next 60m |')
    for k in sorted(rates):
        r = rates[k]
        print('| %s | %d | %d%% | %d%% | %d%% | %d%% |' % (k, r['n'], r['share'], r['cont'], r['kill'], r['oiCont']))


if __name__ == '__main__':
    main()
