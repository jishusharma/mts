# KROWN PIPELINE PROTOCOL - lessons checked, then applied (2026-10-14)

Written before any further extraction, at the operator's request: "check all the lessons we learned in extractions, make sure
everything is structured from the beginning." Sources read in full: methodology/extraction.md, methodology/playbook.md (Part I),
research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md, research/EXTRACTION_ROUND2_2026-10-01.md,
research/EXTRACTION_TO_ALERT_AUDIT_2026-09-19.md, system/LESSONS_DIGEST.md, system/LESSONS_LEARNED.md (2026-10-12 entry),
backtest/PRE_REG_TEMPLATE.md, research/tom_transfer_2026-10-11/ROADMAP.md (F2) and RECALL_DAX.md section 1. The research gate for briefs is methodology/playbook.md Part I (T1-T3/REJECT, verified citations); the former memory notes research-gate-in-briefs and tom-fabio-redefine-direction were retired 2026-10-15.

## 1. Lessons and how each one applies to Krown

| # | Lesson (source) | Applied to Krown |
|---|---|---|
| L1 | Phase 1 = ONE transcript, clean slate: do not load prior extractions or compare videos (extraction.md SAFEGUARD 5) | The pending videos go to fresh single-video workers that read only EXTRACT_TEMPLATE.md + their transcript (batch 2, 7 videos, done this way 2026-10-14). The old STATE.md told workers to copy extracts/extract_HhV4HI9p5Uw.md: replaced by the template. The session that consolidates (Phase 2) never extracts. |
| L2 | In-vivo rule: a code that is not verbatim in the transcript is not valid (SAFEGUARD 1) | Quote gate `verify_extract_quotes.py` on every extract: 8 of 8 PASS (re-run 2026-10-14). |
| L3 | The quote gate reads anchor lines only; paraphrase lines drifted 7 of 267 on first writing (EXTRACTION_ROUND2 s5.2) | New gate `tools/check_numbers.py`: every number in `Stated mechanics:` must exist in the transcript. 8 extracts, 225 numbers, 0 wrong (4 benign mismatches, listed in MANIFEST.csv). Now part of every extract's DONE. |
| L4 | Cluster evidence: a setup cluster needs >= 3 videos in the analyst's own language and a boundary (SAFEGUARD 2) | Every ledger row carries `n_videos`; a family with < 3 videos is marked PROVISIONAL (moving averages: 2 full videos + asides; the 5 EMA leash: 1 video). |
| L5 | Saturation gate: no SETUP FILE until >= 20 videos extracted and the last 5 add < 5 % new codes (SAFEGUARD 3) | Only 19 videos are reachable (37 listed, 18 hidden); 14 TA videos are extracted, 4 missing. The 20-video count cannot be met on this playlist alone, and the last 5 extractions added whole new families (volatility, RSI, tops), so the saturation condition is NOT met either. Decision q-krown-saturation (waiver for descriptive work only). Until then only descriptive detectors + recall checks are built, no engine setup file and no live wiring. |
| L6 | Consolidate (Phase 2): dedupe by principle, keep all GPS refs, FLAG conflicts, do not resolve them (extraction.md s3) | KROWN_CONSOLIDATED.md; conflicts C1-C8 kept open with both sides. |
| L7 | Classify every rule READY / BLOCKED / REJECT with a 5-step check (Phase 3) | Column `phase3` in KROWN_RULES.csv; the reason sits in `blockers`. |
| L8 | Reflexivity log after each batch (SAFEGUARD 4) | reflexivity_log.md, entry 1 written. |
| L9 | Do not force our taxonomy during extraction; mapping to our labels happens later against the code (V2 s4.6) | Template rule 4. Family names in the ledger are Krown's own episode vocabulary. |
| L10 | Do not write the mirrored rule unless he states it; record `Side` as said (V2 s4.1-4.3) | Template field `Side`; ledger column `mirror_stated`. |
| L11 | Lectures give LESSON rows and little trade content; V2 trade format fits trade walk-throughs only (ROUND2 s5.2) | TA 101 are lectures: concept format is right. If Krown's daily event-study / live-call videos are extracted later (KROWN_FREE_VS_PAID.md), use V2 for those. |
| L12 | Prices and dates for ground truth come from frames or from the price data, never from caption text (research/tom_transfer_2026-10-11/ROADMAP.md F2 and RECALL_DAX.md section 1; ASR errors like "55 minute closures", "three seven seven") | Every dated example in the extracts (Mar 2020, Feb 2026, Dec 2018...) is checked against klines before it is used as a recall check. |
| L13 | No layer backtest until the 12-item readiness template is answered with file:line evidence (LESSONS 2026-10-12; PRE_REG_TEMPLATE.md) | PRE_REG_KROWN.md; item 2 (ledger of the source's own trades) is NOT_ANSWERED for TA 101 (lectures, no trade recaps). |
| L14 | Every parameter is SOURCED (his words, quote + file:line) or OURS; OURS is chosen on DEV, checked once on VALIDATION, holdout read once; every variant in the trial ledger (CLAUDE.md 2026-10-13) | Ledger column `param_label`; no number is ever shown as his unless a quote carries it. His own statistics (5,284 candles, 82 %, 26 years, 80 touches) are claims: T3, REJECT as evidence, kept as hypotheses to TEST. |
| L15 | Tier labels never upgraded; T3 = ideas and definitions only; a system change backed only by T3 needs operator approval (playbook Part I) | All ledger rows T3. No live wiring without the operator. |
| L16 | Volume flags use a same-slot baseline; plain relative volume is a clock for BTC (LESSONS_DIGEST s2) | Direct tension with his 2x SMA20 volume rule: both arms are tested (his plain SMA20 = SOURCED arm, same-slot baseline = OURS arm). Conflict C5. |
| L17 | YouTube: about 5 caption fetches per session; on a bot check STOP and ask for pasted transcripts (LESSONS_DIGEST s6) | Caption fetch on 2026-10-14: an 11-id run returned 7 transcripts and HTTP 429 for 4; the page's caption endpoint returns an empty body. Stopped after that, no workarounds (no cookies, tokens, third-party sites, no watch pages in the in-app browser: autoplays audio). I first wrote that all 11 were blocked after reading the log too early; corrected. |
| L18 | Never conclude from truncated output; count by parsing the real format (LESSONS_DIGEST s1) | Playlist counted from the full flat-playlist JSON: 37 entries, 19 reachable, 18 hidden. STATE.md's old numbers (28 listed, 18 reachable, 10 to do) were wrong; 11 ids were pending, not 10. |
| L19 | Spot-check one claim per worker report; read the diff of a worker's output (LESSONS_DIGEST s5) | After each worker: both gates, then read 3 random quotes against the transcript by eye. |
| L20 | Frames beat captions for chart facts (Tom/Fabio ledger lesson) | TA 101 charts were shown on screen; captions carry only what he says. Any rule that depends on what the chart looked like (e.g. "obvious" zones) is flagged DISCRETIONARY. |
| L21 | A gate with a defect teaches workers to write around it (batch 2: ordinals like 50th were false-flagged and a worker rewrote its text) | check_numbers.py now accepts ordinal suffixes; any worker report of a gate false-positive is read, the checker is fixed, the extract is not bent to it. |
| L22 | Read a background log to its end marker before concluding (this session misread an unfinished fetch as blocked) | Rule for this folder: STATE/MANIFEST statuses are written from `ls transcripts/` and the process list, not from a log tail. |
| L23 | Worker logs may be empty, so clean-slate compliance cannot be audited afterwards | Evidence kept instead: the brief text (s3), the template, each worker's report, and an output-side check that no extract names another video's id. For stricter audits run workers with a logged transcript. |

## 2. Pipeline and folder map (fixed from the start)

```
krown_ta101_2026-10-13/
  STATE.md                 status board (counts come from MANIFEST.csv)
  MANIFEST.csv             one row per playlist id (37): status, extract, gate results
  PROTOCOL.md              this file
  EXTRACT_TEMPLATE.md      Phase 1 skeleton (what workers read)
  transcripts/             <id>_timed.txt (input, from fetch_captions_timed.py)
  extracts/                Phase 1 output, one file per video          [Sonnet worker, clean slate]
  tools/check_numbers.py   number gate
  tools/build_ledger.py    generates KROWN_RULES.csv + KROWN_CONSOLIDATED.md from one data list
  KROWN_RULES.csv          Phase 2/3 ledger: one row per principle, READY / BLOCKED / REJECT
  KROWN_CONSOLIDATED.md    Phase 2 readable master list, conflicts, hypotheses
  KROWN_LAYER_SPEC.md      layer v0 spec (setups, SOURCED/OURS parameters, gaps)
  PRE_REG_KROWN.md         the 12-item readiness template, filled honestly
  reflexivity_log.md       Phase 4 safeguard: surprises per batch
```
Rule IDs `KR-<family><nn>` are stable. A new extract adds source ids to an existing row or adds a new row; it never renumbers.
Source ids: `<CODE>-<nn>` = concept `K-<video id>-<nn>` (CODE per MANIFEST.csv).

## 3. Phase 1 worker brief for each pending video (<= 30 lines; send one per video, Sonnet, clean slate)

```
Task: extract ONE Krown video, clean slate. Read only these two files, nothing else under research/krown_ta101_2026-10-13/:
  MyTradingSys/research/krown_ta101_2026-10-13/EXTRACT_TEMPLATE.md
  MyTradingSys/research/krown_ta101_2026-10-13/transcripts/<ID>_timed.txt
Write MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_<ID>.md in the template format.
Do NOT open any other extract, STATE.md, the ledger, or any file about Krown. Do not compare with other videos.
Read the transcript from the first line to the last, in order. Count the concepts you wrote and the transcript's last timestamp;
the last concept must come from the last third. Losing and failed examples get the same detail as winners.
Every concept needs a verbatim quote. No ellipsis inside a quote. Numbers exactly as spoken; garbled captions get INFERRED.
Gaps section: list every threshold, stop, target, size and lookback he leaves open or defers, with t=.
Done = both gates print PASS / 0 not found:
  python -I scripts/dev/verify_extract_quotes.py <your extract>
  python -I MyTradingSys/research/krown_ta101_2026-10-13/tools/check_numbers.py <your extract>
Reply with: concept count, the two gate lines, and the 3 most rule-like concepts. Do not commit.
```

## 4. Hard stops
- Captions: if `fetch_captions_timed.py` prints 429 or a bot check, stop. Do not retry in a loop, do not use cookies, tokens or third-party
  transcript sites, and do not open YouTube watch pages in the in-app browser (it autoplays audio, seen 2026-10-14). Ask for pasted
  transcripts (one `.txt` per id in `transcripts/`, header lines optional) or retry from another network after a few hours.
- No engine setup file, no live wiring and no mainnet anything from T3 content (operator approval, L15).
- Do not edit the 8 finished extracts. A mistake found in one goes into reflexivity_log.md and is fixed by a re-extraction.
