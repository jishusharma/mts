# Habib (Qriptal) plan-and-imbalance method: intake note (2026-10-20)

Status: INTAKE. No edge claimed. Testnet research only, no trade advice. Builds on `research/imbalance_qriptal_2026-10-16/` (construct F, fee-net test of his candle: NO EDGE) and `research/qriptal_2026-10-10/`. Those tested his *fade candle*; this note is about his *weekly/Sunday plan*, which nobody has scored.

## 1. Operator observation (SOURCED to the operator, 2026-10-20)
"More often than not, either completely or partly, his plans work out. His execution might be not good ... but usually it happens somewhere or the other what he says." Not yet measured; the operator's impression is the hypothesis H0 below.

## 2. Sources seen (Discord #trading-thoughts, operator screenshots; images NOT committed, shot ids 8839276278d5 and 94cdcf376035 in the local store)
Times in IST (operator local), converted to UTC (IST = UTC+5:30). Weekly open (wOpen) = Monday 2026-10-19 00:00Z = 05:30 IST.

| Post | IST | UTC | Content (paraphrase / short quote) |
|---|---|---|---|
| Sunday plan chart | 10-18 23:52 | 10-18 18:22Z | Chart projects: sweep low, push up to a boxed level with a note about a "bull trap early in the week", then a drop. Side note: sweep "is optional". |
| Follow-up 1 | 10-19 17:13 | 10-19 11:43Z | "Sunday plan once again starting out very well"; "we got the sweep (before wOpen though)" and price "moving higher". |
| Follow-up 2 (reply, 17:14 / 11:44Z) | 10-19 17:14-17:19 | 11:44-11:49Z | "personally caught the long reaction was fairly simple with all the imbalances"; long "since Friday" with "2 nice adds"; "following the bias outlined, expecting higher 1st". Chart: B markers at sweeps of a green level, red/green horizontal lines. |

Pixel limits: the embedded charts are thumbnails; price axis and the boxed level are not legible. Every level on them is NOT_IN_DATA until we have the original chart or his typed price.

## 3. Plan vs Binance fapi BTCUSDT (15m + 1h, UTC; public data)
| Item | Result | Evidence (OURS, from klines) |
|---|---|---|
| Sweep low happened | MATCH | Low 80,622.0 at 10-18 20:15Z, after the plan post (18:22Z); it took out the prior Sunday low 80,955.9 (15:30Z) and the Friday low 80,780.0 (10-16 17:15Z). |
| Sweep was before wOpen | MATCH | 20:15Z Sunday is 3h45m before Monday 00:00Z; wOpen price 82,077.9. His own "(before wOpen though)" matches. |
| Push higher after sweep | MATCH | 10-19 high 83,157.9 at 07:30Z (+3.1% off the sweep low, +1.3% over wOpen). Price was above wOpen for most of Monday 00:00-11:45Z. |
| Price at his 11:43Z follow-up | MATCH | 1h close 10:00Z 82,651; above wOpen (82,078). |
| Boxed level price | NOT_IN_DATA | Not readable from the thumbnail. |
| Reached the boxed level / "bull trap" | NOT_IN_DATA | Highest print 83,157.9 is the only candidate; cannot be confirmed without his level. |
| Drop after the push | PARTIAL, unscored | After the 07:30Z high price fell to 81,701.0 at 16:00Z (-1.8%) and was 82,043.0 at the last bar fetched (10-19 22:45Z), still above wOpen. Whether this is "the drop" depends on his level. |
| Long-since-Friday | NOT_IN_DATA | Position claim, not checkable; also not scored (execution excluded). |
Verdict for this one plan: the sweep-then-higher part is a clean MATCH; the box/bull-trap/drop part cannot be scored yet. One plan proves nothing about hit rate (n = 1).

## 4. What "imbalance" most likely means here (all HYPOTHESES until Habib defines it)
Prior note (2026-10-16) already pins his *candle* to construct F with quotes. For the *plan* these remain open:
- H-FVG: ICT fair value gap / volume imbalance (candles with no overlap). Common trader word; "all the imbalances" in a reaction long fits it.
- H-F: his volume-anomaly candle (small body on abnormal volume), midpoint/open as level (sourced in the 10-16 note).
- H-SP: single prints / auction imbalance (Tom-style), unlikely for him.
- H-vol: footprint / order-flow volume imbalance, needs trade data, unlikely from a chart-only trader.
- wOpen: weekly open (Mon 00:00Z) as bias level: price above = long bias. Hypothesis: "wOpen" is the UTC Monday open; his "(before wOpen though)" fits Sunday evening UTC. Confirm he does not mean the Sunday 17:00 NY forex-style week open.
- Sweep-then-reversal: sweep of a prior low then close back above. Hypothesis, definition (wick vs close, which low) unknown.
None of these is adopted. The study must test each as a separately named variant, with the variant count in the trial ledger.

## 5. Sources needed (operator-gathered only; no logins by sessions)
1. His typed plan posts with prices (#trading-thoughts and #trading-updates), original uncropped chart images at full resolution, with Discord timestamps and timezone.
2. Livestream recordings or captions where he explains wOpen, the weekly plan and "imbalance" (operator saves audio/video to disk; transcription via local Whisper per ROUTING).
3. At least 12 weekly/Sunday plans with a stated outcome window, to give the hit-rate any meaning.
4. His own definition of the box and the sweep-optional note.

## 6. Numbers
All thresholds above (times, 20:15Z, 80,622.0 etc.) are OURS, read from klines. No SOURCED numeric parameter yet: the only sourced items are the quoted phrases in section 2.

## 7. Routing
- `habib-plan-hit-rate-study` (new, lane DSA-NB: needs the 1m klines that live on JIS-NB): score each plan full / partial / miss, execution excluded; then test his imbalance levels against placebo levels. DEV only; one VALIDATION check; holdout read once.
- `qriptal-discord-calls-2026-10-18` (existing, SONNET): transcription of the Discord calls feeds the study; extend its scope to include plan posts with levels.

## 8. Build status (card habib-plan-hit-rate-study, 2026-10-23): BLOCKED on source, scorer and plan ledger ready
Result: **0 plans scoreable on DEV; the hit-rate and placebo test were NOT run.** `PLAN_LEDGER.csv` lists the 9 plans in the call ledger with a spoken entry price and first target (`qriptal_2026-10-10/CALL_LEDGER.csv`, PLAN, BTC, direction known); all 9 are dated 2026-07-14..09-22, i.e. inside the holdout window (starts 2026-06-26, BACKTEST_PROTOCOL.md section 2), so no 1m candle was read. The 10-18 Sunday plan has no typed level (section 3). Done-when (>=12 plans with full/partial/miss) is not met: 9 candidates, 0 scored.
- `plan_score.py`: pure scorer, execution excluded. Definitions OURS and fixed before any scoring: fill window 24 h, open window 7 d (same as qriptal RULES.md), full = entry then first target touched, partial = entry touched and at least 50% of the distance to target travelled, miss = otherwise, NO_DATA never a miss. `test_plan_score.py` (10 tests; fail on the old tree, which had no scorer or ledger).
- Needed to unblock (operator): >=12 plans dated before 2026-06-26 with typed levels, or a pre-registration that releases the holdout/VALIDATION read for these 9 (one read, variants counted: scorer 1 variant; placebo test not yet defined, so 0 run). Section 5 list stands.
- DECISION (OURS): conservative default, no holdout read without a pre-reg; placebo comparison deferred until >=12 scoreable plans exist.
