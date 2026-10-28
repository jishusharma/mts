VERDICT: FIX-FIRST

# RV05 Fabio ledger frame pass

RESULT (2026-10-13, surface COD, JIS-NUC): 72 ledger rows inventoried; 62 distinct cited image files present and unchanged from the previous evidence manifest. The literal RV05 exclusion leaves **2 rows**, both reviewed against every cited image and four additional adjacent sheets (20 sampled frames). Both match the non-trading screen descriptions; trade/account state and exact dates remain NOT_IN_DATA. Known H1-H3 remain repair concerns, with qualifications below. Findings: 3 HIGH carried forward, 2 MED; 3 SONNET evidence follow-up cards created. No ledger, code or spec edits.

## What was checked

Paths below are relative to `MyTradingSys/` unless starting `F:/`. `CSV` means `research/fabio_transfer/FABIO_TRADE_LEDGER.csv`; `MD` means its `.md` companion; `prior` means `research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md`. Image paths abbreviated `lowres/` and `sheets/` are beneath `F:/MTS/data/fabio_videos/`.

- Read `system/revalidation/RV05_fabio_ledger_frame_pass.md:1-16`, `_COMMON.md:1-19`, CSV:1-73, MD:1-90, prior:1-31 and the complete prior `_evidence.json:1-760`. Read the Fabio section of `system/LAYERS.md` beginning line 44, `research/tom_transfer_2026-10-11/ROADMAP.md:1-64`, and `backtest/PRE_REG_TEMPLATE.md:1-65` for scope/readiness.
- Parsed CSV with Python `csv.DictReader`. Compared its SHA256 with `ledger_sha256` and recomputed the first 16 SHA256 characters for every manifest image. Output: `HASH CHECK 72 62 True True` (row count, unique image count, ledger hash match, all image existence/hash matches). These are MATCH for inventory/integrity, not visual approval of 62 images.
- Opened 12 images using `view_image`: `lowres/Is1HvdfQm5c_w00_00.jpg`, `_w00_01.jpg`, `_w00_02.jpg`, `_w01_00.jpg`, `_w01_01.jpg`, `_w01_02.jpg`; `lowres/DyS79Eb92Ug_w3_01.jpg`, `_w8_00.jpg`, `_w8_01.jpg`, `_w9_01.jpg`, `_w10_00.jpg`; and `sheets/Jpd96fLqr5M_02.jpg`. Read every panel in the six Is1H sheets (0 through 475 seconds, step 25).
- Read local caption evidence `F:/MTS/data/fabio_videos/DyS79Eb92Ug.txt` (3530 lines), selecting risk/protection/auction statements and reading surrounding passages at lines 530-559, 1248-1265, 1360-1390, 1440-1485. These support narrative context, not precise fill prices. In particular lines 1455-1457 say the session is at 17,758; lines 1380-1384 discuss building toward 10 contracts and risk sizing. No caption re-extraction.
- Read the existing H1-H3 repair JSON cards under `system/tasks/` and used `python scripts/dev/tasks.py new ... --lane SONNET --layer fabio --ref <this report>` for the three evidence follow-ups listed below. No git or sync command.

### Exact row selection

The instruction is to open rows **not named H1-H3/M1-M4**. Prior H1 names CSV:25-71 (47 rows), including no-trade rows. Prior M4 names F1 family (5 rows), F3 family (7), F5 family (6); M3 names F2 family (3); M1 names F4a/F4b (2). Those disjoint sets total 70. H2/H3 and M2 overlap them. Therefore the remaining rows are **F-noTrade-Is1H-0-250 (CSV:72)** and **F-noTrade-Is1H-250-500 (CSV:73)**. This pass does not silently interpret a date-only finding as an earlier price/quantity frame audit; see M2 below.

## Per-row frame results

| Row / location | Frames opened | Entry, stop, quantity, side and STP dollars | Instrument / contract | Date / clock and description | Classification |
|---|---|---|---|---|---|
| F-noTrade-Is1H-0-250, CSV:72 | Cited `_w00_02` t=200,225; adjacent `_w00_00/01` t=0..175 | No trading interface, entry, stop, position quantity, side or STP dollar label visible. CSV `-`, `none` and `0` describe a non-trading screen; zero is not a measured account position. | No NQ/ES header or contract month | Intro/avatar at 0..75; Excalidraw welcome board at 100..175; Mental Models / Live Charting / Execution Method Trick agenda at 200,225. Taskbar is present but date/clock too small/obscured for a reliable exact transcription. No chart clock. | MATCH for screen inventory; NOT_IN_DATA for actual position, trade date/time and contract. |
| F-noTrade-Is1H-250-500, CSV:73 | Cited `_w01_02` t=450,475; adjacent `_w01_00/01` t=250..425 | Same absence of trading labels; no account state displayed. | No instrument or contract header | Agenda through 375; arrow and writing at 400,425; at 450,475 text reads “Shift your satisfaction from EOD Result to EOD process”. No readable trade timestamp. | MATCH for screen inventory; NOT_IN_DATA for actual position, trade date/time and contract. |

These are observations of the 20 sampled frames, not continuous-video proof that no unseen trade occurred in either 250-second interval. The cited `_02` image in each row contains only its last two sample times; opening adjacent sheets was necessary to check the rest of the note.

## Findings

| ID | HIGH/MED/LOW | file:line | What is wrong | Evidence / classification | Proposed fix |
|---|---|---|---|---|---|
| H1 | HIGH | CSV:25-71; prior:16 | `2026` is used as a trade-session date without a demonstrated session-date source. | NOT_IN_DATA for true date; MISMATCH with a claimed contemporaneous Dec-2025 contract session. The DyS frames opened show `NQ-202512`; CSV:29-71 explicitly carries that contract, while CSV:25-28 says only NQ. All 47 carry a 2026-prefixed date. Neither the header nor upload/review year establishes execution date. | Keep true session date unknown until a dated execution source is available; preserve recording/review date separately. Integrate this evidence into the existing date repair. |
| H2 | HIGH | CSV:33,45,47,49,50; prior:17 | Entry readings are unreliable; the previous audit's derived replacement entries are not all validated by the position line. | MISMATCH: F8 t=1325 position line is about 25034.53 versus CSV ~25032.5; F12 t=3100 line is about 25105.18 versus ~25107; F12-m2 t=3150 position line 25108.50 versus ~25100. F13 t=3375 line about 25108.90 versus ~25104, and F13-m1 t=3400 about 25108.05 versus ~25105. The prior replacement 25106.5 for F13 does not match the visible line. Small-label readings remain approximate. | Read full-resolution position/stop/order labels together and retain their exact timestamps; reconcile label calculation conventions and partial coverage before deriving an entry. Do not blindly install the prior audit's replacement values. |
| H3 | HIGH | CSV:51; prior:18 | `stopped_out_RESOLVED` overstates the available exit evidence. | MISMATCH in evidence strength: `_w10_00` t=3525/3550 shows +10 QTY and a -8 STP / -1760 dollar label at 25097; t=3575 is flat, Daily P/L 17758 versus 20668 before, a -2910 delta. Difference from the stop label is 1150. No fill price or complete execution history is visible. | Mark exit mechanism inferred pending fill evidence; reconcile uncovered size, other orders and costs separately. A daily P/L delta is not an execution receipt. |
| M1 | MED | CSV:72-73 | Non-trading-screen rows assert year 2026 and quantity zero without a readable trade/account source in their cited images. | NOT_IN_DATA: all 20 Is1H samples show an intro or Excalidraw, no account/contract. Taskbar pixels do not support a confident exact date transcription in this pass. | Retain these as screen-inventory events; source recording date separately, and do not use `qty=0` as a measured flat-position observation or count them as trades. |
| M2 | MED | `system/revalidation/RV05_fabio_ledger_frame_pass.md:9-12`; prior:8,16,22 | The exclusion rule prevents the stated broad completion of unread trade-row frame checks. Date/provenance findings name almost every row even though prior:8 says remaining rows were not frame-read. | MISMATCH between coverage rationale and selection: 70/72 rows excluded; only two non-trading rows remain. A date finding on all F6-F15 rows does not check their entry/stop/size fields. | For any subsequent completion pass, select rows by a recorded visual-read manifest and fields checked, not by whether any finding named the row. Do not label RV05 as a full 72-row visual audit. |

## Known-finding check

| Prior finding | Result | Independently checked evidence and limits |
|---|---|---|
| H1: 47 2026-dated rows versus expired Dec-2025 contract | CONFIRMED for the 47-row unsupported-date problem; NOT_IN_DATA for the stronger proof that every source frame establishes a pre-2026 execution date | Count is 71-25+1=47. Opened DyS headers show NQ-202512. The Jpd sheet is cropped and does not independently expose its contract header. The exact 2025-12-19 expiry is stated in RV05:14 and prior:16; no primary expiry-calendar source was supplied/read, so it is not independently certified here. A historical chart can be reviewed after expiry; contract month alone does not prove recording date. |
| H2: five entry cells off versus labels | CONFIRMED for inaccurate entries; REFUTED as a complete set of ready-to-use replacements | Five rows were compared to the opened position lines (table H2). F8 label arithmetic using the quoted -2040, 8 contracts and ledger's $20 multiplier gives 25021.75+2040/(8*20)=25034.50, close to the visible line. But the prior F13 replacement 25106.50 differs from visible ~25108.90. At F13-m1 the protective order is 8 lots while the position is 10: denominator choice cannot be implicit. F12-m2's visible stop price appears closer to 25098.75 than the quoted 25098.25; this small-text read requires full-resolution adjudication before changing the stop. |
| H3: F13-x -2910 versus -1760 | CONFIRMED | Directly read `_w10_00` t=3525,3550,3575; 17758-20668=-2910 and 2910-1760=1150. Caption .txt:1455-1457 corroborates the session balance figure. Cause of the difference is NOT_IN_DATA; neither slippage nor a discretionary fill is proven. |

### Date/contract conflict row list

The following is the complete 47-row **candidate date conflict / unsupported-date set**, not a claim that all 47 images were reopened. CSV:29-71 explicitly names NQ-202512; CSV:25-28 requires the same-session linkage for that contract. Is1H rows 72-73 have no contract and are not included. F1/F3/F5 month-level 2025 dates do not contradict their CSV December-2025 contract identifiers; this is only a column-consistency check, not date verification. F4's January-2026 date similarly does not contradict its March-2026 identifier.

F6, F6-m1, F6-m2, F6-m3, F6-x, F7, F7-m1, F7-x, F8, F8-x, F9, F9-m1, F9-x, F10, F10-m1, F10-x, F10-z, F11, F11-m1, F11-x, F12, F12-m1, F12-m2, F12-x, F13, F13-m1, F13-x, F-noTrade-3575-3750, F14, F14-x, F-noTrade-4025-4275, F-noTrade-4275-4525, F-noTrade-4775-5025, F-noTrade-5025-5275, F-noTrade-5275-5525, F-noTrade-5525-5775, F-noTrade-5775-6025, F-noTrade-6025-6275, F-noTrade-6275-6525, F-noTrade-6525-6775, F15-draft-6975-7025, F-noTrade-7025-7275, F-noTrade-7275-7525, F-noTrade-7525-7775, F-noTrade-7775-8025, F-noTrade-8025-8275, F-noTrade-8275-8493.

## Backtest readiness / not checked

No backtest result is generated or validated here. PRE_REG items 1 (source home) and 2 (ground truth) are relevant: two non-trading rows cannot establish market/session/holding period, and no minute-ready design/check ledger split is demonstrated. Item 11's holdout boundary is respected: no holdout read and no trial. Items 3 recall/fire rate, 4 proof-input data, 5 profile parity, 6 costs/noise, 7 fills, 8 exit-model fidelity, 9 null, 10 power and 12 stratified readout are **not evaluated**, not passed; no backtest is involved in this scoped frame audit. H3 specifically prevents treating the observed P/L change as a validated exit model.

Not checked: continuous playback between sample times; all 62 images as a new visual census; complete executions or account exports; primary exchange expiry calendar; v2 rules or prior BTC/holdout reports linked by the layer index. The other 70 rows are excluded by RV05's literal selector, except the documented H1-H3 spot rechecks. Their other cited frames/transcripts were not independently reread in this pass. Missing or unreadable facts remain NOT_IN_DATA, never fabricated zeros. Existing repairs themselves are out of scope. No tests are required for this read-only evidence report; the runner owns the shipping gate.

## Follow-up cards created

- `rv05-h1-date-evidence` (SONNET, fabio): evidence integration with existing `fabio-ledger-replace-date-2026-with-unkn`.
- `rv05-h2-position-line-evidence` (SONNET, fabio): adjudicate position-line and stop-label readings before existing `fabio-ledger-recompute-entry-from-stp-la` applies replacements.
- `rv05-h3-outcome-evidence` (SONNET, fabio): evidence integration with existing `fabio-ledger-f13-outcome-provenance-2910`.

These are follow-ups to the existing repairs, not claims that repairs were performed. Each has this report in `refs`. M1/M2 are recorded here for the next ledger-coverage refinement.
