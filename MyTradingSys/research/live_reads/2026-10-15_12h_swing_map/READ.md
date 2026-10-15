# 2026-10-15 BTCUSDT 12h swing map (operator read request, two CoinGlass 12h shots; 1m and 3m intraday zoom added below)
<!-- Process: methodology/screenshot_intake.md. Claim rows `| id | MATCH or MISMATCH or NOT_IN_DATA | claim | evidence |`. No trade advice; testnet only; no trades opened. -->

Shots: ef38b9b34fb6, e43e32a11712 (12h); 17bb712d5ead (1m), d2d2f30fa142 (3m) (intraday zoom section)
Operator words: ef38b9b34fb6 "Operator-annotated 12h BTCUSDT BB(20,2): ABCD arrows Sep 16-21, circles at upper-band/mid-band rejections and the Oct 8 lower-band wick; price now on the lower band (80571). Asks for a read of the 12h structure." / e43e32a11712 "Same 12h chart zoomed out with OI, CVD, Net Delta, RSI, StochRSI, volume; blue verticals at each swing high/low, RSI bearish divergence line Oct 2-5, RSI circles at Sep 18 and Oct 14-15 (RSI 36.9). Asks whether the flows confirm the swing map."
Clocks: both shots are the CoinGlass TradingView page = UTC. 12h bars open 00:00 and 12:00 UTC. Capture instants from the bar countdown: ef38 13:06:43Z (countdown 10:53:17 to the 00:00 close), e43e 13:10:57Z (10:49:03). `shot.py` times 13:06 and 13:11 agree.
Pre-read (VVP-002 F.1): pass for both (timeframe label, OHLC header, BB legend, right-edge cursor, price axis visible). ef38 has price + BB only; e43e adds OI, CVD, Net Delta, RSI 14 (+SMA 14), StochRSI 14 14 3 3, Volume SMA 9.
Set timeframes present: 12h (two zoom levels of the same chart)   missing: every other timeframe (1h, 4h, 1D, 1W). One timeframe only: this is context for the 12h structure, not a multi-timeframe read. A same-day multi-timeframe read exists on branch `claude/compassionate-herschel-52c7ce` (not on origin/fast-track when this was written, so not linked).
Data used: Binance USDT-M perp (the chart is Binance BTCUSDT). 1m klines 2026-10-01 .. 13:13Z fetched free from fapi into a scratch dir (closed bars only), 12h/1h klines from 2026-08-25, `openInterestHist` 1h, archive `metrics` (5m OI) for Sep 2026, live `/fapi/v1/openInterest`. Engine snapshots: `MyTradingSys/research/screenshots/engine/ef38b9b34fb6.json` and `.../e43e32a11712.json` (rebuilt at the shot minute). Taker delta = 2 x taker_buy_volume - volume per bar (Binance only; CoinGlass aggregates, see R-12).

## Carried context
Prior: none
(No committed earlier extract of this 12h chart; see the set note above.)

## Bottom line (3 lines)
1. The operator's swing map is accurate to the data: every blue vertical is a real swing bar (Sep 21 12:00, Sep 23 00:00, Oct 2 12:00, Oct 5 00:00, Oct 8 12:00, Oct 12 00:00, Oct 14 00:00, Oct 15 12:00 now), and the numbers on the chart (OHLC, BB, RSI, StochRSI, CVD step, OI) reproduce from Binance data within the unfinished-bar error.
2. Flows did not confirm every high: Sep 21 (rocket, delta +11.6K, OI at the peak) was a confirmed push; the three lower or equal highs after it (Sep 23, Oct 5; Oct 2 only on the reversal) came with negative or fading delta and falling OI. The Oct 8 low was a flush (OI -3.4K BTC, volume 147K, delta -5.2K, next bar +4.1K). Oct 15 retests that low at a lower level without the flush: delta -5.7K, OI about -1K, RSI below the 40 line it held on Sep 17 and Oct 12.
3. Price (80,456 at 13:10Z) is 0.13% above the lower band (80,350), %b 0.02, RSI 36.9; no catalogued setup is triggered, the engine reports `setup_candidates: []`. Only partial fits are listed below, each labelled SOURCED (a rule from a trader's words) or OURS (our mapping).

## What the operator marked (price read off the axis, +-180 points = +-3 px error)
| Mark | Where (UTC) | Read vs data | Class |
|---|---|---|---|
| Arrow A (start of ABCD, rising) | starts Sep 16 00:00 bar, y=843, about 75.3K; the lowest low of the zone is Sep 15 12:00 L 74,909 | consistent (A zone 74.9K-75.3K) | MATCH |
| Letters A B C D | ef38 shows A (x=251), C (x=350), D (x=426); e43e adds B (x=320). The same x in both shots although the zoom differs, so the letters are screen-anchored, not bound to a swing. They sit beside four arrows: A = first small rise (Sep 16 00:00 to Sep 17 12:00), B = steeper second rise (to the Sep 18 12:00 high), C = the sideways arrow from that high to the Sep 20 00:00 red bar, D = the long rise to the Sep 21 12:00 high. So the letters most likely name the four LEGS, not the points | leg reading is OURS (the operator did not say); the point-based AB/CD arithmetic below is a second, different decomposition | NOT_IN_DATA (intent) |
| Arrow tip near the Sep 18 12:00 high (end of leg B, start of leg C) | y=510, about 81.36K; data H 81,386 (Sep 18 12:00) | MATCH for the price; the letter C is printed beside this tip, which fits the leg reading above | MATCH |
| End of leg C / start of leg D at the Sep 20 00:00 red bar | wick to about 80.1K; data L 80,096 (Sep 20 00:00) | MATCH | MATCH |
| Arrow tip D | Sep 21 12:00, y=183, about 87.3K; data H 87,385 | MATCH | MATCH |
| Circles at the Sep 21 12:00 high and Sep 23 00:00 high | 87,385 and 87,247 (-0.16%) | MATCH | MATCH |
| Circles at the Oct 2 12:00 high, its lower wick, and the Oct 5 00:00 high | 87,250; L 83,842 (mid band 84,285); 86,976 | MATCH | MATCH |
| Circles at Oct 12 00:00 and Oct 14 00:00 highs (mid band) | H 84,340 vs mid 84,105; H 84,118 vs mid 83,735 | MATCH, both highs poke above the mid band and close below it | MATCH |
| Circle at the Oct 8 12:00 wick | L 80,345, lower band that bar 81,979; the bar also CLOSED below the band (81,711) | MATCH | MATCH |
| ABCD as a pattern (point decomposition) | low 74,909 (or 75.3K), high 81,386, low 80,096, high 87,385: first rise 6,477, pullback 1,290 (20% retrace), last rise 7,289 (1.13 x the first) | the two rises are near equal, the pullback is shallow; OURS measurement, not a sourced ABCD rule | OURS |
| RSI lines: green at 60, red at 40 | the same levels as Malkan's 60/40 (MAL-1, MAL-2) | SOURCED level choice (secondary video, machine translation), applied on 12h which is OURS | SOURCED / OURS |
| RSI circles | circle 1 at x=718 = Sep 17 12:00 (RSI 42.1, on the 40 line, then 65.6 a day later); circle 2 at x=808 = **Sep 20 00:00** (RSI 61.3, on the 60 line, then 74.5 at Sep 21 00:00), not Sep 18 as the operator wrote; circle 3 at x=1675 = Oct 14 12:00 (RSI 41.5) | the 60-line and 40-line touches are real; date of circle 2 differs from the operator's note by 2 days (pixel-mapped, +-1 bar) | MATCH (dates +-1 bar). The operator's "Sep 18 and Oct 14-15" does not say which of the three circles is meant for Sep 18 (circle 1 Sep 17 12:00 is nearer by date); the "Oct 15" part: RSI 38.8 at the Oct 15 00:00 close and 36.9 now, both below the 40 line, no circle on those bars |
| Red RSI divergence line Oct 2-5 | from Oct 2 00:00 (RSI 66.0, price high 86,888) to Oct 4 12:00 / Oct 5 00:00 (RSI 63.3 / 61.3; Oct 5 00:00 high 86,976 = +0.10% above 86,888) | divergence exists only with those two pivots and by 88 points; against the real swing high (Oct 2 12:00, H 87,250, RSI 54.9) the Oct 5 high is a lower high in price (86,976) with a HIGHER RSI (61.3), so there is no bearish divergence with that pivot | OURS (pivot choice decides) |

## Flows at each blue vertical (Binance data; bar = 12h bar named by its open)
Delta = taker buy minus sell volume of that bar in BTC; OI in BTC (sumOpenInterest) at the bar's open and the next bar's open; RSI at bar close.
| Vertical | Price (H or L, close) | Bar delta (previous bar) | OI open -> next open | RSI | Reading |
|---|---|---|---|---|---|
| Sep 21 12:00 SH | H 87,385, close 86,579 | +2,340 (+11,622) | 110,348 -> 109,012 (OI at the Sep 21 00:00 open 108,044, so +2.3K into the high) | 77.7 (window max) | CONFIRMED: price, delta and OI all rose into the high; 6 of 8 closes Sep 18 12:00-Sep 22 00:00 were outside the upper band (a band walk) |
| Sep 23 00:00 SH | H 87,247 (-0.16% vs Sep 21), close 85,623 | -1,870 (-5,732, -5,952) | 106,710 -> 106,252 (109,012 at the Sep 22 00:00 open) | 71.2 | DIVERGED: equal high, delta negative for 3 bars (-13,554 total), OI -2.3K over those 3 bars, RSI lower high. The next bar (Sep 23 12:00) shed 7.7K OI (106.25K -> 98.5K) with delta -4,391 |
| Oct 2 12:00 SH | H 87,250 (-0.15% vs Sep 21), close 84,483 | -3,831 (+5,861) | 99,214 -> 98,184 | 54.9 (66.0 on the push bar) | CONFIRMED rejection: the push bar had +5.9K delta and OI +2.3K, the high bar reversed with -3.8K delta, volume 137.7K. Third high within 0.16% (87,385 / 87,247 / 87,250) |
| Oct 5 00:00 SH | H 86,976 (-0.31% vs 87,250), close 86,165 | -425 (+1,038) | 98,941 (Oct 4 12:00) -> 97,452 -> 96,926 | 61.3 | DIVERGED: lower high, near-zero delta, OI falling; the next bar -2,709 delta and OI -2.5K |
| Oct 8 12:00 SL | L 80,345, close 81,711 (below the band 81,979) | -5,208 (-3,749) | 96,353 -> 93,004 (-3.35K) | 38.1 | CONFIRMED flush: OI collapse, volume 146.7K (largest 12h volume since Sep 21 00:00, 150.8K), close 1.7% off the low, next bar delta +4,133 and close 83,200 |
| Oct 12 00:00 SH | H 84,340, close 83,359 | -495 (+3,948) | 92,378 -> 94,921 (+2.5K) | 48.2 | OI rose into a rejection at the mid band (shorts added), next bar delta -5,813 |
| Oct 14 00:00 SH | H 84,118, close 83,424 | +373 (-2,246) | 92,500 -> 90,948 (-1.6K) | 49.7 | rejection at the mid band 83,735 with little delta; next bar (Oct 14 12:00) delta -2,750, OI +2.2K, price -2.1%: new shorts; then Oct 15 00:00 delta -5,718 (heaviest since Oct 8), OI about -1K to 10:55Z |
| Oct 15 12:00 (now, forming bar: provisional swing) | L 80,342 (13:12Z, after both shots), 13:10 close 80,456 | -811 after 70 min (-5,718) | live OI 92,460 (10:55Z 92,083; the 93,117 at 00:00) | 36.9 | see "Where price sits" and R-10 about the OI history glitch |

Same-low comparison (OURS): Oct 8 12:00 (L 80,345, OI -3.4K, delta -5.2K, volume 147K, RSI 38.1) versus Oct 15 00:00 (L 80,188 = 157 points or 0.2% lower, OI about -1.0K to 10:55Z, delta -5.7K, volume 95K, RSI 38.8 at the close): similar sell delta, less OI shed and less volume, a slightly lower low. By closes, RSI 38.8 versus 38.1 at a lower close is a 0.7-point "bullish" difference that vanishes in the forming bar (RSI 36.9 < 38.1), so there is no bullish divergence now.

## Where price sits now (13:10Z)
- Close 80,455.6; BB(20,2) on 12h closes incl. the forming bar: lower 80,350.1, mid 82,968.6, upper 85,587.1, width 6.3% of the mid, %b 0.02. Price had not touched the lower band at either shot (bar low 80,477 then 80,413 versus band 80,377 then 80,347); the first print through it was 80,341.9 at 13:12Z.
- Last three 12h closes sit at %b 0.16, 0.06, 0.02 and the lower band is falling (80,889 -> 80,350 in a day and a half). The mid band has fallen from 84,773 (Oct 6 12:00) to 82,969. Only one 12h close has been outside the lower band in this window (Oct 8 12:00); ten closed outside the upper band since Sep 3 (six of them in the Sep 18-22 walk).
- RSI 36.9 (SMA14 45.1); StochRSI K 10.9, D 40.6. Engine (e43e snapshot): price below daily VAL 80,533 and daily POC 80,863, bar-session VWAP 81,091 falling, `cvd_slope falling`, OI trend flat, weekly swing low 80,344.8 (the Oct 8 low), `setup_candidates` and `module_candidates` empty.
- Higher timeframes (computed, not on either chart): 1D RSI 43.1, 1W RSI 55.2 (prior week 59.5), 1M RSI 51.7.

## Claim rows (chart numbers versus our data)
| id | class | claim | evidence |
|---|---|---|---|
| R-01 | MATCH | ef38 header O 80,942.8 H 81,146.6 L 80,477.0 C 80,571.5 at 13:06Z | 1m archive scratch: O 80,942.8, H 81,146.6, L 80,477.0 exact over 66 bars; close 80,563.7 at 13:05 (chart price is the 13:06 tick) |
| R-02 | MATCH | ef38 BB 82,974.3 / 85,571.2 / 80,377.3 | recomputed 82,974.0 / 85,572.1 / 80,375.9 at the 13:05 close (engine json ef38b9b34fb6) |
| R-03 | MATCH | e43e BB 82,968.0 / 85,588.7 / 80,347.3, close 80,445.9 | recomputed 82,968.6 / 85,587.1 / 80,350.1 at the 13:10 bar close 80,455.6 (the chart's 80,445.9 is the 13:10:57 tick; every 'now' figure in this file uses the 13:10 bar close) |
| R-04 | MATCH | RSI 14 = 36.93, RSI SMA 14 = 45.12 | Wilder RSI on 12h closes incl. forming bar 36.94; SMA14 of it 45.09 |
| R-05 | MATCH | Stoch RSI 14 14 3 3 = 10.63 / 40.35 | recomputed K 10.86, D 40.58 (unfinished bar) |
| R-06 | MATCH | CVD candle of the forming bar steps from -48,393 to -49,182 (-789) | Binance taker delta since 12:00Z through the 13:10 bar = -811 (2.7% larger in size than the chart's -789; the chart caught the bar a few seconds before 13:11) |
| R-07 | MATCH | OI candle O 91.902K C 92.318K ("Coins") | live `/fapi/v1/openInterest` 92,460 at 13:16Z; hourly OI 91,762 at 10:00, 92,083 at 10:55 |
| R-08 | MATCH | blue verticals sit on swing bars: Sep 21 12:00, Sep 23 00:00, Oct 2 12:00, Oct 5 00:00, Oct 8 12:00, Oct 12 00:00, Oct 14 00:00, Oct 15 12:00 | x positions mapped with the date axis (35.4 px per day in e43e); each is the local extreme bar of the 12h series (table above) |
| R-09 | MATCH | big OI drop and big red net-delta bar after the Sep 21-23 highs | OI 106.25K -> 98.5K over the Sep 23 12:00 bar (archive metrics); delta -4,391 that bar, -13.6K over the three bars before |
| R-10 | MISMATCH | Binance `openInterestHist` shows OI 100,231 at 11:00Z Oct 15, then 97-101K noise to 12:40Z | the chart (CoinGlass) and live `/openInterest` say about 92.3-92.5K; hist stepped +8,470 BTC (+9.2%) in one hour at 11:00Z (5m series too) while price moved less than 0.5%. Not the chart's anchoring: the same hist endpoint matched the archive at Sep 24-26 (overlap within 0.4%). Update 13:45Z: the corruption was transient: the 5m hist has no rows for 12:45-13:15Z, then reads 92,495 at 13:20Z, 93,122 at 13:30Z, in line with CoinGlass and live OI. So hist is unusable for 11:00-13:15Z only, and an OI series built from it over that window is spurious (our `oi_5m_30d.csv` recorder uses that endpoint; the tracked copy stops at Oct 5 so not checked) |
| R-11 | MISMATCH | engine e43e `vwap_anchor_utc` = 2026-10-15T13:30:00Z | the snapshot is as of 13:11Z; an anchor 19 minutes in the future is wrong or mislabelled (the VWAP price 81,091 itself was not used for any claim here) |
| R-12 | MISMATCH | Net Delta candle of the forming bar steps -21,953 -> -22,359 (-406) | Binance delta -811 over the same bar (ratio 0.50); at the Sep 23 12:00 bar the Net Delta step reads about -7K by pixels against Binance -4.4K (ratio about 1.7, +-1K). CoinGlass Net Delta is not the Binance taker delta that the CVD panel reproduces; only the sign agrees. Do not use Net Delta magnitudes against our data. The intraday shots repeat it with a varying ratio, see R-25 |
| R-13 | NOT_IN_DATA | CVD level -49,182 and Net Delta level -22,359 | the CVD panel draws candles from the left edge (about Aug 29), but our Binance cumulative from the left edge is -73.5K (Aug 29 00:00) and from Sep 1 -70.5K; it equals the chart only from the start of the Sep 12 00:00 bar (-49.3K, 0.3% off). The anchor is unexplained, so levels cannot be compared: steps only (intake rule). Net Delta level has no match tested |
| R-14 | NOT_IN_DATA | Volume SMA 9 = 1.024B | unit (aggregated coins or USD) unknown; Binance 12h quote volume SMA9 is about 5.6B USDT, base about 70K BTC, neither equals it |
| R-15 | NOT_IN_DATA | operator letters A B C D, circles, arrows, blue verticals | drawings are stored nowhere (T066 blocked); positions pixel-mapped above, +-1 bar |
| R-16 | MATCH | 17bb header O 80,380.2 H 80,386.0 L 80,355.0 C 80,355.0 (BTCUSDT 1m) | the forming 13:12 bar at capture: open 80,380.1 (header shows 80,380.2, display rounding); H/L/C are partial-bar values that cannot be checked directly, only through the exact BB/RSI reproduction with that close (R-17, R-18); the final bar closed H 80,429.8 L 80,341.9 C 80,417.6, so H/L/C are partial-bar values (countdown 00:36) |
| R-17 | MATCH | 17bb BB 80,554.7 / 80,750.5 / 80,358.9 | recomputed with the forming close 80,355.0: 80,554.7 / 80,750.5 / 80,358.9 exact (engine json 17bb712d5ead) |
| R-18 | MATCH | 17bb RSI 28.49, SMA 35.78, Stoch RSI 6.87 / 13.68 | recomputed 28.49 / 35.78 / 6.87 / 13.68 exact on the same forming close |
| R-19 | MATCH | 17bb CVD steps at the flush: about -0.28K, -0.33K, -0.1K | pixel scale 82.5 px per 1K (+-0.03K): bars 12:30 -0.28K, 12:31 -0.33K; Binance taker delta -279.2, -326.8, -91.1 BTC |
| R-20 | MISMATCH | brief: flush at 12:29, long lower wick near 80,450 | the spike is the 12:30 bar (3,171.7 BTC, 256.2M USDT); 1m low 80,520.3 at 12:31 (80,565.1 on the 12:30 bar); nothing near 80,450 until 13:08 (80,413.6) |
| R-21 | NOT_IN_DATA | 17bb OI 92.0K -> 92.34K between 12:30 and 13:12 | Binance `openInterestHist` is corrupt 11:00-13:15Z (R-10) and there is no 1m OI record for today (`oi_1m.csv` has one row); endpoints only: hist 92,083 (10:55Z), 92,495 (13:20Z), live 94,110 (13:45:42Z) |
| R-22 | MATCH | d2d2 header O 80,431.5 H 80,681.0 L 80,408.9 C 80,608.8 (3m) | the forming 13:39 3m bar: open, high and low exact; the close is the tick at about 13:41:53 (bar close 80,580.1) |
| R-23 | MATCH | d2d2 BB 80,516.0 / 80,889.5 / 80,142.4, RSI 51.33 / SMA 36.59, Stoch RSI 84.73 / 73.62 | recomputed 80,515.9 / 80,889.5 / 80,142.4, 51.33 / 36.59, 84.73 / 73.62 with the forming close 80,608.8 (engine json d2d2f30fa142) |
| R-24 | MATCH | d2d2 CVD red candle at 13:27 | pixel scale 32 px per 1K: about -1.22K (+-0.05K); Binance 3m taker delta 13:27 -1,138 BTC |
| R-25 | MISMATCH | Net Delta red candles of the same bars | 3m 13:27 candle about -550 against Binance -1,138 (ratio 0.48); 1m 12:30 about -79 against -279 (0.28) and 12:31 about -21 against -327 (0.06); pixel scales 19 px per 100 (1m) and 70 px per 500 (3m). All Net Delta values here are pixel reads (approximate). Direction agrees, magnitude does not and the ratio is not constant: same finding as R-12 |
| R-26 | MISMATCH | brief's d2d2 numbers: price 80,299, VWAP 81,051, red level 80,930, wick 80,050, CVD -6.6K -> -7.6K, net delta -0.6K -> -1.17K | the image shows price 80,608.8, CVD -7.083K, Net Delta -1.022K -> -747, VWAP hidden, the red line is the RSI 40 line; the brief's price fits 13:24-13:25 (3m close 80,300.4), the low is 80,027.0 (13:31); our day VWAP (hlc3 from 00:00Z) is 81,036 at 13:35 and 81,021 at 13:41; OI 92.4K -> 93.09K is confirmed by hist (92,495 at 13:20, 93,122 at 13:30) |
| R-27 | NOT_IN_DATA | Volume SMA 9 = 5.312M (1m) and 152.889M (3m) | unit unknown (as R-14): our quote-volume SMA9 is 11.8M (1m) and 92.5M (3m); the ratios to the chart (0.45 and 1.65) differ, so no single unit explains both |
| R-28 | NOT_IN_DATA | VWAP on the 1m/3m shots | hidden on both; our day VWAP (hlc3 from 00:00Z) 81,021 at 13:41; the engine anchor problem is R-11 |

## Which setups apply (labelled)
No setup is triggered. The Tom/Fabio catalog (`research/setup_catalog_2026-10-15/SETUP_CATALOG.md`) is volume-profile, session-based futures logic; its BTC-visible entries are mapped here only where the 12h picture resembles the words. Malkan (`research/malkan_extract_2026-10-15/SETUP_SUMMARY.md`, secondary and machine-translated sources, tier T3) and Bollinger (`research/bollinger_2026-10-14/SOURCES.md`) are outside the Tom/Fabio catalog but match the operator's own drawing, so they are included.
| Setup | What matches | What does not | Label |
|---|---|---|---|
| MAL-16 regular bearish divergence (A to B new high, RSI lower high, red-candle confirm, stop above the high, target the point C between A and B) | Oct 2 00:00 to Oct 5 00:00: RSI 66.0 -> 61.3, high +0.10%, Oct 5 00:00 closed red. Malkan's point C (the low between his A and B: Oct 2 12:00 L 83,842, not the Sep 20 ABCD low) was passed by Oct 7 12:00 (L 82,706). After the fact, not a test or an entry | the price margin is 88 points; the larger Oct 2 12:00 high breaks the pairing | rule SOURCED (MAL-16); pivot choice and the outcome note OURS |
| MAL-2 RSI takes support at 60 / MAL-1 | circle 2 (Sep 20 00:00, RSI 61.3 then 74.5); circle 1 on the 40 line (Sep 17 12:00, RSI 42.1 then 65.6) | his RSI levels are for weekly/monthly (5 star) and daily (40 support); on 12h it is OURS. RSI is now 36.9, below the 40 line | level SOURCED, 12h transfer OURS |
| MAL-17 regular bullish divergence long | price lower low than Oct 8 | RSI 36.9 is below Oct 8's 38.1; no divergence | rule SOURCED, check OURS (not present) |
| MAL-19 seven star / 5 star (monthly RSI > 60, weekly > 60, daily at 40 or below) | daily RSI 43.1 | monthly 51.7 and weekly 55.2 are not above 60 | rule SOURCED (secondary), RSI computed from Binance perp closes OURS; not met |
| Bollinger band walk (a tag is not a signal; walks end when price returns to the middle) | Sep 18-22 upper-band walk with 6 outside closes ended on Sep 22 12:00 with the D top inside it; since Oct 14 12:00 three closes at %b <= 0.16; mid band rejected price on Oct 12 and Oct 14 (the mirror of "the 20-day average acts as support in an uptrend walk") | one close outside the lower band in the window (Oct 8, which then bounced to %b 0.35 within two bars); no tolerance for "close enough" exists in the sources, 3 or more near-band closes is an uncited habit | SOURCED (band walk definition, [1][6] in SOURCES.md), tolerance and the mirror reading OURS |
| TOM-1 counter trade at the top of an unhealthy push (fast push far above prior value, stall, sellers appear, short back toward the start) | the D leg: +9.1% from the Sep 20 00:00 low to the Sep 21 12:00 high (80,096 -> 87,385) (delta +11.6K on the Sep 21 00:00 bar), then stall and -5.9K / -5.7K delta bars; the move started at C 80,096; by Sep 24 00:00 the close (83,451) had given back about 54% of the leg | profile thinness at the top and "far above prior value" not checked; Tom trades sessions of FDAX, not 12h bars | catalog text SOURCED, mapping OURS, PARTIAL |
| FAB-2 absorbed push (big delta, no price result, then the other side moves price) | Oct 8 12:00: sell delta -5.2K and volume 147K gave no lasting result, the next bar +4.1K delta | not a footprint read, Binance bar delta only | catalog text SOURCED, mapping OURS, PARTIAL |
| FAB-5 buyers protect a level (long, tight stop) | the level exists: the Oct 8 low 80,345 is also the engine's weekly swing low (80,344.8) | the buyers are not shown: Oct 15 00:00 undercut it by 157 points with delta -5.7K and no absorption | catalog text SOURCED; condition UNTESTED, not met |
| TOM-4 trend continuation pullback (mirrored to the downside) | the two mid-band rejections Oct 12 and Oct 14 are pullbacks to value in a falling market | Tom's quotes are for uptrends; the mirror is not stated in the catalog | OURS |
| TOM-2 counter trade in balance | 12h balance 82.5K-87.2K from Sep 24 to Oct 7 | the balance broke down on Oct 7 and price is now under it | does not apply now |

## Intraday zoom: 1m and 3m shots of the same lower-band touch (17bb712d5ead, d2d2f30fa142)
Added 13:50Z at the coordinator's request after the 12h read. Pre-read (VVP-002 F.1): pass for both (timeframe, OHLC header, BB legend, price axis; OI, CVD, Net Delta, RSI 14 + SMA, StochRSI 14 14 3 3, Volume SMA 9 present; no operator drawings on either; VWAP is struck out/hidden on both). Engine snapshots: `MyTradingSys/research/screenshots/engine/17bb712d5ead.json`, `d2d2f30fa142.json`. Data: Binance USDT-M 1m klines fetched to 13:44Z (closed bars), 5m `openInterestHist`, live `/fapi/v1/openInterest`.
Clocks: 17bb: the last candle is the forming 13:12 bar (open 80,380.1 exact; countdown 00:36, so capture 13:12:24Z; the manifest's 13:11 is one minute early). d2d2: the last candle is the forming 13:39 3m bar (open 80,431.5, high 80,681.0, low 80,408.9 exact; countdown 00:07, so capture about 13:41:53Z); the x label 13:42 sits to the right of the last candle, it is not the bar's open.

### What the brief said versus what the images and data show
The coordinator relayed readings of both shots. Checked against data (rows R-16..R-28):
- 17bb "12:29 flush": the spike is the 12:30 bar (O 81,029.3, H 81,074.1, L 80,565.1, C 80,805.1; 3,171.7 BTC = 256.2M USDT; the chart spike reads about 240M by pixel). The 12:31 bar printed the 1m low 80,520.3, not "near 80,450". 12:30Z is 08:30 ET, the usual US data-release minute; no release was identified here (OURS inference, unchecked).
- 17bb "CVD -1.2K to -1.8K": by pixel the level falls from about -1.2K to about -1.7K (a 0.5K move, a rough read), while the three steps read -0.28K, -0.33K, -0.1K (sum -0.71K); Binance taker delta -279, -327, -91 BTC (sum -697). The steps match Binance; the level reading is the rougher number, and the level anchor is unexplained as in R-13.
- 17bb "OI 92.0K to 92.34K while price grinds down the lower band to 80,355, RSI 28.5": price, band and RSI reproduce exactly (R-16..R-18). The OI path between 12:30 and 13:12 cannot be checked against Binance: `openInterestHist` is corrupt from 11:00Z until about 13:15Z (see R-10 and R-21), so only the endpoints are comparable (hist 92,083 at 10:55Z, 92,495 at 13:20Z).
- d2d2 "price 80,299 below VWAP 81,051 and a red level near 80,930, wick to 80,050, CVD -6.6K to -7.6K, net delta -0.6K to -1.17K": none of these is in the image. It shows price 80,608.8 (a bounce, 0.12% above the 3m middle band 80,516 and 0.58% above the lower band 80,142), CVD -7.083K, Net Delta candle -1.022K to -747, OI candle 93.132K-93.499K, VWAP hidden, and the red horizontal on the RSI panel is the RSI 40 line, not a price level. Those numbers fit a reading from about 13:25-13:35 (3m 13:24 close 80,300.4; low 80,027 at 13:31; our day VWAP, hlc3 anchored 00:00Z, is 81,036 at 13:35 and 81,021 at 13:41). Only the OI step is confirmed: hist 92,495 (13:20) to 93,122 (13:30). I read the image I have; if another 3m capture exists it was not in the inbox.

### What the flows did, in order (Binance 1m taker delta, BTC; share = delta / volume)
| Window (UTC) | Price | Taker delta | Share | OI |
|---|---|---|---|---|
| 10:47-12:29 pre-flush | 80,840 -> 81,029 (+0.23%) | +176 | +3.2% | ~92.0K flat (hist ok until 11:00) |
| 12:30-12:32 flush | 81,029 -> 80,697 (-0.41%), low 80,520 | -697 | -14.9% | chart: dips then rises |
| 12:33-13:11 grind (shot 17bb) | 80,697 -> 80,380 (-0.39%) | -263 | -4.3% | chart +0.34K (unchecked) |
| of which 12:49-13:11 | 80,824 -> 80,380 (-0.55%) | -465 | -12.8% | |
| 13:12-13:26 | 80,380 -> 80,300 (-0.10%) | -136 | -6.9% | hist 92,495 at 13:20 |
| 13:27-13:30 US-open flush | 80,300 -> 80,129 (-0.21%), low 80,120 | -1,381 | -47.4% | hist +575 (13:25 -> 13:30: 92,547 -> 93,122) |
| 13:31-13:40 bounce | 80,129 -> 80,576 (+0.56%), low 80,027 at 13:31 | +1,226 | +23.6% | hist 93,122 -> 93,170, flat |
| 13:41-13:44 | 80,580 -> 80,680 (+0.12%) | -688, -372, +141, +62 = -856 | -39% | live 94,110 at 13:45:42; 93,990.6 at 14:02:05 |

### Answer: new shorts, or absorption at the band?
Reading the 12:33-13:11 grind as the 17bb shot shows it: price fell, taker delta stayed negative and the chart's OI rose. That is the price-down / OI-up / sell-aggression quadrant, which is the "new positions opening with the move" reading (continuation), not absorption. The test against absorption is FAB-2's own words (big delta with no price result). Over the window as a whole price followed delta: the delta share was -12.8% over 12:49-13:11 and price fell -0.55%. Bar by bar the test is a judgement, not a count: 12:50 (-49 BTC, -52% share, price -0.01%), 12:54 (-126, -71%, -0.12%) and 12:57 (-215, the largest sell bar, -45%, -0.08%) each carried a large sell share for a small price move, while 13:08 (-132, -0.13%), 13:03 (-112, -0.08%) and 13:11 (-106, -0.09%) moved price a little more; none of these is a stall of the FAB-2 size seen at 13:27. The 'new shorts' label (OURS) rests on the chart's OI rising, which Binance cannot confirm for this window (hist unusable, R-10), so it is stronger than the data I could verify; what is checked is the sell-side delta and the price decline. The size is small: OI +0.34K BTC (0.4%) against 10.8K BTC traded since 12:30, and the OI path is the one number I could not verify. What would have said absorption was missing: flat or rising price on negative delta.
What happened next is not in the 17bb image but is in our data, and it changes the picture: the 13:27-13:30 US-open bar took delta of -1,381 BTC (47% of the volume) for only -0.21% and a 80,027 low one bar later, then 10 bars of +1,226 BTC delta brought +0.56%. By FAB-2's definition that second flush is absorbed (big delta, little price result, the other side then moves price). It was also the window where OI stepped +575 BTC (the 13:25 -> 13:30 hist rows straddle the 13:27 start, so the attribution is approximate), so the OI-build-on-sell-delta pattern held (new shorts) and was followed by a bounce rather than continuation. OI did not unwind during the bounce (hist 93,122 at 13:30, 93,170 at 13:40; live 94,110 at 13:45), so this is not yet a short-covering squeeze (covering lowers OI); positions opened into the low are still open, whether those are the same shorts or new longs cannot be separated with OI plus delta. Net: the 13:12 snapshot read as continuation, the later low at 80,027 read as absorption after an aggressive build; the two statements are both true and do not conflict (different bars). This is a description, not a trade call.

### Where price sits at 13:44Z and what would change the read (all OURS levels from the data)
- 1m: close 80,680, RSI 63.4, K 96; 3m: forming bar above the 3m middle band (80,516 at capture) after the first 3m close above it since the 12:39 bar (13:39 close 80,580 vs mid 80,514.5). The 80,450 level the brief named has been reclaimed (1m closes above it 13:39-13:44; 13:38 closed 80,431.5); the 80,930 / VWAP area (our VWAP 81,021) has not.
- Continuation would be confirmed by: price taking out 80,027 (the 13:31 low) with delta share negative again and OI rising. Absorption would be confirmed by the opposite: closes holding above the 3m middle band while delta stops being sell-heavy; OI flat means the shorts opened into the low are still open, and OI falling would be a separate squeeze signature (shorts covering), which is a different thing from absorption and weakens 'positions still open'. The 13:41-13:44 delta was -856 BTC (-39%) for +0.12% of price, which by the same OURS test leans toward absorption of the bounce's sellers, but one bar run is not a decision. Neither case is decided at 13:44. OI check after the fact: hist stops at 13:40 (93,170); live OI is 94,110 at 13:45:42 and 93,990.6 at 14:02:05, so no large unwind yet.
- 12h context: the 13:31 low 80,027 is 318 points below the Oct 8 low 80,345 that the 12h read called the weekly swing low; the 12h bar's close is what decides whether the 12h retest held, not these bars.

### Which catalogued setups apply (labelled)
| Setup | What matches | What does not | Label |
|---|---|---|---|
| FAB-2 absorbed push (big delta, no price result, then the other side moves price) | the 13:27-13:30 flush and the 13:31-13:40 bounce (numbers above) | Binance bar delta, not a footprint; the 12:49-13:11 grind did not show it | catalog text SOURCED, mapping OURS, PARTIAL for 13:27, not met for 13:12 |
| Bollinger band walk (a tag is not a signal; the walk ends when price returns to the middle) | 3m closes below the middle band 12:54-13:36; the first 3m close above it after the 12:39 bar is 13:39 (80,580 > 80,514.5); the 1m forming bar at 13:12 sat 3.9 points under the lower band | the walk's end on 3m does not say anything about 12h | band-walk definition SOURCED ([1][6] in SOURCES.md), applying it to 1m/3m OURS |
| MAL-17 regular bullish divergence on 1m (price lower low, RSI higher low, bullish confirm) | at the 13:12 shot: price 80,355 below the 12:31 low 80,520 with RSI 28.5 above 27.7 (a 0.8-point margin, one pivot choice) | the 13:12 version was invalidated by 13:30 (price 80,120, 1m RSI 24.95 below 27.7). Later: the 13:31 low 80,027 is a lower low than 80,120 and the 1m RSI on that bar is 41.2 against 24.95, so the lower-low / higher-RSI geometry exists on one-bar pivots; it is a single-bar pivot pair, not a clean MAL-17 setup | rule SOURCED (MAL-17), timeframe transfer and pivots OURS; weak, not confirmed |
| Malkan BB/RSI 40-60 range logic (RSI pinned under 40 with the SMA overhead in a downtrend; RSI 60 rejection) | 1m RSI below its 40 line 13:00-13:12 with SMA 36-41; 1m RSI spiked to 67.3 at 12:24 and was 55.5 a bar later (a spike through 60, not a rejection at 60) | the other operator shots of this hour (9317fd8402ed, 672453a288eb) show the same teaching case and are being catalogued by another session; I did not read its summary or evaluate it here | not evaluated here |
| TOM-1 / TOM-2 / TOM-4 (Tom) | none: they are session and volume-profile logic on FDAX and are not evaluated on 1m/3m BTC here | | does not apply |

### Falsifiers for the next read of this hour
- "OI has not unwound during the bounce": a 5m `openInterestHist` row after 13:45Z more than 400 BTC below the 13:40 value (93,170) would say shorts are covering after all (squeeze), and weaken "absorption with positions still open".
- "Net Delta is not the Binance taker delta": ratios here are 0.48 (3m, 13:27), 0.28 and 0.06 (1m 12:30, 12:31); any pair of shots with the ratio near 1 would reopen R-12.
- "Binance OI history was only bad 11:00-13:15Z": the corruption evidence is the 11:10-12:40 rows at 98-101K against 92-94K live, then no rows at all 12:45-13:15 (missing is not the same as corrupt). Rows after 13:40 were not yet published at 14:02Z, so the newest hist row lags by about 20 minutes. A second dip in `openInterestHist` away from live `/openInterest` by more than 3% would make it a recurring fault, not a one-off.

## Falsifiers for the next read of this symbol
- "The Oct 15 retest is not a flush": a 12h bar with OI down 2K or more, delta below -5K and a close back above 81.7K (the Oct 8 pattern) would be HELD against us; a 12h close at %b <= 0.1 with OI flat or rising would say the walk continues.
- "RSI 40 is lost on 12h": two consecutive 12h closes with RSI above 40.
- "Net Delta is a different series from the Binance taker delta": the next shot's Net Delta step against the 1m taker delta of the same bar, ratio far from 0.5 repeats the finding in R-12.

## Reviewer (Haiku, cold; REVIEW.md in this folder)
Verdicts: 52 AGREE, 5 DISAGREE, 9 UNVERIFIABLE (66 rows). DISAGREE items and what was done:
- "point B" for the Sep 18 12:00 tip while the letter beside it is C: ACCEPTED, letters re-read as leg labels (table above).
- "lower in both price and RSI" for Oct 5 versus Oct 2 12:00: ACCEPTED, my error (RSI 61.3 > 54.9); fixed, and it makes the divergence depend on the pivot even more.
- R-13 "CVD starts near Sep 10 12:00": ACCEPTED, I mistook the point where candles drop below the legend for the start; I re-tested anchors (left edge gives -73.5K, not -49K) and rewrote R-13.
- R-14 printed "1.0248B": ACCEPTED, the chart prints 1.024B; fixed.
- "+8.6%" for the D leg: ACCEPTED, 80,096 -> 87,385 is +9.1%; fixed.
Reviewer's 'missed or wrong' list (12 items): items 1-9 and 12 fixed in this file (circle ambiguity, name clash for point C, tick versus bar close, provisional forming bar, base of the 2.7%); item 10 (circle 1 pixel reads about 44, not clearly on the 40 line) and item 11 (the 71,987.5 label in ef38 is the cursor readout, not a level) accepted as minor, no change.
The 9 UNVERIFIABLE rows are Binance-data numbers the reviewer cannot see in the images; they rest on the scratch data described at the top and were not independently re-derived by a second reader.

### Intraday section (REVIEW_INTRADAY.md)
Verdicts: 57 AGREE, 10 DISAGREE, 16 UNVERIFIABLE (83 rows). I re-computed every DISAGREE from our 1m data and all 10 were right; all are fixed above:
- CVD "-1.2K to -1.7K" against steps summing -0.71K: ACCEPTED, now stated as a rough level read versus exact steps.
- "0.6% above the 3m middle band": ACCEPTED, 0.12% above the middle and 0.58% above the lower band.
- 13:41-13:44 row omitted the 13:42 bar (-372): ACCEPTED, sum -856 BTC (-39%), and the "mixed" label is gone.
- "none of the 1m bars 12:49-13:11 shows absorption": ACCEPTED as a judgement, not a count; 12:50, 12:54, 12:57 are listed.
- "two largest sell bars 13:03, 13:08": ACCEPTED, the largest is 12:57 (-215); 13:03 was -0.08%, not -0.14%.
- "1m closes above 80,450 from 13:38": ACCEPTED, from 13:39.
- "13:31 higher low": ACCEPTED, it is a lower low; I re-read MAL-17 for that bar (RSI 41.2 against 24.95): geometry present on one-bar pivots, weak.
- "RSI rejected at 60 on 12:24 (67.3)": ACCEPTED, wording fixed.
- Falsifier "only 11:00-13:15Z": ACCEPTED, missing rows and corrupt rows are now separated.
Reviewer's 'missed or wrong' list (18 items): items 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 and 17 fixed above (the 'new shorts' label softened, the absorption/squeeze conflict removed, OI refreshed to 14:02Z); item 2 accepted (the mapping to FAB-2 is OURS and says so); item 18 (no trade call) passed. The 16 UNVERIFIABLE rows are Binance numbers the reviewer cannot see in the images or pixel reads; they rest on the scratch data and were not re-derived by a second reader.

## Decisions logged (routine, goal-serving defaults)
- Used Binance USDT-M perp data because the chart legend says "Binance BTCUSDT"; CoinGlass OI/CVD/Net Delta may aggregate more venues, which is why steps and direction are compared, not levels.
- Treated the operator's date "Sep 18" for the RSI circle as pixel-mapped Sep 20 00:00 and kept both in the table; no question was sent.
- Filed nothing in BUGS.md or PLAN.md (shared hot files); R-10, R-11, R-12 go to the coordinator in the report as candidates.
- Outcome for all four shots: `noaction:` (shot.py refuses `note:` while MISMATCH rows exist) naming R-10..R-12 (and R-20, R-25, R-26 for the intraday shots) as card candidates for the coordinator; the extract is this file.

## Outcomes
| Claim id | Outcome | Item |
|---|---|---|
| R-10 | note | Binance openInterestHist step on 2026-10-15 11:00Z; coordinator to decide a card |
| R-11 | note | engine snapshot vwap_anchor_utc after as_of |
| R-12 | note | CoinGlass Net Delta is not Binance taker delta (ratio 0.5 and 1.7) |
| R-13 R-14 R-15 R-27 R-28 | noaction | levels, drawings and volume units are not comparable or not stored |
| R-20 R-26 | noaction | the coordinator's relayed readings differ from the images and data; reported to the coordinator, nothing filed |
| R-21 | note | OI path 12:30-13:12 is unverifiable because of R-10; R-10 text updated: transient 11:00-13:15Z |
| R-25 | note | Net Delta ratio varies (0.06-0.48); same card candidate as R-12 |
