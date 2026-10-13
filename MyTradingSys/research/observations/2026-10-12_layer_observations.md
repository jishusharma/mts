# Layer observations, 2026-10-12: what each layer has evidence for, what the protocols cost and buy, and when volume applies

Author: Claude (Sonnet 5.5, JIS-NUC), live thread 2026-10-12 15:00-15:40Z. Operator ask (Jis, 15:32Z): build observations across the indicator layers incl. Tom and Fabio; see how protocols help and what is missing to make dev faster and accurate; use a different lens on the chart without an engine read; question everything, keep what is applicable; broaden volume ("when to apply volume analysis - the context").
Sources read this session: system/LAYERS.md (generated, 10-12), research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md, research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md, research/rsi_divergence_mtf_2026-10-09/REPORT.md, research/screenshot_context_2026-10-10/REPORT.md, system/LESSONS_DIGEST.md, methodology/live_session_protocol.md, chart_read_protocol.md, screenshot_intake.md; today's reads: screenshots/2026-10-12_BTCUSDT_set_5b0e17d24d71.md, ..._8h_f3ba42e7e7d6.md, ..._30m_15m_8ff150f93dfc.md. Not read: individual backtest result files beyond their headline rows in layer_map (marked where it matters). Every number below is quoted from a file named in the same row or computed from Binance fapi on 10-12 (labelled).

## 1. One-paragraph answer
No layer in this repo has a validated edge on BTC: Tom core (STOP on the BTC encoding, gross -0.07 to -0.15 R), Fabio (v3 holdout FAIL, ledger FIX-FIRST), cross-guidance (Q33: 336 cells, 0 survivors, smallest q 0.62), RSI (divergence no edge on every timeframe, gross about 0), CryptoCred, positioning, session/timing (all FAIL or no edge), volume (553 pre-registered trials, 0 survivors). What does exist and works is the apparatus: verification (every indicator on today's three charts reproduced exactly from klines), falsifier carry-over, provenance and pre-registration. The bottleneck to "faster and accurate" is therefore not more layers; it is (a) cheap, repeatable measurement of the chart toolkit the operator actually uses, (b) clean ledgers for Tom/Fabio in their home markets before any new encoding, and (c) a way to score context reads, because the null results mostly test mechanical triggers while the traders sell judgement about context.

## 2. Fresh-eyes read of today (chart first, engine second)
Method: I wrote what the 30m chart said (volume spike, stall on less volume, OI flat, momentum repairing on lower TFs while 8h rolls over) before opening any file; it is in the extract's "Chart-first read" section. Then I checked it against klines. What the lens added that the engine-centred reads of 13:05Z did not:
1. **Timeframe disagreement is itself a state.** 15m RSI 37 over its SMA 32 with StochRSI 77; 30m RSI 36 under its SMA 38 with StochRSI 42; 8h RSI 44 with StochRSI 85.5 under its signal 89.6 after 98.3. Three timeframes, three momentum phases. No engine field or layer expresses "lower TFs repairing inside a higher-TF roll-over"; RSI layers fire per timeframe in isolation (GUIDANCE_AUDIT: RSI "separate layer", no regime state).
2. **The first read of volume was effort-versus-result, not size.** 12:30 bar 896M, then 14:30 low on 435M (49 % of that volume; delta -665 vs -2,623). That comparison needs two bars and a level; it is exactly what Wyckoff-style reading does and what no layer encodes (the repo tested "climax", "absorption", "no-demand" as single-bar events at 4h/1d, 20-80 occurrences in 4.5 years, V1).
3. **The toolkit on the chart is not the toolkit in the engine.** Bollinger bands are on every operator chart (BB 20,2 on 8h, 30m, 15m, 12h, 1d, 5m) and are "computed nowhere in code" (GUIDANCE_AUDIT gap 3); I recomputed them by hand to the 0.1 point four times today. The same for RSI/StochRSI. The verification works; the capability to read the chart the operator reads lives in my head, not in a tool.
4. **A pattern in the legends:** "Volume SMA 9" on CoinGlass shows the live bar's own volume (8h 4.728B vs real SMA9 1.98B; 30m 151.6M vs 378.9M; 15m 60.0M vs 193.4M). A reader taking the legend at face value would say "volume is 2.4x its average" when it is 2.4x because the bar is a spike, not because of the legend; harmless once known, wrong the first time. It is now in three extracts as a label issue.
5. **Something the fresh eye got wrong and the data corrected:** I saw "CVD did not confirm the 14:30 low" on the 30m panel. The running Binance total from 12:30 to 15:00 is -3,796 BTC against -2,623 at 12:30 alone: the cumulative did make a lower value. Per-bar delta shrank, the running total did not. Kept in the extract's falsify section as a dropped reading.

## 3. What each layer has evidence for, and what it assumes
(Status lines from LAYERS.md 10-12; "assumed" = parameter or rule with no test or no source in the files I read.)
| Layer | Evidence (file) | Assumed / open |
|---|---|---|
| Tom core | BTC encoding: STOP; gross -0.07 R / net -0.30 R (n=254), rerun net -2.91 R, VP anchors 46/48 CIs straddle 0 (TOM_CORE_BT*, PHASE2_RESULT) | direction rule `below_val -> long only` and "healthy trend = outside value" versus his words (card tom-direction-health-vs-sources, raw); DAX harness has 8 HIGH + 6 MED issues (lab-audit-tom-dax-bt) so no DAX number is usable yet |
| Fabio | v3 holdout FAIL; L1/OF no edge or insufficient n; ledger 8 entries vs goal 20, FIX-FIRST (FABIO_*_REPORT, lab-audit-fabio-ledger-frames) | his market is NQ/ES; BTC is a transfer; ledger dates/timestamps/entries partly unrecovered (4 raw fabio-ledger-* cards) |
| Cross-guidance (BB, LVN, regime) | Q33: 0 of 336 cells survive, fixed horizon, 0.10 % fee (MATRIX_REPORT) | Q33 tests trigger-then-fixed-horizon; neither trader exits at a fixed horizon; no Tom-Fabio signal path exists at all (GUIDANCE_AUDIT gaps 1, 6) |
| RSI / Malkan | divergence: every TF 1m..: gross about +-0.01 %, net about -0.10 % = the fee; 40/60 tolerance study done | the operator's "RSI 40/60 regime" is not computed anywhere (GUIDANCE_AUDIT) |
| Positioning (funding, OI) | funding+CVD fade FAIL (OOS net -0.045 %); OI delta 4-state descriptive only | OI/long-short are in the snapshot and unused as filters; today's OI shape (110.6K 09-21 -> 90-100K band, flat through a 1.4 % drop) has no test |
| Session / timing | T055 C2/C3 no edge; T087 prior-day-high fade net -0.036 %, t -1.72 | volume report: BTC volume has a 2x intraday rhythm; time is a confound for every volume flag |
| Volume | 553 trials, 1 marginal pass failed VALIDATION; intensity not direction (corr with next-bar range, not return); HOLDOUT 2025-07..2026-09 sealed | exhaustion/absorption untested: needs 1m/aggTrades (T071) |
| Live engine | state machine, HALT, mirror | HALT since 09:46Z (exec-halt-entry-10031, raw); VWAP/CVD books disagree with klines (state-machine-vwap-cvd-vs-klines); mirror 19 h stale |

Cross-layer pattern worth saying aloud: the repeated null is "gross about zero", not "gross positive, eaten by fees" (RSI table: gross +0.004 %, -0.005 %, +0.013 %; drift-adjusted nothing). So lowering the fee or the horizon will not rescue the encodings; and the opposite risk is live: every DEV-time "very strong" finding (volume confirms breakouts p=0.008) died on VALIDATION. Today's own 30m/1h study (section 5) shows the same temptation. The correct response so far, pre-registration and sealing HOLDOUT, is what keeps the repo honest.

## 4. Protocols: what they buy, what they cost, what to change
Bought today (observed, not assumed):
- live_session_protocol rules 1/4 (quote the number, label chart read vs system) made the volume-legend mislabel visible; recompute-from-klines found 8 exact matches in 14 claims per shot.
- B157 carried falsifiers: the 5b0e17 "floor 82590-82608" line was scored BROKEN with times and prices in the 8h extract. That is the T092 gap closed in practice.
- chart_read_protocol layer 3/4 (cross-view, higher timeframe): produced the timeframe-disagreement observation above.
- screenshot intake: the images were saved, classified and counted; no shot left `new`.
Friction observed today (each one cost a tool turn or more):
| Friction | Evidence | Change (card) |
|---|---|---|
| shot.py breaks in worktrees on git 2.24 | `--path-format=absolute` echoed, store path garbage | shot-py-main-root-breaks-in-worktrees-on |
| TF list lacked 8h while holding 7h | classify refused `--tf 8h`; CoinGlass has an 8H button | one-timeframe-map-for-the-whole-toolchai (CLAUDE.md rule "grep every TF map" was written for this) |
| the same recompute script written by hand three times (8h, 30m, 15m) | chk.py/chk2.py/chk3.py | chart-verify-py-recompute-bb-rsi-stochrs: one call per shot, prints the legend table |
| falsifier scoring done by hand | extract carried-context table | score-context-reads-automatically-carrie |
| live comparison impossible off JIS-NB | mirror 19 h stale; HALT/layers unreadable | live-mirror-stale-published-2026-10-11-2 |
| Net Delta panel unit unknown, four reads in a row | NOT_IN_DATA in every 10-12 extract | identify-the-coinglass-net-delta-panel-u |
| ship gate ~5 min for a docs-only change | `sync.py ship` ran offline gate with Maven skipped | (not carded: a docs-only path that runs only the doc/lint tests would help; propose to the supervisor) |
| session overhead: 6-8 documents before the first useful number | start ritual + STATUS + protocol + digest + LAYERS | acceptable once; a one-page "live read kit" (the three recompute formulas + file locations) would cut it |
Accuracy cost to guard: more tooling must not become a new unsourced layer. The chart_verify tool recomputes the operator's chart indicators with FORMULAS.md definitions and must stay read-only and label-only (no signal output).

## 5. Volume: when the analysis applies (context), when it is noise
Grounding: the repo's own result is that volume carries intensity (persistence 0.67 lag-1; corr 0.42-0.49 with move size; forecasts the next bar's range 1.25-1.40x) and not direction (corr with next-bar return 0.01-0.04); plain relative volume is partly a clock (36 % of 12-16 UTC 4h bars look like 2x spikes vs 6 % of 04-08 UTC); it recommends volume for risk and volatility timing, not entries.
Apply it when (ordered by how much support the repo's files give):
1. **Range and risk timing.** After a volume spike, expect the next bars to be wider. Today: 12:30 bar then 30m ranges of 1.9x, 3.1x, 1.7x, 3.5x, 1.3x the 10:00-12:00 mean (computed). A stop width sized on 10:00-12:00 ranges would have been inside the noise for four bars. (The Tom stop widths 20-63 points vs 1m ranges of 90-154 points is the same observation from the 13:05 read, G4.)
2. **Against a time baseline.** Ask "high for this slot", not "high". 12:30-13:05 window was second-largest of 12 same-slot windows (earlier extract); 8h bar 4.74B vs SMA9 1.98B (2.4x).
3. **At a level of decision, as effort versus result across visits.** The same level visited twice: 12:30 (896M, delta -2,623) and 14:30 (435M, delta -665, 251 points lower). Less effort for a lower print is the pattern a Wyckoff reader calls a test; the data cannot say which it was in real time (see below), and the repo has no out-of-sample test of it (volume report section 4.3: 20-80 events in 4.5 years).
4. **With OI scope matched.** Volume up with OI flat or down is turnover and closing; volume up with OI up is positioning being added. Today the 8h bar had 2.4x volume with OI -0.15 % (open 94,139.8 to 93,994.3) and 5m OI -1.3 % from the 12:20 peak (94,982) to the 14:15 low (93,725), then +260 back. Same-exchange only: delta/OI/volume are Binance perp, the chart's "aggregated" panels are not (12h panel was 64 % of Binance delta).
Treat as noise when: low-liquidity hours (03-05 UTC, weekends 0.62-0.72x), a baseline shorter than the daily rhythm, a single-bar "spike" on 4h/1d with n below power (volume report section 6: effects below roughly 60-170 bp undetectable), delta used to predict the next bar (corr 0.01-0.03), or any threshold with no trader quote (NO-SOURCE).
Today's question, climax or initiation? From the 12:30 close the data cannot say; afterwards: the bar closed at 23.5 % of its range (weak close), 13:00 extended 2 points beyond (new low 82423.7 on 496M), 13:30 rallied 571 on +896 delta, 14:30 undercut on 49 % of the volume and the next bar closed 83 above the low. Reading it as "initiation, then a test on lower volume, then a stall" fits every bar; reading it as "climax" would have been wrong at 12:30-13:00 by 250 points. The honest label is "unresolved in real time; resolved only by the test". That is context, not a signal, and I am not proposing a rule.
Exploratory check (hindsight, Binance 30m and 1h klines, 1,499 bars each, z >= 2 vs a 48-bar baseline, forward return in the bar's direction, no costs): at a 48-bar extreme vs inside the range, 30m n=57/45: +4.5 / -6.3 bp at 4 bars; 1h n=63/41: +15.4 / +7.8 bp. "Extreme + small body" is +/- noise-level and changes sign between 30m (-5.1 bp) and 1h (+17.3 bp) at 4 bars. Sample 31 and 62 days, one regime, 12 cells tested here, no multiple-testing control: this is the same shape as the V4 "volume confirms breakouts" DEV finding that failed validation. Recorded as a reason not to build, consistent with the repo's null.

## 6. Dependencies (what needs what first)
| To get | Needs first | Card / file |
|---|---|---|
| any Tom number that can be trusted | DAX harness fixes (lab-dax-*) -> clean holdout/design split -> untuned DAX backtest | lab-dax-readiness-gate, tom-holdout-clean-split, tom-dax-backtest |
| Tom v2 spec | ledger groups + sourced rules (done: SOURCED_RULES.md) then spike-fade recall | tom-layer-v2-spec, tom-encode-spike-fade |
| Fabio v2 spec | ledger repairs (timestamps, entries from STP label, dates) and more recap videos | fabio-ledger-minute-timestamps, fabio-ledger-*, find-more-fabio-trade-recap-videos |
| exhaustion/absorption tests | 1m/aggTrades history (T071), time-adjusted baseline, same-slot | volume report section 5; card time-adjusted-volume-context-line-for-th (read-only first) |
| chart-matched context reads | BB / RSI 40-60 regime / StochRSI as read-only fields; chart_verify | chart-verify-py-recompute-bb-rsi-stochrs |
| live engine comparison from the NUC | a mirror that is current, plus HALT resolved | live-mirror-stale-..., exec-halt-entry-10031 |
| any cross-guidance wiring | operator ruling that layers may read Tom (test_layer_boundaries says never) and a pair ledger (same/opposite side) | GUIDANCE_AUDIT gaps 2, 6 (no card; operator decision) |
| OI-shape studies | OI history: 5m openInterestHist exists only for about 30 days on Binance; oi_1m.csv collection on disk is the long-term source | keep the recorder alive (live_engine) |

## 7. Assumptions I would question, and what survives
- "No edge" is a statement about mechanical triggers with fixed horizons and a fee, in BTC. It survives. It does not test judgement about context (what the traders sell). The repo's answer is right to refuse loosening; the missing piece is scoring context reads (T092) so judgement can be measured the same way. Card: score-context-reads-automatically-carrie.
- "Volume cannot be hidden" is not in the 102-transcript corpus (volume report) and is engineering folklore; keep as hypothesis, not as design basis.
- The operator's chart toolkit (BB, RSI 40/60, StochRSI, CVD, net delta, OI) is the shared language of every read; the engine speaks a different one (VP/VWAP/CVD slope). Translating one to the other costs a read every time. Applicable: expose the toolkit read-only.
- Aggregated vs Binance CVD: panel scope varies by page (12h panel aggregated 64 % of Binance; 8h/30m panels track Binance within 0.1 %). A read must name the scope or the comparison is meaningless.
- Fresh eyes are valuable and fallible (section 2 item 5): the chart-first pass generated the question, the data check disposed of it. Keep that order.

## 8. Next steps filed as cards (python scripts/dev/tasks.py brief <id>)
1. chart-verify-py-recompute-bb-rsi-stochrs (SONNET, p2): recompute legend values for any TF at the shot clock.
2. live-mirror-stale-published-2026-10-11-2 (JIS-NB, p2): mirror 19 h stale; add publish heartbeat to STATUS.md.
3. identify-the-coinglass-net-delta-panel-u (SONNET, p3, run): unit and scope of Net Delta.
4. time-adjusted-volume-context-line-for-th (SONNET, p3): read-only same-slot volume context with effort-vs-result and OI scope.
5. score-context-reads-automatically-carrie (SONNET, p3): falsifier scoring by klines.
6. one-timeframe-map-for-the-whole-toolchai (SONNET, p4): one TF map for shot/alerts/audits.
7. shot-py-main-root-breaks-in-worktrees-on (SONNET, p3): git < 2.31 fix.
Not carded, needs an operator ruling: whether Fabio/Tom layers may read each other (GUIDANCE_AUDIT).
