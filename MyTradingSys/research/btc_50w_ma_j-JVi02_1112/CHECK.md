# CHECK: BTC weekly close below the 50-week MA, what followed (title claim of j-JVi02_C88; video text NOT_IN_DATA)

Command: `python MyTradingSys/research/btc_50w_ma_j-JVi02_1112/ma50w_breaks.py` (run 2026-11-11T21:00Z).
Data: Binance spot BTCUSDT 1w klines, 482 closed weeks 2017-08-14 .. week of 2026-11-02 (public, data-api.binance.vision). Simple 50W MA (OURS: SMA vs EMA not known without the transcript). Descriptive, fee-free, no trade rule.
Limit: the MA exists from 2018-07; the 2018 bear break happened before that, so the sample starts in 2019. Re-break = within 8 weeks of the previous break (OURS).

## Every break (close crosses from above to below)

| week | close | 50W MA | re-break | +4w | +12w | +26w | min in 26w | max in 26w |
|---|---|---|---|---|---|---|---|---|
| 2019-11-18 | 6903 | 7159 | no | +8.7% | +43.7% | +26.3% | -22.3% | +47.1% |
| 2019-12-09 | 7119 | 7380 | yes | +15.0% | +12.8% | +31.2% | -24.7% | +42.6% |
| 2019-12-23 | 7388 | 7529 | yes | +16.6% | -21.3% | +23.4% | -27.4% | +37.4% |
| 2020-03-02 | 8033 | 8557 | no | -15.7% | +17.6% | +27.7% | -33.3% | +48.3% |
| 2020-05-04 | 8723 | 8731 | no | +11.7% | +26.9% | +77.4% | -0.0% | +77.4% |
| 2020-05-18 | 8720 | 8772 | yes | +6.6% | +36.6% | +111.2% | +4.0% | +111.2% |
| 2021-07-12 | 31779 | 31852 | no | +47.8% | +72.0% | +35.5% | +11.3% | +106.2% |
| 2021-12-13 | 46681 | 47666 | no | -7.7% | -19.1% | -55.9% | -55.9% | +8.8% |
| 2021-12-27 | 47286 | 48147 | yes | -19.9% | -1.0% | -59.2% | -59.2% | -1.0% |
| 2022-04-04 | 42159 | 45561 | no | -19.3% | -54.2% | -53.9% | -55.4% | -5.9% |
| 2025-11-10 | 94261 | 102956 | no | -6.5% | -25.4% | -17.8% | -30.2% | -0.6% |
| 2026-11-02 | 74851 | 75535 | no | open | open | open | open | open |

First breaks with a full window (n=7): +4w up 3/7 (median -6.5%), +12w up 4/7 (median +17.6%), +26w up 4/7 (median +26.3%).

## Reading (OURS; n=7, no verdict possible)
- The break alone does not tell direction: 4 of 7 first breaks were followed by a rally, 3 by a deep fall.
- Split by cycle phase (BIBLE.md cycle table): breaks 1-2 years after a halving-cycle top (2021-12, 2022-04, 2025-11) were followed by -18% to -56% at 26 weeks; breaks in the year before/after a halving (2019-11, 2020-03, 2020-05, 2021-07) by +26% to +77%. The 50W MA break is a phase marker, not a signal; the phase decides the sign.
- Now (week of 2026-11-02): BTC closed 1% under the MA after a re-cross above it in between; this is the second first-break of this cycle, about 13 months after the 2025-10-06 peak. No earlier cycle had a break at this cycle time (in 2022-23 BTC stayed below the MA through the bottom), so there is no analogue row. BIBLE.md (line 33) puts the cycle bottom window at 2026-10-04 .. 11-16; the post-top breaks (-18% to -56% at 26w) argue caution. Written as a scenario, not a forecast.
- What we should do: nothing to trade from n=7. Log it as one cycle-clock reading in BIBLE.md (append, dated) and score it at 2026-12-01 (+4w) and 2027-01-26 (+12w) via the scenario ledger.
