Result: PROMOTE when the betting e-value E+ (H0: mean fee-net R <= 0, bounded fixed-R trades, one observation per UTC-day cluster) reaches 80 after n >= 30, KILL when E- (H1: mean >= 0.25 R) reaches 10 after n >= 10, RETIRE undecided at 150 trades or 12 months; testnet order: krown-s8-4h (running; add the E+/E- readout, A/B/C untouched), malkan-level-short-div-3-10-4h (card exists; swap its 30-trade kill for this rule, pool ETH paper), T06-rsi-ma-cross-4h (context-only paper run, expected to retire)

# eh-f1-testnet-design: how to tell a real edge from noise on testnet, and what goes first

Design only. No market data loaded, no HOLDOUT bar read, no code outside this folder, nothing wired live. Inputs read: PLAN.md, TRIALS.md, the seven shipped RESULT.md (eh-h1..h5, eh-s2, eh-s3; eh-s1, eh-o1, eh-o2 had not shipped at run time), census_5m_15m_session_ladder_2026-11-09/RESULT.md (landed), fable_run7_forward_test/FORWARD_PREREG.md s3, POSTMORTEM_OPUS.md s3, REVIEW_FABLE.md d, fable_run6_powered_prereg/RESULT.md, malkan_level_shorts_2026-11-09/REPORT.md, reclaim_close_stop_2026-11/RESULT.md. Simulation: `sim_sequential.py` (numpy only, seed 20261109, 4000 synthetic paths per cell; `sim_output.md` is its unedited output; `test_sim_sequential.py` 12 tests pass). Labels: SOURCED = file:line or a RESULT line quoted; OURS = chosen here once, never tuned on an outcome.

## Plain words

The wave produced no PASS. Five of the seven shipped trials FAIL at adequate power, T06 is INCONCLUSIVE with a tiny positive mean (+0.048 R, n = 1322), T02/T03 are too rare to test (1.2 events a year). The census that ran in parallel (5m/15m, in session, HTF ladder, node targets, FEES_DERIBIT) is negative in all ten headline cells. So the testnet question is not "which winner do we confirm" but "what rule would have told us, in the forward record, that a +0.1 R pattern is noise and a +0.4 R pattern is real, without a false claim and without killing the real one on a bad fortnight".

The answer is a pair of anytime-valid e-processes on fee-net R per trade (Q1). They can be read every week without spending alpha, they need no distribution assumption beyond bounded R (which fixed-R exits give, Q4), they handle several concurrent runs by a fixed per-slot alpha (Q2), and they pool symbols by a same-day cluster mean that the simulation shows keeps the error bound where naive pooling breaks it (Q3). The honest part is the horizon: at the shapes the wave measured (30-40 % hit at 2.5 R) and at BTC 4h event rates (1-16 trades a month), the rule promotes a +0.4 R edge in about 90 trades (60 % of the time) and kills the census-null loser (-0.087 R) in about 60 trades (69 %); anything between 0 and +0.25 R is undecidable inside a year and retires. "Within weeks" exists only for clear losers on fast setups, and every fast setup in the wave is dead. What actually shortens the clock is event rate: pooled symbols and several slots, not a sharper statistic. The two kill rules now in use are the wrong shape: Krown R7 FAIL-A/B/C kills a true +0.25 R edge 41 % of the time and a +0.40 R edge 17 % of the time, and the Malkan card's "30 trades, net <= 0" kills a +0.25 R edge 19 % of the time and can never promote anything.

## Context
- Regime: no gate in this design; each candidate carries the regime mix of its own count. Candidates' 4h DEV span (quoted from eh-h5 RESULT.md Regime mix): 358 weeks = bull 72, bear 0, range 223, n/a 63. research_kit's band has 0 bear weeks on this history (PLAN.md s1 pattern 3), so the forward phase tag comes from the Bible clocks, not from this label.
- Phase: the forward run is 100 % current phase by construction (post-bottom recovery, FORWARD_PREREG.md Context); each weekly readout records the phase tag next to the fills, so a kill or a promote is dated to a phase (d-phase-first-method-1106).
- Session: none for 4h candidates; each readout logs the UTC 4h block of entry (REVIEW_FABLE d: session is the largest unexplained split).
- Entry: as each candidate's count: Krown S8 market at the first poll after the 4h close (FORWARD_PREREG s1), Malkan stop order under the prior bar's open within 3 bars (REPORT.md Context), T06 stop order through the prior bar's open (eh-h5 RESULT Context).
Regime mix: 358 DEV weeks: bull 72 (20%) | bear 0 (0%) | range 223 (62%) | n/a 63 (18%) (quoted from eh-h5-rsi-ma-cross-trigger/RESULT.md; no bars loaded by this worker)

## Q1 Promote / kill: one sequential rule on fee-net R per trade

**Observation.** x_i = fee-net R of the i-th closed trade (realised PnL in USD after the venue's actual fees and funding, over risk USD = |fill - stop| x size, FORWARD_PREREG s3 SOURCED); when symbols are pooled, x_i is the mean over the trades of one UTC-day cluster (Q3). Fixed-R exits (Q4) bound it: a <= x_i <= b with b = target - cost (2.45 R for a 2.5 R target, 1.95 R for 2 R) and a = -3 R (OURS: a stop gapped more than 2 R beyond the invalidation is an execution failure; that trade enters E- at its true value, enters E+ at -3, and pauses the run for a parity review, never silently).

**Two e-processes (OURS, standard betting-martingale construction).** With a uniform mixture over lambda fractions f in {1/16, 1/8, 1/4, 1/2, 3/4}:
- E+_n = mean_f prod_{i<=n} (1 + f x lam+ x (x_i - mu0)), mu0 = 0 R, lam+ = 1/(mu0 - a) = 1/3. Under H0 "mean <= 0" each factor has expectation <= 1, so E+ is a test supermartingale and Ville's inequality gives P(E+ ever >= 1/alpha) <= alpha for ANY stopping rule. The weekly look is free.
- E-_n = mean_f prod_{i<=n} (1 - f x lam- x (x_i - delta)), delta = 0.25 R, lam- = 1/(b - delta). Under H1 "mean >= delta" it is a supermartingale, so P(E- ever >= 1/beta) <= beta.
- Worked values (test_sim_sequential.py): one +1 R trade sets E+ = mean(1 + f/3) = 1.141; one -1 R trade sets E+ = 0.859; one -1.05 R trade with b = 2.45 sets E- = 1.252.

**Decision (all OURS).**
| Event | Condition | Why these numbers |
|---|---|---|
| PROMOTE | first n >= 30 with E+_n >= 80 | 80 = 1/(0.05/4): family alpha 0.05 over K = 4 slots (Q2). n_min 30 = Krown FAIL-C and the DEV screen floor; it stops a 3-winner streak from promoting (the bound would still hold, the operator's read would not) |
| KILL | first n >= 10 with E-_n >= 10 | beta = 0.10 per run; a kill costs a missed edge, not a false claim, so no family correction. n_min 10 so that no run dies on three trades |
| RETIRE | n = 150 closed trades or 12 months after the first fill, whichever first, with neither above | the slot is freed; the family keeps its record ("undecided in [0, 0.25) R in phase X"); it is neither promoted nor on the dead list; it may re-enter a slot only with a new pre-registration (a different phase or a pooled symbol set) |
| REVIEW | any x_i < -3 R, any PARITY-FAIL (FORWARD_PREREG s3) | run paused, trades stay in E- at true value |

delta = 0.25 R is the smallest edge worth a slot: the R1 gate's "plausible" effect was 0.30 R (FORWARD_PREREG s2, prereg_gate constants), the wave's large-n trials had MDE 0.11-0.12 R on 4-7 years of DEV (eh-h5, eh-s3), so anything under 0.25 R cannot be settled forward inside a year at BTC rates (table below) and is treated as noise for slot purposes, not as proven absence.

**Simulated error rates** (sim_output.md, shape A = 2.5 R target with a 20 % time-stop leg and 0.05 R cost, hit rate solved from the true mean; 4000 paths; n_max 150):

| true mean R | hit % | P(promote) | P(kill) | P(retire) | median n to decision | P(decided by 60) |
|---|---|---|---|---|---|---|
| -0.300 | 20 | 0.000 | 0.991 | 0.009 | 33 | 0.77 |
| -0.200 | 23 | 0.000 | 0.923 | 0.077 | 47 | 0.57 |
| -0.087 (census null) | 27 | 0.000 | 0.687 | 0.313 | 62 | 0.34 |
| 0.000 | 30 | 0.003 | 0.447 | 0.550 | 65 | 0.21 |
| +0.100 | 34 | 0.024 | 0.205 | 0.770 | 58 | 0.12 |
| +0.250 (delta) | 39 | 0.190 | 0.050 | 0.760 | 89 | 0.07 |
| +0.400 | 45 | 0.599 | 0.015 | 0.386 | 88 | 0.14 |
| +0.600 | 52 | 0.958 | 0.001 | 0.041 | 65 | 0.42 |

Shape B (1 R target, 45-50 % hit; the census shape): a -0.2 R pattern is killed 100 % of the time, median 20 trades; the -0.087 R null in 34 trades (99 %); +0.4 R promotes 99 % (median 72). Shape B decides faster because its outcomes are less dispersed, which is exactly why a 1 R bracket at 48 % is a proven loser everywhere it was counted (Q6). False-promote at mean 0 is 0.3 % against the 1.25 % budget; false-kill at delta is 5.0 % against 10 %. A single-slot threshold of 20 would lift promote power at +0.4 R from 60 % to 77 % (table 3 of sim_output.md); the design keeps 80 because four runs will be live at once. Allowing 300 trades lifts +0.25 R to 46 % promote and the null to 95 % kill (table 4), information only: no slot runs that long.

**What the horizon means in months** (rates from the counts: Krown BTC 142 trades / 54 months = 2.6 a month, pooled BTC+ETH+SOL 332 entry days / 54 = 6.1 clusters a month, fable_run6 RESULT.md cell detail; Malkan div 3-10 126 / 111 months = 1.1 a month, REPORT.md; T06 1322 / 82 months = 16 a month, about 12 day-clusters, eh-h5 RESULT counts):

| run | n = 30 | kill the -0.087 null (median 62) | promote +0.4 R (median 88) | retire at 150 |
|---|---|---|---|---|
| Krown S8 BTC alone | 12 months | 24 months | 34 months | 58 months |
| Krown S8 pooled 3 symbols (cluster) | 5 months | 10 months | 14 months | 25 months |
| Malkan div 3-10 BTC alone | 27 months | 56 months | 80 months | 136 months |
| Malkan + ETH paper (about 2x, uncounted) | 14 months | 28 months | 40 months | 68 months |
| T06 BTC+ETH (cluster, 12 a month) | 2.5 months | 5 months | 7 months | 12.5 months |

So: no BTC-only 4h slot decides inside a year; every run hits the 12-month retire first unless the pattern is a clear loser (shape B at -0.2 R: 20 trades) or a clear winner (+0.6 R: 65 trades). The brief's "weeks" is reachable only for 15m-rate setups (T04 fired 1150 times in 4.5 years, 21 a month), and all of those are dead at adequate power. The design states that rather than hiding it.

**Comparators (sim_output.md table 5, shape A).** Krown R7 FAIL-A/B/C: P(kill) = 0.95 at the census null (good), 0.87 at 0 R, 0.69 at +0.10 R, **0.41 at +0.25 R, 0.17 at +0.40 R**, 0.04 at +0.60 R; the 12 R drawdown and 12-loser streak are routine at a 35-45 % hit rate with a 2 R target. The Malkan card rule (kill at n = 30 if net <= 0): 0.64 at the null, 0.51 at 0 R, **0.19 at +0.25 R, 0.09 at +0.40 R**, and it never promotes. The e-process kills the null less often by n = 150 (0.69) but almost never kills a real edge (0.05 at delta, 0.015 at +0.4 R), which is the error that matters when 0 of 48 ideas have survived: a false kill is a lost edge forever, a slow kill costs a slot-month.

## Q2 Several testnet runs at once without a new multiple-testing problem

- **Slots.** K = 4 concurrent slots (OURS), fixed whether or not all are in use: Krown S8 (live), Malkan level short (carded), T06 (this design), one spare for eh-s1/o1/o2 if any passes. Each run's promote threshold is 1/alpha_slot = K/0.05 = 80, so the family-wise false-promote rate over all four runs is <= 0.05 for the whole year, by the union bound on four Ville inequalities. Opening a fifth slot needs one closed (kill or retire); the alpha is not re-split mid-run.
- **Refinement (e-BH, OURS to adopt; literature: Wang and Ramdas 2022).** Because E+ values are e-values, the family may rank the active runs by E+ and promote the top k runs when the k-th largest E+ >= K/(k x 0.05): one run needs 80, two runs together need 40 each, three 26.7, four 20. This controls the false-discovery rate at 5 % and is never stricter than the per-slot 80. It is optional; the per-slot threshold alone is already valid.
- **Kills** spend no family alpha (beta = 0.10 per run, independent). A kill does not free alpha for the others (conservative; the alpha of a closed slot is not recycled).
- **Looks.** Weekly readouts, after every closed trade if wanted: the e-process is valid at every n. This replaces the R7 "no alpha is spent because no PASS is claimed" with "no alpha is spent AND a PASS can be claimed".
- **One pre-registration per slot before the first fill**: exit (Q4), risk, symbol set and cluster rule (Q3), the three thresholds above, the phase tag at start. Nothing about the rule changes after the first fill; a change = a new slot.
- **The three hand-picked families on testnet as calibration (the 27 grandfathered sources, Tom)** stay outside the slots and outside the alpha, as FORWARD_PREREG s4 already rules.

## Q3 Pooling ETH (and other USD-M symbols) with BTC

- **Yes, pool, with a cluster rule written before the first fill.** Cluster = all pooled-symbol trades whose entry falls in the same UTC day (4h and 1d setups) or the same UTC 4h block (1h and faster setups); the observation is the mean fee-net R of the cluster (OURS; the wave clusters its SE by UTC day for the same reason, PLAN.md s5). A cluster mean of bounded R is bounded by the same a, b, so both e-processes stay exact; the count n is in clusters.
- **Why not naive pooling.** Simulated same-day BTC/ETH pairs with a latent outcome correlation of 0.7 (sim_output.md table 6): treating each leg as its own observation gives P(promote) = 0.014 at mean 0 (budget 0.0125, broken) and P(kill) = 0.12 at delta (budget 0.10, broken); the cluster mean gives 0.003 and 0.046 (inside both budgets) and still beats BTC alone on power (0.66 vs 0.49 promote at +0.4 R; 0.73 vs 0.61 kill at the null). Pooling is worth about one extra symbol's rate minus the overlap, not two.
- **Which symbols.** Only symbols the setup was counted on (Krown: BTC, ETH, SOL, fable_run6 PRE_REG; T06: BTC, ETH; Malkan: BTC only, so ETH enters as a logged paper stream under the same cluster rule and is declared in the pre-registration as pooled from the first fill, OURS; it is a forward test either way).
- **Execution gap.** The Deribit testnet executor is BTC-PERPETUAL only (FORWARD_PREREG s5, `execution/new_plan.py:33`). Until ETH-PERPETUAL exists, ETH trades are paper fills: entry at the signal price plus the setup's own slippage model, exits by the fixed-R rule, costs from fees.py by the setup's regime (A or B as counted), flagged PAPER in the readout. A pooled run with paper legs is promotable (the record is still out-of-sample), but the promote line names the paper share.
- **Funding and fee legs** per trade per symbol as realised (venue) or as modelled (paper), never a flat cost.

## Q4 Payoff: the exit each survivor carries, fixed before the run

| Survivor | Exit on testnet (= the exit it was counted with) | Evidence the shape is right |
|---|---|---|
| Krown S8 4h | target 2 R limit, stop the far side of the 10 signal bars, time stop at the 100th bar close (e2_run.py:61-89 via FORWARD_PREREG s1, SOURCED) | counted: 138 targets / 238 stops / 44 time of 420 (fable_run6 RESULT) |
| Malkan level short div 3-10 | target 2 R, stop the highest high since the level tag + 5 bps, 60-bar time stop (REPORT.md, SOURCED) | hit 1 R 49 %, win 2 R 37 %, +0.10 R (REPORT.md arm table) |
| T06 RSI/MA cross | target 2.5 R, stop the 6-bar swing, 30-bar time stop (eh-h5 PRE_REG, frozen) | exits 251 target / 687 stop / 384 time (eh-h5 RESULT) |

No break-even move, no partials, no trailing, no "next level" target (OURS, with the evidence):
- The census tested exactly those managements against the 1 R bracket on 5m and 15m under FEES_DERIBIT: NODE_BE -0.384 / HALF_BE -0.390 / TRAIL -0.370 vs B1R -0.372 (5m, n = 698), -0.231 / -0.236 / -0.208 vs -0.249 (15m, n = 601): all within one SE; "no right tail shows up for BE/trail to protect" (census RESULT, exits bullet).
- Next-level targets: T09/T10 hit the next HTF level 2 of 41 and 2 of 47 times (5 %, median 11 R away; eh-s2 RESULT funnel); the break-even leg there turned 10 and 12 trades into -0.14 / -0.20 R instead of stops, which did not change the sign.
- 3 R and 10 R tails: T01 reached 3 R 10 of 108 times and 10 R MFE 0 of 108 (eh-h1 RESULT); the 1h fade at fixed 2 R / 3 R: -0.035 / -0.023 R (REVIEW_FABLE a). The traders' "30-40 % at 3 R+" payoff has not appeared in any count on BTC; the forward run should not assume it.
- A fixed-R target bounds the observation at b exactly, which the e-process needs; a trailing exit would need a cap (winsorising from above is conservative for E+ but anti-conservative for E-), so the test would be looser on the kill side.
- Stop = the plan's invalidation, no floor, no fixed percent (d-stops-follow-trade-1106); the fee_r that results is part of x_i, not a gate.
- Risk per trade: 1 R = 1 % of the slot's testnet subaccount equity at the run start, fixed in USD for the whole run, no compounding (OURS; keeps sum of R comparable week to week; FORWARD_PREREG left the size open as "fixed risk per trade").

## Q5 Ranked testnet order (0 PASS in the wave, so the list is the live run, the carded run, then the strongest INCONCLUSIVE with a positive DEV mean and n >= 30)

| # | Setup | Why here | Risk | Symbols / cluster | Expected outcome under the sim | One-line kill rule |
|---|---|---|---|---|---|---|
| 1 | **Krown S8 squeeze break 4h** (live on Deribit testnet, FORWARD_PREREG.md) | the only powered-ish count: pooled +0.131 R, n = 420, t 1.73; BTC alone +0.066, n = 142 (fable_run6 RESULT); already running under the operator's "Yes, start it" | 1 % of the krown_s8 subaccount per trade | BTC live; ETH, SOL paper legs by UTC-day cluster once the readout exists (FORWARD_PREREG s5 follow-up) | at +0.13 R: retire at 12 months most likely (P(kill) about 0.2, P(promote) about 0.03 at n = 60-70 pooled); at +0.4 R (if the recovery phase is kinder than DEV): promote by about 14 months pooled | kill at the first n >= 10 clusters with E- >= 10 (H1 mean >= 0.25 R); A/B/C stay operative until the operator swaps them (they are in the live tree, this worker does not touch it) |
| 2 | **Malkan level short, div 3-10 close arm, BTC 4h** (card malkan-level-short-testnet-forward-1109, READY, context-only) | the operator's own stack, sourced window; +0.10 R, n = 126, 6 of 10 years positive, bull +0.11 / bear +0.13 (REPORT.md) - a 0.9 SE point estimate after 10 arms, so a forward look is the only clean test left | paper, 1 unit risk | BTC + ETH paper (uncounted on ETH, declared pooled before the first fill), UTC-day cluster | 1.1 trades a month on BTC: n = 30 takes 27 months alone, 14 months pooled; a +0.10 R truth retires at 12 months with n about 25; a clear loser is killed from n = 10 (about 9 months) | kill at the first n >= 10 with E- >= 10; replace the card's "30 trades net R <= 0" (19 % false-kill at +0.25 R, never promotes) |
| 3 | **T06 RSI14 back under its SMA14 under 60 / mirror over 40, 4h, BTC+ETH, both sides as frozen** (eh-h5) | the strongest INCONCLUSIVE with n >= 30: +0.048 R, n = 1322, CI -0.029..+0.126, long side +0.105 (post-hoc, logged not traded); it is the operator's stack layer 3 (L4) and the one fast 4h event (16 a month) | paper, 1 unit risk, context-only alert + journaled paper R (no order path) | BTC + ETH, UTC-day cluster, both sides pooled; side logged | if DEV holds (+0.05 R): retire at 12 months (P 0.77), kill (0.2), promote (0.02); if the long side's +0.10 is real it still retires; only a phase shift to >= +0.4 R promotes (7 months) | kill at the first n >= 10 clusters with E- >= 10; retire at 150 clusters / 12 months |

Not ranked (bench, no card): T02 7-star MTF long (+1.06 R, n = 7, 1.2 a year: a logger, not a test; log its events in the Malkan readout, no slot); reclaim-at-close 4h (+0.27 %, n = 114, in percent not R, 2022-24 only; a new count in R would be a new trial); the 4h no-confluence RSI bounce cell (+0.024 R, n = 624, one of dozens of exploratory cells, eh-s3). eh-s1 (T07/T08), eh-o1 (T13), eh-o2 (T14/T15) had not shipped: a PASS from any of them takes the spare slot ahead of #3 under the same rule, by the brief's PASS-first order (DECISION (OURS) 6).

Raw cards filed (SONNET, prio 2), one per ranked setup, as the brief allows:
1. `testnet-forward krown-s8-4h: ...` E+/E- columns in the weekly readout; A/B/C untouched.
2. `testnet-forward malkan-level-short div-3-10 BTC 4h: ...` swap the 30-trade kill for this rule; pool ETH paper by day cluster.
3. `testnet-forward T06 rsi-ma-cross 4h BTC+ETH: ...` context-only paper run under this rule.

## Q6 What not to do (families that stay dead; cite)

| Family | Result | Do not |
|---|---|---|
| Malkan 7-star spinning top, 4h/1d, 3 R / 20 bars (T01) | FAIL -0.217 R, n = 108, CI upper +0.077 < MDE 0.42; 0 of 108 reach 10 R (eh-h1) | re-code with other thresholds; the sourced reading is spent |
| First-touch sweep-and-reclaim of PDH/PDL/PWH/PWL, 15m, 2 R (T04) | FAIL -0.221 +- 0.043, n = 1150, every year negative; repeat touch -0.695 (eh-h3) | session or knife filters: the best block (00-04) is still negative |
| Speed-in + time-at-level fade, 15m (T05) | FAIL -0.086, n = 300, CI upper +0.074 < MDE 0.228, negative every year (eh-h4) | re-cut the 2x2 "fast/time<=2" cell (+0.054, descriptive, post-entry time) as a trial |
| Wick at an HTF level, first touch, effort volume, maker limit at the level, next-level target, BE (T09/T10) | FAIL -0.581 / -0.804 R, n = 41 / 47, both CIs below 0; fill rate 55 % and the fills are the adverse ones (eh-s2) | the Asia 68 % V-sweep (00-04 is the worst cell: -1.10 / -0.97 R); the 3x volume gate (removes 3 of 97) |
| RSI 40/60 bounce with another TF at the line, 1h/4h, 2.5 R (T11/T12) | FAIL -0.146 / -0.133, n = 1588 / 1477, CI upper < 0 < MDE; no dose-response 1/2/3 TFs (eh-s3) | any confluence count as a gate on this entry; "HTF bias" as RSI vs 50 (93 % of events are "against" by construction) |
| 1h auction fade (FAST_REJECTION), any fixed R | -0.087 R net 1 R, n = 1871, 8 of 8 years negative; 2 R -0.035, 3 R -0.023 (REVIEW_FABLE a) | another 1h fade study, hand-picked trades (POSTMORTEM s1 C6) |
| 5m/15m in-session fade with HTF ladder and node/BE/half/trail exits | all 10 headline cells negative under FEES_DERIBIT (5m -0.35..-0.39, 15m -0.20..-0.25); range is the worst regime; ladder has no gradient (census 2026-11-09) | re-run with a different management; "delta with trade side" (-0.07..-0.02 on 15m, post-hoc) as a trial without a new pre-registration and live delta |
| WaveTrend crosses, Bollinger range brackets, pre-US failed break (10 symbols), Jala SMA crosses, Chronos, SMA200 long-flat | REAL as coded (PLAN.md s1 table) | re-run at any m |
| Krown S8 under FAIL-A/B/C as the only verdict | A/B/C kill a +0.25 R edge 41 % and a +0.40 R edge 17 % of the time (sim_output.md table 5) | read an A/B/C kill as "no edge": it is "stopped", and the E- column says whether it was evidence |
| Any "30 closed trades, net R <= 0" kill (malkan card, POSTMORTEM s3 plan, REVIEW_FABLE d) | false-kill 19 % at +0.25 R, 9 % at +0.40 R, never promotes (table 5) | carry it into a new FORWARD_PREREG |
| A longer backtest for any of the above | d-phase-first-method-1106; PLAN.md s5 verdicts | file a backtest card as the next step of a FAIL or INCONCLUSIVE |

## DECISION (OURS) list
1. The rule is a betting e-process pair (not an SPRT): no Gaussian or likelihood model of R is needed, only bounds, which fixed-R exits provide; it is valid at every look.
2. mu0 = 0 R (brief), delta = 0.25 R, a = -3 R, b = target - cost; lambda grid {1/16, 1/8, 1/4, 1/2, 3/4} of the maximal safe bet, uniform weights.
3. Thresholds: 1/alpha_slot = 80 (family 0.05 over K = 4 slots), 1/beta = 10, n_min 30 / 10, retire at 150 clusters or 12 months. Chosen before the simulation and not changed after it; the simulation only reports them.
4. The synthetic shapes: 2.5 R and 1 R targets, 20 % time-stop leg uniform on +-0.6 R, 0.05 R cost (the wave's 4h fee_r 0.02-0.05 R). The hit probability is solved from the true mean, so each cell has an exact mean.
5. Krown S8 keeps FAIL-A/B/C as its operative stop (live tree, not this worker's to change); this design adds the E+/E- columns and recommends the swap in the card text. The 12-month retire does not apply to it until the operator adopts the rule.
6. eh-s1/o1/o2 unshipped at run time: treated as "no PASS" for the ranking; a later PASS takes the spare slot first.
7. ETH legs are paper until the executor has ETH-PERPETUAL; a pooled run with paper legs is promotable with the paper share named.
8. Risk 1 % of the slot subaccount per trade, fixed in USD for the run; paper runs use 1 unit.
9. One observation per UTC-day cluster (4h/1d setups), same UTC 4h block for 1h and faster.
10. No change of exit, symbol set, or thresholds after the first fill; any change opens a new slot with a new pre-registration.

## Noticed
- The Krown R7 FAIL rules A/B were set "so neither rule is looser" than each other, but at a 2 R target and a 35-45 % hit rate a 12 R drawdown or 12 straight losers is a routine excursion: the simulation puts their false-kill at 41 % for a +0.25 R edge. The readout card should carry the E- column before any A/B/C kill is read as evidence.
- The brief's "30-40 % at 2.5-3 R vs 45-50 % at 1 R" are not two edges but two sides of the same line: at a 1 R target 45-50 % is -0.15..0 R net (the census null), at 2.5 R 30 % is break-even and 40 % is +0.4 R. Every counted 1 R family sits at 42-50 %, every counted 2-3 R family at 29-39 %: both at zero.
- Event rate, not statistics, is the binding constraint: the slowest candidate (Malkan, 1.1 a month) cannot reach n = 30 inside two years alone; the fastest (T06, 16 a month) is the weakest. Pooling by cluster is the only lever that does not require new ideas.
- research_kit.regime_tag returned None for three workers (eh-h2, eh-h5, eh-s3 Noticed); a repo-side fix is still open and matters for the forward phase tag.
- The run_cmd shell on this station does not accept heredocs or multi-line python -c; patches went through a throwaway script in this folder (deleted).
