# Krown Video Rules Extract - -9rAJNUpMsk

- URL: https://www.youtube.com/watch?v=-9rAJNUpMsk
- Title: How to Short Bitcoin Using Options | Interview with Krown's Crypto Cave
- Upload Date: 2019-07-17

## Trading Rules Stated (SOURCED)

### 1. Macro Trend Strict Non-Counter-Trend Rule (Direction / Filter)
- SOURCED: "The reason why I'd rather do with options is because anytime I'm trading against the overall macro trend, I don't want to put that position on spot. So I really don't want to be short spot in an overall upward market just like last year, I didn't want to be long spot while we were in a downwards market." (URL: https://www.youtube.com/watch?v=-9rAJNUpMsk at 02:58 - 03:11)
- SOURCED: "I've had very little success trading against the overall macro trend." (URL: https://www.youtube.com/watch?v=-9rAJNUpMsk at 04:24 - 04:28)
- Comparison with `krown_params.json`: MATCH. `krown_params.json` gates trades based on trend alignment (`ma_fast`, `ma_slow`, `ma_long`), forbidding counter-trend spot exposure.

### 2. Delta-Neutral Zone Construction (Architecture / Setup)
- SOURCED: "when I say that I'm an options trader first, I'm typically thinking in that sort of mode I want to be locking in all sorts of sides and making sure that I'm keeping relatively delta neutral. So I'm never really looking for like the big home run play... More often than not, things are rangy and caught in like a, you know, in a nice little zone, kind of like we are right now. And that's the beauty of options, because I can construct a zone of profit essentially, where as long as you stay within that zone, I can make money off that." (URL: https://www.youtube.com/watch?v=-9rAJNUpMsk at 01:44 - 02:20)
- Comparison with `krown_params.json`: CONFLICT / NOT APPLICABLE. `krown_params.json` is a directional technical layer, not a delta-neutral market-making option spread framework.

### 3. Hedging Counter-Trend via OTM Call Selling (Setup / Entry / Exit)
- SOURCED: "If I am going to have any sort of counter trend exposure, I'd rather do with options because one, it's easier to cover. I can specify that strike and then I can then cover in advance, it's all well out, well played in accordance to the levels that we were looking at running over there. So, say like the $10,000 shortage areas where I start to get bearish once again, if we actually break down, I can say, OK, well, then I'll sell some, if I want to have some downside exposure, we break that I'll sell some $10,500 calls or something like that. Or maybe I'll pick the next resistance like $11,000 or $11,500 is what I have right now of which we were just looking, so $11,200 is kind of where I see the short term in the medium term change. So that's why short of the $11,500 strike calls, because I know that if we get back above 11 too just cover those still make money, then still take profit and I can actually keep a spot underlying position as well long without ever going short." (URL: https://www.youtube.com/watch?v=-9rAJNUpMsk at 03:14 - 04:04)
- Comparison with `krown_params.json`: CONFLICT / NOT APPLICABLE. Parameters in `krown_params.json` manage directional swing breakouts and touches on spot/perp, having no option strike, DTE, or option-covering parameters.

### 4. News Reaction Filter (Bear Trap Rule) (Filter)
- SOURCED: "When I was I was in traditional markets, you know, anytime you have a news article like that, it's usually a counter trade type idea. People, retailers will kind of treat it as real. They'll sell in. And then what can happen and what I think is probably likely happening right now, as long as we don't take out that next level that we spoke about... they can drive it down, make you think that that's actually going to happen and then, you know, flip it around." (URL: https://www.youtube.com/watch?v=-9rAJNUpMsk at 05:03 - 05:49)
- Comparison with `krown_params.json`: MATCH. Microstructure and sentiment sweeps on news headlines are treated as potential traps unless technical level breaks are confirmed.

### 5. Specific Trading Parameters (Stop / Target / Sizing)
- Stop: Covered if price reclaims technical inflection level ($11,200), no percentage stop loss stated.
- Target: Option premium expiration / decay within the designated profit zone.
- Sizing: NO SIZING RULE STATED.

## Notes (OURS)

- Third-party Cointelegraph interview explaining Krown's options market-maker background from NYSE Arca.
- Cardinal rule: Never short spot against a macro bull trend.
- Counter-trend exposure is managed strictly via derivative options by selling out-of-the-money calls against resistance levels while keeping the underlying spot long.
- If the market rises above key resistance ($11,200 in his example), short calls are bought back/covered, retaining spot upside without suffering short liquidation.
