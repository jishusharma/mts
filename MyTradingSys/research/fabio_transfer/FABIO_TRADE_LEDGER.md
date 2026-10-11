# FABIO TRADE LEDGER (card fabio-trade-ledger) - Status: DONE 2026-10-11 (all available in the 5 videos: 8 entries F1, F2, F3a-c, F4a-b, F5)

Goal (card): >= 20 trades (or all available) with frame evidence. Reached: F1 full (frame-read order labels), F2 approximate (no order labels in the video),
F3 transcript only. Rows are in FABIO_TRADE_LEDGER.csv. Read 2026-10-11 relay, JIS-NB.

## Videos on F:/MTS/data/fabio_videos (1280x720 f398 video-only mp4 + en vtt; no ffmpeg merge, same as tom_videos)
8CWKfoSJu3c (568 s, "20R in one NQ session"), 0jM5Y31YJak (499 s, "Top 3 trades from the competition"), fZlNGWvd2Ko (406 s, best session of October),
9IliXww64uM (827 s, "$4000 in 1h"), jasv3L-d8ZE (721 s, "manage a -10.000$ session").
Contact sheets (30 s, 4 per sheet): F:/MTS/data/fabio_videos/sheets/<id>_NN.jpg (27). Tools there: sheets.py <step>, grab.py <id> <t> [x0,y0,x1,y1] (1280x720 coords).
Read so far: 8CWKfoSJu3c sheets 00-04 (all), 0jM5Y31YJak 01-02, fZlNGWvd2Ko 00-03 (all). NOT read: 0jM5 00,03,04; 9IliXww64uM (7); jasv3L-d8ZE (6).
Other candidates from search (not downloaded): DyS79Eb92Ug, Is1HvdfQm5c, xUyqIjCfZzg (long live sessions), Jpd96fLqr5M, 9I5vTvwsMBk, gLHd20jE8UQ.
Note: many are teaching videos of chart breakdowns, so trade counts per video are small (~1 each, like Tom).

## F1 numbers (NQ-202512, $20 per point per contract)
Short 10 @ 25652.75, stop 25668.50 (15.75pt = 0.061% = $3150), TP 25514.75 (138pt = 8.8R = $27600). Stop trail in profit: 25640.00 -> 25627.00 -> 25603.25 -> 25556.00 -> 25537.75
(locks +$2550/+$5150/+$9900/+$19350/+$23000). First leg risk 31 ticks ($155 per contract) with R/R 19.06 on the label. Day P/L before the trade +$27492.50 (risking the day's profit).
Stop width stat so far: 15.75pt on NQ at 25.6k = 0.061% (compare Tom FDAX 20-30pt = 0.08-0.12%).

## F3 numbers (fZlNGWvd2Ko, NQ-202512, $20 per point per contract; relay 2026-10-11)
Long 2 @ 24544.50 (t=90, after bounce off 'protection wall buy' 24467-24475), scale to 12 @ 24548.88: stop 24540.00 (8.88pt = 0.036%), TP 24656.26 (12R), closed by t=180 for +1557$.
Re-entry long 14 @ 24568.38: stop 24565.00 (3.38pt = 0.014%, risk 980$), TP 24655.75 (87.4pt = 25.9R = 24500$). Stop to breakeven 24568.25, then 24584.75, then 24604.00; TP pulled to 24647.25.
Result: Daily P/L 6468 -> 28485 = +22017$ (exit fill not on a frame). Stop width stat now: 15.75pt (F1), 8.88pt, 3.38pt on NQ at 24.5-25.6k = 0.014-0.061%.

## Management pattern seen (his words + frames)
Narrative labels on chart: punch to the wall (absorbed effort), re entry, rewarded effort, failed auction on Cash session sensitive high, 0 doubt, squeeze.
Stop moves only in steps behind structure as price falls; TP fixed far; size 10 on the re-entry funded by day profit.

## 9IliXww64uM (read 2026-10-11 relay, sheets 00-06, ES, Jan 2026)
Mostly talk: Schwab account page (value 217,392; equity curve jumped from ~61k on Nov 24 2025 to 210k on Jan 27 2026), ES 5-min and 1-min footprint charts with CVD/delta tables (no order labels),
and two pasted trade screenshots (file 2026-01-30 214344): F4a short 1 @ 6986.75, F4b short 1 @ 6977.5 (ES, 1 lot, no stops visible). Hand-drawn schematic at t=780 (balance -> failed breakout -> reversal).
No stop/TP prices on any frame, so no stop-width stat from this video. Ledger now 17 rows: 7 entries (F1, F2, F3a-c, F4a-b) plus management/exit rows.


## jasv3L-d8ZE (read 2026-10-11 relay, sheets 00-05, NQ-202512, $20/pt)
F5 short 15 @ 24960.28, stop 24969.75 (9.47pt = 0.038%, risk 2850$), TP 24910.25 (50pt = 5.3R = 15000$). Started the trade at Daily P/L -9577.50 (title: manage a -10.000$ session).
Management: stop tightened to 24961.50 then 24961.25 (above avg entry), scale-in to 18 lots avg 24959.18 (risk 720$), held through a pullback (open P/L 6629 -> 4559 -> 11129),
at t=630 stop trailed to 24925.00 (locks 12330$) and TP pulled 24910.25 -> 24917.00. Flat by t=660, Daily P/L +2331.50 (+11909$ on the trade). Exit fill not on a frame.

## Final stats (8 entries, 5 videos; video count is the limit, teaching videos show ~1.6 trades each)
Markets: NQ 7 entries (F1, F2, F3a-c, F5; F2 levels approximate), ES 2 (F4a-b, 1 lot, no stops). Sessions: NY/US cash session for all frames with a clock.
Stop width on NQ (points / % of price): F1 15.75 / 0.061, F3b 8.88 / 0.036, F3c 3.38 / 0.014, F5 9.47 / 0.038 (and 2.07 / 0.008 after tighten). Median 9.2pt ~ 0.037%.
Target distance: 138pt (8.8R), 107pt (12R), 87pt (25.9R), 50pt (5.3R): R-multiples far above 3 on every labelled trade.
Management (all four labelled trades): stop moves only toward profit (breakeven or beyond) in steps; TP is pulled in late (F3c, F5); scale-in on confirmation (F3, F5: 12/14/18 lots) funded by day P/L.
Gap to the 20-trade goal: the 5 downloaded videos are exhausted; more recap videos need a new search (follow-up card).
