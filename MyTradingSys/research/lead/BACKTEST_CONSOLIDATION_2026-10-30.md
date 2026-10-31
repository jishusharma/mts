# Backtesting: where we are, what is shaky, what to do first (2026-10-30)

Read-only consolidation for Supervisor C, base origin/fast-track in worktree mts-super-fix. Paths are under `MyTradingSys/` unless shown.
Labels: SOURCED = quoted with file:line; OURS = my count or reading this turn (command in section 6). No backtest was run, no sealed window read.

## Short answer
- **No tested configuration has a fee-net out-of-sample edge.** `execution/promoted_setups.json:3` is `"entries": []`. VERDICTS.csv (72 rows, OURS count): 37 FAIL, 14 INCONCLUSIVE, 13 UNPARSED, 6 BLOCKED, 2 PASS. Both PASS rows are unlevered funding carry (`research/VERDICTS.csv:26-27`), a yield that needs a spot leg, not a BTC trading edge.
- Intraday (1m to 2h) is dead on cost: best measured gross 3.8 bp against a 14 bp round trip (`research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md:3`). Every longer or rarer family is "cannot be powered on our data", not "proven no edge".
- We are in roadmap stage **S0 Freeze and clean**, 0 of 5 exits verified met (section 3).

## 1. What ran (harness, window, fee, headline)
Harnesses: `backtest/bt/bt_engine.py` + `bt_data.py` + `bt_stats.py` (generic engine); `backtest/tom_bt.py`, `tom_dax_bt.py` (Tom BTC and DAX); `backtest/layers/runner.py` (L1 layer runner, `layers/BACKTEST_L1_REPORT.md`); `research/sim_desk/desk.py` + `studies/` (simulator desk, one study per file); one script per study under `research/*`.
Fee model: one source `backtest/fees.py:8-13,32-37` (Deribit taker 5 bp/side, maker 0; Binance taker 5 bp, maker 2 bp); regimes A-D at `fees.py:19-23` (A all-taker Deribit 10 bp RT ... C all-maker 0 bp). Fable R1 uses 14 bp RT = 5+5 fee + 2+2 slippage (`R1_EDGE_OR_STOP.md:27`). Guard: `backtest/test_no_own_costs.py`.
Windows (SOURCED `research/sim_desk/ROADMAP.md` section 2.1, `OPERATOR_DECISIONS.md:899`): DEV 2022-01..2024-06 (desk locks 2022-04-01..), DEV_EXT 2020-01..2021-12, VALIDATION 2024-07..2025-06, HOLDOUT 2025-07+ sealed. Order-flow history starts 2024-12, after DEV (`R1:11`).

| Family / study | Window read | Headline fee-net result | Source |
|---|---|---|---|
| Tom BTC (TOM-CORE-0929) | DEV + holdout (holdout burned, B147) | net -0.30 R; holdout -0.32 R, n=254 | `layer_review_2026-10-26/PER_LAYER_REVIEW.md:38-41,57` (via R1:11) |
| Tom BTC (TOM-CORE-1007) | DEV, holdout 2026-06-26.. | net -2.91 R; holdout -2.80 R, n=181 | `fable_audit_2026-10-20/GRANDFATHER_DECISION.md` layer row 1 |
| Tom DAX v2 / order-flow core | not testable on DEV; gross screen T arm n=40 INCONCLUSIVE | none | `gross_effect_screen_2026-10-15/RESULT.md:1,8` |
| Fabio v3 | OOS | FAIL, n=79, mean -0.1038 R | `PER_LAYER_REVIEW.md:65-66` (via R1:12) |
| Levels ladder (LC1-LC3) | DEV | 243 cells all negative; best -0.119 R per filled trade | `layer_lab/TRIALS.md:18-260,272` (via R1:15) |
| WaveTrend 1h | DEV | n=369, -0.158 R, CI [-0.288,-0.023] | `TRIALS.md:273` |
| RSI / Malkan 40/60 | DEV | 31 of 32 cells net negative; daily rule 2 fills, -1.036 R | `PER_LAYER_REVIEW.md:113-114`, `TRIALS.md:274` |
| Krown S5 (4h) | DEV | n=35, +0.278 R, CI -0.161..+0.750 (underpowered) | `TRIALS.md:280` |
| Krown S8 4h, BTC+ETH+SOL pooled (run 6) | DEV 2020-01..2024-06, once | **INCONCLUSIVE**: n=420 (need 439), +0.1312 R, t +1.73 (need 3.364); long-only stratum +0.2967 R, t 2.86 cannot rescue it | `fable_run6_powered_prereg/RESULT.md:3,17,23,25` |
| Gross effect screens (G5, mal_bb, opr_*, candle_close, mfe_exit) | DEV | best gross 3.8 bp vs 14 bp cost | `dsa_backtest_audit_2026-10-16/scripts/T06/breakeven.csv:2-14` |
| 62 published BTC rules; ETH replication | DEV | 0 of 62 survive; 0 of 9 | `backtest_gap_review_2026-10-13/REPORT.md:43` |
| Qriptal volume-anomaly candle filter | DEV, VAL, HOLD tagged | FAIL (all arms) | `research/VERDICTS.csv:4-23` |
| Funding-fade (T055-C1) | OOS n=76 | net -0.0453 % | `PER_LAYER_REVIEW.md:167-170` (via R1:19) |
| US-open study replication (today) | 2020-2021 | direction 0.485 [0.442,0.529]: no persistence; descriptive, no costs | `us_open_oos_2026-10-30/REPORT.md:9-15` |
| Funding carry, unlevered | DEV / VAL / HOLD 2021-01..2025-06 | net 15.35 / 12.06 / 6.26 %/yr: PASS (decaying); 2025-07+ unread | `carry_basis_2026-10-18/RESULT.md:3,12,27-29` |
| BB state x candle x regime map | "DEV 2022-2025", descriptive, fee-free | 186,860 bar-observations, 96 cells, 13 grey | `bb_state_map_2026-10/MAP.md:20-22` |

## 2. Gaps and defects, ranked by what they could hide or fake
Tag: HIDE = could bury a real edge; FAKE = could create or inflate a fake one.
1. **HIDE: underpowered tests.** Rare-event families cannot reach the needed n on 912 DEV days (R1 section 3: a rule firing 40 times per 912 days needs 6,263 to 17,585 days; `R1:46`). Power-gate study short by about 1,200 days (`system/ANNOUNCEMENTS.md:36-38`, B187 OPEN `research/BUGS.md:302`). 33 of 72 verdict rows are INCONCLUSIVE/BLOCKED/UNPARSED (OURS). A MDE helper is done (card `trust-recheck-gap-g1-power-mde-helper`), but older FAILs were read without it (`backtest_gap_review.../REPORT.md:86-110`).
2. **FAKE: trial count and sealed-window discipline.** 281 ledger rows and at least 3,018 outcome cells (`R1:34-38`); rule: DEV-mined numbers need t >= 4.0 (`R1:42`). `research/TRIAL_LEDGER.csv` has 116 rows against 7,251 in `TRIAL_LEDGER_BUILT.csv` (OURS). Holdout read log is empty (`research/holdout_reads.csv:1` header only) while Tom's holdout was read twice (B147, `BACKTEST_ERRORS.md` Tom row). Windows are not one definition: Tom/LC use DEV 2024-12..2025-03, VAL 2025-04..06 (`levels_confluence_2026-10-14/PLAN.md:68`); desk DEV starts 2022-04-01; project VAL is 2024-07..2025-06.
3. **FAKE: the BB state map reads sealed months.** `bb_state_study.py:37` keeps 2022-01-01..2025-12-31, which covers VALIDATION and the sealed HOLDOUT 2025-07..12, while `MAP.md:4` says "holdout (2026+) is never loaded". It is descriptive and fee-free, but the setup the operator picks from it is then chosen after seeing sealed-era behaviour. Fix: cut the map at 2024-06-30 or label it as contaminated.
4. **FAKE: optimistic fills and costs (matters at the first PASS).** Touch-only limit fills in Tom harnesses (G4, `REPORT.md:133-138`); DAX bid-only bars, measured spread 1.15-2.65 pt = 0.06-0.13 R (`REPORT.md:236-246`, G2); stop slippage default 0 (`tom_bt.py:176`, G7); costs that do not scale with volatility, no margin model (T10 summary); screens charge a flat 1 bp funding instead of side x real rate (T06, card `fix-screen-real-funding` ready). No verdict flips today, but a first PASS would be an upper bound.
5. **BLIND: backtest cannot be confirmed on testnet.** T09: live layers use one 1%/2%/8-bar bracket no backtest used; volume_fvg trades the inverted side (0 of 24); RSI live fires on untested events; about 94% time exits predicted, 97% observed (`dsa_backtest_audit_2026-10-16/T09_live_parity.md:1-12`, T085). Testnet fills are synthetic (G3, `REPORT.md:124-131`). So testnet P&L today says nothing about any backtest.
6. **Data defects.** (a) `raw_1d` file is not the resample of 1m (905 open, 847 volume day mismatches); funding path missing so flat 1 bp used (T01 summary, T06). (b) **Double-count found today:** `F:/MTS/data/tom_raw/klines` holds monthly `BTCUSDT-1m-2025-09.csv` plus daily `2025-09-01..07` (7 overlapping days; 26 dailies for 2026-09 have no monthly twin). The BB map loader now drops duplicates (`bb_state_study.py:36`, `MAP.md:24`); `bt_data.load_klines` drops and counts them (`bt_data.py:19-21,66-67`). It cannot touch DEV (ends 2024-06-30) but any read of 2025-09 by another script must dedupe; about 41 of 53 py files that name `tom_raw` show no dedupe keyword (OURS grep, unreviewed). (c) Order-flow and OI history absent before 2024-12 / not fetched (G5, card `metrics-oi-toptrader-into-shared-data` parked). (d) Item 4 replay mixed spot (+19..52 above perp) and perp bars (`critical_test_wave1_2026-10-30/ITEM4_REPLAY_2026-10-29.md`).
7. **Look-ahead: low residual.** T02: 0 of 27 testnet layers show look-ahead, 5 untested on synthetic bars, 132 forward-index hits in the repo lint never reviewed (`T02_lookahead_time.md:1-8`). T03: every harness returns the planted +0.30 % to 8 decimals; edge bugs (bt_engine funding side, gap-through-stop booked at the stop). T04: twins reproduce both studies. T07: 8 of 10 reruns reproduce, mfe_exit does not (`T07_stale_verdicts.md:1-8`). T05: LC1 control unfair (about half its lines are real levels).
8. **Source fidelity (extraction).** Tom captions are AI-translated; frame reads have no measured error rate; check set is 2 trades (`REPORT.md:169-181`). Tom/Fabio "SOURCED" rules may not be what the trader meant; wiring audit `research/wiring_audit_2026-10/WIRING_TOM_FABIO_HABIB.md`.
9. **Bookkeeping.** 13 UNPARSED rows in VERDICTS.csv; LESSONS_DIGEST stale (`research/STATUS.md:8`); Gate Board "next" lines for Tom/Fabio/Malkan/Krown still say G3 marks, dropped 10-28 (`R1:21`, `STATUS.md:39-42`).

## 3. Roadmap position
- **Stage: S0 Freeze and clean** (`research/v1_plan_2026-10-20/D7_ROADMAP.md:14`); EXPECT was 2026-10-27, three days late. In force: `system/ANNOUNCEMENTS.md:16-20` (A-20261030-1: machinery stays, no growth, research breadth not cut, 28 ready cards kept, direction = setup review + storybook v2 first, then S3). Operator words and the "code freeze, layers still missing things" quote: `system/OPERATOR_DECISIONS.md:1489-1491` (d-simplify-align-s0).
- Standing operator rule 10-25: no layer dropped before he sees it in the simulator (card `layer-review-after-simulator`, blocked on 13+13 fact sheets). Stop = pause, never delete (R1 section 5).

| S0 exit (`D7_ROADMAP.md:14`) | Now | Met? |
|---|---|---|
| ready cards <= 15 | 32 cards in state `ready` (OURS count of tasks/*.json); decision says 28 kept | NO |
| claims <= 4 and 0 stale | `system/claims/` empty on trunk; real claims live in lane trees, not read | UNVERIFIED |
| worktrees <= 8 | 50 listed here (`git worktree list`); 45 kept per decision, 21 hold unshipped work | NO |
| bookkeeping share < 30 % | STATUS.md:44 flags 24h commits "OVER 30% CAP" (research 38 %, other 62 %) | NO |
| traffic.py jam exit 0; no scheduled task outside keepers | not checked | UNVERIFIED |
- Next after S0 per D7: S1 spec signed (setup review + storybook v2), then S3 two-layer funnel (`D7_ROADMAP.md:17`). **S3 as written names LC3 ladder and CryptoCred 4h/1d; evidence has moved:** Levels is DEAD (243 cells negative), CryptoCred 4h/1d counts are blocked (`GRANDFATHER_DECISION.md` row 2), the one powered family tried (Krown S8) came back INCONCLUSIVE. S3 needs re-pointing to the operator's setup picks and to the R7 forward test.
- Agreed order of work (`eagle_eyes_picture_2026-10-28/SESSION_MAP_2026-10-30.md` section 1): storybook v2 -> setup review with operator -> BB map (done, MAP.md) -> pre-reg and DEV test of his BB-mid rejection rule (card `bb-mid-reject-candle-rule-test`, raw).

## 4. Testnet today
- Routing: `execution/auto_trader_config.json` has 27 `pre_pipeline_sources`, every one "grandfathered ... operator decision pending", `review_by 2026-10-23` (expired, not enforced: `PROMOTION_PIPELINE.md:39` via GRANDFATHER_DECISION headline). `trade_blocklist` is empty. Fable run 5 memo (2026-10-30) recommends KEEP 1 canary (`tom`, 20 USD), DROP 8 prefixes, collection-only for 18 (`GRANDFATHER_DECISION.md` headline 1). I found no card applying it (card `fable-run5-grandfather-decision` is blocked; `pre-pipeline-sources-review-by-2026-10-2` dropped).
- Halted: `LAYERS.md:189` "HALT since 2026-10-12 09:46Z"; the primary checkout showed untracked `execution/HALT` and `execution/AUTO_PAUSE` at session start. Live owner is desktop-f7iu69n; `live_mirror.py brief` here gives no live numbers. Whether anything fired in the last day: UNKNOWN from this host.
- Registered in the live alert runner (`backtest/layers/alerts/live_runner_cli.py:480-520`): fabio escalation / volume_fvg / v3_grid, session_momentum, funding_cvd_fade, malkan bull/bear, cryptocred sr_flip / fib_pullback / failed_msb (1h, 15m), turn_of_candle, wlow_bounce (long on), rsi_divergence, bb_top_reversal, session_levels, candle_close, levels confluence (rsi events and cvd_absorption set earlier in the same function, not re-read).
- **Not registered (no hits in `layers/alerts/`): pizzino, pitchfork (Java flag only, inert), wavetrend, trendlines, krown, kurisko.** So the newest layers are not on testnet. No live code reads CBP/news (card `live-not-fired-audit-1029` note).
- Audit card `live-not-fired-audit-1029` is state `raw`; its output folder `research/live_not_fired_2026-10-29/` does not exist.
- Planned forward test: card `fable-run7-forward-test` (ready, OPUS, operator runs by hand) would trade the frozen R6 Krown S8 4h rule on testnet as fresh OOS data; needs a registered Krown layer first.

## 5. Do-first list (max 7)
| # | What | Why it unblocks the edge search | Size | Card | Lane / machine (ROUTING.md) |
|---|---|---|---|---|---|
| 1 | Operator picks 2-3 setups from the catalog (16 Tom, 7 Fabio) | One idea to test instead of 23; S1 exit | S (his time) + M page | `setup-review-with-operator` (ready) | SONNET; data host JIS-NB; operator YOU DO |
| 2 | One splits module + holdout read log + guard; re-cut or label the BB map at 2024-06-30 | Stops fake edges from sealed-window contamination; one window definition for all studies | M | none found; file it (holdout log empty) | SONNET, any machine with the repo |
| 3 | Pre-register then DEV-test the operator's BB-mid rejection rule with power stated, MDE first | First backtest under the new order; uses the finished map | M | `bb-mid-reject-candle-rule-test` (raw, promote after #1) | SONNET; JIS-NB (tom_raw present) |
| 4 | Fix the fill and cost bundle: real funding loader, through-ticks fills, stop slippage, DAX ask spread | A first PASS would be trustworthy instead of an upper bound | M x3 | `fix-screen-real-funding`, `gap-g7-stop-slippage` (ready); through-ticks/DAX ask: none found | SONNET; NUC or NB for data |
| 5 | Apply the grandfather decision: one canary, rest collection-only, with exits that match a backtest | Testnet then measures plumbing honestly and stops burning slots on dead layers | S | none found (run-5 card blocked); CRITICAL config change, operator OK | JIS-NB desk task; live-tree change goes to operator |
| 6 | Run `live-not-fired-audit-1029` and register the missing newest layers (pizzino, pitchfork, wavetrend, trendlines, krown, kurisko) as shadow emitters | Answers "latest layers on testnet" and gives forward data for Krown R7 | M | `live-not-fired-audit-1029` (raw), `fable-run7-forward-test` (ready) | live owner desktop-f7iu69n; builder in a worktree, no deploy |
| 7 | Re-point S3 in D7 to evidence (Levels dead, 4h+ powered families, forward test) and finish the 28-card S0 exits (worktree retire, ready cards <= 15) | S0 must close before S3 starts; stage text is stale | S | none (decision edit; D7 edit allowed only to shorten) | coordinator, JIS-NB |

## 6. Method and limits
Read: STATUS.md, ANNOUNCEMENTS.md, D7_ROADMAP.md, LESSONS_DIGEST.md, OPERATOR_DECISIONS.md (tail and d-simplify-align-s0), R1_EDGE_OR_STOP.md, GRANDFATHER_DECISION.md, backtest_gap_review REPORT.md, DSA audit T01-T10 summaries (first lines only), fable_run6 RESULT.md, carry_basis RESULT.md, VERDICTS.csv (parsed with csv, counts), bb_state_map files, tasks/*.json (parsed), live_runner_cli.py lines 432-535.
Not done: no re-derivation of any number above (they are quoted); T01-T10 bodies not read past summaries; PER_LAYER_REVIEW rows cited via R1; no live or runtime data read; 41-of-53 dedupe count is a keyword grep, not a review.
