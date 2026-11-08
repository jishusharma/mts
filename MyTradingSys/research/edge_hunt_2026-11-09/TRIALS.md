# Edge hunt 2026-11-09: fixed trial list (written before any result)

**m = 15 confirmatory trials for the whole wave. Holm correction on the one VALIDATION read uses m = 15, whatever number of trials reaches VALIDATION. No trial may be added, dropped, split or re-cut after a worker starts. Everything a worker reports beyond its own trial ids is exploratory and cannot promote.**

Frozen 2026-11-09 by edge-hunt-plan-opus-1109. Shared rules (splits, fees, R, statistics, verdicts) are in PLAN.md s5. Full rules are in each worker brief (workers/<slug>.txt). Labels: S = SOURCED, O = OURS.

| Id | Worker | Hypothesis (one line, primary statistic = mean fee-net R per trade, day-clustered SE) | Data / TF | Fee regime |
|---|---|---|---|---|
| T01 | eh-h1-spinning-top-7star | Malkan's 7-star spinning top (small body, long shadows on both sides, high volume, at a 20-bar extreme; buy above the high / sell below the low, stop at the other extreme [S]; thresholds [O]) has net R > 0 at a 3R target / 20-bar time stop [O], both sides pooled | BTC+ETH 4h and 1d | A |
| T02 | eh-h2-malkan-star-grades | 7-star MTF long: monthly RSI14 >= 60 and daily RSI14 < 40 with a daily bullish divergence [S Wvq1TZh8aF0:8]; stop under the divergence low [O], target 4R (5-star 1:2+ doubled [S]) | BTC+ETH 1d (+1M) | A |
| T03 | eh-h2-malkan-star-grades | 5-star MTF long: monthly > 60, weekly > 60, daily RSI pulls back to 40 (low within 40 +- 2 [O]) and prints a green reversal candle [S 2HcJ3NeZmEQ:8]; stop under the candle low [O], target 2R [S 1:2+] | BTC+ETH 1d (+1w, 1M) | A |
| T04 | eh-h3-first-touch-sweep | A first-touch sweep and reclaim (within 3 bars) of a prior-day or prior-week high/low, faded from the reclaim close, stop at the sweep extreme, target 2R, 96-bar time stop, has net R > 0 | BTC 15m futures | A |
| T05 | eh-h4-speed-time-at-level | Fade of a prior-day high/low touch in the cell "fast in (top tercile of 12-bar speed on DEV) + reclaim within 3 bars + at most 2 bars spent within 0.2 % of the level" has net R > 0 (stop at the extreme, 2R, 96 bars) | BTC 15m futures | A |
| T06 | eh-h5-rsi-ma-cross-trigger | RSI14 back under its SMA14 and under 60 after a >= 60 reading within 6 bars (mirror over 40 after <= 40), confirmed when the next bar trades through the prior bar's open; stop at the 6-bar swing, 2.5R, 30 bars; both sides pooled | BTC+ETH 4h | A |
| T07 | eh-s1-malkan-level-short-4h | The operator's 5-layer level short (READING.md stack: level, divergence or lower-high sweep, RSI trigger, WaveTrend, daily/weekly RSI failing at 60), stop above the swing wick, target 2.5R / 30 bars | BTC+ETH 4h (spot 2017-08+) | A |
| T08 | eh-s1-malkan-level-short-4h | The same stack mirrored as a long (level support, bullish divergence or higher-low sweep, RSI over its MA over 40, WT cross up, daily/weekly RSI recovering over 40) | BTC+ETH 4h | A |
| T09 | eh-s2-wick-level-context | Long wick at an HTF support (prior-week low, prior-month low, unbroken daily pivot low) on first touch, sweep volume >= 3x median, reclaim <= 3 bars, not a knife; maker limit at the level, stop at the sweep extreme, target the next HTF level if >= 2.5R (else skip), break-even at +1R | BTC 15m futures | B |
| T10 | eh-s2-wick-level-context | T09 mirrored: short the upper wick at an HTF resistance | BTC 15m futures | B |
| T11 | eh-s3-rsi-line-confluence | RSI14 bounce off 40 (from above) or 60 (from below) when at least one other TF of {1h, 4h, 12h, 1d} sits within +-2 of the same line; stop beyond the approach swing, 2.5R, 48 bars | BTC+ETH 1h and 4h | A |
| T12 | eh-s3-rsi-line-confluence | T11 restricted to bounces against the higher-timeframe bias (the study found agreeing-bias bounces hold 10-14 points less) | BTC+ETH 1h and 4h | A |
| T13 | eh-o1-confluence-dose-response | At level touches, the net R of a fade rises with the operator-confluence score 0-5 (sweep, line confluence, wick/swing divergence, RSI-MA trigger, HTF RSI failing at 60/40): slope > 0, one-sided, day-clustered | BTC+ETH 1h and 4h | A |
| T14 | eh-o2-phase-lens | Level fades (1h sweep-reclaim of the prior-day high/low, stop at the extreme, 2R, 24 bars) have net R > 0 in the "balance" phase cell (weekly RSI14 between 40 and 60 and outside the cycle-clock peak/bottom windows) | BTC 1h futures | A |
| T15 | eh-o2-phase-lens | The Malkan S1 4h RSI-40 bounce long (malkan_40_60.py) has net R > 0 in the cycle-clock accumulation and bull phases (bottom -> halving -> peak) with weekly RSI14 >= 40 | BTC+ETH 4h | A |

eh-f1-testnet-design carries no trial: it designs the promote/kill rule and the testnet order for whatever passes.

## Reading rule
- DEV screen per trial: n >= 30, mean net R > 0, 95 % CI lower bound > 0. Only then the single VALIDATION read.
- VALIDATION: one-sided p of mean net R > 0, Holm at m = 15 across T01-T15. PASS -> testnet-forward raw card; never a longer backtest.
- Known overlap: T11 and T12 test an effect found on the same DEV span (rsi_40_60_line_behaviour, DEV 2017-08..2024-06), so only their VALIDATION read is independent evidence.
