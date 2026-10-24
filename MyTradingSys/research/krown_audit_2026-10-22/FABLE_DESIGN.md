# FABLE_DESIGN (S2): roles, testability, trades, confidence (2026-10-25, Fable 5.1, effort high)

Step S2 of `FABLE_CARD_CONFLUENCE.md` (s4, prompt s5). Written after S0 (e44b702c0) and S1 (54ae75603) shipped and BEFORE any outcome
exists: `run/sealed/` was not opened, no outcome column was parsed, no bar >= 2024-07-01 was read, and S2 opened no data file at all
(inputs: `run/COUNTS.md`, `run/bands.json`, `run/ACCESS_LOG.md`, the documents named in the s5 prompt, `GPT_AUDIT_S1.md`). Companion:
`PRE_REG_CONFLUENCE.md` (the tests and pass bars; it must precede S3/S4 in git order). No operator question was asked: every open point
is a DECISION (OURS) with its default stated. Labels: SOURCED = quote + file:line; OURS = judgement or tuned.

## 0. Answer in six lines
1. No layer is TESTABLE on its own slope: all 13 joined layers and the pooled slope are DESCRIPTIVE under the frozen gate (week-clustered
   MDE <= 0.10 R per S unit; best layer 0.172, pooled 0.170: COUNTS.md s2). What is powered: the standalone context read on all DEV
   decision bars, the pooled **mean** of a context cell against cost (prereg_gate PASS, COUNTS.md s2), and the T2 trade only if its effect is large.
2. Roles: CONTEXT and REGIME and LOCATION are each filled by exactly one OURS implementation of a Krown object (D1, D2, D3); TRIGGER by
   12 joined trigger tables; RISK by SOURCED structure (KR-Q05/Q06/R07) plus an OURS vol-target; **JUDGE is empty** for this run (forward only).
3. Expansion direction (GPT_AUDIT_S1 HIGH): this run uses the **F6 definition** (sign of the 4h close change since BBWP_4h was last <= 50),
   not the shipped six-bar difference. Reason and consequence in s2; the S1 code change is a precondition for S3 (PRE_REG s0).
4. Trades: T2 (Krown S8 on 4h, structural stop, BBWP-peak exit) is the only verdict-bearing trade; T4 is descriptive; T3 becomes the S16
   interaction cell inside the pooled read; T1 is dropped; T5 goes to the forward call ledger.
5. Confidence = a logistic probability of sign(net) on D1/D2/D3 with layer intercepts, three reliability bins, Brier read once on VALIDATION;
   on testnet it is a tag on the alert and gates nothing.
6. Expected result, said now: the context read (a) decides the run. If D1 does not beat the naive trend baseline, the Krown CONTEXT role
   closes for filters and only the sizing arm (vol-target from BBWP) and T2 remain.

## 1. Role table (one role per layer; same-object layers merged; evidence file:line)
Role order is SOURCED from Krown: trend > volatility > structure > momentum
(`krown_capture_2026-10-16/transcripts/ta101_missing4/hNfjyrJEytI_timed.txt` 00:10:22-00:10:50, cited in FABLE_CARD_CONFLUENCE.md s2).

| role | filled by (this run) | merged same-object layers (one slot, not counted twice) | evidence | state in this run |
|---|---|---|---|---|
| CONTEXT | D1 = side agreement with `trend_1d_ours` + `trend_1w_ours` (OURS impl. of KR-L10/KR-T03), raced against `naive_trend_sma200` and `naive_trend_ret20` | weekly 55 EMA side (KR-M10); weekly/monthly RSI < 40 = Malkan's MTF filter (REVIEW_OPUS F11: weekly RSI, not daily); `rsi_zone_1d_ours` (KR-S03) | COUNTS.md s3 (D1 shares pooled 39.7/53.6/6.7 %), s7 (trend_1d is close to a year dummy: 2022 23/47/30, 2023-24H1 33/55/12); REVIEW_OPUS F2, F12 | FILLED, untested; standalone read (a) is the gate |
| REGIME | D2 = BBWP_4h (OURS tf; KR-Q01 settings basis 7 / lookback 100 SOURCED, FORMULAS.md:537) relative to the event side; BBWP_4h also as the vol forecast for sizing | funding-sign x side (KR-LQC02): `funding_extreme` table NOT_RUN on this host (COUNTS.md s2); OI: NOT_IN_DATA before 2025-09 (REVIEW_OPUS F15); `positioning/oi_delta` descriptive only | COUNTS.md s3 (D2 pooled 16.3/77.8/5.9 %), s6 (bbwp_high 85 frozen); KROWN_RULES.csv KR-Q02 "high volatility is BBWP above 85 ... a break is confirmed when volatility rises above the 50th percentile" | FILLED; (b) vol-forecast read; funding is a ledger row |
| LOCATION | D3 = within 0.25 x ATR14(1d) of a ranked Krown zone on the correct side or in the outer 10 % of the daily range (+1); middle third (-1) (OURS impl. of KR-Z / KR-R01; bands frozen COUNTS.md s6) | Tom balance edges = Krown range edges (KR-S3/TOM-2; `tom_core` STOPPED, LAYERS.md:13); session_levels prior-day H/L (NOT_RUN: 1m archive absent, COUNTS.md s2); fabio_lvn_touch (NO_SIDE, COUNTS.md s2); wlow weekly low (a zone candidate, n = 8); LC level families (live only, no DEV table); pitchfork median lines (detector built, no event table, LAYERS.md:232) | COUNTS.md s3 (D3 pooled 16.4/54.9/28.7 %), s6 grid (pass 1 found no in-band point: +1 is saturated at 0.5 ATR); REVIEW_OPUS F10 | FILLED by Krown D3 only; the merged objects contribute nothing measurable on this host |
| TRIGGER | the 12 joined trigger tables: bb_top_reversal 15m (fade), malkan_rsi 1h, rsi_reclaim 1h, cc_msb 1h, fabio_escalation 1h, session_momentum 5m, rsi_divergence 1h and 4h (fade), candle_pattern 1h/4h, volume 1h/4h; wlow_bounce 1h (n = 8) | candle_pattern close-through = Krown BREAK-CLOSE (KR-Z07, REPORT.md s5.2 "candle_close ... already its definition"); volume spike = Krown volume ratio (KR-V, FORMULAS 21.9); malkan_rsi and rsi_reclaim share RSI14 and the 40/60 levels (one momentum object: both stay as separate tables but are one slot in any trade) | COUNTS.md s2 inventory; event types per layer COUNTS.md s2 (design s6.0 + OURS); every one is FAIL / INCONCLUSIVE / no edge alone (LAYERS.md status lines 43-149) | FILLED, all DESCRIPTIVE (s3 below) |
| RISK | stop = far side of the compression range (KR-Q05, SOURCED structure, no distance); exit = BBWP peak then loss of its MA (KR-Q06) or range height from the trigger (KR-R07); size = vol-target 1 / predicted vol (OURS, REVIEW_OPUS amendment 9), optionally x (1 + 0.5 x D1) only if (a) passes | KR-P02 scale-out (20-85 %, long only): not tested; KR-X01 close-based exit: BLOCKED (conflict C3, MTS needs a protective stop, KROWN_RULES.csv KR-X01) | KROWN_RULES.csv KR-Q05 "the stop on the opposite side of the compression zone (for an upside break a CLOSE below the bottom of the range)"; KR-Q06 "once volatility loses its own moving average and comes down the move is basically over"; KR-R07 "project that height from the breakout trigger as the first area of interest; a heuristic, not a law" | FILLED by rule, **no tested layer**: the role has structure but no evidence |
| JUDGE | nobody | callers (Qriptal, RLinda, Bennett, Crypto Chase, Roman: self-reported 67.1 % wins unverified, LAYERS.md:192); Krown daily call ledger (YOUTUBE_SAMPLE.md, accrues forward) | LAYERS.md:192; REPORT.md s4 "accrues slowly; never compare inside sealed windows" | **EMPTY** in this run (forward collection only; no DEV read possible) |

Not assigned (no DEV event table or excluded by the card): bigtrade (TRIGGER candidate, excluded: only post-fix rows), oi_delta (REGIME, no rows),
turn_of_candle (timing, not a trigger), wavetrend (TRIGGER candidate, FAIL/INCONCLUSIVE, no table), funding_extreme and session_levels
(inputs absent on JIS-NB: a host with `F:/MTS/data/candle_close_dev_2022_2024` can add them in S4 without a design change, as pre-listed
members of the trigger set with the same fixed horizon). Empty roles: **JUDGE**. Roles filled by rule only, with no measurable layer behind them: **RISK**.

## 2. Expansion direction: which definition the run uses (GPT_AUDIT_S1 HIGH)
Facts. `backtest/layers/krown/krown_context.py:181` computes `exp_dir_4h_ours = sign(close[i] - close[i-6])` (six-bar difference; the docstring
at :171 cites REVIEW_OPUS F6). REVIEW_OPUS.md:24 F6 defines "Expansion direction = sign of the 4h close change since BBWP_4h was last <= 50",
and LAYER_CONFLUENCE_DESIGN.md s9 adopts the review's amendments (s9.2 "D2 is set per event from the direction of the 4h expansion").
GPT_AUDIT_S1.md finding 1: the two definitions disagree on 3,139 of 5,472 four-hour bars and change 366 of 22,862 usable layer-event scores;
S>=+2 pooled moves from 353 to 351; S=+3 (12) and S<=-2 (1,849) are unchanged. Most of the 3,139 are bars where BBWP_4h <= 50 (F6 gives 0
there); D2 reads the direction only when BBWP_4h >= 85 (exhaustion) or when a fresh expansion is confirmed > 50 (`d2_regime`,
krown_context.py:239-253), so the 366 scores are the whole effect on S.

**DECISION (OURS): the run uses the F6 definition.** Direction at 4h bar i = sign(close[i] - close[j]) where j is the most recent bar <= i with
BBWP_4h[j] <= 50 (j = i gives 0, which never reaches D2 because D2 needs BBWP_4h > 50); if no such j exists in the available history the
field is None and the event is not usable (same rule as every other missing field).
Reasons: (1) it is the adopted specification (F6 + design s9.2); the code comment itself cites F6, so six bars is an implementation slip, not a
recorded design choice; (2) D2 asks whether the event fades or rides *the expansion*, and the expansion is the move since volatility crossed its
median: a fixed 24 h window measures the last day's drift, which inside an expansion older than six bars can be a pullback and flips the sign of
exactly the events D2 is for; (3) it costs nothing now: no outcome has been read, the frozen bands (near_atr 0.25, edge 0.1, bbwp_high 85:
`run/bands.json`) do not depend on the direction, and the change touches 1.6 % of layer-event scores; (4) keeping six bars would mean the
pre-registration adopts a definition first seen in code after the counts, which is the order the rules forbid.
Consequences, fixed now: the S1 code change (`exp_dir_4h_ours` -> F6, a hand-number test, `test_shifted_join_leaks` unchanged, COUNTS.md,
`joined_events.csv` and `counts_cells.csv` regenerated with no outcome read) is a **precondition for S3** (PRE_REG s0). The bands stay frozen even
if the regenerated D2 shares move (the 5 % rule in COUNTS.md s6 was applied once and is not re-run; a share below 5 % is reported, not fixed).
Residual, not a precondition (LOW): `d2_regime` still takes a per-layer FADE/BREAKOUT type (COUNTS.md s2 "event type"), which F6 asked to drop;
in the shipped code the type only decides which of the two contrasts counts +1, the direction is per event. Logged, not reopened.
**GPT LOW finding:** the audit could not reach `run/sealed/` event tables or `F:/MTS/data/krown_daily/BTCUSDT_1d.csv`, so the S1 counts are verified
only conditionally on the producer's snapshots (event keys, daily fields). The regeneration above is run on a host with the sources and the
auditor's script (`research/gpt_burn_2026-10-24/gx2-confluence-s1/audit.py`) is re-run against it; S3 does not start on a conditional base.

## 3. Testability per trigger layer (from COUNTS.md only)
Gate (PRE_REG_S1_COUNTS.md s1 F8, OURS): TESTABLE iff week-clustered slope MDE <= 0.10 R per S unit; DROP iff median cost/R > 0.25 at the layer's
natural stop (COUNTS.md s5, 0.10 % round trip) and no horizon extension makes the gross move >> cost; else DESCRIPTIVE. Gross move is an outcome and
was not read; the horizon-extension clause is judged on timeframe arithmetic only (a 15m stop of 0.29 % against a 4 h / 24 h BTC range of several
tenths of a percent to several percent is a different trade, OURS).

| layer | tf | n usable | weeks | slope MDE (R/S) | median cost/R @0.10 % | verdict | note |
|---|---|---|---|---|---|---|---|
| bb_top_reversal | 15m | 1553 | 128 | 0.213 | 0.349 | **DROP** at its natural stop | BLOCKED.md: cost alone 0.349 R > 0.30 R plausible gross; stays in the pooled fixed-horizon read as a DESCRIPTIVE horizon-extension row (16 x 15m = 4 h) |
| malkan_rsi | 1h | 127 | 81 | 0.634 | 0.163 | DESCRIPTIVE | n < 100 in every S cell but the middle |
| rsi_reclaim | 1h | 960 | 128 | 0.248 | 0.136 | DESCRIPTIVE | |
| cc_msb | 1h | 807 | 128 | 0.264 | 0.154 | DESCRIPTIVE | |
| fabio_escalation | 1h | 294 | 102 | 0.374 | 0.174 | DESCRIPTIVE | |
| session_momentum | 5m | 894 | 128 | 0.251 | 0.129 | DESCRIPTIVE | one event per day by construction |
| rsi_divergence_1h | 1h | 498 | 125 | 0.272 | 0.130 | DESCRIPTIVE | |
| rsi_divergence_4h | 4h | 137 | 81 | 0.507 | 0.066 | DESCRIPTIVE | best cost geometry of the fades |
| candle_pattern_1h | 1h | 10718 | 128 | 0.172 | 0.188 | DESCRIPTIVE | closest to the gate; weight-capped in the meta-analysis (F4) |
| candle_pattern_4h | 4h | 2835 | 128 | 0.191 | 0.090 | DESCRIPTIVE | |
| volume_1h | 1h | 3388 | 123 | 0.202 | 0.076 | DESCRIPTIVE | descriptive table by nature (F16) |
| volume_4h | 4h | 643 | 109 | 0.294 | 0.034 | DESCRIPTIVE | |
| wlow_bounce | 1h | 8 | 8 | 2.439 | n/a | DESCRIPTIVE | n = 8; T4 parent |
| POOLED (unique) | | 18247 | 128 | 0.170 | | DESCRIPTIVE (slope) | mean-vs-cost gate PASS at n_eff 1203 (COUNTS.md s2): a cell **mean** is testable, a slope is not |

**Counts: TESTABLE 0, DESCRIPTIVE 12, DROP 1 (bb_top_reversal at its natural stop), NOT_JOINED 6** (fabio_lvn_touch NO_SIDE; funding_extreme,
session_levels NOT_RUN; bigtrade, oi_delta, turn_of_candle EXCLUDED). Consequence for the design: no per-layer slope verdict exists at any outcome;
the verdict-bearing objects are (i) the context read (a) on all DEV decision bars, (ii) the pooled D1 contrast as a cell mean against cost,
(iii) T2. Everything per layer is reported with its CI and no verdict (PRE_REG s3).

## 4. Why this is not a rerun of context_factors_2026-10-16
That study tested the operator's composite C (a trigger made of context conditions on 1h decisions) against context-matched controls drawn from
ledger events, and came back INCONCLUSIVE on counts alone: 241 of 1,010 C events found >= 10 controls, 164 matched days against 387 needed,
E = -0.0233 R (SE 0.0739), all 1,010 executed C trades -0.137 R net, Holm m = 37 (`context_factors_2026-10-16/RESULT.md` READ cell and "Why
INCONCLUSIVE"); its V2 successor widened the pool but cannot PASS because the mean-net gate was already read negative (`PRE_REG_V2.md` s3
"Honest expectation"). What was learned there and is reused here: the pool must be counted before the freeze (done: COUNTS.md s2-s4), controls
must be drawn from all same-side decision hours rather than ledger events (`context_null` keys hour x vol tercile x trend tag), the point-in-time
join must be proven by a planted leak (done: S1 shifted-join test; GPT_AUDIT_S1 leak table all PASS), and a context on 1h decisions is mostly
drift unless the year split is reported. What is new: (1) the context is read **standalone** on random entries first (PROJECT_VISION.md:262
"Confluence may gate a trade only after each input passed S3 on its own"), with a naive trend baseline as the competitor, so a positive would
credit Krown's trend definition only if it beats a 200-day average; (2) the primary fee-wall lever is a **sizing arm** at equal capital that keeps
the whole sample, not a filter that shrinks it; (3) the one trade is **structural** (T2: 4h compression breakout with a stop at the far side of the
range) where cost/R is small by construction, not a 1m-15m trigger inside the fee band; (4) the outcome unit is a fixed-horizon net return in %
and ATR(tf) pooled by random-effects meta-analysis across 12 trigger tables with a weight cap, not R in incomparable units; (5) inference is
week-clustered with a 2022 vs 2023-24H1 sign check and a DEV_EXT sign agreement before the single VALIDATION read. The new Holm family is logged
next to the m = 37 family (PRE_REG s4), not merged into it, because the hypotheses differ (Krown context as a reading of random entries and as a
conditioning of existing triggers, versus the operator composite as a trigger).

## 5. Trades (at most 5; T2 first). Every number OURS unless cited; all on DEV + DEV_EXT; VALIDATION once, later.
Common rules. Entry at the open of the bar after the trigger close (the event tables' convention). Costs: taker 0.10 % and 0.14 % round trip,
maker arm 0.02 % + fill haircut (a maker entry counts only when the next bar trades through the limit price by >= 1 tick, else the trade is
skipped; exits always taker). Funding: realised settlements inside the hold (DEV funding from the monthly fundingRate files as in
`context_factors_2026-10-16/RESULT.md` DECISION lines). Size: primary = equal notional per trade; sizing arm = notional x (vol_target /
predicted 24 h vol), predicted vol = realised 24 h vol of the last 7 days mapped by BBWP_4h decile (from read (b)); both arms at equal total capital.
Context conditions are written in two branches; only the branch matching the read (a) verdict is run as pre-registered.

### T2 (primary, verdict-bearing): Krown S8 compression breakout on 4h
- **Timeframe:** 4h BTCUSDT perp (OURS tf; Krown's own chart tf NOT STATED, KROWN_SETUP_CATALOG.md:43 "higher term (Bitcoin)").
- **Setup:** BBWP_4h min over the previous 6 closed bars <= 30 (OURS pick inside KR-Q02's "about 25-35", FORMULAS.md:537) and the current closed
  bar has BBWP_4h > 50 (KR-Q02 "a break is confirmed when volatility rises above the 50th percentile", SOURCED). The compression range = highest
  high / lowest low of the closed 4h bars from the earliest of those 6 bars with BBWP_4h <= 30 through the bar before the trigger (OURS).
- **Trigger and side rule:** the first 4h close outside the compression range on the confirming bar or on one of the next 2 bars (OURS window);
  side = direction of the break (KR-Q05 "wait for the first candle that breaks the range", SOURCED). One trade per compression; the range is
  recomputed only after BBWP_4h returns <= 30.
- **Context (branch if read (a) PASSES):** secondary variant T2-D1: take only breaks whose side equals `trend_1d_ours` (KR-L12 "favour the previous
  trend", SOURCED), reported beside the unfiltered primary; the primary stays unfiltered. **(Branch if (a) FAILS):** no context filter in any variant;
  D1 appears only as a tag. In both branches the primary T2 carries no context gate (PROJECT_VISION.md:262).
- **Stop:** hard protective stop at the far side of the compression range (OURS reading of KR-Q05 "stop on the opposite side of the compression
  zone"; his close-based version KR-X01 is BLOCKED by conflict C3). R = entry - stop.
- **Exit:** first of (i) price reaches entry +/- range height (KR-R07, SOURCED heuristic), (ii) BBWP_4h has been >= 85 and then closes below its
  5-bar SMA (KR-Q06, SOURCED wording; 85 and 5 OURS), (iii) stop, (iv) time stop 30 x 4h bars (OURS).
- **Expected n (OURS, counted by S3 before any outcome and written to `run/COUNTS_T2.md`):** DEV 40-80 (REVIEW_OPUS F13 "tens" with the flow
  conjunction; without it roughly double), DEV_EXT 30-60. If DEV n < 30 the verdict is INCONCLUSIVE, never FAIL.
- **Gross move needed:** cost is paid in %, so the mean signed gross move must exceed +0.10 % (taker 0.10 %) / +0.14 % (taker 0.14 %) /
  about +0.05 % (maker arm). In R: with a typical 4h compression range of 1.5-3 % (OURS estimate; measured in COUNTS_T2), cost/R is 0.03-0.07.
- **Single claim:** the first 4h close beyond a BBWP-confirmed compression range, in the break's direction, has positive net expectancy to the
  range-height / BBWP-peak exit on DEV and DEV_EXT.
- **Kills it:** mean net % at 0.10 % taker <= 0, or week-clustered t below the Holm bar, or opposite signs in 2022 vs 2023-24H1, or the matched
  random-entry placebo (same hour-of-day and vol tercile, 4h bars with no setup) not beaten at t >= 1.96. Any one = FAIL for T2 as specified
  (kill scope: this setup on 4h with this stop and exit; not KR-S8 on other timeframes, not Krown).
- **MDE, honest (OURS, sd 1.5 R, rho 0.1, m = 18):** n 40 -> 0.92 R; n 60 -> 0.75 R; n 80 -> 0.65 R. T2 passes only on a large effect; a small
  positive is hypothesis-generating and goes to the ledger, not to VALIDATION.

### T4 (descriptive, no verdict unless n >= 30): weekly-low sweep and reclaim (wlow x Krown fake-out filter)
- 1h, long only. LOCATION = prior ISO-week low (wlow V1 definition, `wlow_bounce_bbrsi60_2026-10-16/RESULT.md`). Trigger: a 1h close back above
  the weekly low within 1-3 bars of the poke (K-FILT window, OURS) and RSI14(1h) back above 40 (OURS). Stop below the sweep low; target the weekly
  range midpoint, then the prior-week high; time stop 24 h. Context branch if (a) passes: `trend_1w_ours` up or range; if (a) fails: no filter.
- Expected n: parent wlow has 8 events on DEV (COUNTS.md s2); the sweep variant perhaps 20-60 over 130 weeks (REVIEW_OPUS F13 "maybe ~60");
  DEV_EXT similar. Gross move needed: +0.10 % / +0.14 % per trade; cost/R unknown (the table carries no stop). Claim: the reclaim after a weekly-low
  sweep is net positive long. Kills it: n < 30 (INCONCLUSIVE) or mean net <= 0. It keeps its Holm slot (PRE_REG s4) but is reported descriptively.

### T3 -> the S16 interaction cell (not a trade trial)
Counter-trend fade at a volatility extreme (KR-S16 "enter against the move when volatility is very high", KROWN_SETUP_CATALOG.md:51) needs
LOCATION (D3) and REGIME (BBWP) as conditions, and neither has a standalone read that PROJECT_VISION.md:262 accepts (read (a) covers D1 only; read (b)
is a vol forecast). DECISION (OURS): T3 is pre-registered as the **D1 x D2 interaction cell** inside the pooled read (events with D1 = -1 and
BBWP_4h >= 85 against the expansion, fade layers only: bb_top_reversal, rsi_divergence 1h/4h), fixed horizon, descriptive, target = opposite range
edge noted as the trade-form for a later card. No stop, no verdict, one ledger row.

### T1: dropped
The 15m BB-mid rejection is dead on arrival at its stop geometry (REVIEW_OPUS F13: cost/R 0.2-0.47, needs >= 60 % hits at 1 R) and bb_top_reversal is
DROP in s3. The 1h re-specification with a k x ATR stop at cost/R <= 0.15 is one trial-ledger row (no run in this card).

### T5: moved to the forward call ledger
Hidden-divergence continuation after a volatility base (hNfjyrJEytI 00:16:57-00:17:20) is a weekly, months-long trade with single-digit n on DEV;
it is scored forward in the Krown call ledger (REPORT.md s9 card 6), not here.

## 6. Confidence output (replaces design s5; per REVIEW_OPUS amendment 10)
- Model: logistic regression of y = 1[net fixed-horizon return > 0] (for T2: target-first) on D1, D2, D3 as numeric -1/0/+1 plus one intercept
  per layer, fitted on DEV events of the 12 joined trigger tables (wlow excluded, n = 8). Fitted once; no interaction terms except the pre-registered
  D1 x D2 cell reported beside. DEV reliability is out-of-fold by ISO-week blocks (purged, 8 folds, OURS) so the DEV table is not in-sample.
- Reliability bins: S <= -1, S in 0..1, S >= 2 (pooled n 7,477 / 10,417 / 353 under COUNTS.md s3; the S = +3 bin alone has 12 events and is not a bin).
  Per bin: n, mean p_hat, realised rate, Wilson 95 % interval. No per-S-bin shrinkage (it empties exactly the tails).
- VALIDATION: Brier score and the three-bin reliability table read **once**, in the same single pooled VALIDATION trial as whatever passes
  (PRE_REG s6). Pass for calibration = realised rate inside the Wilson interval of p_hat in all three bins and Brier <= Brier of the layer-intercept-only
  model. A failed calibration retires the tag, not the layers.
- Alert tag on testnet (collection only, the `htf_context_live.py` pattern): `confluence: {D1, D2, D3, S, p_hat, bin, n_bin_dev, prereg: PRE_REG_CONFLUENCE.md}`
  appended to every emitted alert. **It gates nothing**: no order, size, veto or pause reads it; no live component may import it as an input until
  VALIDATION passed both the slope and the calibration and the operator signed the wiring decision (PROJECT_VISION.md:262; DEPLOY_RUNBOOK gate).
  Accuracy then has a measurable meaning: the share of alerts in bin S >= 2 and their realised rate against p_hat on VALIDATION.

## 7. DECISION (OURS) log for S2
1. F6 direction definition adopted; S1 code change is a precondition for S3 (s2).
2. Holm family m = 18 = COUNTS.md's 17 (context read (a), pooled test, 13 per-layer slopes, T2, T4) + the sizing arm; the bar rises (z 2.974 -> 2.991),
   never falls; the 13 descriptive slopes keep their slots so the bar does not move when they cannot verdict (PRE_REG s4).
3. Pooled verdict object = the D1 contrast as a cell mean against cost (powered) with the slope reported beside (descriptive); placebo (i) is
   verdict-bearing, (ii) is a p-value beside it (PRE_REG s3).
4. T2 primary is unfiltered in both branches; the D1-filtered T2 is a secondary variant in the (a)-PASS branch only.
5. T3 becomes the S16 interaction cell; T1 dropped; T5 to the call ledger; T4 descriptive with a Holm slot.
6. bb_top_reversal DROP at its natural stop, kept as a fixed-horizon row in the pooled read.
7. funding_extreme and session_levels join S4 only on a host that has their inputs, as pre-listed members with no other change.
8. No operator question was raised; budget at start 39 % weekly all-models (cap 45 %, stop at 44 %).
