VERDICT: FIX-FIRST

# Fabio ledger: frame and caption audit

RESULT (2026-10-12, JIS-NUC, Sonnet): 72 CSV rows (`FABIO_TRADE_LEDGER.csv:2-73`), 62 distinct cited images, all present on `F:/MTS/data/fabio_videos`. 3 HIGH, 4 MED. Verdict FIX-FIRST: the ledger is a good *event inventory* but not a trade-record set; do not build v2 rules or a replay denominator from it until H1-H3 are repaired.

## Method and scope (read this before trusting any row)
- Every row got a programmatic check: frame file exists and is hashed (evidence JSON beside this file), side/qty/entry/stop arithmetic (`|entry-stop| x qty x $20` NQ / `$50` ES vs the STP dollar label quoted in the note), date/contract consistency, duplicate frames.
- Frames were opened as images for the rows in H2, H3, M1, M2 (contact sheets `lowres/DyS79Eb92Ug_w8_01`, `_w10_00`, `sheets/9IliXww64uM_05`, `sheets/Jpd96fLqr5M_02`). The remaining rows are checked on arithmetic and provenance only, NOT re-read frame by frame; a row not named below is "no contradiction found", not MATCH. Image reading used contact sheets (low resolution): levels are +-1-2 points.
- No backtest, no holdout read, no code or spec change. Captions were not re-extracted.
- Classes: frame-observed = a label/order/P&L box visible on a frame; quoted = trader caption; inferred = ledger author's reading (daily-P/L deltas, derived entries).

## Findings
| ID | Sev | Rows (CSV line) | Class | Finding | Missing evidence / fix |
|---|---|---|---|---|---|
| H1 | HIGH | F6..F15, F-noTrade (lines 25-71, 47 rows with date `2026`) | MISMATCH | Date `2026` is asserted for the Jpd96fLqr5M / DyS79Eb92Ug sessions but the chart header on every read frame is `NQ-202512` (the Dec-2025 contract, expired 2025-12-19, ticker strip reads Dec19'25). No frame read shows a calendar date, only 15:31-17:57 clock times. The session therefore cannot be in 2026; its true date is unknown (<= 2025-12-19). | Video upload date from yt-dlp metadata, or a frame with the date axis / taskbar date. Until then date = UNKNOWN, not `2026`. Matters for any date-based design/check split and holdout exclusion. |
| H2 | HIGH | F8, F12, F12-m2, F13, F13-m1 (lines 33,45,47,49,50) | MISMATCH | Entry cells disagree with the frame's own STP label (`label$ / (qty x 20)` = stop distance). Implied entries: F8 25034.5 (ledger ~25032.5), F12-m2 25108.5 (ledger ~25100; stop width 10.25pt, not 1.75pt), F13 25106.5 (ledger ~25104), F13-m1 25108.0 (ledger ~25105). Frame `_w8_01` t=3150 shows STP -10 -2050$ at 25098.25 and sell LMT 25140.75; ledger entry is 8.5pt off. Stop-width statistics derived from `entry`/`stop` are wrong for these rows. | Recompute entry from the label, or read the position line on a full-resolution frame; keep ledger `entry` only where it matches label within 1pt (F7, F9, F10, F11-m1, F12-m1, F14 do). |
| H3 | HIGH | F13-x (line 51) | MISMATCH | Row says `stopped_out_RESOLVED` but the Daily P/L delta is -2910$ while the visible stop label is -1760$ (frame `_w10_00` t=3525: `+10 QTY`, `STP -8 ... -1760$`: only 8 of 10 lots covered). Gap 1150$ is unexplained (unprotected 2 lots, discretionary exit, costs). Not a clean stop fill. | Frame between t=3550 and t=3575 at full resolution, or the trade-statistics screen. Mark outcome INFERRED until read. |
| M1 | MED | F4a, F4b (lines 17-18) | NOT_IN_DATA | Frame `9IliXww64uM_05` t=630 shows a pasted screenshot titled `Screenshot 2026-01-30 214344.png` with `-1@6986.75` at the peak and `-1@6977.5` on the earlier rise. The date is the screenshot *file name*, not the trade date; "scale-in 9.25pt below" is an inference (the lower label is the EARLIER one: two separate shorts or a re-entry). No stop, target or exit. | Full-resolution frame of the screenshot; trader's caption around t=630-750. Treat as 2 unfilled-outcome events. |
| M2 | MED | all `-x` exit rows (13 rows) and 7 rows flagged not-shown/inferred | INFERRED | Exit prices are not on any frame; outcomes are Daily-P/L deltas, which include costs and any other order. Fine for sign/size, not for R-multiple, hold time or exit-rule evidence. | Exit fill frames or trade-statistics export; until then `exit` is blank, not a number. |
| M3 | MED | F2, F2-m1, F2-x (lines 7,15,16) | NOT_IN_DATA | Date unknown, entry/stop approximate from drawn lines, no order labels; ledger already says teaching example. It must not enter any trade-count denominator. | Mark `kind=teaching` in the CSV. |
| M4 | MED | F1..F1-x, F3a..F3c-x, F5.. (months only) | NOT_IN_DATA | `date` is month-level (`2025-10`, `2025-12`); `time_local` mixes chart time and "NY session". Chart clock vs timezone not established, so no minute-level replay. F3c-m1..m3 all cite the same sheet image (`fZlNGWvd2Ko_02`), so four rows share one observation. | Per-frame taskbar clock + timezone for each video (card `fabio-ledger-minute-timestamps` already queued). |

Checked and clean on arithmetic (stop $ label vs `|entry-stop| x qty x mult`, within 1.5%): F1, F3b, F3c, F5, F5-m2, F6, F7, F9, F10, F10-m1, F11, F11-m1, F12-m1, F14.

## Repair cards (HIGH)
- fabio-ledger-date-unknown-2025-12 (H1)
- fabio-ledger-entry-from-stop-label (H2)
- fabio-ledger-f13-outcome-provenance (H3)
Fabio v2 spec cards (`fabio-layer-v2-spec`, `fabio-layer-v2-markets`) depend on these three plus M2/M4.
