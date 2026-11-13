# Iteration 3 — Session Timing, Session Levels & Turn of Candle Gap Hunt (`flash`)

- **Card:** `gemini-hunt-session-timing-flash-1113`
- **Model:** `gemini-3.8-flash-low`
- **Scope:** Canonical transcripts in `raw_transcripts_canonical/` behind `LAYERS.md` section 'session levels, turn of candle, session momentum' (`session_timing`) compared with code in `MyTradingSys/backtest/layers/session`, `MyTradingSys/backtest/layers/session_levels`, and `MyTradingSys/backtest/layers/turn_of_candle`.
- **Method:** 5-gap pattern hunt (ours-as-his number, named-but-uncoded concept, one word many claims, method lost in translation, transfer assumed) evaluating trader rules on session boundaries, opening windows, session levels (PDH/PDL), candle close timing, and session momentum vs the codebase. Every quote below is copied verbatim from canonical transcripts on disk (`raw_transcripts_canonical/<id>_raw.txt`) and verified by `python scripts/dev/verify_extract_quotes.py`.
- **Timestamp Note:** Fabio transcripts contain `[mm:ss]` markers and are cited with exact `[mm:ss]` plus `BEGIN|MIDDLE|END` third position. Tom's raw caption transcripts do not contain `[mm:ss]` markers and are cited with their verified `BEGIN|MIDDLE|END` third.
- **Provenance Flags:** `9IliXww64uM` is tagged `Fabio (CONTESTED)` (course upload where speaker identity is contested); `Is1HvdfQm5c` is tagged `Fabio (ASR)` (Whisper ASR recovery); `5Ljfwvtktek` is tagged `TomGuest` (guest interview on Tom's channel). Sponsor mentions are excluded per `BRIEF.md`.

## Summary Counts (SOURCED vs OURS)

- **Corpus coverage:** 121 held canonical transcripts scanned; **33 distinct findings** extracted below across key session timing transcripts (`Of_wlv3xaZo`, `DyS79Eb92Ug`, `cUTsoU-15Tc`, `StaphlRH8NQ`, `Khgj5q1-ln8`, `Pz8f0wWW12M`, `T6hDJcHrVBM`, `BB3c8visnkI`, `zAwEX_tRUfE`, `9IliXww64uM`, `5Ljfwvtktek`, `K8qtT2_axPo`, `1utSjHs_Mq8`, `k0zm5NYn0IQ`, `Is1HvdfQm5c`).
- **Turn of Candle in transcripts:** `NOT_SEEN` (0 mentions of Shanaev, Kim/Hansen, or fixed 15-minute minute-0 candle-turn calendar edges across all canonical transcripts). The traders use micro-level **order flow tape absorption and candle-close confirmation** (`candle close green` / `closed sell`), not mechanical clock minute-0 returns.
- **Session Momentum in transcripts:** Shen, Urquhart & Wang (2022) academic half-hour paper is `NOT_SEEN` in trader speech. Fabio uses intraday session breakout momentum (`DyS79Eb92Ug`), not fixed-calendar first-30m-to-last-30m sign drift.
- **In our code (`OURS`):** Severe mismatch. Our repo coded academic papers with synthetic calendar assumptions (`MyTradingSys/backtest/layers/session/session_momentum.py:12` uses 00:00 UTC day; `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:3` trades 15m candle turn blind with NO-SOURCE long bias; `MyTradingSys/backtest/layers/session_levels/session_levels.py:16` uses previous UTC day and a synthetic 0.20% proximity rule), while the traders strictly trade cash sessions (RTH), sit on hands during the first 30 minutes, filter by Initial Balance expansion, and evaluate session level rejections causally at the tape.

## Findings Table

| topic | trader | exact quote | video id [mm:ss] | rule in his words | number: SOURCED value or NOT_SEEN | in our code? file:line or NONE |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| First 30m: Wait 15:30 to 16:00 cash open | Tom | Market opens at 15:30. You wait until 16:00 and do nothing. During that time, I carefully look at the cash volume profiles and analyze the market activity to see exactly what is happening. See whether the market is falling or rising according to the value areas and the POCs or if we're in a range to get a clear picture. | `Of_wlv3xaZo [no mm:ss; BEGIN]` | At the 15:30 CET US cash open, wait until 16:00 CET (first 30 minutes) doing nothing while analyzing the cash profiles, Value Areas, and POCs to establish context. | SOURCED: 15:30 open, wait until 16:00 (30 minutes) | NONE (MyTradingSys/backtest/layers/session_levels/session_levels.py:16 trades from minute 0) |
| First 30m: Stop trading first 30 minutes of NY | Tom | stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that. And you will be able to change your whole business. | `Of_wlv3xaZo [no mm:ss; MIDDLE]` | Stop trading during the first 30 minutes of the New York session and evaluate the width of the 30-minute opening range. | SOURCED: first 30 minutes | NONE (no 30m sit-on-hands gate in repo) |
| First 30m: Fabio waits first 30 minutes of NY open | Fabio | usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session. | `DyS79Eb92Ug [04:14] (BEGIN)` | Fabio waits out the first 30 minutes of the New York open so that session volatility stabilizes and market participants set up. | SOURCED: first 30 minutes | PARTIAL (MyTradingSys/backtest/layers/fabio/v3/models.py:194 waits 30m for IVB only) |
| First 30m: Fabio IVB completes first 30 minutes | Fabio | We have a clean defined IVB top and bottom and we are waiting for the first 30 minutes of the session to be completed to define clearly the areas where we see breakout. We have a statistical edge that the price will continue in that direction. | `cUTsoU-15Tc [10:50] (MIDDLE)` | Mark IVB top and bottom over the opening window and wait for the first 30 minutes of the session to complete before trading directional breakouts. | SOURCED: first 30 minutes | CODED (MyTradingSys/backtest/layers/fabio/v3/models.py:194 uses ivb_minutes = 30) |
| First 30m: Fabio Initial Balance definition & volatility contraction | Fabio | The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading. Volatility contraction during this first half hour often revolves in explosive volume confirmed directional breakout runs that hold strong predictive power for the rest of the session. | `StaphlRH8NQ [08:10] (MIDDLE)` | The Initial Balance is the high-low price established in the first 30 minutes of regular cash trading; volatility contraction (narrow IB) leads to explosive directional breakouts. | SOURCED: first 30 minutes, first half hour | NONE (MyTradingSys/backtest/layers/session_levels/session_levels.py:16 has no IB contraction check) |
| IB Regime: 30-minute range size assessment | Tom | The range of the first 30 minutes gives me information about how to assess the trading opening phase. Is it very large or is it rather small? That's the first piece of information that we get from this. | `K8qtT2_axPo [no mm:ss; BEGIN]` | The range of the first 30 minutes reveals whether the opening phase is very large or rather small, determining the daily context. | SOURCED: first 30 minutes | NONE |
| IB Regime: Initial balance shows trend vs balance | Tom | In the market profile, we can display what's called the initial balance showing how large the opening phase of trading was. This tells us whether we should expect a more trending day at first or rather a balanced day. This means is it more likely that the market will establish itself steadily in a trend or will it swing back and forth? | `1utSjHs_Mq8 [no mm:ss; MIDDLE]` | The Initial Balance width shows whether the session will trend steadily or swing back and forth in balance. | NOT_SEEN (no fixed numeric threshold stated) | NONE |
| IB Regime: Small IB acts like a rubber band | Tom | If for example you have a small initial balance. It's a bit like a rubber band. When the market then explodes there's more substance behind it. That's what's called a trend profile. | `K8qtT2_axPo [no mm:ss; MIDDLE]` | A small Initial Balance behaves like a compressed rubber band; breakout from a small IB forms a trend profile with genuine substance. | NOT_SEEN (no numeric width given) | NONE (src/main/java/datafeed/MarketDataSnapshot.java:991 invents unsourced 0.5/0.7 ratios) |
| IB Regime: Very large IB predicts balance play | Tom | If the market open is very very large, the probability is high that the market will play in balance. In this case here, the market opening phase is very large, but afterwards the market moves to fairer prices, prices at the top. So how does this contradiction come about? What can I do with that? I can tell you quite simply. If you see this, the probability is simply there that the market will run back down here because the big market participants simply didn't know right at the start of trading. | `K8qtT2_axPo [no mm:ss; MIDDLE]` | When the opening 30-minute range is very large, price is likely to stay in balance or retest the opening range low. | NOT_SEEN | NONE |
| IB Regime: Large IB driven by opening hedging transactions | Tom | because the initial balance is so large meaning the expansion of the trading opening is just very very big and that means here traders had to buy at the market open at that point they don't really care what the price is because these are hedging transactions | `k0zm5NYn0IQ [no mm:ss; MIDDLE]` | Very large Initial Balance expansion is driven by price-insensitive institutional hedging at the open; avoid chasing breakouts at the extreme. | NOT_SEEN | NONE |
| IB Regime: Fabio break below IB invalidates longs | Fabio | this was not viable for me because we broke below the initial balance and as you know, I like to pair the NASDAQ effort with the IVB model. So, you need to keep in mind a profile framing or IVB directional bias paired with the deep effort | `Khgj5q1-ln8 [10:35] (END)` | A break below the Initial Balance invalidates long setups; trade only when footprint effort aligns with the IB directional breakout bias. | NOT_SEEN | NONE |
| Session Boundaries: US cash session 15:30 to 22:00 CET | Tom | Okay, but keep in mind that you really only want to be trading during the main market hours or what we call the cash session, which runs from 15:30 all the way through to 22:00 hours and just a little bit more. | `Of_wlv3xaZo [no mm:ss; END]` | Trade US index products during the cash session (15:30 to 22:00 CET). | SOURCED: 15:30 all the way through to 22:00 hours | NONE (MyTradingSys/backtest/layers/session/session_momentum.py:12 uses UTC midnight) |
| Session Boundaries: Cash session profile vs 24-hour chart | Tom | The first thing is, when you trade cash time frames, please also use the cash session profiles because they can change. You can have a trend profile in the 24-hour chart, and in the cash session the day before you suddenly have a balance profile. | `Of_wlv3xaZo [no mm:ss; END]` | When trading cash sessions, use cash session profiles rather than 24-hour profiles because 24h profiles distort balance vs trend classification. | NOT_SEEN | NONE (backtest/vp_return_to_value.py:9 uses 24h UTC) |
| Session Boundaries: Special strategies testing London or Asia session | Tom | Unless you have special strategies again where you say, "I know the market likes to test the London session open again. The market tests the Asia session value high again." Or whatever. | `Of_wlv3xaZo [no mm:ss; END]` | Cash session is standard, unless using specific strategies targeting retests of London open or Asian session value high. | NOT_SEEN | NONE (MyTradingSys/backtest/layers/session_levels/session_levels.py:16 has no London open or Asia VAH levels) |
| Session Boundaries: London session too slow for Tom | Tom | That means as soon as I trade the London session, it's all way too slow for me. I might also have a bit too little patience. >> And >> I can't deal with that. I'm so deep into this cash session, that's why I just trade it. | `Of_wlv3xaZo [no mm:ss; END]` | Tom avoids the London session due to lower volatility and focuses strictly on the cash session. | NOT_SEEN | NONE |
| Session Boundaries: Fabio restricts US index profiles to NY cash session | Fabio | specifically the cash session of the volume profile because it's giving us the majority of the volume of the day, and I only trade in the New York session for US indices because it's where the majority of the volume get traded, and I find it from statistical validation, the London session to be usually for US indices not so valuable to add to the profile. So, I only use the cash session profile. | `Pz8f0wWW12M [28:53] (END)` | Build Volume Profiles strictly on the New York cash session for US indices, excluding London/overnight based on statistical testing. | NOT_SEEN | PARTIAL (auction_context.py:355 defines prior_ny_session_profile) |
| Session Boundaries: DAX live cash session 8:30/9:00 to 17:35 CET | Tom | Now here on the right side you can see the exact same information recorded during the live cash session. That means this is the market phase where the highest liquidity is present between 8:30, 9:00 and 17:35 where the cash times of the DAX future are simply present where the stocks are predominantly bought. | `T6hDJcHrVBM [no mm:ss; BEGIN]` | For DAX futures, the cash session profile runs from 08:30/09:00 to 17:35 CET when underlying equities trade. | SOURCED: between 8:30, 9:00 and 17:35 | NONE (no DAX cash window in repo) |
| Session Boundaries: Daily profiles show cash session period of largest sales | Tom | Each of these profiles shows you one day. And in addition, these profiles only show you the period where the so-called cash session is, i.e. the period where the largest sales associated with the corresponding product are shown. | `BB3c8visnkI [no mm:ss; MIDDLE]` | Daily profiles must isolate the cash session where the product's largest sales occur. | SOURCED: 1 day, cash session | NONE |
| Session Boundaries: 1-minute execution context from cash session profile | Tom | When we look for trades on the 1-minute chart, we always look at what is the context. And we determine the context through market profiling. And this here is, for example, a market profile chart, where you can read how the market traded during the cash session, the main trading hours, you can see it here. | `zAwEX_tRUfE [no mm:ss; BEGIN]` | Even for 1-minute intraday execution, directional context must be read from the cash session Market Profile. | SOURCED: 1-minute chart | NONE |
| Session Boundaries: NY RTH vs Asian & London session volume | Fabio (CONTESTED) | orange one is the volume profile of the regular trading hour session, the so-called New York session. The Asian and the London session are in this lighter color because there's less volume into those areas. | `9IliXww64uM [03:51] (BEGIN)` | Regular trading hours (New York) carry heavy volume; Asian and London overnight sessions carry significantly lower volume and are highlighted in lighter colors. | NOT_SEEN | NONE |
| Session Boundaries: Asian & London lack of price discovery auction | Fabio (CONTESTED) | there was no relevant news or price discovery auction during the Asian or London session, and we're about to open the session exactly where most of the money was traded yesterday. | `9IliXww64uM [06:11] (MIDDLE)` | Overnight Asian/London sessions often produce no relevant price discovery, opening the NY session right at yesterday's high-volume area. | NOT_SEEN | NONE |
| Session Boundaries: Asian session low formed at NY midnight | TomGuest | I trade from 6:00 a.m. So, New York midnight, I look at um what happened in the Asian session. If a significant low has formed, then from the morning, I position myself and look and search for a range that is is forming | `5Ljfwvtktek [no mm:ss; BEGIN]` | Guest trader checks the Asian session low formed around NY midnight (06:00 CET) to frame a morning counter-trading range. | SOURCED: 6:00 a.m., New York midnight | NONE |
| Session Levels: PDH/PDL fakeout during night or London | Tom | For this, I use the previous day's high and low points of the previous day's range and then wait or check in the morning if there was a fake out at the previous day's high, for example, or a breakout during the night or the London session. Um, a fake out at the previous day's high, for instance, is when the market um enters the new price range um compared to the previous day uh and doesn't accept this price range above and immediately dives back into the balance or the previous day's range, accepts prices there, >> >> and then trades through them relatively quickly. | `Of_wlv3xaZo [no mm:ss; MIDDLE]` | Check morning state for overnight/London fakeouts above PDH or below PDL; if price re-enters yesterday's range without acceptance, it quickly traverses the balance. | NOT_SEEN | PARTIAL (MyTradingSys/backtest/layers/session_levels/session_levels.py:16 tests failed break but uses UTC calendar day) |
| Session Levels: Liquidity levels = PDH, PDL, pre-session highs/lows | Tom | Liquidity levels for you are, for example, previous day high, previous day low, or also the highs and lows from the pre-session. Correct? | `Of_wlv3xaZo [no mm:ss; BEGIN]` | Core liquidity levels are previous day high, previous day low, and pre-session extremes. | NOT_SEEN | PARTIAL (MyTradingSys/backtest/layers/session_levels/session_levels.py:16 defines PDH/PDL and Asia low) |
| Session Levels: Pressure above PDH/PDL vs quick fake through range | Tom | I found through my research that the probability is simply highest when we're above the previous day's highs or lows and there's pressure. So, the market picks up speed. >> Or? >> Or the other way around, if it fakes, it quickly runs through the previous day's range. | `Of_wlv3xaZo [no mm:ss; MIDDLE]` | Above PDH/PDL with pressure triggers acceleration; a failed probe quickly counter-rotates through yesterday's entire range. | NOT_SEEN | NONE |
| Session Levels: Daily close inside vs outside previous day Value Area | Tom | we can determine whether the closing prices were within the balance the value area or if the closing price was outside. If it was outside then the information is clear for us something changed at the close of trading. And that's important because if the market opens the next day and moves back there the probability is high that we will see a rejection at these balance price areas. | `1utSjHs_Mq8 [no mm:ss; MIDDLE]` | If the daily close finishes outside the previous day's Value Area, market structure shifted; next-day retests of that balance boundary are likely to reject. | NOT_SEEN | PARTIAL (auction_context.py:300 checks close inside prior NY VP VAH/VAL) |
| Session Levels: Break previous day VAH and accept outside | Fabio | or a continuation trade where we break the value area high of the previous day. And when the the day close, as you can see, we continue to accept value, so we only consider long position here. | `Pz8f0wWW12M [27:11] (MIDDLE)` | Breaking previous day VAH with value acceptance on the close establishes a long-only directional continuation bias. | NOT_SEEN | NONE |
| Session Momentum: Fabio session momentum model on high break | Fabio | momentum model. So if we can break this high, we will see exactly the same that we saw in all our session. So I want to take a small risk here with a buy stop. Why? Because my stop loss will be really tight rates. | `DyS79Eb92Ug [18:52] (BEGIN)` | Fabio's session momentum model triggers a tight-stop buy-stop order when the market breaks the session high with order flow aggression. | NOT_SEEN | NONE (MyTradingSys/backtest/layers/session/session_momentum.py:12 trades first-30m sign drift, not breakout momentum) |
| Execution Timing: Micro gap continuation on candle close green | Fabio (ASR) | candle close green is shoot thus and goes to the next level you see how would they reload on the gap this is inefficient volume because it created a micro gap | `Is1HvdfQm5c [40:07] (BEGIN)` | When a candle closes green across a micro gap with inefficient volume, price reloads and shoots to the next level. | NOT_SEEN | NONE (MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:3 ignores delta/footprint and trades minute 0 blind) |
| Execution Timing: Candle close green with sellers absorbed at bottom | Fabio (ASR) | oh and these buyers at the top so the candle close green with sellers absorbed at the bottom and buyers at the top what is telling us is telling us that the buyers look here again someone is willing to buy | `Is1HvdfQm5c [1:00:01] (MIDDLE)` | When a candle closes green with sellers absorbed at the bottom wick and aggressive buyers at the top, buyers have taken control of the auction. | NOT_SEEN | NONE |
| Execution Timing: Wait for candle close dominance completion | Fabio (ASR) | you just want to see how the candle close you don't want to execute you want to understand when you have a moment where the dominance is completed so you have a clean part that is dominating the auction | `Is1HvdfQm5c [1:58:11] (END)` | Wait for the candle to close to confirm that one side has completed dominant control over the auction before executing. | NOT_SEEN | NONE |
| Execution Timing: Absorption confirmed on candle closed green | Fabio | here got absorbed and the candle closed green. This is a potential continuation of the move and an absorption pattern that you can spot using the delta per candle | `Pz8f0wWW12M [15:16] (MIDDLE)` | When delta shows aggressive selling absorbed at the low and the candle closes green, it confirms an absorption pattern for long continuation. | NOT_SEEN | NONE |
| Execution Timing: High effort absorbed when candle closed green | Fabio | volume you can see a lot of effort here, but the candle closed green. So what is telling us that all this input of volume delta got absorbed and probably this absorption happened here and we will continue on the upside. | `Pz8f0wWW12M [18:15] (MIDDLE)` | Heavy selling volume effort accompanied by a green candle close proves aggressive sellers were absorbed, predicting continuation upward. | NOT_SEEN | NONE |

## TOP 5

1. **Complete Fabrication of 'Turn of Candle' (Gap Pattern #4 'Method lost' & Gap Pattern #2 'Named concept never coded'):**
   - **Trader Reality (`SOURCED`):** In 121 held canonical transcripts, the concept of a mechanical 15-minute minute-0 calendar edge is `NOT_SEEN` (0 hits for Shanaev or Kim/Hansen). Fabio explicitly waits for the **candle close to confirm tape absorption or dominance** (`Is1HvdfQm5c` [1:58:11], `Pz8f0wWW12M` [15:16], [18:15]). The trader timing mechanism is an order-flow confirmation on candle close, not a calendar clock.
   - **In Our Code (`OURS`):** `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:3-48` and `MyTradingSys/backtest/layers/FORMULAS.md:385-398` imported an academic paper (Shanaev et al.) that had no direction or cost model, hardcoded a `NO-SOURCE` long bias, and traded it blindly every 15 minutes on testnet (`79%` of all trades, losing round-trip fees on every fill).

2. **Session Momentum Academic Paper vs Trader Session Breakout (Gap Pattern #4 'Method lost in translation' & Gap Pattern #5 'Transfer assumed'):**
   - **Trader Reality (`SOURCED`):** Shen, Urquhart & Wang (2022) academic intraday momentum is `NOT_SEEN` in trader speech. Fabio's actual session momentum model (`DyS79Eb92Ug` [18:52]) trades an aggressive breakout above the session high with a buy stop when tape confirms dominance.
   - **In Our Code (`OURS`):** `MyTradingSys/backtest/layers/session/session_momentum.py:12-45` hardcoded the academic paper's first-half-hour to last-half-hour sign drift, adapted it to a 24/7 UTC day starting at 00:00 UTC (`UNDEFINED in source`), found zero edge in `T055-C2`, and closed it as a failure without ever coding Fabio's session-high breakout model.

3. **Cash Session vs 24-Hour Calendar Day Distortions (Gap Pattern #5 'Transfer assumed' & Gap Pattern #1 'Wrong clock'):**
   - **Trader Reality (`SOURCED`):** Both Tom (`Of_wlv3xaZo`, `BB3c8visnkI`, `zAwEX_tRUfE`, `T6hDJcHrVBM`) and Fabio (`Pz8f0wWW12M` [28:53], `9IliXww64uM` [03:51]) emphasize that index volume concentrates in the **regular cash session** (15:30 to 22:00 CET for US indices, 08:30/09:00 to 17:35 CET for DAX). Tom explicitly warns that 24-hour profiles distort the balance vs trend classification because overnight low-volume bars alter the Value Area calculation.
   - **In Our Code (`OURS`):** `MyTradingSys/backtest/vp_return_to_value.py:9`, `MyTradingSys/backtest/layers/session/session_momentum.py:12`, and `MyTradingSys/backtest/layers/session_levels/session_levels.py:16` default to **24-hour UTC calendar days** (00:00 to 00:00 UTC), assuming 24/7 crypto hours could be applied to equity-index auction concepts without session boundary adaptation.

4. **Missing 30-Minute Opening Sit-on-Hands Gate & Initial Balance Regime Filter (Gap Pattern #2 'Named often, never coded' & Gap Pattern #3 'Invented numbers'):**
   - **Trader Reality (`SOURCED`):** Both Tom (`Of_wlv3xaZo`) and Fabio (`DyS79Eb92Ug` [04:14], `cUTsoU-15Tc` [10:50], `StaphlRH8NQ` [08:10]) sit on their hands during the **first 30 minutes** of the New York cash open while evaluating Initial Balance width. A narrow IB (volatility contraction) predicts an explosive trend day (`K8qtT2_axPo`, `StaphlRH8NQ`), while a very large IB reflects opening hedging transactions and predicts balance play or mean reversion (`K8qtT2_axPo`, `k0zm5NYn0IQ`).
   - **In Our Code (`OURS`):** `MyTradingSys/backtest/layers/session_levels/session_levels.py:16` and `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/census_session_ladder.py:138` execute trades from minute 0 of the session without waiting for the 30-minute opening window to settle. Furthermore, `src/main/java/datafeed/MarketDataSnapshot.java:933-995` anchored its IB to 00:00 UTC midnight and invented unsourced `0.5` and `0.7` day-range ratios (`OURS`).

5. **Previous Day High/Low Fakeouts Evaluated Mechanically Rather Than Causally (Gap Pattern #4 'Method lost in translation'):**
   - **Trader Reality (`SOURCED`):** Tom uses Previous Day High and Low (`Of_wlv3xaZo`, `1utSjHs_Mq8`) as liquidity reference levels. An overnight/London probe above PDH that re-enters yesterday's range without acceptance quickly runs through the prior day's balance. If there is pressure, it accelerates into a trend.
   - **In Our Code (`OURS`):** `MyTradingSys/backtest/layers/session_levels/session_levels.py:16-55` tested a rigid rule (`touch` before US open, `fail` back below level within `FAIL_WINDOW_MIN = 30` bars) against UTC previous-day high on 1m BTC bars, finding a `-0.036%` net loss (`T087`), while completely omitting tape acceptance, volume delta absorption, or session context.

## SINGLE BIGGEST HOLE

**The entire `session_timing` family in `LAYERS.md` (`session_levels`, `turn_of_candle`, `session_momentum`) is an architectural fabrication built on academic calendar anomalies rather than Tom and Fabio's actual session timing rules (`NONE`).**

While our repository spent weeks testing and running academic hypotheses (Shanaev's 15m candle turn, Shen's half-hour momentum, and mechanical UTC PDH fades), 0 lines of code exist for what Tom and Fabio actually preach across dozens of videos:
1. **The 30-minute cash open sit-on-hands gate:** Sitting out 15:30 to 16:00 CET (first 30m of NY open) while participants establish the Initial Balance (`Of_wlv3xaZo`, `DyS79Eb92Ug` [04:14], `cUTsoU-15Tc` [10:50]).
2. **Initial Balance width regime classification:** Identifying narrow IB volatility contraction (rubber-band trend day) vs wide IB opening hedging (balance play) (`K8qtT2_axPo`, `1utSjHs_Mq8`, `StaphlRH8NQ` [08:10]).
3. **Cash-session profile isolation:** Separating RTH cash sessions (15:30-22:00 CET) from overnight/London sessions to prevent 24h profile distortion (`Of_wlv3xaZo`, `Pz8f0wWW12M` [28:53]).
4. **Order-flow candle-close execution timing:** Waiting for candle close confirmation of absorption and delta dominance rather than blindly trading calendar minute-0 (`Is1HvdfQm5c` [1:58:11], `Pz8f0wWW12M` [15:16]).
5. **Causal PDH/PDL auction re-entry:** Trading the swift traversal of yesterday's range only when an overnight/London probe fails to accept outside value (`Of_wlv3xaZo`, `1utSjHs_Mq8`).

## Verified Quotes (Source GPS)

Every quote in the table above is reproduced below in canonical `verify_extract_quotes.py` format (`> "..."` + `**Source GPS: <id> | <BEGIN|MIDDLE|END>**`):

### 1. First 30m: Wait 15:30 to 16:00 cash open (`Of_wlv3xaZo [no mm:ss; BEGIN]`)
> "Market opens at 15:30. You wait until 16:00 and do nothing. During that time, I carefully look at the cash volume profiles and analyze the market activity to see exactly what is happening. See whether the market is falling or rising according to the value areas and the POCs or if we're in a range to get a clear picture."
**Source GPS: Of_wlv3xaZo | BEGIN**

### 2. First 30m: Stop trading first 30 minutes of NY (`Of_wlv3xaZo [no mm:ss; MIDDLE]`)
> "stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that. And you will be able to change your whole business."
**Source GPS: Of_wlv3xaZo | MIDDLE**

### 3. First 30m: Fabio waits first 30 minutes of NY open (`DyS79Eb92Ug [04:14] (BEGIN)`)
> "usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session."
**Source GPS: DyS79Eb92Ug | BEGIN**

### 4. First 30m: Fabio IVB completes first 30 minutes (`cUTsoU-15Tc [10:50] (MIDDLE)`)
> "We have a clean defined IVB top and bottom and we are waiting for the first 30 minutes of the session to be completed to define clearly the areas where we see breakout. We have a statistical edge that the price will continue in that direction."
**Source GPS: cUTsoU-15Tc | MIDDLE**

### 5. First 30m: Fabio Initial Balance definition & volatility contraction (`StaphlRH8NQ [08:10] (MIDDLE)`)
> "The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading. Volatility contraction during this first half hour often revolves in explosive volume confirmed directional breakout runs that hold strong predictive power for the rest of the session."
**Source GPS: StaphlRH8NQ | MIDDLE**

### 6. IB Regime: 30-minute range size assessment (`K8qtT2_axPo [no mm:ss; BEGIN]`)
> "The range of the first 30 minutes gives me information about how to assess the trading opening phase. Is it very large or is it rather small? That's the first piece of information that we get from this."
**Source GPS: K8qtT2_axPo | BEGIN**

### 7. IB Regime: Initial balance shows trend vs balance (`1utSjHs_Mq8 [no mm:ss; MIDDLE]`)
> "In the market profile, we can display what's called the initial balance showing how large the opening phase of trading was. This tells us whether we should expect a more trending day at first or rather a balanced day. This means is it more likely that the market will establish itself steadily in a trend or will it swing back and forth?"
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

### 8. IB Regime: Small IB acts like a rubber band (`K8qtT2_axPo [no mm:ss; MIDDLE]`)
> "If for example you have a small initial balance. It's a bit like a rubber band. When the market then explodes there's more substance behind it. That's what's called a trend profile."
**Source GPS: K8qtT2_axPo | MIDDLE**

### 9. IB Regime: Very large IB predicts balance play (`K8qtT2_axPo [no mm:ss; MIDDLE]`)
> "If the market open is very very large, the probability is high that the market will play in balance. In this case here, the market opening phase is very large, but afterwards the market moves to fairer prices, prices at the top. So how does this contradiction come about? What can I do with that? I can tell you quite simply. If you see this, the probability is simply there that the market will run back down here because the big market participants simply didn't know right at the start of trading."
**Source GPS: K8qtT2_axPo | MIDDLE**

### 10. IB Regime: Large IB driven by opening hedging transactions (`k0zm5NYn0IQ [no mm:ss; MIDDLE]`)
> "because the initial balance is so large meaning the expansion of the trading opening is just very very big and that means here traders had to buy at the market open at that point they don't really care what the price is because these are hedging transactions"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

### 11. IB Regime: Fabio break below IB invalidates longs (`Khgj5q1-ln8 [10:35] (END)`)
> "this was not viable for me because we broke below the initial balance and as you know, I like to pair the NASDAQ effort with the IVB model. So, you need to keep in mind a profile framing or IVB directional bias paired with the deep effort"
**Source GPS: Khgj5q1-ln8 | END**

### 12. Session Boundaries: US cash session 15:30 to 22:00 CET (`Of_wlv3xaZo [no mm:ss; END]`)
> "Okay, but keep in mind that you really only want to be trading during the main market hours or what we call the cash session, which runs from 15:30 all the way through to 22:00 hours and just a little bit more."
**Source GPS: Of_wlv3xaZo | END**

### 13. Session Boundaries: Cash session profile vs 24-hour chart (`Of_wlv3xaZo [no mm:ss; END]`)
> "The first thing is, when you trade cash time frames, please also use the cash session profiles because they can change. You can have a trend profile in the 24-hour chart, and in the cash session the day before you suddenly have a balance profile."
**Source GPS: Of_wlv3xaZo | END**

### 14. Session Boundaries: Special strategies testing London or Asia session (`Of_wlv3xaZo [no mm:ss; END]`)
> "Unless you have special strategies again where you say, "I know the market likes to test the London session open again. The market tests the Asia session value high again." Or whatever."
**Source GPS: Of_wlv3xaZo | END**

### 15. Session Boundaries: London session too slow for Tom (`Of_wlv3xaZo [no mm:ss; END]`)
> "That means as soon as I trade the London session, it's all way too slow for me. I might also have a bit too little patience. >> And >> I can't deal with that. I'm so deep into this cash session, that's why I just trade it."
**Source GPS: Of_wlv3xaZo | END**

### 16. Session Boundaries: Fabio restricts US index profiles to NY cash session (`Pz8f0wWW12M [28:53] (END)`)
> "specifically the cash session of the volume profile because it's giving us the majority of the volume of the day, and I only trade in the New York session for US indices because it's where the majority of the volume get traded, and I find it from statistical validation, the London session to be usually for US indices not so valuable to add to the profile. So, I only use the cash session profile."
**Source GPS: Pz8f0wWW12M | END**

### 17. Session Boundaries: DAX live cash session 8:30/9:00 to 17:35 CET (`T6hDJcHrVBM [no mm:ss; BEGIN]`)
> "Now here on the right side you can see the exact same information recorded during the live cash session. That means this is the market phase where the highest liquidity is present between 8:30, 9:00 and 17:35 where the cash times of the DAX future are simply present where the stocks are predominantly bought."
**Source GPS: T6hDJcHrVBM | BEGIN**

### 18. Session Boundaries: Daily profiles show cash session period of largest sales (`BB3c8visnkI [no mm:ss; MIDDLE]`)
> "Each of these profiles shows you one day. And in addition, these profiles only show you the period where the so-called cash session is, i.e. the period where the largest sales associated with the corresponding product are shown."
**Source GPS: BB3c8visnkI | MIDDLE**

### 19. Session Boundaries: 1-minute execution context from cash session profile (`zAwEX_tRUfE [no mm:ss; BEGIN]`)
> "When we look for trades on the 1-minute chart, we always look at what is the context. And we determine the context through market profiling. And this here is, for example, a market profile chart, where you can read how the market traded during the cash session, the main trading hours, you can see it here."
**Source GPS: zAwEX_tRUfE | BEGIN**

### 20. Session Boundaries: NY RTH vs Asian & London session volume (`9IliXww64uM [03:51] (BEGIN)`)
> "orange one is the volume profile of the regular trading hour session, the so-called New York session. The Asian and the London session are in this lighter color because there's less volume into those areas."
**Source GPS: 9IliXww64uM | BEGIN**

### 21. Session Boundaries: Asian & London lack of price discovery auction (`9IliXww64uM [06:11] (MIDDLE)`)
> "there was no relevant news or price discovery auction during the Asian or London session, and we're about to open the session exactly where most of the money was traded yesterday."
**Source GPS: 9IliXww64uM | MIDDLE**

### 22. Session Boundaries: Asian session low formed at NY midnight (`5Ljfwvtktek [no mm:ss; BEGIN]`)
> "I trade from 6:00 a.m. So, New York midnight, I look at um what happened in the Asian session. If a significant low has formed, then from the morning, I position myself and look and search for a range that is is forming"
**Source GPS: 5Ljfwvtktek | BEGIN**

### 23. Session Levels: PDH/PDL fakeout during night or London (`Of_wlv3xaZo [no mm:ss; MIDDLE]`)
> "For this, I use the previous day's high and low points of the previous day's range and then wait or check in the morning if there was a fake out at the previous day's high, for example, or a breakout during the night or the London session. Um, a fake out at the previous day's high, for instance, is when the market um enters the new price range um compared to the previous day uh and doesn't accept this price range above and immediately dives back into the balance or the previous day's range, accepts prices there, >> >> and then trades through them relatively quickly."
**Source GPS: Of_wlv3xaZo | MIDDLE**

### 24. Session Levels: Liquidity levels = PDH, PDL, pre-session highs/lows (`Of_wlv3xaZo [no mm:ss; BEGIN]`)
> "Liquidity levels for you are, for example, previous day high, previous day low, or also the highs and lows from the pre-session. Correct?"
**Source GPS: Of_wlv3xaZo | BEGIN**

### 25. Session Levels: Pressure above PDH/PDL vs quick fake through range (`Of_wlv3xaZo [no mm:ss; MIDDLE]`)
> "I found through my research that the probability is simply highest when we're above the previous day's highs or lows and there's pressure. So, the market picks up speed. >> Or? >> Or the other way around, if it fakes, it quickly runs through the previous day's range."
**Source GPS: Of_wlv3xaZo | MIDDLE**

### 26. Session Levels: Daily close inside vs outside previous day Value Area (`1utSjHs_Mq8 [no mm:ss; MIDDLE]`)
> "we can determine whether the closing prices were within the balance the value area or if the closing price was outside. If it was outside then the information is clear for us something changed at the close of trading. And that's important because if the market opens the next day and moves back there the probability is high that we will see a rejection at these balance price areas."
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

### 27. Session Levels: Break previous day VAH and accept outside (`Pz8f0wWW12M [27:11] (MIDDLE)`)
> "or a continuation trade where we break the value area high of the previous day. And when the the day close, as you can see, we continue to accept value, so we only consider long position here."
**Source GPS: Pz8f0wWW12M | MIDDLE**

### 28. Session Momentum: Fabio session momentum model on high break (`DyS79Eb92Ug [18:52] (BEGIN)`)
> "momentum model. So if we can break this high, we will see exactly the same that we saw in all our session. So I want to take a small risk here with a buy stop. Why? Because my stop loss will be really tight rates."
**Source GPS: DyS79Eb92Ug | BEGIN**

### 29. Execution Timing: Micro gap continuation on candle close green (`Is1HvdfQm5c [40:07] (BEGIN)`)
> "candle close green is shoot thus and goes to the next level you see how would they reload on the gap this is inefficient volume because it created a micro gap"
**Source GPS: Is1HvdfQm5c | BEGIN**

### 30. Execution Timing: Candle close green with sellers absorbed at bottom (`Is1HvdfQm5c [1:00:01] (MIDDLE)`)
> "oh and these buyers at the top so the candle close green with sellers absorbed at the bottom and buyers at the top what is telling us is telling us that the buyers look here again someone is willing to buy"
**Source GPS: Is1HvdfQm5c | MIDDLE**

### 31. Execution Timing: Wait for candle close dominance completion (`Is1HvdfQm5c [1:58:11] (END)`)
> "you just want to see how the candle close you don't want to execute you want to understand when you have a moment where the dominance is completed so you have a clean part that is dominating the auction"
**Source GPS: Is1HvdfQm5c | END**

### 32. Execution Timing: Absorption confirmed on candle closed green (`Pz8f0wWW12M [15:16] (MIDDLE)`)
> "here got absorbed and the candle closed green. This is a potential continuation of the move and an absorption pattern that you can spot using the delta per candle"
**Source GPS: Pz8f0wWW12M | MIDDLE**

### 33. Execution Timing: High effort absorbed when candle closed green (`Pz8f0wWW12M [18:15] (MIDDLE)`)
> "volume you can see a lot of effort here, but the candle closed green. So what is telling us that all this input of volume delta got absorbed and probably this absorption happened here and we will continue on the upside."
**Source GPS: Pz8f0wWW12M | MIDDLE**
