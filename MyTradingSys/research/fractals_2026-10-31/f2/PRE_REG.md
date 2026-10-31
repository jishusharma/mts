# F2 PRE-REG: rolling 1h DFA Hurst regime gate on RSI-DIV-MTF and the F1 pivot fade, vs shuffled, random and circular-shift gates

Frozen 2026-10-31 BEFORE any event outcome was joined to H (no run_f2.py exists at this commit). Spec: SYNTHESIS.md s3, s4 row F2, s7;
VALIDATION.md 3d, 4a, 4d, 5b; reviews/R1_LITERATURE_TECHNIQUES.md rank 2. Every parameter is OURS unless marked SOURCED. Nothing is tuned after the run.
One look at the price-only H series (no outcome file read) was taken before freezing, to see the on-fraction of the two thresholds:
H over 30,168 DEV hours has mean 0.496, sd 0.056; H<0.45 on 21.7 % of hours, H>0.55 on 17.4 %. Thresholds were NOT moved after that look.

## Design (frozen)
| item | value | label |
|---|---|---|
| Data | BTCUSDT 1m monthly files F:/MTS/data/tom_raw/klines, 2022-01-01..2025-06-30; files after 2025-06 never opened (study.py LAST_MONTH); bars at/after 2025-07-01 dropped | SOURCED (SYNTHESIS F2 row) |
| Bars | complete 1h UTC buckets (tf_break_event_study `bars`) | OURS |
| Series | 1h log returns r_k = ln(close_k / close_k-1), only when bars k-1 and k are consecutive hours | OURS |
| H | DFA-1 exponent on a rolling window of W = 480 returns (20 days): profile of the demeaned window, boxes of s in {8,16,32,60,96,160} (all divide 480), least-squares line per box, F(s) = sqrt(mean squared residual), H = OLS slope of log F on log s. Window must hold 480 true consecutive-hour returns, else H is missing | OURS (estimator SOURCED: Peng 1994 DFA; Bariviera 2017 uses DFA rolling, R1 s1b); FORMULAS.md s27 |
| Availability | H over returns up to bar i is known at open(i) + 3600. For an event entering at second t the H used is the latest with avail <= t (bars closed at or before the entry; the entry hour is never inside the window) | OURS (SYNTHESIS s3 rule) |
| Thresholds | 2 only: A keeps events with H < 0.45 (mean-reverting regime); B keeps events with H <= 0.55 (drops the trending regime H > 0.55). 0.45 / 0.55 are the vendor cut-offs in R1 s1b (ANECDOTE, no evidence attached) | OURS (cut-offs borrowed from ANECDOTE) |
| Layers (k = 2) | L1 RSI-DIV-MTF: p1b_rsi_feenet/events_feenet.csv, n = 640, entry 2022-01-06..2024-06-29, r_net per event, entry time = column `time`. L2 F1 pivot fade: all REAL events of f1/run_f1.py build_events (CONF_ANY + NONE), r_net column `net_r`, entry second = `t`, DEV 2022-01..2025-06 | SOURCED (existing frozen event rules, not retuned) |
| Hypothesis (direction, pre-registered) | both layers are mean-reversion entries (fade a level / buy-sell a divergence). They do better when H is low. So for each test, lift = mean net R of KEPT events minus mean net R of REMOVED events is expected > 0 (A: kept = low H; B: kept = not trending) | OURS |
| Trials | 2 thresholds x 2 layers = 4 tests (F2-1 RSI A, F2-2 RSI B, F2-3 FADE A, F2-4 FADE B), four TRIALS.md rows written at this commit before outcomes | SOURCED (VALIDATION 4d) |
| Warm-up | events with no H (first 480 hours of 2022, any gap) are dropped from every group and counted | OURS |
| Splits | S1 = event entry 2022-01-01..2023-09-30, S2 = 2023-10-01..2025-06-30 | OURS |
| Switches | on the hourly H series inside a split, the kept / removed state per threshold is turned into runs; only runs of >= 24 hours count; switches = counted runs - 1 | OURS |
| CI | week-block bootstrap (entry week), 2,000 resamples, 95 % percentile, seed 31, on lift = mean(kept) - mean(removed) | OURS |
| Control C1 shuffled-H | permute the valid hourly H values at random (1,000 permutations, seed 31), look the shuffled series up at the same event times with the same threshold, recompute lift. p = (1 + #{null lift >= observed}) / 1001 | OURS |
| Control C2 random gate | per test draw a random subset of the layer's events with exactly the observed kept count (1,000 draws, seed 31), recompute lift. Same p rule | OURS |
| Control C3 circular-shift, family-wise | roll the hourly H series by a random k in [1, N-1] (1,000 shifts, seed 31; same shift for all 4 tests), take the MAX over the 4 tests of lift each. A test is flagged if its observed lift exceeds the 95th percentile of that null max (harness.py idea: family-wise max statistic) | SOURCED (phase_tag/harness.py, VALIDATION 4d) |
| Planted edge | after demeaning kept and removed cells separately (lift = 0 exactly), add +0.25 R to every kept event of F2-1 (RSI, threshold A) and run the same pipeline: its CI must exclude 0 and C3 must flag it; without the plant nothing may be flagged | OURS (VALIDATION 5b) |
| Power | harness.power_n(sd of net R per event, effect 0.17 R ~ one taker round trip at a 1 ATR stop) printed beside each n | SOURCED (harness.py) |
| Fees | none added here: r_net columns already carry the all-taker round trip from fees.py (P1b and F1 pre-regs). No new cost constant defined in this study | SOURCED |

## Verdict rule (frozen), per test
- NOT_DECIDABLE: kept n < 200 or removed n < 30.
- PASS_LIFT needs ALL: kept n >= 200; >= 10 switches in each split; lift CI lower bound > 0; lift point estimate > 0 in both splits; C1 p < 0.05; C2 p < 0.05; flagged by C3.
- FAIL: kept n >= 200 and lift CI upper bound < 0.
- Otherwise INCONCLUSIVE.
- Reported beside, NOT part of the verdict: kept-side mean net R with its CI (a lift that leaves the kept side below zero is not a tradable gate), per-split lifts.
- F2 overall: PASS if any test is PASS_LIFT (a tradable follow-up then needs its own pre-reg); else NEGATIVE (an honest negative is a valid result). No gate, layer or rule is added by this study.
