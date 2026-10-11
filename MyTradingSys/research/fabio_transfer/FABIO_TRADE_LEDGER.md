# FABIO TRADE LEDGER (card fabio-trade-ledger) - Status: NOT DONE, F1 and F3 read (3 entries), F2 approximate

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

Next session: read 0jM5 00/03/04, then 9Ili and jasv sheets; add rows with frame evidence; target >= 20 or all available; then stop-width/session stats and `tasks.py done fabio-trade-ledger`.
