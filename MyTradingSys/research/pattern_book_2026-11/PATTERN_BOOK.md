# MTS pattern book (2026-11-07)

Purpose: the classical chart patterns, candlesticks and trendlines the professional way, so MTS reads BTC with the same words the books use. Method: d-phase-first-method-1106 (a pattern valid in today's market phase goes to testnet and runs until it fails; published base rates are the starting belief, not a proof). Nothing here is a backtest and nothing here is an edge.

Every number carries a tag:
- **SOURCED-P** = the author's own page or paper (quote and URL in `sources_raw.md`, same folder).
- **SOURCED-S** = someone quoting the author (StockCharts, a second paper). Flagged where used.
- **DERIVED** = my arithmetic on SOURCED-P rows. **OURS** = a choice or a measurement of ours on BTC.
- **NOT FOUND** = I looked and could not source it; nothing is filled from memory.

## 0. Read this first: what the published rates are and are not

| Fact | Source |
|---|---|
| Bulkowski's tables are **US stocks, daily bars, "Important Bull Market Results"** (outside the two S&P bear markets). No crypto, no bear-market columns on his free pages. | SOURCED-P glossary, thepatternsite.com/glossary.html |
| "Break even failure rate" = the move after the breakout was **under 5 %**. It does not mean the pattern lost money. | SOURCED-P glossary |
| "Average rise/decline" runs from the breakout to the **ultimate high/low** (last extreme before a 20 % reversal). It is a best-case trend-end figure, not a fixed-horizon return. | SOURCED-P glossary |
| Flags and pennants are measured on the **short swing**, so their small averages are not comparable with the other rows. | SOURCED-P flags.html, pennants.html |
| "Reversal rate" for a candle = how often price closes beyond the candle's high or low in the expected direction. It is not performance (bearish engulfing: 79 % reversal, overall rank 91 of 103). | SOURCED-P BearEngulfing.html |
| Edwards & Magee, Murphy and Nison: **book text not accessible**; their rules appear here only second-hand (Lo-Mamaysky-Wang quote E&M for the one-month double-top spacing; StockCharts follows Murphy). | NOT FOUND first-hand |
| BTC on candles, own test (2020-2024 DEV, 14 bps costs): **no pattern survives costs**, 0 of 54 pattern x horizon rows. | OURS `candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md` |

## 1. Chart patterns: rules, targets, invalidation, published rates

Rates = Bulkowski, bull market, US stocks, daily. Cells "up / down" are for an upward / downward breakout. "Fail" = under-5 % move. "Meets" = % reaching his target (his target = pattern height x this rate, added to the breakout price). E&M / StockCharts project the **full height** (x 1.0).

| Pattern | Bias | Fail | Avg move | Throwback / pullback | Meets target | n | Source |
|---|---|---|---|---|---|---|---|
| Double top (4 Adam/Eve variants) | bear | 20-25 % (DERIVED wtd 22.0 %) | -15.5 % (DERIVED) | 64.3 % pullback (DERIVED) | 54.4 % (DERIVED) | 3,369 | P: aadt/aedt/eadt/eedt.html |
| Double bottom (4 variants) | bull | 12-16 % (DERIVED 13.2 %) | +43.3 % (DERIVED) | 66.5 % throwback (DERIVED) | 69.8 % (DERIVED) | 3,885 | P: aadb/aedb/eadb/eedb.html |
| Head and shoulders top | bear | 19 % | -16 % | 68 % pullback | 51 % | >2,800 | P: hst.html |
| Head and shoulders bottom | bull | 11 % | +45 % | 65 % throwback | 71 % | 3,197 | P: hsb.html |
| Flag (up / down) | cont. | 44 / 45 % | +9 / -8 % (short swing) | NOT FOUND | 46 / 46 % | hundreds | P: flags.html |
| Pennant (up / down) | cont. | 54 / 54 % | +7 / -6 % (short swing) | NOT FOUND | 35 / 32 % | >1,600 | P: pennants.html |
| Rising wedge (up / down) | bear | 19 / 51 % | +38 / -9 % | 72 / 72 % | 63 / 32 % | >1,400 | P: risewedge.html |
| Falling wedge (up / down) | bull | 26 / 29 % | +38 / -14 % | 62 / 74 % | 62 / 29 % | >800 | P: fallwedge.html |
| Ascending triangle (up / down) | bull | 17 / 38 % | +43 / -13 % | 64 / 63 % | 70 / 44 % | >1,400 | P: at.html |
| Descending triangle (up / down) | bear | 22 / 23 % | +38 / -15 % | 60 / 58 % | 64 / 50 % | >1,300 | P: dt.html |
| Symmetrical triangle (up / down) | neutral | 25 / 37 % | +34 / -12 % | 62 / 65 % | 58 / 36 % | >3,000 | P: st.html |
| Rectangle bottom (up / down) | neutral | 15 / 24 % | +48 / -16 % | 64 / 66 % | 79 / 55 % | >900 | P: rectbots.html |
| Rectangle top (up / down) | neutral | 15 / 34 % | +51 / -13 % | 66 / 64 % | 78 / 54 % | >1,000 | P: recttops.html |

Reading across: the **reversal patterns that break with the prior trend's grain are weakest** (rising wedge down-breakout 51 % fail, 32 % meets; falling wedge down 29 %), and the double top is the weakest of the reversal tops (22 % fail, 54 % meets). Double bottom and H&S bottom (13 % / 11 % fail, ~70 % meets) are the strongest in the table: consistent with the bull-market sample they come from. Do not read that as "bottoms work better on BTC": that is not tested here.

### 1.1 Definitions, drawing, trigger, invalidation (per pattern)

| Pattern | Professional definition (source) | How it is drawn | Trigger (confirmation) | Target | Invalidation |
|---|---|---|---|---|---|
| Double top | Upward trend into two similar tops; peaks differ "usually less than 3 %"; valley "at least 10 %, but allow exceptions"; weeks apart (P, aadt.html). E&M via Lo et al.: tops at least a month / 22 trading days apart (S). | Horizontal line at the valley low between the peaks. | Close below the valley (P). Unconfirmed twin peaks fail 60 % of the time; confirmed ones 25 % (A&A) (P). | Valley minus full height (E&M/StockCharts, S); Bulkowski: height x 43-64 % hit rate (P). | Stop "a few pennies above the highest peak" (P). Bust = drops at most 10 %, then closes above the top (P BustDoubleTops.html). 36-44 % of confirmed double tops later bust (P BustPerformance.html). |
| Double bottom | Downtrend into two similar lows; rise between at least 10 %; low spread averages 1 % (P, aadb.html). | Horizontal at the peak between the lows. | Close above that peak (P). Unconfirmed: 48 % continue lower (P). | Peak plus full height (S); Bulkowski x 65-73 % (P). | Stop slightly below the lower low (P). Bust = rises at most 10 %, then closes below the bottom (P). |
| H&S top | Three peaks, middle highest, shoulders near the same price and distance from the head (P, hst.html). Formal (Lo et al.): five extrema, E1 and E5 within 1.5 % of their average, E2 and E4 within 1.5 % (P paper). | Neckline through the two armpit lows (may slope). | Close below an up-sloping neckline, or below the right armpit if it slopes down (P). | Head to neckline height, subtracted from the breakout; Bulkowski x 51 % (P). | No stop rule on the page (NOT FOUND). Bust = drop at most 10 % then close above the top of the pattern (P). Busted H&S tops then gain 35 % on average (P BustHST.html). |
| H&S bottom | Mirror (P, hsb.html). | Neckline through the two peaks. | Close above it (P). | Head-to-neckline height up; x 71 %. | NOT FOUND; bust = rises at most 10 %, closes below the bottom (P). |
| Bull / bear flag | Steep pole ("unusually steep, several days"), then a small parallel channel tilted against the move, under 3 weeks (P flags.html). StockCharts: 1-12 weeks (S). | Two parallel lines around the pause; pole = the run before it. | Break of the flag line in the pole's direction (close basis, S). | Pole height from the flag edge (P half-staff; hit rate 46 %). | NOT FOUND from Bulkowski. Practice (OURS): flag extreme, or more than 50 % retrace of the pole. |
| Pennant | Pole, then a short symmetrical triangle, 3 weeks or less (P pennants.html). | Two converging lines after the pole. | Close outside a line. | Pole height; hit rate 32-35 % (the worst in the table). | NOT FOUND; OURS: opposite side of the pennant. |
| Rising wedge | Two up-sloping converging lines; at least 5 touches (3 + 2); at least 3 weeks (P risewedge.html). | Lines through minor highs and lows. | Close outside a line; breaks down 60 % of the time (P). | Bulkowski: lowest valley in the wedge, or height x 32 % (down). | NOT FOUND; bust = close beyond the other side after at most 10 % (P). Down-breakouts bust 63 % of the time (P BustPerformance.html). |
| Falling wedge | Mirror: two down-sloping converging lines, 5 touches (P fallwedge.html). | As above. | Close outside; breaks up 68 % of the time (P). | Highest peak in the wedge, or height x 62 % (up). | NOT FOUND. |
| Ascending triangle | Flat top, rising bottom; at least 3 touches one line, 2 the other; price must fill the triangle (P at.html). | Horizontal at the highs, line under the rising lows. | Close above the flat top (breaks up 63 %); break comes about 64 % of the way to the apex (P). | Height (flat line to lowest valley) x 70 %. | Bulkowski stop: opposite side; for an up-break a minor low, for a down-break the flat line (P). |
| Descending triangle | Flat bottom, falling top; 3 + 2 touches (P dt.html). | Mirror. | Close below the flat bottom; up-breaks 53 %. | Height x 50 % (down). | StockCharts: a reaction high at or above the previous one invalidates it (S). |
| Symmetrical triangle | Falling top, rising bottom; 3 + 2 touches (P st.html). | Converging lines. | Close outside; up 60 %; ideal break 1/2 to 3/4 of the way (S). E&M: about 75 % continue the trend (S, second-hand). | Height x 58 % (up) / 36 % (down). | NOT FOUND; 48 % of down-breakouts bust (P). |
| Rectangle / range | Flat tops and flat bottoms, 5-touch minimum (P rectbots.html, recttops.html). | Two horizontals. | Close outside, wait for it: "the breakout can be in any direction" (P). | Height x 54-79 %. Intrapattern trade allowed if tall enough (P). | Channels: close outside adversely = exit (P channels.html). |
| Channel | Two parallel lines, at least 2 touches each; no performance statistics (P). | Line through two peaks, parallel through a valley (the three-point channel works only while the trend lasts, P). | Close outside the channel. | none | Close outside adverse side (P). |

Hit-rate target rule (Bulkowski) and full-height rule (E&M/StockCharts) disagree: the detector reports the **full-height** target and the book states Bulkowski's hit rate beside it. The honest expectation is the hit rate, not the target.

### 1.2 Breakout, fakeout, throwback

| Fact | Source |
|---|---|
| A breakout is a **close** beyond the line or level, not a wick. | SOURCED-P glossary; StockCharts "closing basis, some apply 3 % or 3 days" SOURCED-S |
| Throwback / pullback = price returns to the breakout price within 30 days. **58 %** of 10,305 up-breakouts threw back; **58 %** of 8,765 down-breakouts pulled back (since 2000). Returns take about 10-11 days; the average excursion is 8-9 %. | SOURCED-P throwbacks.html, pullbacks.html |
| After a throwback reaches the breakout price, 65 % recover; after a pullback 47 % resume the decline. | SOURCED-P same pages |
| Busted pattern = breaks one way, moves at most 10 %, then closes beyond the opposite side. Median bust frequency: **24 %** of up-breakouts, **40 %** of down-breakouts. The move after a bust is often larger than from a working pattern (e.g. failed triple tops +42 % vs triple bottoms +37 %). | SOURCED-P Busted.html, BustPerformance.html |
| Volume: a high-volume breakout throws back 70 % of the time. | SOURCED-P throwbacks.html |

**Detector fakeout rule (OURS):** a close beyond the line that is back inside within 3 bars after an excursion under 1 ATR% is a *fakeout*; a bigger excursion that comes back is a *pullback*. The 2021 double top shows why: the neckline (28,805) was poked and reclaimed in May 2022 before the real break, so a pattern is not called failed on the first poke.

## 2. Candlesticks

Bulkowski's candle study: almost 5 million candle lines, 103 types, US stocks, daily (SOURCED-P EveningStar.html). The tested "reversal rate" is only how often price closes beyond the candle in the expected direction; he calls 50-60 % "near random" (hammer, shooting star pages). Below: published numbers next to **BTC 1d next-candle rates measured by detect_patterns.py on 2017-08..2026-11 Binance daily bars** (OURS: share of events, with the prior-trend condition below, whose next close is in the expected direction; baseline 51.1 % of all days close above the previous close; n small, so each rate has roughly +-10 points of noise at n=100 and +-20 at n=25; no costs, no multiple-testing control).

| Candle | Rule used by the detector (Bulkowski/Nison shape; trend context OURS) | Bulkowski reversal rate (rank of 103) | Bulkowski overall rank | BTC 1d next-candle (OURS) |
|---|---|---|---|---|
| Hammer | lower shadow >= 2 x body, upper <= 15 % of range, body <= 40 % of range, after a down-trend | 60 % (26) | 65 | 55 % (n 47) |
| Hanging man | same shape after an up-trend | "bullish continuation 59 %" (P) | 87 | 52 % (n 52) |
| Shooting star | upper shadow >= 2 x body, lower <= 15 %, after an up-trend | 59 % | 55 | 59 % (n 27) |
| Bullish engulfing | green body covers the prior red body, larger, after a down-trend | 63 % (22) | 84 | 50 % (n 101) |
| Bearish engulfing | red body covers prior green body, after an up-trend | 79 % (5) | 91 | 41 % (n 86) |
| Morning star | long red, small body (<= 30 % of the first), green closing above the first body's midpoint, after a down-trend (no gap rule: crypto trades 24/7) | 78 % (6) | 12 | 47 % (n 19) |
| Evening star | mirror | 72 % (10) | 4 | 57 % (n 23) |
| Dark cloud cover | green then red opening at or above the prior close, closing below the midpoint | 60 % | 22 | 29 % (n 28) |
| Piercing line | red then green closing above the midpoint, below the prior open | 64 % (21) | 13 | 42 % (n 26) |
| Three white soldiers | three green bodies, each opening inside the last body, closing near the high | 82 % (3) | 32 | 0 events with the filter |
| Three black crows | mirror | 78 % | 3 | 0 events with the filter |
| Doji | body <= 10 % of range (indecision, no direction) | long-legged "bullish continuation 51 %" | 37 | n/a (no direction) |

Source URLs (all SOURCED-P): thepatternsite.com/Hammer.html, HangingMan, ShootingStar, BullEngulfing, BearEngulfing, MorningStar, EveningStar, DarkCloudCover, Piercing, ThreeWhiteSoldiers, ThreeBlackCrows, LongLegDoji. Nison's book: NOT FOUND first-hand; Bulkowski's identification guidelines are used for the shapes.

What this says for BTC: **the next daily candle after these shapes is a coin flip** (baselines 50-51 %; the extremes, dark cloud 29 % and bearish engulfing 41 %, are at n 28 and 86; the opposite of the textbook call but small samples). The earlier pre-registered test agrees: 18 patterns x 3 horizons on 1d and 1h, net of 14 bps costs, none passed (OURS CANDLE_PATTERNS_RESEARCH s5). Academic context: Marshall-Young-Rose (2006) and Marshall-Young-Cahan (2008) find no after-cost value in US and Japanese equities; Lu-Shiu-Liu (2012) and Tharavanij et al. (2017) find some in specific markets (SOURCED-P by title and DOI in `candle_patterns_2026-10-04/citations_verified.txt`). Candles are therefore **context, not triggers**, in this book: they mark where a level held or failed, they do not call the next bar.

Bulkowski's tips worth keeping (SOURCED-P, same pages): candles within a third of the yearly low act as reversals most often; use tall candles for engulfing, piercing and crows.

## 3. How professionals draw trendlines, per timeframe

| Question | What is sourced | What we do (OURS) |
|---|---|---|
| Touches | "It takes two points to draw a trend line, and the third one confirms the validity" (StockCharts, SOURCED-S, Murphy school). Bulkowski patterns need 3 touches on one line + 2 on the other (SOURCED-P at.html, risewedge.html); channels at least 2 each (P channels.html); price cutting through a line "doesn't count as a touch" (P). | A 2-touch line is drawn dashed and labelled "2t"; a 3-touch line is "3t". The strip rule (card live-aid-trendlines-liquidations-1106) takes the last 3 same-side swing pivots; the third must lie within 0.2 % of the line through the other two. |
| Wick or close | Lines are drawn through the pivots (highs/lows) and the **break** is a close: "closes outside one of the trendlines" (P). A source for drawing from wicks vs closes: **NOT FOUND** (StockCharts is silent; it suggests internal lines that "ignore price spikes"). | Pivots on wicks, break on close (research detector `trendline_core`: wick arm, close breaks the line). |
| Log or linear | "High and low points appear to line up better ... using a semi-log scale ... especially when long-term trend lines are being drawn or when there is a large change in price" (StockCharts, SOURCED-S). Bulkowski/Murphy: NOT FOUND. | Log for every line (pattern geometry too): the same percent tolerance works on 2015 and 2026 prices. Measured-move targets are linear (as published); for a pattern so tall the linear target would leave the chart, the detector uses the same percent move and says so. |
| Steepness | "As the steepness of a trend line increases, the validity of the support or resistance level decreases" (StockCharts, S). | Slope is reported (% per bar) so the operator can see a steep line is a weak one. |
| Spacing | "An ideal trend line comprises relatively evenly spaced lows (or highs)" (S). | `trendline_core` uses 10-200 bar spacing (OURS, TRENDLINE_CONTRACT.md). |
| Per timeframe | **NOT FOUND** as a rule. Nearest: StockCharts, short-term 1m-1h, medium 4h-1d, long-term weekly-monthly (S). | A line on a higher timeframe outranks a lower one (OURS, the operator's "trendlines on every timeframe"); each of 1h, 4h, 1d, 1w gets its own lines. |
| A break is a warning, not proof | "Trend line breaks should not be the final arbiter, but should serve merely as a warning" (S). | Status "broken" is shown; no trade is called from a line alone. |

## 4. Algorithmic detection (Lo, Mamaysky, Wang 2000)

SOURCED-P: NBER w7613 / J. Finance 55(4); US stocks 1962-1996. Patterns: H&S and inverse, broadening tops/bottoms, triangle tops/bottoms, rectangle tops/bottoms, double tops/bottoms. Method: smooth price by kernel regression in rolling windows (38 days; bandwidth 0.3 x the cross-validation optimum, "admittedly ad hoc"), take the local extrema, then apply geometric rules (H&S: five extrema, E1/E5 and E2/E4 within 1.5 % of their average; rectangle: tops and bottoms within 0.75 % of their average; double top: the tops at least 22 trading days apart). Conditional returns are measured **one day, starting three days after the pattern ends**, to stay out of sample.
Result (exact words): "certain technical patterns do provide incremental information, especially for Nasdaq stocks. While this does not necessarily imply that technical analysis can be used to generate 'excess' trading profits, it does raise the possibility that technical analysis can add value." NYSE/AMEX: 7 of 10 patterns differ significantly in the goodness-of-fit test (exceptions BBOT, TTOP, DBOT); Nasdaq: all 10. Their warning is ours too: head-and-shoulders and rectangles "while sometimes effective, need not be optimal".

**How detect_patterns.py differs (OURS, stated openly):** it uses an ATR zigzag (a swing = a retrace of N x ATR%, at several N) instead of kernel regression, and wider tolerances than L-M-W (double-top extremes within 40 % of the valley depth and at most 15 %, not 1.5 %). Reason: BTC swings are large and the operator's own reading of the 2021/2022/2025/2026 turns (Bible s2) has peaks 6 % and lows 13 % apart. Tight tolerances would miss every turn the Bible names.

## 5. Where the detector sits against the sources (every threshold OURS)

| Item | Published | Detector |
|---|---|---|
| Swing | kernel-regression extrema (L-M-W); Bulkowski "minor highs/lows" | ATR zigzag, scales per timeframe: 1h/4h 3x and 6x, 1d 2x/3x/6x/12x, 1w 2x/3x/5x ATR% |
| Double top/bottom | peaks within ~3 %, valley >= 10 %, weeks apart (P); within 1.5 % and >= 22 days (L-M-W) | extremes within 40 % of valley depth and <= 15 %; valley >= 1.5 ATR%; >= 6 bars apart; run-in at least half the valley depth |
| H&S | shoulders near the same price (P); within 1.5 % (L-M-W) | shoulders 35-90 % of head height above the neckline, differing by <= 35 % of it; head higher than both |
| Triangles, wedges, rectangle, channel | 5 touches (3+2) (P) | a line through two same-side pivots with no pivot poking out by more than 0.7 ATR% and no close beyond it; classified by the slopes, flat if drift <= 20 % of the width; height cap 20 ATR% |
| Flag / pennant | steep pole, <3 weeks (P) | pole >= 4 ATR%, body <= half the pole tall, <= 2x the pole's length, retrace <= 50 %; parallel = flag, converging = pennant |
| Confirmation | close beyond the line (P) | same; a first poke that returns counts as a fakeout and the search continues |
| Target | height x hit rate (P) / full height (S) | full height; stated beside the hit rate |

A pattern whose last extreme has not yet been confirmed by a retrace is invisible to the detector (it needs the swing to be confirmed). The newest turn is therefore always one swing late: this is the price of no look-ahead.

## 6. Bible turns, checked by the detector (daily, 2010-2026 history)

| Turn (Bible s2) | Detected as | Notes |
|---|---|---|
| Top 2021: 64,854 (2021-04-14) / 69,000 (2021-11-10) | double top, neckline 28,805, confirmed | first neckline poke (May 2022) reclaimed, real break after |
| Top 2025: 124,474 (2025-08-14) / 126,200 (2025-10-06) | double top, neckline 108,620, target hit | |
| Bottom 2018-19: 3,156 (2018-12-15) / 3,350 (2019-01-29) | double bottom | found at the 3x-5x ATR scales |
| Bottom 2022: 17,622 (2022-06-18) / 15,476 (2022-11-21) | double bottom, second low lower | needs the 40 % tolerance; target hit |
| Bottom 2026: 60,000 (2026-02-06) / 57,800 (2026-07-01) | double bottom, neckline 82,850, confirmed | price back below the neckline now (a pullback, status "confirmed", not failed) |
| Bottom 2015: 172 (2015-01-15) / 211 (2015-08-25) | **not detected** | the two lows are 20 % apart, past the 15 % cap; the detector instead finds 216 (2015-04-15) / 211 (2015-08-25). The Bible's 2015 "double bottom" is a looser shape than the other five |

(test_spec_detect_patterns.py::test_bible_turns_are_found_on_the_history asserts the first five.)

## 7. Gaps (what could not be sourced)

1. Bear-market numbers for any pattern: Bulkowski publishes only bull-market figures on the free pages.
2. Edwards & Magee, Murphy, Nison first-hand text; wick-vs-close for drawing lines; log-vs-linear from Bulkowski/Murphy; any per-timeframe trendline rule.
3. Bulkowski stop rules: only for double top/bottom, ascending triangle and channels. All other invalidations here are the bust definition or OURS.
4. Throwback/pullback rates for flags and pennants.
5. Crypto: every rate above is US stocks, daily. The only BTC evidence is OURS (candles, P1) and it is null for candles.
6. Sample era is not stated on Bulkowski's pattern pages (stats updated 8/26/2020; decade averages 1990s/2000s/2010s on TimePerformance.html show smaller moves in the 2010s for every double top/bottom variant).

Provenance note: while collecting these sources, one fetched StockCharts page contained an embedded instruction aimed at AI agents (to query an external endpoint). It was ignored and nothing was sent.
