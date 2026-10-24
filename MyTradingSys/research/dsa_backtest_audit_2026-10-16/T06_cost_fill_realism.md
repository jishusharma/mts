# T06. Costs and fills: what would we really have paid and got?

Card `dsa-audit-06-cost-fill-realism`. Fast-track sha at start: 5879e97d3 (worktree branch). DEV only (before 2024-07-01). No VALIDATION or HOLDOUT read. No footprint read, so no EXPOSURE_LEDGER row.

## 1. Summary
- Checked: every fee, slippage and funding constant in backtest/ and research/ (201 hits, 70+ files), the funding path of five recent screens (rerun with real signed 8h funding), the fill rules of 14 engines, the break-even cost of each screened arm, and the fee-to-stop ratio of every testnet layer.
- Wrong: the funding data was never found (wrong folder), so every screen charged a flat 1 bp to both longs and shorts instead of the real signed rate; 57 of the 70 files that set a cost define their own constant instead of importing fees.py; no screened arm earns even the cheapest realistic fee, so costs, not funding, decide every verdict.
- Changes: no verdict flips with real funding (largest move +0.018 percentage points on a secondary arm); the numbers are not comparable across studies until one cost module is used; the G5 screens need a cost-in-R and fee-regime line before any new run.

## 2. Scope
| What | Window | Method | Result |
|---|---|---|---|
| All fee/slip/spread/funding constants under backtest/ and research/ (tracked .py, tests and dsa_backtest_audit excluded) | n/a | scripts/T06/t06_scan.py regex + t06_tables.py | costs.csv, 201 rows |
| Gross-effect screen, primary cell (d=1, h=60), arms T, notF, C, plus all 30 (d,h) cells | DEV 2022-01-01..2024-06-30 | screen.py's own loader/ledger/evaluate, funding swapped (t06_funding.py) | Section 5 |
| Four chart-read G5 screens (mal_bb_mid_engulf, opr_bb_mtf_center, opr_preopen_tops, opr_weekly_low_round_sweep) | DEV | each study.py `main(--full)` with HERE redirected to scripts/T06/out; flat run reproduces the published numbers, real run swaps `net_cells` and `placebo_gross` | Section 5 |
| Fill rules, 14 engines | n/a | code read (Explore subagent, line numbers re-quoted from its report) | Section 6 |
| Break-even per arm | DEV | gross mean after real funding | Section 7 |
| Fee-to-stop, 30 testnet layer rows | n/a | auto_trader_config.json + auto_trader.py:72, :206-221 | Section 8 |

Reproduction check: the flat-funding run gives n_T 40, mean -0.0568%, t -1.51, control n 1439, -0.0081% (gross) and A1 n 1179 +0.0124%, A2 n 807 +0.0143%, AU n 194 +0.0196%, AD n 282 +0.0322%, H1 n 105 -0.0111%, H2 n 104 +0.0373%, RL n 685 +0.0317%, AS n 525 -0.0389%: all equal the section 1b figures of AUDIT_BRIEF.md.

## 3. Findings
| ID | Sev | Status | Evidence | Affects, measured | Fix (one line) | Card |
|---|---|---|---|---|---|---|
| T06-F1 | S2 | CONFIRMED | screen.py:349,:451 test `F:/MTS/Dumps/backtest/raw_fund` (absent); real data is Dumps/backtest/raw/fundingRate. screen.py:32 `FUND_PCT = 0.01`, :177 charges it to both sides; common.py:18-19,:148-151 copy it. Script t06_funding.py, out/funding_rerun.json | Gross screen: T -0.0568 -> -0.0561, C -0.0081 -> -0.0069. G5 primary arms move +0.0001..+0.0037 pp. Largest secondary move: preopen S1 quick SHORT h=180, +0.0126 -> +0.0307 (+0.0181 pp). Of 83 G5 arms, 46 change more than 10% relative and 8 by more than 0.01 pp (t06_probe.py). Verdicts: none change (5 of 5 studies identical) | Load Dumps/backtest/raw/fundingRate in one shared loader; charge `side * sum(rate)`; delete the flat 1 bp | proposed: `fix-screen-real-funding` (SONNET, prio 2) |
| T06-F2 | S2 | CONFIRMED | costs.csv: 164 binding rows in 70 files; only 13 files import fees.py (15 with the doc-only lines); fees.py:3 says no file defines its own fee. Forms in use: 10, 12, 14, 20 bp RT (0.0010, 0.0012, 0.0014, 0.0020), 7 bp per side, 6 bp per fill, 0.09/0.14 % RT pairs, 5 bp flat both sides | Net means are not comparable: the same gross trade nets -0.10 % to -0.20 % depending on the file (spread 10 bp RT = 3.6x the best gross edge found, +0.0359 %) | One `costs.py` (taker/maker, RT and per side, slip) imported by every study; a test that greps for literals | proposed: `fix-single-cost-module` (SONNET, prio 2) |
| T06-F3 | S2 | SUSPECTED | Section 6: bt_engine.py:57 and run_rsi_backtest.py:109-110 charge no slippage on entry or stop; sim.py:77 no slippage; fabio v3 manage.py:141 fills a fill-bar stop at the stop price not the open (tom_bt.py:212 uses the worse open); run_variant (tom_bt.py:260-261) never passes through_ticks, so G4 touch fills still apply | Not measured (needs a planted-gap canary, T03 owns). Direction: every difference makes results more optimistic | One shared fill module with a gap-at-open rule and a slippage default | proposed: `fix-fill-rules-shared` (SONNET, prio 3) |
| T06-F4 | S3 | CONFIRMED | N2: orderflow_views_2026-10-14/study.py:205-206 `res = -risk/p0*100` on any stop hit, and :197-200 drops entries whose stop is already on the wrong side. Still unfixed at this sha | 0 of 12 arms passed, so no verdict at risk; the gap loss is capped at 1 R | Fill the stop at `min(open, stop)` (long) | none (S3) |
| T06-F5 | S3 | CONFIRMED | Section 8: every non-Tom layer uses the fixed 1.0 % bracket (auto_trader.py:72), fee/stop 0.10 R (0.14 R with 2 bp slippage per side). max_loss_usd is 2 % to 10 % of size, 2x to 10x the 1 % stop, so the cap never binds before the stop. 97 % of exits are time exits (MORNING_REPORT) so the stop ratio understates the fee drag | Testnet last 7 days: 486 trades, -40.81 USD, PF 0.38 | Report fee in R of the realised move, not of the stop | none (S3) |
| T06-F6 | S3 | CONFIRMED | Section 7: best measured gross edge is +3.6 bp (AD), best derived is +9.3 bp (candle_close); all-taker Deribit costs 10 bp RT before any slippage | Even the best arm is negative at zero slippage unless both legs are maker | State the fee regime (A/B/C/D) next to every verdict | none (S3) |
| T06-F7 | S3 | SUSPECTED | Backtests apply Binance 8h funding to a Deribit-traded plan; Deribit funding history is not in the repo | Unknown size; small beside the 14 bp cost (Binance DEV mean +0.73 bp per 8h) | Fetch Deribit funding (public) and compare | none |

## 4. Cost inventory and venue table (lead L3)
costs.csv columns: file, line, name, value, unit (fraction/pct/bp/usd/points/other), side (per_side/round_trip/per_8h/n-a), maker_taker, applies_to, imports_fees, kind (assign = name bound to a number; literal_in_text = a fee literal on a line that talks about fees, usually a docstring), text. Classification of unit, side and maker/taker is by name and line text; `n/a` means the line does not say. 201 rows, 164 assignments, 70 files; 57 of those 70 files do not import fees.py.

fees.py values (cited): Deribit taker 0.0005, maker 0.0 (fees.py:23-24, verified 2026-09-26); Binance taker 0.0005, maker 0.0002 (:27-28); FDAX 0.000005 per side (fees.py FDAX_PER_SIDE).

| Study or engine | Charged | Where | Imports fees.py | Venue the number matches | Venue that would trade it (testnet: Deribit) and what it would pay |
|---|---|---|---|---|---|
| Gross screen + 4 G5 screens | 0.14 % RT = 2 x (5 bp + 2 bp slip); maker-in 0.09 % | screen.py:30-31 | no | Binance/Deribit taker (same 5 bp) | Deribit: maker entry 0 bp, so the 0.09 % arm is conservative by 2 bp; flat funding 1 bp |
| bt_engine / RSI runner | taker 0.0005, maker 0.0 | bt_engine.py:20 | no (default args) | Deribit | same; no slippage at all |
| tom_bt / sim / stop_buffer_wf | FEES_DERIBIT (entry/target 0, stop/timeout 5 bp) | tom_bt.py via fees.py | yes | Deribit | matches |
| bigtrade exit_policies | FEE_RT 0.0010 + SLIP_RT 0.0002 | exit_policies.py:28-29 | no | taker both legs | Deribit target leg could be maker; flat on every exit |
| run_t055 / trade_costs | fee_rt 0.0010, slip_rt 0.0002 | run_t055.py:111,:195,:360-361; trade_costs.py:51 | no | taker both legs | matches Deribit all-taker |
| fabio v3 | taker 0.0005 via costs.py, slip_bps default 0 | v3/costs.py:8,:35 | yes | Deribit | matches; maker legs priced |
| candle_patterns pilot, volume_2026-10-09 | 2 x (0.0005 + 0.0002) = 14 bp RT | run_p1.py:27, run_v1.py:23 | no | Binance taker + 2 bp | matches Deribit taker |
| carry_basis, published_strats | 0.0010 per side per leg (20 bp RT) | carry_basis.py:27, run_pub.py:15 | no | 2x Binance taker | over-charges Deribit by 10 bp RT (retail spot-like) |
| context_factors | 0.0007 per side (14 bp RT); maker-in 0.0002 | study.py:29-30 | no | Binance taker+slip | maker-in on Deribit would be 0 |
| orderflow_views | FEE_RT 0.10 % | study.py:47 | no | taker both legs, no slippage | N2 gap also unmodelled |
| krown_malkan, malkan_universe, event_counts | 0.0010 RT (and 0.0014) | run_counts.py:347, event_counts.py:28 | no | Deribit taker | matches |
| pit_levels, setup_catalog, imbalance_qriptal filter | 0.14 %/0.09 % RT; maker 0.0002 per side | count_prior_va.py:32, build_cost_gate.py:12, filter_join.py:42-43 | no | Binance maker 2 bp | Deribit maker is 0 bp, so these over-charge maker legs by 2 bp per side |
| kurisko, p4_corrected, positioning_c1 | 14 bp, 10 bp, 12 bp RT | count_events.py:32, p4_corrected.py:29, count_power.py:42 | no | taker (+ slip) | matches |
| levels_confluence ladder | 0.004 / 0.002 | ladder.py:36 | via fees dict | per-leg flag | read in context |
| FDAX probe | 0.000005 per side | fees.py FDAX_PER_SIDE | yes | Eurex, not crypto | not comparable to BTC |

Resolved L3: CONFIRMED (section 3, T06-F2).

## 5. Funding rerun (lead L1)
Path miss CONFIRMED: screen.py:349 and :451 look for `F:/MTS/Dumps/backtest/raw_fund`; common.py:19 comments the same. The data sit in Dumps/backtest/raw/fundingRate (81 monthly files; 2,736 settlements from 2022-01-01 to 2024-06-30, all 8 h). In DEV: rate -11.92..+8.81 bp per 8h, mean +0.73 bp, 13.4 % negative, 37 % exactly +1 bp. 1,215 of the 2,736 are stamped 1 to 5 ms after the 00/08/16 boundary.

Method: cost to a trade of side s = s x sum(rate of settlements with entry < t <= exit) x 100 % (long pays a positive rate, short receives it). The flat rule counts boundaries crossed (tx//8h - te//8h) x 1 bp for both sides. Because the real stamps are a few ms after the boundary, a trade exiting exactly on a boundary minute is charged by the flat rule and not by the real rule; this is part of the difference.

Gross screen, primary cell (d=1, h=60), mean % of notional after funding (before the 0.14 % cost):
| arm | n | flat 1 bp | real signed | change (pp) | t vs cost flat -> real |
|---|---|---|---|---|---|
| T (session extreme + delta) | 40 | -0.05678 | -0.05610 | +0.00067 | -1.509 -> -1.505 |
| notF | 1399 | -0.00674 | -0.00548 | +0.00126 | -5.79 -> -5.75 |
| C (control) | 1439 | -0.00813 | -0.00688 | +0.00125 | -6.03 -> -5.99 |
DIFF vs control -0.0500 -> -0.0506 (t -0.371 -> -0.375). Verdict INCONCLUSIVE before and after. Sides: 735 short, 705 long, so funding nets out almost to zero over the whole sample, but the flat rule charges 1 bp x crossings regardless.

Four G5 screens, primary verdict arms (mean gross % after funding; net = mean - 0.14):
| study | arm | n | flat | real | change (pp) | verdict before -> after |
|---|---|---|---|---|---|---|
| mal_bb_mid_engulf | A1 SHORT h=60 | 1179 | +0.0124 | +0.0138 | +0.0014 | FAIL -> FAIL |
| mal_bb_mid_engulf | A2 SHORT h=60 | 807 | +0.0143 | +0.0159 | +0.0016 | FAIL -> FAIL |
| opr_bb_mtf_center | AU LONG h=120 | 194 | +0.0196 | +0.0205 | +0.0009 | INCONCLUSIVE -> INCONCLUSIVE |
| opr_bb_mtf_center | AD SHORT h=120 | 282 | +0.0322 | +0.0359 | +0.0037 | FAIL -> FAIL |
| opr_preopen_tops | H1 SHORT h=60 | 105 | -0.0111 | -0.0101 | +0.0010 | INCONCLUSIVE -> INCONCLUSIVE |
| opr_preopen_tops | H2 LONG h=60 | 104 | +0.0373 | +0.0380 | +0.0007 | INCONCLUSIVE -> INCONCLUSIVE |
| opr_weekly_low_round_sweep | RL LONG h=60 | 685 | +0.0317 | +0.0318 | +0.0001 | FAIL -> FAIL |
| opr_weekly_low_round_sweep | AS SHORT h=60 | 525 | -0.0389 | -0.0365 | +0.0024 | FAIL -> FAIL |
Shorts gain (they receive the mean +0.73 bp positive rate), longs lose slightly. Largest secondary moves: preopen S1 quick SHORT h=180 +0.0126 -> +0.0307 (+0.0181 pp); S3 quick SHORT h=180 -0.0125 -> +0.0019; mal_bb engulf a h=240 -0.0158 -> -0.0088; AD h=240 +0.0243 -> +0.0326. All secondary rows stay far below +0.14 %. Full per-arm rows (83 arms) are in out/funding_rerun.json (flat and real, same harness). No verdict changed, so F1 is a number-quality finding, not a flip.

## 6. Engine x fill-rule table (code read; stop-first means the stop wins a same-bar tie)
| Engine | Entry | Stop + target same bar | Gap through stop | Limit fills | Timeout exit | Partials | Slippage |
|---|---|---|---|---|---|---|---|
| bt/bt_engine.py simulate_trade | caller price, scan from next bar (:63) | stop-first, flag `stop_first` (:20,:91) | at the open (:88-89); gap test uses trade-bar open even with mark_bars (:81, lead L5/T03) | targets touch, `target_through=0.0` (:20,:85) | close of last bar (:102-103) | scale-out only (:38,:94) | none; taker on entry, stop, timeout (:57) |
| tom_bt.py sim_limit_trade / run_variant | limit E, touch (:194) | stop-first, flag (:223); fill bar tests the stop only (:211) | `min/max(open, stop)` (:212,:224) | touch in run_variant: through_ticks never passed (:260-261) | close of last hold bar (:228) | no | stop and timeout only (:203-204), default 0 |
| tom_dax_bt.py | limit E, touch (:285) | stop-first (:321) | `min/max(open, stop)` (:322,:303) | touch; reopening gap filled at the limit, "slightly optimistic" (:1471) | close, or next real open after a closure (:326,:316) | no | stop/timeout; +1 pt stress (:1233) |
| sim.py | snapshot price (:57) | stop first (:68), 60 s samples miss wicks | observed: sampled price; ideal: stop (:69) | none; target on sample touch (:70) | sampled price at 12 h (:65) | no | none, taker/maker fees only (:77) |
| run_t055 + trade_costs | event bar close (:128) | n/a (fixed horizon) | n/a | n/a | close of bar i+h (:128) | no | flat slip_rt 0.0002 (trade_costs.py:65,:68) |
| fabio run_backtest | event bar close (runner.py:53) | n/a | n/a | n/a | close at i+h | no | none, FEE_ROUND_TRIP flat (:42) |
| fabio v3 (manage.py, fill.py, costs.py) | limit at bar-i close, live from i+1 (fill.py:304-312) | stop-first, flag (manage.py:140) | open if beyond, but only after the fill bar; on the fill bar at the stop price (:141-143) | through-by-tick entry and target (fill.py:300, manage.py:136) | close of window end (:198) | no | slip_bps on taker legs only, default 0 (costs.py:270-271) |
| rsi/run_rsi_backtest.py | close of bar i (:107) via bt_engine | stop-first (engine default) | open | touch target | close via max_bars | no | none |
| bigtrade fires_kline / capture | next bar open at the earliest (docs :17/:18) | n/a | n/a | n/a | n/a | n/a | flat fee/slip fields only |
| bigtrade exit_policies | open of the successor bar (:64,:120) | stop-first, hard-coded (:77-82) | `min/max(open, stop)` (:79) | target touch (:81) | `c[last]` (:91) | no | flat 12 bp on every exit incl. maker target (:80-82) |
| gross screen compute_cells | open of bar t+1+d (:155) | n/a | n/a | FILL flag through-by-one-tick, conditions the sample only (:167,:178) | open of bar e+h (:172) | no | none; 0.14 % downstream |
| chart_read common.trade_gross | open of bar t+1+d (:142) | n/a | n/a | n/a | open of bar t+1+d+h (:143) | no | none; 0.14 % downstream |
| orderflow_views study.py (N2) | open of entry bar (:193) | stop-first (:205) | stop price, not open (:206) | n/a | close of 120th minute (:201) | no | none; FEE_RT flat |

N2 status: unfixed at this sha (study.py:205-206). Optimistic flags: orderflow :206, :197-200; fabio v3 manage.py:141; touch fills in tom_bt/tom_dax_bt (G4 still applies to every run_variant run); bt_engine/RSI/sim zero slippage; sim.py 60 s sampling; screen.py gross always at `pin` regardless of FILL. Conservative flags: stop-first everywhere; fill-bar target not tested; through-by-tick in fabio v3; exit_policies charges slippage on a maker target.

## 7. Break-even per arm
Break-even RT cost = mean gross after real funding (cost at which mean net = 0). Charged: 0.14 % = 14 bp RT. Columns of fee regimes: A all-taker Deribit 10 bp RT; B maker entry + taker time exit 5 bp RT (fees.py FEES_DERIBIT); C all-maker Deribit 0 bp; D Binance maker both legs 4 bp. Slippage headroom per fill = (gross - fee) / 2. Full table: breakeven.csv.

| arm | n | gross (bp) | break-even RT cost (bp) | headroom vs 14 bp | slip headroom/fill A | B | C | D |
|---|---|---|---|---|---|---|---|---|
| gross screen T | 40 | -5.61 | none (negative) | -19.6 | none | none | none | none |
| gross screen C | 1439 | -0.69 | none | -14.7 | none | none | none | none |
| A1 mal_bb | 1179 | +1.38 | 1.4 | -12.6 | none | none | +0.7 | none |
| A2 mal_bb | 807 | +1.59 | 1.6 | -12.4 | none | none | +0.8 | none |
| AU mtf | 194 | +2.05 | 2.0 | -12.0 | none | none | +1.0 | none |
| AD mtf (best measured) | 282 | +3.59 | 3.6 | -10.4 | none | none | +1.8 | none |
| H1 preopen | 105 | -1.01 | none | -15.0 | none | none | none | none |
| H2 preopen | 104 | +3.80 | 3.8 | -10.2 | none | none | +1.9 | none |
| RL weekly low | 685 | +3.18 | 3.2 | -10.8 | none | none | +1.6 | none |
| AS weekly low | 525 | -3.65 | none | -17.6 | none | none | none | none |
| candle_close best arm (derived from the brief's -4.68 bp net) | n/a | +9.32 | 9.3 | -4.7 | none | +2.2 | +4.7 | +2.7 |
| mfe_exit turn_of_candle (brief) | n/a | +0.3 | 0.3 | -13.7 | none | none | +0.2 | none |

Reading: the best measured arm (AD) turns negative at 0 bp slippage under every regime except an all-maker Deribit plan (1.8 bp per fill of room, which a maker fill on the opposite side of a moving market will not deliver). Verdict: costs, not funding, decide these screens; fee-regime must be recorded with each verdict.

## 8. Fee-to-stop per stop-based testnet layer (extends Fable E3, which covered Tom/Fabio only)
fee RT = 2 x Deribit taker = 0.0010 of notional (fees.py:23; auto_trader.py:206 RT_TAKER_FEE_FRAC); with slippage 0.0014. ratio = fee / stop distance as a share of price, independent of size. Every non-Tom layer uses the fixed 1.0 % bracket (auto_trader.py:72, NO-SOURCE, SAMPLING), so the ratio is the same for all 23 layer rows: 0.10 R (0.14 R with slippage). Differences between layers are only size and the loss cap (full rows: fee_to_stop.csv).

| layer prefix | size USD | max_loss USD | stop USD at 1 % | fee RT USD | fee/stop | fee / max_loss | cap as % of size |
|---|---|---|---|---|---|---|---|
| layers default, turn_of_candle, rsi_divergence, session_levels, bb_top_reversal, candle_close, levels, wlow_bounce | 20 | 2 | 0.20 | 0.02 | 0.10 | 0.010 | 10 % |
| rsi_events:5m | 50 | 2 | 0.50 | 0.05 | 0.10 | 0.025 | 4 % |
| rsi_events:15m, cvd_absorption:15m | 100 | 3 | 1.00 | 0.10 | 0.10 | 0.033 | 3 % |
| session | 150 | 3 | 1.50 | 0.15 | 0.10 | 0.050 | 2 % |
| sr_flip:15m, failed_msb | 200 | 4 | 2.00 | 0.20 | 0.10 | 0.050 | 2 % |
| rsi_events:1h | 250 | 5 | 2.50 | 0.25 | 0.10 | 0.050 | 2 % |
| cvd_absorption:1h | 300 | 6 | 3.00 | 0.30 | 0.10 | 0.050 | 2 % |
| fib_pullback:15m | 350 | 7 | 3.50 | 0.35 | 0.10 | 0.050 | 2 % |
| escalation | 400 | 8 | 4.00 | 0.40 | 0.10 | 0.050 | 2 % |
| malkan_ | 500 | 10 | 5.00 | 0.50 | 0.10 | 0.050 | 2 % |
| sr_flip:1h | 600 | 12 | 6.00 | 0.60 | 0.10 | 0.050 | 2 % |
| positioning | 750 | 15 | 7.50 | 0.75 | 0.10 | 0.050 | 2 % |
| fib_pullback:1h | 800 | 16 | 8.00 | 0.80 | 0.10 | 0.050 | 2 % |
| volume_fvg | 1000 | 20 | 10.00 | 1.00 | 0.10 | 0.050 | 2 % |

Tom (size 20, max_loss 5, stop from the alert): fee/stop = 0.001 / stop%. At the stated Tom stops 0.044 %, 0.07 %, 0.13 %: 2.27 R, 1.43 R, 0.77 R (3.18, 2.0, 1.08 R with slippage). The gate `max_fee_to_stop` 0.3 (auto_trader.py:273-275) needs a stop of at least 0.333 % of price, so it rejects every Tom stop the trader states; the config is consistent with Fable E3 but Tom can not trade at all through it.

So what: at a 1 % stop the layer fee is small as R, but 97 % of layer exits are time exits (8 bars), so the realised move, not the stop, sets the fee drag: -40.81 USD on 486 trades is -0.084 USD per trade against a fee of 0.02 to 1.00 USD per trade. The loss cap (2x to 10x the stop) never binds first.

## 9. Leads
| Lead | Status | Evidence |
|---|---|---|
| L1 funding NOT_IN_DATA | CONFIRMED | Section 5: path miss at screen.py:349,:451, common.py:19; data present; real signed rerun, no verdict change; flat rule over-charges shorts |
| L3 costs hard-coded in 6+ forms | CONFIRMED | Section 4, costs.csv: 57 of 70 files define their own; at least 8 distinct RT forms |

## 10. Not checked (BLOCKED)
- Deribit funding history and its settlement formula: not in the repo and not fetched here (T06-F7). Backtests use Binance rates.
- Footprint-window studies (levels_sizing, order-flow arms) were not rerun: they need the footprint window (EXPOSURE_LEDGER row) and only their cost literals were inventoried.
- Break-even for rows 7, 8, 10, 11, 12, 13, 15, 16 of section 1b: the brief gives no gross mean per arm (counts, R units or no table). Candle_close and MFE use the brief's quoted numbers (derived, not rerun).
- Fill-rule rows marked UNKNOWN by the code read: bigmoves.py labels, fires_kline `entry_price` origin, where fabio run_backtest applies `FEE_ROUND_TRIP`.
- Cards were not created (builder scope is new files only); the three proposed cards are in the table above.

## 11. Decisions taken
- DECISION (OURS): funding sign convention long pays positive rate, short receives it; settlement counts when entry < s <= exit (same boundary rule as the flat count, with the real stamps a few ms after the boundary).
- DECISION (OURS): reruns redirect each study's HERE to scripts/T06/out so no committed RESULT, ledger or trials file is touched; PRE_REG.md is copied there for the rule hash.
- DECISION (OURS): break-even = mean gross after real funding; fee regimes A to D as in section 7; slippage headroom split equally over entry and exit fill.
- DECISION (OURS): the inventory counts name-bound numeric constants plus fee literals on cost-talking lines in tracked .py files, tests and the audit folder excluded; classification of unit/side is by name and line text.
- DECISION (OURS): fee-to-stop uses the 1.0 % layer bracket from auto_trader.py:72 because the shipped config has no stop_pct key; Tom shown at reference stops 0.044 to 1.0 %.
- DECISION (OURS): S2 for F1 by the brief's rule (more than 10 % relative on published secondary numbers), although no verdict moves.

## 12. Bridge log
Not used. One read-only Explore subagent produced the fill-rule table (no bridge result number); its line numbers were quoted, not re-opened except where listed in the code paths above.

## 13. Handover
1. Top fix: one shared funding loader plus one `costs.py` for every study (F1, F2).
2. Files: screen.py:32,:177,:349,:451; chart_read_g5_2026-10-16/common.py:18-19,:148-173; the 57 files in costs.csv with imports_fees = 0.
3. Test that proves it: scripts/T06/test_cost_inventory.py plus a new test that every cost constant under backtest/ and research/ comes from the shared module (starts failing at about 57 files).
4. Risk: switching to real funding moves published means by up to 0.018 pp; keep the old number beside the new one and do not touch any verdict.
5. Rerun after: `python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/t06_funding.py` (about 5 min), then t06_tables.py.

## Files
scripts/T06: t06_scan.py, t06_inventory (inside t06_tables.py), t06_funding.py, t06_tables.py, t06_probe.py, test_cost_inventory.py; costs.csv, breakeven.csv, fee_to_stop.csv; out/funding_rerun.json (per-arm flat and real rows; the per-study output copies were deleted after the run, rerun t06_funding.py to recreate them).
