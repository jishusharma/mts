Verdict: T06=INCONCLUSIVE (DEV screen not passed: n=1322, mean net R +0.048 R, SE 0.040, 95 % CI -0.029..+0.126; mean is positive but the CI includes 0 and the MDE 0.111 R is wider than the mean; VALIDATION not read; no testnet-forward card filed)

# T06 eh-h5-rsi-ma-cross-trigger: RSI14 cross under/over its SMA14 (4h, BTC+ETH spot, both sides pooled)

## Plain answer

The trigger alone, both sides and both symbols pooled, is not shown to be fee-net positive on 4h. On DEV (2017-08 .. 2024-06) the mean net R is +0.048 R per trade (n = 1322), but the day-clustered 95 % CI runs from -0.029 to +0.126 R, so the DEV screen (CI lower bound > 0) fails. Per the frozen rules, VALIDATION was not read. Gross edge is +0.089 R; fees take 0.042 R and funding about 0.001 R. The short side is flat (net -0.002 R). The long side carries the positive mean (+0.105 R, CI -0.024..+0.233), and that is not a screen pass. No PASS, so no testnet-forward card. The next step is not a longer backtest: this trigger as written does not clear the DEV screen.

## Context

- Regime: none, because the trigger is a 4h momentum event and the wave's regime is reported as a mix line, not as a gate.
- Phase: none, because the rule has no phase label.
- Session: none, because 4h bars cover all sessions and the source does not gate by time of day.
- Entry: stop-order entry on the next bar through the signal bar's open (confirmation), no retest.

Regime mix: DEV weeks 358 = bull 72, bear 0, range 223, not computable 63 (SMA200 and monthly RSI warm-up in 2017-18). The bear count is 0 as in the plan (no bear weeks in research_kit's band rule on this history).

## Data and splits

- Spot 4h BTCUSDT and ETHUSDT, 2017-08-17 .. 2025-06-30, from data.binance.vision (`--spot-history`), cached outside the repo at F:/MTS/Dumps/backtest/eh-h5-rsi-ma-cross-trigger/spot_2017. No raw bars are committed.
- Funding: fundingRate archive, cached at .../raw/fundingRate. The cache starts 2020-01 (the fetch logged 4 archive months as 404, not present), so funding is applied from 2020-01 and is 0 before it. Stated per the brief.
- DEV = 2017-08-01 .. 2024-06-30. VALIDATION = 2024-07-01 .. 2025-06-30, not read (screen not passed). HOLDOUT (2025-07+) never loaded: the loader raises SplitRefusal for any end past 2025-07-01 (test_loader_refuses_holdout_range, test_split_refusal).
- The DEV run refuses bars at or past 2024-07-01 (dev_only). Trades still open at the DEV data end would be dropped and counted; the count is 0.

## Event counts (DEV, signal bars, no returns)

| symbol | side | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 (H1) | total |
|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT | short | 32 | 59 | 71 | 96 | 73 | 62 | 84 | 33 | 510 |
| ETHUSDT | short | 31 | 52 | 77 | 103 | 97 | 66 | 78 | 40 | 544 |
| BTCUSDT | long | 14 | 74 | 57 | 56 | 82 | 81 | 55 | 32 | 451 |
| ETHUSDT | long | 19 | 70 | 68 | 63 | 68 | 83 | 64 | 32 | 467 |

Trades taken (after the one-open-trade rule and confirmation): 1322 in DEV (699 short, 623 long). Exits: stop 687, target 251, time 384.

## DEV results (fee-net, R)

Costs: regime A (10 bps RT taker + 2 bps RT slippage = 12 bps RT), fee_r = 12 bps / stop distance; funding R from the archive; net R = gross R - fee_r - funding R. Clustering by ISO week of entry.

| cell | n | hit | mean gross R | mean fee R | mean funding R | mean net R | SE (week) | CI 95 % | MDE 80 % | one-sided p | Holm m=15 | screen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T06 pooled (both sides, both symbols) | 1322 | 0.390 | +0.089 | 0.042 | -0.001 | **+0.048** | 0.040 | -0.029..+0.126 | 0.111 | 0.111 | 1.00 | not passed |
| side short | 699 | 0.356 | +0.032 | 0.043 | -0.009 | -0.002 | 0.063 | -0.125..+0.121 | 0.175 | 0.512 | 1.00 | not passed |
| side long | 623 | 0.427 | +0.152 | 0.040 | +0.007 | +0.105 | 0.066 | -0.024..+0.233 | 0.184 | 0.055 | 0.83 | not passed |
| BTCUSDT | 667 | 0.384 | +0.091 | 0.048 | -0.003 | +0.046 | 0.047 | -0.046..+0.138 | 0.131 | 0.161 | 1.00 | not passed |
| ETHUSDT | 655 | 0.395 | +0.086 | 0.035 | 0.000 | +0.050 | 0.048 | -0.044..+0.144 | 0.134 | 0.147 | 1.00 | not passed |

Per-year, DEV pooled (net R, n): 2017 +0.169 (65); 2018 +0.111 (175); 2019 +0.071 (180); 2020 +0.043 (195); 2021 +0.008 (217); 2022 +0.107 (208); 2023 -0.017 (191); 2024 H1 -0.091 (91). Every year's CI spans 0. Early years are small n. The 2023-24 years are the weakest, and the trend is downward, which is a reason to distrust the pooled mean rather than a finding.

Exploratory only (not promotable; cannot change the verdict): with the last closed daily RSI14 below 60 (short) / above 40 (long), the net R is short +0.102 (n=355) vs -0.109 (n=344) without, and long +0.088 (n=384) vs +0.131 (n=239). The daily filter splits the short side, but the on-cell CI still spans 0 and the split is post-hoc. Labelled EXPL, not a finding.

## Verdict logic

- DEV screen (n >= 30, mean > 0, CI lower > 0): not passed for T06 (CI lower -0.029).
- VALIDATION: not read, because the screen did not pass (the script refuses unless the screen passes: `rsi_ma_cross.py val`).
- FAIL needs DEV mean <= 0 at adequate power. The DEV mean is positive, so this is not a FAIL.
- So: INCONCLUSIVE. The CI lower bound (-0.029) is below 0 while the mean is +0.048; the MDE (0.111 R) is about the size of the mean, so the DEV span does not settle the sign. Settling it would need more events than this definition gives inside DEV (a new trial, not a longer run here).

## DECISION (OURS) list

1. Armed window = the 6 bars before the signal bar (t-6..t-1). The source gives "any of the last 6", not whether the signal bar counts; OURS.
2. Signal event = first bar of a run where the condition holds (not on every bar of a run). OURS, to avoid counting one state many times.
3. Stop-order fill = min(open[t+1], open[t]) for short (max for long), so a gap through the level fills at the open. OURS.
4. Stop = 6-bar extreme including the signal bar; target 2.5R; time stop = 30 bars counting the entry bar (exit at close of bar 30). OURS.
5. Same bar: stop checked before target. OURS (brief s5).
6. One open trade per symbol and side; signals inside an open trade are skipped, not queued. OURS.
7. Regime A fees: 10 bps RT taker + 2 bps RT slippage on all legs (stop-order entry, target, time stop all taker). OURS on the all-taker leg for the target (a limit target would cost less; not tested here).
8. Split constants are this study's own (DEV = 2017-08-01 .. 2024-06-30; VAL 2024-07-01 .. 2025-06-30). backtest/splits.py has DEV_START 2022-01-01, which conflicts with the brief; the brief's wave-wide split wins. OURS.
9. Spot 4h bars for the DEV/VAL statistics; funding from the perp archive from 2020-01 (cache start), 0 before. OURS, stated.
10. Regime mix re-implements the research_kit regime_tag rule with a daily SMA200 side and weekly and monthly RSI14 bands (copied, not imported, to avoid import side effects). OURS.
11. The DEV run and the VALIDATION read share the same code; only the DEV run was executed (the VAL mode would refuse because the screen did not pass).

## Test run (before the code existed, the failing run)

The first test run, before rsi_ma_cross.py existed, ended with: `ModuleNotFoundError: No module named 'rsi_ma_cross'`.

After the code, two of my own test expectations were wrong (armed-window case and below-60 case: the test data themselves made a valid signal); I corrected those inputs, not the rules. Final: `PASSED 18 tests`.

## Noticed

- The worktree sync output said "this tree is not yours (worker start)" for the original checkout; I worked only in the printed worktree, mts-jis-nb-eh-h5-rsi-ma-cross-trigger.
- backtest/splits.py DEV_START 2022-01-01 disagrees with the wave's DEV (2017..2024-06-30). Not edited (read-only); logged as DECISION 8.
- The funding archive starts 2020-01 in this cache; 2019-09..12 returned 404. Funding is 0 before 2020-01.
- Doctor warnings at sync start (CLAUDE.md size headroom 0%, DISK 14.1 GB) are unrelated to this study.

- SHIP BLOCKED: the must-pass gate Step 3xm (dsa_backtest_audit T06 test_cost_inventory) flags the COST_RT_BPS line in rsi_ma_cross.py because costs.csv is in another study's folder (out of this worker's write scope). Not shipped; needs the coordinator to add the row or accept the constant. Quick gate steps 3pc, 3la, 3dl, 3gd, 3qn, 4c, 4d passed; 3cm and 4e-4f not reached.\n