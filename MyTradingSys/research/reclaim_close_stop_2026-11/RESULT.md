# RESULT: reclaim at the close, stop = close back beyond the level (4h, 1D), DEV only

PRE_REG.md frozen before the run; nothing tuned. Data: BTCUSDT USD-M 4h and 1d klines from data.binance.vision (public), DEV 2022-01..2024-06 (2021-12 warm-up only). Fee-net at 0.10 % round trip (fees.py taker both legs, regime A), no slippage. Table: results_DEV.csv (python run_reclaim.py DEV). Tests: test_reclaim.py (hand-built bars, red before reclaim.py existed).

Answer: **INCONCLUSIVE at 4h and 1D.** The video's timing (enter at the reclaim close, stop on a close back below) gives a positive but not distinguishable-from-zero fee-net mean at 4h, and 1D has too few events to say anything. DEV CI lower bound is not above 0, so the one VALIDATION read was NOT taken (VALIDATION and HOLDOUT unread).

| arm | n | gross % | mean fee-net % | week-block 95 % CI % | verdict |
|---|---|---|---|---|---|
| 4h all DEV | 114 | 0.371 | 0.271 | -0.253 .. 0.805 | INCONCLUSIVE |
| 1D all DEV | 13 | -1.093 | -1.193 | -3.884 .. 1.496 | INCONCLUSIVE (n < 100) |

Descriptive (not verdict arms): 4h long after a low-break reclaim n 62, net +0.427 % (CI -0.251 .. 1.218); 4h short after a high-break reclaim n 52, net +0.085 % (CI -0.659 .. 0.811); 1D low n 5, high n 8 (no CI, n < 10). On 4h, 50 % of trades end on the level-stop, mean hold 4.0 bars, win rate 40 %.

Compared with T058 fade-R at 4h (entry N bars after the break, 4-bar hold: -0.417 % DEV, n 111): the reclaim-close entry with the level stop is +0.27 % on 114 events, a difference of about 0.7 points, but both CIs span zero and the two are the same events entered at different times, so it is not an independent confirmation. This is a point estimate worth a pre-registered follow-up only if more events (other symbols or a longer DEV) can lift n; it is not an edge.

FAIL/PASS scope: none reached. What this does not say: the mirror (trading the failed reclaim, excluded by the card), intrabar stops (stop fills at the bar close, which understates slippage on a gap), maker fees, other swing definitions or caps, other symbols.

## Caveats
Bar-close fills only, no slippage (a stop filled at the close of a bar that already closed beyond the level is optimistic against a live stop order). Events are few and overlap in time; week-block bootstrap. 1D run starts at bar 30 of a one-month warm-up, so the first 1D levels come from the 2021-12 and 2022-01 bars; 13 events in 2.5 years is too few for any reading. Parameters are OURS (PRE_REG.md).
