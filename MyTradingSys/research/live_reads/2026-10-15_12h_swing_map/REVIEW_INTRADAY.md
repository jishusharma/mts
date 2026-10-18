# REVIEW_INTRADAY: cold check of the intraday zoom section and rows R-16..R-28

Reviewer: independent cold read (Haiku 5.5). Both images read directly. Binance public data fetched by the reviewer at about 13:56Z: fapi 1m klines (closed bars to 13:53), 5m openInterestHist (newest row 13:40), live openInterest (93,841.9 at 13:56:05Z). Pixel reads of chart panels are approximate and are labelled as such.

| item | AGREE/DISAGREE/UNVERIFIABLE | what you saw or computed |
|---|---|---|
| R-16 17bb header O 80,380.2 | AGREE | Image header O 80,380.2. Binance 13:12 bar open 80,380.1 (= 13:11 close). The header change -25.1 implies previous close 80,380.1, so the 0.1 gap is display rounding; "exact" in the text is overstated. |
| R-16 17bb header H 80,386.0 / L 80,355.0 / C 80,355.0 at capture | UNVERIFIABLE | Bar still forming at capture. Only partial values can be seen; the bar later reached H 80,429.8 and L 80,341.9. Classing these as MATCH is not supported. |
| R-16 final 13:12 bar H 80,429.8 / L 80,341.9 / C 80,417.6 | AGREE | Binance 1m 13:12 bar exactly as stated. |
| R-17 17bb BB 80,554.7 / 80,750.5 / 80,358.9 | AGREE | Recomputed from Binance 1m closes with the 13:12 close set to 80,355.0: mid 80,554.7, upper 80,750.5, lower 80,358.9. Legend order is mid/upper/lower. |
| R-18 17bb RSI14 28.49, SMA14 35.78 | AGREE | Wilder RSI14 on 1m closes gives 28.49 at the forming close; SMA14 of RSI gives 35.78. 13:11 RSI was 29.73. |
| R-18 17bb StochRSI 6.87 / 13.68 | AGREE | Stoch RSI (14,3,3) K 6.87, D 13.68. |
| R-19 17bb CVD steps -0.28K, -0.33K, -0.1K at 12:30-12:32 | AGREE | Binance taker delta 12:30 -279.2, 12:31 -326.8, 12:32 -91.1 BTC. The chart scale itself was not measured to 0.01K by eye. |
| R-20 brief "flush at 12:29, wick near 80,450" is MISMATCH | AGREE | Classification holds. 12:29 bar delta -68 on 148 BTC (quiet). The spike is the 12:30 bar (O 81,029.3 H 81,074.1 L 80,565.1 C 80,805.1). First 1m low below 80,450 is 13:08 (80,413.6). |
| R-21 17bb OI 92.0K -> 92.34K between 12:30 and 13:12 | UNVERIFIABLE | Last OI candle 92.337K matches the image legend. The 12:30 OI is about 91.9-92.0K by eye only. Binance hist: 10:55 92,082.7 and 13:20 92,495.4 match; 11:00-12:40 rows read 98-101K and 12:45-13:15 has no rows, so the path cannot be checked. |
| R-21 live OI 94,110 at 13:45:42Z | UNVERIFIABLE | Historical live reading not retrievable. Live openInterest at 13:56:05Z is 93,841.9, i.e. 268 BTC below the author's 13:45 value. |
| R-22 3m forming 13:39 bar O 80,431.5 / H 80,681.0 / L 80,408.9 | AGREE | Binance 3m bar 13:39: O 80,431.5, H 80,681.0 (13:40 bar), L 80,408.9. Exact. |
| R-22 3m close tick 80,608.8 at about 13:41:53 | UNVERIFIABLE | Tick not in the data. It lies inside the 13:41 1m range (80,505.0-80,621.5). The bar close 80,580.1 is correct. |
| R-23 3m BB 80,516.0 / 80,889.5 / 80,142.4 | AGREE | Recomputed with forming close 80,608.8: mid 80,515.9, upper 80,889.5, lower 80,142.4. |
| R-23 3m RSI14 51.33, SMA14 36.59 | AGREE | Wilder RSI14 51.33; SMA14 of RSI 36.59. |
| R-23 3m StochRSI K 84.73 / D 73.62 | AGREE | Recomputed 84.73 / 73.62. |
| R-24 3m CVD red candle 13:27 about -1.22K | UNVERIFIABLE | Pixel read only. By eye the candle is about 1.2K; not measurable to 0.05K here. |
| R-24 Binance 3m taker delta 13:27 -1,138 BTC | AGREE | 13:27-13:29 bar delta -1,138.3 BTC. |
| R-25 3m Net Delta 13:27 about -550 | UNVERIFIABLE | Pixel only. By eye the red body is roughly -500 to -550. No precise read possible. |
| R-25 1m Net Delta 12:30 about -79, 12:31 about -21 | UNVERIFIABLE | Pixel only; the scale is too fine to read at this size. |
| R-25 Binance 1m delta 12:30 -279, 12:31 -327 | AGREE | -279.2 and -326.8 BTC. |
| R-26 brief numbers (price 80,299; VWAP 81,051; red level 80,930; wick 80,050; CVD -6.6K to -7.6K; Net Delta -0.6K to -1.17K) are not in the image | AGREE | Image shows price 80,608.8, CVD -7.083K, Net Delta -1.022K to -747.031, VWAP hidden. The red horizontal is the RSI 40 line. Classing the brief numbers as MISMATCH is correct. |
| R-26 OI 92.4K -> 93.09K "confirmed by hist" | AGREE | Hist 13:20 92,495, 13:30 93,122, 13:35 93,074. 93.09 is approximate; "confirmed" is loose but not wrong. |
| R-26 day VWAP 81,036 at 13:35, 81,021 at 13:41 | AGREE | Volume-weighted hlc3 from 00:00Z on Binance 1m: 81,036.3 at 13:35, 81,020.8 at 13:41. |
| R-27 chart Volume SMA9 5.312M (1m) and 152.889M (3m) | AGREE | Both legend values read as printed. Unit not established (as the author says). |
| R-27 3m quote-volume SMA9 92.5M | AGREE | 92.51M on Binance 3m bars ending 13:39. |
| R-27 1m quote-volume SMA9 11.8M | UNVERIFIABLE | Closed bars 13:03-13:11 give 12.0M. The author's window (with forming bar) is not reproduced. Ratio 0.44 is therefore approximate. |
| R-28 VWAP hidden on both shots | AGREE | Both legends show VWAP greyed with the eye-slash icon. |
| Pre-read: all panels present, no operator drawings, VWAP hidden | AGREE | OI, CVD, Net Delta, RSI14 + SMA, StochRSI, Volume SMA9 visible on both. Only the last-price dotted line is drawn. |
| Clock 17bb: countdown 00:36, capture 13:12:24Z | AGREE | Bar closes 13:13:00, so 00:36 before that is 13:12:24. |
| Clock 17bb: manifest's 13:11 is one minute early | UNVERIFIABLE | Manifest not read. |
| Clock d2d2: countdown 00:07, capture about 13:41:53Z | AGREE | Bar closes 13:42:00. |
| d2d2 x label 13:42 sits right of the last candle | AGREE | Visible in the image. |
| 12:30 spike = 12:30 bar O 81,029.3 H 81,074.1 L 80,565.1 C 80,805.1 | AGREE | Binance 1m. |
| 3,171.7 BTC = 256.2M USDT | AGREE | 12:30 bar base 3,171.66 BTC; quote 256,211,101 USDT. |
| Chart spike "about 240M by pixel" | UNVERIFIABLE | By eye the spike top is near 250M. Not measurable precisely. |
| 12:31 low 80,520.3; nothing near 80,450 until 13:08 (80,413.6) | AGREE | 12:31 low 80,520.3; first 1m low under 80,450 is 13:08 at 80,413.6. |
| 12:30Z = 08:30 ET (EDT) | AGREE | Calendar arithmetic. Whether a release occurred was not checked (labelled OURS by the author). |
| 17bb CVD "-1.2K to about -1.7K over 12:30-12:32" | DISAGREE | Internal arithmetic fails: the author's own steps (-0.28, -0.33, -0.1) sum to -0.71K, but -1.2K to -1.7K is -0.5K. The start level is wrong or the end level is. |
| 17bb price 80,355, lower band and RSI 28.5 "reproduce exactly" | AGREE | BB and RSI exact (rows above). Price is a partial-bar close; see the H/L/C row. |
| d2d2 price 80,608.8 is "0.6% above the 3m middle band 80,516" | DISAGREE | 80,608.8 is +0.12% above the mid 80,515.9. It is +0.58% above the lower band 80,142.4. The reference is wrong. |
| d2d2 CVD -7.083K; Net Delta -1.022K to -747; OI candle 93.132K-93.499K | AGREE | Legend values as read. |
| d2d2 red horizontal = RSI 40 line | AGREE | Labelled 40 on the RSI panel. |
| Brief numbers "fit 13:25-13:35" | AGREE | 3m 13:24 close 80,300.4; 13:31 low 80,027.0; day VWAP 81,036 at 13:35. |
| OI step hist 92,495 (13:20) -> 93,122 (13:30) | AGREE | 5m openInterestHist rows. |
| Flow 10:47-12:29: 80,840 -> 81,029 (+0.23%) | AGREE | 10:47 open 80,840.1; 12:29 close 81,029.2. |
| Flow 10:47-12:29: delta +176, share +3.2% | AGREE | +175.5 BTC; 3.25% of 5,402 BTC (rounds to 3.2 or 3.3). |
| Flow 10:47-12:29: OI about 92.0K flat, hist ok until 11:00 | AGREE | Hist 91.8-92.1K from 10:00 to 10:55; 11:00 row 100,231. |
| Flow 12:30-12:32: 81,029 -> 80,697 (-0.41%), low 80,520, delta -697 (-14.9%) | AGREE | -697.2 BTC; share -14.88%. |
| Flow 12:30-12:32: chart OI "dips then rises" | UNVERIFIABLE | Chart only; no usable Binance OI for that window. |
| Flow 12:33-13:11: 80,697 -> 80,380 (-0.39%), delta -263 (-4.3%) | AGREE | -263.2 BTC; -4.33%. |
| Flow 12:33-13:11: chart OI +0.34K | UNVERIFIABLE | CoinGlass aggregated OI; Binance hist has no rows 12:45-13:15 and is corrupt 11:00-12:40. |
| Flow 12:49-13:11: 80,824 -> 80,380 (-0.55%), delta -465 (-12.8%) | AGREE | 12:49 open 80,823.8; -464.9 BTC; -12.76%. |
| Flow 13:12-13:26: 80,380 -> 80,300 (-0.10%), delta -136 (-6.9%), hist 92,495 at 13:20 | AGREE | -136.3 BTC; -6.92%; hist 13:20 92,495.4. |
| Flow 13:27-13:30: 80,300 -> 80,129 (-0.21%), low 80,120, delta -1,381 (-47.4%) | AGREE | 13:27 open 80,300.3; 13:30 close 80,129.0; low 80,120.0 (13:30); -1,380.8 BTC; -47.36%. |
| Flow 13:27-13:30: hist OI +575 | AGREE | 13:25 92,546.9 -> 13:30 93,121.9 = +575.0. The 5m step straddles the window start at 13:27, so attribution to that window is approximate. |
| Flow 13:31-13:40: 80,129 -> 80,576 (+0.56%), low 80,027 at 13:31, delta +1,226 (+23.6%) | AGREE | 13:31 open 80,129.0; 13:40 close 80,576.2 (+0.56%); low 80,027.0 at 13:31; +1,225.6 BTC; +23.56%. |
| Flow 13:31-13:40: hist 93,122 -> 93,170, flat | AGREE | 13:30 93,121.9 -> 13:40 93,170.0. |
| Flow 13:41-13:44: 80,580 -> 80,680 | AGREE | 13:41 close 80,580.1; 13:44 close 80,680.0. |
| Flow 13:41-13:44: delta "-687 (13:41), +141, +62" | DISAGREE | Omits the 13:42 bar (-371.9 BTC). Full sum 13:41-13:44 is -856.5 BTC (-39.4% of volume), not a mixed picture. |
| Answer: 12:33-13:11 price fell, taker delta negative, chart OI rose | UNVERIFIABLE | Price and delta AGREE (-0.39%, -263 BTC). The OI rise is chart-only and cannot be checked against Binance. |
| Answer: "none of the 1m bars 12:49-13:11 shows [absorption]" | DISAGREE | Big sell share with small price result occurs: 12:50 (-49 BTC, -52% of volume, price -0.01%), 12:54 (-126 BTC, -71%, -0.12%), 12:57 (-215 BTC, -45%, -0.08%). The author's own test would flag these. The statement is a judgement, not a finding. |
| Answer: "two largest sell bars of the window (13:03 -112, 13:08 -132)" | DISAGREE | Largest sell bar in 12:49-13:11 is 12:57 (-214.9 BTC). 13:08 (-131.8) is second. 13:03 (-112.1) is fourth, after 12:54 (-126.2). |
| Answer: 13:03 bar "-0.14%" | DISAGREE | 13:03 open 80,592.0 to close 80,524.6 = -0.08%; prior close to close also -0.08%. |
| Answer: 13:08 bar "-0.13%" | AGREE | 13:08 open 80,554.9 to close 80,447.5 = -0.13%. |
| Answer: 10.8K BTC traded since 12:30 | AGREE | 12:30-13:11 volume 10,758.7 BTC. |
| Answer: "OI +0.34K BTC (0.4%)" over the grind | UNVERIFIABLE | Chart-only; see the chart OI row. The 0.4% arithmetic is right for +0.34K on 92K. |
| Answer: 13:27 bar "OI stepped +575 BTC, OI-build-on-sell-delta" | AGREE | Number matches the hist step. The "new shorts" label is an inference (see Missed list). |
| Answer: OI did not unwind during the bounce (hist 93,122 at 13:30, 93,170 at 13:40) | AGREE | Hist values. Live value after 13:40 is not in the hist series (see live OI rows). |
| Answer: 13:31 low 80,027 is 318 points below the Oct 8 low 80,345 | AGREE | 80,345 - 80,027 = 318. |
| Where price sits 13:44: close 80,680, RSI 63.4, K 96 | AGREE | 1m RSI14 63.36; Stoch K 95.98. |
| 3m: first 3m close above the mid after 12:39 is 13:39 (80,580 vs mid 80,514.5) | AGREE | 13:39 close 80,580.1 vs mid 80,514.5. But the 12:39 close (80,966.9) was itself above its mid (80,933.2). Only true if 12:39 is excluded; see Missed list. |
| 1m closes above 80,450 "13:38-13:44" | DISAGREE | 13:38 close 80,431.5 is below 80,450. Closes above are 13:39-13:44. |
| 80,930 and VWAP 81,021 area not reclaimed | AGREE | Highest 1m high from 13:31 to 13:53 is 80,681.0 (13:40). Price has not reached 80,930 or VWAP 81,021. |
| Band walk: 3m closes at or below the lower half 12:54-13:36 | AGREE | Every 3m close 12:42-13:36 is below the 3m mid. "Lower half" wording is loose. |
| Band walk: 1m forming bar at 13:12 sat 3.9 points under the lower band | AGREE | 80,355.0 vs lower 80,358.9 = 3.9. |
| MAL-17: 12:31 low 80,520 with RSI 27.7; 13:12 price 80,355 with RSI 28.5 | AGREE | 1m RSI at 12:31 close 27.71; at 13:12 28.49. Margin 0.78. |
| MAL-17 invalidated by 13:30: low 80,120, 1m RSI 24.95 below 27.7 | AGREE | 1m RSI at 13:30 close 24.95; 13:27-13:30 low 80,120.0. |
| MAL-17: "the 13:31 higher low had no divergence" | DISAGREE | The 13:31 low 80,027 is a lower low than 80,120 (13:30) and 80,520 (12:31). It is not a higher low. |
| Malkan 40 line: 1m RSI below 40 from 13:00 to 13:12, SMA 36-41 | AGREE | 1m RSI 13:00-13:12 between 32.3 and 39.6; SMA14 41.4 at 13:00 falling to 36.2 at 13:12. |
| "RSI rejected at 60 on 12:24 (67.3)" | DISAGREE | 1m RSI at 12:24 is 67.30 (value right). It is above 60, so it is not a rejection at 60. Wording error. |
| Falsifier 1: a 5m hist row after 13:45Z more than 400 BTC below 93,170 | UNVERIFIABLE | At the reviewer's fetch (about 13:56Z) the newest hist row is 13:40. No 13:45-13:55 rows exist yet, so the falsifier cannot be evaluated. |
| Falsifier 2: Net Delta ratios 0.48 (3m), 0.28 and 0.06 (1m) | UNVERIFIABLE | Depends on pixel Net Delta values (see Net Delta rows). |
| Falsifier 3: OI history "only corrupt 11:00-13:15Z" | DISAGREE | "Only" is not supported. Hist has no rows at 13:45-13:55 at the reviewer's fetch; that gap is not in the text. |

## Missed or wrong

1. Reasoning, "new shorts" (Answer section): the label rests on chart OI rising over 12:33-13:11. Binance cannot confirm that window (hist corrupt 11:00-12:40, no rows 12:45-13:15). The text then says the shorts and new longs "cannot be separated". The "new shorts" label is stronger than the data.
2. Reasoning, "absorbed": calling the 13:27-13:30 flush absorbed "by FAB-2's definition" is the author's mapping (OURS), not a fact. The 13:27-13:30 price result of -0.21% is a judgement. The same pattern appears at 12:50, 12:54 and 12:57 (see the DISAGREE row), so the continuation-versus-absorption split is not made bar by bar.
3. Logic conflict: the absorption confirmation criterion "closes holding above the 3m middle band with OI flat or falling (the squeeze signature)" counts falling OI as absorption. The falsifier for the same hour says falling OI (a squeeze, shorts covering) weakens absorption with positions still open. The two cannot both hold.
4. Stale OI claim: "OI did not unwind during the bounce" is dated to 13:40 (hist). Live OI was 94,110 at 13:45:42 per the author and is 93,841.9 at 13:56:05 per the reviewer. OI has fallen about 268 BTC since 13:45 and the newest hist row is still 13:40.
5. Missed flow bar: the 13:42 bar (-372 BTC) is omitted from the 13:41-13:44 row (see the DISAGREE row). The "mixed" description is wrong; net delta over 13:41-13:44 is -856.5 BTC.
6. R-16 class: H/L/C at capture are partial-bar values and cannot be verified. The row should read UNVERIFIABLE for those values. The open is 0.1 off the data (display rounding), not exact.
7. Internal arithmetic: the CVD level range (-1.2K to -1.7K) does not match the author's own step sum (-0.71K).
8. Wrong reference: "0.6% above the 3m middle band" should read 0.12% above the mid, 0.58% above the lower band.
9. Wrong bar and wrong move in the sell-bar claim: largest 1m sell bar in the window is 12:57 (-215 BTC), not 13:03; the 13:03 move is -0.08%, not -0.14%.
10. Wrong bar in the reclaim claim: 13:38 closed 80,431.5, below 80,450. Closes above 80,450 start at 13:39.
11. Wrong direction word: 13:31 low 80,027 is a lower low, not a higher low.
12. Wrong wording: 67.3 at 12:24 is above 60, not a rejection at 60.
13. "Since 12:39": the 12:39 3m close (80,966.9) was above the 3m mid (80,933.2). The first close above mid after the 12:39 close is 13:39; the text should say so, because the band-walk line calls 13:39 the "first" close above mid.
14. "Lower half" in the band-walk line: the closes are below the 3m middle band, not in the lower half of the band. Use "below the middle band".
15. Falsifier 3: the hist gaps are 12:45-13:15 and, at the reviewer's fetch, 13:45-13:55. Missing rows are not the same as corrupt rows; the 11:00-12:40 level jump (98-101K) is the corruption evidence and should be cited.
16. Precision of pixel reads: Net Delta values (-79, -21, -550), CVD -1.22K and the Net Delta ratios 0.28 / 0.06 are pixel reads and should be shown as approximate.
17. Hist step attribution: the 13:25 to 13:30 OI rows straddle the 13:27 start of the flush, so "the bar where OI stepped +575" is approximate.
18. Trade call check: the section contains no entry, stop or target. The "confirmed by" and "would be confirmed by" lines are conditional reads, not trade instructions. Passed.

Counts: AGREE 57, DISAGREE 10, UNVERIFIABLE 16
