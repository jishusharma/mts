# OPERATOR source: weekly low + round number sweep and reclaim (2026-10-15, shots 4e8ef8d3f2e5 and 3016b2621f9d)

Label: OPERATOR (the operator's own reading, NOT SOURCED, NOT a Malkan/Tom/Fabio quote).
Provenance of this text: the coordinator (local_1c4041fd, "Fable 5.1 model usage and optimization") relayed it to this session as a SHORT PARAPHRASE, not a transcript. Everything below is the relay's wording. If the operator's raw words are saved elsewhere they replace this file.
Charts: shot `4e8ef8d3f2e5` is a BTCUSDT 1m CoinGlass chart taken at about 14:08:54Z (forming 14:08 bar, countdown 00:06). Shot `3016b2621f9d` (registered 14:11Z as the follow-up chart) is NOT a chart: it is a screenshot of the Claude desktop "New session" screen, so the follow-up numbers below come from the relay only and are checked against our klines instead (`../evidence/weekly_low_sweep_checks_output.txt`).

## Claims as relayed, one per line

- W1: the prior-week low (80,393) and today's low (80,091) were taken, then 80,000, down to a low of 79,732.3 at about 13:53Z, 20 minutes after the US open.
- W2: open interest rose into the break (about 94.1K), so shorts were adding.
- W3: price reclaimed 80K within about 10 minutes.
- W4: at 14:11 it broke the 81,146.6 pre-open top, to 81,293; open interest fell to 93.28K (shorts covering); net delta +488; 1m RSI 77.
- W5 (the operator's question): when a weekly low and a round number break together, what does price do, and what patterns should we compare to set backtest parameters?

## Study design as relayed (all parameters OURS, chosen on DEV)

- Event: a break of the prior-week low and/or a round-1000 level.
- Outcomes: A reclaim within k minutes (failed breakdown); B acceptance below (m closes below on 1m/5m); C range.
- Measure: P(A/B/C); after a reclaim, MFE/MAE and whether the prior swing high or a pre-open top gets hit.
- Condition on: OI change during the break; CVD/net-delta flip; session (US-open window vs other); HTF stretch (1h/4h RSI under 35, price below the 4h/1d lower BB); level stacking (weekly low plus round number within X% vs a single level).
- Penetration depth, reclaim window k, acceptance m and stacking distance are OURS.
