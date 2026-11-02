# RESULT: meta-label rerun, Fabio Model C price-only stand-in (ours), pre-DEV window 2020-01-02..2022-03-31

Protocol: `PRE_REG_EXT.md` (commit d24cc43f1, before any trade list of this window). Numbers: `numbers.json`, `output.md`; sim-desk export `sim_desk/results/desk-meta_label_fabio_c_dev_ext.json`. DEV 2022-04-01+, VALIDATION and HOLDOUT never read; frozen `PRE_REG.md` untouched.

## Verdict by the pre-registered rule: PASSED (marginal, read the flags)
Best third by filter: +0.430 R (95 % range +0.028..+0.869) vs random third (all model trades) -0.047 R.

| item | value |
|---|---|
| filled trades / complete-case (model) / dropped | 509 / 418 / 91 (Cowen 21-week warm-up, WaveTrend, BBWP warm-up) |
| n per tercile (top / middle / bottom) | 139 / 137 / 142 |
| top tercile mean net R, 95 % day-block CI | +0.430, +0.028..+0.869 (97.5 % level: -0.024..+0.937) |
| middle / bottom tercile mean net R | -0.355 / -0.215 |
| top-minus-bottom spread, CI | +0.645, +0.114..+1.194 |
| placebo (300 shuffles) | p95 +0.521 < real 0.645; placebo p 0.023 (real at 98.0th percentile); Holm (m = 2) 0.047; BH q 0.023 |
| gross / fee / net per top tercile | +0.668 / 0.238 / +0.430 R (middle -0.105 / 0.251 / -0.355; bottom +0.030 / 0.245 / -0.215) |
| power | sd (model sample) 2.144 R; delta_min at n_top 139 = 0.509 R (2.144 x sqrt(7.849/139), checked by hand); n needed per tercile for a 0.30 R lift = 401. The tercile has 139, so the 0.30 R lift is NOT resolvable; only the rule's lower CI bound clears 0 |
| same-sign check, 2020 vs 2021-01..2022-03 | top mean +0.336 (n 46) / +0.476 (n 93): same sign; spread +0.340 / +0.833: same sign |
| P0 DEV for comparison | top -0.003 R, n 162, placebo p 0.60. Pooled n_top by simple addition 301 (arithmetic only, no pooled model); still under 401 |

## Flags (why this is a hypothesis, not an edge)
- Weak ranker: out-of-fold AUC 0.527; the middle third (-0.355) is worse than the bottom (-0.215), so the ranking is not monotone.
- Fragile to the CV scheme: the week-purged random K-fold reported beside gives top +0.056 R, CI -0.296..+0.445, spread +0.239 (no verdict by protocol).
- The top mean (+0.430) equals the "luck of the best of 16 tries" level (0.428 = sd x sqrt(2 ln 16)/sqrt(n)); the 97.5 % CI includes 0; Holm p 0.047 is just under 0.05.
- It does not replicate the DEV window (P0 top -0.003 R, NOT ENOUGH DATA). One descriptive reading is distinguishable from zero after Bonferroni: relative volume low third -0.447 R (n 170, a loser bucket, not a winner).
- Gross of the top tercile is +0.668 R vs 0.238 fee: the lift is direction, not fewer-larger trades.
- The 2019-09..2019-12 part of the requested window has no perp 1m data on disk (public from 2019-12-31); the window actually run is 2020-01-02..2022-03-31. Fill check: all 509 fills coincide with the desk touch time (0 differ).
- Expected vs realised: pre-reg expected NOT ENOUGH DATA from ~140 per third; n_top came in at 139 as predicted, but the CI lower bound and placebo cleared, so the rule says PASSED rather than NOT ENOUGH DATA (the NOT ENOUGH DATA clause needs a CI that spans 0 and it does not at 95 %).

## What follows (conservative default, DECISION OURS)
Per PRE_REG_EXT section 3 this is a hypothesis for the card owner, not a gate. No VALIDATION read was made and none is made here (the one-shot read is spent on a decision, not on a marginal pass; ROADMAP 2.2 PASS branch: P1 stresses first: trade-through fills, near-band placebo; the DEV null of P0 does not support it). Meta-labelling for Tom VP is not revived; for Fabio C the combined evidence is one DEV null (n 162, -0.003 R) and one marginal pre-DEV pass (n 139, +0.430 R); treat as NOT confirmed and keep it parked until the stresses are run.
