"""11-09 census rows for the simulator page: one row per tested study with a colour verdict chip, n, mean net R and a one-line why,
read from the studies' own RESULT / cells / events / READING files. Writes results/_census_1109.json (the page's "11-09 census" tab).

Rules (card sim-desk-edge-hunt-census-1109): no new backtest and no number that is not already in a RESULT file; HOLDOUT never read; no prices
(percent distances and timestamps only, the repo is public). A study that saved no per-trade file says so on its row; it is NOT regenerated here.
The only trades with entry/stop/best-move are the operator's 5 Malkan points (READING.md): their 4h candles are fetched once from the public
Binance spot kline API, stored as percent from the entry, and never re-fetched by the tests.

  python MyTradingSys/research/sim_desk/census_1109.py        # fetch candles, write results/_census_1109.json
"""
import csv
import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
OUT = HERE / 'results' / '_census_1109.json'
EH = 'edge_hunt_2026-11-09/results'
CENSUS = 'census_5m_15m_session_ladder_2026-11-09/RESULT.md'
MALKAN = 'malkan_level_shorts_2026-11-09'
TONE = {'FAIL': 'bad', 'INCONCLUSIVE': 'warn', 'PASS': 'good'}
EXITS = ['B1R', 'NODE', 'NODE_BE', 'HALF_BE', 'TRAIL']


def _read(rel):
    return (RESEARCH / rel).read_text(encoding='utf-8')


def _csv(rel):
    with open(RESEARCH / rel, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def _no_file(script):
    return {'status': 'not_saved',
            'note': f'per-trade file not saved by this study (aggregate cells only). Not regenerated here: {script} needs the full DEV run and its '
                    'data cache outside the repo; a regeneration card is filed. No trade chart on this row.'}


# trial -> (study folder, script, why text, quote that must stand in the RESULT file). Numbers in `why` are from the cited files only.
def _trial_rows():
    rows = []
    cells = {
        'T04': next(r for r in _csv(f'{EH}/eh-h3-first-touch-sweep/cells.csv') if r['cut'].startswith('T04')),
        'T06': next(r for r in _csv(f'{EH}/eh-h5-rsi-ma-cross-trigger/cells.csv') if r['cell'].startswith('T06 pooled')),
        'T09': next(r for r in _csv(f'{EH}/eh-s2-wick-level-context/cells.csv') if r['trial'] == 'T09' and r['cell_kind'] == 'primary'),
        'T11': next(r for r in _csv(f'{EH}/eh-s3-rsi-line-confluence/cells.csv') if r['set'] == 'T11' and r['year'] == 'all'),
        'T12': next(r for r in _csv(f'{EH}/eh-s3-rsi-line-confluence/cells.csv') if r['set'] == 'T12' and r['year'] == 'all'),
    }
    g = lambda c, k: float(c[k])
    spec = [
        ('eh-h1-spinning-top-7star', 'T01', 'spinning_top.py', 'Mean net R is below zero and even the top of the 95 % range sits under the smallest effect this sample could detect (0.42 R).', 'DEV mean <= 0 and CI upper below MDE'),
        ('eh-h2-malkan-star-grades', 'T02', 'star_grades.py', 'Too few events: 7 trades in 5.75 years of daily BTC and ETH; +1.06 R with SE 1.01 cannot be told from luck.', 'Sample sizes: 7 and 8 trades over 5.75 years'),
        ('eh-h2-malkan-star-grades', 'T03', 'star_grades.py', 'Too few events: 8 trades; +0.07 R with SE 0.51 says nothing.', 'Sample sizes: 7 and 8 trades over 5.75 years'),
        ('eh-h3-first-touch-sweep', 'T04', 'first_touch.py', 'Costs ate the gross: gross %+.3f R, fees %.3f R per trade, net %+.3f R (cells.csv).' % (g(cells['T04'], 'gross'), g(cells['T04'], 'fee'), g(cells['T04'], 'mean')), 'upper bound below MDE 0.121'),
        ('eh-h4-speed-time-at-level', 'T05', 'speed_time.py', 'Mean net R below zero (-0.086, SE 0.081) and the CI top is under the 0.228 R detectable effect; the time filter barely bites (300 of 307 fast reclaim touches pass it).', 'mean <= 0 and CI upper below MDE'),
        ('eh-h5-rsi-ma-cross-trigger', 'T06', 'rsi_ma_cross.py', 'Not a fail, not a pass: gross %+.3f R minus fees %.3f R leaves +0.048 R, but the 95 %% CI (-0.029..+0.126) includes zero (cells.csv).' % (g(cells['T06'], 'mean_gross_r'), g(cells['T06'], 'mean_fee_r')), 'the CI includes 0'),
        ('eh-s2-wick-level-context', 'T09', 'wick_context.py', 'Gross R was already negative (%+.3f) and fees took another %.3f R; only 41 trades (cells.csv).' % (g(cells['T09'], 'mean_gross_r'), g(cells['T09'], 'mean_fee_r')), 'below the MDE 0.658'),
        ('eh-s2-wick-level-context', 'T10', 'wick_context.py', 'Mean net R -0.804 with the whole 95 % range below zero (-1.226..-0.382); 47 trades.', 'below the MDE 0.602'),
        ('eh-s3-rsi-line-confluence', 'T11', 'line_confluence.py', 'Costs ate the gross: gross %+.3f R vs fees %.3f R per trade (cells.csv), net -0.146 R.' % (g(cells['T11'], 'gross'), g(cells['T11'], 'fee_r')), 'T11: -0.064 < 0.117'),
        ('eh-s3-rsi-line-confluence', 'T12', 'line_confluence.py', 'Costs ate the gross: gross %+.3f R vs fees %.3f R per trade (cells.csv), net -0.133 R.' % (g(cells['T12'], 'gross'), g(cells['T12'], 'fee_r')), 'T12: -0.047 < 0.123'),
    ]
    for folder, trial, script, why, quote in spec:
        rel = f'{EH}/{folder}/RESULT.md'
        text = _read(rel)
        line = re.search(r'^Verdict: (.*)$', text, re.M).group(1)
        seg = re.search(trial + r'=(\w+) \((.*?)(?=\sT\d\d=|$)', line + ' ').group(0)
        chip = re.match(trial + r'=(\w+)', seg).group(1)
        n = int(re.search(r'\bn=(\d+)', seg).group(1))
        mean = float(re.search(r'(?:mean net R|net) ([+-]\d+\.\d+)', seg).group(1))
        row = {'id': f'{folder[:5]}-{trial}', 'study': folder, 'trial': trial, 'title': f'{trial} {folder[6:].replace("-", " ")}', 'chip': chip, 'tone': TONE[chip],
               'n': n, 'mean_net_r': mean, 'why': why, 'why_src': rel, 'why_quote': quote,
               'source_files': [rel], 'per_trade': _no_file(script), 'trades': []}
        rows.append(row)
    # eh-h2 saved events.csv (date, symbol, grade, net R only): a list, no entry/stop/target, so no candle chart
    ev = _csv(f'{EH}/eh-h2-malkan-star-grades/events.csv')
    for r in rows:
        if r['trial'] in ('T02', 'T03'):
            r['trades'] = [{'date': e['date'], 'symbol': e['symbol'], 'r': float(e['R'])} for e in ev if e['grade'] == r['trial']]
            r['per_trade'] = {'status': 'file', 'note': 'events.csv saves date, coin and net R only (no entry, stop or target), so the list has no candle chart.'}
            r['source_files'].append(f'{EH}/eh-h2-malkan-star-grades/events.csv')
    return rows


def _census_row():
    text = _read(CENSUS)
    cells = []
    for tf in ('5m', '15m'):
        i = text.index(f'### {tf} HEADLINE set (FEES_DERIBIT model D, net R)')
        line = next(l for l in text[i:].splitlines() if l.startswith('| headline'))
        for ex, (m, se, n) in zip(EXITS, re.findall(r'([+-]\d\.\d+)\+-(\d\.\d+) \(n=(\d+)\)', line)):
            cells.append({'tf': tf, 'exit': ex, 'mean_net_r': float(m), 'se': float(se), 'n': int(n)})
    head = cells[0]
    return {'id': 'census-5m-15m-session-ladder', 'study': 'census_5m_15m_session_ladder_2026-11-09', 'trial': 'census',
            'title': 'Tom/Fabio census, 5m and 15m, session x ladder x node targets (10 cells)', 'chip': 'FAIL', 'tone': 'bad',
            'n': head['n'], 'mean_net_r': head['mean_net_r'], 'headline': '5m B1R cell shown; all 10 cells in the table',
            'why': 'Costs ate the gross: gross R is about zero while fees on small 5m stops (median 28.6 bps) eat the trade, so all 10 cells are negative net.',
            'why_src': CENSUS, 'why_quote': 'gross R is about zero', 'source_files': [CENSUS], 'cells': cells,
            'per_trade': _no_file('census_session_ladder.py (about 25 min, 7-year mirror download, window beyond DEV)'), 'trades': []}


def _arm(text, label_start):
    ln = next(l for l in text.splitlines() if l.startswith('| ' + label_start))
    c = [x.strip().strip('*') for x in ln.strip('|').split('|')]
    return int(c[1]), float(c[5])


def _malkan_arms():
    rel = f'{MALKAN}/REPORT.md'
    text = _read(rel)
    out = []
    for rid, start, title, why, quote in [
            ('malkan-level-short-best-arm', '+ structure div 3-10 close', 'Malkan level short, best arm (divergence 3-10 bars, close to close)',
             'Not distinguishable from zero: +0.10 R is about 0.9 standard errors with 10 arms tried (126 trades).', 'about 0.9 standard errors from zero'),
            ('malkan-level-short-full-stack', 'FULL 5 layers', 'Malkan level short, full 5-layer stack',
             'Too few and not distinguishable from zero: 37 trades in 9 years, +0.13 R is about 0.6 SE.', 'about 0.6 SE')]:
        n, mean = _arm(text, start)
        out.append({'id': rid, 'study': 'malkan_level_shorts_2026-11-09', 'trial': 'count', 'title': title, 'chip': 'INCONCLUSIVE', 'tone': 'warn',
                    'n': n, 'mean_net_r': mean, 'why': why, 'why_src': rel, 'why_quote': quote, 'source_files': [rel],
                    'per_trade': {'status': 'not_saved', 'note': 'per-trade file not saved (COUNT.json holds per-arm totals only). Not regenerated here: count.py '
                                  'fetches BTC 4h spot 2017-2026, beyond DEV; a regeneration card is filed. No trade chart on this row.'}, 'trades': []})
    return out


# bar (UTC, 2026) where each operator trigger fired, from the RSI column of READING.md; the entry is the first bar from there that trades through the entry
ANCHOR = {'C1': '2026-08-28 04', 'C2': '2026-09-04 12', 'V1': '2026-09-23 04', 'V2': '2026-10-06 12', 'C3': '2026-10-22 00'}


def _parse_operator():
    rel = f'{MALKAN}/READING.md'
    out = []
    for ln in _read(rel).splitlines():
        c = [x.strip() for x in ln.strip().strip('|').split('|')]
        if len(c) == 7 and c[0] in ANCHOR:
            m = re.match(r'([\d,]+)(?: \([^)]*\))? / ([\d,]+) / -([\d.]+) % \(([\d.]+)R\)(?:, (stop hit [\d-]+))?', c[6])
            e, s = float(m.group(1).replace(',', '')), float(m.group(2).replace(',', ''))
            out.append({'name': c[0], 'side': 'short', 'bar': c[1], 'anchor': ANCHOR[c[0]], 'stop_pct': round((s - e) / e * 100, 3),
                        'best_pct': float(m.group(3)), 'best_r': float(m.group(4)),
                        'exit_note': m.group(5) or 'no exit stated in READING.md (the best move is how far it went, not an exit)',
                        'repo_rule': c[5], '_entry': e, '_stop': s})
    return out


def _operator_row():
    tr = _parse_operator()
    rel = f'{MALKAN}/READING.md'
    for t in tr:
        t.pop('_entry'), t.pop('_stop')
    return {'id': 'malkan-operator-5-points', 'study': 'malkan_level_shorts_2026-11-09', 'trial': 'operator', 'title': "Operator's 5 Malkan level shorts (82k-87k range, BTC 4h, 2026-08..10)",
            'chip': 'INCONCLUSIVE', 'tone': 'warn', 'n': len(tr), 'mean_net_r': None,
            'headline': 'hand-marked, no net R computed (READING.md gives the best move in R, not a net result)',
            'why': 'Not a test: 5 points picked in hindsight; all 5 reached 1R or more, only V1 fits the repo divergence rule, a pattern and not an edge.',
            'why_src': rel, 'why_quote': 'Hand-picked in hindsight', 'source_files': [rel],
            'per_trade': {'status': 'file', 'note': 'entry, stop and best move from the READING.md table (percent from the entry); 4h candles from the public Binance spot API. '
                          'Marked: entry, stop, best move (no target was set), exit only where READING.md states it (C1).'}, 'trades': tr}


def _check_next():
    spec = [
        ('Pooled or intraday version of the 5-star / 7-star MTF long (7 and 8 daily trades cannot test it).', f'{EH}/eh-h2-malkan-star-grades/RESULT.md', 'A pooled or intraday version would need a different trial'),
        ('Time-at-level as its own frozen trial: the descriptive time measure showed the sharper contrast than the frozen cell.', f'{EH}/eh-h4-speed-time-at-level/RESULT.md', 'The sharper contrast is the descriptive time measure'),
        ('Wick-sweep "effort" test with a stricter or relative volume measure (every weekly/monthly sweep is a high-volume bar).', f'{EH}/eh-s2-wick-level-context/RESULT.md', 'any "effort" test needs a stricter or relative measure'),
        ('RSI-line bounces gated by a different HTF bias (a trend or SMA side), not HTF RSI vs 50.', f'{EH}/eh-s3-rsi-line-confluence/RESULT.md', 'should use a different HTF measure'),
        ('Spinning-top 7-star with a different location window (the 20-bar window was frozen, other windows untested).', f'{EH}/eh-h1-spinning-top-7star/RESULT.md', 'A different window is untested by design'),
    ]
    return [{'idea': i, 'file': f, 'quote': q} for i, f, q in spec]


def build_rows():
    rows = [_census_row()] + _trial_rows() + _malkan_arms() + [_operator_row()]
    return {'rows': rows, 'check_next': _check_next(),
            'notes': ['eh-f1 DESIGN.md is not in the tree (only the worker brief workers/eh-f1-testnet-design.txt), so no idea comes from it.',
                      'eh-o1 and eh-o2 are not shipped (no RESULT file), so they have no row.',
                      'Chips: FAIL red, INCONCLUSIVE amber, PASS green, as written in each RESULT verdict line; census FAIL and Malkan INCONCLUSIVE are our reading of the prose (OURS).']}


def _fetch_4h(start='2026-08-10'):
    ms = int(dt.datetime.fromisoformat(start).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    url = f'https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=4h&limit=1000&startTime={ms}'
    return [[int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4])] for r in json.load(urllib.request.urlopen(url, timeout=30))]


def with_candles(d, prev=None, bars=None):
    """Add candles (percent from the entry), entry_i, exit_i, exit_t to the 5 operator trades. prev = an earlier built file whose candle fields are reused (offline)."""
    row = next(r for r in d['rows'] if r['id'] == 'malkan-operator-5-points')
    if prev is not None:
        old = {t['name']: t for r in prev['rows'] if r['id'] == row['id'] for t in r['trades']}
        for t in row['trades']:
            t.update({k: old[t['name']][k] for k in ('t0', 'c', 'entry_i', 'exit_i', 'exit_t')})
        return d
    bars = bars or _fetch_4h()
    tm = [dt.datetime.fromtimestamp(b[0] / 1000, dt.timezone.utc) for b in bars]
    for t, p in zip(row['trades'], _parse_operator()):
        e, s = p['_entry'], p['_stop']
        a = next(i for i, x in enumerate(tm) if x.strftime('%Y-%m-%d %H') == p['anchor'])
        ei = next((i for i in range(a, a + 12) if bars[i][3] <= e), a)
        xi = None
        if t['exit_note'].startswith('stop hit'):
            xi = next((i for i in range(ei, min(len(bars), ei + 60)) if bars[i][2] >= s), None)
        i0, i1 = max(0, ei - 20), min(len(bars), max(ei + 31, (xi or 0) + 6))
        t['t0'] = tm[i0].strftime('%Y-%m-%dT%H:%MZ')
        t['c'] = [[round((x - e) / e * 100, 3) for x in b[1:5]] for b in bars[i0:i1]]
        t['entry_i'] = ei - i0
        t['exit_i'], t['exit_t'] = (None, None) if xi is None else (xi - i0, tm[xi].strftime('%Y-%m-%dT%H:%MZ'))
    return d


def main():
    d = with_candles(build_rows())
    OUT.write_text(json.dumps(d, indent=0, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print(OUT, len(d['rows']), 'rows')


if __name__ == '__main__':
    sys.exit(main())
