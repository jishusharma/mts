# POOLED RESULT, 10 coins, frozen rules (PREREG.md; tables.md has every row; fee 10 bp round trip, price + fee only)

**Both rules FAIL the pass bar on VALIDATION. No edge claim, no forecast.**

## 1. Result table
| Rule | Period | n | Mean net | t | Placebo | Verdict |
|---|---|---|---|---|---|---|
| A. Long after 1h drop >= 3 % on 3x volume, 24 h | DEV | 596 events, 198 days | +0.73 % per event, +0.67 % per day | per-day 1.57 | 100th pct (p95 +0.34 %) | not in the bar |
| A | VALIDATION | 132 events, 69 days | -0.43 % per event, -0.19 % per day | per-day -0.36 | 44th pct per day, 20th per event (p95 +0.33 %) | FAIL (t 2.5 missed, mean negative, placebo not beaten; 69 days is enough n) |
| B. 4h Donchian 55/20, all trades | DEV | 415 trades, 19 months | +0.31 % per trade, +0.74 % per month | monthly 0.74 | 67th pct (p95 +0.98 %) | not in the bar |
| B | VALIDATION | 354 trades, 38 months | +0.59 % per trade, +0.84 % per month | monthly 1.11 | 80th pct (p95 +1.15 %) | FAIL (t 1.11 under 2.5, placebo not beaten) |

## 2. Rule A in plain words
- DEV looked good (596 events, t 1.57 per day, placebo 100th pct). VALIDATION turned negative: buying a 3 % drop on 3x volume and holding 24 h lost money after fees on 132 events (69 days).
- VALIDATION is mostly BTC and ETH: BTC n 19 (+1.27 %), ETH n 54 (+0.20 %). The eight alts only have 2024-03-20..2024-06-30 in VALIDATION (n 3 to 11 each) and all are negative (-0.1 % to -2.8 %). That alt window is three months.
- DEV per coin: positive on 9 of 10 coins (ETH -0.41 %); per-coin t above 1.8 only for ADA (n 56, 1.98) and DOGE (n 76, 1.80).
- Events cluster by day (596 events on 198 days, 132 on 69), so day pooling cuts n by about 2.5x; that is the honest n.

## 3. Rule B in plain words
- Long side VALIDATION: 187 trades, +2.69 % per trade, monthly t 0.84 (per-trade t 2.05), placebo pct 80 (placebo long is +1.91 %, the long bias of the market). Not separable from being long.
- Short side VALIDATION: 167 trades, -1.76 % per trade, monthly t -1.86, placebo 29th pct. DEV short was +1.08 % (216 trades, per-trade t 1.38, monthly 0.78); it flipped sign.
- Buy-and-hold on the same windows (mean of ten coins): VALIDATION +122 % against the long side compounded +50 %; long side beat buy-and-hold on 2 of 10 coins (BTC +105 % vs +191 %, SOL +174 % vs +539 %, ETH +60 % vs +47 %). The short side stand-alone: -26 % compounded, beat buy-and-hold on 1 of 10. DEV: coin buy-and-hold mean -59 %; long side -19 %, short side +15 % compounded.
- Reference: BTC alone in the earlier study had n 85, t 0.97; ten coins pooled give monthly t 1.11.

## 4. Method notes (DECISION, OURS unless stated)
- Data: 1m perp candles on disk, BTC and ETH 2022-01..2026-09, eight alts 2022-01..2024-06; bars built per PREREG. A DEV entries before 2024-02-19, VALIDATION from 2024-03-20; B DEV bars to 2023-07-05 16:00, VALIDATION from 2023-08-04 20:00 (copied from the BTC studies).
- "Trailing average" in the order was implemented as the median of the previous 720 bars, as flow_test.py does. Rule A long side only (as ordered).
- Monthly t for B: a trade goes to the calendar month of its exit; month value = mean net of trades exited that month.
- Rule B final open trade of each segment is closed at the last close, as trend.py. Rule A had 0 skipped signals (no bar gaps).
- Placebo for B keeps trade direction, so the long placebo carries market drift; it does not remove the long bias (known from the BTC study).
- Funding not included (not on disk for alts). 100 studies are listed in TESTED_MAP.md, so a pass would have needed more than t 2; none reached it.

Regime mix: A DEV 36% bull / 23% bear / 40% range (99 weeks); A VAL 30% bull / 25% bear / 45% range (132 weeks); B DEV 28% bull / 34% bear / 37% range (67 weeks); B VAL 36% bull / 20% bear / 44% range (165 weeks). Label: BTC 13-week return above +15 % bull, below -15 % bear, else range.
