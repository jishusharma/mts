# EDGE POSTMORTEM 2026-11-14 (Fable, read-only; 46 study reports read, 0 passed)

**Harness verdict: SOUND but EXPENSIVE. It reads zero on a no-edge world and finds a planted edge, so it is not broken. But at the standard settings (stop floor 0.5%, 12 bp) a trade pays 0.21-0.24 R in fees and the stop keeps only about one third of a real move. An idea needs gross of about +0.30 R per trade (n about 6,000) or +0.45 R (n about 600) to pass. The best gross any intraday study showed was +0.10 R. The intraday ideas could not have passed; the slow ideas (4h and daily) failed for a different reason: too few independent days.**

Scope limits: the planted-edge test used one harness (nkp4 `simulate()` + `stats.py`, read from its worktree, not edited). Every study wrote its own simulator, so the other 40+ were not run, only read. `COMBO_EDGE_SYNTHESIS_1114` and `NK_PHASE_BRAINS_SYNTHESIS_1114` did not exist at 04:13 or 04:40 local; the two raw reports behind them (combo-edge-miner, nkp3) did and are included. `nk-sourced-hm-supertrap-1114` is pre-registered and still running (no result yet). The study tables below were extracted by two Sonnet readers from the RESULTS files; I spot-read NK synthesis, combo miner and the nkp4 code myself, not every row.

## 1. One row per study (best VALIDATION cell)

Units: R = mean net R per trade after fees unless marked % or bp. "Phase" = what was actually used as a gate. CI low = day or week cluster where the file gives it, else per-trade (pt).

### Wave 1-3 (13 Nov, Bybit perps, VAL 2024-07..2025-06)
| Study | Idea | Phase gate | n VAL | Net / trade | CI low | Why it failed |
|---|---|---|---|---|---|---|
| edge-crowding-reversal | Fade funding / account-ratio extremes, 4h-1d | none | 57 | +8.7 bp | -315 bp | n 57; 21 of 24 cells negative; DEV +196 bp flipped to -86 bp |
| edge-extreme-confirm-template | Extreme bar + confirm candle, 1h | HTF bucket | 73 | +1.17% | < 0 | 0 of 54 cells; RECENT +0.01% |
| edge-forced-move-fade | Fade/follow 15m impulse by OI class | none | 2259 | +0.12% | -0.10% | placebo same; OI class does not separate |
| edge-oi-flush | Long after OI liquidation flush, 4h | none | 48 (19 days) | +3.91% | +1.49% | placebo-difference CI spans 0; one episode; RECENT +0.39% |
| edge-rsi-extreme-confirm | 1h RSI extreme + confirm | daily-RSI bucket | 79 | +0.196 R | n/s | 0 of 384; sign unstable DEV/VAL/RECENT |
| edge-session-sweep-reclaim | Europe-low sweep, reclaim in US | session | 173 | +0.105 R (maker) | -0.298 | taker cells -0.23 to -0.32 R; power gate said BLOCK |
| edge-xsec-momentum | Weekly cross-coin momentum | none | 53 wks | +0.39%/wk | -2.13% | noise 2-3%/wk vs mean 0.4% |
| NK_RSI (nk-rsi-hilega) | NK RSI 70/30 + Hilega session rules | HM agree | 123 | +1.16% | -0.15% | fails BH; RECENT -0.17%; R2 gross about 0 |
| edge2-capitulation-long | Long after capitulation bar, new coins | none | 340 | +0.65% | -0.61% | DEV -0.10%; only works after mid-2024 |
| edge2-ratio-fade-wide | Account-ratio fade, 20 new perps | none | 670 | +0.1 bp | -146 bp | wave-1 lead did not replicate |
| edge3-rsi-deep-extreme-grid | Deep RSI extreme grid, 1h-12h | none | 32 | +0.585 R | -0.482 | 48 of 60 cells n < 30; DEV -0.294 |

### Wave 4-6 (edge4-edge6, VAL 2024-01 on)
| Study | Idea | Phase gate | n VAL | Net / trade | CI low | Why it failed |
|---|---|---|---|---|---|---|
| edge4-malkan-divergence | RSI divergence, 1h/4h | none | 1364 | +0.030 R | -0.125 | 22 of 24 cells below 0; 1h cost 0.14 R |
| edge4-ny-session-value | Return to prior NY value area | balanced day | 101 | +0.037 R | -0.155 | reaches far edge 40%, not the claimed 70-80% |
| edge4-rsi-confirm-exits | Exits for 4h RSI<=20 long | none | 144 (38 days) | +0.264 R | -0.30 | DEV -0.125; 38 signal days |
| edge4-rsi-confirm-layers | One layer at a time on RSI long | daily ADX 20-25 | 30 | +0.648 R | +0.17 (wk) | DEV -0.183; BH missed (p 0.006 vs 0.0054) |
| edge4-rsi-htf-extreme | 12h RSI<=20, next bar up | daily-RSI band | 47 (15 days) | +0.56 R | -0.24 | 15 days; DEV -0.16 |
| edge5-ny-value-poc-target | NY value, POC target, new coins | balanced day | 370 | -0.006 R | -0.074 pt | gross +0.077 eaten by fee |
| edge5-rsi-4h-exits-newcoins | Replicate 4h RSI long, 40 coins | none | 452 | +0.081 R | -0.163 pt | best 5 days = 239% of profit |
| edge5-rsi-htf-power | 4h RSI<=12 and daily<30, 60 coins | daily RSI<30 | 36 (18 days) | +1.218 R | -0.18 | one date = 14 of 36 trades; ex-best-5 -0.334 |
| edge5-rsi-oi-unwind-newcoins | Replicate OI-unwind / ADX layers | ADX 20-25 | 41 | +0.214 R | -0.135 pt | ex-best-5 -0.060 |
| edge6-capitulation-breadth | Market-wide RSI washout long | breadth event | 28 events | +1.2% | -0.7% | 28 events; DEV -1.7% |

### Wave 7-9 and bear-phase studies
| Study | Idea | Phase gate | n VAL | Net / trade | CI low | Why it failed |
|---|---|---|---|---|---|---|
| edge7-daily-trend-follow | Daily trend, 60 coins | BTC > 200d (rules 8-10) | 680 | Sharpe 0.85 | -0.253%/day | best 10 days = 226% of profit |
| edge8-long-gated-trend-newcoins | Same, 60 new perps | BTC > 200d | 267 | Sharpe 0.70 | -0.041%/day | below buy-and-hold basket (0.74) |
| edge8-mined-rules-nk-mal-cbp | NK-R04/05/11, MAL-R05 | none | 49922 (R11) | -0.236 R | n/s | stops 0.13-0.17% make fee about 0.8 R |
| edge9-bear-trap-reclaim-long | Sweep + reclaim of prior low | downtrend + OI flush | 583 | -0.036 R | -0.192 | gross about 0, all 24 rows negative |
| edge9-downtrend-seller-layers | Short at stacked seller levels | BTC DOWN days | 1924 | -0.295 R | -0.453 | gross about 0, fee about 0.4 R |
| edge9-phase-matched-trades | Right trade type in right phase | coin-day UP/DOWN/RANGE | 2465 | -0.047 R | -0.141 | matched no better than mismatched |
| edge9-weekly-streak-bounce | Long after N red weeks | none | 391 | +2.6% | -0.2% | placebo p 0.053; 0 of 48 |
| edge9-winrate-vs-expectancy | Scalp target/stop grid, 5m | none | 7968 | -0.142% | -0.182% | all 96 cells negative; win rate is shape only |
| btc-bear-phase-reactions | Where buyers step in after 5 red weeks | descriptive | 7 / 44 episodes | n/a | n/a | no level beat base rate |
| big-trades-at-bottoms | Big prints at 6 BTC lows | descriptive | 6 lows | n/a | n/a | flow follows price (corr next 24h +0.05) |
| cycle-conditioned-buy-odds | Buy odds by cycle position | cycle features | about 4 bottoms | +26.4% / 90d | n/s | 9 overlapping episodes; analog rule skill 0.00 |
| htf-divergence-outside-bb-ride | HTF divergence outside band | none | 37 | +1.03 R | -0.44 | DEV -0.35; about 320 cells |
| retest-double-bottom-anatomy | Confirmation after long falls | descriptive | 21 | +2.5% | n/s | every trigger inside placebo band |
| top-87k-case-study | Divergence shorts at the 87k top | 200d phase table | 11 | +5.8% / 30d | -1.9% | n 11; shorts lose in bull phase |

### NK studies
| Study | Idea | Phase gate | n VAL | Net / trade | CI low | Why it failed |
|---|---|---|---|---|---|---|
| nk1-first-hour-low-break-vwap | Opening-range break near VWAP, 5m | prior-close UP/DOWN/RANGE | 9852 | -0.136 R | -0.125 (6 bp row) | fee 0.20 R; placebo equal |
| nk2-pivot-sr-reclaim | Reclaim of daily pivot, 1h short at P | same | 6102 | -0.009 R | -0.098 | gross +0.101, fee 0.110 |
| nk3-breakout-fakeout-retest | Fakeout fade, 1h | same | 2448 | -0.034 R | -0.110 | fee 0.13 R; +0.030 at 6 bp |
| nk4-hilega-milega-recon | HM state flip, 15m | same | 12897 | -0.192 R | -0.098 | gross about 0; holds 10-90 min |
| nk5-session-open-15-10-5 | Session-open RSI + HM, hold to 08:00 | same | 1663 | +0.074 R | -0.151 | ex-best-5 -0.108; 30.7% win tail |
| nk5-nyasia-fresh-coins | Same on 14 unseen coins | same | 2524 | -0.101 R | -0.254 | did not replicate; pre-2024 -0.253 |
| nk6-confluence-combos | 33 layer-agreement combos | same | 1996 | -0.112 R | -0.193 | gross +0.084, fee 0.20 |
| nkp1-session-rules-phase | NK1/NK5 in 6 phases x 8 contexts | BTC 6-phase | 232 | -0.174 R | -0.819 | DEV +0.892 shrank to -0.174 |
| nkp3-hilega-milega-phase | HM + band breakout in 6 phases | BTC 6-phase | 384 | +0.324 R | -0.322 | ex-best-5 -0.334; placebo p 0.14 |
| nkp4-nk-plus-mts-confluence | NK + MTS context count | BTC 6-phase | 306 (6 days) | +0.347 R | -0.202 | 0 of 1088 DEV cells; CAPITULATION = 6 VAL days |
| combo-edge-miner | 210,684 layer combos, 4h/1d | cycle clock x structure | 80 | +1.625 R | +0.185 | ex-best-5 -0.008; BH q 0.062 |

## 2. Harness sanity check (measured tonight, 6 coins, 15m, 2024-01..2026-11)

Code under test: nkp4 `simulate()` (stop = max(1.0 ATR14 of 15m, 0.5%), target 2R, 24-bar time exit, entry next open, stop wins ties) and `stats.cluster` / `ex_best`. Detection rule: net > 0 and day-cluster CI low > 0 and ex-best-5 > 0.

**A. No-edge world** (each real bar's direction flipped at random, volatility kept): gross +0.007 R, net -0.203 R at 12 bp, detected 0 of 6. No false positive.

**B. Planted edge** (a fixed upward drift added over the 24 bars after each random signal):
| Drift planted over 6 h | Gross R seen | Net at 12 bp | Detected, n 6285 (12 / 6 bp) | Detected, n 630 over 105 days (12 / 6 bp) |
|---|---|---|---|---|
| 0 bp | +0.007 | -0.203 | 0/6, 0/6 | 0/6, 0/6 |
| 15 bp | +0.101 | -0.110 | 0/6, 0/6 | 0/6, 0/6 |
| 30 bp | +0.200 | -0.010 | 0/6, 6/6 | 0/6, 2/6 |
| 50 bp | +0.334 | +0.123 | 6/6, 6/6 | 4/6, 6/6 |
| 80 bp | +0.521 | +0.311 | 6/6, 6/6 | 6/6, 6/6 |

**C. Is the rule set itself killing ideas?** Yes, for intraday ideas, in three measurable ways:
| Check | Measured | Meaning |
|---|---|---|
| Stop floor | 0.5% floor binds on 36% (LINK) to 88% (BTC) of 15m bars at 1.0 ATR; on 80-98% at 0.6 ATR | "max(0.6 ATR, 0.5%)" is in practice a flat 0.5% stop on 15m and below |
| Fee in R | 12 bp = 0.21-0.24 R per trade; 6 bp = 0.105-0.12 R | break-even needs win rate 43% against 36% for random entries |
| Stop inside noise | median 6 h absolute move is 0.52% (BTC) to 1.06% (LINK), the stop is 0.50-0.57% | 60% of random real entries stop out, 27-29% hit target, 12% time out |
| Capture | a 30 bp planted move shows up as 0.20 R; full capture would be about 0.6 R | the stop keeps one third of a real move and pays the whole fee |
| Random entries, real data | long gross -0.011 R, short +0.024 R, net -0.222 / -0.186 R | real market reads zero, so "beats placebo" only means "is not worse than a coin flip" |
| Clustering | day-cluster CI half-width 0.043 R vs naive 0.033 R (6 coins) | 1.3x wider already; with 20 coins on the same bar it is wider still |
| Phase label | prior-close lag is real (STUDY_BUG and PHASE_LAG=0 tests exist and fail as designed). VAL days: DISTRIBUTION 31.7%, MARKUP 30.6%, MARKDOWN 19.0%, ACCUM-RANGE 14.9%, RELIEF 3.2%, CAPITULATION 0.6% (6 days) | the catch-all label is the biggest VAL phase; CAPITULATION and RELIEF cannot be powered on VAL |

Not checked: the other study simulators (run), maker fill realism, funding. The no-edge world flips coins independently, so it understates same-day correlation across coins.

**Break-even line to carry forward (OURS, from this run):** at 12 bp an intraday idea must produce more than about 30 bp of true directional move per trade just to reach zero. No intraday study tonight showed more than about 15 bp equivalent (+0.10 R gross).

## 3. Common failure modes

| # | Failure mode | Studies | Evidence |
|---|---|---|---|
| 1 | Gross about zero, fee decides | nk1, nk4, nk6, edge9 x4, edge8 NK rules, edge5-ny, NK_RSI R2 | gross -0.02 to +0.10 R against fee 0.11-0.40 R (0.8 R on 0.15% stops) |
| 2 | Too few independent days | edge4-layers (30), edge4-htf (15 days), edge5-htf-power (18 days), oi-flush (19 days), edge6 (28 events), nkp4 CAPITULATION (6 days) | the same three crash dates (2024-07-05, 2024-08-05, 2025-04-07) carry most winners in every washout study |
| 3 | DEV and VAL disagree in sign | edge4-layers, edge4-htf, edge3, edge-crowding, nkp1, htf-divergence, nk5 fresh coins | washout longs: DEV negative, VAL positive in 6 of 6. Likely reason: DEV holds the 2022 bear (washouts kept falling), VAL washouts were dips inside a bull. This is a phase effect nobody gated on |
| 4 | Phase was reported, not used | all of wave 1-6 | BTC vs 200d was printed as a mix line; only edge9 on used a prior-close gate |
| 5 | Phase gate too coarse where used | edge9-phase-matched, nk1-nk6 | matched direction no better than mismatched; one ADX/MA20 label |
| 6 | Tail dependence | combo miner, edge7, edge8, nk5, edge5-4h | ex-best-5 flips sign; for trend exits this is by design, not a defect of the idea |
| 7 | Search far larger than data | combo miner (210,684 trials), htf-divergence (about 320), nkp (144 cells per rule) | the best-of-noise t is 6.7; best real t was 5.3 |
| 8 | Power gate overruled | edge-session-sweep, nk-sourced-hm-supertrap | `prereg_gate.py` said BLOCK before the run (needs 0.76 R, plausible 0.30 R) |
| 9 | Each study built its own simulator | all | fees 10, 12, 13, 22 and 24 bp; two VAL windows; spot priced as perps; survivor coin lists; placebo with a stop on the wrong side (malkan, fixed) |

### The 3 that came closest, and why each is still alive
| Rank | Lead | Numbers | Why still alive | What killed it |
|---|---|---|---|---|
| 1 | Trend continuation long in early-cycle uptrend (combo miner, 1d, exit on structure break) | VAL +1.625 R, CI [0.185, 3.461], n 80, fee 0.007 R; 86% of 649 DEV-positive cells stay positive on VAL, median excess over same-phase random +0.47 R | only lead whose sign replicates out of sample and where fees do not matter | ex-best-5 -0.008 (tail), BH q 0.062; phase is not active today (BTC is MARKDOWN) |
| 2 | Washout long (one event tested 7 times: oi-flush, edge4-htf, edge5-htf-power, edge4-layers, edge6, nkp4 X3, combo T10) | +3.91% (CI low +1.49%); +0.56 R; +1.22 R; +0.65 R; combo T10 4h +0.882 R CI [0.10, 1.84], n 375 | never failed on sign in VAL, only on count of days; moves are 2-4% so fees are irrelevant | 15-19 independent days; DEV sign negative (see failure mode 3) |
| 3 | NK pivot rejection short, 1h (nk2 SHORT-P) | gross +0.101 R, n 6102, placebo p 0.001 and BH keeps it; +0.046 R at 6 bp | the only large-sample intraday rule with a real, significant gross | fee 0.110 R at 12 bp gives -0.009; ex-best-5 -0.041 |

Dropped as closest: nk5 NY-asia (+0.074 R) because it failed on 14 fresh coins (-0.101 R).

## 4. Three next tests (PRE_REG drafts)

Shared rules for all three (S = SOURCED, O = OURS):
- Phase: shared table `F:\MTS\data_cache\mts_brains\phase_daily.csv`, label for day d from closes through d-1 (S: MTS_BRAINS_SPEC s1; thresholds O). Cycle state BULL / BASE / BEAR from the same table (S: BIBLE s1, s5; thresholds O).
- Split DEV <= 2023-12-31, VAL >= 2024-01-01 by signal bar. Fee 12 bp primary, 6 bp row with a fill model. Stop >= max(0.6 ATR, 0.5%). Day-cluster CI, ex-best-5, same-phase placebo reported as EXCESS (real minus random), BH over the stated family (task standard).
- New, from section 2 (O): design rule fee/R <= 0.10 at 12 bp, so stop distance >= 1.2%; run `prereg_gate.py` first and do not run on BLOCK; one shared simulator (nkp4 `simulate` + `stats.py`) with the planted-edge test from section 2 added as a unit test; code committed with PRE_REG.
- One frozen cell per test, no grid. Fresh coins (not in the 20 used tonight) are the primary sample so earlier peeks do not count.

### T1. MARKDOWN rally-rejection short at the daily pivot (active today: BTC label MARKDOWN / BEAR since 2026-11-13)
Hypothesis: on MARKDOWN days a 1h push above the daily pivot that closes back below it, while NK's Hilega Milega is in sell state on 30m and price is under VWAP, falls to the next pivot.
| Parameter | Value | Label |
|---|---|---|
| Phase gate | BTC day label = MARKDOWN | S spec, O thresholds |
| Level | classic daily pivot P and R1 from the prior UTC day | S (NK pivot class 3EpXq8JC4jU); UTC day O |
| Trigger | 1h high above level, 1h close below it | S (nk2 SHORT rule as registered) |
| HM state | RSI 9, EMA 3 and WMA 21 on the RSI; sell = WMA21 above both lines; read on 30m | S (Qdug_K_TNHg 00:23:25-00:39:49; 30m frame 00:26:28) |
| VWAP filter | signal close below VWAP anchored 00:00 UTC | S (never trade against VWAP, 00:38:38 mirrored); anchor O |
| Entry | next 1h open, taker. 6 bp row: limit at signal close, counts only if next bar trades through by 1 tick | O |
| Stop | above the 1h signal high, floor max(1.0 ATR14 1h, 1.2%) | S (beyond the level); floor O |
| Exit | next pivot below (S1 from P, P from R1), else 24 h | S target = next pivot; time cap O |
| Sample | 20 fresh spot coins + perp funding, all MARKDOWN days 2020-2026 (343 DEV + 199 VAL days) | O |
| Pass | VAL and DEV both: net > 0 at 12 bp, day-cluster CI low > 0 on the pooled set, ex-best-5 > 0, excess over same-phase random shorts > 0 | task |
Why high odds: nk2 already shows gross +0.10 R at n 6102; a 1.2% floor cuts fee to about 0.10 R; the gate removes the 81% of days where shorts fight the phase. Risk: needs gross of roughly +0.25 R after gating; if gross stays at +0.10 R it fails, and that closes NK pivots.

### T2. Washout Supertrap long, split by cycle state (explains the DEV/VAL sign flips)
Hypothesis: NK's Supertrap on 1h (a candle at least half outside the lower band, then price back above VWAP) is a buy in BULL and BASE cycle states and is not in BEAR. Prediction registered in advance: BULL/BASE mean > 0, BEAR mean <= 0.
| Parameter | Value | Label |
|---|---|---|
| Cycle split | BULL+BASE vs BEAR, from prior close | S (BIBLE s5 200-week clock; cycle-conditioned PRE_REG); thresholds O |
| Washout gate | BTC 4h RSI14 <= 40 at signal | S (Malkan 40/60, layers/rsi/malkan_40_60.py) |
| Trap candle | 1h candle with >= 50% of its range below the lower Bollinger band | S (AKZ-7zvDxpY 00:25:49; 1h named at 00:27:58) |
| Band | 20, 2 | O (never spoken) |
| Entry | first 1h close back above VWAP anchored at the trap candle, within 12 bars; next open | S (00:27:07); window O |
| Stop | trap candle low, floor max(1.0 ATR14 1h, 1.2%) | S (stop hunt low / VWAP); floor O |
| Exit | 24 h time exit, or stop | O (NK gives no number; 12-24 h came from oi-flush, which is seen data) |
| Unit | episode = all signals within 72 h, all coins; statistics on episodes | O |
| Sample | 40 fresh spot coins + BTC/ETH, 2018-2026 so 2018 and 2022 bears are in | O |
| Pass | BULL/BASE: >= 30 episodes, episode-cluster CI low > 0, ex-best-5 episodes > 0, excess over random same-state longs > 0, at 12 bp. BEAR row reported as the control | task + O |
Why high odds: seven studies agree on sign in VAL and the moves are large against fees; the cycle split is the one thing none of them tested. Honest limit: BTC is in BEAR today, so a pass says "wait", not "buy now"; if BEAR is also positive, that is the tradable result.

### T3. Early-uptrend continuation long, one frozen cell, fresh coins (not active today; ready for the next UP_E)
Hypothesis: in cycle label UP_E (BTC above a rising 200d average, under 540 days after the halving) a daily ADX/DI + volume expansion onset beats being long at a random UP_E day.
| Parameter | Value | Label |
|---|---|---|
| Phase | UP_E from the cycle clock x structure, prior closes | S (BIBLE s1 halving dates); 540 days and slope window O |
| Cell A | 1d long, ADX_DI + VOLX, exit on structure break (combo miner rank 1 by DEV, definitions unchanged) | O |
| Cell B | daily Hilega Milega buy state (WMA21 below both lines) + close above weekly-anchored VWAP | S (NK positional = daily; VWAP leg); weekly anchor O |
| Stop | max(2.5 ATR14 1d, 2%) | O (combo miner) |
| Cost | 12 bp + real funding, perp prices | task |
| Sample | 40 coins outside the miner's 20, including delisted ones where data exists | O |
| Primary metric | EXCESS over 1000 random same-phase long entries with the same exit, week-cluster CI | O |
| Pass | excess CI low > 0 on VAL, net > 0, BH over 2 cells. ex-best-5 reported on a capped 3R exit row, where it is meaningful | task + O |
Why high odds: the only family whose sign held on VAL (86% of cells). Why it may still be nothing: edge8 on new coins scored below a plain basket, so the question is strictly "does the signal add to the phase", which is what the excess metric answers.

## Noticed
- `nk-sourced-hm-supertrap-1114` will very likely return NO PASS for power reasons its own PRE_REG states; read it as untested, not failed.
- The 6-phase table leaves 31.7% of VAL days in the catch-all DISTRIBUTION label; split it before more phase studies.
- A shared simulator plus the planted-edge unit test would have caught failure modes 1 and 8 before 46 runs.
- The first sanity run was started at normal priority by mistake (ctypes call did not take) and ran about 14 min before being lowered and then replaced by a smaller BelowNormal run.
