# Krown catalogue G2: second-model audit of S1-S9 (2026-10-17)

Card krown-catalogue-gpt-audit. Report only: no catalogue, code or spec edit. No VALIDATION/HOLDOUT read. Audited file:
`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md` (lines 1-745: sections 0-3, KR-S1 to KR-S9) against
`transcripts/*_timed.txt` and `KROWN_RULES.csv` / `KROWN_CONSOLIDATED.md` / `DATA_COVERAGE.md`.

## What was checked
- (b) Quote support, mechanical: every `> "..."` + `Source GPS` pair in lines 1-745 (151 quotes in lines 1-745; the script ran over all 229 in the file) searched as a normalised word run in the
  named video's timed transcript. Result: 0 not found, 0 whose caption time differs from the stamp by more than 20 s. `verify_extract_quotes.py` on the
  whole file: PASS 0 problems.
- (b) Quote supports row, by reading: each S1-S9 quote sits under a claim it supports, except the shading noted in F3 and F6.
- Extract citations `extracts/...md:N (ID)` in S1-S9 (38): every cited line holds the quote the number is credited to.
- (a) NOT STATED cells re-searched in the transcripts (stop, loss, target, exit, profit, oscillator, timeframe, period words in all 11 videos used by S1-S9).
- (c) BTC-visible Y/P/N against `DATA_COVERAGE.md` (Binance BTCUSDT 1d from 2017-08-17; 1w_from_1d from 2017-08-21; Coinbase BTC-USD 1d from 2015-07-20).
- (d) SOURCED vs OURS labels: no OURS number is presented as his in S1-S9; all SOURCED numbers trace to a spoken line.

## Findings
| # | Sev | file:line | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|---|
| F1 | MED | KROWN_SETUP_CATALOG.md:349 (also :37, :361) | S3 says his close-beyond rule is about support/resistance "not about range edges", so the S3 stop is OURS. He states a close rule for range edges in the range video the catalogue itself quotes at :245 and :404. | 6aA-P4Gvhrc t=00:13:04 "You need to see a closure above, in this case, the wick high of that initial range."; t=00:18:04 "Only act on the close back inside with proof." | S3 stop class: close back inside / close beyond the range edge is stated (CLEAR for the fake-out arm); keep distance OURS. |
| F2 | MED | :693, :694, :743 | S9 volume threshold is SOURCED as "2x the 30-day average" only. He gives 30- OR 60-period ("both of them are probably going to be about right") and the 30 is in bars of the chart timeframe (weekly/monthly), not days. A 60-bar arm is a stated alternative missing from the SOURCED list. | 7IxfsuD2wCM t=00:12:40 "you could do a 60-period average. You could do a 30-period average."; t=00:05:27-00:05:36 "past 30 days for that time frame's volume" | Add 60-bar arm to SOURCED; write the unit as bars of the signal timeframe. |
| F3 | LOW | :691 | "A MACD cross is the weakest, ignored alone" attaches the weakness to MACD. He says it of the momentum item as a whole (RSI divergence or MACD). Cell NOT STATED in the catalogue: he says the momentum signal usually fires last, and the MACD cross almost always last. | 7IxfsuD2wCM t=00:06:57 "that would be the least important out of all these things"; t=00:19:36 "you'll see this one happen last, especially if you're looking at the MACD"; t=00:19:41 MACD cross weekly, monthly, quarterly | Reword; add the order statement (momentum last, MACD almost always last) to S9 "what you see"; keeps "which 3 of 4" OURS. |
| F4 | LOW | :740 | BTC visibility PARTIAL is "not verified against the disk". It can be: the call is right. | DATA_COVERAGE.md:11,28: Binance BTCUSDT 1d from 2017-08-17, 1w_from_1d from 2017-08-21; the Dec 2017 weekly top is about week 17, so no warm-up for a 100-bar BBWP or a 30/60-bar volume mean. Coinbase 1d from 2015-07-20 covers price/BBWP but its volume is one venue (C6). | Replace "not verified" with the DATA_COVERAGE lines; 2017 top = NOT_IN_DATA for the volume and BBWP legs on Binance. |
| F5 | LOW | :657, :658, :663, :652 | S8 labels BBWP below 25-35 and above 85 as SOURCED without his qualifier "can be time frame dependent". The catalogue omits his caution that breakouts out of low volatility fail quickly, which bears on the S8 entry. | kcMnnQr1VFg t=00:07:12 "Yes, can be time frame dependent"; t=00:21:34 "Breakouts fail and reverse quickly during low volatility" | Add both quotes to S8 context; list "threshold per timeframe" under NOT STATED. |
| F6 | LOW | :505, :506 | S6 lists "Side: both". He describes only the upside disconnect (candles floating above a short EMA). The mirror below is NOT STATED. He also says other markets show it ("as well as many different markets I've noticed"), the catalogue limits it to Bitcoin daily. | -NXzJs5JRks t=00:23:34 "the entire candles will float above"; t=00:24:18 "as well as many different markets" | Side: long-side disconnect stated; short mirror NOT STATED. Timeframe/market: his count is Bitcoin daily, other markets claimed without data. |
| F7 | LOW | :137, :416, :500 | Hypothesis ids are inconsistent. :137 maps 80-95 % (21/55 cross) to H-M2 and 70 % compression to H-Q1; :500 maps the 80-95 % to H-M4; :416 maps the 70 % to H-R1. KROWN_CONSOLIDATED.md:221,224,229,236: H-M2 = 200-week SMA touches, H-M4 = weekly 55 EMA bias, H-R1 = consolidation vs expansion, H-Q1 = BBWP below 25-35 and 70 % compressed. The 80-95 % cross claim has no hypothesis. | KROWN_CONSOLIDATED.md:218-236 | Align ids or add an H row for the 21/55 cross claim. |

No finding in (d): the numbers that look like his (3-5 zones, 2 turns, 2x/20-period volume, 3-5 candles, 3 tests, 40-60 RSI, 7/100 BBWP, 25-35, 85, 50th, 93rd, 252, 20-85 %, 3 of 4, 85, 21/55/200/377/5) are each a spoken line; 1.5 x ATR14, 2R, MACD 12-26-9, grids and stops are labelled OURS.
Not checked: KR-S10 to KR-S16 and section 4 (outside the card). Video frames (charts shown with "here") are NOT_IN_DATA.

HIGH findings: 0, so no follow-up cards were created.

VERDICT: SOUND (quotes 151/151 verbatim, timestamps right, no OURS-as-SOURCED; fix F1 and F2 before G3 marks, the rest are wording).
