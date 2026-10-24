# Krown Video Rules Extract - _JoJbu_Ug-A

- URL: https://www.youtube.com/watch?v=_JoJbu_Ug-A
- Title: Beginner Traders Keep Adding Indicators And Losing Money | Here's The Real Setup
- Upload Date: 2021-11-13

## Trading Rules Stated (SOURCED)

### Mechanical Rules Status
- NO RULES STATED.
- SOURCED: "Which indicators would you recommend a newer person. A very difficult question to answer... Here here's a general rule. Certainly no more than three indicators. I really do not know too many like successful traders who use more than three indicators and the ones that that that I do know, they really only focus on like three or less actually" (URL: https://www.youtube.com/watch?v=_JoJbu_Ug-A at 00:08 - 00:26)

### System Construction Heuristics & Filters (Process / Indicator Selection)
1. **Indicator Cap Rule (Filter / Sizing / Indicators)**
   - SOURCED: "Certainly no more than three indicators... but probably even just one indicator at a time and then get a feel for what you want to do" (URL: https://www.youtube.com/watch?v=_JoJbu_Ug-A at 00:15, 01:50 - 01:53)
   - Comparison with `krown_params.json`: MATCH. Adheres to indicator parsimony.

2. **Sequential Framework Order (Hierarchy)**
   - SOURCED: "my sort of way of looking at things is trend first or structure if you want to call it that. It's kind of one in the same to myself. And then I look at of course volatility. That's that's number two and then momentum after that. And then anything on top of that is just kind of icing on the cake and actually in most cases I don't even want to be looking at it because it can just you know, add in more you know, confounding factors which probably don't really help at the end of the day" (URL: https://www.youtube.com/watch?v=_JoJbu_Ug-A at 02:42 - 03:13)
   - Comparison with `krown_params.json`: MATCH. Direct architectural alignment with MTS Krown layer design.

3. **Oscillator Redundancy Prohibition (Negative Filter)**
   - SOURCED: "I wouldn't just say, all right, everyone needs to learn everyone needs to put on an RSI, they need to put on a stoke, which doesn't really make sense to have like both of those in my" (URL: https://www.youtube.com/watch?v=_JoJbu_Ug-A at 04:37 - 04:45)
   - Comparison with `krown_params.json`: MATCH. Layer uses RSI (`rsi_period`, `rsi_bull`, `rsi_bear`) without redundant overlapping momentum oscillators.

4. **Timeframe & Style Tool Pairing (Timeframe / Indicator Pairing)**
   - SOURCED: "if you want to trade ranges, I like to use something a little bit more short form like like stokes because I tend to get uh know, the shorter term moves a little bit better. If I'm looking for you know, more trends style trading, so I'll probably employ like an RSI just because a lot of the time... it's going to speak towards more long-term moves for example." (URL: https://www.youtube.com/watch?v=_JoJbu_Ug-A at 03:45 - 04:04)
   - Comparison with `krown_params.json`: MATCH. `krown_params.json` is a daily/swing system pairing RSI with moving averages.

5. **Specific Trading Parameters (Entry / Stop / Target / Sizing)**
   - Entry: NO ENTRY RULE STATED.
   - Stop: NO STOP RULE STATED.
   - Target: NO TARGET RULE STATED.
   - Sizing: NO SIZING RULE STATED.

## Notes (OURS)

- This video addresses beginner indicator clutter, advising against piling on redundant indicators.
- Krown treats Trend and Structure as synonymous first principles, followed by Volatility, and lastly Momentum.
- He explicitly warns against running both RSI and Stochastic together, calling it redundant and confusing.
- No concrete numerical triggers, stop loss formulas, price targets, or sizing algorithms are provided.
