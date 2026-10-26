# PRE-REGISTRATION: replace the HTF balance definition (bal_4h / bal_1d) - 2026-10-07

Session: MTS-2026-10-07-1000Z-APP-ANA-whea-htf (Track C). Playbook Part I: pre-registration first, run second.
Status: **BOUND 2026-10-07.** Operator direction this session: "replace-via-backtest". The operator delegated the sweep-range choice in
session ("make default choices to meet the task objectives"), which satisfies BUILD_PIPELINE R4-T3 "sweep ranges from operator": the
section 4 grids are bound as written. Any later change to sections 2-7 is a new pre-registration, not an edit. No outcome (return, forward range, flag-vs-future) has been computed for any candidate. Section 1
descriptive numbers contain no forward information.

## 1. Diagnosis: why bal_4h, bal_1d, failed_breakout are null (C1-C4)

- C1 Producer. `MyTradingSys/backtest/layers/fabio/htf_context_live.py`: `build_row()` (line 97) calls
  `signals.balance(bars, i, N_4H=240)` and `balance(bars, i, N_1D=1440)` and `failed_breakout()` (line 87). `balance()` is
  `MyTradingSys/backtest/layers/fabio/v3/signals.py:183-205`. `failed_breakout()` returns None when the previous-4H balance is None (R4-T2).
- C2 Logs. `runtime_data/htf_context_live.err.txt` and `.out.txt` are both 0 bytes (written 2026-10-06 16:02). No runtime error, no
  missing-input warning. The writer runs and writes rows (13 rows 10-02 .. 10-07; OI delta populated each time).
- C3 Cause: **not a bug. The rule is working as written and almost never returns a balance.** `balance()` requires
  `R <= k_bal * sqrt(N) * ATR_N` with k_bal = 0.8 (P02, labelled NS-fixed = no source) AND `|close - poc| <= 0.25 * R` (also NS-fixed).
  Measured on 6 days of live BTCUSDT 1m klines (8,641 bars, fetched 2026-10-07 read-only, windows stepped every 30 bars):
  N=240: 1 of 281 windows balanced (0.4%); N=1440: 0 of 241; N=60: 6 of 287. Ratio R/(sqrt(N)*ATR_N): N=240 min 0.68, p10 0.94, p50 1.38,
  p90 2.17; N=1440 min 1.03, p50 1.54. Re-run (validation, window 2026-10-01T11:16Z..10-07T11:15Z, same code): N=240 6 of 280 (2.1%),
  N=1440 0 of 240, N=60 6 of 286; ratio N=240 p10 0.94 p50 1.41. Same conclusion (all far below the 15% coverage floor in section 5). The threshold 0.8 sits below the 10th percentile, so the flag is a near-constant null.
  Over all 13 stored rows: bal_4h non-null 0, bal_1d non-null 0, failed_breakout non-null 4 (the 4 are the legacy `false` rows
  before R4-T2; they are not computed values). Branch classification: **missing/unsourced parameter calibration (NS-fixed constant too tight
  for 1m-ATR scaling), not a schema mismatch, not an unwritten branch, not a missing input.** Code comment in test_htf_context_live.py:126
  assumes ATR ~ 8.7 USD ("~108"); the live ATR_1m is ~34 USD, so the intended threshold is about four times lower than what the
  rule gives in practice (my reading; untested against the author's intent).
- C4 Parameters. K_BAL 0.8, BAL_POC_BAND 0.25, B_PROF 50 live in `v3/signals.py:25-27`. Provenance audit:
  `research/_archive/loose_2026-10/FABIO_PROVENANCE_AUDIT_2026-10-01.md:59` (P02 k_bal 0.8 + POC band 0.25 = NS-fixed, CONCEPT-ONLY) and `:98` (P41 B_prof 50 =
  SIM). No parameter file exists; they are module constants. The N values (240, 1440) are in the writer (`htf_context_live.py:31-32`).
  Per the provenance rule they are NO-SOURCE: flag, then remove or replace; never tune. This pre-registration is the replace path.

## 2. Hypotheses (declared direction)

Sourced anchor (Tier T3, Tom transcript, quoted from TOM_FABIO_STORY_2026-10-05.md and the TOM index): [TOM-031] "when supply and demand
are balanced, the market will always try to return to that equilibrium." [TOM-044] balance "in about 70% of market phases" (Tom's own
statistic, unverified, used only as a descriptor).
- H1 (information): a window labelled balanced has a **lower** forward realised range, normalised for volatility, than an unlabelled one
  (balance persists / returns to equilibrium).
- H2 (flag): after `failed_breakout = true` (probe beyond the previous balance edge, then reclaim), price moves back toward the
  previous POC / far edge by more than random 4H closes do, net of costs (Fabio model B probe-reclaim; reference models.py:121).
- H0: no difference. The incumbent (k_bal 0.8) is a degenerate case and cannot support H1 or H2 (coverage ~0%).

## 3. Data

- 1m klines `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-YYYY-MM.csv` (Binance, 2022-01 through 2026-09-26; 89 files in the folder,
  coverage and gaps to be recorded at run time, load-time continuity check as in tom_bt).
- Order-flow footprint for the profile POC: `F:/MTS/data/orderflow_1m/*.csv.gz` (2024-12-02 .. 2026-09-28, column `fp`). Where it is
  absent (2022-01 .. 2024-11), use the writer's own kline approximation (`klines_to_bars`, one 10 USD bin at hlc3), same as live.
- Periods (project protocol, TOM_CORE_BT): hist 2022-01 .. 2025-08; dev 2025-09-01 .. 2026-06-25; **holdout 2026-06-26 .. 2026-09-26, read once.**
- Costs: taker fee both sides from `backtest/fees.py` as of the run commit, recorded in the result block; no funding term (horizon <= 24 h
  with signed legs; funding per 8 h recorded as a sensitivity). Slippage: the P1 passive-fill result is NOT assumed.

## 4. Candidate definitions (declared trials, N = 28)

Evaluated at every 4H close (cell TF=4H, window N=240 1m bars) and every 1D close (TF=1D, N=1440).
- Family A (incumbent form, loosened): `R <= k * sqrt(N) * ATR_N` and `|c - poc| <= b * R`.
  k in {0.8 (incumbent), 1.0, 1.25, 1.5, 2.0}; b in {0.25 (incumbent), 0.5}; TF in {4H, 1D} -> 20 cells.
- Family B (efficiency ratio, no profile): `ER = |c_i - c_(i-N)| / sum|c_j - c_(j-1)| <= e`, e in {0.05, 0.10, 0.15, 0.25};
  TF in {4H, 1D} -> 8 cells.
- Every k, b, e, N value is NO-SOURCE and carries the label OPERATOR-EXPERIMENT. Nothing else is added after seeing results. Total
  declared cells N_trials = 28 (the incumbent is cell 1 of 28 in each TF).

Failed-breakout flag for each cell: unchanged definition from `htf_context_live.failed_breakout` (previous-window balance (H, L) probed
by a 1m close beyond an edge in the just-closed window, last close back inside [L, H]), computed with that cell's balance.

## 5. Method

1. Stage 1, coverage (no outcome data): fraction of closes with non-null balance on hist+dev. A cell with coverage < 15% or > 85% is dropped as
   uninformative (a constant flag carries no information). Tom's 70% is reported next to each coverage, not used as a target.
2. Stage 2, H1: forward range ratio FR = (max high - min low over next H bars) / (sqrt(H) * ATR_1m at the close), H = 24 h for TF 4H, 7 d for
   TF 1D. Statistic: median(FR | balanced) - median(FR | not balanced). CI95 by day-block bootstrap (block = UTC day, seed 12345, 2000
   draws). Overlap: forward windows overlap, so effective n = number of non-overlapping H blocks, reported beside raw n. Sign must hold in each
   calendar year of hist+dev. Placebo: shuffle the label within vol terciles (1000 shuffles); the real statistic must exceed the 95th percentile.
3. Stage 3, H2: events where the flag is true. Entry at the next bar's open after the close, side = reclaim direction (short after a probe above H,
   long after a probe below L), exit at the previous POC or the far edge touch, else time exit at 8 h; stop at the probe extreme. Net R after costs.
   Placebo: matched random 4H closes (same vol tercile, same hour of day), 1000 draws. Require effective n >= 100 (day-clustered); if fewer, H2 is
   labelled NOT EVALUABLE, not passed.
4. Selection uses hist+dev only. The surviving cell with the best Stage 2 CI lower bound is the single candidate; ties broken by higher coverage
   nearer 70%. Then the holdout is read **once**.
5. Multiple testing: Deflated Sharpe on Stage 3 net R with N = 28; PBO by CSCV (S = 16) over the 28-cell Stage 2 matrix.

## 6. Success criterion (replace the incumbent)

All of: (a) coverage in [15%, 85%] on hist+dev; (b) Stage 2 CI95 excludes 0 in the declared direction with year-by-year sign stability and
beats the placebo; (c) holdout agrees in sign and its CI95 excludes 0; (d) PBO < 0.5; (e) if H2 is evaluable: net mean R > 0, CI95 lower
bound > 0, and beats the matched placebo, DSR(N=28) >= 0.95. Passing (a)-(d) replaces bal_4h/bal_1d; passing (e) as well is required
before `failed_breakout` is used by anything beyond collection.

## 7. Failure criterion and consequence

Fail = no cell satisfies (a)-(d). Then: the NS-fixed balance rule is **removed** from `htf_context_live.py` (columns dropped or emitted as
a constant `UNAVAILABLE`, `failed_breakout` likewise), the layer keeps OI delta only, R5 (model B shadow) stays blocked for lack of a sourced
HTF definition, and the incumbent is recorded as NO-INFO (0.4% / 0% coverage). Mixed result (H1 passes, H2 not evaluable or fails): replace
balance, keep failed_breakout null with the reason logged.

## 8. Execution constraints

Offline script under `research/` only, reading F:/MTS/data; no live import edited. A writer change (a `.new` of `htf_context_live.py`) happens
only after the verdict, is promoted per the staging rule, and the pythonw writer is restarted by the supervisor only. No orders, no keys.

## 9. Result block

### Stage 1 (coverage), run 2026-10-10 by research/loose_code/b141_htf_stage1.py (test_b141_htf_stage1.py, 7 pass; incumbent cell cross-checked against signals.balance)
Data F:/MTS/data/tom_raw/klines, 2022-01-01..2026-06-25 (holdout NOT loaded); valid closes 4H 9821, 1D 1636; POC from the 10 USD hlc3 kline approximation (as live). Full table: research/loose_code/b141_stage1_result.json.
- Incumbent (k 0.8, b 0.25): 4H 3.3%, 1D 3.0% -> dropped (confirms NO-INFO, section 1).
- Kept (coverage in [15%, 85%]): 4H A k1.0/b0.5 21%, k1.25 34%/48%, k1.5 48%/68%, k2.0/b0.25 61%, ER e0.05 50%, e0.10 82%; 1D A k1.0/b0.5 19%, k1.25 30%/43%, k1.5 42%/62%, k2.0 55%/80%. 16 of 28 cells.
- Dropped: 4H k0.8 (both b), k1.0/b0.25 14.8%, k2.0/b0.5 85.0%, ER e0.15/0.25; 1D k0.8 (both b), k1.0/b0.25 13.9%, all ER (85%..100%). 12 of 28.
- Stage 2: see below. Stage 3, holdout, PBO/DSR: not run (no Stage 2 survivor).

### Stage 2 (H1 forward range), run 2026-10-10 by research/loose_code/b141_htf_stage2.py (test_b141_htf_stage2.py, 10 pass; mutation sqrt(H)->H fails 1 test)
16 kept cells, hist+dev only (holdout NOT loaded). Valid closes with a full forward window: 4H 9815 (effective n 1636), 1D 1629 (effective n 233). D = median(FR|balanced) - median(FR|not); H1 predicts D < 0. Full table: research/loose_code/b141_stage2_result.json.
- **No cell passes** (CI95 upper < 0 AND every calendar year D < 0 AND placebo beaten). Only 4H A k1.0/b0.5 has a CI95 excluding 0 in the declared direction (D -0.052, CI [-0.098, -0.004]) but 2022 is +0.041 and the placebo is not beaten.
- Direction: 4H family A D is small and negative (-0.01..-0.05), CI includes 0 in 5 of 6 other cells; 4H family B (ER) is the OPPOSITE sign (e0.05 D +0.13, e0.10 D +0.19, CI excludes 0 against H1: low-ER windows are followed by LARGER ranges); 1D cells are CI-wide (effective n 233), signs flip by year.
- Selected candidate: none. Per section 7 (fail = no cell satisfies (a)-(d)): the NS-fixed balance rule is removed from htf_context_live.py / emitted as UNAVAILABLE, R5 stays blocked, incumbent recorded NO-INFO. Not yet done: that writer change (needs a `.new` + supervisor restart), Stage 3 (H2, flag-based, depends on a balance definition so is moot), holdout (not read: no candidate), PBO/DSR (no candidate to deflate).
