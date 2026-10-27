# TOM TRADE LEDGER - REPAIRED 2026-10-12 (cards tom-ledger-canonical-identities, -instrument-identity, -time-provenance, -management-provenance)
Source of every repair: audit report `research/layer_lab/reports/2026-10-12_lab-audit-tom-ledger-frames.md` (FIX-FIRST). No frame was re-audited here; no value was invented. Evidence classes: frame-observed / trader-quoted (AI-translated caption) / inferred. Unresolved items are written NOT_IN_DATA in the CSV columns `date_time_status`, `evidence_unresolved`.

## Current counts (supersede the 10-trade/NOT DONE header and the "14 trade ids" totals below)
- 39 rows preserved (37 previous + 2 losing first attempts T1-a0 and T7-a0), all IDs and frame pointers kept. 14 headline IDs = **12 candidate trade groups** (see `TOM_LEDGER_CANONICAL_GROUPS.csv`), not 12 certified executions: no fill price, execution minute or timezone is certified for any group.
- Duplicate aliases: T9 -> T4 (UOBgXV20yCM, 23887/23857/23962), T10 -> T6 (zQTbdEweG3c, 25344), T3-s -> T3, T3b-s/T3b-r -> T3b (second video SANOimk8M9o).
- Losing first attempts (card `tom-ledger-add-the-losing-first-attempts`, 2026-10-19): added rows `T1-a0` (S1 n7ZSkjb7JXs:31-33, pre-trade stop loss) and `T7-a0` (S6 l8RZrBfzvp4:175-177, pre-session stop, losing 1R) with `row_kind=ATTEMPT_LOST`. S2 T2 first entry was already row T2 (stopped out at T2-x). S3/T5 losing attempts have no frame fills (spec section 3).
- Treatment in `backtest/tom_dax_recall.py`: V2 group recall targets are constructed from `ENTRY` rows only (`row_kind == "ENTRY"`), so `row_kind=ATTEMPT_LOST` does not count as a recall target; it ensures backtests count every attempt to prevent survivorship bias.
- Do not use 14 / 12 / 7 / 4 as a recall denominator. Every inspected episode is EXPOSED for the holdout split; this repair does not touch the split manifest.

## What changed (CSV)
- New columns appended: canonical_id, row_kind, chart_symbol_observed, executed_contract, multiplier_tick_ccy, date_time_status, evidence_unresolved, prior_exposure.
- T5 family: chart header reads Continuous(FDXM)@EUREX (_0520.jpg) while the ledger says FDAX; executed contract/multiplier/tick/currency are NOT_IN_DATA and no monetary risk may be computed from them.
- T11: date no longer "trade day = recording day"; screenshots are titled 31.08, taskbar 01-Sep: UNRESOLVED (31-Aug likely, unverified).
- T7: TP 6767.25 is frame-observed (was n/s). T3-s-p1: SL 24220 removed (unsupported); observed states 24265 then 24257. T3b-x: pointer moved to sheets/ujedEcmvBMk_02.jpg cells t=460-520. T5-m1: price 24493 (not ~24650); breakeven stays inferred. T12-m1: SL 25097 at _0900 then 25038 at _0990 (taskbar 08:54). T2b-p1/T1-m1/T1-p1: rounded/derived/position-vs-bracket qualifiers added.
- TIME PROVENANCE (card tom-ledger-time-provenance, 2026-10-12): new CSV columns recording_date_observed, trade_date_status, trade_date_inferred, execution_minute_status, time_evidence_type, tz_status separate recording clock / chart / execution time. Every row: execution minute = UNKNOWN (no frame shows a fill or modification minute). T4/T9 are one trade (18-May INFERRED from caption 'yesterday', not observed); T6/T10 one trade, trade date NOT_IN_DATA; T11 31.08 chart title vs 01-Sep recording = CONFLICT, 2026-08-31 likely but unverified; T7 taskbar 19-Mar is recording clock; T12-m1 SL 25097 at t=900 then 25038 at t=990 (taskbar 08:54), modification minute unknown. CET/CEST in time_local is a typed label only (chart/recorder TZ NOT_IN_DATA). Date column values unchanged; no split created, no holdout read. Prior exposure stays EXPOSED for all rows (hand to the split owner tom-holdout-clean-split: group episodes by canonical id, not by row).
- DATE COLUMN (card rv-fix-tom-ledger-date-column, 2026-10-13, RV01 D4/F1/F2): `date` = observed trade date or empty. No row has an observed trade date (no dated order frame), so `date` is empty on all 37 rows. Former `date` values moved: ASSUMED-same-day rows -> `trade_date_inferred` (status text still says ASSUMED); T11/T11-x `trade_date_inferred` = 2026-08-31 (status stays CONFLICT/UNRESOLVED); every blanked cell kept in new column `date_legacy_unverified` (ISO only; T5 2026-05-19, T6 2026-06-02, T10 2026-06-08 are contextual, not trade dates). One inferred date per canonical group; T5/T6/T7 groups have none. TOM_LEDGER_CANONICAL_GROUPS.csv gained `trade_date_observed`, `trade_date_inferred`, `date_candidates_to_exclude` (union of recording, inferred and legacy dates: the list a holdout split must drop, each +-1 trading day). Check: `python scripts/dev/tom_ledger_dates.py check` (0 violations; 46 before).
- Taskbar clocks are recording/observation times, never execution times. T3b-r "after partial" does not exclude the trader-stated stop-out (ujedEcmvBMk.txt:142-149).

Original header (obsolete, kept for history): TOM TRADE LEDGER (card tom-trade-ledger) - PARTIAL, 10 trades / 19 rows, 2026-10-11
Status: NOT DONE (target >= 30 or every trade in every available video). 7 videos are on F:/MTS/data/tom_videos (l8RZrBfzvp4 now downloaded, video-only f398 mp4; no ffmpeg merge).
Frame contact sheets (30 s spacing, 6 per sheet) are in F:/MTS/data/tom_videos/sheets (36 sheets); only l8RZrBfzvp4 sheet 00 has been read this session.
Rows T1-T6 come from RECALL_DAX.md s1 (frames read earlier). T7 is new: ES short 6806.25, stop 6812.25 (frame l8RZrBfzvp4_0100.jpg, zoomed labels + taskbar clock 19.03.2026 08:48).
Family counts so far: spike fade (T1,T2,T3,T5,T6,T7) 6; re-entry (T3b) 1; gap pullback (T4) 1. Only ~1-2 trades per video were seen: reaching 30 may be impossible from these 7 videos (honest outcome: every trade in every available video).
Remaining: read sheets of k0zm5NYn0IQ (10), n7ZSkjb7JXs (6), UOBgXV20yCM (5), T6hDJcHrVBM (4), ujedEcmvBMk (4), zQTbdEweG3c (4), l8RZ 01-02 (2) for further trades and management actions (stop moves, partials, exits).


## Update 2026-10-11 ~00:00Z (relay via cron, JIS-NB): k0zm5NYn0IQ sheets 00-09 all read
- T2 CORRECTED: order labels at t=280 read short 1 @25318, SL 25338, TP 25196 (zoom k0zm5NYn0IQ_0280_crop.png). RECALL_DAX's 25343 is a MISMATCH
  (it sits in the later re-entry zone). RECALL_DAX T2 should be re-read against these labels before tom-encode-spike-fade uses it.
- New trade T2b (re-entry after stop, same morning 2026-01-08): short 2 @25341 at ~09:35 CET, SL 25363, TP 25199.
- Management seen in one trade, all from order labels + taskbar clock: scale-in on both entries (T2 1->2 lots; T2b 2->3 lots, 3rd ~25324),
  stop tightened 25363 -> 25349 -> 25344, two one-lot partials (FIFO), last lot with stop moved into profit (25310, entry 25324) at 10:53 CET.
  Final exit is not in the video. T2's exit is INFERRED (stop 25338), its fill is not shown.
- Stop/target geometry seen on the platform panel: SL 20-22 points, TP 120-142 points (R:R ~6) on entry; Tom draws risk/chance boxes
  and a hit-rate vs required-CRV table (t=1360) and computes 55/15 = 3.66 on screen (t=1420).
- Family counts now: spike fade 6 (T1,T2,T3,T5,T6,T7); re-entry after stop 2 (T3b,T2b); gap pullback 1 (T4). Management actions:
  scale_in 2, stop_tighten 3, partial 2+ (T1,T5,T2b x2), stop_to_profit 1, stop_out 2 (T3, T2 inferred).
- Remaining sheets: n7ZSkjb7JXs (6), UOBgXV20yCM (5), T6hDJcHrVBM (4), ujedEcmvBMk (4), zQTbdEweG3c (4), l8RZ 01-02 (2).
  Frame grabber used: grab.py pattern (cv2, CAP_PROP_POS_MSEC, crop x2 cubic); videos are 1280x720, sheet cells are 960x540 (scale 4/3).

## Update 2026-10-11 ~00:40Z (relay via cron mts-dispatcher-night, JIS-NB): n7ZSkjb7JXs sheets 00-05 all read
- Video is edited (t=10 intro clip shows 08:59, t=220 shows 08:26; ends ~t=905 at 09:01 CET, 22.12.2025). Platform shows FDAX, GC, NQ, ES panels.
- T1 management (FDAX, from order labels + panel): scale-in to 4 lots avg 24480.25 (t=580; RECALL_DAX had 3) -> partial 1 at 08:52 (-3 @24480.0)
  -> TP pulled 24422 -> 24426 (t=730) -> partial 1 at 09:01 (-2 @24479.5), stop 24485 -> 24484, TP removed, order dragged to ~24456. Final 2 lots' exit not shown.
- NEW T8: GC gold short 1 @4446.8, SL 4456.1 (93T), TP 4415.1 (317T, R:R 3.4), at the top of a steep rally; open before 08:26 (entry not shown), still open at 09:01, exit not shown.
  Family spike_fade_candidate (the entry moment is not on screen).
- Family counts now: spike fade 6 (T1,T2,T3,T5,T6,T7) + 1 candidate (T8); re-entry after stop 2 (T3b,T2b); gap pullback 1 (T4). 10 trades.
  Management actions: scale_in 3, partial 4 in rows (T2b x2, T1 x2) + T5 noted, stop_tighten 4, tp_tighten 1, tp_removed 1, stop_to_profit 1, stop_out 2.
- Check: every frame path in all 19 rows exists (scratch append script prints missing = 0). Rows T1-p1, T1-p2, T8 re-read from the zoomed crops while writing them.
- Remaining sheets: UOBgXV20yCM (5), T6hDJcHrVBM (4), ujedEcmvBMk (4), zQTbdEweG3c (4), l8RZ 01-02 (2).

## Update 2026-10-11 ~05:00Z (relay via cron mts-dispatcher-night, JIS-NB): UOBgXV20yCM sheets 00-02 read
- One trade only (teaching video, hindsight chart): T9 FDAX long 1 @23887, SL 23857 (30pt), TP 23962 (75pt), CRV ~2.5; zoom F:/MTS/data/tom_videos/frames/UOBgXV20yCM_0250_lab.png.
  Taskbar clock 19.05.2026 07:12 is the recording time, not the trade time; chart header 2026-05-15 is the volume-profile history. Entry moment and exit fill are NOT shown (T9-x exit inferred from price 24014 on later chart).
- Family: breakout_pullback_teaching (new family, 1). 11 trades / 21 rows in the csv; every frame path exists.
- Remaining sheets: UOBgXV20yCM 03-04 (2), T6hDJcHrVBM (4), ujedEcmvBMk (4), zQTbdEweG3c (4), l8RZ 01-02 (2).

## Update 2026-10-11 ~01:30Z (relay via cron mts-dispatcher-night, JIS-NB): T6hDJcHrVBM sheets 00-03 all read
- Only one trade in the video: T5 (ledger label FDAX; chart header observed `Continuous(FDXM)@EUREX` at _0520.jpg, executed contract/multiplier/tick/currency NOT_IN_DATA, instrument-identity audit 2026-10-12; 2026-05-19 open-range spike fade). Labels re-read at t=430 (zoom T6hDJcHrVBM_0430_crop.png): -3 @24690, SL 24753, TP 24184. MATCH with RECALL_DAX.
- Management (new rows T5-m1, T5-p1, T5-a1): stop to breakeven 24690 by t=520 (SL label stacked behind the position tag, no printed value);
  one-lot partial by t=550 while price tags VWAP 24425/24435 (fill price not shown); t=610 hand-drawn "SL 650" above the broken range low. Final exit of 2 lots NOT shown.
- Sheets 00-01 are teaching (BTC daily profile, FDAX TPO "Openrange" profiles 05-11..05-19), no orders.
- Family counts unchanged: spike fade 6 + 1 candidate (T8); re-entry 2; gap pullback 1; breakout pullback teaching 1. 11 trades / 24 rows; every frame path exists.
  Management actions now: scale_in 3, partial 5 rows, stop_tighten 4, stop_to_breakeven 1, stop_to_profit 1, tp_tighten 1, tp_removed 1, stop_out 2.
- Remaining sheets: UOBgXV20yCM 03-04 (2), ujedEcmvBMk (4), zQTbdEweG3c (4), l8RZ 01-02 (2).

## Update 2026-10-11 ~06:30Z (relay via cron mts-dispatcher, JIS-NB): ujedEcmvBMk sheets 00-03 all read
- Video is the 2026-05-12 FDAX day (taskbar 12.05.2026); sheets 00-01 teaching (weekly profile, 'W' drawing), 02 re-entry review, 03 talking head + outro.
- T3 corrected from zoom F:/MTS/data/tom_videos/frames/ujedEcmvBMk_0070_crop.png: -2 @24229, SL 24265 (RECALL_DAX 24257 = MISMATCH), TP 24111. The old 'stopped out' note is not supported by any frame: by t=250 the position is -1 (T3-p1, one lot closed, fill not shown).
- T3b re-read (t=310 crop): -1 @24216, SL 24236, TP 24111, labelled 'reentry' by Tom: MATCH. Outcome of the re-entry NOT shown (T3b-x).
- New management action: partial_exit at the 'Low Volume' node (T3-p1), re-entry after partial (not after stop). 11 trades / 27 rows, every frame path exists.
- Remaining sheets: UOBgXV20yCM 03-04 (2), zQTbdEweG3c (4), l8RZrBfzvp4 01-02 (2).

## Update 2026-10-11 ~02:30Z (relay via cron mts-dispatcher, JIS-NB): zQTbdEweG3c 00-03, UOBgXV20yCM 03-04, l8RZrBfzvp4 01-02 read
- All 36 sheets are now read. New trade T10 (zQTbdEweG3c t=310, zoom ..._0310_crop.png): FDAX short 1 @25344 (position tag), spike to ~25400 then 25230; hand-drawn SL above the spike at t=370.
  Entry/stop order/exit NOT shown; recording date 2026-06-08 (taskbar), trade day unlabelled. Family spike_fade_candidate.
- T7 management (l8RZ t=190 zoom): -1 @6806.25, SL 6812.25 ($-300), TP 6767.25 ($+1950) -> TP 6771.25 ($+1750) by t=220, SL label gone. Exit not shown.
- UOBgXV20yCM 03-04 and zQTbdEweG3c 00,02,03 are teaching/outro: no orders.
- Ledger 12 trade ids (T1-T10 incl. T2b, T3b) / 29 rows. Every trade visible in all 7 videos is now listed; target >= 30 NOT reachable from these videos
  (~1.7 trades/video; most recaps show the position tag only). Honest outcome per the card: "every trade in every available video if fewer".
  Family counts: spike fade 6 + 3 candidates (T8,T10 + T9 teaching breakout pullback); re-entry 2; gap pullback 1.
  More trades need more videos (card step 1: find further recap videos): file a follow-up card.

## Update 2026-10-11 ~15:00Z (relay via cron mts-dispatcher, JIS-NB): card find-more-tom-trade-recap-videos-yt-dlp-
- NEW COUNT: 14 trade ids / 37 rows (was 12 / 30). Three new video ids downloaded (f398 video-only, 1280x720; 30 s sheets in F:/MTS/data/tom_videos/sheets, frames in .../frames). English captions hit HTTP 429, so no .vtt for these three (frames only).
- liEJMfE_PXg (2026-09-01): NEW T11 FDAX short 2 @26444, SL 26490, TP 26286 (3.4R), then "Ziel erreicht" (T11-x, fill not shown).
- ZZeET7ng1nk (2026-07-14): NEW T12 FDAX short 1 @25116, SL 25139, TP 24974 (6.2R); T12-m1 stop moved to 25038 (78pt locked); exit not shown.
- SANOimk8M9o (2026-05-12): SAME trade as T3/T3b (second video of it), not a new trade. Rows T3-s, T3-s-p1, T3b-s confirm the corrected T3 values (SL 24265) and add that the remaining lot's stop went to 24220 after the first lot closed.
- Queries tried (yt_dlp ytsearch25): "World Champion LIVE trade DAX", "Trading World Champion DAX live trade recap", "World Champion trades DAX short stop target explained". Channels: Tom Vorwald (DE) and Tom Vorwald EN. Not downloaded (no trade recap on screen per title, explainers): K8qtT2_axPo, WSCIURybK3U, VumVuGnCcFM, jXR1afMy-3o.
- Still unread-by-search: German-channel titles are not English; a query for "Tom Vorwald Live Trading DAX" on the DE channel playlist may yield more (follow-up). Families so far: spike fade 8 (T1,T2,T3,T5,T6,T7,T11,T12), unchanged others.
- Check run: every frame path in the 7 new rows exists (append script printed missing = 0).
