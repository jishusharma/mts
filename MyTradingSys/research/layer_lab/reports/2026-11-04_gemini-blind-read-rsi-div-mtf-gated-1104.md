# Layer Lab Report: `gemini-blind-read-rsi-div-mtf-gated-1104`

- **Card**: `gemini-blind-read-rsi-div-mtf-gated-1104` (`OURS`)
- **Date**: 2026-11-04 UTC (`OURS`)
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_RSI_DIV_MTF_1104.md` (`OURS`)
- **Headline Counts**: `FOUND=104 DIFF=0 NOT_IN_DATA=0` (`OURS`)

## Findings

1. **Independent Blind Re-read & Re-computation Matches `RESULT.md` and `RESULT_LONG.md` Byte-for-Byte (`FOUND=104, DIFF=0, NOT_IN_DATA=0`)**:
   - Every metric in `MyTradingSys/research/rsi_divergence_mtf_gated_2026-11-04/RESULT.md` (`SOURCED`) and `RESULT_LONG.md` (`SOURCED`) was re-computed from `dev_cells.csv:1-257` (`SOURCED`), `counts.csv:1-257` (`SOURCED`), `dev_cells_long.csv:1-273` (`SOURCED`), `counts_long.csv:1-273` (`SOURCED`), `regime_mix_dev.txt:1` (`SOURCED`), and `regime_mix_dev_long.txt:1-2` (`SOURCED`).
   - Run 1 regime mix (130 weeks DEV 2022-01..2024-06): bull 25 (19%), bear 0 (0%), range 105 (81%), n/a 0 (0%) (`regime_mix_dev.txt:1`).
   - Long window regime mix (360 weeks DEV 2017-08..2024-06): bull 73 (20%), bear 0 (0%), range 222 (62%), n/a 65 (18%) (`regime_mix_dev_long.txt:1`). Bear proxy P40 adds 57 bear weeks (16%) and 165 range weeks (46%) (`regime_mix_dev_long.txt:2`).
   - Gate effect on 15m W12 bullish signal: ungated $n = 973$, net $-0.161\%$ $[-0.229, -0.092]$ (`dev_cells.csv:2`); aligned bull $n = 164$ / 96 days, gross $-0.036\%$, net $-0.176\%$ $[-0.307, -0.045]$, excess $-0.064\%$ ($t = -1.0$) (`dev_cells.csv:4`). Gate drops 83% of events without improving net return (`OURS`).
   - Retest entry fills: 126/164 on 15m (net $-0.130\%$), 34/43 on 1h (net $+0.123\%$), 15/18 on 4h (net $-0.189\%$) (`dev_cells.csv:5,69,133`).
   - P40 Bear proxy (long window): 15m aligned short $n = 434$ / 236 days, net $-0.158\%$ $[-0.278, -0.039]$, excess $-0.013\%$ ($t = -0.23$) (`dev_cells_long.csv:18`).
   - Side-by-side table (`RESULT_LONG.md:19-30`) recomputed across all 9 cells with exact agreement.
   - Multiple testing family adjustment: Holm adjustment with $m = 32$ for Run 1 and $m = 48$ for Long window produces exactly 0 survivors (`dev_survivors.json:1` is `[]`, `dev_survivors_long.json:1` is `[]`).
   - Audit conclusion: `VERDICT: MATCH`.
