# MTS formula inventory (2026-09-28, Sonnet Explore agent; supervisor notes marked SUP)

Scope: every numeric formula in MTS. Canonical definitions go to MyTradingSys/backtest/layers/FORMULAS.md
(layers done; core/execution/indicators pending). "Test" = hand-computed numeric test exists.

## Core
| Formula | Where | As implemented | Variant notes | Test |
|---|---|---|---|---|
| Zone distance | runtime/mts_math.py:10-13 | (price-zone)/zone | signed | test_mts_math.py |
| Zone substate | mts_math.py:16-22 | abs(dist)<=0.001 -> at_zone | inclusive | yes |
| Distance cap | mts_math.py:25-40 | per-zone-type table 0.002-0.005, x2 if speed_picking_up | 19 types, default 0.003 | yes |
| Tier | mts_math.py:43-49 | <=0.001 trigger; <=cap conditional | inclusive | yes |
| Gross R:R | mts_math.py:62-67 | abs(target-entry)/abs(entry-stop), 0 if risk 0 | - | yes |
| Net R:R (Python) | mts_math.py:70-71 | gross*(1-friction), friction 0.25 | parameter | yes |
| Net R:R (Java) | src/main/java/datafeed/SetupCandidatesBuilder.java:182 | gross*0.75 hardcoded | SUP: same value as Python today, but two unsynced copies | NO |
| net_rr_sanity | SetupCandidatesBuilder.java:184 | net>=2.0 | mirrored in core_invariants.py NET_MIN | invariant script only |
| Confluence clustering | mts_math.py:78-104 | cluster if abs(p-mid)/mid<=0.003 | mid recomputed per zone | partial |
| Verdict bands | backtest/verdict.py:110-125 | proof<3 WAIT_PROOF, <5 WATCH, else SETUP_FORMING | must match PowerShell | parity.py (541/544) |
| proof_direction | verdict.py:46-62 | status -> aligned/contradiction/error | fail_closed toggle | test_proof_direction.py |
| State (balance/trend) | mts_math.py:333-346 | cascade on vwap/cvd slope, price vs VA | must match Java classifyState | yes |
| Target R bounds | SetupCandidatesBuilder.java:150-151 | 2.0R..3.5R | hardcoded | invariant script only |

## Execution (live orders - highest priority)
| Formula | Where | As implemented | Variant notes | Test |
|---|---|---|---|---|
| Tick snap | execution/plan_compiler.py:38-40 | round(p/0.5)*0.5 | round-half-even (Python round) | NO |
| Size rounding | plan_compiler.py:43-46 | max(10, round(a/10)*10) | floor 10 | NO |
| Ladder rung prices | plan_compiler.py:97-109 | even split, rung1 best | direction-dependent | NO |
| Ladder avg entry | plan_compiler.py:111-126 | sum(p*s)/sum(s) | SUP: inverse contracts need harmonic mean (see executor) | NO |
| Fixed-% stop + worst loss | plan_compiler.py:138-152 | entry*(1-/+pct); loss=-abs(entry-stop)*size/entry | fees/funding excluded | NO |
| Target from pnl% | plan_compiler.py:196-198, executor.py:470-471 | avg_fill*(1+/-pct/100), snapped | duplicated | NO |
| Inverse avg fill | executor.py:411-426 | sum(amt)/sum(amt/price) | inverse (Deribit BTC-PERP) | NO |
| Notional cap | execution/risk_guard.py:24-83 | abs(size)*mark, projected>10000 breach | mark None -> assumes USD units | check test_risk_guard.py |
| Daily loss cap | execution/daily_loss_guard.py:11-51 | sum(realized)+unrealized <= -500 | inclusive | yes |
| Daily P/L (live) | execution/daily_loss_monitor.py:149-154 | (equity_now-day_start)*mark | L6 part 2 changes source | yes |
| Preflight worst loss | executor.py:242,322 | -size*stop_pct/100 | different shape from plan_compiler | NO |
| Sim fees | backtest/sim.py:76-80 | fee_R=(taker+maker|taker)*entry/risk | taker 0.0005, maker 0 | NO |
| bt_engine R accounting | backtest/bt/bt_engine.py:28-108 | net_r=gross-fee-funding | stop_first, gap fills at open | test_bt_engine.py |

## Indicators (Java feeds zones/proofs)
| Formula | Where | As implemented | Variant notes | Test |
|---|---|---|---|---|
| ATR | SetupCandidatesBuilder.java:837-845 | SMA of True Range | SUP: NOT Wilder RMA - operator decision needed | NO |
| Speed/ATR ratio | SetupCandidatesBuilder.java:782-796 | atr14/atr baseline; score=min(10, r*3+consec*2) | magic numbers | NO |
| VWAP (session) | src/main/java/datafeed/MarketDataSnapshot.java:618-656 | sum(tp*v)/sum(v), tp=HLC/3 | session-anchored | NO |
| VWAP bands | MarketDataSnapshot.java:638-653 | vol-weighted population sigma, +/-1,2 | population | NO |
| VWAP slope | MarketDataSnapshot.java:641-648 | half-vs-half avg, +/-0.0005 | fixed thresholds | NO |
| CVD | MarketDataSnapshot.java:658-702 | cvd += 2*buy - vol | slope needs 40 bars, +/-0.02 | NO |
| Volume profile POC/VAH/VAL | MarketDataSnapshot.java:494-593 | triangular weighting, VA 70% | tie -> lower side | NO |
| VP shape | MarketDataSnapshot.java:569-587 | 0.6 / 0.8-1.2 heuristics | heuristic | NO |
| Swings (core) | MarketDataSnapshot.java:704-737 | 3-bar close pivot, per-tf lookback {2,7,3,24,16,12} | fallback raw H/L | NO |
| CryptoCred swings/MSB, R-targets | layers/cryptocred/*.py | see FORMULAS.md s9 | body-based | yes |

## Probability / backtest stats
| Formula | Where | As implemented | Variant notes | Test |
|---|---|---|---|---|
| Wilson CI (sim) | backtest/sim.py:34-39 | standard | SUP: algebraically equal to bt_stats; only n==0 differs: sim (0,0) vs bt_stats (0,1) - (0,1) is correct | NO |
| Wilson CI (bt_stats) | backtest/bt/bt_stats.py:6-13 | standard | - | via test_ref_pbo? |
| Breakeven win rate | sim.py:96 | 100/(1+avg_win_R) | - | NO |
| Outcome labels | runtime/outcome_labeler.py:81-87 | (fwd-p)/p*100 at 30/60/120m, first snapshot >= target | no interpolation | NO |
| Quad classify | runtime/quad_classify.py:38+ | sign octants price x CVD x OI | thresholds past L50 | NO |
| Moments | bt_stats.py:26-38 | population sd; raw kurtosis | population | yes |
| Sharpe | bt_stats.py:40-44 | mean/sd, no annualisation, no rf | - | yes |
| PSR / DSR | bt_stats.py:46-67 | Bailey & Lopez de Prado | 0.5 fallback | check |
| PBO (CSCV) | bt_stats.py:69-99 | S=16, Laplace +1 | - | test_ref_pbo.py |
| Duplicate stats copy | research/fast_track_2026-09-27/backtest_xcheck/bt_stats.py | same math, separate copy | drift risk | separate tests |

## Priority (SUP)
1. Execution math with no tests: plan_compiler.py, executor.py price/size/avg-fill/worst-loss, risk_guard
   mark=None branch. Tests from FORMULAS definitions; must fail on a mutated copy. T4 review (lesson B).
2. Java net R:R 0.75 vs Python 1-friction: one shared constant + a Java unit test.
3. Java indicators (ATR, VWAP+bands, CVD, volume profile, swings): hand-computed JUnit tests; ATR SMA vs
   Wilder is an OPERATOR DECISION (core is Tom's method - do not change silently).
4. Stats duplicates + sim.py Wilson n==0: dedupe or cross-test.
5. Outcome labels + quad classify: tests (they feed the probability layer).
