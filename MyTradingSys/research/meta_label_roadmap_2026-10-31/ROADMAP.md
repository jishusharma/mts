# Meta-labelling across MTS: review of the Opus analysis and roadmap (2026-10-31)

Operator order 2026-10-31 (via the login C coordinator): independently review the Opus analysis "meta-labelling across MTS" (side note
`metalabel_analysis_opus_2026-10-31.md`, not in the repo) and build the roadmap. Written by Fable 5.1 before any outcome of the running
Sonnet test is read. Paths are relative to `MyTradingSys/` unless they start with `scripts/`. SOURCED = quote + file:line; OURS = my judgement
or my arithmetic. No code change, no deploy, no live-path change. Everything here is on DEV (desk lock 2022-04-01..2024-06-30,
`research/sim_desk/desk.py:31`); VALIDATION and HOLDOUT stay sealed.

## 0. Verdict in one paragraph

The Opus analysis is right on the three things that matter: a filter can lift a weak-but-real edge over fees but cannot rescue a setup whose
gross is negative; the question is "under which conditions does this setup work" (regime), not "how many layers agree" (Q33 0/186 cells,
`system/LAYERS.md:85`); and nothing global gets built before one setup passes. It is weak or wrong on six points: (1) it proposes building a
trial ledger that already exists (`research/layer_lab/TRIALS.md`, 424 rows) while the real gap is that the project's trial families are never
merged; (2) "deflation" is named but no method is fixed, and the running card says "deflate for features tried" with no family or bar
(`system/tasks/meta-label-tom-vp-fabio-trades.json:36`); (3) sizing is proposed before any take/skip pass, on setups with negative gross;
(4) the snapshot has two look-ahead seams the note does not name (touch time vs fill time, and higher-timeframe values at an intraday entry);
(5) the tercile test is underpowered on both candidate setups by my arithmetic (section 1.5), so NOT ENOUGH DATA is the most likely result
and the roadmap must say what that means; (6) one feature (funding) is not on disk, and the "Fabio Model C" being labelled is our price-only
stand-in, not Fabio's setup. The roadmap below is gated so that the only thing that happens before a fee-net DEV pass is the running test
and its pre-registration amendments.

## 1. Review of the Opus analysis (where it is wrong, weak or missing something)

### 1.1 Look-ahead in the "layer state at entry" snapshot (missing)
- The desk trade row carries `touch_t` (`research/sim_desk/studies/_bars.py:195,211`), the time the level was touched; the fill is `entry`
  `(time, price)` inside `run_trade` (`_bars.py:176`) and can be later than the touch (limit waits, `_bars.py:126-133`). Features must be
  stamped at the fill time, not at `touch_t`; the note says "at entry" without saying which. Stamping at the touch is conservative (earlier),
  stamping at a later bar than the fill is look-ahead. Default taken: stamp at the fill bar's open, using bars that closed before it.
- Higher-timeframe features at an intraday entry (D1 trend sign, Cowen band side on completed weeks, 4h BBWP) must use the last CLOSED bar:
  the project's convention is `available_at = bar_open + timeframe` and "HTF value at time t = last HTF bar with open + htf_tf <= t"
  (`backtest/layers/FORMULAS.md:522`, WaveTrend 20.2). A D1 trend sign that reads today's daily close for a 14:30 UTC entry is look-ahead.
  Cowen's band is already "completed weeks only" (`research/sim_desk/PLUGIN.md:40`). BBWP is causal by its definition ("number of the previous
  lookback bbw values strictly below bbw[t]", `FORMULAS.md:544`). Relative volume must be the trailing hour-of-week median (TRIALS.md volume
  event table row, "hour-of-week median RV (8 wk, OURS)"), not a full-sample normalisation. (P0 used a trailing 24 h mean instead; a rerun should switch to the hour-of-week median.)
- Score terciles: the cut points must come from the training fold, not from all DEV scores; otherwise the test fold's bucket membership uses
  its own outcomes' scores. Small leak, but it is the leak that makes "top tercile" look better than it is.
- Missing test: there is a look-ahead forcing test pattern in the repo (`backtest/layers/alerts/test_lookahead_forcing_fabio_v3.py:50-92`,
  SETUP_REVIEW.md:211). The snapshot function, when built (phase 2), needs the same: shift a future bar and assert no feature changes.

### 1.2 Multiplicity and deflation (weak: named, not fixed)
- The note says "global ledger + deflation is the core control" and the card says "deflate for features tried" without a method. The repo
  has three fixed methods and the test must pick one before the outcome is read: BH-FDR q <= 0.05 on placebo p (Q33,
  `research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md:26`); a Holm family with m fixed in the pre-reg (confluence, m = 18,
  `research/krown_audit_2026-10-22/PRE_REG_CONFLUENCE.md:35-46`); DSR with n_trials (`FORMULAS.md:194-199`, `bt/bt_stats.py`). Default
  taken: Holm, family = setups x model specifications x one verdict bucket each (top tercile), m written before the read. Per-feature splits
  are descriptive beside the family, no verdict (as PRE_REG_CONFLUENCE 3.4).
- The 200-shuffle placebo answers "is this classifier better than a random labelling of the same trades"; it is a per-test p, not a family
  control. Both are needed: the placebo gives p, Holm sets the bar.
- The ledger exists. Opus step 4 ("one global trial ledger across setup x feature combos") duplicates `research/layer_lab/TRIALS.md`
  (every desk setting writes a row before the result shows, `PLUGIN.md:25`). What does not exist is a merged family: the confluence pre-reg
  logs its m = 18 "next to the context_factors family (m = 37, V2 m = 42) ... not merged" (`PRE_REG_CONFLUENCE.md:46`). The meta-label test
  is the third family asking the same question of the same DEV bars ("does other-layer context help"). Across the three the project has
  tried about 70 to 90 context cells on DEV (OURS count: 18 + 37/42 + this family). A third family is fine if it is logged and the roadmap
  says that a VALIDATION read of a context filter is one read for the whole question, not one per family.

### 1.3 Sizing is premature (wrong order)
- "Use sizing, not only take/skip" (Lopez de Prado meta-labelling) assumes a primary model whose bets are worth taking; sizing multiplies
  the sign. Tom VP's 10 FAILED runs are -0.20 to -0.26 R net per trade (`research/sim_desk/results/desk-tom_vp-*.json` kpis; e.g. c8d2f341:
  1812 trades, -0.257 R, 95 % range -0.296..-0.218). Sizing a negative stream by a probability that is itself unproven produces a
  negative stream with more variance.
- The project already has a pre-registered sizing arm with a bar: Sharpe at equal capital, and "mean net % of B >= mean net % of A - 0.01 %
  (sizing must not buy Sharpe with a lower mean), same sign in 2022 and 2023-24H1" (`PRE_REG_CONFLUENCE.md:71-75`). Reuse that bar; do not
  write a new one. Sizing is phase 3 here, after a take/skip VALIDATION pass, and in the live engine it is a live-path change (restart/reset,
  balance and API-error tests, CLAUDE.md Hard rules).

### 1.4 Cross-validation purging (adequate, one gap)
- "Week-purged CV" is enough for label overlap: Tom VP trades exit at acceptance, POC or day end (`studies/tom_vp.py` SETUP/TARGET text) and
  Model C exits by the US close, so no label spans more than a day; a one-week gap on both sides of the test fold removes overlap.
- The gap: the slow features (D1 trend, Cowen band, weekly regime) are constant for weeks. Random week assignment to folds puts the same
  regime in train and test, so the model learns "2022 was a bear" and is scored on 2022 weeks. Default taken: blocked contiguous folds
  (6 blocks of about 137 days each over the 822-day desk lock) as the verdict-bearing CV, and the project's own split, 2022 vs 2023-24H1,
  as the same-sign check (Q33 rule, `PRE_REG_Q33.md:26`; `PRE_REG_CONFLUENCE.md:24`). Week-purged K-fold is reported beside, no verdict.

### 1.5 Power for terciles (missing; decisive)
Arithmetic OURS, from the review's own rule n = 7.849 x (sd/delta)^2 (SETUP_REVIEW.md:240) and the exported 95 % ranges (sd back-solved as
half-range x sqrt(n) / 1.96; this treats the day-block range as if i.i.d., so real power is lower).

| Setup (largest DEV run) | n filled | mean net R | 95 % range | sd (R, implied) | n per tercile | tercile half-width | top tercile must reach | needed lift over base |
|---|---|---|---|---|---|---|---|---|
| Tom VP c8d2f341 | 1812 | -0.257 | -0.296..-0.218 | 0.85 | 604 | +-0.068 | > +0.07 | +0.33 R |
| Tom VP 20c09090 | 1765 | -0.238 | -0.284..-0.193 | 0.98 | 588 | +-0.079 | > +0.08 | +0.32 R |
| Fabio C 820e427d | 515 | +0.071 | -0.127..+0.274 | 2.32 | 172 | +-0.35 | > +0.35 | +0.28 R |
| Fabio C b6b13619 | 518 | +0.062 | -0.135..+0.268 | 2.34 | 173 | +-0.35 | > +0.35 | +0.29 R |

- Fabio C: to detect a tercile lift of 0.30 R at sd 2.3 needs n = 7.849 x (2.3/0.3)^2 = 461 per tercile; we have 172, so the test is
  2.7x underpowered. NOT ENOUGH DATA is the expected verdict unless the effect is enormous.
- Tom VP: n is fine but the base is -0.25 R; the top tercile must be +0.33 R better than the average while the other two average -0.42 R.
  A feature that separates that much would already show as a simple filter in the 12-run grid. Prior is low.
- The note's "pass = top tercile fee-net mean > 0 with day-block CI excluding 0" is the right bar; the roadmap must pre-state that the
  likely result is NOT ENOUGH DATA and that NOT ENOUGH DATA builds nothing.

### 1.6 Regime vs agreement (right framing, half-implemented)
- The reframing matches Q33 and the confluence design. But a logistic over 8 features IS a weighted agreement vote. The regime answer the
  operator asked for ("can confluence separate winners from losers") is the per-feature conditional mean: net R of the trades with D1 up vs
  down, BBWP high vs low, each with its day-block range and n. Default taken: report those beside the logistic, descriptive, no verdict,
  in the same table shape as the desk's breakdown rows (`desk.py:137` MIN_BUCKET 30).
- Only BBWP -> realised vol (rho 0.24, t 7.9) is an established context signal, and it predicts volatility, not direction (note; LAYERS.md
  guidance status). For a breakout setup (Model C) volatility is the right thing to predict: the test should state that BBWP is expected to
  work for Model C and not for a fade (Tom VP RETURN/FADE), so a BBWP pass on Model C alone is consistent with the prior, and a BBWP pass on
  Tom VP would be the surprise to distrust.

### 1.7 Fit with S0 and the discovery-phase freeze (right conclusion, one miss)
- A-20261030-1 (`system/ANNOUNCEMENTS.md:16-18`): machinery does not grow; "no new roles, pages, rule documents, vendors, lanes or
  dashboards"; new cards that add machinery go raw and stay parked ("S0 park"); research breadth is not cut. S0 exits: ready cards <= 15,
  claims <= 4 and 0 stale, worktrees <= 8, bookkeeping share < 30 % (`research/v1_plan_2026-10-20/D7_ROADMAP.md:16`).
- Opus is right not to build steps 2-5 before a pass. It misses that step 5 (sim desk panel) and the card's own "export per-trade feature
  table to the sim desk so the split is visible as charts" are page changes under the freeze. Default taken: the test result goes in its
  RESULT.md and in the result JSON (`kind` rows the desk already renders, `desk.py:440`), no new panel; the panel card is parked S0.
- Fit with S3 (two-layer funnel, `D7_ROADMAP.md:19`): S3 promotes "one config passes VALIDATION fee-net with lower CI > 0". A meta-labelled
  setup is such a config (setup + filter). It enters S3's WIP = 2 line like any other; it does not get its own track.

### 1.8 Missing facts
- Funding is not on disk for DEV: `F:/MTS/data/binance_metrics/*.csv` holds open interest and long/short ratios, no funding column
  (header checked 2026-10-31); `F:/MTS/data` has no funding folder. The feature list says "funding sign (if on disk)": it is NOT RUN, and the
  family m shrinks by its specifications. Say so in RESULT.md.
- The "Fabio Model C" on the desk is our price-only stand-in (first-30-minute range breakout on 1m klines, `PLUGIN.md:44`; SETUP_REVIEW.md
  3.5): the real v3 needs order-flow bars that start 2024-12-02. A pass labels OUR setup, not Fabio's; the roadmap says so in every line.
- Gross and fee are not in the exported kpis (only net); FORMULAS 18.7 (`FORMULAS.md:485-490`) defines them. The test must report gross and
  fee per bucket so a "fee lift" (fewer, larger trades) is told apart from a "direction lift".
- Fill optimism: touch = fill everywhere (`_bars.py:165-167`, SETUP_REVIEW.md:206). Any positive bucket must be re-run with a trade-through
  fill before it is called a pass (phase 1 stress).
- The VALIDATION read is a one-shot per setup family (`PRE_REG_CONFLUENCE.md:25`: "one pooled read, a later card"). A meta-label VALIDATION
  read on Fabio C consumes Fabio C's read. Default taken: the read is of (setup + filter) jointly and is logged as the setup's read in
  `research/layer_lab/TRIALS.md` and the holdout exposure ledger card (`tom-fabio-holdout-exposure-ledger`).

### 1.9 What Opus got right (keep)
Regime over agreement; a filter cannot rescue negative gross (it shrinks n until nothing is provable); multiplicity as the core control;
do not build 2-5 before a pass; the test protocol (features frozen before any outcome, logistic, purged CV, terciles, placebo, one VALIDATION
read, HOLDOUT never).

## 2. Roadmap

Gates are fee-net and pre-registered; nothing in a later phase starts before the earlier exit is written in a RESULT.md and a TRIALS.md row.
Costs are in cards (one Sonnet card ~ one worker session); budget context 2026-10-31: login C week 64 % of an 85 % cap, login B 88 %,
login A 18 % (hook header). Phases 0 and 1 fit this week on login A; phase 2 waits for S0 exit regardless of budget.

| Phase | Entry gate | Work | Exit gate (pre-registered, fee-net) | Builds | Cost |
|---|---|---|---|---|---|
| P0 Running test | pre-reg frozen (`4ca494b3a`) | card `meta-label-tom-vp-fabio-trades`; amendments of 2.1 applied POST HOC (one DEV read happened before they arrived) | `research/meta_label_tom_fabio_2026-10-31/numbers.json` + `output.md` | nothing | **DONE 2026-10-31 (`68eac1e27`)**: Tom VP FAILED (top third -0.277 R, CI -0.344..-0.211, n 608, placebo p 0.76, AUC 0.47); Fabio Model C stand-in NOT ENOUGH DATA (top third -0.003 R, CI -0.364..+0.404, n 162, placebo p 0.60). VALIDATION not read. Branches taken: FAIL row for Tom VP, NOT ENOUGH DATA row for Fabio C (card 2 of section 3) |
| P1 DEV pass stress | P0 PASS on at least one setup: top tercile lower day-block CI > 0 after fees, beats >= 200 shuffles, Holm within the family, same sign 2022 vs 2023-24H1 | trade-through fill rerun; 0.14 % round-trip cost scenario; per-feature attribution (which one carries it); Fable verdict (as confluence S5) | all three stresses keep lower CI > 0; then ONE VALIDATION read of (setup + filter), same sign and lower CI > 0 -> candidate row for `promoted_setups.json`, enters S3 WIP line | nothing (a RESULT.md and a verdict) | 1 Sonnet card + 1 Fable verdict turn |
| P2 Minimum snapshot | P1 VALIDATION pass AND S0 exit signed (or the operator's word) | `layer_state_at(ts)` shared causal snapshot in `research/sim_desk/studies/_bars.py` (last-closed-bar rule, features of 2.1), look-ahead forcing test, per-trade feature columns in result JSON (existing `kind` rows, no new page); family m logged in TRIALS.md | forcing test green on CI; one study reruns to identical numbers with and without the snapshot; no new page | the snapshot and its test only | 1-2 Sonnet cards |
| P3 Sizing arm | P2 done AND a second setup passes P1 | sizing by model score vs equal risk, bar copied from `PRE_REG_CONFLUENCE.md:71-75` (Sharpe at equal capital, mean not lower by more than 0.01 %, same sign both halves) | bar met on DEV, then its one VALIDATION read | research code only; live wiring is S5 and needs restart/reset/balance/API-error tests | 1 Sonnet card |
| P4 Live | S5 (`D7_ROADMAP.md:21`) | not in this roadmap | - | - | - |

### 2.0 Panel shape (operator decision d-meta-label-panel-simple-self-tested, 2026-10-31: "simplified and easy to test - check it yourself")
Built in P2 only. Per study: one table `Layer reading | trades | win % | average R after fees`, one verdict line
`Best third by filter vs random third -> PASSED / FAILED / NOT ENOUGH DATA`, the existing 6 example charts; nothing more. Every panel change
ships with an automated check: result-JSON shape, bucket trade counts sum to the filled trades, and a page click test like
`research/sim_desk/test_page_click.py`; the building session opens the rendered page and checks it before reporting. Testing is ours, not his.

### 2.1 Amendments to the running test (apply before any further outcome read; if a DEV read already happened, report it as read and apply the bar post hoc, labelled POST HOC)
1. Stamp features at the fill bar open (`entry[0]`), last-closed-bar rule for every higher-timeframe value (1.1).
2. Holm family, m = setups x specifications, written in RESULT.md before the read; the placebo p per cell; BH-FDR reported beside (1.2).
3. Tercile cut points from the training fold (1.1).
4. Verdict-bearing CV = 6 contiguous blocks; same-sign check 2022 vs 2023-24H1; week-purged K-fold beside (1.4).
5. Report gross, fee, net per bucket (FORMULAS 18.7); report n per bucket; under 30 per bucket = too few (desk MIN_BUCKET) (1.8).
6. ~~Funding = NOT RUN (not on disk)~~ Corrected 2026-10-31: funding IS on disk for DEV (`F:/MTS/Dumps/backtest/raw/fundingRate`, BTCUSDT 2020-01..2026-09) and P0 used it (1.8).
7. Name the setup "Fabio Model C price-only stand-in (ours)" in every table (1.8).
8. Power line per setup from section 1.5; NOT ENOUGH DATA is a named, expected outcome and builds nothing (1.5).

### 2.2 What the P0 result changes, per branch
| P0 result | What follows | What is NOT done |
|---|---|---|
| PASS on Fabio C stand-in | P1 on it; the sister card `meta-label-break-events-layer-features` runs with the same amendments; snapshot stays unbuilt until VALIDATION | no Tom VP work, no panel, no sizing |
| PASS on Tom VP | distrust first: a +0.33 R lift on a -0.25 R base is the surprise (1.5, 1.6); P1 stresses run before anything else; attribution must name one feature and its mechanism | no build until the stresses hold |
| NOT ENOUGH DATA (expected) | one rerun card: same frozen features on pre-DEV `dev_ext_2019_2021` for Model C (NY session on 1m klines exists there, A-20261018-2) to lift n toward 461 per tercile; if still NOT ENOUGH DATA, park meta-labelling for these two setups | no snapshot, no panel, no sizing, no new feature hunting |
| FAIL (top tercile CI below 0 or placebo not beaten) | TRIALS.md row; both meta-label cards closed with the result; meta-labelling returns only when a primary setup first passes gross on DEV (SETUP_REVIEW.md section 6 tests 2 and 3 are the ones that can) | everything |

### 2.3 Order across primary setups (which are worth meta-labelling at all)
Rule (Opus, kept): a filter lifts a weak-but-real edge; it does not rescue negative gross. Ranking OURS from the numbers on disk.

| Rank | Setup | Gross / net on DEV | Worth meta-labelling? | Why |
|---|---|---|---|---|
| 1 | Fabio Model C price-only stand-in (ours) | net +0.035..+0.071 R, n 515-518, CI spans 0 (results 820e427d, a955213e, b3972cec, b6b13619) | yes, first; underpowered 2.7x (1.5) | the only candidate with a positive mean; BBWP -> volatility fits a breakout |
| 2 | tf_break 1h/4h hold/reclaim/sweep events (sister card) | see `research/tf_break_event_study_2026-10-30/RESULT.md` (not re-read here) | yes, second, same amendments | event counts large; the card is already written |
| 3 | Tom VP return / fade / accept | net -0.20..-0.26 R, 10 of 12 FAILED | not now | needs +0.33 R lift; first make a variant pass gross (SETUP_REVIEW.md section 6 test 2, near-band placebo on dev_ext) |
| 4 | Tom level touch (POC/VAH/VAL) | gross -0.042..+0.010, net -0.185..-0.248 (SETUP_REVIEW.md:115) | no | gross ~0, the loss is the fee; a filter would have to find a subset with gross > fee |
| 5 | TOM-1a, FAB-1, FAB-2, FAB-4, CVD/escalation proxies | CODED-UNSCORED or NEG proxy (SETUP_REVIEW.md:44-60) | no | nothing to label; fix scoring (FAB-4 scored 0 R) and run the primary first |

### 2.4 Defaults taken (none is money, mainnet or the live tree)
- Holm as the family method; m = setups x specifications; BH-FDR beside.
- Fill-bar-open stamping; last-closed-bar rule; training-fold tercile cuts; blocked CV verdict-bearing.
- A VALIDATION read of (setup + filter) counts as that setup's one read.
- No new desk page or panel under S0; results go in RESULT.md and existing result-JSON rows.
- Sizing bar copied from PRE_REG_CONFLUENCE 3.2, not rewritten.
- Running test is not stopped or restarted; amendments apply from the next read, post hoc labelled where already read.

## 3. Cards filed (raw, this commit; `system/tasks/` checked for duplicates: none for these three)
1. `meta-label-prereg-amendments` (SONNET, prio 1): apply section 2.1 to the running test and its sister before any further read.
2. `meta-label-fabio-c-dev-ext-power` (SONNET, prio 2): the NOT ENOUGH DATA branch rerun on `dev_ext_2019_2021`, frozen features, n target 461 per tercile.
3. `layer-state-snapshot-causal` (SONNET, prio 3, note S0 park): phase 2 `layer_state_at(ts)` + look-ahead forcing test + the panel of 2.0 with its checks; starts only on a P1 VALIDATION pass and S0 exit.

Noticed (not fixed here): ~~funding data absent for DEV on this host~~ (wrong, see 2.1 item 6); exported desk kpis carry net only (no gross/fee); Opus step 4 duplicates
`layer_lab/TRIALS.md`; three unmerged context families on the same DEV bars (confluence m 18, context_factors m 37/42, meta-label).
