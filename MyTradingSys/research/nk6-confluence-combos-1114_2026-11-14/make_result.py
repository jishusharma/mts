import json, itertools
r = json.load(open('results.json')); res = r['res']; mix = r['mix']; td = r['today']
f = lambda x, d=3: '-' if x is None else f'{x:.{d}f}'
P = lambda c, k='prim', fee='12bp': res[f'{c}|{k}|{fee}']
passed = [k.split('|')[0] for k, s in res.items() if '|prim|12bp' in k and s.get('pass')]
best = max((k.split('|')[0] for k in res if k.endswith('|prim|12bp')), key=lambda c: P(c)['mean'])
bg = max((k.split('|')[0] for k in res if k.endswith('|prim|12bp')), key=lambda c: P(c)['gross_mean'])
L = []
L.append(f"VERDICT: {'PASS: ' + ', '.join(passed) if passed else 'FAIL - no combination passes (all 33 combos negative net of 12 bp on VALIDATION; best net ' + best + ' ' + f(P(best)['mean']) + 'R)'}")
L.append("")
L.append("Study nk6-confluence-combos-1114: five NK layers as 15m booleans, agreement counted in the phase direction, every single/pair/triple + count buckets, 20 Binance spot coins, DEV <= 2023-12-31, VALIDATION >= 2024-01-01. PRE_REG.md committed before any outcome (sha cc7de58ca). Trade: entry next open, stop max(1 ATR, 0.5%), target 2R, 24-bar time exit, fee 12 bp taker primary.")
L.append("")
L.append("## Context")
L.append("Phase for each UTC day from the prior daily close: UP = ADX(14)>=20, +DI>-DI, SMA20 rising 5d; DOWN = mirror; else RANGE. Primary rows trade only the phase-matched direction (RANGE = both). Control rows (opposite direction in UP/DOWN) are shown for comparison only.")
tot = lambda m: sum(m)
def sh(m): t = tot(m); return f"UP {m[0]/t*100:.0f}% / RANGE {m[1]/t*100:.0f}% / DOWN {m[2]/t*100:.0f}%"
L.append("")
L.append(f"Regime mix: DEV bars (all coins): {sh(mix['DEV'])}. VAL bars: {sh(mix['VAL'])}.")
vs = P('n>=4')['val_phase_share']; v1 = P('n=1')['val_phase_share']
L.append(f"Phase of VAL trades: n=1 UP {v1[0]*100:.0f}% / RANGE {v1[1]*100:.0f}% / DOWN {v1[2]*100:.0f}%; n>=4 UP {vs[0]*100:.0f}% / RANGE {vs[1]*100:.0f}% / DOWN {vs[2]*100:.0f}%.")
L.append("")
L.append("## Matched-row table (VALIDATION, 12 bp taker, phase-matched)")
L.append("Fee col = mean fee as a fraction of R. Gross = mean R before fees. BH q over 66 primary rows (33 combos x 12/6 bp). Pass = all gates.")
L.append("")
L.append("| combo | n DEV | n VAL | win % | mean net R | gross R | fee/R | CI lo trade | CI lo day | placebo p | BH q | ex-best-5 | 6 bp mean | control mean | pass |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for k in [k for k in res if k.endswith('|prim|12bp')]:
    c = k.split('|')[0]; s = P(c); s6 = P(c, 'prim', '6bp'); ct = P(c, 'ctl')
    L.append(f"| {c} | {s['dev_n']} | {s['n']} | {s['win']*100:.1f} | {f(s['mean'])} | {f(s['gross_mean'])} | {f(s['fee_R'],2)} | {f(s['ci_trade_lo'])} | {f(s['ci_day_lo'])} | {f(s['placebo_p'])} | {f(s['bh_q'])} | {f(s['ex_best5'])} | {f(s6['mean'])} | {f(ct['mean'])} | {'PASS' if s['pass'] else 'no'} |")
L.append("")
L.append("## Heat table: mean net R (12 bp, VALIDATION). Diagonal = single layer, off-diagonal = pair")
L.append("")
L.append("| | L1 | L2 | L3 | L4 | L5 |")
L.append("|---|---|---|---|---|---|")
for a in range(1, 6):
    row = []
    for b in range(1, 6):
        c = f"L{a}" if a == b else f"L{min(a,b)}&L{max(a,b)}"
        row.append(f(P(c)['mean']))
    L.append(f"| L{a} | " + " | ".join(row) + " |")
L.append("")
L.append("Triples (mean net R / gross R): " + "; ".join(f"{c} {f(P(c)['mean'])}/{f(P(c)['gross_mean'])}" for c in [k.split('|')[0] for k in res if k.endswith('|prim|12bp')] if c.count('&') == 2))
L.append("")
L.append("Count buckets (mean net R, n VAL): " + "; ".join(f"{c} {f(P(c)['mean'])} (n={P(c)['n']})" for c in ["n=1", "n=2", "n=3", "n>=4", "n=1+VWAP", "n=2+VWAP", "n=3+VWAP", "n>=4+VWAP"]))
L.append("")
L.append("## Reading")
L.append(f"- Fees are about 0.20R per trade (stop floor 0.5% of price); at a 2R target the break-even win rate on a gross-zero edge is above 33% only after fees. Win rate is 33-38% in every row, i.e. the layers alone move the gross edge by at most {f(P(bg)['gross_mean'])}R ({bg}).")
L.append(f"- Gross R rises slightly with agreement (n=1 {f(P('n=1')['gross_mean'])}, n=2 {f(P('n=2')['gross_mean'])}, n=3 {f(P('n=3')['gross_mean'])}, n>=4 {f(P('n>=4')['gross_mean'])}) but never covers the fee: best net row is {best} at {f(P(best)['mean'])}R; at 6 bp best is still negative.")
L.append("- Several rows show placebo p < 0.05 (e.g. L1&L4, L2&L3&L5, n=3+VWAP), meaning they beat random phase-matched entries, but random entries are themselves -0.20R net, so beating placebo is not an edge. None clears mean>0, CI, BH or ex-best-5.")
L.append("- Phase-matched rows are no better than control (opposite-direction) rows in DEV or VAL: phase direction adds nothing measurable here on 15m entries.")
L.append("- 6 bp maker row assumes every limit fills (optimistic) and is still negative everywhere.")
L.append("")
L.append("## BTC today (descriptive only)")
L.append(f"- Data to {td['last_bar_utc']} UTC (partial 2026-11-13 day), close {td['close']:.0f}, session VWAP {td['vwap']:.0f} (price below).")
L.append(f"- Phase label for 2026-11-14: {td['phase_label']} (ADX {td['adx']:.1f}, +DI {td['pdi']:.1f}, -DI {td['mdi']:.1f}, SMA20 {td['sma20']:.0f}). Daily phase counts 11-13 as the closed day only in labelling for 11-14.")
pv = td['pivots_from_last_day']; h, l, c = td['yday_hlc']
L.append(f"- 11-13 H/L/C {h:.0f} / {l:.0f} / {c:.0f}; standard pivots for 11-14: P {pv['P']:.0f}, R1 {pv['R1']:.0f}, S1 {pv['S1']:.0f}. Price is under P, above S1.")
L.append(f"- Layers active on the last bar: none (long {td['active_long']}, short {td['active_short']}). A DOWN-phase setup would need shorts on a rejection at P / R1 or first-hour reclaim down; nothing here tested to pay after fees.")
L.append("")
L.append("## Parameters")
L.append("SOURCED: RSI 30/70 re-cross, standard pivots P/S1/R1, breakout-retest-fakeout concept, Hilega state meaning (red under green = buy). OURS: first-hour = UTC 00:00-01:00, K=4 window, RSI9/EMA3/WMA21, 20-bar breakout window, 6-bar retest window, ADX 20/SMA20 phase, stop/target/time exit, fees, placebo design.")
L.append("")
L.append("Files: study.py, run_nk6.py, make_result.py, test_study.py (causality test passes on real code, fails under STUDY_BUG=1), fetch.py, results.json. Data: F:\MTS\data_cache\binance_spot (note: sibling workers share this cache and overwrite files with key `t`; study.load accepts both).")
open('RESULT.md', 'w').write("\n".join(L) + "\n")
