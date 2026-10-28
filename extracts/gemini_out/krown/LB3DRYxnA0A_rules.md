# Krown Video Rules Extract - LB3DRYxnA0A

- URL: https://www.youtube.com/watch?v=LB3DRYxnA0A
- Title: Stop Strategy-Hopping — Build a System You'll Actually Follow.
- Upload Date: 2022-02-05

## Trading Rules Stated (SOURCED)

### Mechanical Rules Status
- NO RULES STATED.
- SOURCED: "while I can't give you a direct strategy because I don't know who you are, I don't know what you actually trade, I don't know what time frames you want to trade, I don't know what your lifestyle looks like that actually even makes those styles of trading relevant. So, what I have to do here is I have to give you a cookie-cutter generalized rules that which you can then backwards engineer and of course apply to hopefully your life." (URL: https://www.youtube.com/watch?v=LB3DRYxnA0A at 00:10 - 00:29)

### System Construction Heuristics & Filters (Process / Architecture)
1. **Indicator Cap Rule (Filter / Sizing / Indicators)**
   - SOURCED: "employ uh at most three different indicators. In fact, the less the better. The less the better." (URL: https://www.youtube.com/watch?v=LB3DRYxnA0A at 02:12 - 02:16)
   - Comparison with `krown_params.json`: MATCH. The MTS Krown layer adheres to this indicator economy: trend moving averages (`ma_fast`, `ma_slow`, `ma_long`), volatility (`bbwp`), and momentum (`rsi`).

2. **Indicator Taxonomy & Roles (Architecture)**
   - SOURCED: "if I was going to trade the daily trend, I don't want to use moving averages cuz I like that for a trend. I like volatility as always cuz that always, you know, that always kind of coincides and kind of help me uh identify where we're at and and like when to be a little bit more aggressive and and things like that and when to kind of expect breakdowns and whatnot as well. And then maybe maybe something for momentum as well, just kind of like go alongside volatility for a bias and direction, but momentum is always like a much distant third in uh at least in my style, at least at least in my opinion." (URL: https://www.youtube.com/watch?v=LB3DRYxnA0A at 02:19 - 02:46)
   - Comparison with `krown_params.json`: MATCH. Trend moving averages determine regime; volatility (BBWP) dictates aggressive timing/breakouts; momentum (RSI) is auxiliary.

3. **Backtesting Requirement (Validation Gate)**
   - SOURCED: "Then, what you need to do is you need to go ahead and you need to do the very, very boring process, but very enlightening process of back-testing... because why would you ever put any real money to a strategy? Why would you ever allocate real money to a strategy that is untested, that is unproven?... to get about 100 iterations of a strategy tested takes about 2 hours, actually, if I really like nail it down and get it right." (URL: https://www.youtube.com/watch?v=LB3DRYxnA0A at 02:53 - 03:26)
   - Comparison with `krown_params.json`: MATCH. Pre-registration, objective backtesting, and trial ledgers are prerequisites before any strategy deployment.

4. **Specific Trading Parameters (Entry / Stop / Target / Sizing)**
   - Entry: NO ENTRY RULE STATED.
   - Stop: NO STOP RULE STATED.
   - Target: NO TARGET RULE STATED.
   - Sizing: NO SIZING RULE STATED.

## Notes (OURS)

- This video is a trading psychology and strategy design Q&A, not a mechanical signal breakdown.
- Krown explicitly refuses to prescribe fixed universal parameters, insisting that traders must backtest at least 100 sample trades on historical data before committing capital.
- His core technical triad is reaffirmed: Trend (MAs) primary, Volatility (compression/expansion) secondary for timing/aggression, Momentum (RSI) tertiary. Maximum 3 indicators on any chart.
