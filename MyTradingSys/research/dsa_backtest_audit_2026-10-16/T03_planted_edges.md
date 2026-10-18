# T03 Planted edges: do the simulators return answers we know?

Run by a Sonnet worker on the Lenovo (DESKTOP-F7IU69N, no F: drive, no data) on 2026-10-18, started from origin/fast-track 49754e62. Code-only method: seeded synthetic markets, expected numbers from formulas written in the script, never from the code under test.

## 1. Summary
- Seven simulators and the two verdict functions were fed markets with known answers (no edge, a planted +0.30%, a move inside the signal bar, a move after the exit, funding, a gap through the stop, a same-bar stop and target, a timeout). The price accounting is right everywhere: no harness captures a move it could not have known, and every harness returns the planted +0.30% to 8 decimals.
- What is wrong is at the edges: `bt_engine` ignores missing funding without an error and charges the wrong side of a settlement boundary, the screens charge a flat 1 bp that ignores side and rate, and `orderflow_views.trade` books a gap through the stop at the stop price.
- The published numbers survive. The gross screen T arm and mal_bb A1 statistics rebuild from the ledgers to rounding, and every pass-bar threshold sits exactly where the PRE_REG says. No verdict changes. Result: 0 S1, 1 S2, 3 S3 findings (89 harness x canary cells: 62 PASS, 18 FAIL, 9 BLOCKED).

## 2. Scope
| What | Window | Method | Script |
|---|---|---|---|
| bt_engine.simulate_trade, tom_bt.sim_limit_trade, run_t055.score_trades + trade_costs.net_return/funding_paid, screen.compute_cells, chart_read_g5 common.trade_gross/funding_pct, orderflow_views study.trade, levels_sizing probe.run | synthetic 30-day 1m markets, 43,200 bars, 83 events each, seed 20261018 (arrays in %TEMP%/dsa_audit/T03) | 8 canary families, expected from own formulas | scripts/T03/t03_canaries.py |
| screen T arm, notF, C, DIFF; mal_bb A1 | committed DEV ledgers only (gross_effect_screen/ledger.csv 1,439 events, mal_bb/ledger.csv 1,179 events) | pure-Python rebuild of mean, day-clustered SE, t, MDE, DIFF | scripts/T03/t03_stats.py |
| pass-bar boundaries | constructed results | fed to `common.verdict_arm` and `screen.evaluate` | scripts/T03/t03_stats.py |
| opr_bb_mtf_center and mal_bb study.py trade accounting | static read | both call `K.net_cells` and `K.verdict_arm` (opr study.py:297,302), so the chart_read_g5 rows cover them; their signal detection is T02/T04 territory | grep |

No VALIDATION or HOLDOUT value was read; no footprint window was read (no EXPOSURE_LEDGER row needed). Mutation self-test: `t03_canaries.py --mutations` re-runs the table against five deliberately broken copies and shows the canaries go from PASS to FAIL (section 7).

Re-run: `python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T03/t03_canaries.py --mutations` and `.../t03_stats.py` from the worktree root. Full 89-row table: scripts/T03/out/canary_table.md (json beside it).

## 3. Harness x canary table
Expected and got are means in percent; the status compares every event, max abs diff <= 1e-8 pp. "n/a" = BLOCKED (reason in the row).

| Canary (expected from own formula) | bt_engine | tom_bt | run_t055 + trade_costs | screen.py | chart_read_g5 | orderflow trade | levels probe |
|---|---|---|---|---|---|---|---|
| a. zero drift (per-event ratio of exit to entry; walk mean within 3 SE of 0) | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| b. planted +0.30% over the hold (expected +0.300000) | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| b'. net after costs (0.30 - 0.05 - 0.05*pout/pin; Deribit 0 + 0.05; 0.0012 flat) | PASS | PASS | PASS | n/a (gross only) | n/a (gross only) | n/a | n/a |
| c. move inside the signal bar (expected 0) | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| d. move one bar after the exit (expected 0) | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| e1. funding crossed mid-hold, +/-0.01% long/short (expected side x rate) | PASS | n/a (no funding term) | PASS (funding_paid) | **FAIL** flat 1 bp | **FAIL** flat 1 bp | n/a (no funding term) | n/a (no rate input; flat stress) |
| e2. entry exactly at a settlement (expected 0, FORMULAS 13 `t_in < s`) | **FAIL** charged | n/a | PASS | PASS | PASS | n/a | n/a |
| e3. exit exactly at a settlement (expected charged, `s <= t_out`) | **FAIL** not charged | n/a | PASS | **FAIL** (side/rate blind) | **FAIL** (side/rate blind) | n/a | n/a |
| e4. funding=None / records missing for the hold (expected: error, as `trade_costs` B103) | **FAIL** silent 0 (0 of 76 raise) | n/a | PASS (76 of 76 raise) | n/a | n/a | n/a | n/a |
| f. gap 2% through the stop (expected fill at the gap open, -2.00) | PASS | PASS | n/a (no stop) | n/a | n/a | **FAIL** -0.50 (stop price) | PASS |
| f2. tape gaps but MARK stays above the stop (expected no stop) | PASS | n/a | n/a | n/a | n/a | n/a | n/a |
| g. stop and target in one bar (expected stop first, -0.50; ambiguous counter 83) | PASS | PASS | n/a | n/a | n/a | PASS | PASS |
| h. timeout reason, bars held (60), exit bar | PASS | PASS (59 + fill bar) | n/a | n/a | n/a | n/a | PASS (day_end) |
| h2. last bar closes 100, next bar opens 99 (L5; expected = next-open exit -1.00) | **FAIL** exits at the close, 0.00 | **FAIL** exits at the close, 0.00 | n/a | PASS (exits at the next open) | PASS | n/a | n/a |

Notes on reading it: e1/e3 on the screens FAIL only for the wrong-sign half of the events (a short with positive funding receives, a long with negative funding receives), the table checks every event. h2 is a convention difference, not an arithmetic error (finding T03-F4). The zero-drift walk is also compared with zero: mean within 3 SE (PASS).

## 4. Findings
Severity per brief 5.6. Evidence file:line at 49754e62; every row has a canary in t03_canaries.py (CONFIRMED = reproduced there).

| ID | Sev | Status | Evidence | What it affects, measured | Fix | Card |
|---|---|---|---|---|---|---|
| T03-F1 | S2 | CONFIRMED mechanism; SUSPECTED size | bt_engine.py:39 `fund_evt = sorted(funding or [])`, :61-66 no coverage check. Canary e1/e4: 83 of 83 events pay 0 with `funding=None`, expected +/-1.0 bp; 0 of 76 events raise when the records stop before the hold (`trade_costs.funding_paid` raises on all 76, B103). rsi/run_rsi_backtest.py:109 calls `simulate_trade` with no funding argument at all; run_cc_setups.py:144 passes `funding or None`. | Every RSI-runner result and any CryptoCred run without a funding file has funding = 0 with no warning. Per 8h crossed the error is up to 1 bp (+/-0.01% rate at the brief's range -11.9..+8.8 bp per 8h); holds up to 1440 bars cross up to 3 settlements, so the net mean can be off by more than 0.01 pp. Size on the published RSI/CryptoCred rows not measured (needs real bars). | Raise when `funding` is None/short for the hold (same rule as trade_costs B103) unless the caller passes an explicit `funding=[]` "no funding model"; make the RSI runner pass funding. | bt-engine-simulate-trade-fail-closed-on- |
| T03-F2 | S3 | CONFIRMED | bt_engine.py:61 `bisect_right(fund_times, last_t)` with `last_t = entry_t` (the SIGNAL bar open) and :60 `bar_end = t + 59999`. Canary e2/e3: an entry bar opening exactly at 00/08/16:00 is charged (should not be, FORMULAS 13 `t_in < s`); an exit whose instant is exactly the settlement is not charged (should be, `s <= t_out`). `trade_costs` and `screen.py` get both boundaries right. | 2 of 1,440 minutes per day (0.14%) change by 1 bp; negligible on every published number. | Make the funding window (open of the first scanned bar, open of the exit bar+1]; add the two boundary canaries to bt tests. | same card as F1 |
| T03-F3 | S3 | CONFIRMED (repeats N2 of 2026-10-15-strategy-direction-audit) | orderflow_views_2026-10-14/study.py:206 `res = -risk / p0 * 100` books the stop price on a gap. Canary f: 2% gap, the harness returns -0.50, the right fill is -2.00 (1.50 pp optimistic on that trade). | Optimistic bias on every stopped trade that gaps. Published verdict is already NEGATIVE (0/12 arms), so it cannot flip. | Fill at `min(open, stop)` for longs (max for shorts), as bt_engine, tom_bt and the levels probe do. | none (S3) |
| T03-F4 | S3 | CONFIRMED | L1 for the screens: screen.py:32 FUND_PCT, :177 and chart_read common.py:148-151 charge +1 bp to every trade whose [entry, exit] crosses a settlement, whatever the side or the rate. Canary e1/e3: errors of 0 or 2 bp per crossing event. Separately (L5, timeouts): bt_engine.py:93-96 and tom_bt.py:229 fill a timeout at the last bar's close with no slippage; a market exit sent at that close fills at the next open. Canary h2: gap of 1% between the close and the next open gives 0.00 vs -1.00; the screens exit at the next open and agree with the second reading. | At the primary cell (h=60) 15% of events cross a settlement (my rebuild: pre-funding mean -0.05528 vs after -0.05678, diff 0.0015 pp), so the flat-1bp error moves a published mean by about 0.0015 pp, under the S2 bar. Close-vs-open on BTC 1m bars is not measurable without data; BLOCKED-DATA, no desk row (T06 owns costs). | T06 (real funding file). For timeouts: choose one convention and add slippage to the timeout leg. | none (S3) |

Three more observations, no severity (nothing is wrong, recorded so nobody re-checks them):
- `tom_bt.sim_limit_trade`, `orderflow_views.trade` and the levels probe have no funding input (levels charges a flat stress, `probe.py` `qty*op*.0001/480` per bar). All three hold under about two hours, so it is bounded; BLOCKED rows e1 are the reason, not a pass.
- The mean >= 0.14 bar is implied by t_net >= 2 (t_net = (mean - 0.14) / SE); it can never decide a verdict on its own.
- `screen.evaluate` returns PASS_CONTROL when the all-events control arm clears the bar without a DIFF test (screen.py:260). It is the stated rule of that PRE_REG, but it means a study can "pass" with no flow effect; it is not the five-condition bar of brief 1a. `common.verdict_arm` has no such path.

## 5. Independent statistics rebuild (pure Python, from the committed DEV ledgers)
Screen: ledger.csv, cell d=1 h=60, funding = flat 1 bp per settlement crossed (the screen's own rule, recomputed), SE = sqrt(sum over days (sum (g-m))^2)/n.

| quantity | published (RESULT.md) | rebuilt | match |
|---|---|---|---|
| T n / mean / SE / t_cost / MDD | 40 / -0.0568 / 0.1304 / -1.51 / 8.47 | 40 / -0.05678 / 0.13036 / -1.509 / 8.4667 | yes |
| notF n / mean / SE / t_cost | 1399 / -0.0067 / 0.0253 / -5.79 | 1399 / -0.00674 / 0.02533 / -5.792 | yes |
| C n / mean / SE / t_cost / MDD | 1439 / -0.0081 / 0.0246 / -6.03 / 214.21 | 1439 / -0.00813 / 0.02458 / -6.027 / 214.207 | yes |
| DIFF T-notF, SE, t | -0.0500 / 0.1350 / -0.37 | -0.05004 / 0.13495 / -0.371 | yes |
| MDE T = 2.8 SE | 0.3650 | 0.36501 | yes |

mal_bb A1 (ledger.csv, day = entry-bar day, h=60 after funding): n 1179 / mean +0.0124 / SE 0.0212 / net -0.1276 / t_net -6.02 / MDE 0.0593 published; rebuilt 1179 / +0.012401 / 0.021183 / -0.127599 / -6.0236 / 0.059312. All match to the published rounding. 490 day clusters.
**DIFF vs control for A1 is BLOCKED-DATA:** the control set (n 2486) is in no committed file and the Lenovo has no bars. Desk row `20261018-183805-t03-blocked-data-mal-bb-a1-diff-vs-contr` (target DSA). The DIFF estimator itself is validated on the screen (above).
Small-sample check (observation, no verdict moves): with the G/(G-1) cluster correction the T arm t_cost goes -1.509 -> -1.490 (39 clusters) and A1 t_net -6.024 -> -6.017; MDE T 0.3650 -> 0.3698 (+1.3%). The code uses the uncorrected form; no verdict changes (S3 at most).

## 6. Boundary tests (the verdict code is the object under test)
All 16 constructed cases behave as the PRE_REG says; every comparison is `>=` for n, t_net, DIFF, t_diff and `<=` for MDD.

| test | expected | got |
|---|---|---|
| n = 200 / n = 199 (everything else clear) | PASS / INCONCLUSIVE | PASS / INCONCLUSIVE |
| t_net exactly 2.0 (C patched to 0, values [2,0,2,0], dyadic so exact) | PASS | PASS |
| t_net 2.0 - 2e-9 | FAIL | FAIL |
| DIFF 0.05 - 1e-9 / 0.05 / 0.05 + 1e-9 | FAIL / PASS / PASS | FAIL / PASS / PASS |
| DIFF built as 0.5 - 0.45 (decimal 0.05) | PASS | PASS |
| t_diff bisected to 2.0000000000000204 / 1.9999999999999913 | PASS / FAIL | PASS / FAIL |
| MDD equal to the buy-and-hold MDD / 1e-9 above it | PASS / FAIL | PASS / FAIL |
| screen.evaluate nT = 200 / 199 with a clearing control | PASS_FLOW / PASS_CONTROL | PASS_FLOW / PASS_CONTROL |
| screen.evaluate nT = 199, control failing | INCONCLUSIVE | INCONCLUSIVE |

The first run of the t_net 2.0 - e case failed because my construction was scale invariant (t does not change when values are scaled); I corrected the test, not the harness.

## 7. New tests must fail on broken code (mutation check)
Five broken copies of the harness code, loaded in memory by `t03_canaries.py --mutations`; each turns PASS cells into FAIL:
| mutation | newly FAIL |
|---|---|
| M1 bt_engine funding sign dropped | 2 (funding interior, both rates) |
| M2 bt_engine gap fills at the stop | 1 (f gap through stop) |
| M3 bt_engine target before stop on a double hit | 1 (g same-bar) |
| M4 chart_read exit one bar late | 4 (zero drift, planted, inside-bar, after-exit) |
| M5 chart_read enters on the signal-bar open | 2 (zero drift, move inside the signal bar) |

## 8. Leads
| Lead | Result |
|---|---|
| L5 timeout fills at the last close (bt_engine.py:93-96) | CONFIRMED as a convention: fill at the close with no slippage and no latency; equal to the screens on a continuous tape, 1.00 pp apart on the h2 canary. S3 (T03-F4). |
| L5 gap test on the trade bar while the stop hit uses the mark bar (:74, :79) | CLEARED for current use: no caller in the repo passes `mark_bars` (grep: only the optional cc_bt_adapter parameter). With a full mark series the stop correctly does not trigger while the mark stays above it (canary f2 PASS). A partial mark dict silently falls back to the trade bar per bar (`(mark_bars or {}).get(b["t"], b)`), which is a trap but unused. |
| L5 `funding=None` means 0 (:39) | CONFIRMED, S2 (T03-F1). |
| L1 (T06) flat 1 bp funding | evidence added: canary e1/e3, size about 0.0015 pp at h=60 (T03-F4). |
| L7 (T05) drawdown units | not touched; boundary tests only confirm the comparison operator. |

## 9. Not checked
- mal_bb A1 DIFF vs control (needs F:/MTS/data bars): BLOCKED-DATA, desk row posted.
- Real-tape close-vs-open gap size for the timeout convention: BLOCKED-DATA, folded into T06.
- Signal logic of the opr and mal_bb studies (touch_events, engulf): T02/T04.
- run_t055 pipeline with real funding files and the 70/30 split (L2): T08.
- tom_dax_bt.py, sim.py, fabio/run_backtest.py, fires_kline.py, exit_policies: no canary, out of time budget; same canary families apply.

## 10. Decisions taken
- DECISION (OURS): the working tree is `mts-desktop-f7iu69n-dsa03-lenovo`; a second `sync.py start` call created a duplicate tree `-2` (nothing in it), which I removed, so only one tree and branch remain.
- DECISION (OURS): FORMULAS.md covers indicators and the T055 cost model (section 13) but not trade accounting for stops; for stops and gaps the expected values come from first principles (fill at the worse of open and stop; stop first on a double hit, as the engines document).
- DECISION (OURS): the funding boundary convention is `t_in < s <= t_out` (FORMULAS 13), not what bt_engine happens to do.
- DECISION (OURS): the h2 timeout case is graded against the next-open exit; the FAIL is a convention flag (S3), not a bug claim.
- DECISION (OURS): `tasks.py done dsa-audit-03-planted-edges` was refused: the card note carries a T0-ONLY review stamp and the gate wants a real one (ACCEPT or REVIEWED: <reviewer> <date>); hold A-20261018-5 is already lifted (ANNOUNCEMENTS.md, EXPIRED) and the card is exempt from it. I did not write a review stamp myself. The report ships with the card left in state ready, for its reviewer slot to stamp and close.
- DECISION (OURS): only one fix card (F1 + F2, one file, one test file); F3 and F4 are S3 and not carded.

## 11. Bridge log
Not applicable: this card ran in a Claude Code session on the Lenovo, not through the AIBridge. 0 bridge replies.

## 12. Handover
1. Top fix: bt_engine.simulate_trade funding handling (card bt-engine-simulate-trade-fail-closed-on-): fail closed on missing funding, fix the (t_in, t_out] window, make run_rsi_backtest.py pass funding.
2. File: MyTradingSys/backtest/bt/bt_engine.py (:39, :60-66), MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:109.
3. Test that proves it: scripts/T03/t03_canaries.py rows e1-e4 flip from FAIL to PASS (they fail today).
4. Risk: RSI and CryptoCred net numbers will move by the funding they never paid; rerun them on DEV and compare against the published rows before quoting any.
5. Rerun after: t03_canaries.py (expect the bt_engine e-rows PASS), then the RSI and CryptoCred DEV runs; and T06 for the screens' flat funding.
