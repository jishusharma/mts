# Layer-combination verdict: can any combination of layers trade profitably? (2026-10-13, cloud, read-only)

Session: MTS-2026-10-13-1440Z-CLD-ANA-layer-combo. Base: origin/fast-track ea87a005. No code, card or live-path change.
Operator ask: can any combination of any layers make consistently profitable trades, and can it be checked quickly?

## Answer
**No.** It has already been checked, and the check is quick to repeat (section 3, seconds, T0). The Q33 matrix is the
"any combination" test: 7 triggers x context filters up to 2 deep, 336 cells, 186 with n >= 300, **0 survivors**, smallest
q 0.62 (tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md). Stacking filters only picks subsets of events; when every subset has
about zero gross edge, the best stack is the best-of-N draw, not an edge. More stacking means smaller n and more trials.

## 1. The arithmetic (recomputed here from MATRIX_CELLS.csv, 186 tested cells)
| horizon | best gross of 186 | cell (n) | taker round trip | maker-in / taker-out |
|---|---|---|---|---|
| 15 min | +0.043 % | T1_cont long F7=1 (495) | 0.10 % | 0.05 % |
| 60 min (primary) | +0.058 % | T3_hold short F1=1&F3=1 (393) | 0.10 % | 0.05 % |
| 240 min | +0.139 % | T3b_through short F1=1&F3=0 (425) | 0.10 % | 0.05 % |
Costs: fees.py:23-24 (DERIBIT_TAKER 0.0005, DERIBIT_MAKER 0.0). Median gross across cells at 60 min: +0.0003 %.
Even the selected maximum at the primary horizon does not cover a taker round trip. The 240-min maximum is a best-of-186
pick at a non-primary horizon, not significant (report: q 0.62) and not stable across halves; a maker entry also has
adverse selection that a fixed-horizon study does not model. None of these is a lead.

## 2. Every other line of evidence agrees (latest per layer)
| Layer / study | Result | Where |
|---|---|---|
| Tom v2 family A (fade, DAX home market) | DESIGN FAIL today: recall 2 of 5 at best k; DAX dev run not started, holdout sealed | tom_transfer_2026-10-11/RECALL_DAX_V2.md |
| Fabio v3 | holdout never read; no positive DEV verdict on record | P2_FABIO_V3_HOLDOUT_STATUS.md |
| 62 published BTC rules (TSMOM, SMA, Donchian, RSI2, calendar) | 0 survive DEV; best TSMOM 30 d p 0.119, q 0.63 | published_strats_2026-10-13/RESULTS.md |
| Exits (MFE study) | setups have the same MFE/MAE as random entries; no causal exit beats a time exit | mfe_exit_2026-10-13/REPORT.md |
| RSI, CryptoCred, positioning, session, ToC, session levels | none meets S3 (walk-forward OOS net > 0 with CI above zero) | non_core_layer_audit_2026-10-12/REPORT.md |
| Daily SMA200 long-flat (alpha) | NO-SOURCE; CAGR 20.5 % vs buy-and-hold 43.8 % (lower drawdown only) | setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md |

## 3. Quick re-check (T0, seconds; rerun on any new matrix output)
```
python - <<'P'
import csv; COST=0.001  # FEES_ALL_TAKER round trip; use 0.0005 for maker-in/taker-out
r=[x for x in csv.DictReader(open('MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_CELLS.csv')) if x['status']=='tested']
for k in ('mean_H1','mean_H4','mean_H16'):
    b=max(r,key=lambda x:float(x[k])); g=float(b[k])+0.001
    print(k,'best gross %.4f%%'%(g*100),'= %.2fx cost'%(g/COST),b['trigger'],b['side'],b['filt'],b['n'])
P
```
`mean_*` columns are net of 0.10 % taker; adding 0.001 gives gross.

## 4. What is still open, and why none is quick
1. Tom family A on DAX: blocked by today's recall FAIL; the next step is an operator decision on the encoding, not a run.
2. 1m detection + stop/target + maker entry with trade-through fills (Q33 limit 3): needs the G4 fill model first (Sonnet build).
3. OI / long-short / funding filters (G5 data is being fetched on JIS-NUC): NO-SOURCE for Tom and Fabio (0 hits in 113
   transcripts, SOURCED_RULES.md:45). Allowed only as an MTS-own positioning layer with its own pre-registration; its nearest
   relative (funding-CVD fade) is already negative.
4. Multi-week trend overlay: outside evidence says drawdown reduction, not extra return; NO-SOURCE under the provenance rule.

## 5. Operator decision proposed (not adopted here)
Gross-edge gate from backtest_gap_review_2026-10-13 s7: no new combination or encoding is built unless its DEV gross edge is
at least 2x the round-trip cost of the venue it will trade on. At the taker cost it would have stopped all 186 Q33 cells before any placebo run.
