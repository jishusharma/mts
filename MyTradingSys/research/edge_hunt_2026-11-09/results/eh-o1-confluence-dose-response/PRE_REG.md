# PRE_REG eh-o1-confluence-dose-response (trial T13)

Frozen 2026-11-09 before any return was computed. Worker brief: workers/eh-o1-confluence-dose-response.txt. Wave rules: PLAN.md s5, TRIALS.md.

Inputs seen: the wave-2 results of eh-s1, eh-s3 and eh-h5 had NOT shipped (`git log origin/fast-track -- .../results` shows only eh-h1..h4). I read only their BRIEFS (workers/eh-s1-*.txt, eh-s3-*.txt, eh-h5-*.txt) and implemented their layer definitions from the brief text. I saw no DEV result of those workers.

## Hypothesis (T13)
At level touches on BTC/ETH 1h and 4h, the fee-net R of a fade rises with the operator-confluence score 0-5. One slope test: OLS of net R on score, SE clustered by UTC day, both TFs and both symbols pooled, one-sided H1 slope > 0.

## Rules (copied from the brief; frozen)
| Item | Rule | Label |
|---|---|---|
| Event | a 1h or 4h bar that trades into a level: a confirmed swing pivot (5 each side) high for shorts / low for longs, unbroken by a close, price within 0.3 % of it; one event per level per 24 bars | OURS |
| Score (0-5), each layer computed on bars up to the event bar | S1 sweep: the bar trades beyond the level and closes back inside / S2 line confluence: RSI14 of the trade TF within +-2 of 60 (short) or 40 (long) AND at least one other TF of {1h, 4h, 12h, 1d} within +-2 of the same line / S3 divergence: eh-s1 layer 2 (wick or close, swing to swing, 3..20 bars) / S4 trigger: eh-h5 signal bar on this or the previous bar / S5 HTF: eh-s1 layer 5 | each layer's label as in its source brief |
| Entry | the event bar close (taker), fade direction (short at highs, long at lows) | OURS |
| Stop / exit | the extreme of the last 6 bars beyond the level / 2.5R or 30 bars | OURS |
| Primary test (T13) | OLS of net R on score (0-5) with SEs clustered by UTC day, both TFs and symbols pooled; one-sided H1: slope > 0. DEV screen for T13 = slope > 0 with its 95 % CI lower bound > 0 AND the score >= 3 group having n >= 30 and mean net R > 0. VALIDATION once (Holm m = 15) | OURS |
| Exploratory | mean net R per score level; leave-one-layer-out slopes; per TF | - |
Score distribution first (count pass): if score >= 3 has < 30 DEV events, T13 is INCONCLUSIVE by rule.

## Layer definitions copied from the source briefs (text as written there)
- S3 = eh-s1 layer 2, divergence half only (the lower-high sweep half is S1 here): "two confirmed swing highs (pivot 3) 3..20 bars apart, the later one a higher high on the WICK or on the CLOSE, RSI lower at the later one" (eh-s1 brief, Exact rules, layer 2; READING.md; 20-bar cap OURS there). Long mirror: two swing lows, later one a lower low on wick or close, RSI higher.
- S4 = eh-h5 signal bar: armed = RSI14 >= 60 on any of the last 6 closed bars; signal bar = RSI14 closes below its SMA14 AND below 60 (long mirror: <= 40 armed, above SMA14 and above 40) (eh-h5 brief; 60/40 SOURCED malkan_40_60.py MLK-R1, 6 bars OURS there). The confirmation bar is NOT required (the brief says "signal bar").
- S5 = eh-s1 layer 5: "last closed daily RSI14 < 60 and its prior close was higher, OR the last closed weekly RSI14 fell from >= 60 to < 60"; long mirror "daily RSI > 40 and rising or weekly back over 40" (eh-s1 brief).
- S2 cushion +-2 and the TF set {1h, 4h, 12h, 1d} as in the eh-s3 brief (cushion OURS there). Other TFs use their last CLOSED bar.

## OURS fills (chosen once, never tuned)
1. Pivot (5 each side): bar j is a swing high when high[j] > every high of j-5..j-1 and high[j] >= every high of j+1..j+5 (mirror for lows). Confirmed after bar j+5 closes; first usable on bar j+6.
2. "Unbroken by a close": no close above (short) / below (long) the level on any bar after the pivot up to and including the event bar. A bar that closes beyond the level kills the level and is not an event.
3. "Within 0.3 %": event bar high >= L x (1 - 0.003) (short); low <= L x (1 + 0.003) (long). The high may exceed L (that is a sweep, S1).
4. Several live levels touched by one bar on one side: one event, the level nearest the bar's extreme (high for shorts, low for longs); every touched level starts its 24-bar cooldown. Both sides may fire on the same bar.
5. Levels have no age limit (live until broken by a close).
6. S1 strict: high > L and close < L (short); low < L and close > L (long).
7. S2: trade-TF RSI14 of the event bar within [58, 62] (short) / [38, 42] (long); other TFs (the set minus the trade TF) as of the event bar close, last closed bar only. 4h from the native 4h file; 12h and 1d resampled from 1h in UTC; 1w resampled from 1d, weeks Monday 00:00 UTC; a resampled bar exists when at least one 1h bar is in its period and is usable at its period end.
8. S3: pivot 3 = high[p] > highs p-3..p-1 and >= highs p+1..p+3; confirmed after p+3. The later pivot p2 must be confirmed by the event bar and recent: p2 + 3 >= i - 6 (confirmed within the last 6 bars, the eh-s1 "within 6 bars" gate). Any earlier pivot p1 with 3 <= p2 - p1 <= 20 may pair.
9. S4 window "last 6 closed bars" = bars k-6..k-1 of signal bar k; k in {i-1, i}.
10. S5: "its prior close was higher" read as the daily RSI14 falling (RSI of the last closed day < RSI of the day before); long: rising.
11. Stop (short) = max(highest high of bars i-5..i, L); long = min(lowest low of i-5..i, L). Skip (count) if stop distance <= 0.
12. Exit: bars i+1..i+30; target 2.5R, stop wins a same-bar tie; time exit at the close of bar i+30. A trade whose 30 bars run past the split end is censored (counted, dropped).
13. Every event is traded; overlapping trades allowed (this is a dose-response measurement, not a portfolio).
14. Costs regime A: fees.BINANCE_TAKER x 2 + fees.SLIPPAGE_RT_S13 = 12 bps RT; fee_r = 0.0012 / stop fraction. Funding: USD-M fundingRate archive (BTC, ETH); records with entry < t <= exit; side_sign: a short receives positive funding; data.binance.vision has no fundingRate file before 2020-01 (404 for 2019-09..12), so funding = 0 before 2020-01.
15. OLS sandwich SE clustered by UTC day of the event bar, small-sample factor G/(G-1) x (n-1)/(n-2). 95 % CI = slope +- 1.96 SE. MDE (80 %) = 2.80 x SE.
16. VALIDATION: events with entry in 2024-07-01..2025-06-30 (levels and indicators warmed on earlier bars; nothing after 2025-06-30 is loaded). Holm at m = 15: the wave's other p-values are not available to this worker, so the slope passes only if one-sided p <= 0.05/15 (the strictest Holm step; conservative).
17. Verdict: PASS = DEV screen and VALIDATION pass with slope > 0; FAIL = DEV slope <= 0 with its CI upper bound below the slope MDE; INCONCLUSIVE otherwise (and by rule when score >= 3 has < 30 DEV events).

## Context
- Regime: none as a gate, because T13 pools every regime; the per-week research_kit regime tag (weekly+monthly RSI band and daily SMA200 side) is reported as the `Regime mix:` line over DEV weeks (BTC).
- Phase: none as a gate, because the trial pools phases; S5 (daily/weekly RSI turning at 60/40) is the only HTF context and it is one of the scored layers.
- Session: none, because 1h/4h level touches are taken around the clock.
- Entry: signal bar: the event bar close (taker), no retest.

Regime mix: computed in the count pass (RESULT.md).

## Data and splits
BTCUSDT, ETHUSDT Binance spot 1h and 4h from 2017-08 (cache F:/MTS/Dumps/backtest/spot_2017, outside the repo). DEV = start..2024-06-30; VALIDATION 2024-07-01..2025-06-30 read once only if DEV screens in; HOLDOUT never loaded. The loader refuses any month past the split end.
