# Claude verification of the GPT trend-line research, 2026-10-17

Scope: REPORT, METHOD, REVIEW, CLAUDE_HANDOFF, DAILY_WATCH, daily/2026-10-17.md, daily/ledger.jsonl, card `trendline-priority-drawing-contract`, LAYERS.md line (commits 55c66f96, d35115ea). Checked at origin/fast-track 36be7c22. No backtest, no market data read.

## VERDICT: FIX-FIRST
Everything the report cites checks out and it is honest about having no economics. But it is a research plan, not a drawing contract: no parameter is set, so nothing can be coded or tested yet. The eye-read part (what is an "obvious" line) has no blind-mark step, and the daily watch has produced zero usable geometry. Build the contract and the causal module first (cards below); no study until a count-only PRE_REG.

## (a) Sources and quotes
| Claim | Verdict | Evidence |
|---|---|---|
| Krown TRL locators and timestamps (TRL-04/05 04:18/04:27 ... TRL-22/23/24 24:11/25:44/26:26) | VERIFIED | Every timestamp matches a `Source GPS` line in `extract_14bxwxC8gBQ.md`; `verify_extract_quotes.py` on that extract: PASS, 0 problems. Note: "TRL-nn" is the rule-source id in KROWN_RULES.csv, the extract itself numbers K-14bxwxC8gBQ-nn (same nn). Report should say so. |
| "No new transcript quotations reproduced" | VERIFIED | Report has paraphrases only; nothing to quote-check beyond the extract. |
| Krown stated numbers (3 touches, 2 on heavy volume, volume about 2x, 4-5 degrees) | VERIFIED | KR-L02/L03/L07, KR-V02 in KROWN_RULES.csv; swing bars each side NOT given (KR-L01: "k is OURS"), degrees BLOCKED by chart scale. Report's "missing mechanical choice" column is accurate. |
| StockCharts (two points propose, third confirms; internal lines ignore spikes; chart size changes angle; steep-line breaks hard to play) | VERIFIED | Fetched 2026-10-17; all four statements present. |
| Fidelity (join rising lows / falling highs; break is a warning needing confirmation) | VERIFIED | Fetched; present. |
| TradingView Pine FAQ (algorithmic line through recent pivots) | VERIFIED | Example connects the two most recent same-type pivots from ta.pivothigh/pivotlow. |
| IG Analyst (swing-line bounce, pip offsets are FX-specific) | VERIFIED | Page gives 2-5 pip stop/entry offsets. |
| IG Academy breakout companions, StockCharts Price Channel, TradingView angle tool | UNSUPPORTED (not opened by me) | Not fetched, tokens; low risk, T3 definitions only. |
| "Method note was written before searching" (REPORT) | UNSUPPORTED | METHOD.md and REPORT.md land in one commit (55c66f96); no earlier timestamp. |
| Parameters SOURCED or OURS | OVERSTATED | Tagged OURS in prose, but no value exists for k, tie policy, spacing, age, tolerance, reset distance, ATR length. "Declared" is promised, never declared. |
| REVIEW.md "independent review" | OVERSTATED | Reviewer is the same GPT agent that wrote the WaveTrend review; same lane as the author. It is a self-review, useful as a checklist only. |

## (b) Numbers and the daily ledger
The report contains almost no computed numbers (no backtest). Checked every checkable one:
| Claim | Verdict | Evidence |
|---|---|---|
| ledger.jsonl sha256 per record | VERIFIED | Recomputed over sorted-key JSON without the `sha256` field: 4/4 match. The serialisation recipe is not written anywhere (a reader needs trial and error); also a self-hash, tamper-evident only against casual edits. |
| Ledger timestamps (first observed 03:26:58-03:28:45Z = 08:56:58-08:58:45 IST; receipt 08:57-08:59; commit d35115ea 08:59:23) | VERIFIED | Consistent. The interval is the run window, not per-post capture time (receipt says so). |
| "No `backtest/layers/krown/` folder; no trendline code" | VERIFIED for HEAD | Directory absent; no tracked .py/.java/.pine with trendline in its path. The "197 Git refs" scan is not reproducible: repo now has 568 refs. Unrelated pivot/swing code exists (`layers/cryptocred/cc_structure.py`, `fabio/fabio_volume_fvg.py`, `rsi/rsi_divergence.py`, `bigtrade/bigmoves.py`) and `layers/timeframe/tf_resample.py` (closed-bar resample with a real-data gate): the build card must reuse them, not write a fifth pivot function. |
| "STATUS.md CI-red is stale; three successful fast-track runs" | VERIFIED | `gh run list`: success at 03:34Z (450636f4), 02:04Z, 02:02Z, 01:36Z. |
| Daily watch coverage: 4 candidates from a 10-card feed, 0 geometries, 0 outcomes | VERIFIED as stated; USELESS as is | The ledger says so itself: anchors, equation, touches, transform all null. A post-image line cannot be reconstructed from a title and a screenshot that timed out. Engagement counts (330/60 ...) are unverifiable and unused. |
| The selection rule ("explicit diagonal/triangle/channel in title or preview") | OVERSTATED | eDD5YPAG's title ("Bearish Reversal Targets") carries none of those words; the rule was applied loosely. Stable sampling needs the exact string match written down. |
| "Heartbeat scheduled daily 09:00; no successful scheduled run yet" | UNSUPPORTED | Only the first manual-time run (08:57) exists; scheduler not inspected. |
| Daily observations are point-in-time | PARTLY | Observation time and publication time are stored, outcomes not scored: honest. But "first observed" is a 2-minute window per run, not per post, and no content hash of the chart image/text is stored (report promises one). |

## (c) Look-ahead, repainting, splits, fees
| Item | Verdict | Evidence |
|---|---|---|
| Pivot available only at close(i+k); anchors immutable; new anchors = new version | VERIFIED as design | Sound and causal. Not implemented, no test. |
| Contact episodes, eligibility, break, retest | UNSUPPORTED as contract | No distance-away reset, no tolerance, no minimum anchor spacing, no max age, no penetration test threshold; two readers would code different detectors. |
| Repainting | OK on paper | Versioned lines solve it; the card test must assert that a line computed on data cut at t equals the same line computed on all data (truncation test). |
| "Three touches" ambiguity | OVERSTATED | Krown KR-L02 (touches=3) conflicts with KR-Z13 (catalogue C1). The report's reading, 2 anchors + 1 later test, is OURS, not Krown. Both readings must be arms. |
| Splits | UNSUPPORTED | Report says "DEV" without dates. Repo split: DEV to 2024-06-30, VALIDATION 2024-07-01..2025-06-30, HOLDOUT after (SPLIT_ALIGNMENT_2026-10-17.md). The old bigtrade labels TRAIN to 2024-12 must not be inherited. Any read of DEV needs an EXPOSURE_LEDGER line. |
| Fees | OK | No P&L claim; says recheck. Entry/stop/target are NOT STATED for KR-S10/S11 (catalogue), so no executable test is possible before G2 gaps close. Do not borrow stops from other layers (report agrees). |

## (d) Lessons and gates G0-G6
| Check | Verdict |
|---|---|
| No economics claimed, DEV discovery / freeze / validate once, control arms (line alone, context alone, horizontal alone, placebo lines), clustering by day, effective n | VERIFIED as intent; none have numbers. |
| G3 blind marks by two readers for anything eye-read | WRONG ORDER | Report puts "build descriptive detector" at priority 2 and "compare selector with analyst-labelled sample" in prose, but never schedules two blind readers. "Obviousness" (Krown K-03) is exactly an eye-read concept. Mechanical pieces (pivot, line, touch, break) can be unit-tested now; the "is this line legitimate/obvious" selector needs a G3 pack under READER_PROTOCOL.md first. Krown sits at G2, G4 encode must follow G3. |
| Count before freeze, MDE/Holm, one-run study | UNSUPPORTED | Mentioned, no count exists. Rare conditional cells (e.g. 5-touch line + break + near horizontal) will be underpowered; a count-only run must precede any PRE_REG (gross-effect lesson: T arm n=40, MDE 0.365 %). |
| One-run / trial ledger | OK | Report says track all variants; no ledger created yet. |
| LAYERS.md line | VERIFIED | One line listing the card; claims nothing about gate status. Krown remains G2. |
| Card `trendline-priority-drawing-contract` | OVERSTATED | `tests` is "spec review", done_when is a spec document; a code lane card with no fail-first test, and it asks one session for spec + fixtures + ledger schema + two issued cards. Superseded by the cards below. |

## Wrong / overstated, short list
1. WRONG ORDER: detector before blind marks (G3) for the eye-read selector.
2. OVERSTATED: "independent review" (same agent); "declared" parameters (none set); selection rule applied loosely; "three touches" as Krown's meaning of 2 anchors + 1.
3. UNSUPPORTED: method-note-before-search timing; DEV dates; 197-ref scan (now 568); scheduler state.
4. Daily watch: honest but yields 0 geometries; fix by recording per-post capture time, content hash, exact selection string, and never counting image-read lines as lines until two readers agree.

## Next cards (gate order, no backtest study)
1. `trendline-contract-spec` (SONNET): TRENDLINE_CONTRACT.md with every parameter SOURCED (quote + file:line) or OURS, values fixed once, ledger schema.
2. `trendline-causal-module` (SONNET, depends 1): causal module + tests incl. truncation test; reuse existing pivot/tf code.
3. `trendline-count-only` (DSA, depends 2): DEV-only counts per TF/arm, no outcomes, exposure ledger line, then a PRE_REG with MDE/Holm.
4. `trendline-g3-marks-pack` (SONNET, depends 1): blind two-reader pack for the eye-read selector, per READER_PROTOCOL.md.
`trendline-priority-drawing-contract` is dropped as superseded.

Defaults taken (no operator asked): treated REVIEW as self-review; sources not opened by me left UNSUPPORTED rather than guessed; verdict FIX-FIRST.
