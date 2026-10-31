# DEV_CHECK: Krown free setups on BTC, DEV, fee-net

Spec: PRE_REG.md (frozen first, sha256 in RESULT.csv: a6a0ab3e52d557d097d0cdbd4283d8b4dd54c6b7a6fe7682ab07ce4577a43020). Code: silver_cross_dev.py. Data: BTCUSDT 1m klines 2022-01..2024-06 resampled to daily (912 complete days). Fee 0.10 % round trip from backtest/fees.py (SOURCED). VALIDATION and HOLDOUT unread.

**Result: one of the 14 free-setup rows is testable (Silver Cross, 1-month hold). On DEV it fired 6 times: 3 of 6 green fee-net (50 %) against his claimed 83 %. INCONCLUSIVE by pre-declaration (n = 6).**

## Per-setup table

| Setup | n | hit-rate (net > 0) | mean net return | mean R (scale only) | His claim | Verdict |
|---|---|---|---|---|---|---|
| Silver Cross 1-month (daily EMA21 up-cross EMA55, enter next daily open, exit open 30 days later) | 6 events, 5 blocks | 50 % (3/6); block-bootstrap 95 % CI 0 % to 87.5 % | +7.87 %; CI -9.8 % to +21.7 % | +1.54 R (R = net / (2 x ATR14 / price), no stop exists) | 83 % green at 1 month, median +7.4 % (since 2018, his n NOT_IN_DATA) | INCONCLUSIVE (underpowered); hit-rate point estimate below the claim, mean return is not distinguishable from zero |
| Silver Cross 1-year | not run | n/a | n/a | n/a | 100 % green (6 of 6), median +219 % | NOT_TESTABLE on DEV: exits fall after 2024-06-30 |
| Free AI Bot (4H) | not run | n/a | n/a | n/a | NOT_IN_DATA | NOT_TESTABLE: "Range deviation" blue/red state is a proprietary indicator with no formula in the file |
| 10-Day Reconnect (+ Stoch > 80), 2-Day Bounce | not run | n/a | n/a | n/a | 62 % / 83 % / 56 % | NOT_TESTABLE: "reconnect" / "test of the 55 EMA" has no rule, stochastic settings and stop NOT_IN_DATA |
| 5/21, 13/34 corrective, 2-Day corrective | not run | n/a | n/a | n/a | NOT_IN_DATA | NOT_TESTABLE: no stop, no time bound on the EMA target, no claim to compare |

Labels: n, hit-rate, mean return, mean R, CI = OURS computed this run (SOURCED data, fee from fees.py); the 83 % and 7.4 % are SOURCED quotes (bXug2l6qICc 00:03:08); 30-day hold, next-open entry, "green = net > 0" and the ATR risk unit are OURS (PRE_REG.md section 2).

## The six events (entry date, net return, green)

| Entry | Net | Green |
|---|---|---|
| 2022-11-05 | -19.20 % | no |
| 2023-01-14 | +9.17 % | yes |
| 2023-06-23 | -0.41 % | no |
| 2023-10-08 | +25.36 % | yes |
| 2023-10-17 | +32.90 % | yes |
| 2024-05-18 | -0.59 % | no |

Two events (2023-10-08 and 2023-10-17) overlap and are one block for the bootstrap. Two losses are near zero (-0.41 %, -0.59 % net); gross they are also red (-0.31 %, -0.49 %), so the fee does not flip any event: the gross hit-rate is also 3 of 6.

## Context (descriptive, not a test)

All-days baseline, same 30-day rule and fee, entries 2022-04-01 on: 792 entries, 53.9 % green, mean net +3.10 %. The silver cross (50 %, +7.87 %) is not separable from simply holding BTC for 30 days in this window; DEV was a recovery from the 2022 low, so any long hold looks good.

## Checks

| Check | Result |
|---|---|
| PRE_REG frozen before the run | yes; the script refuses to run without the FROZEN_UTC line (test_refuses_run_without_frozen_prereg) |
| One-bar shift look-ahead | pass: signal exists with data to day t and is absent with data to t-1; changing all bars after day d leaves earlier events unchanged (test_one_bar_shift_causality, test_future_perturbation_leaves_earlier_events) |
| MyTradingSys/tests/test_lookahead_lint.py | pass after two reviewed allowlist rows (baseline outcome label, forward index by design, not read by the signal) |
| Fail-first test, hand-worked values | closes 10,10,10,12,16,16,10 with EMA spans 2 and 3: cross on day 3, entry 12, exit 16, net 0.33333 - 0.001 = 0.33233; test file failed with ModuleNotFoundError before silver_cross_dev.py existed, 11 pass after |
| Costs | fees.BINANCE_TAKER imported; test_no_own_costs passes |
| Trial ledger | TRIAL_REGISTRY.csv row added in this folder and picked up by scripts/dev/trial_ledger.py (1 new cell, Holm m = 1) |

## What this does and does not say

- It does not confirm his 83 %. With 6 events the 95 % CI of the hit-rate spans 0 % to 87.5 %, so 83 % is inside the interval: it neither supports nor rejects the claim.
- His quoted sample is since 2018 and its n is not given; this DEV window has 6 events. A fair test needs the full history (2018 on), which crosses into VALIDATION/HOLDOUT and needs its own pre-registration and a holdout-read log entry.
- The 1-year claim (6 of 6) is untestable here.
- Next, if the operator still wants it: a separate card to run 2018-2022 BTC (older than DEV, no DEV overlap) or to ask Krown for the exact "reconnect" and Range Deviation definitions. Not started.

## DECISION (OURS)

Tested only the one setup whose entry and exit are both in his words and computable from price. Everything else is listed NOT_TESTABLE with the missing part rather than filled with guesses.
