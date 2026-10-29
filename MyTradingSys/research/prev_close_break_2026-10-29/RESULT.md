# Previous-close break, any TF (operator idea, 10-29): fee-net DEV backtest

Setup:
- **Data:** Binance BTCUSDT perp 1m, 2022-2025 (DEV). 2026 is the holdout and was not read.
- **Costs:** 12 bp round trip (taker + slippage).
- **Rules:** see the `study.py` header; `results.csv` has all 48 rows.

## Answer

**The rule loses after fees on every TF, exit and filter tested.** Before fees it makes +0.01% to +0.12% per trade. Fees are 0.12%.

| TF | Best variant | n | Win rate | Gross per trade | Net per trade | Median stop distance |
|---|---|---|---|---|---|---|
| 5m | mid-cross filter, exit on mid cross | 20,764 | 17% | +0.017% | -0.103% | 0.19% |
| 15m | mid-cross filter, exit on mid cross | 8,130 | 17% | +0.030% | -0.090% | 0.27% |
| 1h | mid-cross filter, exit on mid cross | 2,132 | 19% | +0.057% | -0.063% | 0.49% |

These rows use a 5 bp trigger. A 0 bp trigger only fires on bars that gap away from the previous close, which is a different and much smaller sample.

## Why it does not work as stated

1. **It fires on almost every candle.** The new candle opens at the previous close, so it trades on both sides of it almost every bar. Nothing in the rule says which bars are the trend bars.
2. **The stop is tiny.** The previous candle's low or high is 0.06-0.5% away. The 0.12% fee is 25-200% of the risk, so a 15-30% win rate cannot pay for it.
3. **The trailing stop exits too early.** On the 10-29 example (20:00Z short at 80,849), the trail on the previous candle's high exited at 20:10 at 80,436. That was +0.39% net, but price went on to 78,159 (your arrow). Holding until a close back across the BB mid rides such moves, but across all trades it did no better.
4. **Larger TFs come closer to break-even.** Fees become a smaller share of the stop. The best case was 1h with the mid-cross filter.

## What would have to be added (OURS, next tests)

- **A filter for "this bar starts an expansion."** Candidates: the bar after a coil (C17), a pierce with strong force (C18), or OI and CVD agreeing (Fabio F-CVD7).
- **Gross must beat 0.12%.** That needs about a 3x better gross; this is the bar any filter has to clear.

## The operator's rule as he walked it (shot 8faf2cac14be, 10-29 22:25Z). This is the spec for the next test.

He corrected two things the first test missed.

**Context picks the trade.**
- The setup candle touches the BB mid coming back from outside the band. Here it was the 21:35 green candle: high 79,688, mid 79,641.
- He takes only the side away from the mid (here short). The test above took every candle, both sides.

**The take-profit is at the band, not the trailing stop.**
- Exit (or part) when price nears the lower band.
- The "clearance" matters: on 10-29 the low was 78,627 against a band of 78,541, so it stopped 86 points (0.11%) short of the band.

Spot 5m walk-through, 10-29:

| Candle | Event |
|---|---|
| 21:35 green | Setup; touched the mid |
| 21:40 red | Crossed below 79,553: short at 79,553, stop 79,688 (0.17%) |
| 21:45 green with wick | Stop = 21:40 high 79,556, not hit; still in |
| 21:50 | Stop = 21:45 high 79,279; this candle's high was 79,311, so the trailing stop was tagged by 32 points (spot; the perp may differ) |
| 22:05 | Low 78,627, lower band 78,541 |

Open questions for the backtest, to be fixed in the pre-reg before any run:
- **Stop.** A fixed stop at the setup candle's high, or trailing to each previous candle's high?
- **Take-profit.** At what distance from the band? Set it from a measured distribution of how close moves from the mid stop to the band.
