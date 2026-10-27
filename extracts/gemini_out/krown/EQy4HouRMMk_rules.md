# Krown Video Rules Extract - EQy4HouRMMk

- URL: https://www.youtube.com/watch?v=EQy4HouRMMk
- Title: What is the Next Bitcoin Buy Zone? | Eric Krown and Charlie Burton
- Upload Date: 2020-01-22

## Trading Rules Stated (SOURCED)

### 1. Daily 200 SMA Pullback Rule (Setup / Level)
- SOURCED: "The 200 simple on the daily. Always gonna be a classic pullback area, you know, on your first pass and also hitting a very long term trend line as well... lower nine thousand dollar region. So Bitcoin likely to pull back off a region like that and now consolidate at a higher level" (URL: https://www.youtube.com/watch?v=EQy4HouRMMk at 00:54 - 01:16)
- Comparison with `krown_params.json`: MATCH. `ma_long`: 200 (SMA 200) is explicitly parameterised in `krown_params.json` as a major regime and support/resistance boundary (`KR-M01` / `KR-M07`).

### 2. Major Level Grinding & Retest Consolidation (Level / Filter)
- SOURCED: "the 50 simple moving average on the weekly coming in right around about fifty five hundred. And Bitcoin, you know, tested it a few times, pulled back. Everyone got really, really scared, saying, we're gonna go back down because that's what rejected in 2014, 2015. Little, you know, little do people remember that any time you you know, you grind out a major area like this typically is bullish. So I do think that as long as Bitcoin kind of stays in this region right here between and just kind of hovering and putting another potentially higher low as it stands right now in the mid 8 thousands more or less OK, and probably get another test back up to that 200 simple moving average" (URL: https://www.youtube.com/watch?v=EQy4HouRMMk at 01:32 - 02:06)
- Comparison with `krown_params.json`: MATCH. `zone_mature_tests`: 3 (KR-Z13: "beyond three tests the break probability is higher") reflects consolidation and grinding around major moving averages.

### 3. Portfolio Allocation & Sizing Rule (Sizing / Risk)
- SOURCED: "10 to 20 percent is even if you even would seem a little bit high on the on the higher end to myself. Yeah, agreed. I would say 5 percent, but rather than ten to twenty... You put 5 percent of your entire portfolio maybe into gold. You don't ever go too heavy. So for me, 5 to 10 percent, Max." (URL: https://www.youtube.com/watch?v=EQy4HouRMMk at 13:47 - 14:36)
- Comparison with `krown_params.json`: SOURCED (quote+URL), NEW (NOT IN PARAMS). `krown_params.json` does not contain a portfolio capital allocation fraction; Krown explicitly caps Bitcoin exposure at 5% to 10% maximum.

### 4. Options Market Maker Edge Principle (Filter / Options)
- SOURCED: "we had a great saying on the floor of ARCA and it was options were created to be sold. And the thing is that most retailers look at options exactly as Charlie just said, it's like, oh, extra leverage for a lower price. You know, they treat it as a lottery ticket. And, you know, I think there's also a great statistic that like 80% of options expire worthless. I think that kind of answers a question for most retailers. Most retailers are only buying options to begin with. They're not selling them. They're not using it to cover" (URL: https://www.youtube.com/watch?v=EQy4HouRMMk at 20:13 - 20:42)
- Comparison with `krown_params.json`: NOT APPLICABLE. `krown_params.json` is a spot/perp momentum-level layer and does not model options Greeks or option sales.

### 5. Specific Execution Parameters (Entry / Stop / Target)
- Entry: Rebounds and consolidations off the 200 daily SMA or weekly 50 SMA; no exact candle entry trigger formula stated.
- Stop: NO STOP DISTANCE STATED (structural invalidation around prior consolidation support, e.g. $8,300, without a percentage stop).
- Target: NO MECHANICAL TARGET STATED (mentions prior swing highs like $12,000 as discretionary roadmap).

## Notes (OURS)

- Interview on Cointelegraph panel alongside Charlie Burton.
- Krown explains that prolonged grinding against a major level (like weekly 50 SMA) consolidates support and forms higher lows rather than guaranteed immediate rejections.
- Crucial sizing limit: Krown states that for crypto, total portfolio allocation should be 5% to 10% maximum, pushing back against aggressive 20%+ allocations.
- From his ARCA floor experience, Krown highlights that retail traders lose because they buy options as lottery tickets, whereas professional market makers sell options to collect premium and capture decay.
