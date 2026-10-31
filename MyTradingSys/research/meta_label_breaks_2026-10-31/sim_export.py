"""dev.json -> sim_desk/results/meta-label-breaks.json (schema: sim_desk/DESIGN.md "Result files").

Tables only: no per-trade chart data was saved, so examples are the meta-label, early-exit and 1h feature tables plus
`none` (DESIGN.md: never invent examples). Percent per trade only, no prices.
Usage: python sim_export.py [run_dir] [results_dir]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RID = 'meta-label-breaks'
FEAT_PLAIN = {
    'bbwp': 'BBWP on the trade timeframe', 'bbwp_4h': 'BBWP on 4h', 'trend_d': 'daily trend with the trade (close vs SMA200)',
    'rsi_e': 'RSI(14) at entry', 'flow_e': 'taker flow with the trade, last 5 bars', 'relvol_e': 'relative volume (hour of week)',
    'dist_atr': 'distance to the level in ATR', 'move_e': 'move from the break to entry', 'rv': 'realised volatility',
    's_eu': 'Europe session (1 = yes)', 's_us': 'US session (1 = yes)', 's_late': 'late session (1 = yes)',
    'c_R': 'reclaim trade (1 = yes)', 'c_W1': 'wick-sweep fade (1 = yes)', 'hi_side': 'break of a high (1 = yes)',
}


def f(x, d=3):
    return 'na' if x is None else f'{x:+.{d}f}'


def doc(R):
    meta, early = R['meta'], R['early']
    mrows = [[tf, str(c['n_all']), f(c['all']['net']), str(c['top']['n']), f(c['top']['net']),
              f"{f(c['top']['lo'])}..{f(c['top']['hi'])}", f(c['bottom']['net']), f"{c['placebo_p']:.3f}", f"{c['holm_p']:.3f}", c['verdict']]
             for tf, c in meta.items()]
    erows = [[tf, k[1], f(e['hold_net']), f(e['early_net']), f(e['diff']), f"{f(e['diff_lo'])}..{f(e['diff_hi'])}",
              f"{100 * e['winners_underwater']:.0f} %", f"{100 * e['losers_underwater']:.0f} %", e['verdict']]
             for tf, ec in early.items() for k, e in ec.items()]
    frows = []
    for k, v in R['features'].get('1h', {}).items():
        cells = [f"{f(t['net'])} ({t['n']})" for t in v['thirds']] + [''] * (3 - len(v['thirds']))
        frows.append([FEAT_PLAIN.get(k, k)] + cells)
    verdicts = {c['verdict'] for c in meta.values()}
    label = 'PASS' if 'PASS' in verdicts else ('INCONCLUSIVE' if 'INCONCLUSIVE' in verdicts else 'FAIL')
    h1 = meta.get('1h')
    why = [f"{tf}: best third {f(c['top']['net'])} % per trade after fees, placebo p {c['placebo_p']:.3f}, Holm p {c['holm_p']:.3f} -> {c['verdict']}"
           for tf, c in meta.items()]
    why.append('Early exit: every difference CI includes zero. After one bar about 28 % of eventual winners are still under water '
               'and about 65 % of losers, so "not in profit yet" cuts winners almost as often as losers.')
    if h1:
        why.append(f"1h lead: best third positive in both halves ({f(h1['top_net_2022'])} / {f(h1['top_net_2023'])} %); "
                   f"next check is 2019-2021 data never seen (card meta-label-1h-dev-ext-check).")
    rt = R['rt_pct']
    return {
        'id': RID, 'kind': 'backtest', 'parity': None, 'family': 'Meta-label (layer filter)',
        'title': 'Meta-label + early exit on timeframe-break trades: can other layers pick the winners, and does getting out early help?',
        'what': [
            {'name': 'Trades', 'value_plain': 'tf_break events (break of a prior-period high/low; classes H follow, R reclaim, W1 wick-sweep fade), '
             'BTCUSDT 15m / 1h / 4h, entry at the open of the bar after the signal, exit at the close 4 bars later', 'label': 'OURS'},
            {'name': 'Costs', 'value_plain': f'{rt:.2f} % round trip (taker both legs), no slippage, no funding', 'label': 'OURS'},
            {'name': 'Filter', 'value_plain': 'logistic score (L2 1.0) from 15 readings at entry: BBWP (basis 7, lookback 100) on the trade TF and 4h, '
             'daily trend, RSI, taker flow, relative volume, distance to level, move since break, realised vol, session, setup class', 'label': 'OURS'},
            {'name': 'BBWP settings', 'value_plain': 'basis 7, lookback 100 (Krown, KR-Q01)', 'label': 'SOURCED'},
            {'name': 'Early exit', 'value_plain': 'exit at the close of bar 1 or 2 if not in profit, else hold the 4 bars', 'label': 'OURS'},
        ],
        'how': 'Scored every trade out of fold (6 purged time blocks, 7-day purge, score cut from the training fold), compared the best third with all '
               'trades; 200 label shuffles as placebo, Holm over 3 timeframes, week-block bootstrap CI. Rules frozen in PRE_REG.md before any result.',
        'window': 'DEV only, 2022-01 to 2024-06 (trades before about 2022-07-19 dropped: daily SMA200 warm-up); VALIDATION and HOLDOUT not read',
        'verdict': {'label': label, 'tone': 'good' if label == 'PASS' else ('warn' if label == 'INCONCLUSIVE' else 'bad')},
        'why': why,
        'kpis': [{'label': f'{tf} trades', 'value': str(c['n_all'])} for tf, c in meta.items()]
        + ([{'label': '1h best third, net % per trade', 'value': f(h1['top']['net']), 'tone': 'warn'}] if h1 else []),
        'examples': [
            {'kind': 'table', 'title': 'Filter: does the best third by score beat the rest? (net % per trade after fees)',
             'caption': 'CI = week-block 95 %; placebo p = share of label shuffles doing as well; Holm over 3 timeframes',
             'cols': ['TF', 'trades', 'all net', 'best third n', 'best third net', 'best third CI', 'worst third net', 'placebo p', 'Holm p', 'verdict'],
             'rows': mrows},
            {'kind': 'table', 'title': 'Early exit: get out at bar k if not in profit vs hold 4 bars (all trades, net % per trade)',
             'caption': 'under water at k = share of eventual winners / losers below entry at the close of bar k',
             'cols': ['TF', 'k', 'hold net', 'early-exit net', 'difference', 'difference CI', 'winners under water', 'losers under water', 'verdict'],
             'rows': erows},
            {'kind': 'table', 'title': '1h: net % per trade by each reading\'s DEV thirds (descriptive, not a test; 0/1 readings show value 0 / value 1)',
             'caption': 'each reading is one cut of 15 on the same trades: a lead to test, not a rule',
             'cols': ['reading at entry', 'low third (n)', 'middle third (n)', 'high third (n)'], 'rows': frows},
            {'kind': 'none', 'title': 'Examples', 'caption': 'no example trades exported (per-trade chart data was not saved)'},
        ],
        'source_files': ['MyTradingSys/research/meta_label_breaks_2026-10-31/PRE_REG.md', 'MyTradingSys/research/meta_label_breaks_2026-10-31/meta.py',
                         'MyTradingSys/research/meta_label_breaks_2026-10-31/RESULT.md'],
        'commit': 'c6a6bb3b',
    }


def catalogue_row(d):
    v = d['verdict']['label']
    return {'id': RID, 'family': d['family'], 'title': d['title'], 'kind': 'backtest', 'kind_source': 'result file', 'verdict': v,
            'source': f'MyTradingSys/research/sim_desk/results/{RID}.json', 'exported': True, 'result_id': RID, 'date': '2026-10-31',
            'status': 'FAILED' if v == 'FAIL' else 'SEE_VERDICT', 'verdict_class': {'PASS': 'passed', 'FAIL': 'failed'}.get(v, 'unclear')}


def main(run_dir, results_dir):
    R = json.load(open(os.path.join(run_dir, 'dev.json'), encoding='utf-8'))
    d = doc(R)
    with open(os.path.join(results_dir, f'{RID}.json'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps(d, indent=1, ensure_ascii=False) + '\n')
    cp = os.path.join(results_dir, '_catalogue.json')
    cat = json.load(open(cp, encoding='utf-8'))
    cat['rows'] = [x for x in cat['rows'] if x['id'] != RID] + [catalogue_row(d)]
    cat['rows'].sort(key=lambda x: (not x['exported'], x['family'].lower(), x['title'].lower()))
    cat['count'], cat['exported'] = len(cat['rows']), sum(1 for x in cat['rows'] if x['exported'])
    with open(cp, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps(cat, indent=0, ensure_ascii=False) + '\n')
    return d


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'F:/MTS/runs/meta_label_breaks',
         sys.argv[2] if len(sys.argv) > 2 else os.path.normpath(os.path.join(HERE, '..', 'sim_desk', 'results')))
