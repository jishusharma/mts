# ASR extraction addendum: Fabio long live sessions (2026-10-16)

Applies the existing V2 method (`research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md` + `EXTRACTION_METHOD_V2_FABIO.md`) to the two ASR transcripts
`raw_transcripts_canonical/Is1HvdfQm5c_raw.txt` (2.5 h) and `raw_transcripts_canonical/xUyqIjCfZzg_raw.txt` (3.8 h). A 2-4 h session is too long for one
reader pass, so each video is read in parts of about 40 minutes by independent workers and the part files are merged into ONE extract per video:
`extracts/v2/fabio/<id>_v2.md`. This file lists only what differs from V2. Everything not listed here (decision types, trade-block fields, the Fabio
vocabulary table, the 14-point checklist, "NOT STATED where he does not say it", no computed numbers) is V2 unchanged.

## 1. Differences from V2
1. **ASR, not captions.** Every anchor says ASR (see 3). Do not repair misheard words in a quote; flag them in AMBIGUITY FLAGS with `[?]`. A price, size or
   contract count that a decision rests on gets `[ASR number: check frames]`. The frames in `F:/MTS/data/fabio_videos/` (f398 video, 1280x720) are the
   arbiter for numbers; reading them is NOT part of this extraction.
2. **Speaker column.** ASR has no speaker labels. Is1HvdfQm5c is Fabio answering a live chat (viewers' names are spoken). xUyqIjCfZzg has TWO traders
   (Fabio Valentini and Carmine Rosato). Every decision row has `speaker`: FABIO / CARMINE / HOST / VIEWER / UNKNOWN. Write FABIO only when the words settle
   it (first-person position statements, "my stop", answering a chat question in the Fabio style, an explicit hand-over such as "Fabio, what do you think").
   Two readings stay UNKNOWN. Never turn a CARMINE or UNKNOWN trade into a Fabio trade block; give it a block marked `speaker: UNKNOWN`.
3. **Source kinds.** Each trade block says `kind`: LIVE_TRADE (a position he holds or took today), ILLUSTRATION (a past trade or chart he walks through, with a
   stated entry/stop/target), HYPOTHETICAL ("if I took a short from here ..."), VIEWER_Q (answering a viewer, no position). Only LIVE_TRADE and ILLUSTRATION get
   full trade blocks; HYPOTHETICAL and VIEWER_Q are rows of type TEACHING/LESSON/REJECT unless a number is stated.
4. **Part files.** Row ids are `<part>.<n>` (for example `2.17`), trade ids `T<part>.<n>`; each worker reads its own line range plus up to 60 lines before it for
   context, and writes rows only inside its range. "state at start" of a trade that began in an earlier part: `continues from earlier part (unknown)`; the
   merge pass links them.
5. **Position tags** BEGIN/MIDDLE/END are thirds of the WHOLE transcript body, not of the part. The checker computes them; run it and fix.

## 2. Part file layout (the merge keys on these headings, exactly)
```
# <video id> part <k>: lines L<a>-L<b> [<t0>-<t1>]
## READ RANGES            (every range read, in order, 60 lines at a time)
## DECISION LOG           (V2 3.2 table + columns `lines`, `speaker`)
## TRADE BLOCKS           (V2 3.3 fields + `kind`, `speaker`)
## REJECTIONS AND CONDITIONS
## VERBATIM ANCHORS       (every ENTRY, STOP_SET, TARGET_SET, STOP_MOVE, PARTIAL, ADD, EXIT, REJECT row, plus one per SETUP CANDIDATE)
## AMBIGUITY FLAGS
## DAY NOTES              (P&L statements with spoken numbers, session phase, risk rules he states)
## SETUP CANDIDATES       (see 4)
```

## 3. Anchor format (checked by `python scripts/dev/verify_extract_quotes.py <file>`)
```
> "exact words from the transcript"
**Source GPS: <VIDEO_ID> | MIDDLE** (ASR, L120-L122, [41:05]-[41:12])
```
The quote line starts with `> "` and ends with `"`; one passage per anchor; no `...` inside; the GPS line is directly after. L numbers are line numbers of the
canonical file (line 1 is `# Video ID`), `[t]` the stamps on those lines.

## 4. Setup candidates (input for the catalogue merge)
Existing Fabio rows after catalogue-p1-p2 (SETUP_CATALOG.md section 4, merged numbering; ids 3 and 7 are gone from the setup list):
FAB-1 balance with CVD pressure, break on volume ("sell model day"); FAB-2 absorbed push, rewarded effort ("punch to the wall"), including the failed auction of
one side then the other side's aggression (former FAB-3); FAB-4 failed breakout back into balance (reversal at the edge of the previous day's value area);
FAB-5 buyers protect a level (value-area low, gap, protection wall), long, squeeze trapped sellers; FAB-6 IVB first 30 minutes of the US open;
FAB-8 volume-defined fair value gap rejection. Heat-map liquidity (reload, protection wall, break and protect, book sweep) is the tool family in section 4.1
(was FAB-7), not a setup.
For each trade block or setup-bearing passage list: which row it supports, which it contradicts, or NEW (name in his words) with 1-3 anchors from the anchor
list; the entry, stop, target and management words it adds (NOT STATED where it does not give them). The worker proposes; it does not edit the catalogue.
