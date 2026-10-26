# P1 - Cost floor and passive-fill adverse selection (BTC perp)

Session: MTS-2026-10-06-1300Z-CLD-ANA-research-agenda-p1 (Cloud, static, read-only on live paths). Agenda item P1 of the research agenda published 2026-10-06.
Script: `research/p1_cost_floor/p1_cost_floor.py`, output `research/p1_cost_floor/results.json` (reruns in seconds). Fees from `backtest/fees.py` (single source, B081).
Tag: research only. No engine parameter, no rule, no signal. Nothing here is a trading claim.

## 0. Question

Almost every tested candidate has gross edge about zero and fees make it negative (TOM_CORE_BT.md, T055_BT_c1..c3.md). How much of the loss is the fee schedule, and how much of that can passive (maker) execution remove once adverse selection is charged?

## 1. Pre-registration (fixed before the run)

- Metric A: round-trip fee as a multiple of the stop distance (R), per fee profile. Arithmetic only.
- Metric B: share of rolling windows (5m, 15m, 60m) whose absolute move exceeds 5, 10, 12, 20 bp.
- Metric C: mean forward return, from the limit price, of signal-less passive orders (buy below / sell above the prior 1m close by 0, 2, 5 bp), filled by "touch" (next-bar low/high reaches the price) or "through" (strictly trades beyond it), held 5m or 15m. Both sides pooled so drift cancels. Reported per day.
- Decision rule: if the mean adverse selection in C is smaller than the maker-vs-taker fee saving in A, passive execution is worth modelling per candidate; if it is larger, it is not. No threshold tuned on the result.

## 2. Data

`runtime/orderflow_live/2026-09-29..2026-10-03.csv`: 6,605 one-minute BTCUSDT bars, 2026-09-29 00:00Z to 2026-10-03 17:05Z, one 3h02m gap (windows never cross it). Only 4.7 days, one regime. Tom replay episodes from `REPLAY_2026-10-04_05.md` are cited, not recomputed.

## 3. Results

### A. Fee cost in R (fraction of price / stop distance)

| stop distance | 0.20% | 0.30% | 0.43% | 0.60% | 1.00% |
|---|---|---|---|---|---|
| taker/taker, 10 bp RT (Deribit or Binance) | 0.50R | 0.33R | 0.23R | 0.17R | 0.10R |
| Binance maker entry + taker stop (loss leg, 7 bp) | 0.35R | 0.23R | 0.16R | 0.12R | 0.07R |
| Binance maker/maker (win leg, 4 bp) | 0.20R | 0.13R | 0.09R | 0.07R | 0.04R |
| Deribit maker entry + maker target (win) | 0 | 0 | 0 | 0 | 0 |
| Deribit maker entry + taker stop (loss) | 0.25R | 0.17R | 0.12R | 0.08R | 0.05R |

The 0.43% column reproduces the "about 0.23R per trade" in TOM_CORE_BT.md.
Breakeven win rate at 1:1 R:R and a 0.43% stop: 61.6% taker/taker; 56.2% Binance maker-win/taker-stop-loss; 52.8% Deribit maker-win/taker-stop-loss. So moving to maker removes about 9 points of required hit rate on Deribit, if every order fills.

### B. Typical move vs the cost floor (4.7 days)

| window | median abs move | > 5 bp | > 10 bp | > 12 bp | > 20 bp |
|---|---|---|---|---|---|
| 5m | 5.0 bp | 50% | 25% | 19% | 7% |
| 15m | 8.1 bp | 65% | 43% | 36% | 19% |
| 60m | 17.1 bp | 82% | 66% | 61% | 45% |

A 12 bp taker round trip exceeds the median 15m move. Scalp-horizon candidates need a gross edge larger than the typical move itself.

### C. Passive fills with no signal (mean bp from limit price, sd about 12 to 25 bp)

| order | fill rule | hold | fills | mean bp |
|---|---|---|---|---|
| at close | touch | 5m / 15m | 12,980 / 12,942 | -0.08 / -0.09 |
| at close | through | 5m / 15m | 11,274 / 11,244 | -0.56 / -0.62 |
| 2 bp away | touch = through | 5m / 15m | 5,722 / 5,719 | -0.73 / -0.50 |
| 5 bp away | touch = through | 5m / 15m | 2,296 / 2,296 | -0.84 / -0.95 |

Daily means keep the same sign at 0 and 2 bp offset on every day except the last partial day at 15m; at 5 bp offset the daily means swing between -2.0 and +2.0 bp, so that row is noise-level. Orders at close are filled 98% of the time by touch and 85% by trade-through; 2 bp away fills about 43%, 5 bp away about 17%.

## 4. Reading

1. Signal-less adverse selection is about 0.1 to 1 bp. The maker-vs-taker fee saving is 5 to 10 bp round trip. By the pre-registered rule, passive execution is worth modelling per candidate.
2. This is a lower bound on adverse selection. A signal-triggered entry (for example, after a CVD or sweep event) fills when informed flow is moving, which this test does not capture.
3. 1m bars cannot show queue position. "Through" fills are a rough proxy for fills that need price to trade beyond the level; real fill rates for resting orders at a level will be lower, and the missed fills are the trades that ran away. The Tom replay already shows the effect: 268 to 300 of 930 episodes never filled (`REPLAY_2026-10-04_05.md`).
4. Fee schedule discrepancy: `fees.py` carries Deribit taker 5 bp per side (API-verified 2026-09-26) but T055b L22-23 and `LEGACY_FABIO_*` use 7 bp RT taker and a -3 bp maker rebate. Fabio tests still use the legacy numbers. This is the operator decision already noted in `fees.py`; it changes Fabio's cost by about 3 bp round trip.

## 5. Limits

- 4.7 days, one regime, no signal. It sizes the fee and adverse-selection terms; it says nothing about edge.
- No funding, no slippage on stop fills, no partial fills, no latency.
- Per-day sample is 1,000s of overlapping orders, so effective n is far lower than "fills"; no CI is claimed.

## 6. Next steps (for the owner of each path)

- Desktop/NUC: rerun C on `F:/MTS/data/orderflow_1m` (2024-12 onward) with aggTrades-based queue/through logic, then apply the fill model to the C1 1h and T063 candidates as they mature.
- Operator: decide the Deribit fee number Fabio carries (section 4.4).
