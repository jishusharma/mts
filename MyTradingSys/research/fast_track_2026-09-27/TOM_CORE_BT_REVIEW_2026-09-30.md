# TOM_CORE_BT method review (defects only), 2026-09-30

Scope: TOM_CORE_BT.md, backtest/tom_bt.py, tom_bt_run.py, tom_bt_report.py, test_tom_bt.py, sim.py, verdict.py,
SetupCandidatesBuilder.java, l1_patch_mds.py. Sandbox: no F: data, so nothing was re-run; every item below is from code
and the printed report. Already found in MISSING_PIECES_2026-09-30.md section 2 and NOT repeated: backtest measures the
0.2% fallback stop (Java:111-124); nearest-level target choice drives WAIT_RR (Java:149-170). Paths: tom_bt.py = T,
tom_bt_report.py = RPT, TOM_CORE_BT.md = BT.

Not reviewable here: ArchiveHistoricalSource.java.new and MarketDataSnapshot.java.archive_mode.new are gitignored and
absent. The committed fetchHistoricalSnapshot (MarketDataSnapshot.java:960-1235) is look-ahead clean for what it
reads (bars cut at asOf, dropFormingBar(asOf) at :1235, price = last closed 1m close :969); the archive variant's
week/day alignment and range semantics must be checked on the NUC.

Look-ahead verdict: no look-ahead found in entry timing. Signal at asOf, first eligible bar opens at asOf (T:162-164,
212). Regime tags use bars <= t-1 (T:233-238). Fabio events are stamped at the confirmation bar (cvd_absorption) or
the firing bar (escalation) plus one tf (tom_bt_run.py:109). Only the mild items L1/L2 below.

## HIGH (2)

H1. The live rule is untested and the reason is not diagnosed; the headline substitutes a non-tradable rule.
- BT:14 histogram has max proof 5 (320 rows) but BT:6 and BT:14 say "max proof 6". Text and data disagree.
- 320 rows reach proof 5 yet only 19 are SETUP_FORMING. The 301 lost rows go to the downgrades in verdict.py:122-137
  (proof-direction contradiction, fail-closed "proof_dir error" at :124, broken-VA and CVD flow contradiction). RPT never
  counts which gate removes them (tom_bt.py:102-105 computes it per row and keeps only the final verdict).
- All 19 signals are short (BT:55). If long/short were 50/50 that is p = 2^-18 (about 4e-6): a gate is killing longs
  in archive mode (candidates: derived cvd_slope / cvd_trade_flow_aligned from l1_patch_mds.py:48-62, or fail-closed
  proof_dir on historical snapshots). The "insufficient N" verdict for the live rule (BT:524) may be an archive
  artefact, not a property of Tom. The WATCH/p4 variants (BT:6) are a different, non-tradable rule; the paragraph mixes
  them into the answer. Fix: log the verdict reason per row, tabulate the 301 losses by reason and by direction before
  quoting any live-rule N.

H2. The random-entry null is not like-for-like, so "null at least as good" (BT:6, p=0.995 at BT:343) is partly a
mechanics artefact.
- RPT:90-95: null = market entry at next-bar open, fill_window 1, always fills, no "ran"/no_fill attrition. Real = limit
  at zone, filled only on touch, and trades where price reached the target before E are dropped (T:169-170, 192 "ran" +
  240 no_fill of 4849 in BT watch variant). Dropping "ran" removes trades that a market-entry comparator would have won.
- The null keeps the real trades' day but not their conditioning (zone touch, distance-to-level <= 0.1%). A fair null
  is a random limit order at the same side/distance from the current price, same 8-bar window, same ran/no_fill rules.
- Only gross R is compared, so the fee asymmetry is not the issue; fill selection is. real -0.072 vs null -0.015 is
  small in R units and sits inside what the attrition difference can explain (not quantifiable here).
- p4 variant (BT:473): real -0.011 vs null -0.012, p=0.458: "at least as good" is true there only as a tie, and the
  headline is written from watch_episode only.
- Null is not run for episode/A (n<30, RPT:77), so the live rule has no null at all.

## MED (9)

M1. Touch-only fills on BOTH maker legs at fee 0 (T:166, 198-199, 151). A resting limit needs trade-through or queue
position to fill; here a 1-tick touch on a 1m bar fills entry and target. Stress set (RPT:25-30) has no fill-through or
queue case. With ~11% wins at 3R, target touches dominate gross. Bias is optimistic for Tom; the no-edge conclusion
survives, but the gross figure and the 0.23R fee figure (BT:6) are lower bounds on cost.

M2. Entry zone not checked to be on the passive side of price. Java:69-71 and :239-242 use abs() distance; setup types
(Java:439-474, e.g. prior_day_close, poc, vwap) are not side-constrained. tier=trigger_ready means |price-E| <= 0.1%,
either side. T:164-168 fills a zone already crossed at bar i0 at E with maker fee 0, where a real order would be
marketable (taker 5 bps = 0.25R at 0.2% stop). Count such rows on F: before trusting base fees.

M3. Fee structure "as in sim.py" is not sim.py. T:18 and FROZEN claim sim.py parity. sim.py:394 charges taker on entry
(market entry) and maker only on the target; tom_bt base charges maker 0 on entry (T:151). Rates are the same, structure
is not. No stress config equals sim.py (taker entry, maker target, taker stop): all_taker makes the target taker too
(T:152). The operator decision (sim.py fees win) is applied to the rates only.

M4. Invented exit rules not stress-tested. Order life and time stop = 8 zone-tf bars (T:16-17, RPT:133). 34% of trades
(1494/4417, BT watch variant) exit by taker timeout and drive the mean (stops 2459 at about -1R, targets 464 at about
+3R, so timeouts must average about +0.5R to reach gross -0.07). No sensitivity on hold_bars or fill_window. Also the
order is never cancelled when later snapshots drop the setup (no re-evaluation in sim_limit_trade): live order
management is not mirrored or checked.

M5. Stress config "target_first" is vacuous (BT:126 equals base; ambiguous bars 0-1 on 1m data). The real ambiguity is
inside the fill bar, where the target is never tested and the stop is (T:182-185) and on gap fills; neither is stressed.
Also base slippage is 0 on stop-market fills (T:176 only under slip>0), and stress applies slip only to stop/timeout.

M6. Episode dedupe key includes zprice (T:116-117). Dynamic zones (vwap, vwap_band, developing daily/4h levels, swing
stops) change price every snapshot, so a continuing setup becomes a "new episode". Evidence: 5984 WATCH + 19
SETUP_FORMING rows (BT:14) became 4849 signals after one-at-a-time, i.e. only ~19% reduction, for a state that persists
across rows. Consecutive trades re-enter right after the previous exit on the same levels.

M7. Bootstrap CI treats trades as iid (T:284-290, 2000 draws, percentile, no block/cluster). Trades are clustered in
time and on shared levels (M6), so [-0.34, -0.25] is too narrow. Direction of verdict (net negative) is unlikely to flip,
but the holdout interval (BT:274, n=254) and every sub-table claim are overstated in precision. Subgroup tables
(setup, tf, direction, regime, vol, year, period: RPT:237-243) are not multiplicity-adjusted; only Fabio tags get
Bonferroni-8 (RPT:268-281), per variant, not across 4 variants x 8.

M8. Holdout and "every period is out-of-sample" (BT:20, RPT:217) are contaminated by design history. Java:120 cites
Rule 32 evidence from 2026-09-12/13 (inside the holdout 2026-06-26..2026-09-26) for the stop floor; sim.py:10-13 cites
a 2026-09-26 replay of the same live period; rulings D1/D3/D4 (verdict.py:62-66 and 99-102, dated 2026-09-27) followed live
observation. Tom has tuned constants (distance caps Java:428-437, 2.0-3.5R window, floor, proof >= 3/5) that were
chosen after seeing data. The WATCH and p4 variants were added after the live rule gave n=17 (BT:6). Also the holdout
line in the paragraph is watch_episode only; the live-rule holdout is n=5 or less.

M9. Freeze and trial count are not a real pre-registration. FROZEN.md is written by the report script itself after
snapshots and rows exist and is overwritten on every run (RPT:123-139, git HEAD noted "working tree not committed").
Registry dedupe is by run_id = date (RPT:115, 176-183): a same-day re-run after a code or adapter fix adds no rows, so
N_trials is understated. The 16 rows are 4 variants x 4 stress configs, not independent trials, and the WATCH/p4
variants were not pre-declared. DSR/PBO "does not apply" (BT:530) is asserted because all variants are reported, but
variants were chosen post hoc.

## LOW (6)

L1. Vol terciles use full-history cut points (RPT:143-147): future data labels the regime of each trade. Descriptive only.

L2. Verdict gate uses the full sample, not the OOS subset: RPT:288-295 tests n>=100 and CI on all periods while
reporting the OOS count beside it; a pooled result could pass the protocol on hist alone. Not triggered today (all
negative).

L3. Funding ignored on the claim "<= 8 zone bars = at most 8h" (T:20, BT:18). True for hold only; 1h-zone trades hold up
to 8h after up to 8h of pending order, and every live-rule signal is short (BT:55), so the funding sign is one-sided.
Small at 0.2% stops but unstated in sign.

L4. archive patch hard-codes trade_flow confidence "HIGH" (l1_patch_mds.py:70) where the live path can emit LOW; it is not
shown whether any verdict.py or score path reads it (verdict proof comes from score.proof_count, verdict.py:86). Check.

L5. "n signals" in every table is post one-at-a-time (RPT:163 via T:205-229); skipped overlapping signals are never
counted, so fill_rate and signal counts are conditional on earlier trades' outcomes.

L6. Tests do not cover the gaps above: test_tom_bt.py has no case for a wrong-side zone (M2), a touch without
trade-through (M1), the fill-bar target (M5), episode dedupe when zprice drifts (M6), nor for random_entry_null at all
(only sim/signals/stats helpers are tested). The null and report paths are unguarded.
