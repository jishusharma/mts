# RESULT: weekly red-streak bounce, LONG only (edge9, 2026-11-14)

Research, not advice. PRE_REG.md governs (code: study.py, make_result.py, test_study.py). Data: Binance spot daily via data-api.binance.vision, 22 coins (BTC, ETH + 20 largest others with >=4y history), weeks Monday 00:00 UTC, last complete week = Mon 2026-11-02. Costs 12 bp round trip (fees.py).

## Verdict
**0 of 48 rows PASS. No entry trigger shows a fee-net edge after N red weeks.** Mean returns are mostly within noise of zero, and the week-cluster CI lower bound is below 0 on every row with >= 30 VAL events. Streak N=6 (the operator's setup) has only 43 VAL events on E1 and is UNDERPOWERED on E2/E3.

Closest to a signal (descriptive, not a pass): DD20 E1 X2 mean 2.6%, CI low -0.2%, p 0.053; S4 E1 XS mean 2.1%, CI low -0.42R, p 0.119; S5 E3 X1 mean 1.8%, CI low -3.5%, p 0.203.

Regime mix: share of VAL events fired while weekly close < 50-week MA (BEAR): S4 80%, S5 86%, S6 93%, DD20 75%. Unknown-regime events (first 50 weeks of a coin) are excluded from the share. VALIDATION (2022-01-01 on) is dominated by the 2022 bear, the 2023 to 2026 chop and the 2026 slide, so the result says little about a bull-phase streak.

## Main table: STREAK-5 (primary), all 12 rows
| Row (event entry exit) | Events DEV/VAL | Win | Mean VAL (R for XS; % in brackets) | CI low (week-cluster) | Placebo p | Without best 3 weeks | DEV mean | Verdict |
|---|---|---|---|---|---|---|---|---|
| S5 E1 X1 | 33/97 | 52% | -0.6% (-0.6%) | -6.8% | 0.726 | -3.9% | 6.7% | FAIL: mean/CI |
| S5 E1 X2 | 33/93 | 43% | 0.7% (0.7%) | -9.2% | 0.552 | -6.6% | 17.0% | FAIL: mean/CI |
| S5 E1 X4 | 33/93 | 44% | 0.7% (0.7%) | -10.9% | 0.635 | -7.8% | 26.1% | FAIL: mean/CI |
| S5 E1 XS | 33/93 | 28% | 0.17R (1.3%) | -0.63R | 0.369 | -0.63R | 1.38R | FAIL: mean/CI |
| S5 E2 X1 | 14/45 | 60% | 0.6% (0.6%) | -4.9% | 0.392 | -3.7% | 2.5% | FAIL: mean/CI |
| S5 E2 X2 | 14/45 | 51% | 1.4% (1.4%) | -6.1% | 0.397 | -5.1% | 8.2% | FAIL: mean/CI |
| S5 E2 X4 | 14/45 | 53% | 1.9% (1.9%) | -4.7% | 0.469 | -2.6% | 6.4% | FAIL: mean/CI |
| S5 E2 XS | 14/45 | 27% | -0.46R (-3.3%) | -0.86R | 0.999 | -0.85R | 0.08R | FAIL: mean/CI |
| S5 E3 X1 | 19/35 | 54% | 1.8% (1.8%) | -3.5% | 0.203 | -2.2% | 2.1% | FAIL: mean/CI |
| S5 E3 X2 | 19/35 | 51% | 2.9% (2.9%) | -4.3% | 0.233 | -3.1% | 5.6% | FAIL: mean/CI |
| S5 E3 X4 | 19/35 | 40% | -1.8% (-1.8%) | -9.7% | 0.742 | -7.0% | 21.2% | FAIL: mean/CI |
| S5 E3 XS | 19/35 | 31% | -0.14R (-3.8%) | -0.49R | 0.804 | -0.37R | 0.67R | FAIL: mean/CI |

S5 E1 VAL events per coin: ICP 8, SHIB 7, SOL 7, BCH 6, ADA 5, AVAX 5, DOGE 5, HBAR 5, LINK 5, LTC 5, XLM 5, XRP 5, BNB 4, NEAR 4, QNT 4, ZEC 4, AAVE 3, ETH 3, UNI 3, BTC 2, TRX 1, XMR 1 (total 97 trades, 36 calendar-week clusters).

## All other rows
| Row (event entry exit) | Events DEV/VAL | Win | Mean VAL (R for XS; % in brackets) | CI low (week-cluster) | Placebo p | Without best 3 weeks | DEV mean | Verdict |
|---|---|---|---|---|---|---|---|---|
| S4 E1 X1 | 71/184 | 45% | -1.0% (-1.0%) | -3.4% | 0.928 | -2.4% | -0.7% | FAIL: mean/CI |
| S4 E1 X2 | 71/176 | 47% | -0.5% (-0.5%) | -6.0% | 0.820 | -3.5% | 2.9% | FAIL: mean/CI |
| S4 E1 X4 | 71/170 | 52% | 3.6% (3.6%) | -6.3% | 0.295 | -3.3% | 12.9% | FAIL: mean/CI |
| S4 E1 XS | 71/170 | 35% | 0.43R (2.1%) | -0.42R | 0.119 | -0.39R | 0.71R | FAIL: mean/CI |
| S4 E2 X1 | 42/121 | 41% | -3.3% (-3.3%) | -9.1% | 0.999 | -4.9% | 1.0% | FAIL: mean/CI |
| S4 E2 X2 | 42/117 | 50% | -0.3% (-0.3%) | -7.1% | 0.736 | -4.1% | 5.7% | FAIL: mean/CI |
| S4 E2 X4 | 42/117 | 49% | 2.2% (2.2%) | -6.6% | 0.512 | -3.0% | 13.6% | FAIL: mean/CI |
| S4 E2 XS | 42/117 | 27% | -0.17R (0.2%) | -0.66R | 0.974 | -0.59R | 0.71R | FAIL: mean/CI |
| S4 E3 X1 | 34/71 | 55% | 1.3% (1.3%) | -1.9% | 0.323 | -1.3% | 5.3% | FAIL: mean/CI |
| S4 E3 X2 | 34/71 | 37% | -1.4% (-1.4%) | -6.4% | 0.856 | -4.5% | 14.6% | FAIL: mean/CI |
| S4 E3 X4 | 34/71 | 42% | -0.6% (-0.6%) | -7.0% | 0.802 | -5.2% | 15.8% | FAIL: mean/CI |
| S4 E3 XS | 34/71 | 34% | -0.06R (-2.5%) | -0.45R | 0.823 | -0.37R | 0.71R | FAIL: mean/CI |
| S6 E1 X1 | 12/43 | 40% | -1.1% (-1.1%) | -5.2% | 0.762 | -3.8% | 7.7% | FAIL: mean/CI |
| S6 E1 X2 | 12/43 | 44% | -3.4% (-3.4%) | -10.2% | 0.949 | -7.3% | 9.7% | FAIL: mean/CI |
| S6 E1 X4 | 12/43 | 37% | -8.1% (-8.1%) | -20.5% | 0.997 | -15.8% | 42.5% | FAIL: mean/CI |
| S6 E1 XS | 12/43 | 33% | 0.08R (-5.9%) | -0.60R | 0.525 | -0.52R | 1.79R | FAIL: mean/CI |
| S6 E2 X1 | 8/15 | 47% | -0.5% (-0.5%) | -4.7% | 0.613 | -3.3% | 7.6% | UNDERPOWERED |
| S6 E2 X2 | 8/15 | 40% | -1.3% (-1.3%) | -12.6% | 0.599 | -9.2% | 19.5% | UNDERPOWERED |
| S6 E2 X4 | 8/15 | 53% | -2.4% (-2.4%) | -12.4% | 0.650 | -6.5% | 12.3% | UNDERPOWERED |
| S6 E2 XS | 8/15 | 27% | -0.26R (-4.1%) | -0.86R | 0.806 | -0.86R | 0.83R | UNDERPOWERED |
| S6 E3 X1 | 8/16 | 50% | 1.3% (1.3%) | -3.9% | 0.366 | -3.2% | -6.4% | UNDERPOWERED |
| S6 E3 X2 | 8/16 | 31% | -3.6% (-3.6%) | -11.2% | 0.853 | -8.8% | -6.0% | UNDERPOWERED |
| S6 E3 X4 | 8/16 | 25% | -1.9% (-1.9%) | -19.9% | 0.701 | -18.4% | -7.8% | UNDERPOWERED |
| S6 E3 XS | 8/16 | 25% | 0.72R (0.2%) | -0.63R | 0.077 | -0.60R | -0.58R | UNDERPOWERED |
| DD20 E1 X1 | 213/395 | 48% | 0.8% (0.8%) | -0.9% | 0.269 | -0.1% | 1.2% | FAIL: mean/CI |
| DD20 E1 X2 | 213/391 | 54% | 2.6% (2.6%) | -0.2% | 0.053 | 1.3% | 3.0% | FAIL: mean/CI |
| DD20 E1 X4 | 213/379 | 45% | 3.0% (3.0%) | -1.8% | 0.363 | 0.0% | 8.3% | FAIL: mean/CI |
| DD20 E1 XS | 213/379 | 33% | 0.24R (1.4%) | -0.20R | 0.271 | -0.15R | 0.26R | FAIL: mean/CI |
| DD20 E2 X1 | 124/231 | 45% | 0.4% (0.4%) | -1.5% | 0.445 | -0.5% | 1.2% | FAIL: mean/CI |
| DD20 E2 X2 | 124/224 | 50% | 0.6% (0.6%) | -2.5% | 0.605 | -0.9% | 4.7% | FAIL: mean/CI |
| DD20 E2 X4 | 124/221 | 44% | 1.2% (1.2%) | -3.7% | 0.729 | -1.4% | 10.6% | FAIL: mean/CI |
| DD20 E2 XS | 124/221 | 23% | -0.23R (-2.3%) | -0.54R | 1.000 | -0.49R | 0.55R | FAIL: mean/CI |
| DD20 E3 X1 | 67/133 | 38% | -0.4% (-0.4%) | -3.7% | 0.718 | -2.7% | 4.1% | FAIL: mean/CI |
| DD20 E3 X2 | 67/133 | 44% | 0.0% (0.0%) | -4.5% | 0.677 | -2.7% | 12.8% | FAIL: mean/CI |
| DD20 E3 X4 | 67/133 | 43% | 3.7% (3.7%) | -4.2% | 0.344 | -2.5% | 20.5% | FAIL: mean/CI |
| DD20 E3 XS | 67/133 | 42% | 0.22R (3.6%) | -0.14R | 0.351 | -0.06R | 0.59R | FAIL: mean/CI |

## BTC: every streak of >= 5 red weeks (Coinbase BTC-USD, 2015 on, complete weeks)
Forward returns: next Monday open to the close of week +1/+2/+4/+8 (no costs). Swept = traded below the last red week's low within 3 weeks; Reclaim = then a daily close back above it.

| Streak start to last red week | Weeks | Open-to-close depth | +1w | +2w | +4w | +8w | Swept / Reclaim |
|---|---|---|---|---|---|---|---|
| 2022-03-28 to 2022-05-23 | 9 | -37.1% | 1.5% | -9.8% | -28.6% | -23.3% | Y / N |
| 2026-01-19 to 2026-02-23 | 6 | -29.8% | 0.3% | 10.7% | 0.3% | 19.6% | N / N |
| 2026-10-05 to 2026-11-02 | 5 | -13.6% | - | - | - | - | N / N |

3 rows only (Coinbase series is gap-free from 2015-07-20): the last row is the ONGOING streak, 5 completed red weeks (the 6th, from 2026-11-09, was still open at data pull), so it has no forward returns. Two finished streaks in 11 years cannot power any test; descriptive only. Neither reclaimed the last red week's low within 3 weeks (2022 swept it and kept falling; 2026 never swept it).

## Caveats
- Survivorship: coins are today's large caps (listed >= 4y), which favours longs; XMR delisted from Binance (data to 2024-02) and is kept for the span it has.
- XS rows: R is net return divided by (entry - stop)/entry; tiny stop distances make R fat-tailed and the XS means are unstable (win rate 23-42%). Read the % return in brackets and the CI.
- DD20 events and E3/E2 entries overlap in calendar weeks across coins (one crash week fires many coins); the CI is week-clustered but the effective sample is a few dozen independent weeks.
- Gate 4 (BH 10%) is applied to the 48 placebo p-values; no row reached it.
- Test: test_study.py has 4 tests; with STUDY_BUG=lookahead (E1 entry one day early) test_streak_event_and_e1_is_next_monday_open fails, without it all pass.
