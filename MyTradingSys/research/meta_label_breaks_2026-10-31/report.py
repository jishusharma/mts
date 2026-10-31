"""dev.json -> markdown tables on stdout. Usage: python report.py [out_dir] > output.md"""
import json
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else 'F:/MTS/runs/meta_label_breaks'
R = json.load(open(os.path.join(OUT, 'dev.json')))


def f(x, d=3):
    return 'na' if x is None else f'{x:.{d}f}'


print(f"Round trip cost {f(R['rt_pct'], 2)} %. Net = mean % per trade after that cost. CI = week-block 95 %.\n")
print('## Meta-label: does the model\'s best third beat the rest? (DEV, out-of-fold, 6 purged blocks)')
print('| TF | trades | all net | top third n | top gross | top net | top CI | middle net | bottom net | lift | placebo p | Holm p | top net 2022 / 2023-24 | lift detectable | verdict |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for tf, c in R['meta'].items():
    print(f"| {tf} | {c['n_all']} | {f(c['all']['net'])} | {c['top']['n']} | {f(c['top']['gross'])} | {f(c['top']['net'])} | [{f(c['top']['lo'])}, {f(c['top']['hi'])}] | "
          f"{f(c['mid']['net'])} | {f(c['bottom']['net'])} | {f(c['lift'])} | {f(c['placebo_p'])} | {f(c['holm_p'])} | {f(c['top_net_2022'])} ({c['n_top_2022']}) / {f(c['top_net_2023'])} ({c['n_top_2023']}) | "
          f"{f(c['detectable_lift'])} | {c['verdict']} |")
print('\n## Early exit: get out at the close of bar k if not in profit, else hold 4 bars (DEV, all trades)')
print('| TF | k | trades | hold net | early-exit net | early CI | difference | diff CI | diff 2022 / 2023-24 | share exited | winners under water at k | losers under water at k | verdict |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for tf, ec in R['early'].items():
    for k, e in ec.items():
        print(f"| {tf} | {k[1]} | {e['n']} | {f(e['hold_net'])} | {f(e['early_net'])} | [{f(e['early_lo'])}, {f(e['early_hi'])}] | {f(e['diff'])} | [{f(e['diff_lo'])}, {f(e['diff_hi'])}] | "
              f"{f(e['diff_2022'])} / {f(e['diff_2023'])} | {100 * e['exited_share']:.0f} % | {100 * e['winners_underwater']:.0f} % | {100 * e['losers_underwater']:.0f} % | {e['verdict']} |")
print('\n## Per feature (descriptive, no verdict): net % per trade in the DEV thirds of the feature; winners vs losers median')
print('| TF | feature | winners median | losers median | low third | middle third | high third |')
print('|---|---|---|---|---|---|---|')
for tf, fd in R['features'].items():
    for k, v in fd.items():
        cells = [f"{f(t['net'])} ({t['n']})" for t in v['thirds']]
        cells += [''] * (3 - len(cells))
        print(f"| {tf} | {k} | {f(v['win_median'])} | {f(v['loss_median'])} | {' | '.join(cells)} |")
