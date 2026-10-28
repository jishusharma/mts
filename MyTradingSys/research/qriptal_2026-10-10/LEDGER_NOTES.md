# Qriptal call ledger: notes (card qriptal-call-ledger, B162 step 1)

Result: **70 candidates, 2 ELIGIBLE** (both are variants of one weekly plan from the Sunday live stream, video ZPFK3ZsLwoo).
Zero ELIGIBLE rows fall in the DEV window, so nothing can be scored on DEV (see `SCORECARD.md`).

Files: `CALL_LEDGER.csv` (70 rows, generated), `ledger_rows.json` (the reviewed rows, one per statement),
`ledger.py` (verifies quotes, applies RULES.md, writes the CSV), `test_ledger.py` (18 tests), `PUBLISH_TIMES.tsv` (call times).
Rebuild: `python MyTradingSys/research/qriptal_2026-10-10/ledger.py build`; drift check: `... ledger.py check`.

## What a row is

One statement that could be mistaken for a call. Columns: `video_id`, `file_line` (raw transcript path:lines, found by the code, not typed),
`video_ts`, `quote` (verbatim, at most 25 words, verified against the raw file ignoring case and punctuation),
`published_utc` + `time_source`, `direction`, `entry`, `stop`, `targets` (each as stated, or `NOT STATED`),
`aux_refs` (quotes from neighbouring lines that carry a field the main quote does not), `kind`, `eligible` Y/N, `reason`, `window_split`, `note`.

`kind`: PLAN = forward-looking idea; RECAP = trade, order or plan he describes after the fact; HYPO = illustration for a viewer;
VIEW = market view with no trade offered. Eligibility is mechanical (RULES.md): BTC, kind PLAN, publish time known, and entry, stop and
at least one target each stated with a price.

## Counts

| Verdict / reason | Rows |
|---|---|
| ELIGIBLE (entry+stop+target stated, forward-looking, BTC, time known) | 2 |
| retrospective (RECAP) | 27 |
| no stop, no target | 16 |
| no stop (entry and target stated) | 7 |
| no entry, no stop, no target | 5 |
| no entry, no stop | 4 |
| view only, no trade offered | 4 |
| not BTC (ETH, Netflix, Circle, Chainlink) | 4 |
| hypothetical (viewer illustration) | 1 |
| **Total** | **70** |

By kind: PLAN 34, RECAP 30, VIEW 5, HYPO 1. Rows per video: ZPFK3ZsLwoo 13, then 1 to 5 for each of the other 21 videos.

Window split (call time + 8 days must end before the holdout starts on 2026-06-26, BACKTEST_PROTOCOL.md section 2):

| Split | Videos | Rows | ELIGIBLE |
|---|---|---|---|
| DEV (video 2026-04-15, 05-05, 06-02) | 3 | 11 | 0 |
| HOLDOUT window (video 2026-06-23 to 2026-09-22) | 19 | 59 | 2 |

The only fully specified forward calls (entry, stop, target) are the two ZPFK variants; the other 33 PLAN rows lack a priced stop
(he usually says "stop below this low" or "invalidated above this high" without a number) and often a priced entry.
The 7 "no stop" rows have an entry and a target: yKm-lCrA_zw short 65,600 to 60,000; dYlk1gtY2Lk short 66,400 to 65,400;
tJnls-_oGXc short 64,600 to 62,000; xnuGOjqzcqY long 76,600 to 81,000 and long 72,000 to 100,000; t5xiPuo3yuc short 80,000;
lRB4wMGa9tw short 82,800 to 72,000-73,000. Scoring them would mean inventing a stop, which is a parameter without a trader quote
(card scope_out), so they stay NOT_ELIGIBLE.

## How the rows were made, and the limit of the review

All 21 shorter transcripts were read end to end. ZPFK3ZsLwoo (1,479 lines, a 64-minute live stream) was read in full for the opening recap and
weekly plan (lines 40 to 330), the closing recap (1375 to 1460), the hedge/imbalance explanation (536 to 680), the October outlook (725),
the stock and viewer Q&A that mention levels (930 to 1130); the rest of it (mostly Q&A on other assets and indicator theory) was covered by a keyword scan
for stop, target, entry, take profit and invalidation, plus the cross-check below. A call that sits only in ZPFK lines 330 to 530 or 1130 to 1375
and uses none of those words could have been missed.

A second automatic check lists every raw line with "stop loss / stopped out / take profit / target is / invalidat" that sits more than 6 lines from a
ledger row: 46 lines, all read; none adds a priced stop or a new call (they are retail-trader commentary, trade management advice, past stop-outs,
or the 82.8 invalidation already used as the stop of the two eligible rows).

## DECISIONs (OURS)

- Call time = YouTube publish time from the video metadata (RULES.md says raw file name/metadata, the raw files carry none). Fetched 2026-10-16
  with yt-dlp, metadata only, no cookies; `PUBLISH_TIMES.tsv`. For the live stream the metadata time (2026-09-21 07:11:25Z) is the VOD time; the stream itself
  ran the evening of 2026-09-20 UTC, about six hours before the weekly open. The later time is the conservative one.
- A price is "stated" only if a number is spoken. "Stop below this low", "back above this high", "the open of this candle" are NOT STATED (chart-relative);
  the audio cannot resolve them without looking at the chart, and guessing would be a parameter without a quote.
- ZPFK weekly plan: his "hard invalidation" of 82,800 ("this will be invalidated if we break above 82.8") is taken as the stop of both variants. He also says
  "short hard stop loss on that high" (line 1430), which could mean just above 82.2; 82,800 is the only priced stop, so it is used and the row says so.
  The safer variant (short below 79.5) does not restate a stop; the idea-wide invalidation is applied to it. Both are in the HOLDOUT window and not scored.
- Ranges: "73 to 72,000" lists 73,000 then 72,000 (nearest edge first), per the RULES.md two-column scoring.
- A trade described after the fact is RECAP even if complete (t5xiPuo3yuc: Monday limit order 80,050 / stop 80,550 / targets 75.5 and 73-72k, reported
  front run; RrCbiOqXLRg: long with stop 75,700 and target 81,500). Scoring it at the video time would not be "as posted".
  The original statements sit in Discord or in Sunday live streams that are not staged.
- Window split: 8 days = 24 h limit-fill window + 7 days open (RULES.md). DEV needs the whole window before 2026-06-26.

## Cross-check with the one structured extraction (2026-09-20_ZPFK3ZsLwoo.md)

| Extract row | Ledger row (`QRP-ZPFK3ZsLwoo-NN`) | Verdict |
|---|---|---|
| Past 1: limit 80,000, stop 80,500 | 01 | retrospective |
| Past 2: long at 75.2, acceptable, skipped | 02 | retrospective |
| Past 3: short sweep of 80,000, stop 80,550 | 03 | retrospective |
| Past 4: short two imbalances, stop at daily open | 04 | retrospective |
| Past 5: ETH short | 08 | not BTC |
| Past 6: BTC hedge long, target 80,000, not taken | 09 | retrospective |
| Past "three wins, one loss" self-summary | none | a tally, not a call |
| QRP-ZPFK-01 aggressive short, 82.2 / 82.8 / 73-72k | 06 | ELIGIBLE |
| QRP-ZPFK-02 safer short below 79.5 | 05 | ELIGIBLE |
| QRP-ZPFK-03 October outlook | 10 | view only |
| Other markets: Circle, Netflix, Chainlink | 11, 12, 07 | not BTC |
| "Nero O", "LV", IBIT, "Zeke" (ticker unclear or non-BTC) | none | not BTC, ticker unresolved; none could be ELIGIBLE |
| Hypothetical viewer long 75.5 / stop 70,000 | 13 | hypothetical |

The extract's own outcome check (stop-out about 14 h after the stream) is not used here: it reads candles from the holdout window.

## Discord rows (card qriptal-discord-calls-2026-10-18)

Added 11 rows (`QRP-discord-01..11`, source `discord_rows.json`, built by `ledger.py` after the 70 transcript rows). Ledger now **81 candidates, 2 ELIGIBLE** (unchanged).
Counts of the 11: kind RECAP 4, PLAN 2, VIEW 5 (10-13..18 posts: 9 rows; 2 rows are 10-19 follow-ups from `research/habib_plan_imbalance_2026-10-20/README.md`);
reasons: retrospective 4, view only 5, no entry/no stop 1 (85.5k weekly target), NO_TIME 1 (73k short, PLAN); 3 rows have no recorded post time (NO_TIME split), 8 are HOLDOUT-window dated.
Evidence is the B162 section (operator's transcription of three screenshots) and the habib README, not the images (not in git). Each quote is verified verbatim
in those files and its line is the `file_line`. No Discord post gives a typed entry AND stop AND target, so none is ELIGIBLE; chart-only levels (Sunday plan chart, 10-14 support) stay blank (no reading from the image).
Not scored: no Discord row is ELIGIBLE and none is in DEV (Oct 2026 is after the 2026-06-26 holdout start); no candles were read.

DECISION (OURS): Discord times read as IST (UTC+5:30), the operator clock (the habib README converts 10-18 23:52 IST to 18:22Z). B162 itself says "UTC+?". If the clock were another zone, only `published_utc` shifts; no row changes eligibility.
DECISION (OURS): 10-19 follow-ups kept as rows although outside 10-13..18 (the plan study needs them). Missing: the 2026-10-16 "later" posts have no time, so they are NO_TIME.
Gap: the plan posts with typed price levels and full-res charts are not available (README section 5); the operator has to paste them.

## Transcript coverage and the daily retry

22 transcripts are staged: 21 of the 40 videos in `raw/q_list.txt` plus the 2026-09-21 live stream (which is not on that list). Known videos: 41. Missing: 19.
The list was written 2026-09-27, so videos posted since then are not on it either.

Missing video ids for the daily retry (YouTube captions returned HTTP 429 this week; do not fetch until the block clears):
`cuhsL6RENvw LSndcT8-nhg wvLNAGLsTe8 eJeMAX7CboQ brg09NkHi6A ntFHFFJiGhI YQwYXGBj1wg 8Bz1xQretRw 3Ce3Ndjd7mg oaUd1Lq9nKw abB-WYuhwlU Kagza2ZgZaI q6J9HlBCT-Y 1OxM_Bn0SNQ jz2Oak2qHQ0 nx2YBpkP-KA 3jzs_5chL_s XmgicExRT50 9fJElej4Hjw`

More valuable than those 19: the **Sunday live streams** (the weekly plans with levels, e.g. the 2026-08-23 stream drawn in RrCbiOqXLRg and the 2026-09-13 plan in t5xiPuo3yuc).
Only one is staged, and it holds the only eligible calls. The upload list `q_list.txt` does not enumerate the channel's /streams tab; add it to the retry list.

## Scorer (card qriptal-score-binance) decisions

Result: scored n = 0 on DEV, see `SCORECARD.md`; code `score_calls.py`, tests `test_score_calls.py` (26 with the committed-ledger checks).

- DECISION (OURS): one claim for both cards. `sync.py claim` refuses a second claim over the same area as the first (`qriptal-call-ledger`, same session),
  so card `qriptal-score-binance` was worked under that claim and the claim is released once, at the end.
- DECISION (OURS): the holdout is not read. The two ELIGIBLE rows (one weekly plan, 2026-09-21) are listed in SCORECARD.md as unscored; `--allow-holdout`
  exists, is off by default and has only been exercised on synthetic candles in the tests. Scoring them would give n = 1 plan and power 0.
- DECISION (OURS): in the fill candle only the stop is checked (the order of entry and target inside one 1m candle is unknown); a target counts from the next candle.
- The 7 PLAN rows with an entry and a target but no stop are not scored: any stop would be invented (NO-SOURCE, card scope-out).
