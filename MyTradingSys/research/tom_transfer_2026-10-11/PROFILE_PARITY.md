# PROFILE_PARITY: computed side, 2026-10-12, JIS-NUC

Card: tom-profile-parity-check. The operator restricted this fallback to its computed side because
holdout-clean-split is claimed on JIS-NB. Frame comparison is delegated below.

Verdict: **NOT_IN_DATA**. Volume proofs are not established as usable on this feed.
Drawn prices, axis increments and profile anchors have not been read: the frames are on JIS-NB.
This is missing evidence, not a measured mismatch; no cost decision is inferred.

## Computed candidates (six levels)

| Ledger instant | Level | Drawn price | Computed candidate (points) | Difference (points) | Difference (% of drawn) | Status |
|---|---|---:|---:|---:|---:|---|
| T1 | POC | unavailable | 24314.70 | unavailable | unavailable | NOT_IN_DATA |
| T1 | VAH | unavailable | 24333.40 | unavailable | unavailable | NOT_IN_DATA |
| T1 | VAL | unavailable | 24280.70 | unavailable | unavailable | NOT_IN_DATA |
| T2 | POC | unavailable | 25078.14 | unavailable | unavailable | NOT_IN_DATA |
| T2 | VAH | unavailable | 25123.94 | unavailable | unavailable | NOT_IN_DATA |
| T2 | VAL | unavailable | 25066.69 | unavailable | unavailable | NOT_IN_DATA |

All six statuses await frame reads. Difference = computed minus drawn; percent = 100 * difference / drawn.
MATCH requires absolute difference <= one verified chart-axis tick AND identical profile window/time.
A line with unreadable identity, price, time or anchor remains NOT_IN_DATA.

These are engine UTC-day profile candidates, not assumed matches to Tom's session/composite anchors:
- T1: 2025-12-22 00:00 UTC to 06:25 UTC (ledger ~07:25 CET), 353 closed 1m bars.
  Frame n7ZSkjb7JXs_0314.jpg. The ledger time is approximate; exact chart cutoff needs verification.
- T2: 2026-01-08 00:00 UTC to 07:35 UTC (ledger 08:35 CET), 438 closed 1m bars.
  Frame k0zm5NYn0IQ_0280.jpg. Confirm this frame's clock corresponds to the ledger instant.
- Only these two dev dates were downloaded. No 2026-04-11..2026-10-09 bars or outcomes were inspected.
  Total rebuilt: 2,616 bars; profile windows use 791 closed bars. Gaps preserved, no forward fill.

## Implementation and reproduction

`MyTradingSys/backtest/tom_profile_parity.py` extracts the UNCHANGED two `buildVp` methods and their
VALUE_AREA_PCT / confidence constants from `src/main/java/datafeed/MarketDataSnapshot.java`.
It compiles only that profile code with cached Jackson in an isolated directory; no live engine is instantiated.
Java 11 on this NUC runs it without unrelated Java 17 engine classes or missing SLF4J dependencies.
Extracted engine source SHA-256: 009f6f533956ccffd2d85f531b15f0e408ac8252abb2beda5c5c8a82a7eab9a3.
The engine uses a dynamic grid, normalized triangular allocation, 70% value-area expansion and bin-key levels.
No Python reimplementation, setup encoding, tuning, signals or P&L reads.

The operator required work to stay in F:/MTS/mts-codex, so the regenerable archive is `work/dax_archive`
inside this checkout instead of the absent F:/MTS/data/dax_archive. `work/` is ignored in Git.
Feed: approved Dukascopy DEUIDXEUR 1m BID CFD feed volume, not Eurex FDAX contract volume.
Raw daily SHA-256:
- 2025-12-22.bi5: 865a4a6a17a213f2044641fbe20f9782f923308f1c261612694ae931571aa8ac
- 2026-01-08.bi5: 5d0a5c67d47c95d368e7b9413f3b4de32091ac3f0b2d23081471a5e993dc0990

Commands from this checkout (raw files handled with isolated Python):
```text
python -I MyTradingSys/backtest/dax_data.py fetch --start 2025-12-22 --end 2025-12-22 --raw work/dax_raw
python -I MyTradingSys/backtest/dax_data.py fetch --start 2026-01-08 --end 2026-01-08 --raw work/dax_raw
python -I MyTradingSys/backtest/dax_data.py convert --raw work/dax_raw --out work/dax_archive
python MyTradingSys/backtest/tom_profile_parity.py --raw work/dax_archive --start 2025-12-22T00:00:00Z --at 2025-12-22T06:25:00Z --out MyTradingSys/research/tom_transfer_2026-10-11/PROFILE_PARITY_T1.json
python MyTradingSys/backtest/tom_profile_parity.py --raw work/dax_archive --start 2026-01-08T00:00:00Z --at 2026-01-08T07:35:00Z --out MyTradingSys/research/tom_transfer_2026-10-11/PROFILE_PARITY_T2.json
```
JSON files record each exact cutoff, first/last minute, bar count and volume sum.
After verified frame anchors arrive, rerun the explicit window rather than substitute these candidates.

## Verification and remaining frame step

EXPECT: 1m point masses at prices [100,101,102,103,150] with volumes [1,2,10,4,3] have a
1-point engine grid, total volume 20 and value-area target 14. POC 102 starts with volume 10;
upper 103 adds 4 before lower 101 adds 2. POC=102, VAH=103, VAL=102.
Value-area expansion follows FORMULAS.md 18.1. Point masses avoid the probe's documented
uniform-spread versus engine triangular-spread distinction; engine output uses bin keys.
RESULT (2026-10-12, JIS-NUC): test failed with ModuleNotFoundError before the script existed, then
all 3 tests passed with no skips. Other tests prove forming/future bars are excluded and execute the CLI.
Collected by the quick gate's MyTradingSys/tests step. Java integration cases explicitly skip on
hosts lacking Java or coherent Jackson cache; the window test always runs.

JIS-NB desk request: `20261011-192710-tom-profile-parity-read-drawn-levels-and` (shipped, pending).
It asks for >=6 actual chart-axis levels, axis tick spacing, exact time/timezone and profile anchors,
with frame paths and no outcomes. Full drawn-vs-computed parity remains pending that evidence.
Research rationale: BACKTEST_FAILURES_RESEARCH.md N3 / section 6 item 5.

RESULT (2026-10-12, JIS-NUC): python scripts/dev/run_all_tests.py --quick: ALL TESTS PASSED.

## JIS-NB frame read, 2026-10-12 (relay session; dev dates T1/T2 only, no holdout bars read)

Frames viewed: n7ZSkjb7JXs_0314.jpg (T1), k0zm5NYn0IQ_0280.jpg (T2), plus T4/T5/T7 frames for the line inventory.
- No labelled POC / VAH / VAL line is drawn on either DAX dev frame. Tom's only profile object there is the right-edge volume
  histogram (no price text on its bars). T4/T5 show hand-drawn range lines (T5 blue line 24425 is "the value area", transcript
  T6hDJcHrVBM 04:22) but 2026-05 dates are inside the closed holdout window, so their computed side was NOT read.
  T7 is ES, not DAX. So the card's >= 6 drawn-vs-computed levels cannot be filled from dev data: 0 of 6 are MATCH/MISMATCH, all stay NOT_IN_DATA.
- Price level offset (measured from price levels only, no outcomes): ledger entry price minus archive 1m close at the ledger minute:
  T1 24481 - 24265.07 = +215.9 (2025-12-22 06:24Z); T2 25318 - 25087.66 = +230.3 (2026-01-08 07:34Z).
  The dxFeed FDAX chart and the Dukascopy DEUIDXEUR CFD archive sit ~220 pts apart, and the offset differs by day, so a
  1-tick absolute match is impossible by construction. (Part of it may be a timezone mismatch of the ledger instant; unverified.)
- Eyeball of the T2 histogram: widest bar ~25215-25225 on the chart axis (10-pt labels, +-10 pt read). Computed candidate POC 25078.14 +
  230 = 25308: not within a tick of the eyeball. Reading is screenshot-resolution only (no image library on this host: PIL/cv2 absent), so it is
  evidence, not a status.

Verdict unchanged: **NOT_IN_DATA**. Next steps, each one session:
1. Operator decision or Q: volume proofs need futures volume (FDAX) or a per-day basis rule; the CFD feed shape can only be compared after
   a basis offset, which is a parameter with no Tom source (provenance rule), so it must not be tuned.
2. Pixel-accurate reads need Pillow on JIS-NB (download needs operator approval): then measure histogram POC row, top/bottom rows on T1/T2 frames
   and compare SHAPE (POC position as fraction of high-low range) with the computed profile; that is basis-free.

## Basis-free shape comparison, 2026-10-13 (T1/T2 dev frames)

Shape metric: `f=(widest-row price - profile low)/(profile high - profile low)`. For drawn, profile low/high are visible chart-axis endpoints; for computed, they are VAL/VAH in the corresponding `PROFILE_PARITY_T1/T2.json`. A match is within one histogram-row height normalized by visible chart height.

| Frame | Chart / axis pixel box (x1,y1,x2,y2) | Widest row pixel box | Visible price low-high | f_drawn | Computed VAL-VAH; POC | f_computed | Result |
|---|---|---|---:|---:|---|---:|---|
| T1 `n7ZSkjb7JXs_0314.jpg` | DAX lower-left chart, approx (0,360,550,550); axis labels too compressed/obscured for endpoints | right-edge histogram visible, exact row bounds unreadable | NOT_IN_DATA | NOT_IN_DATA | 24280.70-24333.40; POC 24314.70 | NOT_IN_DATA | NOT_IN_DATA |
| T2 `k0zm5NYn0IQ_0280.jpg` | approx (243,80,1112,694); visible axis 25070-25370 | approx (959,357,1073,365), widest row center ~25220 | 25070-25370 | ~0.500 | 25066.69-25123.94; POC 25078.14 | ~0.200 | MISMATCH (~0.300 difference; row fraction ~0.014) |

**PROFILE arm on DAX = NOT_IN_DATA** (T1 is unreadable at the required axis precision; T2 alone indicates a shape mismatch, but both frames are required for the card verdict). Pixel boxes are approximate from the 1280x720 source images. No basis offset or outcomes were used.
