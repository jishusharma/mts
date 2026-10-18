# FABIO TRADE LEDGER (card fabio-trade-ledger) - current inventory: see "Audit correction H4 - inventory" at the end (2026-10-17); every paragraph below is a dated historical changelog, superseded where marked [L1]

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
Observed per event (not rules): F1 stop moved in steps behind structure as price fell and its TP read 25513.25 at t=210 then 25514.75 at t=330 (not fixed); F12 stop read ~25105.50 at t=3075 then 25089.75 at t=3100 (away from the entry); the earlier pass noted size 10 on the re-entry funded by day profit (not re-verified). No universal management rule is claimed [H5].

## 9IliXww64uM (read 2026-10-11 relay, sheets 00-06, ES, date UNKNOWN [H3])
Mostly talk: Schwab account page (value 217,392; equity curve jumped from ~61k on Nov 24 2025 to 210k on Jan 27 2026), ES 5-min and 1-min footprint charts with CVD/delta tables (no order labels),
and two pasted trade screenshots (file name 2026-01-30 214344 = screenshot creation time, not an entry date [H3]): F4a short 1 @ 6986.75, F4b short 1 @ 6977.5 (ES, 1 lot, no stops visible). Hand-drawn schematic at t=780 (balance -> failed breakout -> reversal).
No stop/TP prices on any frame, so no stop-width stat from this video. Ledger now 17 rows: 7 entries (F1, F2, F3a-c, F4a-b) plus management/exit rows.


## jasv3L-d8ZE (read 2026-10-11 relay, sheets 00-05, NQ-202512, $20/pt)
F5 short 15 @ 24960.28, stop 24969.75 (9.47pt = 0.038%, risk 2850$), TP 24910.25 (50pt = 5.3R = 15000$). Started the trade at Daily P/L -9577.50 (title: manage a -10.000$ session).
Management: stop tightened to 24961.50 then 24961.25 (above avg entry), scale-in to 18 lots avg 24959.18 (risk 720$), held through a pullback (open P/L 6629 -> 4559 -> 11129),
at t=630 stop trailed to 24925.00 (locks 12330$) and TP pulled 24910.25 -> 24917.00. Flat by t=660, Daily P/L +2331.50 (+11909$ on the trade). Exit fill not on a frame.

## Historical stats (SUPERSEDED by the H4 inventory; 8 entries, 5 videos; video count is the limit, teaching videos show ~1.6 trades each)
Markets: NQ 7 entries (F1, F2, F3a-c, F5; F2 levels approximate), ES 2 (F4a-b, 1 lot, no stops). Sessions: UNKNOWN per execution [H3]; see the H3 section.
Stop width on NQ (points / % of price): F1 15.75 / 0.061, F3b 8.88 / 0.036, F3c 3.38 / 0.014, F5 9.47 / 0.038 (and 2.07 / 0.008 after tighten). Median 9.2pt ~ 0.037%.
Target distance: 138pt (8.8R), 107pt (12R), 87pt (25.9R), 50pt (5.3R): R-multiples far above 3 on every labelled trade.
Management observed on the labelled trades (per event, [H5]): F1, F3c, F5, F6 stops were raised in steps while in profit; F3c and F5 TPs were pulled in at the events noted in their rows; F1 TP and the F12 stop moved otherwise (see Audit correction H5). F3/F5 size grew 12/14/18 lots; the "funded by day P/L" wording is not sourced for each.
Gap to the 20-trade goal: the 5 downloaded videos are exhausted; more recap videos need a new search (follow-up card).

## Find-more pass (card find-more-fabio-trade-recap-videos-yt-dl, relay 2026-10-11, JIS-NB) - PARTIAL, 9 entries now
Downloaded f398 720p (no en vtt exists for these): DyS79Eb92Ug (8500 s), Is1HvdfQm5c (8881 s), xUyqIjCfZzg (13777 s), Jpd96fLqr5M (1051 s), gLHd20jE8UQ (701 s).
9I5vTvwsMBk: read; f398 not available (downloaded f298 1280x720 60fps mp4, 970 s, 9 contact sheets cut at 30 s); no live trades found. t=0-140 shows a clip from Chart Fanatics interview where Fabio illustrates low-volume node on NQ (hypothetical sketch LONG 1 at 21805, stop 21797, target 21815-21830.25, not an executed live trade); t=140-970 is third-party commentary and TradingView chart review (SECONDARY_NOT_SOURCED [H6]). File on F: F:/MTS/data/fabio_videos/9I5vTvwsMBk.298.mp4 (recorded as row F-noTrade-9I5v).
- Jpd96fLqr5M (read sheets 00-05; 06-08 are talking head): one live NQ trade F6, long 4->6 lots avg 24914.3, stop 24883.50 (30.8pt = 0.124%), stop trailed 24896.50 -> 24914.50 -> 24954.50 -> 24966.50 -> 24971.00, TP 25001.00, exit fill not shown. Sheets 00-05 in F:/MTS/data/fabio_videos/sheets.
- gLHd20jE8UQ (read sheets 00,03): none shown, it is a MotiveWave big-trades (bubble) tutorial, no trade. SECONDARY_NOT_SOURCED [H6]: this is another presenter, not Fabio. He says 'What I run on ES' (t=420): Aggregate by Order ON, size filter 50; a separate slide footer attributes 'Fabio Valentini uses 30 to 40 on NQ' to Fabio. Neither is Fabio's own statement, so none of ES 50, NQ 30-40 or the aggregation mode is a layer parameter on this source.
- DyS79Eb92Ug, Is1HvdfQm5c, xUyqIjCfZzg: downloaded, NOT read (2.4 h, 2.5 h, 3.8 h = 280, 296, 459 sheets at 30 s). Need per-video cards with a search step first (transcript or 5-min sampling); see follow-up cards.

## DyS79Eb92Ug (read 2026-10-11 relay, JIS-NB, frames t=380-1100 + captions)
2.4 h interview (Tradezella journal, Alpha Capital sponsor); at t=380-1000 it replays the SAME live NQ session as Jpd96Fl qr5M (Daily P/L 10922 at start): F6 long 4->6 lots avg 24914.38, stop 24883.50 (-2460$ at 4 lots, 'risking 2,000'), TP 25001.00.
Outcome now resolved: stop trailed to 24971.00 (6780$ locked) at t=960, flat by t=1000 with Daily P/L 10922 -> 21290 (+10368$); a TP fill near 25001 is INFERRED, not shown [H2] (frames lowres/DyS79Eb92Ug_w2_00/01.jpg). Caption quotes: 'risk 2,000 to make eight' (t=772), setup = buyers protecting the gap/value-area low, 'tight stop' (t=821).
Captions F:/MTS/data/fabio_videos/DyS79Eb92Ug.txt (flattened, 3530 lines): other trade stories at t=1196 ('only risking 1,500'), 1289 ('risking $20 to make 3,000'), 2790 ('risking 800'), 6992 ('risking exactly 2,000'), 7598 ('10,000 risking 1,500'): each a candidate to read next (one window per session, tool: python -I scripts/dev/fabio_window_sheet.py <id> <t0> <t1> <step> <tag> writes lowres sheets; copy it into the tree if reused).
Status: still 9 entries (F1-F6 families); 20-trade goal not met, remaining unread: DyS79Eb92Ug t>1100, Is1HvdfQm5c (2.5 h), xUyqIjCfZzg (3.8 h).

## DyS79Eb92Ug t=1150-1350 (read 2026-10-11 relay, JIS-NB; sheets lowres/DyS79Eb92Ug_w3_00/01.jpg, step 25 s)
Two more trades in the same live NQ session as F6 (Daily P/L 21290 at start). F7 long 4 lots ~25022.75 (derived from risk), stop 25003.25 (19.5pt = 0.078%, risk 1560$), TP sell limit 25067.32 (2.3R);
stop raised to 25006.75, flat by t=1300 at about breakeven (Daily P/L 21290 -> 21252, -38$). F8 long 8 lots avg 25034.53 [H1-corrected from ~25032.5], stop 25021.75 (12.78pt = 0.051%, risk 2040$), TP not on frame.
Setup in his words: buyers 'protecting the level', squeeze against trapped sellers, stop sized to a fixed dollar risk (1,500-2,000). Management: stop to ~zero risk fast, scratch if the auction fails, re-enter ('can try another time').
Entry prices are derived (stop +/- risk/(qty*20)), flagged in the notes. Ledger now 11 entries (F1-F8). Still < 20: unread DyS79Eb92Ug t>1360 (captions: 2790, 6992, 7598), Is1HvdfQm5c, xUyqIjCfZzg.

## DyS79Eb92Ug t=1350-1600 (read 2026-10-11 relay, JIS-NB; sheets lowres/DyS79Eb92Ug_w4_00/01/02.jpg, step 25 s)
F8 (8 lots) was flat by t=1400 (Daily P/L 21252 -> 19131, -2121$; stop label 25021.75, risk 2040$); a stop fill is INFERRED, the extra 81$ is unattributed [H2]. Captions: 'we give back 2,500 ... auction is slow', 'this is the last trade for the day' (t=1410), yet he re-entered: F9 long 8 lots avg ~25034.25 [H1-corrected] with a 4-lot buy limit add, initial stop preview ~25019.44 [H1: not ~25010.4] then 25019.50 on 4 lots, flat by t=1550 for +259$ net (Daily 19390). F10 long 4 lots avg ~25040.00 [H1-corrected from ~25040.5] at t=1575, stop 25019.50 (-1600$), outcome not read.
Pattern: after a loss he re-enters the same protection-level squeeze three times in 5 minutes (F7 scratch -38$, F8 -2121$, F9 +259$): stop widths 12.75-21pt = 0.05-0.08%. Entry/stop values here are low-res reads, flagged approximate in the CSV.
Ledger now 14 entries (F1-F10 + sub-rows). Still < 20 trades: unread DyS79Eb92Ug t>1600 (captions 2790, 6992, 7598), Is1HvdfQm5c, xUyqIjCfZzg.

## DyS79Eb92Ug t=1575-1775 (read 2026-10-11 relay, JIS-NB; sheets lowres/DyS79Eb92Ug_w5_00/01.jpg, step 25 s)
F10 long (4 lots avg ~25040.00 [H1], stop 25019.5) scaled to 8 lots avg 25043.00, stop raised to 25038 then 25051.50 (+1360$ locked), sell LMT TP 25074.25 (5000$). Flat by t=1700, Daily P/L 19390 -> 24354 = +4964$ (a TP fill is INFERRED from the 5000$ label, not shown; cost split unknown) [H2]. Session sequence F7-F10: -38$, -2121$, +259$, +4964$. Stop 21pt (0.084%).
Ledger: 13 entry rows / 40 lines (F1-F10 incl. F3a-c, F4a-b). Still < 20: unread DyS79Eb92Ug t>1775 (captions 2790, 6992, 7598), Is1HvdfQm5c, xUyqIjCfZzg.

F11 (DyS79Eb92Ug t=2775-3000): NQ long 4 lots ~25104.75 after the squeeze above 25110, stop ~10pt (0.04%), scaled to 8 lots (stop 25094.25, 13pt = 0.052%), no TP reached, flat with Daily P/L 24354 -> 22239.02 = -2115$ (stop INFERRED; a further -46.02 follows to 22193 at t=3025, unexplained) [H2]. Ledger 14 trades / 43 rows. Still < 20: unread DyS79Eb92Ug t>=3025 (captions 6992, 7598), Is1HvdfQm5c, xUyqIjCfZzg.
F12 (DyS79Eb92Ug t=3025-3275): NQ long 6 lots, avg 25105.78 at t=3100 [H1-corrected], stop read ~25105.50 at t=3075 then 25089.75 at t=3100 (16.03pt) [H1: not 25085.75], scaled to 8 (stop 25098.50, 9pt) and 10 (avg 25108.50, stop 25098.75 at t=3150, TP sell LMT 25148.75 ~40pt [H1: not 25098.25 / 25140.75; a later frame shows 25098.25]); outcome not on those frames (t=3175 intro/ad, 3225+ talking head); later frames show flat with Daily P/L 22193 -> 20668 = -1525$, cause INFERRED [H2]. Ledger 15 trades / 46 rows. Still < 20: next window t=3275+, then Is1HvdfQm5c, xUyqIjCfZzg.
F13 (DyS79Eb92Ug t=3525-3775): NQ long 8->10 lots avg 25108.90 then 25108.05 [H1-corrected from ~25104], stop 25097.00 (11.9pt = 0.047%); the +2 order at 25104.75 is a buy add [H1], flat between t=3550 and 3575 (exit cause INFERRED): Daily P/L 20668 -> 17758 = -2910$ (20668-17758=2910), larger than the -1760 stop label [H2]; 2910-1760=1150, difference 1150 USD = NOT_IN_DATA (not slippage, cost or a discretionary fill: none proven; exit price stays '-', no fabricated fill; 8 covered vs 10 open [RV05 H3]). Then flat, no trade through t=3750 (the window ends t=3775; sheet shows 3725-3750 only). Sequence after F10 (+4964$): F11 -2115$, F12 -1525$, F13 -2910$, three chase longs near the 25110 prior high in ~9 chart minutes with stops 7-21pt. Ledger 16 trades / 52 rows (>= 20 trades not yet). Still < 20: next window t=3775+, then Is1HvdfQm5c, xUyqIjCfZzg.

F14 (DyS79Eb92Ug t=3775-4025): NQ long 8 lots ~25101.4, stop 25086.25 (~15pt = 0.060%), target label 25186.75 (+13600$), flat between t=3925 and t=3950 (stop INFERRED): Daily P/L 17758 -> 15147 = -2611$ [H2]. A 10-lot preview near 25109 at t=3800 is a preview, not a submitted order proven, and no fill was seen [H5]. Talking-head at t=3850. Flat t=3975-4000. Sequence F10 +4964, F11 -2115, F12 -1525, F13 -2910, F14 -2611: four chase longs near the 25110 prior high. Ledger 17 trades / 53 rows (>= 20 not yet). Next window t=4025+, then Is1HvdfQm5c, xUyqIjCfZzg.

## DyS79Eb92Ug t=8275-8493 (read 2026-10-12 relay, JIS-NB; sheets lowres/DyS79Eb92Ug_w30_00/01/02.jpg) - VIDEO FINISHED
Flat, no trade (Daily P/L 15147$ unchanged); chart at t=8300 shows low ~24880 then bounce ~24940; talking heads to the end (video ends ~8493). Ledger 70 rows.

## Historical stats paragraph (SUPERSEDED by the H4 inventory; was headed FINAL / "read end to end")
SUPERSEDED (H4): Filled trades: 14 (F1-F6 from 5 videos, F7-F14 from DyS79Eb92Ug). F15 (t=6775-7025) is a chart drawing, not a submitted order ("I will not execute it", DyS79Eb92Ug.txt:2854-2855) [H5]. Goal of >= 20 not reached: "all available" per the card (video count is the limit).
SUPERSEDED (H4): Markets: NQ 13, ES 1 (F4, 1 lot, no stops). Session/timezone: sourced per row only (H3 section), no universal US-cash claim.
SUPERSEDED (H4; the min 1.5pt came from the rejected F12 initial stop read): Stop width, 13 NQ stops with a read stop (points / % of ~25000): median 10.75pt = 0.043%, mean 13.6pt, min 1.5pt (0.006%), max 30.83pt (0.123%).
DyS79Eb92Ug day: F7-F10 won/ended +4964$ at F10, then F11 -2115$, F12 -1525$, F13 -2910$, F14 -2611$ (four consecutive same-range longs stopped), then flat for 4400 s; day ended Daily P/L +15147$.
Management as observed [H5]: per-event stop/TP/size changes are in the CSV management rows; no "stops only toward profit" or "TP pulled in late" rule is claimed (F12 stop moved away from the entry at t=3100).

Is1HvdfQm5c t=0-250 (w00, 25 s steps) read: black intro, Excalidraw board (agenda: Mental Models, Live Charting, Execution Method Trick), no chart, no trade. Ledger +1 no-trade row (71 lines), still 14 trades. Next: t=250+ (w01), one 250 s window per session; the Live Charting part is likely later, so a coarse 120 s sample of the whole video may find it faster.

## Minute timestamps (card fabio-ledger-minute-timestamps, 2026-10-14)
Replay-ready rows (date + minute, convertible to UTC): **0 of 18 entry rows**. Columns `entry_time_utc` + `entry_time_src` added to the CSV.
- Read this pass: F1 crop (no clock), fZlNGWvd2Ko sheets (no axis, no date), 9IliXww64uM t=630 (only the pasted screenshot's file name 2026-01-30 214344 = save time, not fill time), DyS79Eb92Ug t=1150-1225 (axis minutes 15:55-15:56 chart time, no date).
- DyS79Eb92Ug / Jpd96fLqr5M (F6-F15) trade NQ-202512, so the session is 2025-09..12, not "2026" as the date column said before the H3 correction; minutes are on the time axis but the day is not on screen. Dating it needs a price-path match (F6 24914 -> TP 25001, F11-F14 25095-25110 range) against NQ 1m history: follow-up card fabio-session-date-price-match.
- Chart time zone: the axis puts the US open at 15:30, i.e. CET/CEST; UTC needs the date (DST), so no UTC value is written without it.
- Times never come from transcripts (card rule); every unknown carries its reason.

## Update 2026-10-16 (fabio-transcribe): Is1HvdfQm5c read from audio
D2 was flipped to YES by the operator (OPERATOR_DECISIONS q-fabio-asr-d2). Is1HvdfQm5c now has a canonical ASR transcript (raw_transcripts_canonical/Is1HvdfQm5c_raw.txt, faster-whisper small.en) and a full V2 extract (extracts/v2/fabio/Is1HvdfQm5c_v2.md, 333 decision rows, 9 trade blocks). Result for the ledger: the session is mostly teaching and viewer Q&A; it holds NO confirmed live Fabio position with a stated entry and stop (one live order, 'the last sniper', was never filled). No row is added to the 14-trade ledger from it. xUyqIjCfZzg: ASR transcription is running (research/fabio_asr_2026-10-16/ASR_RUN.md); the frames-only reading of these two videos is superseded, not needed.

## Audit correction H1 (card fabio-audit-20261013-prices, 2026-10-17)
Source: layer_lab/reports/2026-10-13_lab-audit-fabio-ledger-frames.md H1 row (full-res pixel reads) applied to the CSV rows below. The old approximate values are superseded; nothing here is a new frame read.
| Row | Old | Corrected | Check |
|---|---|---|---|
| F8 entry | ~25032.5 (derived) | 25034.53 avg (w3_01 t1325) | 25021.75+2040/(8*20)=25034.50 |
| F9 initial stop | ~25010.4 | ~25019.44 preview, then 25019.50 | width ~14.75pt |
| F10 entry | ~25040.5 | ~25040.00 avg (w4_02 t1575) | width ~20.5pt |
| F12 entry/stop (t3100) | ~25107 / ~25085.75 | 25105.78 / 25089.75 | width 16.03pt |
| F12-m2 (t3150) | ~25100 / 25098.25 / ~25140.75 | 25108.50 / 25098.75 / 25148.75 | later w9_00 stop 25098.25 not backdated |
| F13 entry | ~25104 | 25108.90 avg | 8 x 25108.90 + 2 x 25104.75 = 10 x 25108.07 |
| F13-m1 entry | ~25105 | 25108.05 avg | matches the line above |
| F13 +2 LMT 25104.75 | sell partial | buy add | green order |
UNRESOLVED (H1): the F12-m2 label STP -2050$ ties to 25098.25 (10 x 10.25 x 20), not 25098.75 (1950$); F12 -1860$ and F13 -1520$ cash labels do not tie to the corrected averages. Labels are kept as observed; platform accounting is not reconciled (audit M2). Stop widths for F9, F10, F12, F13 in the old stats above are stale; H4 recomputes them.

## Audit correction H2 (card fabio-audit-20261013-exits, 2026-10-17)
Rule from the audit: a flat position and a Daily P/L delta are observations; the exit price, whether a stop or a TP filled, and the slippage/cost share are INFERRED or UNKNOWN until a fill record or a continuous frame sequence shows them. Exit rows F3c-x, F5-x..F14-x are relabelled `*_cause_inferred` / `*_cause_unknown` and their notes keep only the observed numbers.
- F6 +10368 and F10 +4964 are visible differences only; exact fills are absent.
- F12 -1525 is smaller than the displayed -2050 stop risk; F13 -2910 is larger than the -1760 stop label with 8 covered vs 10 open (20668-17758=2910, 2910-1760=1150; difference 1150 USD = NOT_IN_DATA, exit price stays '-', exit cause INFERRED, no fabricated fill [RV05 H3]). Unreconciled, no transaction list exists in the repo.
- Omitted interval: Daily P/L 22239.02 (t=3000) -> 22193 (t=3025) = -46.02 between the F11 and F12 frames, unexplained.
- Interval totals (M4): F10 +4964 and F11 -2115 sum to +2849; F7-F10 sum to -38-2121+259+4964 = +3064; neither is the day P/L.
UNRESOLVED (H2): the exit fill prices and causes, the 81$ (F8), 36$ (F10), 35$ (F11) label differences and the -46.02 need a fill/transaction record that is not in the repo.

## Audit correction H3 (card fabio-audit-20261013-dates, 2026-10-17)
The date column no longer carries any 2026 or month value that no source states. Every row is `UNKNOWN (...)` with the partial evidence kept separate: a contract suffix (NQ-202512) is not a date; the F4 screenshot file name is the save time, not the entry time; recording, upload, screenshot and trade dates are not interchangeable.
| Evidence | Where | Used for |
|---|---|---|
| "30 of December", tentative ("if I'm not wrong"), no year | 0jM5Y31YJak.en.vtt:826-842 | F2 rows, partial only |
| "central European time" before the session | 0jM5Y31YJak.en.vtt:82-90 | F2 timezone |
| "Today it's day 15 of October", year absent; New York session begins | DyS79Eb92Ug.txt:66-81 | DyS79Eb92Ug rows (F7-F15, no-trade rows); F6 shares the session per the earlier pass |
| chart axis puts the US open at 15:30 (CET/CEST) | 2026-10-14 minute-timestamp pass (below) | DyS/Jpd chart clocks, no UTC without a date |
Rows with no date and no zone evidence (F1, F3, F5, F4, Is1H) stay UNKNOWN; the earlier "NY session" time labels were removed from F3 and F5. Link exact frame clock, date and timezone per execution before any replay or design/check split.
UNRESOLVED (H3): the calendar date of every execution (year absent everywhere in the repo sources read); DyS is Oct 15 of an unstated year; the F1 chart-clock 02/12 reading was not re-verified (no frame re-read in this card).

## Audit correction H4 - inventory (card fabio-audit-20261013-counts, 2026-10-17)
Definitions. PARENT TRADE = one position from flat to flat (scale-ins and re-sizing inside it are fills/management of the same parent). FILL = an entry row (a label with a quantity and price). MANAGEMENT = a `-m` row (stop/TP/size change on an open parent). FLAT-STATE OBSERVATION = an `-x` row (position 0 and Daily P/L, not an exit fill, see H2). TEACHING EXAMPLE = a row from a commentary video with approximate levels (F2). A drawing is none of these.

| Parent | Market | Member entry rows | Initial stop width used | Status |
|---|---|---|---|---|
| P1 | NQ | F1 | 15.75 pt = 0.061% (row F1) | frame-read entry/stop/TP |
| P2 | NQ | F2 | none read | PARTIAL: teaching example, levels approximate; transcript says 3 positions closed (0jM5Y31YJak.en.vtt:1026-1058) and 5+ more with another later (:1234-1258): one row cannot represent them |
| P3 | NQ | F3a, F3b | 8.88 pt = 0.036% (row F3b) | F3b scales F3a (no flat frame between); stop read only on F3b |
| P4 | NQ | F3c | 3.38 pt = 0.014% (row F3c) | re-entry after the first leg closed (flat frame at t=180 per note) |
| P5 | ES | F4a, F4b | none read | UNRESOLVED grouping: two screenshot fills, order -1@6977.5 is left of -1@6986.75, continuity not shown; counts as 1 or 2 parents; no stop |
| P6 | NQ | F5 | 9.47 pt = 0.038% (row F5) | frame-read; scaled 15 -> 18 within the position |
| P7 | NQ | F6 | 30.83 pt = 0.124% (row F6) | frame-read; scaled 4 -> 6 within the position |
| P8 | NQ | F7 | 19.50 pt = 0.078% (row F7) | entry derived from risk (approximate) |
| P9 | NQ | F8 | 12.75 pt = 0.051% (row F8) | frame-read average |
| P10 | NQ | F9 | 14.81 pt = 0.059% (row F9) | frame-read average ~ |
| P11 | NQ | F10 | 20.50 pt = 0.082% (row F10) | frame-read average ~ |
| P12 | NQ | F11 | 10.00 pt = 0.040% (row F11) | entry and stop both approximate (~) |
| P13 | NQ | F12 | 16.03 pt = 0.064% (row F12) | frame-read average and stop at t=3100 |
| P14 | NQ | F13 | 9.50 pt = 0.038% (row F13) | frame-read average |
| P15 | NQ | F14 | 15.13 pt = 0.060% (row F14) | frame-read |

Excluded from every count: F15-draft-6975-7025: drawing (DyS79Eb92Ug.txt:2854-2855), not a submitted order, no fill.

Counts (replace the earlier "14 filled trades, 13 NQ / 1 ES" and "all available"): 15 parent rows listed = 13 with a frame-read initial stop (NQ), 1 partial teaching example (P2, NQ), 1 unresolved ES grouping (P5: 1 or 2 parents). So NQ frame-read parent trades = 13; ES = 1-2 parents with no stop; total 14 to 15 parents.
Row classes in the CSV (73 rows): drawing 1; fill (entry row) 17; flat-state observation (exit) 13; management observation 21; no-trade window (sampled frames only) 21.

Stop-width statistic (initial stop, 13 NQ parents with a read stop; entry/stop = first number of the CSV cells, so F7 and F11 are approximate): median 14.81 pt, mean 14.35 pt, min 3.38 pt, max 30.83 pt.
The old "min 1.5pt (0.006%)" came from the F12 initial stop read (~25105.50 vs ~25107) that the audit rejects (F12 stop is 25089.75 at t=3100); tightened management stops (F5 2.07 pt after the tighten, F12-m1 8.83 pt) are management rows, not initial stops, and are not in this statistic. Members of the statistic: F1=15.75, F3b=8.88, F3c=3.38, F5=9.47, F6=30.83, F7=19.5, F8=12.75, F9=14.81, F10=20.5, F11=10.0, F12=16.03, F13=9.5, F14=15.13.

Coverage is PARTIAL, not "all available": 8CWKfoSJu3c, fZlNGWvd2Ko, jasv3L-d8ZE, Jpd96fLqr5M sheets read; 0jM5Y31YJak sheets 00/03/04 were unread in the first pass; 9IliXww64uM has no stop/TP labels; DyS79Eb92Ug read in 250 s windows where each no-trade window cites only 2-4 sampled frames, so "no trade" holds for the sampled frames only; Is1HvdfQm5c has frames to t=500 and an ASR extract with no confirmed live position; xUyqIjCfZzg (3.8 h) is unread in this ledger; 9I5vTvwsMBk downloaded (f298 720p60) and read (t=0-140 interview clip has hypothetical trade sketch only, rest is 3rd-party review; no live Fabio trade). F2 omits at least the positions named in 0jM5Y31YJak.en.vtt:1026-1058 and 1234-1258.
UNRESOLVED (H4): the P3/P5 grouping rule for F3b/F4 (no flat frame between fills), the F2 position count and prices, and the unread videos; counts above are a definition applied to the current rows, not ground truth.

## Audit correction H5 (card fabio-audit-20261013-rules, 2026-10-17)
Rule: describe each observed change per event; distinguish preview, drawing, submitted order and fill; reserve universal rules for direct sourced statements (none are claimed here).
- F1: TP read 25513.25 (sheet01 t210) then 25514.75 (sheet02 t330): contradicts "fixed TP".
- F12: stop read ~25105.50 (t3075) then 25089.75 (t3100): contradicts "stops move only toward profit".
- F11: the two +2 adds at t2825/2850 are green STP orders, not LMT; the sell order is a target preview.
- F15 and the 7025-7275 window: a drawing the speaker will not execute (DyS79Eb92Ug.txt:2854-2855); hypothetical, not a submitted ticket.
UNRESOLVED (H5): the F1 sheet01/sheet02 TP reads and the F11 STP typing are the audit's reads; no frame was re-read in this card.
The H4 inventory above is generated by `python MyTradingSys/research/fabio_transfer/ledger_stats.py` (ledger_stats.py) from the CSV; test_ledger_audit.py asserts the text equals its output.

## Audit correction H6 (card fabio-audit-20261013-attribution, 2026-10-17)
gLHd20jE8UQ (sheet 03, t=420) is a different presenter's MotiveWave tutorial: "What I run on ES" (filter 50) is his own setting, and the NQ 30-40 figure is a footer claim about Fabio by that presenter. Status SECONDARY_NOT_SOURCED.
Fabio's own words exist elsewhere in the repo and are the source to cite instead: raw_transcripts_canonical/DyS79Eb92Ug_raw.txt:681-683 ([27:14]-[27:19]) answers "What was the minimum contract?" with "Always the same. It's 30 contracts" and "If you are in London, I use 20" (ASR turn markers carry no speaker names; the answer follows the interviewer's question to the trader). That sources NQ 30 contracts (London 20) as SOURCED; it does not source ES 50, "30 to 40", or aggregation mode.
UNRESOLVED (H6): speaker identity of the DyS79Eb92Ug_raw.txt:681-683 answer is inferred from the turn order, not labelled; a Fabio quote for ES 50 and for the aggregation mode does not exist in the files read.

## Card fabio-ledger-recompute-entry-from-stp-la (2026-10-17)
Rule: entry = label stop + |STP label $| / (label lots x 20 $ per point). Applied to the four rows whose STP label is on frame. The displayed frame-read averages stay in each CSV cell.

| Row | STP label | Stop used | Recomputed entry | Displayed average (kept) |
|---|---|---|---|---|
| F8 | STP -8 -2040$ | 25021.75 | 25034.50 | 25034.53 (w3_01 t1325) |
| F12-m2 | STP -10 -2050$ | 25098.25 (the H1 tie, not the row stop 25098.75) | 25108.50 | 25108.50 (t3150) |
| F13 | STP -8 -1520$ | 25097.00 | 25106.50 | 25108.90 (w9_01 t3375) |
| F13-m1 | STP -8 -1760$ | 25097.00 | 25108.00 | 25108.05 (t3400) |

Consequences: the F13 initial stop width is now 9.50 pt (was 11.90 pt), so the H4 statistic above moves. The F13 label (-1520$ on 8 lots = 9.50 pt) does not match the frame average 25108.90 (11.9 pt, which would be -1904$), so the entry for F13 is UNRESOLVED between the label and the frame read (H1). F13-m1 uses the label's own 8 lots, not the row's 10. F8 width is 12.75 pt (was 12.78).
Tests: test_ledger_audit.py asserts the new values for F8, F13 and F13-m1 (the assertions failed before this change).

## Card fabio-ledger-replace-date-2026-with-unkn (2026-10-17)
Checked, no edit needed. Every date cell for the Jpd96fLqr5M and DyS79Eb92Ug rows (F6 to F15 and the no-trade rows) already reads UNKNOWN (...) with no 2026 value. The only 2026 strings left in the CSV sit inside UNKNOWN reasons or screenshot file names (F4a, F4b).

## RV05 H1 date evidence (card rv05-h1-date-evidence, 2026-10-17)
Scope: CSV lines 25-71 (47 rows). Count of non-UNKNOWN date fields on these lines: 0 (checked before and after; no CSV edit needed, the earlier card fabio-ledger-replace-date-2026-with-unkn already set them).
Rule: execution date is UNKNOWN unless a same-session source is on screen. A 2026 file name, a 2026 upload or review year, and a contract name such as NQ-202512 are not session dates.
Rows: F6, F6-m1, F6-m2, F6-m3, F6-x, F7, F7-m1, F7-x, F8, F8-x, F9, F9-m1, F9-x, F10, F10-m1, F10-x, F10-z, F11, F11-m1, F11-x, F12, F12-m1, F12-m2, F12-x, F13, F13-m1, F13-x, F-noTrade-3575-3750, F14, F14-x, F-noTrade-4025-4275, F-noTrade-4275-4525, F-noTrade-4775-5025, F-noTrade-5025-5275, F-noTrade-5275-5525, F-noTrade-5525-5775, F-noTrade-5775-6025, F-noTrade-6025-6275, F-noTrade-6275-6525, F-noTrade-6525-6775, F15-draft-6975-7025, F-noTrade-7025-7275, F-noTrade-7275-7525, F-noTrade-7525-7775, F-noTrade-7775-8025, F-noTrade-8025-8275, F-noTrade-8275-8493.
Finding (RV05 report, H1, HIGH, CONFIRMED for the 47-row unsupported-date problem): the DyS frames show NQ-202512 (CSV lines 29-71 carry that contract); the Jpd sheet does not expose its contract header. Recording or review date is kept separate from execution date. The stronger claim that every source frame proves a pre-2026 date is NOT_IN_DATA.
Source: MyTradingSys/research/layer_lab/reports/2026-10-13_rv05-fabio-ledger-frame-pass.md (H1 row, line 34; detail line 44).
