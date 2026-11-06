# Blind read: Multi-TF Bias Stack DEV Study (2026-11-06)

Method: Blind read protocol strictly executed. `RESULTS.csv` and `study.py` were inspected and recomputed first; `REPORT.md` was read only after independent recomputation. All raw 1m klines (1,313,280 bars, DEV window 2022-01-01 to 2024-06-30 from `F:/MTS/data/tom_raw/klines`) were processed independently through the multi-TF rule logic (N=20, ER 0.30, edge 0.15, step 4h, hold 8h, cost 12.0 bps) and day-clustered standard error formulas.

## 1. Summary of Arms and Arithmetic Verification

Cost is 12.0 bps round trip (SOURCED `study.py:19` and `REPORT.md:3`).
Formulas independently recomputed:
- `net = gross - cost` = `gross - 12.0 bps`
- `t = mean_net_bps / se`
- Day-clustered standard error: `se = sqrt(sum_{d in days} (sum_{i in d} (x_i - mean))^2) / n` (SOURCED `study.py:131`, `REPORT.md:17`, `FORMULAS.md`)
- Decision partitioning: `1h-only n` (5469) = `STACK n` (1348) + `1h-only-filtered-out n` (4121)
- `1D-only n` (5464) = `1348` + `4116`

## 2. Per-Number Table: REPORT.md vs RESULTS.csv vs Independently Recomputed

Every number in the table below is cross-verified:

| # | Item / Arm | Metric | REPORT.md [SOURCED `REPORT.md:7-14`] | RESULTS.csv [SOURCED `RESULTS.csv:1-7`] | Independently Recomputed (Raw DEV Data) [OURS] | Status |
|---|---|---|---|---|---|---|
| 1 | STACK | n | 1348 (line 9) | 1348 (line 2) | 1348 decisions | MATCH |
| 2 | STACK | days | 524 (line 9) | 524 (line 2) | 524 distinct days | MATCH |
| 3 | STACK | mean net bps | -6.58 (line 9) | -6.58 (line 2) | -6.5795 bps | MATCH |
| 4 | STACK | SE | 5.62 (line 9) | 5.62 (line 2) | 5.6205 bps | MATCH |
| 5 | STACK | t | -1.17 (line 9) | -1.171 (line 2) | -1.1706 | MATCH |
| 6 | STACK | mean gross bps | +5.42 (line 9) | 5.42 (line 2) | +5.4205 bps | MATCH |
| 7 | 1h-only | n | 5469 (line 10) | 5469 (line 3) | 5469 decisions | MATCH |
| 8 | 1h-only | days | 912 (line 10) | 912 (line 3) | 912 distinct days | MATCH |
| 9 | 1h-only | mean net bps | -9.75 (line 10) | -9.748 (line 3) | -9.7483 bps | MATCH |
| 10 | 1h-only | SE | 2.37 (line 10) | 2.368 (line 3) | 2.3675 bps | MATCH |
| 11 | 1h-only | t | -4.12 (line 10) | -4.117 (line 3) | -4.1175 | MATCH |
| 12 | 1h-only | mean gross bps | +2.25 (line 10) | 2.252 (line 3) | +2.2517 bps | MATCH |
| 13 | 1D-only | n | 5464 (line 11) | 5464 (line 4) | 5464 decisions | MATCH |
| 14 | 1D-only | days | 911 (line 11) | 911 (line 4) | 911 distinct days | MATCH |
| 15 | 1D-only | mean net bps | -8.25 (line 11) | -8.254 (line 4) | -8.2541 bps | MATCH |
| 16 | 1D-only | SE | 3.06 (line 11) | 3.058 (line 4) | 3.0582 bps | MATCH |
| 17 | 1D-only | t | -2.70 (line 11) | -2.699 (line 4) | -2.6990 | MATCH |
| 18 | 1D-only | mean gross bps | +3.75 (line 11) | 3.746 (line 4) | +3.7459 bps | MATCH |
| 19 | ALL-LONG | n | 5469 (line 12) | 5469 (line 5) | 5469 decisions | MATCH |
| 20 | ALL-LONG | days | 912 (line 12) | 912 (line 5) | 912 distinct days | MATCH |
| 21 | ALL-LONG | mean net bps | -9.73 (line 12) | -9.727 (line 5) | -9.7266 bps | MATCH |
| 22 | ALL-LONG | SE | 3.06 (line 12) | 3.057 (line 5) | 3.0573 bps | MATCH |
| 23 | ALL-LONG | t | -3.18 (line 12) | -3.181 (line 5) | -3.1814 | MATCH |
| 24 | ALL-LONG | mean gross bps | +2.27 (line 12) | 2.273 (line 5) | +2.2734 bps | MATCH |
| 25 | 1h-only filtered-out | n | 4121 (line 13) | 4121 (line 6) | 4121 decisions | MATCH |
| 26 | 1h-only filtered-out | days | 907 (line 13) | 907 (line 6) | 907 distinct days | MATCH |
| 27 | 1h-only filtered-out | mean net bps | -10.78 (line 13) | -10.785 (line 6) | -10.7849 bps | MATCH |
| 28 | 1h-only filtered-out | SE | 2.88 (line 13) | 2.881 (line 6) | 2.8808 bps | MATCH |
| 29 | 1h-only filtered-out | t | -3.74 (line 13) | -3.744 (line 6) | -3.7437 | MATCH |
| 30 | 1h-only filtered-out | mean gross bps | +1.22 (line 13) | 1.215 (line 6) | +1.2151 bps | MATCH |
| 31 | 1D-only filtered-out | n | 4116 (line 14) | 4116 (line 7) | 4116 decisions | MATCH |
| 32 | 1D-only filtered-out | days | 906 (line 14) | 906 (line 7) | 906 distinct days | MATCH |
| 33 | 1D-only filtered-out | mean net bps | -5.54 (line 14) | -5.54 (line 7) | -5.5405 bps | MATCH |
| 34 | 1D-only filtered-out | SE | 3.30 (line 14) | 3.305 (line 7) | 3.3049 bps | MATCH |
| 35 | 1D-only filtered-out | t | -1.68 (line 14) | -1.676 (line 7) | -1.6764 | MATCH |
| 36 | 1D-only filtered-out | mean gross bps | +6.46 (line 14) | 6.46 (line 7) | +6.4595 bps | MATCH |

Total discrete table metrics: 36.
Matching: 36 of 36 (100%).

## 3. Narrative and Text Claim Verification

1. **Decisions and Coverage** (SOURCED `REPORT.md:3`):
   - Claim: "The written stack (RULE.md) gives a bias on 1,348 of 5,469 four-hourly decisions (524 days)".
   - Recomputed [OURS]: exactly 1,348 non-zero stack bias decisions out of 5,469 total evaluated 4-hourly slots over 524 distinct UTC calendar days. Result: MATCH.

2. **Headline Net and Gross** (SOURCED `REPORT.md:3-4`):
   - Claim: "8h-forward net of 12 bps it is -6.58 bps (SE 5.62, t -1.17), gross +5.42 bps".
   - Recomputed [OURS]: Net = `+5.4205 - 12.0 = -6.5795 bps` (rounds to -6.58 bps); SE = `5.6205` (rounds to 5.62); t = `-1.1706` (rounds to -1.17); gross = `+5.4205 bps` (rounds to +5.42). Result: MATCH.

3. **Baselines Comparison** (SOURCED `REPORT.md:4-5`):
   - Claim: "1h-only -9.75 (t -4.12), 1D-only -8.25 (t -2.70), always-long -9.73".
   - Recomputed [OURS]:
     - 1h-only: mean net `-9.7483` -> `-9.75`, t `-4.1175` -> `-4.12`.
     - 1D-only: mean net `-8.2541` -> `-8.25`, t `-2.6990` -> `-2.70`.
     - ALL-LONG: mean net `-9.7266` -> `-9.73`, t `-3.1814` -> `-3.18`.
   - Result: MATCH.

4. **Filter Gap** (SOURCED `REPORT.md:5`):
   - Claim: "The 1h trades the stack removed average -10.78 bps (t -3.74) against -6.58 kept, a 4.2 bps gap well inside one SE (5.6)".
   - Recomputed [OURS]: `-6.5795 - (-10.7849) = +4.2054 bps` (rounds to 4.2 bps). Stack SE is 5.62 bps. Gap of 4.20 bps < 5.62 bps. Result: MATCH.

5. **1D Removed vs Kept Contrast** (SOURCED `REPORT.md:22`):
   - Claim: "The 1D-only arm's removed trades look better than the kept stack ones (-5.5 vs -6.6 bps gross +6.5 vs +5.4): the stack filter did not select the better 1D trades".
   - Recomputed [OURS]: 1D filtered out net is `-5.5405` vs stack `-6.5795`; gross is `+6.4595` vs stack `+5.4205`. Result: MATCH.

6. **Gross Return vs Cost** (SOURCED `REPORT.md:21`):
   - Claim: "Gross is positive for every flow arm (+1 to +6 bps) and cost is 12 bps: the flow sign carries no net edge at 8h on this window, with or without the stack".
   - Recomputed [OURS]: Gross values are: STACK `+5.42`, 1h-only `+2.25`, 1D-only `+3.75`, ALL-LONG `+2.27`, 1h-filtered-out `+1.22`, 1D-filtered-out `+6.46`. All are between +1.22 and +6.46 bps. All net results are negative after 12 bps fee cost. Result: MATCH.

7. **Power Limit** (SOURCED `REPORT.md:34`):
   - Claim: "SE is 5.6 bps, so a net effect under about 11 bps (2 SE) is invisible here".
   - Recomputed [OURS]: `2 * 5.6205 bps = 11.241 bps` (~11 bps). Result: MATCH.

8. **Unit Tests** (SOURCED `REPORT.md:17`):
   - Claim: "17 tests, failed before study.py existed".
   - Recomputed [OURS]: `python MyTradingSys/research/multi_tf_bias_2026-10-18/test_study.py` runs exactly 17 tests: `Ran 17 tests in 0.311s, OK`. Result: MATCH.

## 4. Edge Assessment

The blind read confirms that the multi-TF bias stack as written produces NO NET EDGE on the DEV dataset (BTCUSDT perp 2022-01-01 to 2024-06-30). All arms exhibit negative mean net returns after 12 bps cost (-5.54 to -10.78 bps). The filter provides no statistically significant uplift (+4.2 bps vs 1h flow alone, t = -1.17, well within the 5.62 bps SE).

VERDICT: MATCH
