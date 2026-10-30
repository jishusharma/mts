# RESULT: Setup Alpha / Setup Beta v2 (B163 re-run, NO-SOURCE)

PRE_REG.md (commit 14502d93b) was frozen before this run; run once, rules unchanged. Data BTCUSDT 1m 2020-01..2025-06-30 (last bar 2025-06-30 23:59:00+00:00); HOLDOUT 2025-07+ never loaded. Fees 0.05% per side taker on every leg, funding included, no slippage. DEV 2022-01-01..2024-06-30, VALIDATION 2024-07-01..2025-06-30. Numbers: result_numbers.json (setup_v2.py).

Answer: Alpha FAILS the frozen rule (beats buy-and-hold in DEV, loses to it in VALIDATION). Beta primary arm S1 is INCONCLUSIVE by the frozen n rule (DEV n 50 < 100, VAL n 23 < 30), but every one of the 8 Beta cells is negative after fees and the large plain-sweep arms are negative at t from -4.8 to -9.7. v1's Beta n of 708,240 was per bar; here n is sweep events (one per day and side).

## Verdict arms

| arm | n | mean R | SE R | verdict |
|---|---|---|---|---|
| Alpha DEV (entries; joint rule with VAL) | 4 | 6.178 | - | FAIL |
| Alpha VAL (entries; joint rule with DEV) | 11 | 0.146 | - | FAIL |
| Beta S1 session+CVD DEV | 50 | -0.583 | 0.230 | INCONCLUSIVE |
| Beta S1 session+CVD VAL | 23 | -0.697 | 0.217 | INCONCLUSIVE |

Units: R fee-net, funding included. Alpha's FAIL is the joint rule (Sharpe and max drawdown better than buy-and-hold in both splits; it failed in VAL). INCONCLUSIVE: the frozen rule needs DEV n >= 100 and VAL n >= 30 for PASS or FAIL.

FAIL means stop: Alpha = daily close > SMA200 long-flat, taker fees, funding, BTCUSDT 2022-2025 as a drawdown or return improvement over buy-and-hold; it says nothing about other filters (EMA7/RSI2, Supertrend), other assets or shorting. FAIL/INCONCLUSIVE: stop; Beta = PDH/PDL sweep, kline-CVD absorption, 1.5R/90 min bracket, taker fees; it says nothing about true aggTrades CVD, 5m structure-shift entries, other levels or maker entries.

## Alpha (daily SMA200 long-flat) vs buy-and-hold, fee-net, funding included

| split | days | arm | n entries | win | mean R | CAGR | Sharpe | max DD | time in market |
|---|---|---|---|---|---|---|---|---|---|
| DEV | 912 | Alpha | 4 | 50% | 6.18 | 45.4% | 1.22 | 21.5% | 52% |
| DEV | 912 | Buy-and-hold | 1 | 100% | - | 6.1% | 0.38 | 68.0% | 100% |
| VAL | 365 | Alpha | 11 | 27% | 0.15 | 5.3% | 0.32 | 32.1% | 70% |
| VAL | 365 | Buy-and-hold | 1 | 100% | - | 62.7% | 1.23 | 29.0% | 100% |

Alpha R = net trade return / (2 x ATR14 / entry close); DEV has 4 entries, VAL 11, so the per-trade columns are INCONCLUSIVE as an edge claim (n < 30); a position open at a split end is closed there with a fee. Alpha cut drawdown in DEV (21% vs 68%) and had the better Sharpe, then lagged buy-and-hold in 2024-25 (CAGR 5% vs 63%).

## Beta (15m PDH/PDL sweep, one entry per sweep event)

| arm | split | events | trades | win | mean R net | SE | t | median fee in R |
|---|---|---|---|---|---|---|---|---|
| S1 session + CVD (PRIMARY) | DEV | 50 | 50 | 30.0% | -0.583 | 0.230 | -2.54 | 0.22 |
| S1 session + CVD (PRIMARY) | VAL | 23 | 23 | 21.7% | -0.697 | 0.217 | -3.21 | 0.19 |
| S0 session plain | DEV | 344 | 344 | 37.8% | -0.470 | 0.065 | -7.19 | 0.25 |
| S0 session plain | VAL | 148 | 148 | 34.5% | -0.669 | 0.139 | -4.82 | 0.39 |
| A1 all hours + CVD | DEV | 92 | 92 | 39.1% | -0.533 | 0.186 | -2.86 | 0.22 |
| A1 all hours + CVD | VAL | 53 | 53 | 34.0% | -0.456 | 0.141 | -3.23 | 0.20 |
| A0 all hours plain | DEV | 605 | 605 | 39.0% | -0.513 | 0.053 | -9.75 | 0.28 |
| A0 all hours plain | VAL | 269 | 269 | 37.2% | -0.567 | 0.090 | -6.28 | 0.34 |

Dropped (window not fully in data) and skipped (entry at or past the stop) are 0 in every cell. CVD vs plain: S1 DEV -0.58 R against S0 DEV -0.47 R (S1 not better); the kline-CVD absorption test adds nothing over a plain sweep reclaim here. Median round-trip fee is 0.19-0.39 R (stops are the wick), so taker fees alone take 0.2-0.4 R of every trade.

## Limits
- Taker-buy kline CVD, not aggTrades; 5m structure-shift entry not used (entry = next 15m open). Equal highs/lows dropped (v1 swing code was the look-ahead). No slippage on stop fills.
- lookahead_lint --new: 0 FAIL. test_beta_events.py: single planted sweep gives exactly 1 event, no bar after the entry bar used; the same check fails on the v1 beta_sweep.py logic.
- DECISION (OURS): PDH/PDL only, first sweep per day and side, 8-bar absorption window, 0.1 stop buffer, 90 min time stop; all frozen in PRE_REG.md.
