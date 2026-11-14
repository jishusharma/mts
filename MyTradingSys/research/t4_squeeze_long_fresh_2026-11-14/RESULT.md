**FAIL (and all three KILL criteria fire): on 48 fresh coins the trapped-shorts squeeze long, ridden (RIDE), has VAL n 111 trades in 37 entry weeks, gross +0.050 R, fee-net -0.002 R (fee 0.020 R, funding 0.032 R), week-cluster 95% CI [-0.664, +1.148], placebo percentile 64.7. Bars 2, 4, 5, 6 and 7 fail; bars 1 and 3 pass. The old-coin +2.42 R did not carry over to new coins; "squeeze long was a tail of the 20 old coins" is the reading. Not an edge.**

# RESULT: T4 trapped-shorts squeeze long on FRESH coins, 4h (2026-11-14)

Frozen rule: `PRE_REG.md` (untouched). Code: `t4_core.py`, `t4_trades.py`, `t4_stats.py`, `t4_report.py`. Numbers: `summary.json` (verdict bars), `report_numbers.json` (table rows), `tables.md` (by year / coin / phase), all parsed, none from console. Fix round before statistics: `FIXLOG.md`, `DEVIATIONS.md`.

## Context

Question: does the miner's one surviving lead (4h, same-bar AND of low funding, spot net taker buying and a 5-day breakout, long only, ridden until a 10-day-low break) hold on coins it was never fitted on? Not a trade instruction; nothing is an edge until a fee-net out-of-sample result passes the bars and a blind review.
Regime: BTC structure UP / MIX / DOWN (miner label: BTC close vs SMA200d and the 20-day slope of that SMA). Hypothesis cell = non-bear (UP_E, UP_L, MIX_E, MIX_L). Control = DOWN_E / DOWN_L, descriptive only, never pooled.
Phase: miner 6-label phase (structure x halving clock, E under 540 days since the last halving, L from 540), keyed to the entry bar's UTC day from BTC closes of days <= D-1 (halving clock also at D-1, DEVIATIONS 15). The MTS brain label (phase_daily.csv, BULL / BASE / BEAR cycle) is a descriptive second cut only.
Session: none (4h bars, holds of days to 60 days; intraday session timing is not the mechanism).
Entry: onset 4h bar where FUND_LO, NB_ABS and BRK5 are all true (not all true on the coin's previous bar), fill at the next 4h open (taker, 12 bp round trip plus actual 8h funding), stop max(2.5 x ATR14, 2% of entry), primary exit RIDE (next open after a close at or below the prior 10-day low, time exit day 60), secondary exit T3R (+3R, time exit day 30).

Regime mix: UTC days of each split by miner label next to the share of fresh-basket RIDE signals in the same split. Calendar days: DEV 1461, VAL 1047.

| Phase | DEV days | DEV signals | VAL days | VAL signals |
|---|---|---|---|---|
| UP_E | 415 (28.4%) | 21 (19.8%) | 410 (39.2%) | 60 (54.1%) |
| UP_L | 325 (22.2%) | 45 (42.5%) | 199 (19.0%) | 19 (17.1%) |
| MIX_E | 113 (7.7%) | 7 (6.6%) | 116 (11.1%) | 30 (27.0%) |
| MIX_L | 194 (13.3%) | 33 (31.1%) | 42 (4.0%) | 2 (1.8%) |
| DOWN_E (control) | 12 (0.8%) | 1 control signal | 14 (1.3%) | 1 control signal |
| DOWN_L (control) | 402 (27.5%) | 19 control signals | 266 (25.4%) | 20 control signals |

Regime mix, brain cycle tag of the RIDE signals: DEV BASE 60 (56.6%), BEAR 35 (33.0%), BULL 11 (10.4%); VAL BASE 8 (7.2%), BEAR 18 (16.2%), BULL 85 (76.6%). The two splits sit in very different cycle regimes: DEV signals are mostly BASE / BEAR cycle days (2020 to 2023), VAL signals are 77% BULL cycle days (2024-2025). Old-20 signals by phase: DEV UP_E 11, UP_L 14, MIX_E 4, MIX_L 10 (n 39); VAL UP_E 43, UP_L 15, MIX_E 13, MIX_L 1 (n 72).

## Pass-bar table (fresh coins, non-bear, 12 bp plus actual funding)

| Bar | Test | Value | Threshold | Met |
|---|---|---|---|---|
| 1 | VAL n and entry weeks | n 111, 37 weeks | n >= 30 and weeks >= 20 | yes |
| 2 | VAL RIDE mean net R and week-cluster CI low | -0.0019 R, CI [-0.664, +1.148], one-sided p 0.539 | mean > 0 and CI low > 0 | NO |
| 3 | DEV RIDE mean net R | +0.791 R (n 106, 50 weeks) | > 0 | yes |
| 4 | Excess over 1000 same-coin random entries (VAL) | real -0.0019 vs placebo mean -0.0712, excess +0.069 R, 97.5th pct +0.632, percentile 64.7 | real above 97.5th pct | NO |
| 5 | Ex-best-5 entry weeks, VAL T3R row | -0.488 R (n_left 105 of 112; 5 of 37 weeks dropped) | > 0 | NO |
| 6 | Mean net daily return in position vs basket | strategy -0.00152 per position-day (829.5 position-days) vs basket -0.0000195 (767 non-bear days) | strategy >= basket | NO |
| 7 | Top-coin removal, VAL RIDE | worst removal OCEAN gives -0.304 R; 9 of 38 removals are negative (1INCH, ANKR, BAT, HBAR, ICX, MKR, OCEAN, ONT, RVN) | stays > 0 after each removal | NO (FRAGILE) |

Verdict by the PRE_REG vocabulary: FAIL (bars 2, 4, 5, 6, 7), labelled FRAGILE. Holm: VAL one-sided p 0.539; it cannot pass Holm at 0.05 over m = 3 whatever the T5 / T6 p-values are (the coordinator assembles the rank). Registered prediction (fresh VAL RIDE mean > 0 with the T3R row smaller): REFUTED (RIDE -0.002 R, not above zero; T3R -0.272 R).

KILL criteria (PRE_REG; bar 1 holds, so the n condition is met): (a) fresh VAL RIDE mean <= 0: FIRES (-0.0019 R); (b) VAL T3R ex-best-5 <= 0: FIRES (-0.488 R); (c) real VAL mean at or below the 97.5th placebo percentile with n >= 60: FIRES (n 111, percentile 64.7). Three of three. Because n 111 and 37 weeks meet bar 1 this is a powered FAIL, not UNDERPOWERED. But see the power gate: at the measured sd only a mean of about +1.2 R could have registered, so this study says "the old-coin +2.4 R did not reproduce", not "the true mean is zero".

## Main table (RIDE primary; fresh coins, non-bear; R per trade; week-cluster CI, 2000 resamples, seed 1114)

| Split | n | Entry weeks | Win % | Gross R | Fee R | Funding R | Net R | 95% CI (weeks) | Placebo pct | Ex-best-5 weeks | Buy-and-hold | Top-coin removal |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DEV | 106 | 50 | 25.5 | +0.801 | 0.019 | -0.009 | +0.791 | [-0.176, +1.982] | not run (VAL only, PRE_REG) | not run | not run | not run |
| VAL | 111 | 37 | 17.1 | +0.050 | 0.020 | +0.032 | -0.002 | [-0.664, +1.148] | 64.7 | RIDE -0.703 (n_left 105); T3R -0.488 | -0.00152 vs basket -0.00002 per day: below | worst OCEAN -0.304; FRAGILE |
| Pooled fresh | 217 | 87 | 21.2 | +0.417 | 0.019 | +0.012 | +0.385 | [-0.232, +1.183] | not run | not run | not run | not run |

Funding R is funding paid in R (positive = longs paid). VAL sd of R 3.894, DEV 5.174. VAL shape: 75.7% of trades end at the stop, median R -1.02, 90th percentile +1.05, best trade +34.6 R, and the 5 best VAL trades sum to +68.7 R against a VAL total of -0.2 R: the profit, where there is any, lives in a handful of trends and is cancelled by the stops. 6 bp round-trip row (informational, no fill model): VAL +0.008 R, DEV +0.800 R.

Secondary row T3R (+3R target, time exit day 30; carries bar 5):

| Split | n | Weeks | Win % | Gross R | Fee R | Funding R | Net R | 95% CI (weeks) |
|---|---|---|---|---|---|---|---|---|
| DEV | 113 | 51 | 35.4 | +0.390 | 0.019 | -0.026 | +0.396 | [-0.145, +0.871] |
| VAL | 112 | 37 | 18.8 | -0.241 | 0.019 | +0.011 | -0.272 | [-0.562, +0.092] |
| Pooled fresh | 225 | 88 | 27.1 | +0.076 | 0.019 | -0.007 | +0.064 | [-0.258, +0.421] |

TRAIL exit not run (PRE_REG).

## Control and descriptive rows (never in the verdict)

| Row | Split | n | Weeks | Gross R | Net R | 95% CI |
|---|---|---|---|---|---|---|
| Control DOWN_E / DOWN_L, RIDE, fresh | DEV | 20 | 17 | +0.589 | +0.554 | [-0.649, +1.942] |
| Control DOWN, RIDE, fresh | VAL | 21 | 15 | -0.338 | -0.204 | [-0.988, +0.933] |
| Control DOWN, T3R, fresh | DEV / VAL | 20 / 21 | 17 / 15 | +0.200 / -0.326 | +0.175 / -0.359 | [-0.590, +0.979] / [-0.910, +0.250] |
| Old-20 coins, RIDE (miner list, same code) | DEV | 39 | 33 | +3.292 | +3.104 | [+0.003, +7.796] |
| Old-20 coins, RIDE | VAL | 72 | 42 | +2.554 | +2.420 | [-0.012, +6.214] |
| Old-20 coins, T3R | DEV / VAL | 44 / 76 | 35 / 42 | +0.545 / +0.263 | +0.520 / +0.220 | [-0.266, +1.289] / [-0.300, +0.820] |
| Old-20 + fresh pooled, RIDE | VAL | 183 | 55 | +1.035 | +0.951 | [-0.323, +2.867] |
| Old-20 + fresh pooled, T3R | VAL | 188 | 55 | -0.037 | -0.073 | [-0.391, +0.352] |

Replication check of the code on the old coins: VAL RIDE +2.420 R (n 72) and T3R VAL +0.220 R reproduce the miner's seen numbers. Old-20 DEV RIDE is +3.104 R (n 39), not the seen +2.675 R (n 45), because the strict 90-value FUND_LO rule (DEVIATIONS 13) removes 6 early-2020 trades there; documented, not tuned. The contrast: same code and same weeks, +0.05 gross R on fresh VAL against +2.55 on the old coins. The old-coin result is not shared by coins it was not found on. (Note the old-20 VAL CI here is [-0.012, +6.214] on week clusters, slightly different from the miner's day clusters.)

Pooled by phase (RIDE, DEV plus VAL, fresh): UP_E n 81 +0.451 R, UP_L n 64 +1.160 R, MIX_E n 37 -0.105 R, MIX_L n 35 -0.666 R. VAL by miner phase: MIX_E 30 -0.398, MIX_L 2 +1.642, UP_E 60 -0.432, UP_L 19 +1.810. VAL by brain label: DISTRIBUTION 71 -0.765, MARKDOWN 20 -0.326, MARKUP 16 +1.141, ACCUM-RANGE 4 +10.594 (n 4, noise). No cell has a CI away from zero; none is a finding.

## By year (fresh RIDE; U = n under 30, underpowered)

| Year | DEV n | DEV net R | VAL n | VAL net R |
|---|---|---|---|---|
| 2020 | 12 U | +3.855 | | |
| 2021 | 20 U | +1.097 | | |
| 2022 | 12 U | -0.987 | | |
| 2023 | 62 | +0.443 | | |
| 2024 | | | 63 | +0.344 |
| 2025 | | | 43 | -0.513 |
| 2026 | | | 5 U | +0.037 |

Year is the entry-bar UTC year. T3R by year, VAL: 2024 -0.209 (n 64), 2025 -0.468 (n 43), 2026 +0.618 (n 5 U).

## By coin

All 38 coins that traded in VAL have n between 1 and 7, so every per-coin row is underpowered (n < 30); full table in `tables.md`. Positive VAL coins on RIDE: OCEAN +10.87 (n 3), BAT +5.32 (n 2), ONT +4.27 (n 1), 1INCH +2.05 (n 3), HBAR +1.94 (n 2), ICX +1.78 (n 5), MKR +0.55 (n 3), RVN +0.47 (n 5), ANKR +0.11 (n 3). The other 29 are negative, most near -1.0 R (a stop). Dropped coins: none; all 48 candidates have 4h spot and funding (`coverage.json` `fresh_dropped` is empty). PRE_REG says 49 but the frozen list holds 48 names.

## Power-gate output

PRE_REG run (n 72, old-coin sd 12.3, cost 0.03, m 3): BLOCK, MDE 4.688 R; at n 150: BLOCK, MDE 3.248 R (pasted in PRE_REG; the run was ordered by the operator). Re-run with the measured fresh sd:

```
python scripts/dev/prereg_gate.py --n 111 --sd 3.894 --cost 0.02 --m 3 --sd-source "T4 measured VAL fresh RIDE sd, summary"
n 111 sd 3.894 m 3 z_holm 2.394 MDE 1.195 R + cost 0.02 = 1.215 vs max plausible gross 0.3; n needed 2023
BLOCK: do not freeze   [exit 1]
```

Plain reading: at the measured spread the study could only have confirmed a mean of about +1.2 R or more. The old coins showed +2.4 R, so the test was powered for the size that was claimed; it returned +0.05 gross. A smaller true mean (say +0.3 R) is neither shown nor excluded: detecting that needs about 2000 trades, far beyond 48 coins.

## Deviations, fixes and allowlist rows

- DEVIATIONS.md items 1 to 17 stand (list size 48 not 49; overlap per window; funding window to the next bar open; funding cache ends 2026-10-31; strict FUND_LO; funding stamps snapped to the minute; phase halving clock at D-1; LUNA splice and FTT gap documented; NaN ex-best-5 gives UNDERPOWERED).
- FIXLOG.md round 1 (before statistics): strict FUND_LO removed 22 RIDE and 25 T3R DEV trades from 2020, 0 from VAL; funding timestamp jitter fix changed funding on 128 of 442 trades (max |R| change 0.17).
- Step C: no crash, no bar changed, no change to the rule code. Added `t4_report.py` (descriptive tables only; reads trades.csv and the BTC cache; no gate).
- Placebo caveats: draws are independent across trades and need no 90-day funding warm-up (slightly anti-conservative against the week-clustered real mean). The result fails the bar anyway.
- Allowlist rows needed (lookahead_lint, not self-approved): `t4_stats.py` lines 50 and 119 are WARN (bootstrap and placebo percentiles on resampled means, not features). Any further WARN from `t4_report.py` is listed in the notes file.

## What this does and does not show

- Out of sample by coin, NOT by calendar time. The 48 coins were not used to find the rule, but they share the same weeks as the 20 that were. Altcoins squeeze together: 111 VAL trades sit in only 37 entry weeks, so the week-cluster CI [-0.66, +1.15] is the honest width.
- Spot price stands in for the perpetual: no basis, no liquidation, a flat 12 bp (real alt spreads can be wider). Actual 8h funding was charged; the funding cache ends 2026-10-31.
- Survivorship is unfixed: the candidate list is not point-in-time and coins missing from the archive are absent; the bias direction is unknown. The LUNA splice and the FTT gap touch no trade.
- The rule is tail-shaped. About 3 of 4 trades are stopped out near -1 R and a few trends pay; five VAL trades add +68.7 R while the whole VAL set nets -0.2 R. On 48 new coins the tail did not pay on net.
- DEV (+0.79 R) is positive but is carried by 2020-21 outliers (2020 n 12 at +3.9 R) and offset by the 2022 bear (n 12 at -0.99 R). Bar 3 is a sign check only.
- A FAIL on a tail-shaped cell with an MDE of about 1.2 R says the claimed +2.4 R was not general. It does not prove no smaller edge.
- Nothing here is advice or a signal.

## Active today (descriptive, NOT advice)

Miner label on the last closed BTC day (2026-11-12): MIX_L, active for the cell; the brain label is MARKDOWN / BEAR (provisional), so the two disagree. No fresh-coin signal can be evaluated on the last closed 4h bar because FUND_LO needs funding and the cache ends 2026-10-31. The last fresh-coin signals in the file are COMP 2026-10-20 (RIDE stopped out, T3R hit the target) and KAVA 2026-10-18 (stopped out), both closed; the last old-20 signal is 2026-09-30. So: no known open signal, and the last two weeks are untested for lack of funding data.

## Next

END: FAIL on 48 fresh coins, all three kill criteria fire (VAL net -0.002 R, T3R ex-best-5 -0.488 R, placebo percentile 64.7); old-coin +2.4 R is read as a 20-coin tail. No testnet-forward card. Revisit only if a materially larger independent coin and time sample becomes available.
