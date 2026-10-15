INCONCLUSIVE

# RESULT: gross-effect screen on DEV (primary cell d=1, h=60, C=0.14 %). Verdict above is per PRE_REG.md section 4, one run.

## Primary cell (mean of G after funding, % of notional; SE day-clustered)
| arm | n | mean | SE | t_cost | MDD (% of clip) |
|---|---|---|---|---|---|
| T | 40 | -0.0568 | 0.1304 | -1.51 | 8.47 |
| notF | 1399 | -0.0067 | 0.0253 | -5.79 | 205.82 |
| C | 1439 | -0.0081 | 0.0246 | -6.03 | 214.21 |

DIFF (T - notF) = -0.0500 %, SE 0.1350, t_DIFF = -0.37. Buy-and-hold DEV max drawdown = 67.80 %. MDE (80 % power) for arm T = 2.8 x SE = 0.3650 %.

## Benchmarks (report only)
Cash = 0. Arm T total net = -7.87 (sum of %-of-clip nets, cost C). Buy-and-hold DEV return 35.8 %, scaled by time in market f=0.0018 (n x h / DEV minutes) = 0.07. Arm C total net = -213.16.

## Participation
Median 1m quote volume 4,442,430 USDT; clip 1,000 USDT = 0.0225 % of it (not size-limited).

## Per-side rows at the primary cell and decay grid
Full 3 arms x ALL/SHORT/LONG x 5 d x 6 h table: decay.csv (30 cells per arm). Primary-cell per-side rows:

| arm | side | n | mean_G | net_C | t_cost | net_Cm (filled only) | fill rate |
|---|---|---|---|---|---|---|---|
| T | ALL | 40 | -0.05528 | -0.19678 | -1.509 | -0.14678 | 1.000 |
| T | SHORT | 18 | -0.13286 | -0.27397 | -2.081 | -0.22397 | 1.000 |
| T | LONG | 22 | 0.00820 | -0.13361 | -0.635 | -0.08361 | 1.000 |
| notF | ALL | 1399 | -0.00571 | -0.14674 | -5.792 | -0.18246 | 0.900 |
| notF | SHORT | 716 | 0.01346 | -0.12760 | -3.302 | -0.16008 | 0.904 |
| notF | LONG | 683 | -0.02581 | -0.16681 | -4.967 | -0.20612 | 0.896 |
| C | ALL | 1439 | -0.00709 | -0.14813 | -6.027 | -0.18136 | 0.903 |
| C | SHORT | 734 | 0.00988 | -0.13119 | -3.486 | -0.16181 | 0.906 |
| C | LONG | 705 | -0.02475 | -0.16577 | -5.139 | -0.20187 | 0.899 |

## Funding, drops, decisions
Funding NOT_IN_DATA (F:/MTS/Dumps/backtest/raw_fund absent): flat 1 bp per encounter whose [entry, exit] contains a 00/08/16 UTC settlement; verdict statistics use G minus funding.
dropped_missing_bars (primary cell, incl. exit beyond DEV end, never read): 1 of 1440.
DECISION (OURS): INCONCLUSIVE tested after PASS_FLOW and PASS_CONTROL on n_T; maker readout counts a fill when a bar after the entry bar trades through p_in by 0.1 USDT before the exit bar; arm MDD is the sum-of-nets drawdown in % of one clip vs BH in % of price.

## Count section (no outcome column)

Files: 30 (SHA256 in DATA_MANIFEST.csv). Bars present 1313280 of 1313280; missing 0.
Gaps: 0; longest 0 bars.
Missing bars per month: none
Ledger encounters (after shared cooldown): n_T=40, n_notF=1400, n_C=1440; SHORT 735, LONG 705.
With bars present for the primary cell (d=1,h=60): n_T=40, n_notF=1399, n_C=1439; dropped_missing_bars (or exit beyond DEV end)=1.
Encounters per day: mean 1.579, max 11, days with >=1: 485 of 912 (per-day list: counts_per_day.csv).
OI: NOT_IN_DATA in DEV. Funding: funding NOT_IN_DATA (flat 1 bp per straddling encounter).

FAIL/INCONCLUSIVE: stop; no detector, chart, layer or management work follows on this family.
