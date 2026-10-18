# PRE_REG: 15m BB top-reversal short, DEV only (2026-10-18, card bb-top-reversal-candle-backtest)

Status: NOT FROZEN. Power gate failed (see BLOCKED.md). No outcome (PnL, MFE, MAE) was read; DEV only (2022-01-01..2024-06-30); VALIDATION/HOLDOUT not read.

## verdicts.py check "bollinger top reversal"
`check 'bollinger top reversal': no prior row matches (need 2 of ['bolli', 'rever', 'top']). Safe to pre-register; append your row after RESULT.`
(The shipped event-table trial, bb_top_reversal_event_table, is gross-excursion only, not a fee-net backtest.)

## Variants (12, would have been frozen)
E1 sell-stop at green open / E2 red close below green open, fill next open / E3 red close below green low, fill next open (all OURS) x S1 max(green, red high)+2 ticks / S2 red open+2 ticks (OURS) x exit 2R / middle band (OURS). BB(20,2) population sd (SOURCED: operator rule 2026-10-14, research/screenshots/2026-10-14_BTCUSDT_9fda889f1529.md; 24/7 candidates in bollinger_2026-10-14/SOURCES.md are a later variant). Cushion k=0 (OURS). Fees: taker both legs 0.0005 per side (fees.py DERIBIT_TAKER, SOURCED to exchange schedule).

## Count-only gate inputs (OURS, no PnL read)
- n = 759 distinct UTC days holding >=1 event (1,577 events, count_gate.py).
- sd = 1.5 R: upper bound of sd for a -1R/+2R outcome (max at p(win)=0.5: sqrt(.5*.5*9)=1.5); table rows not scored.
- cost = 0.001 / median stop-distance fraction 0.002863 (red high - next open, over entry) = 0.349 R.
- m = 46 (verdicts.py count --split DEV) + 12 = 58.

## Gate output
`n 759 sd 1.5 m 58 z_holm 3.332 MDE 0.227 R + cost 0.349 = 0.576 vs max plausible gross 0.3; n needed inf`
`BLOCK: do not freeze` (exit 1)
