**KILL: fresh pooled (DEV+VAL) mean net R is negative on both funding rows (-0.031 no funding, -0.029 with funding), and the VAL placebo percentile is 29.8 / 31.4 (below 90) at VAL n 352. VAL n 352 trades in 90 ISO entry weeks, gross R -0.024, fee-net R -0.046 (no funding) / -0.043 (with funding), week-cluster 95% CI [-0.159, 0.078] / [-0.157, 0.081]. The +0.10 R of the 22 source coins did not replicate on 45 coins it never saw. Not an edge.**

# T5 RESULT: bear-phase 4h bearish-divergence short, 45 fresh coins (2026-11-14)

PRE_REG.md is the law and was not edited after its first commit (a9be6f2d3). Fix round (FIXLOG.md, before any statistic): BEAR higher-low window moved to the PRE_REG text (BEAR-true trades 1096 -> 828), funding inside the hold always counted, placebo pool split by signal bar. Numbers below come from summary.json (parsed) and trades.csv (parsed), not from console output.

## Context

Regime: per-coin ex-ante BEAR flag (daily, read at D-1) is the only gate; shorts are claimed only when BEAR is true. Descriptive BTC cycle shown below.
Phase: claim flag = per-coin BEAR. Descriptive BTC brain phase on the signal day: cycle BEAR 56.0%, BULL 23.6%, BASE 20.4% of claim trades (pooled). BTC today (2026-11-14, provisional): MARKDOWN / BEAR.
Session: not applicable; 4h bars run 24/7 UTC, no session gate.
Entry: short at the next 4h open after the confirming close of the second swing high (SOURCED).
Regime mix: share of coin-days with BEAR true: DEV 36.7%, VAL 43.0% (RECENT and pooled coin-day shares were NOT produced by t5_stats.py and are not reported; the pooled value lies between the two). Test 1 label share of coin-days, DEV: UP 26.1%, BASE 33.8%, RANGE 5.1%, DOWN 3.2%, POSTPEAK_BEAR 31.7%; VAL: UP 20.2%, BASE 33.8%, RANGE 5.1%, DOWN 3.9%, POSTPEAK_BEAR 37.0%. BTC cycle share of pooled claim trades: BEAR 56.0%, BULL 23.6%, BASE 20.4% (per-split cycle share not produced). Claim trades by calendar year, DEV: 2019 3.2%, 2020 4.4%, 2021 3.2%, 2022 50.2%, 2023 39.1%; VAL: 2024 30.4%, 2025 39.5%, 2026 30.1%; pooled top year 2022 at 28.9%. ONE-YEAR (more than 85% from one year): no on DEV (max 50.2%), VAL (max 39.5%) and RECENT (max 62.7%, 2025).

## Pass bars (fresh VAL, both 12 bp rows)

| Bar | Value (no fund / with fund) | Threshold | Met |
|---|---|---|---|
| 1 Power | n 352, 90 weeks | n >= 30 and >= 20 weeks | yes / yes |
| 2 VAL mean R > 0 and CI low > 0 | mean -0.046 / -0.043, CI low -0.159 / -0.157 | > 0 and > 0 | no / no |
| 3 DEV mean R > 0 | -0.020 / -0.018 | > 0 | no / no |
| 4 Beats placebo | pct 29.8 / 31.4, 97.5th pct of draw means 0.088 | real mean above it | no / no |
| 5 Ex-best-5 VAL weeks mean R | -0.136 / -0.140 | > 0 | no / no |
| 6 Signal rate vs short-and-hold basket (per day) | -0.00274 vs +0.00061 / -0.00271 vs +0.00048 | signal >= baseline | no / no |
| 7 Top-coin removal (CELR removed) | -0.062 / -0.060 | > 0 | no / no |

Kill criteria (design note): pooled mean <= 0 on either row: yes (-0.031 / -0.029). VAL placebo pct < 90 with VAL n >= 200: yes (29.8 / 31.4 at n 352). Both fire. Raw one-sided VAL bootstrap p (larger row) 0.773; Holm over the wave family is the coordinator's step and is moot for a KILL. Labels: none (the verdict is KILL before PASS / REPLICATED-WEAK are reached, so the FRAGILE / ONE-YEAR naming question does not arise).

## Main table, BEAR true, 12 bp (R units; funding R and fee R are per-trade means of funding/r and cost/r)

| Cell | n | Entry weeks | Win % (net, with fund) | Gross R | Fee R | Funding R | Net R no fund | Net R with fund | Week-cluster 95% CI (with fund) | Placebo pct (with fund) | Ex-best-5 weeks (with fund) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DEV | 476 | 110 | 36.6 | 0.000 | 0.020 | +0.002 | -0.020 | -0.018 | [-0.127, 0.103] | 83.0 | -0.097 |
| VAL | 352 | 90 | 34.4 | -0.024 | 0.022 | +0.003 | -0.046 | -0.043 | [-0.157, 0.081] | 31.4 | -0.140 |
| Pooled fresh | 828 | 200 | 35.6 | -0.010 | 0.021 | +0.002 | -0.031 | -0.029 | [-0.110, 0.051] | 62.4 | -0.077 |
| RECENT (descriptive) | 169 | 49 | 35.5 | -0.014 | 0.020 | +0.001 | -0.035 | -0.033 | [-0.191, 0.151] | n/a | -0.201 |

No-funding CIs: DEV [-0.129, 0.102], VAL [-0.159, 0.078], pooled [-0.113, 0.049], RECENT [-0.193, 0.149]. Placebo percentiles without funding: DEV 81.4, VAL 29.8, pooled 58.2. 6 bp rows (descriptive): VAL -0.035 / -0.032, DEV -0.010 / -0.008, pooled -0.021 / -0.018 (no fund / fund); none is positive. Per-trade sd of R about 0.88 (the PRE_REG assumed 1.26). Time in market: 8728 4h bars pooled (DEV 5137, VAL 3591). Exit mix of the 828 claim trades: 763 trail, 59 stop, 6 time.

Top-coin removal, pooled: the largest summed contributor is ICX (summed R about +12.1; n 30, mean +0.40, the only coin with n >= 30). The VAL top coin by the bar-7 definition is CELR. Removing LUNA (16 claim trades, re-denominated 2022-05-31 so its BEAR flag and stops are distorted for about a year; 4 trades fall in that year): pooled net R with funding -0.030 (n 812), VAL -0.043 (n 343); no change to any conclusion.

## Baselines and controls

| Row | Result |
|---|---|
| Short-and-hold of the fresh basket over BEAR coin-days (per day, 12 bp row; no fee on the baseline, which favours it) | VAL: signal -0.00271 vs baseline +0.00048 (with fund), -0.00274 vs +0.00061 (no fund); DEV: -0.00152 vs -0.00210 (with fund), -0.00151 vs -0.00219 (no fund). The signal trails the baseline in VAL and edges it only in DEV, where both are negative. |
| Placebo (1000 random BEAR-true entries per real trade, same coin, split, stop distance and exit rule) | VAL real mean sits at the 29.8 / 31.4 percentile of the draws: random bear-phase shorts did better than the divergence signal. |
| Control: same signal with BEAR false (1384 trades, with fund) | mean +0.048 R, gross +0.059 R, win 40.2%. By Test 1 label: UP 631 trades +0.042, BASE 642 +0.080, RANGE 106 -0.116, DOWN 5 +0.081, POSTPEAK_BEAR 0. The ungated signal did better than the gated one, so the BEAR gate added nothing here. Descriptive only. |
| Old 22 + fresh pooled (n-weighted from SOURCE summary numbers; fresh re-run, old NOT re-run) | DEV n 763 +0.028 / +0.030, VAL n 563 +0.005 / +0.008, pooled n 1326 +0.018 / +0.021 (no fund / fund). Almost all the pooled positive comes from the old coins. |

## By year (12 bp with funding, claim trades)

| Year | n | Mean R |
|---|---|---|
| 2019 | 15 | +0.513 (underpowered) |
| 2020 | 21 | -0.285 (underpowered) |
| 2021 | 15 | -0.272 (underpowered) |
| 2022 | 239 | +0.076 |
| 2023 | 186 | -0.132 |
| 2024 | 107 | -0.057 |
| 2025 | 139 | +0.032 |
| 2026 | 106 | -0.129 |

## By BTC cycle on the signal day (descriptive, with funding)

BASE n 169 -0.112 (CI [-0.256, 0.038]); BEAR n 464 -0.030 ([-0.137, 0.078]); BULL n 195 +0.046 ([-0.111, 0.234]). By BTC brain label: ACCUM-RANGE n 130 +0.077; CAPITULATION n 14 +0.011 (underpowered); DISTRIBUTION n 158 -0.052; MARKDOWN n 249 -0.024; MARKUP n 165 -0.106; RELIEF n 112 -0.021. No label has a CI excluding 0. The trades do not get better when BTC is in a bear cycle.

## By coin (12 bp with funding; n < 30 is underpowered)

Only ICX reaches n 30 (+0.403). The other 44 coins are underpowered (n 7 to 29); means range from -0.396 (XTZ) to +0.386 (SUSHI) with no pattern. Full table in tables.md.

## Power gate

The PRE_REG power gate printed BLOCK (assumed n 150 and sd 1.26; MDE 0.333 R + cost 0.045 vs max plausible gross 0.3; n needed 255). Realised VAL n is 352 and sd 0.88, so the study was better powered than planned: the VAL CI half-width is about 0.12 R. The result is not an under-power story: the CI excludes any fee-net mean above about +0.08 R and the point estimate is below zero.

## Deviations, fixes, and the minor checker findings

- Fix round (FIXLOG.md): BEAR flag higher-low window corrected to the PRE_REG text min Low[t-179..t-60] (the source engine used t-179..t-120); BEAR-true trades 1096 -> 828 (DEV 595 -> 476, VAL 501 -> 352). Funding in the hold always counted (one ONT control row changed). Placebo pool now splits by signal bar like the real trades. 15 tests pass.
- DEVIATIONS.md rows 1-12 apply unchanged, including: the lockout chain runs over all labelled events (BEAR true and false), as the source engine does (a BEAR-false event can lock out a later BEAR-true one; the PRE_REG says "previous KEPT entry"; the coordinator may record a clarification); windows are bar-index based and span 4h gaps in 9 coins; the funding cache ends 2026-10-31 (24 claim trades hold past it, 28 have no print in the hold).
- Minor findings carried to wording: (1) the ONE-YEAR flag was computed by t5_stats.py only on VAL; the DEV and RECENT year shares above were computed from trades.csv and also pass (not ONE-YEAR). (2) Regime-mix coin-day shares for RECENT and pooled, and per-split BTC cycle shares, were not produced by the stats script; stated as not reported rather than patched, since no pass bar depends on them. (3) Verdict naming when FRAGILE / ONE-YEAR blocks a PASS (DEVIATIONS #9) did not arise. (4) LUNA re-denomination: ex-LUNA rows above. (5) ICX and ONT have 9 4h bars on a 2-hour offset in 2018 (inside warm-up, no trade affected). (6) The 'stop' exit label means exit at stop0 on any bar (cosmetic).
- Allowlist rows needed (NOT self-approved, coordinator decides): lookahead_lint prints 3 WARN hits for fullsample-quantile in t5_stats.py (bootstrap CI percentiles and the placebo 97.5th percentile, computed on result arrays, not on a feature or threshold taken from the future). WARN exits 0.
- The stats script ran once, unmodified, with no crash; no pass bar or rule was changed.

## What this does and does not show

- Out of sample by coin, not by calendar time: the 45 fresh coins cover the same weeks as the 22 source coins, so the week-cluster bootstrap treats weeks, not trades, as the sample.
- The source cell's sign and size did not carry over to these 45 coins: gross is about zero (DEV 0.000, VAL -0.024 R), so fees alone push the net below zero, and random bear-phase shorts matched or beat the signal.
- It does not prove the source +0.10 R was noise on the old coins; it says that, if real, it is not a property of this rule on small and mid-cap coins at 12 bp cost. Spot bars stand in for a perp (funding from Binance prints; the entry-notional funding approximation is inherited). 12 bp may understate small-coin slippage, which would only make the net worse.
- Survivorship: the coin list was chosen knowing which coins have 4h history; delisted coins (LUNA, FTT, OMG, WAVES) are kept. For a short, collapse tails help the signal, so any survivorship bias is not obviously against the rule.

## Active today (descriptive, NOT advice)

The cache ends at the 4h bar opened 2026-11-12 20:00 UTC. The last BEAR-true claim signal in trades.csv is ZIL, signal bar 2026-10-30 04:00, already closed out (2026-11-02). Trades still open at the data end are dropped by design, so a signal in the last few bars could not appear in the list; no open signal is asserted. The line is killed regardless.

Next: END: fresh-coin replication failed (pooled net R -0.029 with funding, VAL placebo pct 31); the source +0.10 R does not extend to unseen coins. No testnet card.
