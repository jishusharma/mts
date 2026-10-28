# Point-in-time levels, phases and cost: are the backtests reading what a trader could have drawn? (2026-10-16, Fable 5.1)

Session: JIS-NB worktree `claude/fable-catalogue-audit-rebuild-679c65`, claim `pit-levels`, base origin/fast-track 6dfa51eb.
Prompt: `fable_audit_2026-10-16/FABLE_PIT_LEVELS_PROMPT.md`. Inputs read: `FABLE_RUNS_AUDIT.md` (full), the builders listed in
section 2, `CATALOGUE_AUDIT.md` sections 2-5, `gross_effect_screen_2026-10-15/PRE_REG.md`. No VALIDATION or HOLDOUT bar read;
the count script refuses bars at or after 2024-07-01. No production code changed; tests and scripts live in this folder.
Labels: SOURCED (file:line or quote), RE-DERIVED (computed here), OURS. Operator overrides for this session: tool-turn cap 40,
no hand-over mid-way (the hook's cap-15 notices were overridden by the prompt). DECISION (OURS) lines mark defaults taken.

## 1. Verdict
**Leakage: the Python builders in `backtest/` are point-in-time where a decision reads them: 12 of 13 family checks PASS; the one
FAIL is a reporting split (full-sample volatility terciles in `tom_bt_report.py:161`), which no decision reads.** The pivot audit's
claim that availability "is NOT built" is half right: no module carries an `available_at` field, but every builder tested enforces
the same delay in code (`vp_pivot_probe.py:175-183` confirmation at the close of i+n plus one hour; `cc_structure.py:99`
confirmed_i < k; `tf_resample.py:114-116` closed buckets only; `screen.py:111-117` prior 20 days; `orderflow_bars.py:144-157`
prior 30 days). What is missing is the ledger, not the delay. Two builders sit outside this proof: the Java engine's zones
(`SetupCandidatesBuilder.java:299-322`: weekly/daily/4h profile, VWAP and bands, prior-day levels), which `tom_bt.py` consumes
through 15-minute snapshots, and the CVD level (`orderflow_bars.py:186-189`), which depends on the loaded start day and is
therefore not a level at all. VWAP has no Python builder; its anchor is NOT VERIFIED here (Java out of scope).
**Cost: of the 20 catalogue rows with a stated or derivable stop, 9 are FEASIBLE on Binance at their natural stop, all of them
daily/weekly-bar rows or intraday rows with a probe-extreme stop above 0.40 %; Tom's and Fabio's tick-sized intraday stops are
NOT AS WRITTEN (1.1-8 R of cost).** The one experiment that passes both gates with the most DEV events is the failed auction at
the prior-day value-area edge (FAB-4 / TOM-12): 4,905 triggers on DEV, 1,835 with a stop >= 0.40 %, MDE 0.094 R against a
cost of 0.179 R and a plausible gross of +0.75 R, so the PRE_REG freezes. Card `pit-prior-va-failed-auction-dev` (lane SONNET).
Where I disagree with FABLE_RUNS_AUDIT: its 3.2 says "every intraday Tom/Fabio row at the stop he states loses by construction";
RE-DERIVED here, the probe-extreme stop that both traders describe in words is above the 0.40 % floor in 37 % of DEV events
(count_prior_va.py), so the intraday family is not dead, it is filtered.

## 2. Inventory (READ): every builder of a level, zone, phase or session in `backtest/` and `backtest/layers/`
formed_at = last bar the value uses; available_at = first decision time that may read it; "later input" = does any bar after available_at reach a decision at t.
| family | builder (file:line) | formed_at | available_at | consumed by | later input reaches t? |
|---|---|---|---|---|---|
| prior UTC day high/low | `session_levels.py:43-52` day_levels | last 1m bar of day d-1 | 00:00 of day d (needs >= 1400 bars, :91) | `session_levels.py:90-93` failed_break_events | NO (PASS F1) |
| prior day / prior week POC, VAH, VAL | `vp_pivot_probe.py:431-453` static_levels, families :465-470 | period end | first 15-min refresh after the period | `vp_pivot_probe.py:490-507` events (level in force at the touch bar, :486-488 ffill) | NO (PASS F3 prior_day) |
| developing session / weekly profile | `vp_pivot_probe.py:403-429` developing (bars [anchor, refresh)) | bar before the refresh | the refresh (>= 12 bars) | same | NO (PASS F3 session) |
| anchored A1 (last major high to last major low) / A2 | `vp_pivot_probe.py:471-484` via last_confirmed_vec :175-183 | later pivot's 1h bar | close of pivot bar i+n, + 1 h | same | NO (PASS F3 A1, A2) |
| fractal pivots (width n) | `vp_pivot_probe.py:130-144`; usable index :170-172 | bar i | open of i+n+1 | A1/A2 profiles; CYCLE_DESIGN.md:7 (j+2 close) | NO (PASS F2b) |
| swing pivots (body, left=right=2) | `cc_structure.py:11-60` confirmed_i = i+right | bar i | bar i+right closed | `cc_structure.py:99` MSB scan (confirmed_i < k) | NO (PASS F2a) |
| Java zones: weekly_/daily_/4h_ vp POC/VAH/VAL/HVN, vwap + bands, prior_day_* | `SetupCandidatesBuilder.java:148-154, :299-322` (outside backtest/) | per snapshot | snapshot time (15 min, `tom_bt.py:30`) | `tom_bt.py:120-135` snapshot_to_row, zone_tf :33-47 | NOT VERIFIED here; `tom_profile_parity.py` exists for the profile; VWAP anchor unknown |
| VWAP | no Python builder; Java `buildVwap` (`tom_profile_parity.py:49`) | - | - | snapshots only (`p1_compare.py:20-24`) | NOT VERIFIED |
| session anchors | 00:00 UTC: `screen.py:82-134` (L1-L3), `session_levels.py:28-31` Asia/EU/US, `vp_pivot_probe.py:460-464`; US/London/Asia opens with DST: `fabio/v3/day_gates.py:46-77` | - | bar open | ledgers, day gates | NO (anchors are clock rules); DST handled in day_gates |
| 4h/day/week aggregation | `tf_resample.py:9-60` bucket_start, :90-116 closed only; `tom_bt.py:105-116` resample_dicts; `vp_pivot_probe.py:315-324` | bucket end | bucket end | all TF layers | NO (PASS F4, F4b) |
| regime tags | `tom_bt.py:256-272` regime_features (i = idx(t)-1), trend_tag | last closed bar | t | `tom_bt_report.py:158-161, :202-204` | NO for trend (PASS F5); **YES for vol terciles**: `tercile_cuts` over all trades (FAIL, descriptive split) |
| balance (Fabio S1) | `fabio/v3/signals.py:183-205` window [i-N+1, i] | bar i | close of i | `htf_context_live.py:87-103` (previous 4H balance probed) | NO (window ends at i; not re-tested, pure function of bars <= i) |
| P / B / D shape | none in code; catalogue says "taught elsewhere" (`CATALOGUE_AUDIT.md:127`) | - | - | - | n/a: defined in PIT_CONTRACT D-PBD |
| percentile thresholds | `screen.py:111-117` L4 80th pct over the prior 20 days; `orderflow_bars.py:144-157` 99th/99.9th over the prior 30 days (own-day fallback flagged thr_days=0, :236-241; excluded by `day_gates.py:99`) | prior days | day start | ledger; big-trade counts per bar | NO (PASS F6a, F6b) |
| ATR | `vp_pivot_probe.py:116-127` atr_sma (TR ending at i); R5 = ATR of 1h bars closed before the 5m open (:376-378); `fabio/v3/signals.py` atr(bars, i, N) | bar i | close of i | barriers, size filter 18.3 | NO (checked inside F2b) |
| CVD level | `orderflow_bars.py:176-190` load_days stitches cvd = carry + cvd_day from the first loaded day | - | - | any study reading `cvd` as a level | **series-start dependent** (RESULT.md:18-19 of the screen); windowed sums only (PIT_CONTRACT section 3) |
| big-move ground truth (zigzag legs) | `bigtrade/bigmoves.py` (hindsight by design, `capture.py:12`) | - | never a decision input | capture scoring only | label only; must never feed a fire |

## 3. Leakage proof (RE-DERIVED): `test_pit_leakage.py`
Harness: builder(bars) returns lev[j] = the value in force at the open of bar j; PIT iff builder(bars[:j])[j] == builder(bars)[j]
for 12-15 decision bars j (seeded synthetic bars, no market data). Each family runs on the repo code (must be identical) and on a
planted copy that peeks one bar (must differ at >= 1 j); PASS needs both, so a green row proves the test has teeth.
Run: `python MyTradingSys/research/pit_levels_2026-10-16/test_pit_leakage.py` (about 2 minutes; output below from the run on 2026-10-16).
| family | repo code | planted peek | verdict | file:line |
|---|---|---|---|---|
| F1 prior-period high/low | identical | caught (current-day level) | PASS | session_levels.py:43-52, :90-93 |
| F2a swing pivots, confirmed_i | identical | caught (pivot used before its right window) | PASS | cc_structure.py:49, :57, :99 |
| F2b fractal pivots + ATR14 | identical | caught (active at the open of i+n, no +HOUR) | PASS | vp_pivot_probe.py:130-141, :175-183, :116-127 |
| F3 profile: session (developing) | identical | caught (refresh bar added) | PASS | vp_pivot_probe.py:403-429 |
| F3 profile: prior_day (static) | identical | caught (segment runs 5 min into today) | PASS | vp_pivot_probe.py:431-453, :467 |
| F3 profile: A1_n2_k0 (last high to last low) | identical | caught | PASS | vp_pivot_probe.py:471-480 |
| F3 profile: A2_n2_k0 | identical | caught | PASS | vp_pivot_probe.py:481-484 |
| F4 closed buckets, tf_resample | identical | caught (partial trailing bucket) | PASS | tf_resample.py:114-116 |
| F4b closed buckets, tom_bt.resample_dicts | identical | caught | PASS | tom_bt.py:105-116 |
| F5 regime trend_tag (ret30) | identical | caught (label at bar open) | PASS | tom_bt.py:256-272 |
| F5 vol terciles | **differs** (cuts over all trades) | n/a | **FAIL** (descriptive split; no decision reads it) | tom_bt_report.py:158-161 |
| F6a screen L4 percentile | identical | caught (own day's end-of-day leg) | PASS | screen.py:111-117 |
| F6b orderflow 99th percentile | identical | caught (own day in the window) | PASS | orderflow_bars.py:144-157 |
Not proven by a test (documented only): the Java zones consumed by tom_bt (outside `backtest/`), VWAP (no Python builder), the
CVD level (a design property, PIT_CONTRACT section 3), the candle_close study's `label='right'` day index (`study.py:114`, a report index).
Trap coverage: pivot before its window (F2a, F2b), profile includes the decision bar (F3), full-sample percentiles (F5, F6a), day
buckets by open vs close (F1, F4), CVD start dependence (documented), repainting (F2b: a replaced pivot keeps its availability; the
ledger of PIT_CONTRACT section 1 makes this explicit), labels at bar open (F5).

## 4. The as-of contract
`PIT_CONTRACT.md` (same folder, 5.9 KB): the ledger schema of pivot_pattern_audit :41 with types; OURS definitions D-SESSION,
D-BAL, D-PBD, D-THIN, D-BIG (Fabio's 30 / 20 contracts as the SOURCED anchor), D-TREND, D-LEVELS, D-PIVOT, D-STOPFLOOR; each
with its bars-<=-t computation, what the trader sees, and the catalogue rows that need it; a forbidden list.

## 5. Cost in R per row (RE-DERIVED; C = 0.14 % all-taker, 0.09 % maker-in; break-even stop % = C / gross expectancy)
Trader's own SOURCED numbers (hQ8sOq67x5o, `CATALOGUE_AUDIT.md` 3.2 T-3): intraday swing 35 % at 4 R = +0.75 R per trade;
breakout 75 % win (R:R not stated); counter trades R:R 3-4 (hit rate not stated). Break-even stop at +0.75 R: 0.19 % taker, 0.12 %
maker-in; at the 0.40 % floor (`TOM_ON_BTC.md:24`) the cost is 0.35 R taker. Daily/weekly stop sizes are OURS estimates of a
typical BTC daily range (2-4 %) because no trader gives a distance; the DEV count gives the intraday probe-extreme distribution.
| row | stop (his words) | stop % | TF | cost R taker | cost R maker | SOURCED hit / R:R | verdict |
|---|---|---|---|---|---|---|---|
| TOM-1a | "stop-loss of 20 points in the DAX" (C:316); above the volume bell | 0.08-0.13 | 5m | 1.1-1.7 | 0.7-1.1 | counter 3-4 R | NOT AS WRITTEN |
| TOM-1b | "entered the market at 640, you had a stop loss at 730" (C:364) | 14 | 1d | 0.01 | 0.006 | swing 35 % / 4 R | FEASIBLE |
| TOM-2 | NOT STATED (above the balance edge, OURS) | n/a | 5m-1h | - | - | counter 3-4 R | not costable |
| TOM-3 | "risk of 12 ticks" at 6,768 ES (C:514) | 0.044 | 1m-5m | 3.2 | 2.0 | none | NOT AS WRITTEN |
| TOM-4 (+5) | "below the last volumes" / "below the last swing low" (C:588, :630) | derivable: probe-extreme class, median 0.28 (count) | 5m-15m | 0.50 at the median | 0.32 | swing 35 % / 4 R | FEASIBLE only in the >= 0.40 % subset (37 %) |
| TOM-6 | NOT STATED | n/a | - | - | - | breakout 75 % | not costable |
| TOM-12 | above the failed outside prices (derivable = probe extreme), target the impulse origin | median 0.28; feasible subset median 0.78 | 5m | 0.50 / 0.18 | 0.32 / 0.12 | breakout 75 % | FEASIBLE in the >= 0.40 % subset (n = 1,835) |
| TOM-15 | beyond the formation (derivable) on 30m / 5m | not computed (needs the 30m ATR table) | 30m | - | - | none | deferred |
| TOM-17 | NOT STATED | n/a | 1m | - | - | none | not costable |
| FAB-1 | "The first stop loss was here" (chart point) | n/a | 1m-5m | - | - | none | not costable |
| FAB-4 | "Stop was likely somewhere above here" = probe extreme | as TOM-12 | 5m | 0.18 (feasible median) | 0.12 | none | FEASIBLE in the >= 0.40 % subset |
| FAB-5 | "below the protection level ... risking maybe $2,000" at 30 NQ contracts (DyS79) | OURS derivation: 2,000 / (30 x 20 USD/pt) = 3.3 pts, about 0.02 % of NQ | 1m | about 8 | about 5 | none | NOT AS WRITTEN |
| FAB-6 | other side of the first 30 minutes (derivable) | not computed | 1m-5m | - | - | FR-81 "a lot of value" | deferred |
| KR-S1 | close beyond the zone's outer wick (CLEAR, K:210) | zone width, OURS 1-4 on 1d | 1d/1w | 0.04-0.14 | 0.02-0.09 | none | FEASIBLE |
| KR-S8 | first breakout candle's range (CLEAR, K:43) | daily range, OURS 2-4 | 1d+ | 0.04-0.07 | 0.02-0.05 | none | FEASIBLE |
| KR-S2/S3/S4 | OURS (close back inside) | zone width | 1d/1w | <= 0.14 | <= 0.09 | none | FEASIBLE (stop OURS) |
| MAL-2 | "stop loss will be below the candle" (M:97) | daily candle, OURS 2-4 | 1d | 0.04-0.07 | 0.02-0.05 | none | FEASIBLE |
| MAL-5 | "stop loss against below the longest" (M:193) | OURS 3-6 | 1d | 0.02-0.05 | 0.02-0.03 | none | FEASIBLE |
| MAL-16/17/18 | beyond pivot A/B of the divergence (CLEAR) | OURS 3-8 | 1d/1w | 0.02-0.05 | 0.01-0.03 | none | FEASIBLE |
Counts: 20 rows costed; FEASIBLE 9 (TOM-1b, KR-S1, KR-S8, KR-S2/S3/S4 as one, MAL-2, MAL-5, MAL-16/17/18 as one, plus TOM-12/FAB-4
in their >= 0.40 % subset, counted once); NOT AS WRITTEN 4 (TOM-1a, TOM-3, FAB-5, TOM-4 at its median); not costable 5; deferred 2.

## 6. The chosen experiment and why
Candidates passing section 3 (level from a PASS builder) and section 5 (feasible): the daily/weekly rows (KR-S1, KR-S8, MAL-2/5/16/17,
TOM-1b) and the prior-day-value failed auction (FAB-4 / TOM-12 subset). DEV events, count-only: daily/weekly rows give at most a
few dozen events in 912 days (pivot_pattern_audit REPORT: 1,810 of 2,016 cells under 100); the failed-auction family gives 4,905
triggers, 1,835 above the stop floor over 662 days, with a control of 1,254 touches. So the experiment is **the failed auction at
the prior-day VAH/VAL on 5m closes, stop at the probe extreme, target the other edge, feasible subset only** (`PRE_REG.md`).
Count-only power: MDE 0.094 R (80 %), cost 0.179 R, plausible gross +0.75 R (Tom's swing metrics, OURS transfer): freeze OK.
Card: `pit-prior-va-failed-auction-dev` (lane SONNET, ref PRE_REG.md), runs count -> freeze gate -> one outcome run -> RESULT.md
with one verdict per arm. The kill scope is this family only. Not chosen: the daily rows (too few events; they go to G3 marking
first, P6 of the catalogue audit), and any 1m tape row (stops below the floor).

## 7. Operator decisions (defaults applied as DECISION (OURS) until overruled)
| # | decision | default |
|---|---|---|
| D1 | Adopt `PIT_CONTRACT.md` as the G3 reader protocol (the P3 page of the catalogue audit)? | YES; the P1 catalogue session links it from the shared frame |
| D2 | Build the level ledger (section 1 of the contract) as a module under `backtest/layers/levels/` before G5? | YES, Sonnet, S: the builders exist, only the ledger writer is new; its test is `test_pit_leakage.py` extended per origin |
| D3 | Java zone availability (tom_bt snapshots, VWAP anchor): verify or retire? | VERIFY with `tom_profile_parity.py` plus a VWAP anchor read of `buildVwap`; until then tom_bt results carry "levels NOT VERIFIED PIT" |
| D4 | Fix `tom_bt_report.py:161` (expanding terciles) or label it? | LABEL (descriptive split only); fix only if a decision ever reads it |
| D5 | Run the chosen PRE_REG now (card `pit-prior-va-failed-auction-dev`) or after G3 marking of FAB-4? | NOW: it is count-gated, DEV-only, and its levels are proven; G3 marking of FAB-4 runs in parallel |

## 8. Usage
`PIT_USAGE.md` (same folder): get_usage at start and end, other sessions at start and end, turn count.
