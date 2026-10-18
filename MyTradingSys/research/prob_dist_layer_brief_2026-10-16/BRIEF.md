# Probability-distribution layer: design brief for the operator talk
Date 2026-10-17 | card prob-dist-layer-design-brief | build nothing, no VALIDATION/HOLDOUT read, no new gate numbers.
Every prior claim below cites file:line. "Unverified" means I could not reproduce it from files in this checkout.

## 1. Why this exists
- The operator wants a probability-distribution layer as a peer layer (PROJECT_VISION.md:94 "INTEGRATIONS ARE PEERS ... probability distribution ... each enter as a separate read layer", table row PROJECT_VISION.md:103).
- Vision says add-on, isolated first, confluence later (PROJECT_VISION.md:91-94). So: an independent read, never a gate on Tom/Fabio core.

## 2. What exists
| Thing | Where | State |
|---|---|---|
| Parked design (4-AI study, 2026-09-12/13) | research/event_probability_layer_DESIGN.md:1-4 | header says "DESIGN ONLY. Not implemented"; stale, code below exists |
| Core finding: named events (bull trap, absorption) are intent labels, not verifiable on snapshots; use observable forward kline outcomes | event_probability_layer_DESIGN.md:16-30 | still sound |
| MVP choice: Dirichlet-smoothed frequency table on coarse buckets; no HMM/ML; raw P threshold REJECTED (:53); EV+costs and fractional Kelly SUPPORTED | event_probability_layer_DESIGN.md:46-56, DO NOT BUILD :66 | design only |
| Frequency table code | backtest/prob_table.py:27 build_table (alpha=1 Dirichlet), :95 evaluate (log-loss vs baseline, min_n=100 at :101), :174 main (70/30 chronological split at :185) | exists |
| Its tests | backtest/test_prob_table.py, test_prob_table_edge.py (12 + 9 tests) | passed the 2026-09-29 gate: research/fast_track_2026-09-27/GATE_REPORT_2026-09-29.md:19 (2 bugs fixed: ts None skip; log-loss averaged over scored, not len(test)) |
| Outcome labeler | runtime/outcome_labeler.py:3 (+30/60/120m forward return per snapshot); :12-13 reads runtime_data/snapshots, writes runtime_data/outcome_labels.json | exists, hardcoded live-tree path |
| Label count | PROJECT_VISION.md:103 "10,289 labels; 5,000 gate met"; commit 7279cf8e message | claim only. outcome_labels.json is not in this checkout: unverified |
| Stale claim | "frequency-table MVP queued (NUC 033)" PROJECT_VISION.md:103; the NUC queue is gone (research/VISION_GAP_2026-10-10.md:23) | text needs fixing |

## 3. What failed or never happened
1. The MVP never produced a result. No run of prob_table.py on current labels is recorded, and research/VERDICTS.csv has no prob_table row (grep for "prob_table"/"probab" returns nothing). Passing unit tests (GATE_REPORT_2026-09-29.md:19) is not an evidence run.
2. Why the 09-13 design stalled: it was data-gated ("Awaiting data prerequisite", event_probability_layer_DESIGN.md:4; 5,000-label gate at :41). The gate was declared met on 2026-09-28 (PROJECT_VISION.md:103), but the follow-up was a queue item that vanished with the NUC queue (VISION_GAP_2026-10-10.md:23). Nobody owned the run. This is my reading, not a recorded cause.
3. Label counts overstate sample size. Labels are per snapshot at ~716/day (event_probability_layer_DESIGN.md:38) with 30/60/120m forward windows (outcome_labeler.py:3), so neighbours overlap heavily. The OI event study on the same label file had 66 and 48 events over only 17 and 15 days (research/OI_EVENT_STUDY_2026-10-10.md:12,20); no horizon had |t| above 1.3. Independent units are days, not labels.
4. Sibling probability work found nothing pooled. Candle-close study: 126 conditional arms on 1.31M BTC minutes, zero pooled candidates (commit 6f904aa6 message); every pooled arm negative after the 14bp cost screen (research/layer_lab/candle_close_2026-10-14/REPORT.md:11). Its audit: the 912-day DEV window gives at most 5 disjoint 180-day blocks, so macro probability claims are underpowered by design (research/layer_lab/candle_close_2026-10-14/CYCLE_DESIGN.md:29-31; system/tasks/candle-close-independent-audit.json).
5. Win rate misleads: a 53.2% hit rate with -10.13bp mean after costs (REPORT.md:38). Any layer must show EV after cost next to probability.

## 4. Worked case: screenshot c5e7b5c17d90 (research/screenshots/2026-10-16_BTCUSDT_c5e7b5c17d90.md)
Sequence: sweep toward the rays 81,800 / 82,459.8 / 82,900.5, volume spike, CVD up-step, OI drop on the wick (read as a short squeeze, "Reading notes" section, unproven), then a ladder-like bear-flag channel from the upper Bollinger band through the middle band to a bounce near 81,270.
- Every check is NOT_IN_DATA (rows A-01..A-04, B-01..B-06): no 1m OI candles stored; OI is a 1-per-minute REST poll since 2026-10-05 with gaps (row B-02); no ray or flag files.
- "Ladder selling" has no OI/CVD definition in either extract set (research/T064_TF_CONFIRMATION_EXTRACT.md:226). Tom's discriminator is behaviour after the poke: acceptance beyond the level = continuation; absorption and quick return = failed auction (same line).
- Operator point B-06: these moves recur everywhere, yet backtests find nothing. A probability layer is the place to ask "of all sweep + spike + OI-drop events, what happened next, and how wide is the spread?" The narrow earlier version (research/T063_STOP_RUN_OI_FLUSH.md:65, arm A0: 78 events over 5 days) was tiny.
- The case is a sequence (spike, then channel), not a single-bar state. A frequency table over a static state cannot express it; an outcome-after-event table can.

## 5. Three candidate designs
### D1. Frequency table by state (what prob_table.py is)
State = (vp_shape, price_vs_va, cvd_slope) at a snapshot; outcome = UP/FLAT/DOWN at 60m with a +-0.2% band (prob_table.py:19,27).
- Aim: live read "in this state, baseline P(up/flat/down) and its distance from unconditional".
- Data: snapshot labels (exist, location unverified). Cells: 3 features x 3-5 bins = 27-125 cells; at 100 per cell that is 2.7k-12.5k independent observations (DESIGN :33-36). Independent observations are about days, so this fails on today's weeks of snapshots.
- Power: with ~17-30 independent days it cannot resolve a 5pp edge. Needs the 6.7y daily kline history (commit 7279cf8e) re-labelled rather than weeks of snapshots.
- Risks: bins chosen after looking; overlapping windows inflate n; a state is not an event.
### D2. Outcome-after-event table (recommended first)
Event = detectable observable (sweep of a marked level, volume spike, CVD step, OI drop, ladder channel after). Outcome = forward kline path: break-and-hold, break-and-fail, continuation, reversal within N bars, plus MFE/MAE (DESIGN :18-24).
- Aim: per event, a distribution (quantiles, not one number) of forward return and path outcome versus a matched non-event control (as T063 did: events vs control).
- Data: 1m klines (1.31M BTC minutes exist, commit 6f904aa6); OI 1m poll since 2026-10-05 (short); CVD from trades. Event definitions come from the confluence-read-encode work and are frozen before outcomes are computed.
- Power: always report event count AND independent days/episodes; refuse to print a probability below an episode minimum. The minimum is an operator question (no number proposed here).
- Risks: OI history is weeks long, so the OI-drop clause is underpowered; start with price/volume/CVD-only events and add OI as it accrues.
### D3. EV / Kelly sizing for leverage
Convert D1/D2 distributions into EV after a 14bp-class cost and a fractional-Kelly size cap (DESIGN :53-56 supports EV+costs and fractional Kelly; full Kelly overbets on estimation error per the cited literature, DESIGN :55, :82).
- Aim: answer "how much leverage is justified here" as an upper bound, not a signal.
- Data: needs a realized payoff log (DESIGN sequence step 5), which does not exist for the live system.
- Risks: highest. Estimation error compounds; with underpowered inputs it emits false precision. Defer until D2 has an interval for the edge; size from the interval lower bound, not the mean.

Recommended order: D2 as the first independent read (fits the peer-layer rule), D1 re-run on kline-derived labels as a calibration baseline (log-loss vs baseline, prob_table.py:95), D3 only after both show a lower bound above cost.

## 6. Aims and non-aims
Aims: calibrated forward-outcome distributions per observable event; uncertainty (n, independent days, interval) shown beside every number; a switchable add-on that never gates core (PROJECT_VISION.md:91-94). Non-aims: a trade trigger from raw P (DESIGN :53); named intent labels (DESIGN :16-30); HMM/ML (DESIGN :66).

## 7. Risks
Overlapping windows and snapshot autocorrelation; regime non-stationarity (5 disjoint blocks, CYCLE_DESIGN.md:29); selection bias when events are picked from charts after the move (the screenshot case); labeler path hardcoded to the live tree (outcome_labeler.py:10-13); single asset; probabilities read as advice.

## 8. Open questions for the operator
1. First deliverable: a read-only distribution report per event (D2), or a live panel? Which timeframe, 1m or 5m, for the spike-then-channel case?
2. Event list: which 3 events first (sweep of a marked ray, volume+CVD spike with OI drop, ladder channel)? Who defines "ladder" (no source exists, T064 extract :226)?
3. Outcome definition: path outcome (hold/fail), forward-return quantiles, or both? Horizons: 30/60/120m as the labeler, or longer?
4. How many independent episodes before we show a probability at all? The number is yours; none is proposed here.
5. Data: accept price/volume/CVD-only events now and add OI later, or wait for OI history (poll since 2026-10-05, with gaps)? Do you want 1m OI candles stored?
6. Should your marked rays be stored per chart so events can anchor to them (T066)?
7. Cost model for EV: flat 14bp screen, or funding and spread too? Is Kelly/leverage sizing in scope now, or only after D2?
8. Where does it surface: a separate column beside Tom/Fabio reads, switch off by default? May the stale text (PROJECT_VISION.md:103, DESIGN header) be corrected?

## 9. Next step
Operator opens a design session from this file. No code is proposed before questions 1-4 are answered.
