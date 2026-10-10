# TOM TRADE LEDGER (card tom-trade-ledger) - PARTIAL, 9 trades / 14 rows, 2026-10-11
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
