"""Generate the report and register the diagnostic in the existing Session family."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
folder = Path(__file__).resolve().parent
d = json.loads((folder/'results.json').read_text())
lines = ['# Levels + staged position sizing: quick DEV probe', '',
         'RESULT (2026-10-14, JIS-NUC): all eight fixed variants lost after modeled costs. No deployment or validation run.', '',
         '120 complete UTC days (172,800 minute bars), 2024-12-02 through 2025-03-31. First day supplies levels only. 117 signal days: 50 long, 67 short. Each arm receives the same signals; 936 simulated campaigns are NOT 936 independent trades.', '',
         'Fixed reference equity $10,000; $50 initial planned risk per campaign; no compounding. Cost = 5bp fee + 1bp slippage each fill, plus a funding stress charge of 1bp per eight elapsed hours. Funding is a scenario, not historical funding. R = net dollars / $50. Drawdown uses closed campaigns, not intratrade equity.', '',
         '| Entry / exit | Trades | Mean net R | Net USD | Max closed-trade DD USD | Avg entries |',
         '|---|---:|---:|---:|---:|---:|']
for s in d['summary']:
    lines.append(f"| {s['arm']} | {s['n']} | {s['mean_r']:.3f} | {s['total_usd']:.2f} | {s['max_dd_usd']:.2f} | {s['mean_entries']:.2f} |")
lines += ['', '## What this means', '',
          'Single/full gross P&L before all modeled costs: +$66.81; net: -$1,262.71. Equal-dip/staged loses least (-$1,139.58), but its paired mean improvement is only about 0.021R with a day-bootstrap 95% interval [-0.049, +0.087]R. That includes no improvement. These are exploratory, unadjusted intervals across eight correlated trials, not significance claims; serial dependence can further weaken uncertainty estimates.', '',
          'Staging did not rescue this basic entry rule. This does not reject the full operator idea: higher-timeframe bias, RSI 40/60 and RSI-MA, current-session evolving profiles, independent level-family/random-line controls and conditional absorption are not implemented. This is a small position-management diagnostic alongside LC1–LC4; none of those cards is marked complete.', '',
          'Staged exit = half at first opposing level, quarter at second, remainder on adverse five-minute delta/opposite Bollinger band or day end. Adverse delta can close the remainder before target two. In single/staged, only 1 campaign reached target two; 31 reached target one and then used indicator exit. Therefore this sample chiefly tests one partial followed by an indicator exit, not a reliably filled three-exit ladder.', '',
          '## How to improve the leveraged design', '',
          'Treat 1:2:3 as capped tranche weights: 16.7%, 33.3%, 50% of planned quantity, with quantity derived from all entry-to-stop distances and costs. It is not repeated doubling after losses. Keep one campaign loss budget, freeze invalidation, cancel remaining adds when invalidated, and disallow new adds after distribution starts. Planned entries may never all fill.', '',
          'Next compare additions after a support reclaim with additions into falling price, conditioned on completed 1h/4h structure and delta behavior. Negative CVD plus a holding/rising price may indicate absorption; negative CVD alone is not a reason to hold a losing long. Record CVD slope and price response separately. For shorts reverse the interpretation. Define flat numerically on DEV before trying it.', '',
          'Select size from stop risk, then check margin separately. A displayed exchange leverage multiplier is not the risk budget. This probe caps reference-equity notional at 2x; actual maximum was about 1.29x. It does not model margin, liquidation, mark price, contract rounding or inverse BTC collateral. No claim that any chosen leverage is safe follows from it. Worst modeled campaign was -$52.10: funding/gaps mean a $50 planned stop budget is not a guaranteed loss ceiling.', '',
          '## Reproducibility and verification', '',
          'Run `python MyTradingSys/research/levels_sizing_2026-10-14/probe.py` then `python MyTradingSys/research/levels_sizing_2026-10-14/verify_probe.py`. Raw input paths and SHA-256 hashes, all fills, monthly results and all eight trials are in results.json. METHOD.md records choices before the run; no post-result parameter tuning was performed. April–June files were not opened. Five synthetic checks cover long/short arithmetic, stop/target ambiguity, gap stops, next-bar adds and volume-profile construction (long/short share the arithmetic check category); all 936 campaign cash-flow and inventory checks pass.', '',
          'All eight arms count toward the shared Tom/LC DEV research search. They must be included when assessing selection bias later, even though this probe selects no strategy. Only the footprint archive is used; no live account or order API is touched. Historical archive provenance relies on the repository orderflow_bars.py producer, not a fresh exchange-download audit.', '',
          '## Internet research (verified 2026-10-14)', '',
          '- CME, [Proper Position Size](https://www.cmegroup.com/education/courses/trade-and-risk-management/proper-position-size): size depends on stop distance and the allowed account loss. T2 educational mechanics, confidence high for definition, no BTC profitability evidence.',
          '- Charles Schwab, [How Traders Can Take Advantage of Volatile Markets](https://international.schwab.com/investing-education/how-traders-can-take-advantage-volatile-markets), July 23 2019: partial profit-taking while retaining exposure is a recognized exit method. T3 education, high confidence for definition, no tested edge supplied.',
          '- Deribit, [Fees](https://support.deribit.com/hc/en-us/articles/25944746248989-Fees) and [Liquidations](https://support.deribit.com/hc/en-us/articles/25944769313309-Liquidations): execution costs and maintenance-margin liquidation must be considered separately from stop sizing. T2 exchange mechanics; current schedules are not proof of historical costs. This probe uses explicit OURS cost assumptions.', '',
          'No validated evidence found in this limited source review that 1:2:3 scaling makes this BTC strategy profitable. Sources justify testing mechanics only.', '']
(folder/'REPORT.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
mp = root/'MyTradingSys/system/layer_map.json'
m = json.loads(mp.read_text(encoding='utf-8'))
m['backtests'] = [x for x in m['backtests'] if x['id'] != 'LC-SIZING-QUICK-20261014']
m['backtests'].append(dict(id='LC-SIZING-QUICK-20261014', title='Levels: eight staged sizing/exit diagnostics',
    date='2026-10-14', market='BTCUSDT footprint 1m', layers=['session_levels'],
    params='OURS: prior-day H/L/POC/VA, 4 entry arms x 2 exits; $50 campaign risk, 2x notional cap',
    split='DEV 2024-12-02..2025-03-31 only; no validation', fees='6bp each fill + funding stress 1bp/8h',
    interaction='Sizing and exit mechanics only; no HTF/RSI filter',
    effects='All eight negative; mean net R -0.216 to -0.195', n='117 paired signal days',
    verdict='EXPLORATORY NEGATIVE; full LC hypothesis untested',
    report='MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md', read='summary'))
m['asof'] = '2026-10-14'
mp.write_text(json.dumps(m, indent=1)+'\n', encoding='utf-8', newline='\n')
print('Saved REPORT.md and registered LC-SIZING-QUICK-20261014')
