# PRE-REGISTRATION (DRAFT): Habib weekly/Sunday plan hit-rate vs placebo levels, BTCUSDT perp

> **DRAFT - awaiting operator approval.** Nothing in this file is frozen until the operator approves it and a commit says so. No holdout candle, no VALIDATION candle and no DEV candle was read to write it. Card `habib-holdout-prereg-draft`. Written 2026-10-24.

Status: planned test, not a strategy. No edge is claimed or implied. Testnet research only, no trade advice.
Precedes: any run of the placebo test and any release of the holdout read for the 9 plans in `PLAN_LEDGER.csv`. The commit that adds this file (once approved) precedes any commit that adds an outcome.
Format follows `research/wavetrend_2026-10-17/PRE_REG.md`. Habib is the analyst (the Discord channel is Qriptal).
Labels: SOURCED = quote + file:line; OURS = judgement or tuned (allowed: chosen on DEV, checked once on VALIDATION, holdout read once, variants in the trial ledger).

## 0. What was read to produce this file
- Read: `README.md` (this folder), `plan_score.py`, `PLAN_LEDGER.csv` (ids, timestamps, directions, spoken entry and target, split tags only), `research/qriptal_2026-10-10/RULES.md`, `research/core_readiness_2026-09-27/BACKTEST_PROTOCOL.md` s2, `research/imbalance_qriptal_2026-10-16/BACKTEST.md` header, the wavetrend PRE_REG for format.
- NOT read: any 1m/15m/1h candle of any window, any plan outcome. `plan_score.py` and `PLAN_LEDGER.csv` are not edited by this card.

## 1. The situation that forces a pre-registration
- All 9 priced BTC plans in `PLAN_LEDGER.csv` are dated 2026-07-14 .. 2026-09-22, inside the holdout window. SOURCED: "HOLDOUT: 2026-06-26 .. 2026-09-26 (last 3 months). Untouched until the rules freeze; run ONCE." (`research/core_readiness_2026-09-27/BACKTEST_PROTOCOL.md:25`). DEV for these plans is empty: there is nothing to tune on and nothing to score on DEV.
- So the only way to score them is to release the holdout once, under a frozen rule. That release is the operator's decision (README s8). If the operator declines, this study stays unrun and the answer is "no measurement possible until >= 12 plans dated before 2026-06-26 with typed levels exist".
- The 2026-10-18 Sunday plan has no typed level (README s3): excluded, not scored.

## 2. Hypotheses (all stated before data)
- **H0 (null):** the full-hit rate of Habib's spoken entry/target levels, scored with `plan_score.py`, is no higher than the full-hit rate of placebo levels with the same direction and the same offsets from the post-time price, placed at random times.
- **H1 (operator observation, README s1, SOURCED to the operator 2026-10-20: "More often than not, either completely or partly, his plans work out"):** the plan full rate exceeds the placebo full rate. One-sided. The full-or-partial rate is reported as a descriptive secondary.
- **Not tested here (explicit):** that his "imbalance" levels (H-FVG, H-F, H-SP, H-vol, wOpen, sweep-reversal; README s4) carry information. Seven independent posts cannot support a multi-definition test, and none of these definitions is adopted. Each needs its own pre-reg once >= 12 DEV plans exist. Imbalance variants run: 0.
- **Not tested:** execution quality (stop, size, adds). Execution is excluded as in `plan_score.py`.

## 3. Frozen numbers
| Item | Value | Label |
|---|---|---|
| Plan set | the 9 rows of `PLAN_LEDGER.csv` with status `NOT_SCORED_HOLDOUT_WINDOW`; they come from 7 distinct posts (2026-08-27T11:39:59Z carries 2 rows, 2026-09-21T07:11:25Z carries 2 rows) | OURS (ledger as shipped) |
| Unit of inference | the distinct post (7), not the plan row; rows of one post are pooled into one post-level score (mean of their 0/1 outcomes) | OURS |
| Holdout window | 2026-06-26 .. 2026-09-26 | SOURCED `research/core_readiness_2026-09-27/BACKTEST_PROTOCOL.md:25` |
| Fill window / open window | 24 h / 7 d after the post | SOURCED `research/qriptal_2026-10-10/RULES.md:7` (limit entry not filled within 24 h = NOT_FILLED) and `:10` (open after 7 days = closed at market); reused by `plan_score.py:23-24` |
| Outcome classes | full / partial / miss; PARTIAL_FRAC = 0.5; NO_DATA never a miss | OURS, fixed in `plan_score.py:25` before any scoring |
| Primary outcome | `full` indicator (entry, then first target, inside the windows) | OURS |
| Secondary outcome | `full or partial` indicator | OURS (descriptive, outside the decision) |
| Reference price P0 | close of the last 1m bar whose open time is strictly earlier than the post time (causal) | OURS |
| Placebo draws per post | 200 | OURS |
| Placebo random seed | 20261024, fixed in the run script and logged | OURS |
| Taker fee | 0.05 % per side, both legs (10 bp round trip) | OURS (carried from `research/imbalance_qriptal_2026-10-16/BACKTEST.md:4`; Binance USDT-M VIP0 taker) |
| Minimum posts to claim anything | 12 distinct posts | OURS (README s8 done-when) |
| Alpha | 0.05, one-sided, one primary test | OURS |
| VALIDATION stability tolerance | 5 percentage points | OURS |
| Fee-dominated flag | target distance below 20 bp of entry | OURS |

## 4. Placebo definition (exact, causal)
For a real plan with direction d in {long, short}, spoken entry E, first target T, post time t:
1. P0 = close of the last 1m bar with open time < t. Offsets a = (E - P0) / P0 and b = (T - P0) / P0 (signed ratios, measured from the real data at t; an entry on the "wrong" side of P0 for its direction keeps its signed a).
2. Placebo clock: draw 200 times t' from the DEV pool (below), each satisfying, using only information available at or before t':
   - same UTC hour-of-day as t, same day-type (Mon-Fri vs Sat-Sun) as t;
   - t' is a whole-minute bar boundary;
   - the 7-day window [t', t' + 7 d) lies inside the DEV pool (no crossing into VALIDATION or HOLDOUT);
   - t' is at least 7 d away from any real post time in the ledger (no overlap with the real plan windows);
   - drawn uniformly without replacement within a post, seed fixed.
3. Placebo levels: E' = P0' * (1 + a), T' = P0' * (1 + b), same direction d, where P0' is the close of the last 1m bar with open time < t'. Only candles before t' build the levels; only candles from t' on score them.
4. Score each placebo with `plan_score.score_plan` unchanged (same windows, same classes). The placebo full-rate p_i for a post = mean `full` indicator over its 200 draws (rows of one post pooled as in s3).
5. DEV pool for t': 2022-01-01 .. 2025-08-31. The protocol's dev window (2025-09-01 .. 2026-06-25) is reserved as VALIDATION for this study (s5). Rejected alternative: placebo clock drawn from inside the holdout (92 days minus the real 7 d windows leaves too few non-overlapping days, and it would read holdout candles beyond the real plans).

Why this is a fair placebo: it keeps his direction, his distances (risk/reward geometry and level spacing) and the time-of-day, and removes only the claim that his levels were placed with knowledge of what price would do. If price just trends or ranges, the placebo hits as often.

## 5. DEV / VALIDATION / HOLDOUT use
- DEV (2022-01 .. 2025-08): draws placebo clocks only. No real plan lies in DEV, so no plan outcome is read here. Run once to produce the placebo rate table per post geometry; the table is frozen (CSV hash logged) before any holdout read.
- VALIDATION (2025-09-01 .. 2026-06-25): the same placebo procedure on a second pool, read once. If the VALIDATION placebo full-rate differs from the DEV one by more than 5 pp for any post geometry, the placebo is regime-unstable and the study stops with "placebo not stable", no holdout read.
- HOLDOUT (2026-06-26 .. 2026-09-26): the 7 real posts scored once, after the DEV and VALIDATION tables are frozen and committed. Posts of 2026-09-15, 09-21 and 09-22 have windows ending up to 2026-09-29, past the holdout end; candles after 2026-09-26 are fresh unread data and are allowed. A plan whose 7 d window is not fully covered by stored 1m data is NO_DATA, never a miss, and is dropped from the count (reported).
- Read count: one holdout run, one script invocation; its stdout and the SHA of its output CSV are logged in trial row HP-H01 (s7). A rerun for any reason is a new ledger row and cannot change the verdict.
- The operator's approval of this file is the release of the holdout read for these 9 plans only.

## 6. Decision rule, fee-net rules, kill rules
**Test.** Post-level one-sided exact test. Real statistic: the number of the N real posts scored `full`. Null: each post is `full` with its frozen placebo rate p_i, so the null count is Poisson-binomial. p-value = P(null count >= real count). Alpha 0.05, one primary test, so no multiplicity correction; the descriptive variant is outside the decision.
**Power (stated up front).** With N = 7 the test detects only a large effect: if the placebo rates are about 0.3, 4 of 7 fulls gives p of about 0.13 and only 5 of 7 or more gives p < 0.05 (approximate, to be computed exactly at run time from the frozen p_i). A non-significant result means "cannot tell", not "no edge". Accepted: this is a feasibility read, not a go/no-go for trading.
**Fee-net rule (any tradability statement).** Per filled post, net bp of E, with no stop (none spoken; execution excluded): full = |T - E|/E in bp minus 10 bp; not full = (close at the end of the 7 d window - E) x d / E in bp minus 10 bp (close-at-market rule, `RULES.md:10`); not filled = 0, counted separately. Gross-only numbers are never reported as a finding. A plan with |T - E|/E below 20 bp is flagged "fee-dominated" and excluded from the fee-net mean.
**Net claim threshold.** Mean fee-net bp per filled post > 0 AND placebo-adjusted excess (same net rule on the placebo draws) > 0 with a 95 % bootstrap CI lower bound > 0 (resampling posts). With N = 7 this is expected to fail; failing is the pre-registered default outcome and ends this track.
**Kill rules (any one stops the study and is reported as the result):**
1. Fewer than 12 distinct posts with typed levels at run time: descriptive only; no p-value, no claim, no holdout read (current state: 7).
2. Placebo not stable (DEV vs VALIDATION gap > 5 pp on any post geometry): stop, no holdout read.
3. Any candle before a post's time used for anything other than P0: the run is void.
4. Holdout read twice for the same plan set outside HP-H01: the later numbers are void.
5. After the run: p >= 0.05, or fee-net mean <= 0, or net CI lower bound <= 0: verdict "no measurable edge in Habib's plans at this n". Nothing is adopted as a layer; no re-slicing by asset, direction or definition to rescue it.
6. If the operator gathers more plans (README s5), a new pre-reg is written; this one is not extended.

## 7. Variant count and trial-ledger rows
Variants run: **3** (scorer S1, placebo P1, placebo P2). Trial-ledger rows to add to `research/TRIAL_LEDGER.csv` (columns study,variant,run_utc,split,data_source,description,status), study id `habib_plan_placebo_2026-10-24`: **4 rows**.
| Row | Variant | Split | Role |
|---|---|---|---|
| HP-S1 | scorer `plan_score.py` (24 h / 7 d / 0.5), as fixed | none read | already counted in README s8 ("scorer 1 variant") |
| HP-P1 | placebo P1: offset-transfer random clock (s4) | DEV + VALIDATION table, HOLDOUT compare | primary, the only decision test |
| HP-P2 | placebo P2: mirrored direction (same post time t, same |a| and |b|, direction reversed, levels reflected around P0) | HOLDOUT, same single read | descriptive control: does his side beat the opposite side |
| HP-H01 | the holdout read itself (one row, output hash) | HOLDOUT | read-once log |
Imbalance definitions: 0 variants (s2). Before running, `verdicts.py check` for aliases {habib, qriptal, plan, wOpen} must be run and any prior row listed here; it was not executed for this draft.
No other variant (windows, PARTIAL_FRAC, draw count, pool, hour matching) may be run; a change is a new pre-reg.

## 8. Known weaknesses (read before trusting any later number)
1. N = 7 independent posts: only a large effect is detectable. A null is uninformative.
2. Spoken levels were extracted from transcribed calls (`research/qriptal_2026-10-10/CALL_LEDGER.csv`); extraction errors move levels and cannot be audited without the audio.
3. Plans enter the set only if a spoken entry AND first target exist; direction-only plans are absent (selection).
4. Post time is the video publish time (`research/qriptal_2026-10-10/PUBLISH_TIMES.tsv`), not the time he formed the plan. If it is later, the real score is biased up. Using the publish time as t for both real and placebo keeps them comparable, not clean.
5. The placebo transfers his offsets, not his level-selection logic: it tests "do levels of this geometry get reached", not "is his logic good".
6. The 2022-2025 placebo pool differs from mid-2026 in volatility and trend; the VALIDATION stability check is the only guard.
7. No stop in the fee-net rule: losses on non-full plans are unbounded within 7 d; the fee-net mean is not what a disciplined trader would keep.

## 9. DECISIONS (OURS, taken without operator input; conservative defaults)
- DECISION (OURS): unit of inference is the distinct post (7), not the 9 rows.
- DECISION (OURS): placebo pool is DEV 2022-01..2025-08; the protocol dev window is held as VALIDATION; no placebo from inside the holdout.
- DECISION (OURS): one primary outcome (`full`), one decision test, alpha 0.05 one-sided; partial is descriptive.
- DECISION (OURS): if the operator does not approve, no holdout candle is read and the README s8 default stands.
- DECISION (OURS): no imbalance-definition variants until >= 12 DEV plans exist.

## 10. Approval block (operator fills in)
Approved by: ____________  Date: ____________  Holdout read for the 9 plans released: yes / no
