# Tom and Fabio setup review (technical), 2026-10-31

Operator order 2026-10-31 via the login C coordinator ("Tom and Fabio setup review", Opus). Feeds D11 stream A "setup truth"
(`research/v1_plan_2026-10-20/D11_PROGRAMME.md:29`) next to the operator-facing sheet `research/setup_review_2026-10/SETUP_REVIEW.md`
(22 setups, his verdicts pending). That sheet says what each setup is; this one says what our code does with it, what was measured,
on which dates, and what is wrong or untested. No trading verdict: no Tom or Fabio setup has a fee-net out-of-sample pass.

Paths are relative to `MyTradingSys/` unless they start with `src/` or `F:/`. Quotes are copied from the catalog
(`research/setup_catalog_2026-10-15/SETUP_CATALOG.md`, "CAT"), which took them from captions checked by `check_spec_quotes.py`
(CAT:18); captions are machine-translated (Tom) or auto (Fabio): "a quote proves what the trader says he looks at, never a price,
date or time" (CAT:20). SOURCED = his words with a cite; OURS = our choice. Numbers are copied from the cited reports; the
arithmetic marked "OURS check" is mine, from FORMULAS.md, not from study code.

## 0. Read first: which dates each study used

Project split (`backtest/splits.py:4-6`, guard at :26-29): DEV 2022-01-01..2024-06-30, VALIDATION 2024-07-01..2025-06-30,
HOLDOUT 2025-07-01.. sealed. The desk lock 2022-04-01 is "a subset of this DEV" (`splits.py:12-13`). The brief said
"DEV 2022-04-01..2024-06-30": both windows are listed below; `splits.py` is the guard the code enforces.

| Study | Window read | Inside DEV? | Cite |
|---|---|---|---|
| Tom VP return-to-value count (57.2 %) | 2022-01-02..2024-06-30, 911 days | YES (splits.py); starts 89 days before the desk lock | `research/tom_transfer_2026-10-11/vp_return/RESULT.md:4` |
| Tom sim_desk VP trade tries 1-12 | 2022-04-01..2024-06-30 | YES (both) | `research/sim_desk/studies/tom_vp.py:37` |
| Tom PHASE2 level-touch study (48 streams) | 2022-01-01..2026-10-07, 1741 days | NO: reads VALIDATION and HOLDOUT | `research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:5`; `phase2/results.json` coverage first_ms 1640995200000, last_ms 1791417540000 |
| Tom core BT (old Java engine) 0929 + 1007 | hist 2022-01..2025-08, "dev" 2025-09..2026-06, "holdout" 2026-06-26..09-26 | NO: its "dev" lies in project HOLDOUT; its holdout was read twice (B147) | `research/fast_track_2026-09-27/TOM_CORE_BT.md:20`; `TOM_CORE_BT_RERUN_2026-10-06.md:3-9` |
| Tom stop width (B146) | hist 2022-01-20..2025-08 + dev 2025-09..2026-06 | NO | `research/fast_track_2026-09-27/TOM_STOP_WIDTH_2026-10-09.md:3`; `backtest/tom_stop_width.py:25-26` |
| Tom DAX BT / recall | DAX 2024-11..2026-04 (own split) | n/a (DAX); report is a smoke and says do not quote | `research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:1` |
| Fabio v3 L3 (Models A-D) | IS 2024-12-02..2025-12-31, OOS 2026-01-01..06-25 | NO: VALIDATION + HOLDOUT era (data starts 2024-12-02) | `research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:18-20` |
| Fabio L1 kline proxies | 2022-01-01..2026-09-26, 70/30 chronological | NO: OOS (~2025-04..2026-09, OURS arithmetic) is VALIDATION + HOLDOUT | `backtest/layers/fabio/FABIO_L1_REPORT.md:5-8` |
| Fabio order-flow conditional model | 2026-07-01..2026-09-28 | NO: HOLDOUT era, and overlaps the v3 holdout 2026-06-26..09-28 | `backtest/layers/fabio/FABIO_OF_REPORT.md:13-15`; `PRE_REG_FABIO_V3.md:13` |
| Fabio escalation 1h / LVN-touch 1h event tables | 2022-01-01..2024-06-30 | YES (descriptive, no fees) | `research/layer_lab/reports/2026-10-17_gptb-fabio-escalation-event-table.md:3`; `..._gptb-fabio-lvn-touch-event-table.md:4` |
| Cards `tom-btc-dev-backtest` / `-encode` / `-validation` / `-other-setups` | "DEV 2024-12-01..2025-03-31", "VALIDATION 2025-04..06" | NO: both windows are project VALIDATION | `system/tasks/tom-btc-dev-backtest.json` (note), `tom-btc-validation.json` (title) |

Consequence: the only DEV-clean, fee-net TRADE numbers for either trader are the Tom sim_desk tries (all negative, section 2.2).
HOLDOUT 2025-07+ has already been read for the VP level-touch family (PHASE2) and for Fabio's order-flow family (L1 OOS, v3 IS second
half + OOS, OF model). A later promotion read for those two families needs a window none of them touched (default taken, section 7).

## 1. Setup status table

Status keys: NOT CODED; CODED-UNSCORED (code exists, no fee-net outcome); NEG (fee-net negative); COUNT (a count, no trade).

| Id | Setup (plain) | Our code | Best evidence | n | Window clean? | Status |
|---|---|---|---|---|---|---|
| TOM-1a | Fade a rushed push at the session top | old `ct_short` (`src/main/java/datafeed/SetupCandidatesBuilder.java:464-471`); new `SpikeFadeDetector` `fade_short` (`src/main/java/datafeed/SpikeFadeDetector.java:18-42`) | old engine watch_episode net -0.30 R; new: DAX recall DESIGN FAIL, no outcome | 4417 / 5 designs | NO | NEG (old) / CODED-UNSCORED (new) |
| TOM-1b | Swing fade, B-profile top / gap rejection (daily) | none | - | - | - | NOT CODED |
| TOM-2 + 70/30 claim | Sell top / buy bottom of balance; return to value after leaving it | `backtest/vp_return_to_value.py`; `research/sim_desk/studies/tom_vp.py` | count 57.2 % vs placebo 46.8 % (near-band placebo 55.8 %); trades -0.22..-0.26 R | 871 events; 918-1812 trades | YES | COUNT + NEG |
| Level touch (POC/VAH/VAL, pivot-anchored "last major high to low") | bounce at level, +-1 ATR barriers | `backtest/vp_pivot_probe.py` | all 48 streams net -0.185..-0.248 R; 0 beat placebo | >= 1055 per stream | NO | NEG |
| TOM-3 | Resting sell below the last volume step | none | - | - | - | NOT CODED |
| TOM-4 | Trend pullback to VWAP / value | old `tc_long` only (`SetupCandidatesBuilder.java:489`) | only inside the old-engine aggregate | - | NO | CODED-UNSCORED |
| TOM-6 / TOM-12 | Breakout / break-in | none (chart-lab card blocked, window) | - | - | - | NOT CODED |
| TOM-7 | VWAP balance scalp | old `scalp_long/short` | 7 live-rule signals, net +0.06 R | 7 | NO | n too small |
| TOM-8, 9, 10, 11, 14, 15, 16, 17 | gaps, crude lead, news V, candles, hedger top, LVN speed scalp | none | - | - | - | NOT CODED (8-11 not visible on BTC: CAT:51-54) |
| FAB-1 | Balance + CVD pressure, break on volume | v3 S1/S2/S5 -> Model A (pullback to LVN, OURS) (`backtest/layers/fabio/v3/models.py:274-322`) | Model A: 12 IS trade days over 48 cells, 0 OOS | 1 (chosen cell) | NO | CODED-UNSCORED (never fires) |
| FAB-2 / FAB-2v | Absorbed push, rewarded effort; failed auction then other side | v3 S3, S5D -> Model D (`v3/models.py:231-260`) | 8 IS trade days over 24 cells, 0 OOS | 1 | NO | CODED-UNSCORED (never fires) |
| FAB-4 | Failed breakout back into prior-day value (5m close back inside) | v3 Model B, a different definition (`v3/models.py:121-191`) | 42 IS fills all scored 0 R as "unmanaged" | 0 scored | NO | CODED-UNSCORED (scoring bug, 4.3) |
| FAB-5 | Buyers protect a level / VAL fade ("AAA") | none (needs L2) | 11 of his 17 assigned trades, none dated | - | - | NOT CODED |
| FAB-6 | IVB, first 30 min of US open | v3 Model C (`v3/models.py:194-228`) | OOS mean -0.1038 R/day, CI -0.2087..-0.0053 | 79 OOS trade days | NO | NEG |
| FAB-8 | Rejection at the lowest-volume price inside a swing's value area | `backtest/layers/fabio/fabio_volume_fvg.py` (kline proxy) | real ~ random-bin control at 5m/15m | 93 (1h OOS) | NO | NEG (proxy) |
| FAB-9, FAB-10 | Delta print zone; volume ledge | none; catalog candidates only (CAT:1474-1503), absent from the operator sheet | - | - | - | NOT CODED |
| CVD absorption (FR-16), escalation (FR-18) | kline-delta proxies | `fabio_cvd_absorption.py`, `fabio_escalation.py` | 0 cells survive 0.10 % RT fees with PBO < 0.5 | 109-16999 | NO | NEG (proxy) |

## 2. Tom

### 2.1 TOM-1a spike / imbalance fade (the setup most of his real trades sit in: 11 assigned examples, CAT:44, CAT:74)
- SOURCED rule (CAT:312-320): idea "I can clearly see that there's no liquidity left" (k0zm5NYn0IQ:21-22); proof "the market formed a
  completed auction at the top" (k0zm5NYn0IQ:84-86); proof count NOT STATED: "you need many, many parameters that speak in your favor"
  (zQTbdEweG3c:23-26, CAT:353); stop "20 points in the DAX ... I don't have any reference values up here" (k0zm5NYn0IQ:22-26) or
  "above the bell" (n7ZSkjb7JXs:299-301); target "the entire distance below the start of the impulse" (T6hDJcHrVBM:170-172);
  session 08:30/09:00-17:35 Berlin (T6hDJcHrVBM:94-97); arithmetic "hit rate ... 40 to 45% ... riskreward ratio of 1.5" (k0zm5NYn0IQ:549-552).
- OURS, encoding 1 (old Java engine, run by `backtest/tom_bt.py`): proof thresholds 3 (WATCH) / 5 (SETUP_FORMING) (`backtest/verdict.py:121-126`);
  stop = swing extreme beyond the zone, no floor since 0c34a2d (`SetupCandidatesBuilder.java:129-137`); target = nearest POC/HVN passing
  net R:R (`:139-156`); limit at zone, 8 zone bars order life and timeout (`tom_bt.py:260-261`); fee profile `FEES_DERIBIT` = maker 0 at entry
  and target, taker 0.0005 at stop/timeout (`backtest/fees.py:48`).
- OURS, encoding 2 (`SpikeFadeDetector`, flag `mts.spikeFade`): A1 sell limit at session extreme only; window 07:00-17:35 Berlin, lookback
  20 sessions; A_S2_POINTS 20.0 SOURCED; A_S1_MAX_DISTANCE_PCT 3.0 OURS (`SpikeFadeDetector.java:36-42`). BTC minimum stop 0.40 % taker /
  0.20 % maker is OURS, 1.5-5x wider than his 0.08-0.26 % (`research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:312-324`; RECALL_DAX.md:22).
- Evidence: run 0929 live rule 17 filled, net -0.19 R, CI -0.76..0.46 (`TOM_CORE_BT.md:27-34`); watch_episode 4417 filled, gross -0.07,
  net -0.30 (CI -0.34..-0.25), random-entry null "at least as good" (`TOM_CORE_BT.md:6`). Rerun 1007 without the stop floor: live rule 0 filled,
  watch_episode 2880, net -2.91 R driven by tiny stops (fee ~2.76 R/trade) (`TOM_CORE_BT_RERUN_2026-10-06.md:13-22`). B146: gross R negative in
  every stop-width bucket (`TOM_STOP_WIDTH_2026-10-09.md:6-19`). Encoding 2: DAX recall best 2 of 5 at k=1, DESIGN FAIL, no outcome computed
  (`research/tom_transfer_2026-10-11/RECALL_DAX_V2.md:3,24-31`; `backtest/tom_v2_recall.py:1-8`). None of this is DEV-clean.
- Risks (file:line): touch = fill for entry and target at maker 0, `through_ticks` default 0 (`tom_bt.py:194-198`); fill bar tests the stop only,
  so the "target_first" stress is vacuous (`tom_bt.py:210-213`); zone can already be crossed at signal time and still "fill" (abs distance,
  `research/audits/tom_ctlong_below_zone_2026-10-18.md:6-9`); iid bootstrap on clustered trades (`tom_bt.py:327-333`); historical snapshots
  lack book/funding/OI so the proof ceiling caps the live rule (`TOM_CORE_BT.md:14`); the archive snapshot adapter (where a profile look-ahead
  would sit) was never inspected (`TOM_CORE_BT_REVIEW_2026-09-30.md:9-12`).
- Untested: his stop and target locations on BTC; A2/A3 entry paths; profile and aggressor proofs; any DEV run of encoding 2.

### 2.2 TOM-2 balance counter-trade and the 70/30 return-to-value claim
- SOURCED: "only the case about 30% of the time and the other 70% he will try and strive to run back here"
  (`extracts/processed/tom/extract_BB3c8visnkI.md:38`); value area = 70 % ("traded 70% of the total liquidity", :28); TOM-2 "short trades up
  here and long trades down here" (BVpYGKz9PBU, CAT:46). His profile is a cash-session profile: NOT_IN_DATA for BTC; UTC day is OURS
  (`vp_return/RESULT.md:71`).
- Count study (`backtest/vp_return_to_value.py`, pre-registered `vp_return/PRE_REG.md`): event = first 5m close outside prior-day value; outcome =
  a later 5m bar of the same UTC day touches prior-day POC. Real 57.2 % (CI 53.9..60.7, n 871) vs placebo 46.8 %, +10.4 pp (CI 6.4..14.4)
  (`RESULT.md:8,15-17`). His 70 % is above the CI. Post-hoc: placebo bands within 1 ATR return 55.8 % vs real 55.0 % on the same days,
  -0.8 pp (CI -5.2..3.7) (`RESULT.md:10,47`): the pooled excess comes from far-shifted bands; a band near value behaves like value.
  After 3/6/12 closes beyond the edge the return share drops 5.9/9.4/11.7 pp (`RESULT.md:53-55`). UNCHECKED: the independent re-derive
  card `gpt-rederive-tom-vp-return-to-value` is ready, not run (A-20261018-1: cite as UNCHECKED until tagged).
- Trade tests of the same idea, DEV desk window (`research/tom_transfer_2026-10-11/VP_VIDEO_CONCEPT_CHECK_2026-10-31.md:40-57`):
  RETURN (market entry next 5m bar, stop 1 x ATR14(1h) OURS, target POC) n 1054, -0.224 R (-0.300..-0.148); FADE edge->POC n 1765,
  -0.238 R, win 58 %; ACCEPT -0.202..-0.264 R; weekly RETURN n 148 -0.172 R and weekly ACCEPT n 365 +0.081 R (-0.206..+0.385), both
  NOT ENOUGH DATA. No placebo column and no gross R in that table.
- Risks: target at maker fee with touch fill and no slip (`research/sim_desk/studies/_bars.py:165-167`); stop 1 x ATR is OURS, not his "move
  back above this level" (CAT:424); event-bar POC touch excluded by design (`vp_return_to_value.py:54`); late-day censoring fixed (f38e17805),
  4 of 871 events have < 12 bars left, immaterial (`RESULT.md:66-67`).
- Contradiction: Gemini method review (`research/gemini_burn_2026-10-31/METHOD_REVIEW_TOM_VP_STUDY.md:21,55-65`) cites
  `vp_return_to_value.py:58,65` behaviour that the censoring fix already changed (now `:55-56,61,68`): its finding 1 is stale.

### 2.3 Level touch at POC / VAH / VAL (pivot-anchored and calendar profiles), PHASE2
- SOURCED anchor: profile "from the last major high to the last major low" (sQ_biBKhPVU:19, FORMULAS.md:418); VA 70 % (1utSjHs_Mq8:19).
  Everything else NO-SOURCE: bin 10 USD, pivot n {2,3,5}, size k, R = 1 x ATR14(1h), H = 48 x 5m, placebo d cycle (FORMULAS.md 18.1-18.6;
  `PHASE2_RESULT.md:25-26`).
- Code `backtest/vp_pivot_probe.py` follows FORMULAS 18.5: limit at level on touch, stop-only on the touch bar, stop first on ties.
- Result: 48 streams, every net R taker -0.185..-0.248, maker -0.10..-0.16, gross -0.042..+0.010; 46/48 placebo CIs straddle 0, two worse,
  none better; best weekly POC +0.032 (CI -0.003..0.065); every year 2022-2026 negative (`PHASE2_RESULT.md:10-17`). Independently matched
  to `phase2/results.json` by the Gemini re-derive (`research/gpt_rederive_2026-10-26/layer_rederive/tom.md`, 20 of 20 MATCH).
- OURS check (FORMULAS 18.5, all-taker): fee in R = (0.0005 L + 0.0005 exit)/R ~ 0.001 L/R; the reported ~0.19 R fee (PHASE2_RESULT.md:12)
  implies R ~ 0.53 % of price, plausible for ATR14 of BTC 1h bars. Gross ~0 means the loss is the fee, as reported.
- Window: reads VALIDATION and HOLDOUT (section 0). The result is negative, so nothing was promoted from it, but those dates are now
  exposed for this family.
- Untested: Tom's own stop/target (Phase 3 never ran, `PHASE2_RESULT.md:23-24`); regime split (no sourced phase labels, :15).

### 2.4 TOM-4 trend pullback, TOM-6/12 breakout and break-in, TOM-7 scalp
- SOURCED (CAT:537-619): "wait until the VWAP gives me a pullback", "not with quick spikes but with real acceptance", stop "below the last
  volumes" (YkclL6xgu-s), target "where there used to be large volumes in the past". Stop distance, time stop and entry trigger NOT STATED (CAT:601).
- Code: old `tc_long` (VWAP, healthy uptrend, no short) and `scalp_long/short` only inside the old engine; no stand-alone test.
- Card `tom-btc-other-setups` (the TOM-4/6 event study) holds `result` "504 candidates; 100 blind charts" while its own report says BLOCKED,
  "No event study was conducted", pre-flight candidates=105 read from a forbidden window "must not be used"
  (`research/layer_lab/reports/2026-10-22_tom-btc-other-setups.md:1-9`). Treat 504/100 as void.

## 3. Fabio

Shared facts: he trades NQ/ES in the New York cash session; no BTC in his transcripts (`research/fast_track_2026-09-27/FABIO_BTC_RESEARCH_2026-09-30.md:15-17`).
v3 thresholds that decide whether a trade exists: 0 of 8 grid rows SOURCED (`research/_archive/loose_2026-10/FABIO_V3_SOURCING_2026-10-02.md:52`);
the two numbers in his words are the 30-minute IB and the break-even day floor (`FABIO_PROVENANCE_AUDIT_2026-10-01.md:39-40`). His NQ initial stops:
median 14.81 pt of 13 (~0.06 %), our floor f 0.3-0.5 % (`backtest/layers/fabio/run_v3_l3.py:41`), 5-8x wider, no quote.
v3 fills: limit fills when price trades 1 tick through, at the limit price, no queue (`v3/fill.py:175-179`); maker 0 / taker 0.0005 (Deribit,
`backtest/fees.py:32-33`); funding not charged (`v3/costs.py:265-277`); the fill bar tests the stop on the whole bar range (pessimistic, `v3/manage.py:319-330`).

### 3.1 FAB-1 balance + CVD pressure, break on volume (v3 Model A)
- SOURCED: "the market was balanced ... the cumulative volume delta is pretty huge even before the breakout" and "the first moment that we had
  some kind of follow up on volume and confirmation from price was exactly this candle. This was my first position" (0jM5Y31YJak, CAT:1142,1148).
  Stop NOT STATED; break-even "once it explodes" (CAT:1152-1153).
- OURS: Model A does not enter on that candle; it waits for a pullback to the nearest LVN that retraced >= 25 % of the leg (`v3/signals.py:172-179`;
  `v3/models.py:312-318`). The spec itself says the 25 % retrace is "not in these transcripts" (`FABIO_V3_SPEC.md:226`).
- Evidence: 12 IS trade days over 48 cells, 0 OOS (`PRE_REG_FABIO_V3.md:44`; F:/MTS/data/fabio_v3_bt grid files, not in git). Not a loss, a
  rule that almost never fires (balance true in ~3 % of windows).
- Untested: the literal first-candle entry; adds (not executed, `v3/manage.py:199-201`).

### 3.2 FAB-2 / FAB-2v absorbed push, failed auction (v3 S3, S5D, Model D)
- SOURCED: "the buyers getting completely absorbed ... the punch to the wall ... the rewarded effort of the sellers" (8CWKfoSJu3c, CAT:1181);
  "capitalize on the failed auction of the seller and then aggression of the level of the buyers" (fZlNGWvd2Ko, CAT:1213). Absorption threshold
  "UNDEFINED (almost zero)" (FABIO_RULEBOOK.md:152). Stop NOT STATED.
- OURS: S3 z-scores L=60, r_abs 0.25, r_ctl 1.0, z_hi grid (`v3/signals.py:29-31,232-261`); Model D rest 3 bars (`v3/models.py:34`).
- Evidence: 8 IS trade days over 24 cells, 0 OOS: NOT EVALUABLE (`PRE_REG_FABIO_V3.md:47-48`).
- Contradiction: spec S8(b) exits on `S2 == -s` yet says a new balance where the other side was absorbed "is a HOLD" (`FABIO_V3_SPEC.md:93-95`);
  the golden test skips it as a known gap (`v3/tests/test_fabio_golden.py:362`). His "three losing trades to stop" (DyS79Eb92Ug, CAT:263) is coded
  as a -3 R day stop (`v3/day_gates.py:16`), a different rule (helpers not applied in L3 anyway, `v3/engine.py:103`).

### 3.3 FAB-4 failed breakout back into prior-day value (v3 Model B, different definition)
- SOURCED (9IliXww64uM, ES; CAT:1252-1285): prior-session value "70% of the trading activity happened within this range"; trigger "negative delta
  with a positive price action ... the 5-minute was about to close right over here and that was my signal"; target "the other side of the range";
  stop a chart point only. Speaker conflict: CAT:1247 says Fabio, `research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md:37-40` says Andrea Cimi.
- OURS Model B: rolling 60/120/240 x 1m balance, reclaim within 5 x 1m bars (`v3/models.py:128-135`), target opposite balance edge (:167).
  Not his prior-day value area, not his 5m close.
- Scoring bug: `v3/engine.py:100-102` returns None for Model B, so `run_v3_l3.py:108-109` records each B fill as `(0.0, "unmanaged")`. All 42 IS
  and 4 OOS B fills were scored 0 R. Model B was never measured; the L3 table shows it as a flat zero, not as missing.
- FAB-4 as he states it needs only klines (prior-day value from 1m volume, 5m close, kline delta = 2 x taker-buy minus volume): testable on DEV now
  (test 3 below).

### 3.4 FAB-5 buyers protect a level / value-area-low fade ("AAA")
- SOURCED: "a protection wall ... absorb the first time, strike again this area, absorb the second time" (FawPrRUGNpk, CAT:1328); "covered below the
  protection level for buyers" (DyS79Eb92Ug); "Why AAA setup? Value area low." (DyS79Eb92Ug). The only Fabio row with a stop location in words (CAT:72).
- No code. The wall is heat-map L2, not on disk. 11 of his 17 assigned trades, all NQ frames, no minute timestamps, date match AMBIGUOUS
  (`research/fabio_date_match_2026-10-18/DATE_MATCH.md:3`). A BTC proxy (repeated absorption at one price from aggTrades) is OURS and unbuilt.

### 3.5 FAB-6 IVB, first 30 minutes of the US open (v3 Model C), the only scored Fabio model
- SOURCED: "the bottom of the first 30 minutes is giving a lot of value in the direction of the day" (LQvv5xgy_ik, CAT:1396); entry, stop and target
  NOT STATED there (CAT:1399-1401). IB = 30 min SOURCED; stop at IB mid, rest at IB edge, one try per day, S4 big push, f, g all OURS
  (`FABIO_V3_SPEC.md:126-129`, "May not port").
- Evidence: chosen cell C|m5|f0.005|rest|g0.8, OOS 79 trade days, mean -0.1038 R/day at 2 bps (0 bps -0.0802, 5 bps -0.1391), CI -0.2087..-0.0053,
  L3-FAIL (`PRE_REG_FABIO_V3.md:46,48`); all 16 C cells negative IS and OOS (grid files, not in git).
- OURS check: maker entry 0 + taker exit 0.0005 at D = 0.5 % gives 0.10 R fee per trade; -12.45 R over 79 days ~ -0.16 R per trade day, so gross is
  also negative (about -0.06 R per trade if one first leg per day), not a fee-only loss.
- Risk: the rest limit at the IB edge stays live until window end with no invalidation cancel (`v3/models.py:221`).

### 3.6 Kline-delta proxies (CVD absorption, escalation, volume FVG = FAB-8) and the order-flow model
- Results (`FABIO_L1_REPORT.md:33-38,53-67`): fixed horizon h=5 bars, 0.10 % RT taker; none survives fees out of sample with PBO < 0.5; the one
  positive net cell (escalation 1h, +0.113 %, n 182) has PBO 0.756. FVG real ~ random-bin control.
- Code vs doc: `fabio_cvd_absorption.py:88-89` accepts any higher low (`price >= prev*(1-tol)`, no upper bound) while the quote says price "still
  on the same level" (CVD_CONCEPTS.md:26); `fabio_escalation.py:2-4` promises a breakout but the event fires on a record bar whose high/low stays
  within tol of the level (:45-48, :117-123), no break test; CVD never resets per session (`fabio_cvd_absorption.py:13-15`). Entry at the event
  bar's close (`run_backtest.py:83`), for FVG after the touch already happened (:200-203): mild look-ahead.
- `FABIO_OF_REPORT.md`: 0 of 64 true-flow variants net-positive OOS n >= 30 (:120-128); run with legacy fees 3.5 bp / -1.5 bp (banner :1-4), before
  the DST session fix (B102, 2026-10-04), driver now in `archive/cleanup-2026-10-08/fabio_of_model/` (reproduce line :10 stale). Spec: do not reuse
  (`FABIO_V3_SPEC.md:273`). `fabio_of_model.py:8-9` docstring states fixed UTC sessions; code is DST-aware (:118-124); card
  `fabio-of-model-docstring-dst-sessions` ready.

## 4. Cross-cutting problems (ranked by how much they change a conclusion)

1. Windows (section 0): most Tom and Fabio numbers were measured on VALIDATION/HOLDOUT dates. Nothing was promoted, so no false pass exists,
   but HOLDOUT 2025-07+ is spent for the VP level-touch family and for Fabio's order-flow family.
2. Fabio Model B scored 0 R per fill (`run_v3_l3.py:108-109`): the L3 table hides "not measured" as "zero".
3. The `tom-btc-*` chain is blocked on windows that are VALIDATION; its card text needs a DEV re-scope before any worker can take it.
4. Touch = fill at the limit price everywhere (`tom_bt.py:194`, `vp_pivot_probe.py` 18.5, `v3/fill.py:175-179`, `_bars.py:165-167`); no queue, no
   trade-through requirement. For the negative results this only makes them less negative than reality; for any future positive it must be stressed.
5. Our stops are 5-8x (Fabio) and 1.5-5x (Tom) wider than theirs, by fee design. Their payoff (Fabio 1:3 to 1:19, management and adds) was never run.
6. FORMULAS.md has no section for Fabio v3 (S1-S8, Models A-D) or for the VP return count; an independent re-derivation has no written formula to
   start from (FORMULAS.md headings 1-27).
7. Tests: v3 129 passed / 4 skipped; look-ahead forcing test covers Model C on one 35-bar fixture only
   (`backtest/layers/alerts/test_lookahead_forcing_fabio_v3.py:50-92`); `pending_test_fabio_v3.py` has 1 failing test (`test_X01_reexports`,
   `BAL_POC_BAND` not re-exported) and is never collected.

## 5. Contradictions (docs vs code, docs vs docs)

| # | Side A | Side B |
|---|---|---|
| 1 | CAT:353 TOM-1a proof count NOT STATED | `backtest/verdict.py:121-126` hard 3 / 5 (OURS) |
| 2 | `research/gemini_burn_2026-10-25/layer_facts/tom.md:38,43` "no fitted parameter, every period out-of-sample" | `TOM_CORE_BT_REVIEW_2026-09-30.md` M8 (constants chosen after data) and B147 (holdout read twice) |
| 3 | card `tom-btc-other-setups` result "504 candidates; 100 blind charts" | its report: BLOCKED, no event study, 105 candidates void |
| 4 | Model A called "LVN pullback trend (FBR:28-29)" (`FABIO_V3_SPEC.md:109`) | P35 retrace "not in these transcripts" (`FABIO_V3_SPEC.md:226`) |
| 5 | FAB-1 entry on the first confirming candle (CAT:1148) | Model A pullback limit (`v3/models.py:312-318`) |
| 6 | FAB-4 prior-day value, 5m close (CAT:1252-1261) | Model B rolling 1m balance, 1m reclaim (`v3/models.py:128-135`) |
| 7 | S8(b) exit clause (`FABIO_V3_SPEC.md:93`) | same paragraph: other side absorbed is a HOLD (:94-95) |
| 8 | escalation docstring "breakout" (`fabio_escalation.py:2-4`) | no break condition (:45-48, :117-123) |
| 9 | CVD absorption quote "same level" | any higher low accepted (`fabio_cvd_absorption.py:88-89`) |
| 10 | `fabio_of_model.py:8-9,26` fixed UTC sessions, maker 0.02 % | code DST-aware (:118-124), `FEE_MAKER = DERIBIT_MAKER` 0 (:45) |
| 11 | v3 holdout end 2026-09-28 (`PRE_REG_FABIO_V3.md:13`) | 2026-09-26 (`FABIO_V3_SPEC.md:257-258`) |
| 12 | 9IliXww64uM speaker Fabio (CAT:1247) | Andrea Cimi (`CVD_CONCEPTS.md:37-40`) |
| 13 | CAT:72 "Fabio 6 setup rows" | CAT:1503 "8 rows" (FAB-9, FAB-10 added); operator sheet lists 6 |
| 14 | `v3/README.md:29` "tests/*.py.new (93 tests)" | tests are `.py`, 129 pass + 4 skip |

## 6. Next tests, pre-registered here before any run (ranked)

Rules for all: DEV only, `splits.py` guard (`assert_dev_only`), desk lock 2022-04-01..2024-06-30 unless the test says otherwise; VALIDATION and
HOLDOUT untouched; costs FORMULAS 13 (taker 0.0010 RT + slip 0.0002, funding charged) unless stated; day-block bootstrap 2000, FORMULAS 18.7;
Holm across the tests run in one batch. Power (FORMULAS-independent arithmetic, decision d-flexible-min-n-per-case):
n = ((1.96 + 0.8416) x sd / delta)^2 = 7.849 x (sd/delta)^2; for R outcomes sd ~ 1 R: delta 0.10 R -> 785, 0.15 R -> 349, 0.20 R -> 196;
for a share near 50 %: delta 5 pp -> 785. Desk-lock DEV has 822 days (275 + 365 + 182).

1. Re-derive before citing (no new data): run the ready card `gpt-rederive-tom-vp-return-to-value` (57.2 / 46.8 / 51.2 / 47.8 / 45.5). Pass = all
   SAME within rounding. Cost: one CODEX card.
2. Tom return-to-value with the near-band placebo as PRIMARY, on fresh pre-DEV data `dev_ext_2019_2021` (A-20261018-2), same code and rules as
   `vp_return/PRE_REG.md` except: primary = real minus placebo restricted to |d| <= 1. H1: diff > 0 with CI lower bound > 0. Expected n ~ 870 events
   per 911 days (fire rate 95.6 %, RESULT.md:19); detectable diff ~5 pp at 80 % power. If it fails, the 70/30 claim has no value-specific content on BTC.
3. FAB-4 as he states it, BTC 1m klines, DEV desk lock: prior UTC-day value area (FORMULAS 18.1, bin 10 USD NO-SOURCE, VA 70 % SOURCED); probe =
   a 5m close outside VAH/VAL; trigger = the first 5m close back inside with 5m kline delta against the probe direction (delta = 2 x taker-buy - volume,
   OURS proxy); entry market at the next 5m open; stop = probe extreme + 1 tick, floored at W_min = round-trip/0.25 (OURS, as TOM_LAYER_V2_SPEC:312-324);
   target = opposite value edge; exit at UTC day end. Primary: mean net R vs a placebo with the value area shifted by d x ATR14(1h), |d| <= 1.
   Pass: net R > 0 with CI lower bound > 0, n >= 349 (delta 0.15 R). Fill: market entry, stop at stop price or worse open.
4. TOM-1a encoding 2 on BTC DEV with his target (start of impulse) and the W_min stop, after the price-arm fire rate is recorded (no outcome yet):
   pre-register fire rate first; outcome run only if n >= 349 over 822 days.
5. Fabio v3 Model B scoring fix (section 4.2), then a DEV run once DEV order-flow bars exist (public aggTrades 2022-04..2024-06; data build card).
   Until the data exists, Fabio v3 has no DEV test at all.
6. FAB-6 IVB on DEV klines without S4 (no aggTrades), stop at IB mid floored at W_min, one try per day, NY open DST-aware. Low priority: the model
   was already negative out of sample in the HOLDOUT era; run only as a DEV replication if test 3 or 5 passes.

## 7. Defaults taken (operator may overrule; none is money, mainnet or the live tree)

- DEV for Tom/Fabio work = desk lock 2022-04-01..2024-06-30 for new tests (subset of `splits.py` DEV, so both guards pass).
- HOLDOUT 2025-07+ counts as spent for the VP level-touch family and the Fabio order-flow family; a promotion read for them uses data after
  2026-10-31 (forward testnet calibration rows) or a window no study has read.
- This review files raw cards for the gaps (section 8) and makes no code change: every finding is a research-rule or study-scoring question, and the
  CVD-absorption / escalation detectors also run live (`backtest/layers/alerts/live_runner_cli.py:20,438,482`), so changing them is a live-path change.

## 8. Cards filed (raw, this commit)

- `tom-btc-cards-window-rescope` - tom-btc-* windows are project VALIDATION; re-scope to DEV desk lock.
- `tom-btc-other-setups-void-result` - clear the 504/100 result that its report contradicts.
- `fabio-v3-model-b-unmanaged-scored-zero` - Model B fills recorded as 0 R; report them as NOT MEASURED and fix `_manage`.
- `fabio-detectors-match-quotes` - CVD absorption unbounded higher low; escalation without a break test (live path: tests first).
- `formulas-fabio-v3-and-vp-return` - write FORMULAS sections for v3 S1-S8 / Models A-D and the VP return count.
- `tom-fabio-holdout-exposure-ledger` - record PHASE2, Fabio L1/OF/v3 reads of VALIDATION/HOLDOUT in an exposure ledger.
- `fabio-of-report-superseded` - mark FABIO_OF_REPORT legacy fees / pre-DST / stale driver path.
- `pending-test-fabio-v3-bal-poc-band` - 1 failing never-collected test.
