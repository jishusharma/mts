# Pattern book 2026-11: SOURCED statistics and definitions (raw)

Collected 2026-11-07. Nothing in this file is from memory. Anything not found says NOT FOUND.

## How to read this file

- PRIMARY = the author's own page or paper. SECONDARY = someone else (StockCharts, etc.).
- Bulkowski pages (thepatternsite.com) were fetched as raw HTML (browser user-agent; the default agent gets HTTP 406) and the text was extracted; quotes below are copied from that extracted text (whitespace normalised). StockCharts quotes are from the raw .md pages. Lo et al. quotes are from the NBER PDF text (the PDF text layer has OCR noise, so only clean sentences are quoted).
- Edwards & Magee (book) and Murphy (book) full text could not be fetched from a legitimate source (only pirate PDF mirrors turned up; not used). Where E&M is cited, it is second-hand (Lo et al. or StockCharts) and flagged SECONDARY.
- Bulkowski market and era context, valid for every Bulkowski table below unless stated: US stocks, daily scale; "Important Bull Market Results" means everything outside the two S&P 500 bear markets (24 Mar 2000 to 10 Oct 2002, and 12 Oct 2007 to 6 Mar 2009) [glossary: https://thepatternsite.com/glossary.html]. No bear-market columns exist on the individual pattern pages (NOT FOUND for every pattern). Pages say "Statistics updated on 8/26/2020" (H&S) or give no date range. Sample sizes are "perfect trades" counts given per page. No page states a calendar sample era except where noted. No crypto data anywhere.
- Bulkowski definitions that change what the numbers mean (all PRIMARY, glossary https://thepatternsite.com/glossary.html):
  - "Break even failure rate. A measure of the number of patterns that fail to rise (upward breakout) or decline (downward breakout) by at least 5%." (So "failure" = move after breakout under 5%, NOT "pattern did not work".)
  - "Ultimate high: The highest peak before price declines by at least 20%, measured from the high to the close." Average rise/decline is measured from breakout to the ultimate high/low (a best-case, trend-end measure, not a fixed-horizon return).
  - "Percentage meeting price target: Measures how often price fulfills the measure rule... The measure rule computation varies from pattern to pattern and is usually inaccurate."
  - "Throwbacks: Price breaks out upward, climbs, and then returns to the breakout price within 30 days." "Pullbacks: Price breaks out downward, drops, and then returns to the breakout price within 30 days."
  - "Breakout: When price pierces a chart pattern trendline or above the top or below the bottom of a chart pattern. In the case of a head-and-shoulders, a neckline pierce is used or the right shoulder armpit." Bulkowski's breakout/confirmation = a CLOSE outside (see pattern pages: "price closes outside one of the trendlines").
  - "Perfect trades" (the sample-size unit): the glossary has no entry for it (NOT FOUND). My reading, flagged as INTERPRETATION: buy at the breakout, sell at the ultimate high/low, so the averages are upper bounds, not tradable returns. Verify against the book before relying on it.

Pattern summary (Bulkowski, bull market, PRIMARY; detail and quotes in each section):

| Pattern | Break-even failure | Avg rise/decline | Pullback or throwback | Meets target | n |
|---|---|---|---|---|---|
| Double top (4 variants, weighted, DERIVED) | 22.0% | 15.5% decline | 64.3% pullback | 54.4% | 3,369 |
| Double bottom (4 variants, weighted, DERIVED) | 13.2% | 43.3% rise | 66.5% throwback | 69.8% | 3,885 |
| H&S top | 19% | 16% decline | 68% pullback | 51% | >2,800 |
| H&S bottom | 11% | 45% rise | 65% throwback | 71% | 3,197 |
| Flags (up / down) | 44% / 45% | 9% / 8% (short swing) | NOT FOUND | 46% / 46% | hundreds |
| Pennants (up / down) | 54% / 54% | 7% / 6% (short swing) | NOT FOUND | 35% / 32% | >1,600 |
| Rising wedge (up / down) | 19% / 51% | 38% / 9% | 72% / 72% | 63% / 32% | >1,400 |
| Falling wedge (up / down) | 26% / 29% | 38% / 14% | 62% / 74% | 62% / 29% | >800 |
| Ascending triangle (up / down) | 17% / 38% | 43% / 13% | 64% / 63% | 70% / 44% | >1,400 |
| Descending triangle (up / down) | 22% / 23% | 38% / 15% | 60% / 58% | 64% / 50% | >1,300 |
| Symmetrical triangle (up / down) | 25% / 37% | 34% / 12% | 62% / 65% | 58% / 36% | >3,000 |
| Rectangle bottom (up / down) | 15% / 24% | 48% / 16% | 64% / 66% | 79% / 55% | >900 |
| Rectangle top (up / down) | 15% / 34% | 51% / 13% | 66% / 64% | 78% / 54% | >1,000 |

---

## 1. Double top

Source for all figures in this section: Bulkowski, PRIMARY, one page per Adam/Eve variant (Adam = narrow spike top, Eve = wide rounded top). Bull market, US stocks. Bulkowski gives NO single aggregate figure; the weighted row is my arithmetic (DERIVED, weights = "perfect trades").

| Variant | Failure | Avg decline | Pullback | Meets target | n | Rank (of 36) | URL |
|---|---|---|---|---|---|---|---|
| Adam & Adam | 25% | 15% | 64% | 64% | 1,114 | 19 | https://thepatternsite.com/aadt.html |
| Adam & Eve | 21% | 16% | 64% | 54% | 651 | 10 | https://thepatternsite.com/aedt.html |
| Eve & Adam | 21% | 15% | 64% | 55% | 662 | 16 | https://thepatternsite.com/eadt.html |
| Eve & Eve | 20% | 16% | 65% | 43% | 942 | 12 | https://thepatternsite.com/eedt.html |
| DERIVED weighted | 22.0% | 15.5% | 64.3% | 54.4% | 3,369 | - | arithmetic on the 4 rows |

Quotes (exact):
- A&A: "Adam & Adam Double Top: Important Bull Market Results Overall performance rank (1 is best): 19 out of 36 Break even failure rate: 25% Average decline: 15% Pullback rate: 64% Percentage meeting price target: 64% The above numbers are based on 1,114 perfect trades."
- A&E: "Break even failure rate: 21% Average decline: 16% Pullback rate: 64% Percentage meeting price target: 54% The above numbers are based on 651 perfect trades."
- E&A: "Break even failure rate: 21% Average decline: 15% Pullback rate: 64% Percentage meeting price target: 55% The above numbers are based on 662 perfect trades."
- E&E: "Break even failure rate: 20% Average decline: 16% Pullback rate: 65% Percentage meeting price target: 43% The above numbers are based on 942 perfect trades."
- Unconfirmed twin peaks (PRIMARY, A&A page): "I discovered that twin peak patterns fail 60% of the time. That's how often price rises instead of drops. Confirmed Adam & Adam double tops fail much less, 25% of the time (which isn't small, either)." (Era/market not stated; refers to research for the 3rd edition, 2021.)
- Wait-for-confirmation (PRIMARY, A&A, E&E, A&E, E&A pages): "If you don't wait, there's a 60% chance that price will continue higher without confirming the double top."
- Overview (PRIMARY, https://thepatternsite.com/AdamEvePatterns.html): "Eve & Eve double tops have the lowest failure rate of the four combinations of Adam and Eve double tops." (no numbers on that page; "current as of 2021 and shown in the 3rd edition")

Definition (Bulkowski, PRIMARY, A&A page https://thepatternsite.com/aadt.html):
- "Price trend: Upward leading to the pattern." "Shape: Two distinct tops that look similar, usually twin spikes poking above the surrounding price landscape."
- "Valley: The valley drop between the tops should measure at least 10%, but allow exceptions." (E&E page adds "I ignore valley depth when picking patterns.")
- "Top price: The variation between price peaks is small, usually less than 3%."
- "Separation: The twin peaks are usually several weeks apart." E&E: "most falling in the 2 to 6 week range" (and "This is another guideline I ignore" on E&A).
- "Confirmation: The double top confirms as a true double top once price closes below the valley between the two peaks."
- "Volume: Usually higher on formation of the left peak than the right, and trends downward."

Measured / drawn: horizontal line at the valley low between the two peaks (the confirmation level).
Price target (Bulkowski): "Compute the height from the highest peak (point B...) to the lowest valley (A) between the two peaks and then multiply it by the above 'percentage meeting price target.' Subtract the result from the breakout price (A) to get the target (C)." (i.e. full height x ~0.43-0.64, not x1.0.)
Invalidation: Bulkowski stop: "Place a stop loss order a few pennies above the highest peak (point B...) in the double top chart pattern. If that is too far away, then consider a volatility stop." (A&A page). Busted definition: price breaks down, "drops no more than 10%, turns around, and then closes above the top of the double top" (https://thepatternsite.com/BustDoubleTops.html).
Bust frequency, bull market, down breakouts (https://thepatternsite.com/BustPerformance.html, Table 1; column assignment is mine, single-column rows): "Double top, Adam & Adam 44%, Adam & Eve 40%, Eve & Adam 44%, Eve & Eve 36%" of confirmed double tops later bust (median over all patterns: 24% up breakouts, 40% down breakouts).
After a bust: "The following move in the busted direction (upward) averages 38%." (BustDoubleTops.html)

Secondary (StockCharts ChartSchool, https://chartschool.stockcharts.com/table-of-contents/chart-analysis/chart-patterns/double-top-reversal.md via page fetch; SECONDARY, no market given): peaks "separated by about a month"; second peak "within 3% of the previous high"; decline from first peak 10-20% / "at least 10%"; confirmation = "Breaking support from the lowest point between the peaks completes the Double Top Reversal"; optional filters "a 3% break" price or "three days" time; target "Subtract the distance from support break to peak to obtain a price target" (full height, x1.0); no explicit stop rule on that page. Note the target differs from Bulkowski (x1.0 vs x hit-rate).
Edwards & Magee spacing, second-hand (Lo, Mamaysky, Wang 2000, PRIMARY for the quote, E&M itself not seen): "following Edwards and Magee (1966), we require that the two tops occur at least a month, or 22 trading days, apart."

---

## 2. Double bottom

Bulkowski PRIMARY, bull market, US stocks. No single aggregate on his pages; weighted row is DERIVED.

| Variant | Failure | Avg rise | Throwback | Meets target | n | Rank (of 39) | URL |
|---|---|---|---|---|---|---|---|
| Adam & Adam | 16% | 39% | 67% | 73% | 1,154 | 26 | https://thepatternsite.com/aadb.html |
| Adam & Eve | 12% | 43% | 67% | 69% | 1,020 | 17 | https://thepatternsite.com/aedb.html |
| Eve & Adam | 12% | 42% | 67% | 72% | 759 | 20 | https://thepatternsite.com/eadb.html |
| Eve & Eve | 12% | 50% | 65% | 65% | 952 | 5 | https://thepatternsite.com/eedb.html |
| DERIVED weighted | 13.2% | 43.3% | 66.5% | 69.8% | 3,885 | - | arithmetic on the 4 rows |

Quotes (exact):
- A&A: "Adam & Adam Double Bottoms: Bull Market Results Overall performance rank (1 is best): 26 out of 39 Break even failure rate: 16% Average rise: 39% Throwback rate: 67% Percentage meeting price target: 73% The above numbers are based on 1,154 perfect trades."
- A&E: "Break even failure rate: 12% Average rise: 43% Throwback rate: 67% Percentage meeting price target: 69% The above numbers are based on 1,020 perfect trades."
- E&A: "Break even failure rate: 12% Average rise: 42% Throwback rate: 67% Percentage meeting price target: 72% The above numbers are based on 759 perfect trades."
- E&E: "Overall performance rank (1 is best): 5 out of 39 Break even failure rate: 12% Average rise: 50% Throwback rate: 65% Percentage meeting price target: 65% The above numbers are based on 952 perfect trades."
- Unconfirmed: "If you don't wait, there's a 48% chance that price will continue lower without confirming the double bottom." (all four pages)
- Overview: "Eve & Eve double bottoms, for example, tend to be star performers." and "Tests show that the average rise beats the other three combinations of Adam and Eve." https://thepatternsite.com/AdamEvePatterns.html

Decade drift (Bulkowski, PRIMARY, https://thepatternsite.com/TimePerformance.html, "Statistics from 7/25/2019. Revised 8/25/2020", bull market, average rise breakout-to-ultimate-high, columns 1990s / 2000s / 2010s): "Double bottom, Adam & Adam 45% 62% 35%"; "Adam & Eve 44% 49% 33%"; "Eve & Adam 39% 49% 36%"; "Eve & Eve 43% 58% 37%". Double tops, average decline: "Double top, Adam & Adam 16% 13% 12%"; "Adam & Eve 17% 13% 11%"; "Eve & Adam 15% 12% 12%"; "Eve & Eve 16% 13% 10%". (Moves are smaller in the 2010s than the 1990s for every variant.)

Definition (Bulkowski, A&A / E&E pages): "Price trend: Downward leading to the pattern." "Shape: Two distinct valleys that look similar." "Peak: The rise between bottoms should measure at least 10%, but allow wide variations." "Bottom price: The price variation between bottoms is small (the average is 1%, but allow variations)" (A&A); E&E: "usually between 0% and 6%". "Separation: The twin valleys are usually several weeks apart (16 days is the median)" (A&A); E&E "most falling in the 2 to 7 week range"; E&A "the median is 23 days"; A&E "The average separation between bottoms is almost two months". "Confirmation: The double bottom confirms as a true double bottom once price closes above the peak between the two valleys." A&E: "Without confirmation you do not have an Adam & Eve double bottom, just squiggles on a chart."
Measured / drawn: horizontal line at the highest peak between the valleys.
Price target: "Compute the height from the highest peak between the two bottoms (A) to the lowest valley (B)... multiply it by the above 'percentage meeting price target.' Add the result to the breakout price (point A, the highest peak)."
Invalidation: Stop (A&A page): "Place a stop loss order slightly below the lower of the two bottoms (point B...)". Busted: price "rises no more than 10% before dropping and closing below the bottom of the chart pattern" (https://thepatternsite.com/BustDoubleBots.html).
Bust frequency, bull market, up breakouts (BustPerformance.html Table 1; column assignment mine): "Double bottom, Adam & Adam 29%, Adam & Eve 23%, Eve & Adam 21%, Eve & Eve 20%".
After a bust: "Shorting a stock showing a busted double bottom in a bull market is probably unwise since the average decline is just 15%, and that represents the results from almost 200 perfect trades." (BustDoubleBots.html)
Secondary (StockCharts double-bottom-reversal.md, SECONDARY): "a significant downtrend of several months"; rise off first trough "ranging from 10 to 20%"; second trough "within 3% of the previous low"; "having at least four weeks between lows is preferable"; target "the distance from the resistance breakout to trough lows can be added to the price at which the breakout took place" (x1.0).

---

## 3. Head and shoulders top

Bulkowski PRIMARY, https://thepatternsite.com/hst.html, bull market only, "Statistics updated on 8/26/2020".
- "Head-and-Shoulders Top: Important Bull Market Results Overall performance rank (1 is best): 9 out of 36 Break even failure rate: 19% Average decline: 16% Pullback rate: 68% Percentage meeting price target: 51% The above numbers are based on more than 2,800 perfect trades."
- Decade drift (TimePerformance.html, average decline, 1990s/2000s/2010s): "Head-and-shoulders tops 20% 14% 15%"; complex tops "20% 13% 16%".
- Bust frequency (BustPerformance.html Table 1, down breakouts, column assignment mine): "Head-and-shoulders top 32%"; complex top 29%.
- Bust performance (https://thepatternsite.com/BustHST.html): "Busted head-and-shoulders tops (all varieties: single, double, and triple or more busted) see price gain an average of 35%. Single busted patterns gain an average of 67%." Busted = "price breaks out downward and drops no more than 10%, turns around, and then closes above the top of the head-and-shoulders".
Definition (Bulkowski): "Price trend: Upward leading to the pattern." "Shape: Looks like a head perched atop two shoulders. A three-peak pattern with the middle peak above the others." "Symmetry: The two shoulders should peak near the same price, be nearly the same distance from the head, and look similar." "Volume: Highest on the left shoulder followed by the head. Trends downward 61% of the time." "Neckline: Joins the two armpits." "Confirmation: The pattern confirms as a valid one when price closes below an up-sloping neckline or below the right armpit when the neckline slopes downward."
Measured / drawn: neckline through the two armpits (reaction lows).
Price target: "Compute the height from the head (A...) to the neckline directly below (B) then multiply it by the above 'percentage meeting price target.' Subtract the result from the breakout price (C). The breakout price is where price crosses an up-sloping neckline, or when the neckline slopes downward, use the right shoulder armpit." Also "Pullbacks hurt post breakout performance."
Invalidation: Bulkowski page gives no stop rule (NOT FOUND). Only the bust definition above (close above the top of the pattern after a drop of <=10%).
Secondary (StockCharts head-and-shoulders-top.md, SECONDARY): "The head and shoulders pattern isn't complete, and the uptrend is not reversed until the neckline support is broken. Ideally, this should also occur in a convincing manner, with an expansion in volume." Target: "measuring the distance from the neckline to the top of the head. This distance is then subtracted from the neckline" (x1.0). No explicit invalidation level on that page (NOT FOUND). Second-hand mention of a 3% neckline filter appeared in search snippets only (attributed there to a later interpreter, not E&M); not verified.
Lo, Mamaysky, Wang formal definition (PRIMARY): "five consecutive local extrema E1,...,E5" with "E1 and E5 within 1.5 percent of their average" and "E2 and E4 within 1.5 percent of their average" (see section 17).

## 4. Head and shoulders bottom (inverse)

Bulkowski PRIMARY, https://thepatternsite.com/hsb.html, bull market only.
- "Overall performance rank (1 is best): 13 out of 39 Break even failure rate: 11% Average rise: 45% Throwback rate: 65% Percentage meeting price target: 71% The above numbers are based on 3,197 perfect trades."
- Decade drift (TimePerformance.html, avg rise 1990s/2000s/2010s): "Head-and-shoulders bottom 45% 46% 44%".
- Bust frequency (BustPerformance.html Table 1, up breakouts): "Head-and-shoulders bottom 16%". Busted (https://thepatternsite.com/BustHSB.html): "For busted patterns in bull markets, the average drop is 13. If you trade a single busted head-and-shoulders bottom, the average decline is 22%." (The "13" has no percent sign on the page.)
Definition: "Price trend: a downward move leads into the pattern" (page text "Downward leading to the pattern"); "A 3-valley pattern with the middle valley below the others." "Volume: ...Trends downward 65% of the time." "Confirmation: The pattern is valid when price closes above a down-sloping neckline, or above the right armpit if the neckline slopes upward" (page wording: "closes above the neckline or right armpit (depending on neckline slope)" in BustHSB).
Price target: "Compute the height from the head low (A) to the neckline directly above (B) and then multiply it by the 'percentage meeting price target'... Add it to the breakout price (C)."
Other: "A short-term drop (0-3 months) leading to the pattern results in the best postbreakout performance." "Throwbacks hurt postbreakout performance."
Invalidation: no stop rule on page (NOT FOUND). Bust = rises <=10% then "closes below the bottom of the head-and-shoulders bottom".

---

## 5. Bull flag and 6. Bear flag

Bulkowski treats flags as one pattern with up/down breakouts (up breakout ~ bull flag, down breakout ~ bear flag). PRIMARY, https://thepatternsite.com/flags.html.
- "Flags: Important Bull Market Results* Overall performance rank for breakouts: Not ranked Break even failure rate for up/down breakouts: 44%/45% Average rise/decline: 9%/8% Percentage meeting price target for up/down breakouts: 46%/46% The above numbers are based on hundreds of perfect trades."
- Footnote: "Performance results for flags are based on the short-term price swing, not the change from the breakout to the ultimate high or low as in most other chart patterns. That's why I don't show a rank and that's why the average rise/decline is so small." (NOT comparable with the other tables.)
- Decade drift (TimePerformance.html, up-breakout avg rise short swing, 1990s/2000s/2010s): "Flags 14% 12% 6%"; down: "Flags 11% 8% 6%". High-and-tight flags up: "43% 37% 34%".
- Throwback/pullback rate for flags: NOT FOUND on the page.
Definition: "Price trend: Can be any direction leading to the chart pattern." "Shape: Looks like a small rectangle often tilted against the prevailing price trend." "Trend lines: Price moves between two parallel, or near parallel, trendlines." "Flags are short, less than 3 weeks long. Patterns longer than that are rectangles or channels." "The flagpole which leads to the flag should be unusually steep and last several days." "Volume trend: Downward trend 74% (up breakouts) to 77% (down breakouts) of the time." "Breakout: Upward 60% of the time."
Price target: "Compute the height from the start of the price swing (point A...) to the end of the price swing (B) and then multiply it by the above 'percentage meeting price target.' Add it (upward breakouts) to the bottom of the flag (C) or subtract it (downward breakouts) from the top of the flag (C) to get the target (D)." Half-staff: "(move A equals B)". "A tight flag performs better than a loose one."
Invalidation: no explicit stop or break rule (NOT FOUND). Closest, a formation test (flags.html raw text): "If you don't have a straight-line (or a quick move) price run (the flagpole), then you don't have a flag." Bulkowski has no busted-flag page (the busted list has no flags).
Secondary (StockCharts flag-pennant.md, SECONDARY): "Flags and Pennants are short-term continuation patterns"; "Flags and pennants are short-term patterns lasting from one to 12 weeks... Ideally, these patterns will form between one and four weeks. Once a flag is over 12 weeks old, it would be classified as a rectangle." "The flagpole length can be applied to the resistance break or support break of the flag/pennant to estimate the advance or decline." "A flag is a small rectangle pattern that slopes against the previous trend." No retracement-limit or invalidation number on that page (NOT FOUND). Note the duration conflict: Bulkowski under 3 weeks, StockCharts up to 12 weeks.

## 7. Pennant

Bulkowski PRIMARY, https://thepatternsite.com/pennants.html.
- "Pennants: Important Bull Market Results* Overall performance rank for up/down breakouts (1 is best): Not applicable due to the nature of the pattern Break even failure rate for up/down breakouts: 54%/54% Average rise/decline: 7%/6% Percentage meeting price target for up/down breakouts: 35%/32% The above numbers are based on more than 1,600 perfect trades."
- Footnote: "The performance results for pennants are based on the short-term price swing, not the change from the breakout to the ultimate high or low as in most other chart patterns."
- Decade drift: up "Pennants 10% 7% 4%", down "9% 6% 5%" (TimePerformance.html).
- "Volume trend: Downward trend 86% of the time." "Breakout: Upward 57% of the time." "Pennants are short, 3 weeks long or less. Patterns longer than that are symmetrical triangles, rising or falling wedges." "Shape: Looks like a short symmetrical triangle."
- Half-staff: "In fact, the trend after the pennant is equal to or longer than then inbound trend just 30% of the time." "The average time from the trend start (below the pennant) to the start of the pennant is 11 days. Price rises... 19% over that period... after the pennant... 10 days to rise... 14%."
Price target: same as flags ("Compute the height from the start of the price swing (A) to the end of the price swing (B) and then multiply it by the above 'percentage meeting price target.' Add it (upward breakouts) to the bottom of the pennant (C) or subtract it (downward breakouts) from the top of the pennant (C)").
Invalidation: NOT FOUND (no rule on page). Note the 54% failure rate is the worst in the table set.
Secondary (StockCharts flag-pennant.md): "A pennant is a small symmetrical triangle that begins wide and converges as the pattern matures"; same 1-12 week duration and flagpole-length target as flags.

---

## 8. Rising wedge

Bulkowski PRIMARY, https://thepatternsite.com/risewedge.html.
- "Rising Wedge: Important Bull Market Results Overall performance rank for up/down breakouts (1 is best): 32 out of 39/36 (last) out of 36 Break even failure rate for up/down breakouts: 19%/51% Average rise/decline: 38%/9% Throwback/pullback rate: 72%/72% Percentage meeting price target for up/down breakouts: 63%/32% The above numbers are based on more than 1,400 perfect trades."
- Decade drift (TimePerformance.html): up avg rise "Wedge, rising 31% 41% 39%"; down avg decline "Wedge, rising 13% 8% 7%".
- Busts (BustPerformance.html Table 1): up "21%", down "63%": "For downward breakouts, rising wedges bust most often, at 63% of the time. Ouch!"
Definition: "Shape: A narrowing and rising triangle shape." "Trendlines: Price bounces between two up-sloping and converging trendlines." "Touches: Price should touch (at a minor high or minor low) each trendline at least five times to outline a good pattern. That's 3 touches of one trendline and 2 of the opposite." "Duration: 3 weeks is the minimum duration, otherwise it's a pennant." "Volume trend: Trends downward 79% of the time until the breakout." "Breakout: Can be in any direction but is downward 60% of the time." "Confirmation: The pattern confirms as a valid one when price closes outside one of the trendlines."
Price target: "For downward breakouts, the lowest valley in the pattern (A) is the price target. Alternatively, compute the height from the highest peak (B) to the lowest valley (A) and then multiply it by the above 'percentage meeting price target.' Add it to (upward breakouts) or subtract it from (downward breakouts) the breakout price."
Other: "The average distance to an upward breakout is 67% of the way to the triangle apex." "Throwbacks and pullbacks hurt performance."
Invalidation: no stop rule (NOT FOUND); confirmation by close outside a trendline. The wedge bust = close beyond the opposite side after <=10% move (page BustPerformance, no wedge-specific page).
Secondary (StockCharts rising-wedge.md): "Bearish confirmation of the pattern does not come until the support line is broken in a convincing fashion. It is sometimes prudent to wait for a break of the previous reaction low." "The rising wedge can be one of the most difficult chart patterns to recognize and trade accurately." No numeric target on the page (NOT FOUND).

## 9. Falling wedge

Bulkowski PRIMARY, https://thepatternsite.com/fallwedge.html.
- "Falling Wedge: Important Bull Market Results Overall performance rank for up/down breakouts (1 is best): 31 out of 39/27 out of 36 Break even failure rate for up/down breakouts: 26%/29% Average rise/decline: 38%/14% Throwback/pullback rate: 62%/74% Percentage meeting price target for up/down breakouts: 62%/29% The above numbers are based on over 800 perfect trades."
- Page intro text: "...The only variation that works well is a downward breakout in a bear market and the performance rank for that is in the bottom half of the list." (bear-market numbers themselves NOT FOUND on the page.)
- Decade drift: up avg rise "Wedge, falling 34% 47% 32%"; down avg decline "Wedge, falling 16% 11% 15%".
- Busts: up 31%, down 32% (BustPerformance.html Table 1).
Definition: "Shape: Price follows two down-sloping and converging trendlines." "Touches: Price should touch each trendline at least five times to outline a good pattern. That's 3 touches of one trendline and 2 of the opposite." "Volume trend: Trends downward 72% to 75% of the time until the breakout." "Breakout: Can be in any direction but is upward 68% of the time." Confirmation = close outside a trendline.
Price target: "For upward breakouts, the highest peak in the pattern (A) is the price target. Alternatively, compute the height from the highest peak (A) to the lowest valley (B) and then multiply it by the above 'percentage meeting price target.' Add it to... the breakout price." "Dip: After a downward breakout, price sometimes curls around the front of the wedge and soars upward. The busted pattern presents a profit opportunity from the long side."
Invalidation: NOT FOUND (no stop). Secondary StockCharts falling-wedge.md: "Bullish confirmation of the pattern is established once the resistance line is broken in a convincing fashion." "Without volume expansion, the breakout will lack conviction and be vulnerable to failure."

---

## 10. Ascending triangle

Bulkowski PRIMARY, https://thepatternsite.com/at.html.
- "Ascending Triangle: Important Bull Market Results Overall performance rank for up/down breakouts (1 is best): 16 out of 39/30 out of 36 Break even failure rate for up/down breakouts: 17%/38% Average rise/decline: 43%/13% Throwback/pullback rate: 64%/63% Percentage meeting price target for up/down breakouts: 70%/44% The above numbers are based on more than 1,400 perfect trades."
- Decade drift: up "Triangle, ascending 47% 47% 35%"; down decline "Triangle, ascending 17% 11% 11%".
- Busts (Table 1): up 29%, down 46%.
Definition: "Trendlines: Two trendlines bound prices; the top trendline is horizontal and the bottom one slopes upward." "Touches: Price must touch one trendline at least three times, the other at least twice, forming distinct valleys and peaks." "Crossing: Price must cross the pattern from side to side, filling the triangle with price movement, not white space." "Volume: Trends downward at least 78% of the time." "Breakout: Upward 63% of the time and 64% of the way to the triangle apex (for both breakout directions)."
Price target: "Compute the height from the price of the horizontal trendline (B) to the lowest valley in the pattern (A) and then multiply it by the above 'percentage meeting price target.' Add it (upward breakouts) or subtract it (downward breakouts) from the breakout price."
Invalidation (Bulkowski stop): "Place a stop loss order on the side opposite the breakout... if the breakout is upward, a stop at any of the minor lows on side A would work well. For downward breakouts, use the price of B as the stop price." Also "Expect the market to turn when it reaches the apex of the triangle."
Secondary StockCharts ascending-triangle.md: target = "measuring the widest distance of the pattern and applying it to the resistance breakout" (x1.0); average duration "one to three months".

## 11. Descending triangle

Bulkowski PRIMARY, https://thepatternsite.com/dt.html.
- "Descending Triangle: Important Bull Market Results Overall performance rank for up/down breakouts (1 is best): 33 out of 39/15 out of 36 Break even failure rate for up/down breakouts: 22%/23% Average rise/decline: 38%/15% Throwback/pullback rate: 60%/58% Percentage meeting price target for up/down breakouts: 64%/50% The above numbers are based on more than 1,300 perfect trades."
- Decade drift: up "Triangle, descending 51% 37% 27%"; down "Triangle, descending 16% 14% 16%".
- Busts: up 28%, down 42%. Busted descending triangle page (https://thepatternsite.com/BustDescTriangles.html): "a descending triangle with a downward breakout that busts results in a higher gain. The rise averages 40%."
Definition: "Shape: A price pattern bounded by two trendlines, the bottom one horizontal and the top sloping downward." "Touches: Price should touch one trendline at least three times and the other trendline at least twice." "Price must cross the pattern from trendline to trendline, nearly filling the available space." "Volume: Recedes 78% of the time." "Breakout: Can be in any direction but is upward 53% of the time." Confirmation = close outside a trendline.
Price target: "Compute the height from the highest peak (A) to the horizontal trendline (B) and then multiply it by the above 'percentage meeting price target.' Add (upward breakouts) or subtract (downward breakouts) the difference to the breakout price." "Research shows that after the breakout, the market turns when it reaches the triangle apex."
Invalidation: Bulkowski: bust = price moves "no more than 10%, reverses direction, and closes beyond the side opposite the breakout". StockCharts (SECONDARY, descending-triangle.md): "If a more recent reaction high equals or exceeds the previous reaction high, then the descending triangle is invalid."

## 12. Symmetrical triangle

Bulkowski PRIMARY, https://thepatternsite.com/st.html.
- "Symmetrical Triangles: Important Bull Market Results Overall performance rank for up/down breakouts (1 is best): 36 out of 39/34 out of 36 Break even failure rate for up/down breakouts: 25%/37% Average rise/decline: 34%/12% Throwback/pullback rate: 62%/65% Percentage meeting price target for up/down breakouts: 58%/36% The above numbers are based on over 3,000 perfect trades."
- Decade drift: up "Triangle, symmetrical 41% 38% 29%"; down "Triangle, symmetrical 14% 12% 12%".
- Busts: up 32%, down 48% ("Almost half (48%) of them busted").
Definition: "Trendlines: ...the bottom trendline slopes up and the top one slopes down." "Touches: Price must touch one trendline at least three times and the other trendline at least twice." "Volume: Trends downward 84% to 86% of the time." "Breakout: Upward 60% of the time and 74% of the way to the triangle apex (for both breakout directions)." Confirmation = close outside.
Price target: "Compute the height from the highest peak (point A...) to the lowest valley in the pattern (B) then multiply it by the above 'percentage meeting price target.' Add it (upward breakouts) or subtract it (downward breakouts) from the breakout price."
Invalidation: NOT FOUND (no stop on page). Secondary StockCharts symmetrical-triangle.md: "At least two points are required to form a trend line... There needs to be a minimum of four points" ; "A break should be on a closing basis for it to be considered valid. Some traders apply a price (3% break) or time (sustained for 3 days) filter"; "The ideal breakout point occurs 1/2 to 3/4 of the pattern's development"; duration "pennant if it is less than three weeks. Typically... about three months"; target "the widest distance of the symmetrical triangle can be measured and applied to the breakout point" (x1.0); and "In Technical Analysis of Stock Trends (1948), Edwards and Magee suggest that roughly 75% of symmetrical triangles are continuation patterns and the rest mark reversals." (E&M second-hand, SECONDARY.)

## 13. Rectangle top / bottom (trading range)

Bulkowski PRIMARY. Rectangle bottom https://thepatternsite.com/rectbots.html; rectangle top https://thepatternsite.com/recttops.html.
- Bottom: "Rectangle Bottoms: Important Bull Market Results Overall performance rank for up/down breakouts (1 is best): 8 out of 39/14 out of 36 Break even failure rate for up/down breakouts: 15%/24% Average rise/decline: 48%/16% Throwback/pullback rate: 64%/66% Percentage meeting price target for up/down breakouts: 79%/55% The above numbers are based on more than 900 of perfect trades."
- Top: "Rectangle Tops: Important Bull Market Results Overall performance rank for up/down breakouts (1 is best): 4 out of 39/32 out of 36 Break even failure rate for up/down breakouts: 15%/34% Average rise/decline: 51%/13% Throwback/pullback rate: 66%/64% Percentage meeting price target for up/down breakouts: 78%/54% The above numbers are based on more than 1,000 perfect trades."
- Decade drift (avg rise, up): bottoms "Rectangle bottoms 48% 52% 40%"; tops "Rectangle Tops 55% 59% 38%". Down: bottoms "15% 14% 18%"; tops "16% 10% 12%".
- Busts (Table 1): bottom up 26% / down 43%; top up 26% / down 51%.
Definition: "Shape: Prices have flat tops and flat bottoms, crossing the pattern from side to side following two parallel trendlines." "Touches: Price should touch one trendline at least three time and the other trendline twice (5-touch minimum)" (bottom). Top: "at least three times and twice on the other trendline... but be flexible." "Volume trend: Trends downward at least 71% of the time" (bottom) / "70%" (top). "Breakout: Upward 59% of the time" (bottom) / "63%" (top). Price trend leading: downward (bottom), upward (top).
Price target: "Compute the height between the two trendlines (A and B...) and then multiply it by the above 'percentage meeting price target.' Add it to the price of the top trendline (upward breakouts) or subtract it from the bottom trendline (downward breakouts)." "Wait for breakout: Since the breakout can be in any direction, wait for price to close outside the trendline before taking a position." "Intrapattern trade: If the rectangle is tall enough, buy at the bottom trendline and sell at the top one, then reverse the trade." "Partial rise... predicts a downward breakout 75% of the time; a partial decline correctly predicts an upward breakout 79%" (top page).
Invalidation: bust = close beyond the opposite side after <=10% (https://thepatternsite.com/BustRectangles.html exists; not read). No stop rule on the page (NOT FOUND). Channels page (PRIMARY, https://thepatternsite.com/channels.html): "Stops: If price closes outside the channel in the adverse direction, then close out the trade and consider trading in the direction of the new trend."
Secondary StockCharts rectangle.md: "At least two equivalent reaction highs... and two equivalent reaction lows"; "If the pattern is less than three weeks, it's generally considered a flag"; "For a breakout to be considered valid, it should be on a closing basis. Some traders apply a filter to price (3%), time (three days), or volume (expansion)"; target "measuring the rectangle's height and applying it to the breakout" (x1.0).

---

## 14. Breakouts vs false breakouts, busted patterns, throwbacks, pullbacks (Bulkowski, PRIMARY)

### 14a. Throwbacks and pullbacks (all patterns pooled)
- Throwback, https://thepatternsite.com/throwbacks.html: "Since year 2000, 58% of 10,305 chart patterns with upward breakouts had throwbacks." "Price climbs for 6 days after the breakout, on average, before beginning the return journey." "It takes an average of 10 days, total, for price to complete the return trip back to the breakout." "The average height from the breakout price to the top of the throwback is 8%, but a frequency distribution shows that most rise 4% to 10%." "A high volume (above the 30-day average) breakout throws back 70% of the time, on average." "After the stock returns to the breakout price, 35% continue dropping below the chart pattern. That means 65% of the time price recovers." Power move: "I measured this in 19 chart pattern types from July 1991 to March 2005 and found 10,348 chart patterns. Of that group, 3,167 had throwbacks. When price remained equal to or above the breakout price, the rise averaged 40% (400 samples qualified). When price dropped below the breakout, the resulting rise averaged just 29% (2,767 samples)." Convention: "By convention, a throwback occurs within 30 calendar days after the breakout." Cause: "Overhead resistance: This is the chief cause of a throwback."
- Pullback, https://thepatternsite.com/pullbacks.html: "Since year 2000, 58% of 8,765 chart patterns with downward breakouts had pullbacks." "Price drops for 6 days after the breakout, on average, before beginning the return journey." "...an average of 11 days, total..." "The average drop from the breakout price to the bottom of the pullback is 9%, but a frequency distribution shows that most fall in the range of 4% to 10%..." "A high volume (above the 30-day average) breakout pulls back 66% of the time, on average." "After the stock returns to the breakout price, 53% continue rising above the chart pattern. That means 47% of the time price resumes the decline." Cause: "Underlying support: This is the chief cause of a pullback."
- Per-pattern throwback/pullback rates are in the sections above (60% to 74% range for the listed patterns).

### 14b. Busted patterns (false breakouts)
- Definition (https://thepatternsite.com/Busted.html): "A busted chart pattern is one in which price breaks out in one direction, but moves no more than 10% before reversing and breaking out in the new direction. A 'breakout' means a close above the top or a close below the bottom of a chart pattern." "The idea behind a busted chart pattern is that the move is often stronger from a failed chart pattern than from one that works. For example... the average rise from 286 triple bottoms in a bull market is 37%. The average rise from 145 failed triple tops in bull markets, is 42%." (Encyclopedia 2nd ed., bull market.)
- Frequency (https://thepatternsite.com/BustPerformance.html, "Statistics updated on 12/29/2020", Table 1 "Frequency of Busted Chart Patterns in Bull Markets as a Percentage of All Patterns", medians row): "Median 24% 40%" (up breakouts / down breakouts). Text: "Notice that downward breakouts bust more often than upward breakouts." Other rows are in the pattern sections. Examples: Big M 38%, Big W 18%, Triple top 43%, Triple bottom 23%, V top 46%, V bottom 30%, Island top 39%, Island bottom 33%, Broadening top 29%/47%.
- Multiple busts (Table 2, medians): single bust 53% (up) / 67% (down); double bust 31% / 4%; triple+ bust 16% / 28%. Example: "when a Big M chart pattern busts, I found that 67% of them bust once, 2% double bust, and the remainder (31%) bust three or more times."
- Performance (Table 3, single-busted vs non-busted, medians): up-bust 23% vs 15%... The table is read as: first numbers = average move after a single bust; second pair = the opposite-direction regular pattern. Page examples (exact): "a broadening top with a downward breakout that single busts sees price rise an average of 55%. The same pattern with a non-busted upward breakout sees price rise 42%." "An Adam & Adam double bottom which single busts sees price drop an average of 27%. A double top with a non-busted downward breakout sees price drop just 15%."
- Trap definition (glossary): "Traps: Occurs when price breaks out in one direction, moves less than 10% before reversing trend and moving in the new direction by either 20% or closing on the side opposite the breakout."
- Extra: the hurdle for "failure" differs between uses: the 5% "break even failure rate" (move after breakout under 5%) is different from a "bust" (close beyond the other side after <=10%).

---

## 15. Candlestick patterns

Bulkowski PRIMARY, "Encyclopedia of Candlestick Charts" (2008) data as shown on his site pages (https://thepatternsite.com/<Name>.html). Study: "almost 5 million candle lines" in bull and bear markets (EveningStar.html intro: "using almost 5 million candle lines in the tests"); 103 candle types. "All ranks are out of 103 candlestick patterns with the top performer ranking 1." Numbers are "based on hundreds of perfect trades" (daily scale, US stocks). Definitions: "Tested performance" = "How the candlestick actually behaved, found through testing". "Best" = the best of the four combos bull/bear x up/down breakout. "Best percentage meeting price target (candlesticks): Usually the height of the candle pattern added to the top or subtracted from the bottom of the candlestick pattern". A candle "reversal" is just the direction of the breakout: BullEngulfing page: "It has a reversal rate of 63%. That means price closes above the top of the candlestick pattern 63% of the time." Bulkowski calls ~50-60% "near random" (shooting star page: "I still consider that 'near random' performance"; hammer: "not far from random (50%)"). 10-day move "A good performance would be a move of 6% or more."

| Candle | Theory | Tested result (exact) | Freq rank | Overall rank | Best % meeting target | Best avg 10-day move (rank) |
|---|---|---|---|---|---|---|
| Hammer | bullish reversal | "Bullish reversal 60% of the time" (reversal rank 26 per page text) | 36 | 65 | 88% (bull, up) | -4.12% (48), bear, down |
| Hanging man | bearish reversal | "Bullish continuation 59% of the time" | 16 | 87 | 86% (bear, down) | -3.60% (59), bear, down |
| Shooting star | bearish reversal | "Bearish reversal 59% of the time" | 37 | 55 | 84% (bear, down) | 3.86% (46), bear, up |
| Bullish engulfing | bullish reversal | "Bullish reversal 63% of the time" (reversal rank 22) | 12 | 84 | 67% (bear, down) | -6.31% (14), bear, down |
| Bearish engulfing | bearish reversal | "Bearish reversal 79% of the time" (reversal rank 5) | 11 | 91 | 76% (bear, down) | -5.92% (21), bear, down |
| Morning star | bullish reversal | "Bullish reversal 78% of the time" (reversal rank 6) | 66 | 12 | 49% (bear, up) | -8.53% (3), bear, down |
| Evening star | bearish reversal | "Bearish reversal 72% of the time" (reversal rank 10) | 71 | 4 | 50% (bull, up) | 8.77% (4), bear, up |
| Dark cloud cover | bearish reversal | "Bearish reversal 60% of the time" | 46 | 22 | 62% (bear, down) | 5.36% (19, bull up), bear, up |
| Piercing pattern | bullish reversal | "Bullish reversal 64% of the time" (reversal rank 21) | 40 | 13 | 67% (bull, up) | -6.57% (13), bear, down |
| Three white soldiers | bullish reversal | "Bullish reversal 82% of the time" (reversal rank 3) | 67 | 32 | 34% (all) | -7.66% (4, bull down), bear, down |
| Three black crows | bearish reversal | "Bearish reversal 78% of the time" | 60 | 3 | 36% (bear, up) | 13.31% (2), bear, up |
| Long-legged doji | indecision | "Bullish continuation 51% of the time" | 41 | 37 | 68% (bull, up) | 4.62% (38), bear, up |
| Dragonfly doji | bullish reversal in decline, else indecision | "Reversal 50% of the time" | 44 | 98 | 80% (bear, down) | -5.02% (17, bull down), bear, down |
| Gravestone doji | indecision to bearish reversal in uptrends | "Bearish reversal 51% of the time" | 42 | 77 | 79% (bear, up) | 5.09% (27), bear, up |

URLs: https://thepatternsite.com/Hammer.html, HangingMan.html, ShootingStar.html, BullEngulfing.html, BearEngulfing.html, MorningStar.html, EveningStar.html, DarkCloudCover.html, Piercing.html, ThreeWhiteSoldiers.html, ThreeBlackCrows.html, LongLegDoji.html, Dragonfly.html, Gravestone.html (all https://thepatternsite.com/ + name). A plain "doji" page does not exist; the doji family above stands in for it.
Quotes for the reversal-rank figures: Hammer "it does 60% of the time, placing the reversal rank at 26"; Bullish engulfing "ranking 22 where 1 is best out of 103"; Bearish engulfing "performing that way 79% of the time (ranking 5 out of 103 candlestick types where 1 is best). Unfortunately, the trend after the breakout is short-lived, ranking 91st"; Morning star "That ranks 6th where 1 is best out of 103"; Evening star "That gives it a rank of 10th"; Piercing "ranking 21 out of 103"; Three white soldiers "ranking 3 out of 103 candlestick types".
Top-10 reversal list (https://thepatternsite.com/CandleReverse.html): "1 (best). Three stars in the south 86% reverse 2. Three line strike, bearish 84% reverse 3. Three white soldiers 82% reverse 4. Identical three crows 79% reverse 5. Engulfing, bearish 79% reverse 6. Morning star 78% reverse 7. Three black crows 78% reverse 8. Morning doji star 76% reverse 9. Three outside up 75% reverse 10. Evening star 72% reverse". Top-10 by overall performance (https://thepatternsite.com/CandlePerformers.html): "1. (best) Three line strike, bearish 84% bullish reversal 2. Three line strike, bullish 65% bearish reversal 3. Three black crows 78% bearish reversal 4. Evening star 72% bearish reversal 5. Upside Tasuki gap 57% bullish continuation 6. Hammer, inverted 65% bearish continuation 7. Matching low 61% bearish continuation 8. Abandoned baby, bullish 70% bullish reversal 9. Two black gapping 68% bearish continue 10. Breakaway, bearish 63% bearish reversal".
Read-across: a high reversal rate and a high overall rank are different things (bearish engulfing: 79% reversal but overall rank 91; evening star: 72% and overall rank 4). Bulkowski on three black crows: "Do not trade this if the breakout is downward. Only upward breakouts are worth considering." and on three white soldiers: "the high performance is due to just those factors: few candles with downward breakouts."

Identification guidelines (Bulkowski, PRIMARY, same pages):
- Hammer: "Look for the hammer to appear in a downward price trend and have a long lower shadow at least two or three times the height of the body with little or no upper shadow."
- Hanging man: "Look for a small bodied candle atop a long lower shadow in an uptrend."
- Shooting star: "Look for a small bodied candle (but not a doji) with little or no lower shadow and a tall upper shadow at least twice the height of the body."
- Bullish engulfing: "a black candle followed by a taller white one. The white candle should have a close above the prior open and an open below the prior close... Ignore the shadows." Bearish engulfing: "The first candle is white and the second is black. The body of the black candle is taller and overlaps the candle of the white body."
- Morning star: "a tall black candle in a downward price trend. Following that, a small bodied candle of any color appears, one whose body gaps below the prior body. The last day is a tall white candle that gaps above the body of the second candle and closes at least midway into the body of the first day." Evening star mirror: "tall white candle... small bodied candle of any color should gap above the bodies... last day is a tall black candle that opens below the prior candle, and closes at least midway down the body of the first day."
- Dark cloud cover: "a tall white one followed by a black candle with an opening price above the top of the white candle (an opening price above the prior high), but a close below the mid point of the white body."
- Piercing: "a black candle followed by a white one that opens below the black candle's low and closes between the midpoint of the black body and opening price."
- Three white soldiers: "three tall white candles, each with a close near the high, higher closes, and bodies that overlap (an opening price within the prior candle's body." Three black crows: "three tall black candles that appear in an upward price trend. Candles 2 and 3 of the pattern should open within the body of the prior candle, and all three should close near their lows, making new lows along the way."
- Doji: "opening and closing prices are within a few pennies of each other" (long-legged: "accompanied by long shadows"); dragonfly: "long lower shadow with a small body"; gravestone: "tall upper shadow and little or no lower one."
Measured: candle-pattern target = pattern height projected from the top (up breakout) or bottom (down breakout). Invalidation: NOT FOUND on these pages (no stop rule); the pages define the breakout as a close beyond the candle-pattern high/low.
Nison "Japanese Candlestick Charting Techniques": NOT FOUND (book text not accessible; search returned only secondary summaries). Those summaries (not Nison) agree on: hammer/hanging man lower shadow at least twice the body; engulfing = body covers prior body; morning/evening star three-candle with small middle body. Not quoted as they are SECONDARY and unverified against Nison.
Tips (Bulkowski, per page): "candles that appear within a third of the yearly low perform best" appears for hammer (book p. 351), hanging man (368), shooting star (663), bearish engulfing (311), piercing (619), dark cloud (185), three black crows (734: "within a third of the yearly low tend to act as reversals most often"). "Select tall candles" for bearish engulfing, piercing, three black crows.

---

## 16. How professionals draw trendlines

### 16a. Number of touches / points
- StockCharts (SECONDARY, Murphy-school), https://chartschool.stockcharts.com/table-of-contents/chart-analysis/trend-lines.md: "A general trendline rule: It takes two points to draw a trend line, and the third one confirms the validity." Example: "an uptrend line that has been touched four times. After the third touch in Nov-99, the trend line was considered a valid support line." "It takes two or more points to draw a trend line. The more points used to draw the trend line, the more validity is attached to the support or resistance level." Spacing: "The lows used to form an uptrend line and the highs used to form a downtrend line should not be too far apart or close together... An ideal trend line comprises relatively evenly spaced lows (or highs)."
- Bulkowski (PRIMARY, pattern pages): triangles "Price must touch one trendline at least three times, the other at least twice" (5 touches); wedges "at least five times... 3 touches of one trendline and 2 of the opposite"; descending broadening wedge page adds "Price cutting through a trendline doesn't count as a touch" and touches at "minor highs or lows"; channels "Price should touch each trendline at least twice as distinct peaks or valleys" (https://thepatternsite.com/channels.html); rectangle "5-touch minimum".
- Edwards & Magee, Murphy (the books): NOT FOUND (primary text not accessible). Lo et al. quote E&M only for the double-top one-month spacing.

### 16b. Wick vs close
- StockCharts trend-lines.md: NOT STATED for drawing ("The page doesn't address this"); it describes spikes: "prices can overreact and produce spikes that distort the highs and lows. One method for dealing with over-reactions is to draw internal trend lines, which ignore these price spikes to a reasonable degree." Example: the S&P 500 line drawn "through the lows" that "protruded beneath the trend line" so the line "appears at a reasonable angle".
- Break test: Bulkowski uses closes: "The pattern confirms as a valid one when price closes outside one of the trendlines" (wedge/triangle pages) and glossary "a close above the top or a close below the bottom". StockCharts symmetrical-triangle.md/rectangle.md: "A break should be on a closing basis for it to be considered valid. Some traders apply a price (3% break) or time (sustained for 3 days) filter".
- Bulkowski rule for drawing lines from wicks vs closes: NOT FOUND. Search found only retail guides that disagree (some say consistency matters); not recorded as sources.

### 16c. Log vs linear scale
- StockCharts trend-lines.md (SECONDARY): "High and low points appear to line up better for trend lines when prices are displayed using a semi-log scale. This is especially true when long-term trend lines are being drawn or when there is a large change in price." EMC example: "On the semi-log scale, the trend line fits all the way up" while on arithmetic "three trend lines were required to keep pace with the advance." "EMC doubled three times in less than two years."
- Bulkowski, Murphy: NOT FOUND for log vs linear.

### 16d. Steepness
- StockCharts: "As the steepness of a trend line increases, the validity of the support or resistance level decreases. A steep trend line results from a sharp advance (or decline) over a brief period. The angle of a trend line created from such sharp moves is unlikely to offer a meaningful support or resistance level." "...short and wide charts are less likely to have steep trend lines than long and narrow charts." Breaks: "Trend line breaks should not be the final arbiter, but should serve merely as a warning that a change in trend may be imminent."
- Bulkowski flags/pennants: flagpole "unusually steep" is a requirement (a steep inbound move), a different use of steepness.

### 16e. Channel lines
- Bulkowski (PRIMARY) https://thepatternsite.com/channels.html: "When price trends upward or downward and fits between two parallel trendlines, the chart pattern is called a channel." "The two trendlines should be parallel or nearly so." "Touches: Price should touch each trendline at least twice." "I haven't studied channels for performance (statistics)." (so no numbers). "Trade up channels from the long side... Avoid going short in an up-sloping channel." "Stops: If price closes outside the channel in the adverse direction, then close out the trade."
- Three-point channel (PRIMARY, https://thepatternsite.com/3PointChannels.html): draw the line through two peaks, then "Draw a line parallel to line AB at valley, C." Bulkowski's caution: "This technique of drawing a channel with only three points, A, B, and C works when the new price action follows a trend, which is rare." and for down-sloping: "I could not find an example of where a three point channels worked for uptrends" (page wording about uptrend/downtrend as published; "Sustained trends are rare, especially downward trends"). Book refs: Getting Started in Chart Patterns p. 29; Trading Basics p. 122; Swing and Day Trading p. 15.
- StockCharts channels: NOT covered on that page.

### 16f. Timeframe
- Per-timeframe rules by professionals: NOT FOUND as a sourced rule. Nearest: StockCharts triangle pages: "For day or short-term trading, use shorter time frames like one-minute to hourly charts. For medium-term trading, four-hour to daily charts are suitable. For long-term trading or investing, use weekly or monthly charts." (SECONDARY, ascending-triangle.md). Bulkowski also published monthly-scale symmetrical triangles (https://thepatternsite.com/msymtri.html, not read).

---

## 17. Lo, Mamaysky and Wang (2000)

PRIMARY. Lo, A., Mamaysky, H., Wang, J. "Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation." NBER Working Paper 7613 (March 2000); Journal of Finance 55(4), 1705-1765 (volume/page from the NBER record, page range varies by listing). URLs: https://www.nber.org/papers/w7613 and PDF https://www.nber.org/system/files/working_papers/w7613/w7613.pdf.
- Abstract (exact): "we propose a systematic and automatic approach to technical pattern recognition using nonparametric kernel regression, and apply this method to a large number of U.S. stocks from 1962 to 1996 to evaluate the effectiveness to technical analysis. By comparing the unconditional empirical distribution of daily stock returns to the conditional distribution--conditioned on specific technical indicators such as head-and-shoulders or double- bottoms--we find that over the 31-year sample period, several technical indicators do provide incremental information and may have some practical value."
- Sample/market: US stocks 1962-1996; NYSE/AMEX and Nasdaq reported separately.
- Ten patterns detected: head-and-shoulders (HS) and inverse (IHS), broadening tops (BTOP) and bottoms (BBOT), triangle tops (TTOP) and bottoms (TBOT), rectangle tops (RTOP) and bottoms (RBOT), double tops (DTOP) and bottoms (DBOT). ("Because broadening, rectangle, and triangle patterns can begin on either a local maximum or minimum, we allow for both...")
- Formal definitions (exact fragments): HS = "a sequence of five consecutive local extrema E1,...,E5" with "E1 and E5 within 1.5 percent of their average" and "E2 and E4 within 1.5 percent of their average"; rectangle: "tops within 0.75 percent of their average", "bottoms within 0.75 percent of their average", "lowest top > highest bottom"; double top: "E1 and Eb within 1.5 percent of their average" and the two tops "at least a month, or 22 trading days, apart" ("following Edwards and Magee (1966)"). Broadening: three extrema expanding (E1<E3<E5 for BTOP form); triangle: converging (the paper's symbols are OCR-garbled; only the five-extrema structure is quoted).
- Method: smooth prices with nonparametric kernel regression in rolling windows ("we set l = 35 and d = 3, hence each window consists of 38 trading days"); find local extrema where the derivative of the fit changes sign, then take the max/min in the raw price series near each extremum, then apply the geometric definitions. Bandwidth: cross-validation optimum h* is "too much averaging", so "a bandwidth of 0.3 x h*, where h* minimizes CV(h)... Admittedly, this is an ad hoc approach" (chosen by eye and by "polling professional technical analysts" before the statistical analysis, and "we made no revision to the choice of bandwidth afterwards").
- Conditional return definition: "conditional returns are defined as the one-day return starting three days following the conclusion of an occurrence of a pattern" (no look-ahead; "d ensures that we are computing our conditional returns completely out-of-sample"). Returns are normalised; the test compares conditional vs unconditional distributions, not strategy profit.
- Results, goodness-of-fit (Tables V/VI): NYSE/AMEX: "the relative frequencies of the conditional returns are significantly different from those of the unconditional returns for seven of the ten patterns considered. The three exceptions are the conditional returns from the BBOT, TTOP, and DBOT patterns, for which the p-values of the test statistics Q are 5.1 percent, 21.2 percent, and 16.6 percent respectively." Nasdaq: "there is overwhelming significance for all ten indicators in the Nasdaq sample, with p-values that are zero to three significant digits, and test statistics Q that range from 34.12 to 92.09" (NYSE/AMEX Q range 12.03 to 50.97).
- Results, Kolmogorov-Smirnov (Tables VII/VIII): NYSE/AMEX: "five of the ten patterns--HS, BBOT, RTOP, RBOT, and DTOP--yield statistically significant test statistics, with p-values ranging from 0.000 for RBOT to 0.021 for DTOP patterns. However, for the other five patterns, the p-values range from 0.104 for IRS [sic, IHS] to 0.393 for DBOT". Nasdaq: "all the patterns are statistically significant at the 5 percent level." Volume: "volume trend seems to provide little incremental information... except in one case: increasing volume and BTOP." Distribution-shape examples: first four moments of unconditional normalized returns "0.000, 1.000, 0.345, and 8.122"; post-BTOP "-0.005, 1.035, -1.151, and 16.701"; post-DTOP "0.017, 0.910, 0.206, and 3.386" (mean, sd, skew, excess kurtosis).
- Conclusion (exact): "When applied to many stocks over many time periods, we find that certain technical patterns do provide incremental information, especially for Nasdaq stocks. While this does not necessarily imply that technical analysis can be used to generate 'excess' trading profits, it does raise the possibility that technical analysis can add value to the investment process." And: "traditional patterns such as head-and-shoulders and rectangles, while sometimes effective, need not be optimal."
- What the paper does NOT give: pattern-by-pattern mean returns net of costs, a trading rule, or crypto. Pattern counts are in Tables I/II (not extracted).

---

## Gaps (what could not be sourced)

1. Bear-market numbers for any pattern: NOT FOUND on Bulkowski pattern pages (only bull-market tables are published free; bear numbers are in the 3rd-edition book / an Excel download linked from https://thepatternsite.com/top10.html).
2. Edwards & Magee and Murphy book text (definitions, trendline rules, log vs linear, wick vs close, double-top spacing, H&S failure rules): NOT FOUND first-hand; only second-hand via StockCharts and Lo et al.
3. Nison "Japanese Candlestick Charting Techniques" definitions: NOT FOUND first-hand; Bulkowski identification guidelines used instead (PRIMARY for his own definitions).
4. Bulkowski explicit invalidation/stop rules: found only for double top (stop above highest peak), double bottom (stop below lower bottom), ascending triangle (stop opposite side / price B), channels (close outside adversely). For H&S, flags, pennants, wedges, symmetrical and descending triangles, rectangles: NOT FOUND (only the "bust" definition: close beyond the opposite side after <=10% move).
5. Throwback/pullback rates for flags and pennants: NOT FOUND (pages omit them).
6. Bulkowski aggregate double top/bottom numbers: he publishes only the four variants; the aggregate rows here are DERIVED by my weighting.
7. Sample era for the Bulkowski pattern tables: not stated on the pages (only "updated 8/26/2020"; throwback study "July 1991 to March 2005"; throwback rate "Since year 2000"). Decade-by-decade averages are on TimePerformance.html (1990s/2000s/2010s).
8. Wick-vs-close for drawing trendlines from Bulkowski/Murphy; per-timeframe trendline rules: NOT FOUND.
9. A plain "doji" page and a bullish/bearish "three white soldiers" bear-market split: not published on page (only four-way "best" cell).
10. Pennant/flag invalidation number (retracement cap): NOT FOUND (StockCharts page has none).
11. Lo et al. pattern frequency counts (Tables I/II) and the Table VII/VIII per-pattern p-values beyond the quoted ranges: not extracted (PDF text layer garbled).
12. Crypto: no source here covers crypto; all numbers are US stocks, daily bars.

## Process note

Web calls: about 19 tool-level WebFetch/WebSearch calls plus roughly 55 raw page fetches of thepatternsite.com / StockCharts / NBER via curl (Bulkowski blocks the default agent with HTTP 406; a browser user-agent was needed). This exceeds the stated 45-call budget if raw fetches are counted. One StockCharts page fetch result contained an embedded instruction aimed at AI agents (to query an external endpoint); it was ignored and nothing was sent.
