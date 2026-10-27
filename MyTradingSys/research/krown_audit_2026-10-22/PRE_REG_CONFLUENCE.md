# PRE-REG: confluence S3 (standalone context read) and S4 (DEV trials). Frozen 2026-10-25 before any outcome is read.

Written by S2 (Fable 5.1) from `FABLE_DESIGN.md`, `run/COUNTS.md` (S1, commit 54ae75603), `run/bands.json` and `GPT_AUDIT_S1.md`. No outcome
column, no `run/sealed/` file, no bar >= 2024-07-01 and no data file at all was opened for this document. Its git commit must precede
`run/CONTEXT_READ.md` and `run/DEV_RESULTS.md` (FABLE_CARD_CONFLUENCE.md s6 success test 3). Class C2, weight CRUCIAL. Nothing here is a result.
Labels: SOURCED = quote + file:line; OURS = judgement or tuned. Any variant tried outside this file is a row in `research/layer_lab/TRIALS.md`.

## 0. Preconditions for S3 (all must hold; S3 does not start otherwise)
1. **Expansion direction = F6** (REVIEW_OPUS.md:24; FABLE_DESIGN.md s2): `exp_dir_4h_ours` at 4h bar i = sign(close[i] - close[j]), j = the most
   recent bar <= i with BBWP_4h[j] <= 50; None when no such bar exists. The shipped six-bar difference (`krown_context.py:181`) is replaced by an S1
   follow-up card that (a) changes only that field, (b) adds a hand-number test for it (FORMULAS.md:537 BBWP worked example extended by two closes,
   expected values computed by hand), (c) keeps `test_shifted_join_leaks` red on the leaking variant, (d) regenerates `run/COUNTS.md`,
   `run/joined_events.csv`, `run/counts_cells.csv` with no outcome read, (e) re-runs the GPT auditor's script
   (`research/gpt_burn_2026-10-24/gx2-confluence-s1/audit.py`) on a host that has `run/sealed/` and `F:/MTS/data/krown_daily/`, closing the
   GPT LOW finding (sources absent: counts verified only conditionally). Expected after the change (GPT_AUDIT_S1.md, conditional): S>=+2 pooled 351,
   S=+3 12, S<=-2 1,849; 366 layer-event scores change.
2. **Bands stay frozen**: near_atr 0.25, range edge 0.1, bbwp_high 85 (`run/bands.json`, COUNTS.md s6). If the regenerated pooled D2=+1 or D2=-1 share
   falls below 5 %, it is reported in COUNTS.md and nothing is changed.
3. Hosts: S3/S4 run where `F:/MTS/data` exists (DESKTOP-F7IU69N or JIS-NB); DEV_EXT 1m files (`dev_ext_2019_2021`) must be present for the DEV_EXT
   arms, else those arms are reported NOT_RUN and the VALIDATION precondition in s6 cannot be met.
4. `run/ACCESS_LOG.md` is appended by every S3/S4 run with min/max bar used per file; `note()` aborts on any bar >= 2024-07-01 00:00 UTC.

## 1. Data, sets, outcome unit (frozen)
- Sets: DEV 2022-01-01..2024-06-30 split 2022 vs 2023-24H1 (SOURCED operator, OPERATOR_DECISIONS.md:883,894 via PRE_REG_S1_COUNTS.md s3);
  DEV_EXT 2020-01-01..2021-12-31. Never read: VALIDATION 2024-07-01..2025-06-30 (one pooled read, a later card), HOLDOUT 2025-07-01..2026-09-30.
- Venue: Binance USD-M BTCUSDT perp bars (1h/4h/15m from `bigtrade/cache/perp`); daily context from Binance spot `krown_daily` (basis noted, F17).
- **Outcome unit for every pooled and context test (amendment 3):** net signed return over a fixed horizon from the entry open: 1h layers 4 bars,
  15m layers 16 bars, 5m (session_momentum) 48 bars, 4h layers 1 bar, i.e. 4 h for every layer (OURS, one clock), plus a 24 h horizon reported
  beside; in % and in ATR14(tf) units; signed by the event side; minus 0.10 % (primary) and 0.14 % round trip; funding settlements inside the window.
  R units of the event tables are not pooled (F4).
- Costs: taker 0.10 % and 0.14 % round trip (OURS scenarios); maker arm 0.02 % + fill haircut (FABLE_DESIGN.md s5 common rules).
- Inference: SE clustered by ISO week (primary) and a 20-day block bootstrap (1,000 resamples, OURS) printed beside; year split 2022 vs 2023-24H1
  must agree in sign for any PASS; MDE at 80 % power printed before the outcome of each test (from counts).

## 2. The Holm family (one family, m = 18, frozen)
| # | test | verdict-bearing | object |
|---|---|---|---|
| 1 | context read (a): D1 vs naive trend baseline on random entries | yes | s3.1 |
| 2 | pooled conditional read: D1 contrast as a cell mean against cost (only if 1 PASSES) | yes | s3.3 |
| 3-15 | per-layer slopes on S (13 joined layers: bb_top_reversal, malkan_rsi, rsi_reclaim, cc_msb, fabio_escalation, session_momentum, rsi_divergence_1h, rsi_divergence_4h, candle_pattern_1h, candle_pattern_4h, volume_1h, volume_4h, wlow_bounce) | no: all DESCRIPTIVE (COUNTS.md s2 MDE > 0.10 R/S); they keep their slots so the bar does not move | s3.4 |
| 16 | T2 | yes | s3.5 |
| 17 | T4 | yes only if n >= 30 on DEV, else INCONCLUSIVE | s3.6 |
| 18 | sizing arm: vol-target vs equal notional, pooled, Sharpe at equal capital | yes | s3.2 |
z_holm(18) = 2.991 (two-sided 0.05 / 18; COUNTS.md used m = 17, z 2.974: the bar rose, pooled slope MDE 0.170 -> 0.171 R/S). Holm step-down over
the verdict-bearing p-values with m = 18 (the descriptive slots count as never rejected). A recount before S3 that gives a larger m uses the larger m.
Logged next to the `context_factors_2026-10-16` family (m = 37, V2 m = 42) in `research/layer_lab/TRIALS.md`; not merged.
Beside the family, no verdict: context read (b), D2 and D3 contrasts, the S16 (D1 x D2) cell, the 24 h horizon, the 0.14 % and maker scenarios,
the per-year lines, the circular-shift p, the T2-D1 variant, and every ledger row of s5.

## 3. Tests and pass bars (fixed now)
### 3.1 Context read (a): does Krown D1 predict the signed 24 h net return better than a naive trend baseline?
- Population: every closed 1h bar of DEV (21,888) and of DEV_EXT as decision points; no trigger. Entry at the next 1h open; outcome r24 = 24 h net
  return in % (close 24 bars later over entry open minus 0.10 %), long sign. Overlapping windows are the reason for week clustering.
- Side readings at each point from the last available context row (available_at < decision_ts): side_D1 = +1 if `trend_1d_ours` and `trend_1w_ours`
  are both up, -1 if both down, 0 otherwise (both range -> 0, F17); side_sma = sign(close - SMA200) (`naive_trend_sma200`); side_ret = sign of the
  20-day return (`naive_trend_ret20`).
- Statistics: E_X = mean(side_X x r24) over points with side_X != 0, for X in {D1, sma, ret}; paired difference Delta = mean over points where
  side_D1 != 0 of (side_D1 x r24 - side_best x r24), side_best = the baseline with the larger E on the same points, chosen on DEV and fixed for DEV_EXT.
- Context-matched line (beside): E_D1 recomputed within strata hour-of-day x realised-vol tercile (`context_null.context_key`), equal stratum weights.
- **PASS iff** E_D1 > 0 with week-clustered t >= 2.991 AND Delta > 0 with week-clustered t >= 1.96 (OURS: the race is a nominal one-sided comparison;
  the Holm bar applies to the existence of the effect) AND E_D1 > 0 in both 2022 and 2023-24H1. **FAIL** otherwise. No INCONCLUSIVE state: the
  population is the whole set of DEV hours.
- Consequence: FAIL closes the Krown CONTEXT role for filters in this run (FABLE_CARD_CONFLUENCE.md s4 S3): tests 2 and the (a)-PASS branches of
  T2/T4 are not run; D1 remains a tag; the sizing arm and T2 primary run regardless.
- MDE (OURS, sd of r24 2.5 %, within-week rho 0.3, n 21,888, 128 weeks): about 0.47 % on E_D1; printed from the real counts before the read.

### 3.2 Context read (b) and the sizing arm
- (b), descriptive: Spearman rank correlation between BBWP_4h at each closed 4h bar and the realised volatility of the next 24 h (sqrt of the sum of
  squared 1h log returns), DEV and DEV_EXT, week-clustered t; reported with a decile calibration table (BBWP decile -> mean next-24 h realised vol).
  Expectation stated now: positive (volatility clusters). If the correlation is <= 0 the sizing arm uses trailing 7-day realised vol instead and says so.
- Sizing arm (test 18, verdict-bearing): over the pooled fixed-horizon events (s3.3 population, all S cells, both branches) compare arm A = equal
  notional per event with arm B = notional x (vol_target / predicted 24 h vol), vol_target = the DEV median predicted vol, capped at 3x and floored at
  0.33x (OURS), both arms scaled to equal total capital over DEV. Statistic: difference in weekly Sharpe (mean / sd of ISO-week net % sums) B - A,
  20-day block bootstrap CI and week-clustered t on the per-week difference. **PASS iff** Sharpe_B - Sharpe_A > 0 with t >= 2.991 and mean net %
  of B >= mean net % of A - 0.01 % (sizing must not buy Sharpe with a lower mean) and the same sign in 2022 and 2023-24H1. FAIL otherwise.
  The x (1 + 0.5 x D1) multiplier is a variant reported beside, only in the (a)-PASS branch.

### 3.3 Pooled conditional read (only if 3.1 PASSES)
- Population: the usable events of the 12 trigger tables (wlow excluded, n = 8) with the F6 context; one row per (decision_ts, side) in the pooled
  statistics, layer rows kept for the per-layer lines; fixed-horizon net return (s1).
- **Verdict object (test 2): the D1 contrast as a cell mean against cost.** For each layer: m_plus = mean net % of events with D1 = +1, m_minus = mean
  net % with D1 = -1, diff_L = m_plus - m_minus; combined across layers by inverse-variance random effects (DerSimonian-Laird) with any one layer's
  weight capped at 1/3 (F4). **PASS iff** the combined diff > 0 with week-clustered t >= 2.991 AND the combined m_plus > 0 at 0.10 % cost (the trade
  must pay, not only rank) AND placebo (i) is beaten: for every event, K = 20 matched random entries of the same side with the same D1 cell, hour-of-day
  and vol tercile (`context_null` draw, seed 0, without replacement, spaced > 4 h, kmin 10, drawn from all same-side decision hours: the V2 lesson),
  and the combined (event diff - control diff) > 0 with t >= 1.96 (OURS) AND the same sign of the combined diff in 2022 and 2023-24H1. FAIL otherwise;
  INCONCLUSIVE only if the matched-events count is below 80 % of events (then the pool, not the context, is the problem).
- Placebo (ii), beside: 200 circular shifts of the whole context series by >= 30 days (shift k x 30 days, k = 1..200 modulo the DEV length, OURS),
  recomputing the combined diff each time; p_shift = share of shifts with a diff >= the observed; reported, not a gate.
- Beside, no verdict: the pooled slope on S (descriptive, MDE 0.171 R/S); D2 contrast (events with D2 = +1 vs -1); D3 contrast (+1 vs -1); the S16
  cell (D1 = -1 and BBWP_4h >= 85 against the expansion, fade layers only); the 24 h horizon; 0.14 % and maker scenarios; ATR-unit versions.

### 3.4 Per-layer slopes (tests 3-15): descriptive
For each layer: OLS slope of net % on S with week-clustered SE, CI, n, weeks, year lines, printed in `run/DEV_RESULTS.md` with the label DESCRIPTIVE
(MDE > 0.10 R/S at any outcome, COUNTS.md s2). No verdict, no cell is promoted from these lines.

### 3.5 T2 (test 16): Krown S8 compression breakout on 4h
Definition exactly as FABLE_DESIGN.md s5 T2 (setup min6 <= 30 then > 50; range = the compression bars' extremes; first 4h close outside within the
confirming bar + 2; hard stop at the far side; exit range height / BBWP peak then below 5-bar SMA / stop / 30 bars; entry next 4h open; taker 0.10 %
primary). Counted first: `run/COUNTS_T2.md` with n, weeks, median range height %, median cost/R, per set (2022, 2023-24H1, DEV_EXT), written before
any T2 outcome is computed.
- **PASS iff** DEV n >= 30 AND mean net % per trade at 0.10 % > 0 with week-clustered t >= 2.991 AND mean net % > 0 at 0.14 % AND the same sign in 2022
  and 2023-24H1 AND placebo beaten: K = 20 matched random 4h entries per trade (same hour-of-day and vol tercile, no setup within the compression
  window, same side, same exit rules), T2 mean - control mean > 0 with t >= 1.96.
- **INCONCLUSIVE iff** DEV n < 30. **FAIL** otherwise. Kill scope of FAIL: this setup on 4h with this stop and exit; nothing else.
- Beside: maker arm; target-first rate; MAE/MFE; exit mix; T2-D1 variant ((a)-PASS branch only); sizing arm B applied to T2.
- MDE stated now (OURS, sd 1.5 R, rho 0.1): n 40 -> 0.92 R, n 60 -> 0.75 R, n 80 -> 0.65 R per trade. A PASS needs a large effect; anything smaller
  is hypothesis-generating and does not go to VALIDATION.

### 3.6 T4 (test 17): weekly-low sweep and reclaim, descriptive unless n >= 30
Definition as FABLE_DESIGN.md s5 T4. Counted first into `run/COUNTS_T2.md` (same file). **PASS iff** DEV n >= 30 AND mean net % at 0.10 % > 0 with
t >= 2.991 AND the same sign in both years AND the matched-random-entry placebo beaten at t >= 1.96. **INCONCLUSIVE iff** n < 30. FAIL otherwise.

## 4. Rules that bind every test
1. **Week clustering or 20-day blocks** (F2): no day-clustered or iid SE gates anything; day-clustered values may appear as footnotes only.
2. **Year split**: 2022 and 2023-24H1 must agree in sign for any PASS (trend_1d is close to a year dummy: COUNTS.md s7).
3. **DEV_EXT agreement before VALIDATION** (amendment 12): a DEV PASS goes to the single VALIDATION read only if the same statistic has the same
   sign on DEV_EXT 2020-21 (no significance required there). A DEV PASS with the opposite sign on DEV_EXT is logged as hypothesis-generating and
   does not spend the VALIDATION read.
4. **Placebo** (amendment 8): matched random entries are verdict-bearing (s3.3, s3.5, s3.6); the >= 30-day circular shift (200) is reported beside.
5. **Fee wall** (F3): every pass bar is a mean net % against cost %; cost/R appears only as the feasibility filter (< 0.25) and never as evidence.
6. **No band, threshold, horizon, window or family change after this commit.** Alternatives are TRIALS.md rows with no verdict. A change needed to
   run at all (a missing input, a host without files) is reported as NOT_RUN for that arm, never substituted.
7. **Labels**: every number in CONTEXT_READ.md and DEV_RESULTS.md is SOURCED or OURS; Haiku re-derives three numbers per file from FORMULAS.md
   (one BBWP value, one ATR14, one week-clustered SE) before `tasks.py done`.
8. **Survivorship** (amendment 12): every trigger in the pool already failed or was inconclusive on this DEV; a positive here is a second look and is
   written as hypothesis-generating until rule 3 and VALIDATION hold.

## 5. Trial-ledger rows pre-declared (no run, no verdict; one row each in TRIALS.md when touched)
Meta-labeling (logistic on D1/D2/D3 + funding over a frozen trigger, purged by week); horizon extension 24 h for bb_top_reversal (DROP at its stop);
funding-sign x side (KR-LQC02, funding only); T1 on 1h with a k x ATR stop at cost/R <= 0.15; T3 as a trade with target = opposite range edge;
the (1 + 0.5 x D1) sizing multiplier; D2 with bbwp_high 80 / 90 (COUNTS.md s6 grid, logged there already).

## 6. VALIDATION: one pooled trial, later card
Whatever PASSES in DEV under s3 and holds its sign on DEV_EXT (rule 3) is read once on VALIDATION 2024-07-01..2025-06-30 as **one pooled trial**: the
passing tests with their DEV-fixed definitions, plus the confidence model's Brier score and three-bin reliability table (FABLE_DESIGN.md s6), all in
one read by a separate card (`confluence-s5-fable-verdict` decides the list; the read itself is its own slug). No second VALIDATION read exists for
this family. HOLDOUT is never read by this programme. A PASS on VALIDATION licenses an alert-only tag on testnet, never a gate (PROJECT_VISION.md:262);
a gate needs a signed operator decision after that.

## 7. Fails of the programme (any one voids the run, FABLE_CARD_CONFLUENCE.md s6)
A VALIDATION or HOLDOUT bar read before s6; a band, threshold, window, horizon or family changed after this commit; an unlabelled number; a
confluence gate proposed for live before the context passed read (a) and VALIDATION; CONTEXT_READ.md or DEV_RESULTS.md committed before this file
in git order; an S3 start before the s0 preconditions are met.

## 8. Parameters: SOURCED or OURS
| parameter | value | label | source |
|---|---|---|---|
| Role order trend > volatility > structure > momentum | ordering only | SOURCED | hNfjyrJEytI_timed.txt 00:10:22-00:10:50 (via FABLE_CARD_CONFLUENCE.md s2) |
| BBWP basis 7, lookback 100, close | 7 / 100 | SOURCED | FORMULAS.md:537 (KR-Q01) |
| BBWP high 85, confirm > 50, compression <= 30 | 85 / 50 / 30 | SOURCED 85 and 50 (KR-Q02 "above 85", "above the 50th percentile"); 30 OURS inside "about 25-35" | KROWN_RULES.csv KR-Q02; FORMULAS.md:537 |
| Expansion direction | sign since BBWP_4h last <= 50 | OURS (REVIEW_OPUS F6 amendment) | REVIEW_OPUS.md:24; FABLE_DESIGN.md s2 |
| Fresh-expansion window | 6 bars | OURS | krown_context.py:29; COUNTS.md s6 |
| D3 bands near_atr 0.25, edge 0.1 | frozen | OURS (from counts) | run/bands.json; COUNTS.md s6 |
| T2 stop structure | far side of the compression range | SOURCED structure, OURS hard-stop reading | KROWN_RULES.csv KR-Q05 |
| T2 exit: range height; BBWP peak then below its MA | heuristic | SOURCED wording; 85 and 5-bar SMA OURS | KROWN_RULES.csv KR-R07, KR-Q06 |
| T2 trigger window +2 bars, time stop 30 bars | 2 / 30 | OURS | this file |
| Fixed horizon 4 h (and 24 h beside) | 4 h | OURS | REVIEW_OPUS amendment 3 |
| Costs 0.10 %, 0.14 %, maker 0.02 % + haircut | scenarios | OURS | REVIEW_OPUS amendment 3; BLOCKED.md unblock (a) |
| Holm m = 18, z 2.991 | fixed | OURS | s2 |
| MDE inputs sd_R 1.5, rho 0.1 | fixed | OURS | COUNTS.md s2 |
| Matched controls K 20, kmin 10, spacing > 4 h, seed 0 | fixed | OURS (context_factors V2 lesson) | context_factors_2026-10-16/PRE_REG_V2.md s1 |
| Circular shifts 200 x >= 30 days | fixed | OURS | REVIEW_OPUS F9 |
| Sizing caps 0.33x-3x, vol_target = DEV median | fixed | OURS | s3.2 |
| n >= 30 for a T2/T4 verdict | 30 | OURS | s3.5 |
| Sets DEV / DEV_EXT / VALIDATION / HOLDOUT | as s1 | SOURCED operator | OPERATOR_DECISIONS.md:883,894 |
