"""explore_div_output.md + confirm_div.json -> sim_desk/results/malkan-div-breaks.json (schema: sim_desk/DESIGN.md "Result files").

Tables only (no per-trade chart data saved), so the last example is `none`. Percent per trade only, no prices.
Usage: python sim_export_div.py [run_dir] [results_dir]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim_export as SE  # noqa: E402

RID = 'malkan-div-breaks'
LEAD = ('RSI prd, lower TF', 'RSI nrd, lower TF')


def parse_explore(text):
    """-> (exit rows [TF, exit, trades, net, CI, win, PF, no_top5, bars], entry rows of the lead cells [TF, kind, n, with, without])."""
    exits, entry, tf, part = [], [], None, None
    for line in text.splitlines():
        if line.startswith('## '):
            tf, part = line.split()[1], 'exit'
        elif line.startswith('At entry'):
            part = 'entry'
        elif line.startswith('| ') and not line.startswith('| exit') and not line.startswith('| divergence'):
            c = [x.strip() for x in line.strip('|').split('|')]
            if part == 'exit':
                exits.append([tf] + c)
            elif part == 'entry' and c[0] in LEAD and c[1] == 'with':
                entry.append([tf, 'PRD (longs)' if 'prd' in c[0] else 'NRD (shorts)', c[5], c[4], c[6]])
    return exits, entry


def doc(text, C):
    exits, entry = parse_explore(text)
    f = SE.f
    crow = [[tf, str(c['n']), f(c['net']), f"{f(c['lo'])}..{f(c['hi'])}", 'na' if c['holm'] is None else f"{c['holm']:.2f}",
             f(C['extra'][tf]['not_flag_net']), c['verdict']] for tf, c in C['cells'].items()]
    xrow = [[tf, f"{f(e['long_net'])} ({e['long_n']})", f"{f(e['short_net'])} ({e['short_n']})",
             f"{f(e['y2020_net'])} ({e['y2020_n']})", f"{f(e['y2021_net'])} ({e['y2021_n']})", f(e['all_net'])]
            for tf, e in C['extra'].items()]
    label = C['card']
    why = [f"2020-2021 (never seen): {tf} flagged trades {f(c['net'])} % per trade (n {c['n']}), Holm p "
           f"{'na' if c['holm'] is None else format(c['holm'], '.2f')} -> {c['verdict']}" for tf, c in C['cells'].items()]
    why += ['Flagged trades did no better than the rest on 2020-2021; the DEV lead (best of about 66 cells) was chance.',
            'Exit on a divergence against the trade (DEV): no better than simply holding longer at any timeframe.']
    return {
        'id': RID, 'kind': 'backtest', 'parity': None, 'family': 'RSI divergence (Malkan)',
        'title': 'Malkan divergence on timeframe-break trades: exit on divergence, and reverse divergence (PRD/NRD) on the lower TF as an entry filter',
        'what': [
            {'name': 'Trades', 'value_plain': 'tf_break events, BTCUSDT 15m / 1h / 4h, entry at the next open, fixed exit 4 bars later '
             '(exit study: held to the first divergence against the trade, max 24 / 24 / 12 bars)', 'label': 'OURS'},
            {'name': 'Divergence detector', 'value_plain': 'regular 3-10 bars; reverse (PRD / NRD) 5-14 bars with RSI >= 60 / <= 40', 'label': 'SOURCED'},
            {'name': 'Lower timeframe', 'value_plain': '15m -> 5m, 1h -> 15m, 4h -> 1h', 'label': 'OURS'},
            {'name': 'Entry filter', 'value_plain': 'reverse divergence WITH the trade (PRD long, NRD short) on the lower TF known in the last 10 bars',
             'label': 'OURS'},
            {'name': 'CVD divergence', 'value_plain': 'cumulative taker delta in place of RSI (regular kinds only)', 'label': 'OURS'},
            {'name': 'Costs', 'value_plain': '0.10 % round trip (taker both legs), no slippage, no funding', 'label': 'OURS'},
        ],
        'how': 'Step 1, exploratory on DEV 2022-01..2024-06: every divergence kind x source x timeframe, at entry and as exit (about 66 cells). '
               'Step 2: the one consistent cell frozen in PRE_REG_DIV.md and run once on 2020-2021, week-block bootstrap, Holm over 3 timeframes.',
        'window': 'DEV 2022-01..2024-06 (exploratory); fresh check 2020-01..2021-12; VALIDATION and HOLDOUT not read',
        'verdict': {'label': label, 'tone': 'good' if label == 'PASS' else ('warn' if label == 'INCONCLUSIVE' else 'bad')},
        'why': why,
        'kpis': [{'label': f'{tf} 2020-21 flagged net %', 'value': f(c['net']), 'tone': 'bad' if c['net'] <= 0 else 'good'}
                 for tf, c in C['cells'].items()],
        'examples': [
            {'kind': 'table', 'title': 'Fresh check 2020-2021: trades with a lower-TF reverse divergence with the trade (net % per trade after fees)',
             'caption': 'rule frozen before the data was read; CI = week-block 95 %; Holm over 3 timeframes',
             'cols': ['TF', 'flagged trades', 'net', 'CI', 'Holm p', 'not flagged net', 'verdict'], 'rows': crow},
            {'kind': 'table', 'title': '2020-2021 split, descriptive (net % per trade, n)',
             'caption': 'not a test: shown so the side and year spread is visible',
             'cols': ['TF', 'longs with PRD', 'shorts with NRD', '2020', '2021', 'all trades'], 'rows': xrow},
            {'kind': 'table', 'title': 'DEV (exploratory): the lead cell that was tested (net % per trade)',
             'caption': 'best-looking of about 66 cells, so a big number was expected by chance',
             'cols': ['TF', 'divergence', 'n with', 'net with', 'net without'], 'rows': entry},
            {'kind': 'table', 'title': 'DEV (exploratory): exit on the first divergence against the trade vs fixed holds',
             'caption': 'net % per trade after fees; CI = week-block 95 %',
             'cols': ['TF', 'exit', 'trades', 'net', 'CI', 'win %', 'PF', 'net without best 5 %', 'median bars held'], 'rows': exits},
            {'kind': 'none', 'title': 'Examples', 'caption': 'no example trades exported (per-trade chart data was not saved)'},
        ],
        'source_files': ['MyTradingSys/research/meta_label_breaks_2026-10-31/PRE_REG_DIV.md',
                         'MyTradingSys/research/meta_label_breaks_2026-10-31/explore_div.py',
                         'MyTradingSys/research/meta_label_breaks_2026-10-31/confirm_div.py',
                         'MyTradingSys/research/meta_label_breaks_2026-10-31/RESULT.md'],
        'commit': '2203ad50',
    }


def main(run_dir, results_dir):
    text = open(os.path.join(HERE, 'explore_div_output.md'), encoding='utf-8').read()
    C = json.load(open(os.path.join(run_dir, 'confirm_div.json'), encoding='utf-8'))
    d = doc(text, C)
    with open(os.path.join(results_dir, f'{RID}.json'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps(d, indent=1, ensure_ascii=False) + '\n')
    return d


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'F:/MTS/runs/meta_label_breaks',
         sys.argv[2] if len(sys.argv) > 2 else os.path.normpath(os.path.join(HERE, '..', 'sim_desk', 'results')))
