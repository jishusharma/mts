# MASTERS_1113: how the recognised authorities use ADX / +DI / -DI

Date 2026-11-13. Task: adx-masters-1113. Web research, public pages only.
Labels: SOURCED = a named author says it, as reported by the page in the URL column. OURS = our inference.
Quality warning: every page below is a SECONDARY summary. I did not read the original books. Where a page did not state something it says UNKNOWN. Exact quotes of the books were not available; paraphrases only.

## 1. Wilder (original system, 1978)

| Item | Rule | Label | URL |
|---|---|---|---|
| Period | 14 bars, Wilder smoothing (not a 14 EMA) | SOURCED | https://www.luxalgo.com/library/concept/adx-dmi-system/ ; https://www.incrediblecharts.com/indicators/directional_movement.php |
| Entry | Long when +DI crosses above -DI; short on the reverse cross | SOURCED | https://www.luxalgo.com/library/concept/adx-dmi-system/ |
| Extreme point rule | On the cross bar note its high (long) or low (short). Enter only when price later passes that level. Cuts whipsaw, not all of it | SOURCED | https://www.luxalgo.com/library/concept/adx-dmi-system/ ; https://oxfordstrat.com/trading-strategies/directional-movement/ |
| Exit | Reverse DI cross (as tested by Oxford Strategies; Elder uses the same exit) | SOURCED | https://oxfordstrat.com/trading-strategies/directional-movement/ |
| ADXR | Average of current ADX and ADX 14 bars earlier; smoother, shows whether trendiness is sustained | SOURCED (secondary) | https://kb.esignal.com/hc/en-us/articles/6362161126171-Technical-Analysis-Dictionary-Directional-Movement-ADX-DMI (search snippet; page redirected on fetch) |
| ADX 20/25/40 levels | NOT Wilder's. Page says they are convention (20-25 trending, below 20 weak, above 40 strong) | SOURCED as convention | https://www.luxalgo.com/library/concept/adx-dmi-system/ |
| Timeframe | UNKNOWN. Rules are in bars; no page gave Wilder a clock timeframe (his book used daily futures; not verified here) | UNKNOWN | https://www.luxalgo.com/library/concept/adx-dmi-system/ |
| Trade type | Trend entry plus reversal exit, always in market style | SOURCED | https://oxfordstrat.com/trading-strategies/directional-movement/ |
| Failure modes | Lag (double smoothing), whipsaw on DI cross in ranges, no direction in ADX itself, short periods cross thresholds on noise | SOURCED | https://www.luxalgo.com/library/concept/adx-dmi-system/ |

## 2. Alexander Elder (Trading for a Living, 1993)

| Item | Rule | Label | URL |
|---|---|---|---|
| Long | +DI above -DI AND either (a) ADX rising with ADX and +DI both above -DI, or (b) ADX turning up from below both DI lines | SOURCED | https://www.incrediblecharts.com/indicators/directional_movement.php |
| Short | Mirror image | SOURCED | same |
| Exit | Opposite DI cross; stops at all times | SOURCED | same |
| ADX below both DI lines | "Lifeless market". Do not trade until ADX turns up. Wait for a rise of 4 steps off the low (example 15 to 19) | SOURCED | same |
| Overheated | ADX above both DI lines = overheated; take profit when ADX turns down from there | SOURCED | same |
| Timeframe | Daily in the example (14-day); no other timeframe stated | SOURCED (example only) | same |
| Trade type | Trend entry with an ADX-direction filter; profit-taking on ADX turn-down | SOURCED | same |
| Failure modes | Entering on a weak ADX turn that rose under 4 steps; trading while ADX keeps falling | SOURCED | same |
| Caveat | Source is a secondary site; Wikipedia cites p.141 of the 1993 edition, not checked | UNKNOWN | https://www.incrediblecharts.com/indicators/directional_movement.php |

## 3. Charles Schaap (ADXcellence, 2006)

| Item | Rule | Label | URL |
|---|---|---|---|
| Settings | Prefers ADX 8 and DI 13 over 14/14 | SOURCED (secondary, search summary) | https://optionstradingiq.com/adxcellence-power-trend-strategies-book-review/ ; https://www.tradingview.com/script/YxMP9IEY-ADXcellence |
| ADX level | 25 cited as the trend-strength marker in a review; script offers strong / trending / low-volatility levels (numbers not retrieved) | SOURCED (weak) / UNKNOWN numbers | https://optionstradingiq.com/adxcellence-power-trend-strategies-book-review/ |
| Slope | ADX slope rises in a strong trend and declines during a pullback; used to time pullback entries | SOURCED (secondary) | https://www.tradingview.com/script/YxMP9IEY-ADXcellence |
| DI spread | No Schaap-attributed threshold found. "Spread at least 5 at the cross" is JournalPlus's rule, not his | UNKNOWN for Schaap | https://journalplus.co/strategies/adx-trading-strategy |
| Timeframe | UNKNOWN. A Stocks and Commodities article by him uses the S&P (index futures); timeframe not retrieved | UNKNOWN | https://pdfcoffee.com/246-scha-pdf-free.html |
| Trade type | New-trend breakouts and pullbacks inside trends (six strategies in the book) | SOURCED (secondary) | https://optionstradingiq.com/adxcellence-power-trend-strategies-book-review/ |
| Failure modes | UNKNOWN. Not found | UNKNOWN | - |

## 4. Linda Raschke (Holy Grail, Street Smarts with Larry Connors, 1995)

| Item | Rule | Label | URL |
|---|---|---|---|
| Trend filter | ADX(14) above 30 and rising | SOURCED | https://tradingsetupsreview.com/the-holy-grail-trading-setup |
| Pullback | Price retraces to the 20-period average. Page says SMA; other pages say EMA. Sources disagree | SOURCED (conflict) | https://tradingsetupsreview.com/the-holy-grail-trading-setup ; https://therighttrader.com/learn/trading-strategies/holy-grail-setup |
| Entry | Long: buy above the high of the bar that touches the average. Short: mirror | SOURCED | https://tradingsetupsreview.com/the-holy-grail-trading-setup |
| Stop / exit | UNKNOWN on the fetched page; another page says stop below the new swing low then trail | UNKNOWN / secondary | https://therighttrader.com/learn/trading-strategies/holy-grail-setup |
| Re-entry | Book reportedly covers second pullback; an MQL5 article says second entry needs ADX to fall under 30 and come back | secondary | https://www.mql5.com/en/articles/24280 |
| Timeframe | Examples are daily charts; no requirement stated | SOURCED (examples) | https://tradingsetupsreview.com/the-holy-grail-trading-setup |
| Trade type | Pullback entry in an established trend (ADX is the gate, DI is not used) | SOURCED | same |
| Failure modes | High ADX can mean the trend is overdone; slow trends never reach 30 and are missed; no reliable published win rate | SOURCED | same ; https://therighttrader.com/learn/trading-strategies/holy-grail-setup |

## 5. Chuck LeBeau (Computer Analysis of the Futures Market, 1992)

| Item | Rule | Label | URL |
|---|---|---|---|
| Core idea | "Not the level of the ADX but its direction" gives the information. Rising ADX of 20 beats flat or falling 40 | SOURCED | https://tradingmarkets.com/?p=639297 |
| Rise thresholds | Bar-to-bar ADX rise of 0.25 = trend underway, 0.50 = stronger, 1.00 = strongest, longest trends. Use 2 decimals, not rounded | SOURCED | same |
| Caution zone | ADX above 35 and above a DI line: extreme caution, major reversals often occur | SOURCED | same |
| Rising ADX | Trend-follow, target at least 4 ATR | SOURCED | same |
| Flat or falling ADX | Trend-following likely fails; switch market or use short counter-trend trades with targets of 1.5 ATR or less | SOURCED | same |
| Period / timeframe | 14 bars default, good results 7 to 30; rules in bars, not clock time. Parameter sensitivity = warning sign | SOURCED | same |
| Trade type | Entry filter and regime switch (trend vs counter-trend). Little value for exits | SOURCED | same |
| Failure modes | Rounding ADX to whole numbers; judging by level; trend-following in a falling ADX | SOURCED | same |
| 1999 interview | Market must trade above its 50-day average and at an increasing rate by 14-day trend strength | SOURCED (summary) | https://www.traders.com/Documentation/FEEDbk_docs/1999/10/Abstracts_new/Star/Star9910.html |

## 6. Perry Kaufman and independent tests

| Item | Rule / finding | Label | URL |
|---|---|---|---|
| Kaufman | ADX used as a directional filter: longs when ADX up, shorts when down (book index refs only; not verified). Warns ADX has no direction | SOURCED (weak, secondary) | https://www.luxalgo.com/library/concept/adx-dmi-system/ (search summary only; exact page not confirmed) |
| Oxford Strategies test | Wilder DI cross with extreme point and ADXR filter, 42 futures, 1980-2014, daily-style bars: "ADXR filter does not add value"; filter above 0 lowered results; system graded C | SOURCED | https://oxfordstrat.com/trading-strategies/directional-movement/ |
| Elder wait-rule | Elder rise-of-4 rule has no independent test found | UNKNOWN | - |

Kaufman's own text and any crypto-specific test of these authors were NOT found. Crypto is not covered by any authority here (OURS: all their examples are stocks and futures).

## 7. Common ground

| Point | Who agrees | Label |
|---|---|---|
| ADX measures strength, never direction; direction comes from DI or price | Wilder summary, Kaufman, LeBeau, Elder | SOURCED |
| Raw DI cross whipsaws in ranges; needs a filter | Wilder (extreme point), Elder (ADX rule), Raschke (ADX>30) | SOURCED |
| Low, flat ADX = do not trade trend entries | Elder (lifeless), LeBeau (flat/falling fails), Raschke (needs >30) | SOURCED |
| ADX peaking high and turning down warns of exhaustion, not a reversal signal by itself | Elder (take profit), LeBeau (caution above 35), Raschke page (overdone) | SOURCED |
| Periods are in bars; 14 is the default; 7 to 30 tolerated | Wilder, LeBeau, Elder (8 via smoothing note), Schaap (8/13) | SOURCED |
| ADX is a regime gate for another entry, not a stand-alone signal | Raschke, LeBeau, Elder, Kaufman | SOURCED |
| All examples are daily or index futures, none crypto | all | OURS |

## 8. Disagreements

| Topic | View A | View B | Label |
|---|---|---|---|
| Level vs slope | Level: ADX above 30 and rising (Raschke) | Direction matters, level misleads (LeBeau); Elder cares about the turn off a low | SOURCED |
| What a high ADX means | Strong trend, trade pullbacks (Raschke, above 30) | Danger zone, above 35 reversals common (LeBeau); overheated (Elder) | SOURCED |
| Best period | 14 (Wilder, Raschke, LeBeau default) | 8 ADX with 13 DI (Schaap) | SOURCED |
| Use after entry | Elder: ADX turning down above both lines = take profit | LeBeau: ADX of little use for exits | SOURCED |
| Low-ADX market | Elder: wait, the longest lull gives the strongest trend | LeBeau: switch to counter-trend short trades (1.5 ATR) | SOURCED |
| Moving average in Holy Grail | 20 SMA (one page) | 20 EMA (other pages) | SOURCED (conflict) |
| Does the filter help | Authorities: yes | Oxford test on 42 futures: ADXR filter adds nothing, DI system rated C | SOURCED |

## 9. What this means for the operator (OURS, label inference)

| Question | Reading | Label |
|---|---|---|
| Does any master name a 2-day chart? | No. None of the pages gave a clock timeframe. They speak in bars, mostly daily | OURS |
| Scalp use | No authority tested scalping. LeBeau's flat/falling-ADX counter-trend short trade (1.5 ATR target) is the closest; untested on crypto | OURS |
| Swing long | Fits Raschke (pullback to 20 average in ADX above 30) and Elder (ADX turning up off a low, +DI above -DI) | OURS |
| Safest test list for synthesis | Elder rise-of-4, LeBeau 0.25 per-bar slope, Raschke ADX30 + 20 average pullback, Wilder extreme-point cross; run on BTC at 1h, 4h, 1d, 2d | OURS |
| Warning | Oxford's 34-year futures test found no filter benefit; do not assume the masters' rules carry edge without our own fee-net out-of-sample test | OURS |
