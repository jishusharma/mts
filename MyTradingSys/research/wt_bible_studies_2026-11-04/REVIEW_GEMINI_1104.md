# Blind Spec Review: WaveTrend Bible Studies Frozen Designs (SPEC.md, Class C2)

- **Target Spec**: `MyTradingSys/research/wt_bible_studies_2026-11-04/SPEC.md` [SOURCED: SPEC.md:1-22]
- **Reviewer**: Gemini 3.8 Flash (independent cross-vendor review lens per `roles/lab_guy.md` Class C2 policy)
- **Date**: 2026-11-04 (UTC)
- **Scope & Context**:
  - `MyTradingSys/research/wt_bible_studies_2026-11-04/SPEC.md`
  - `MyTradingSys/backtest/splits.py` [SOURCED: splits.py:1-110]
  - `MyTradingSys/backtest/layers/wavetrend/wavetrend.py` [SOURCED: wavetrend.py:1-109]
- **Focus**: Defects only, classified under E1-E7 per `MyTradingSys/system/roles/lab_guy.md:20-27`, severity, and concrete fix.
- **Rule Check**: All numbers labelled SOURCED or OURS.

---

## 1. Executive Summary & Core Mandate Assessment

The frozen design in `SPEC.md` attempts to specify three WaveTrend studies derived from operator instructions:
1. `wt30-lower-high-divergence-short` (Card 1: 30m lower-high divergence short)
2. `wt-mtf-cycle-nesting` (Card 2: 5m/15m cycle nesting into 30m phase and 4h slope)
3. `wt-cycle-clock` (Card 3: descriptive cycle frequency and duration distribution)

While the specification establishes rigorous global bounds (`splits.py:4-6` DEV/VALIDATION/HOLDOUT windows) and acknowledges that earlier scratch runs peeked into VALIDATION and HOLDOUT bars, the specification suffers from critical defects in statistical integrity, multiple testing bounds, algorithmic determinism, and mathematical formulation:
- **Burned Confirmation Window**: Card 1 relies on a VALIDATION read for its PASS/FAIL verdict, despite acknowledging that VALIDATION and HOLDOUT bars were already observed during exploratory tuning on BTCUSDT.
- **Unbounded Multiple Testing ($m$)**: Card 1 specifies multiple feature dimensions without concrete binning cutoffs or an explicit Cartesian vs marginal hypothesis count.
- **Non-Causal & Colloquial Rules**: Divergence peaks ("high around the earlier cross") and cycle completions ("last valid top before next bottom") are defined colloquially or require lookahead.
- **Mathematically Invalid Paired Metric**: Card 2 mandates a "paired net-bp difference" between filtered (nested) and unfiltered (baseline) trades, which have unequal event counts and identical returns on overlapping trades.

Consequently, `SPEC.md` cannot be accepted in its current form and requires remediation before builders copy sections into `PRE_REG.md`.

---

## 2. Defects Tagged by Error Class (E1–E7)

### Defect 1: [E1 Data / E7 Broken Gate] Burned VALIDATION/HOLDOUT Data Contaminates Confirmation Gate
- **Location**: `SPEC.md:4-5,14-15` [SOURCED: SPEC.md:4-5,14-15]
- **Severity**: HIGH (Blocker)
- **Evidence**:
  - `SPEC.md:5` explicitly discloses: *"the 30m lower-high divergence short (Card 1 event, incl. the operator-context subset) and the cycle-frequency counts (Card 3 numbers; per-TF cycle length) were counted on BTCUSDT 2020-01..2026-11 bars, which include VALIDATION (2024-07..2025-06) and sealed HOLDOUT (2025-07+). Consequence: for these two setups the later VALIDATION read and any HOLDOUT read are NOT clean first looks."* [SOURCED: SPEC.md:5]
  - `SPEC.md:14` quotes exploratory results on those peeked bars: *"Candidate only, so far (coordinator scratch, not pre-registered, overlapping events, read bars past DEV_END): n=1219 net -6.1 bp; his context n=975 -3.4 bp; 2020-22 +8.9 bp, 2023-26 -12.0 bp."* [SOURCED: SPEC.md:14]
  - Yet `SPEC.md:15` mandates: *"Verdict rule (OURS, as every study): a cell PASSES only if Holm-adjusted net CI > 0 on DEV and then the one VALIDATION read confirms the sign and CI; otherwise FAIL or INCONCLUSIVE"* [SOURCED: SPEC.md:15]
  - Under `splits.py:5-6`, VALIDATION (`2024-07-01 .. 2025-07-01`) is strictly read once under a frozen PRE_REG, and HOLDOUT is sealed. The coordinator scratch run broke this seal. Running a VALIDATION confirmation read on BTCUSDT after results across 2023–2026 have already been observed violates out-of-sample confirmation integrity.
- **Concrete Fix**:
  - In `SPEC.md:5,15`, formally disallow BTCUSDT 2024-07..2025-06 from serving as the clean VALIDATION confirmation.
  - Require the pre-registration to explicitly freeze an unpeeked confirmation target: either a cross-asset confirmation on ETHUSDT / SOLUSDT (if DEV coverage holds) or specify that Card 1 on BTCUSDT is restricted to an exploratory/DEV-only status without claiming out-of-sample PASS until a fresh forward-window confirmation is available.
  - Formally record the prior holdout exposure in `research/holdout_reads.csv` per `splits.py:101-110`.

---

### Defect 2: [E2 Definition / E1 Data] Non-Existent File Reference for Canonical Operator Rules
- **Location**: `SPEC.md:2` [SOURCED: SPEC.md:2]
- **Severity**: MEDIUM
- **Evidence**:
  - `SPEC.md:2` states: *"Source of the ask: operator voice 2026-11-04 ~13:50Z (verbatim in `system/layer_bible/wavetrend.md` Operator rules), relayed by the coordinator."* [SOURCED: SPEC.md:2]
  - The file `system/layer_bible/wavetrend.md` does not exist in the repository (neither on disk nor in git index; only `MyTradingSys/research/layer_bible/DESIGN.md` exists).
  - Citing a non-existent file as the canonical authority for operator rules violates traceability and provenance (`roles/lab_guy.md:21-22`).
- **Concrete Fix**:
  - Update `SPEC.md:2` to cite the actual source commit, session log, or verbatim notes where the voice prompt was transcribed, or create and commit `system/layer_bible/wavetrend.md` before approving the spec.

---

### Defect 3: [E5 Selection] Unbounded Multiple Testing Space ($m$) and Unfrozen Binning in Card 1
- **Location**: `SPEC.md:6,13-15` [SOURCED: SPEC.md:6,13-15]
- **Severity**: HIGH
- **Evidence**:
  - `SPEC.md:13` lists 5 feature dimensions for Card 1:
    1. *"size of the WT drop below 0 between the two crosses"*
    2. *"hours since the last 30m valid top dot"*
    3. *"session (08/13/21 UTC cutoffs)"*
    4. *"RSI14 lower at the second high (his d-context-retest-1104 rule)"*
    5. *"4h wt1 slope"*
  - The spec notes: *"Features (each OURS, each a cell, counted in m)"* [SOURCED: SPEC.md:13], but specifies ZERO bin edges for features 1, 2, and 5.
  - Furthermore, `SPEC.md:6` states: *"m (Holm) = DEV variants + new cells"* [SOURCED: SPEC.md:6], but does not define whether cells are evaluated as 1D marginal slices ($m = \sum K_i$) or a full factorial grid ($m = \prod K_i$).
  - With 2 distinct metrics listed in `SPEC.md:14` ("net bp after 0.14 % at 24 bars, first-touch -1 % vs +1 %"), the total hypothesis count $m$ is completely unfrozen, allowing arbitrary degrees of freedom on DEV.
- **Concrete Fix**:
  - Explicitly freeze the bin thresholds in `SPEC.md`:
    - Drop size: e.g. 2 bins (`wt1_min < -20` vs `wt1_min >= -20`).
    - Age: e.g. 2 bins (`hours < 24` vs `hours >= 24`).
    - Session: 3 bins (`ASIA 00-08`, `EU 08-13`, `US 13-21 UTC`).
    - RSI14: binary (lower vs higher).
    - 4h slope: binary (positive vs negative).
  - Explicitly declare whether $m$ is evaluated over 1D marginal cells (e.g. $m = 2 + 2 + 3 + 2 + 2 = 11$ [OURS]) or full combinations, and state the exact integer value of $m$ for the Holm-Bonferroni correction.

---

### Defect 4: [E3 Implementation / E2 Definition] Ambiguous and Colloquial Divergence Event Definition in Card 1
- **Location**: `SPEC.md:11-12` [SOURCED: SPEC.md:11-12]
- **Severity**: HIGH
- **Evidence**:
  - `SPEC.md:11` defines Card 1 Event as:
    *"an earlier down-cross within 48 h with wt1 >= 45 and at least 10 higher; wt1 went below 0 in between; the price high since that dip exceeds the high around the earlier cross."* [SOURCED: SPEC.md:11]
  - The phrase *"the high around the earlier cross"* is colloquial and ambiguous: does it mean the high of the exact bar of the cross, $\pm 1$ bar, $\pm 3$ bars, or the swing high of that entire local cycle?
  - The phrase *"the price high since that dip"* is similarly ambiguous: where does "that dip" begin and end? (Is it the first bar where `wt1 < 0`, the local minimum bar, or the entire sub-zero sequence?)
  - `SPEC.md:12` defines His-context subset: *">= 3 down-cross waves above 0 since"*. What constitutes an "above-0 down-cross wave"? (Does an intermediate cross touching 0 invalidate it? Does it require both `wt1 > 0` and `wt2 > 0`?)
- **Concrete Fix**:
  - Replace colloquial phrases with exact programmatic rules:
    - Define "high around the earlier cross" as $\max(\text{high}_{t_1 - k \dots t_1 + k})$ with a fixed parameter (e.g. $k = 1$ bar, OURS).
    - Define "since that dip" as starting at the bar index where $\text{wt1}$ reaches its minimum between the two down-crosses.
    - Define "down-cross wave above 0" as a cross event where `cross_events(wt1, wt2) == -1` and $\min(\text{wt1}_t, \text{wt2}_t) > 0$.

---

### Defect 5: [E4 Wrong Question / E3 Implementation] Mathematically Invalid "Paired Difference" in Card 2
- **Location**: `SPEC.md:19` [SOURCED: SPEC.md:19]
- **Severity**: HIGH
- **Evidence**:
  - `SPEC.md:19` specifies:
    *"Primary read = paired net-bp difference nested minus baseline per TF, day-block bootstrap CI (OURS). Fee-net."* [SOURCED: SPEC.md:19]
  - Card 2 defines arms: *"nested; unnested baseline (same TF, same dots, no gate); phase-only; slope-only; age bins..."* [SOURCED: SPEC.md:19]
  - Nested entries are a strict filtered subset of unnested baseline dots.
  - On any trade taken by nested, the entry dot, exit (12 bars), and return are identical to the baseline trade on that same dot (difference = 0 bp).
  - Meanwhile, baseline takes numerous dots that nested rejects. Because the trade counts are unequal, a trade-by-trade paired difference cannot be computed.
  - If the pairing is intended across daily return blocks ($R_{\text{nested}, d} - R_{\text{baseline}, d}$), the spec fails to define position sizing, maximum concurrent trades, capital allocation, or the return calculation for days with zero trades.
- **Concrete Fix**:
  - Clarify the mathematical formulation:
    - If comparing strategy equity curves: define daily net returns $R_{t}$ using fixed notional sizing (e.g. 1 unit per trade with compounding off) and compute paired daily return differences.
    - If comparing trade distributions: frame the metric as an two-sample difference in trade expectancies (mean net return of nested trades vs mean net return of all baseline trades) with two-sample bootstrap CI.

---

### Defect 6: [E1 Data / E3 Implementation] Card 3 Cycle Definition Relies on Non-Causal Lookahead
- **Location**: `SPEC.md:21-22` [SOURCED: SPEC.md:21-22]
- **Severity**: MEDIUM
- **Evidence**:
  - `SPEC.md:22` defines:
    *"cycle frequency and median length per TF (full cycle = valid bottom up-cross to the last valid top before the next bottom, the Bible rule, OURS)"* [SOURCED: SPEC.md:22]
  - `SPEC.md:22` further asserts: *"output tables feed the Bible Findings and the `layer_state.py` 'which cycle' line."* [SOURCED: SPEC.md:22]
  - Identifying "the last valid top before the next bottom" is non-causal: at bar close $t$, an observer cannot know whether a current valid top is the *last* valid top until the *next bottom* has arrived in the future.
  - A runtime state machine (`layer_state.py`) cannot use a non-causal definition to track the active cycle in real time.
  - Furthermore, defining a cycle as "bottom to last top" measures only the up-phase (half cycle), omitting the down-phase and truncating true cycle period.
- **Concrete Fix**:
  - Define cycle period causally from full oscillation endpoints: valid bottom to next valid bottom (trough-to-trough) or valid top to next valid top (peak-to-peak).
  - For real-time phase tracking in `layer_state.py`, define causal state transitions: state is `EXPANSION` from the first valid bottom until a confirmed valid top, then `CONTRACTION` until the next valid bottom.

---

### Defect 7: [E1 Data / E3 Implementation] Unspecified Multi-Timeframe Alignment for 4h Slope
- **Location**: `SPEC.md:13,19` [SOURCED: SPEC.md:13,19]
- **Severity**: MEDIUM
- **Evidence**:
  - In Card 1 (`SPEC.md:13`) and Card 2 (`SPEC.md:19`), "4h wt1 slope" is defined as `sign of wt1 now minus wt1 three 4h bars ago`.
  - The spec does not define how lower-TF bars (5m, 15m, 30m) synchronize with the 4h timeframe.
  - Evaluating 4h WT on the in-progress (open) 4h bar creates lookahead bias and intrabar repainting.
  - Evaluating 4h WT strictly on closed bars requires integrating `htf_index()` from `wavetrend.py:62-70` (`open + htf_ms <= t`).
- **Concrete Fix**:
  - In `SPEC.md:13,19`, mandate that HTF 4h slope must be computed strictly using closed 4h bars via `wavetrend.py:htf_index(t, 4*3600*1000, htf_open_times)`.

---

### Defect 8: [E6 Execution Realism] Omission of Slippage and Execution Latency in 5m/15m Swings
- **Location**: `SPEC.md:3,11,19` [SOURCED: SPEC.md:3,11,19]
- **Severity**: LOW
- **Evidence**:
  - `SPEC.md:3` defines: *"fee-net 0.14 % round trip (SOURCED wavetrend_c30_retest_2026-11-04/PRE_REG.md)"*.
  - `SPEC.md:11,19` assumes entry at the confirming bar close.
  - Entering at bar close on extreme-momentum 5m/15m WaveTrend reversals implies taker market execution, which experiences slippage and spread. Zero slippage buffer is budgeted.
- **Concrete Fix**:
  - Specify execution mechanics: taker execution at next bar open with a 1–2 bp slippage buffer per leg, or maker execution requiring an explicit limit queue model.

---

## 3. Final Verdict

**VERDICT: FIX-FIRST**

The specification contains 8 identified defects across E1, E2, E3, E4, E5, E6, and E7. Specifically, Defect 1 (burned VALIDATION window), Defect 3 (unbounded hypothesis count $m$), Defect 4 (colloquial divergence logic), and Defect 5 (ill-defined paired difference) must be corrected in `SPEC.md` before builders copy designs into `PRE_REG.md`.

---

## Claude spot-check

Checked against SPEC.md, backtest/splits.py and backtest/layers/wavetrend/wavetrend.py on branch `gemini-q/gemini-spec-review-wt-bible-studies-1104`. Findings 1-5 checked (the review's cap); Defects 6-8 not checked.

| # | Finding | Result | Evidence | Card |
|---|---|---|---|---|
| 1 | Burned VALIDATION/HOLDOUT feeds the Card 1 verdict (E1/E7) | CONFIRMED | SPEC.md:5 discloses BTCUSDT 2020-2026 bars already read; SPEC.md:14 quote and SPEC.md:15 verdict rule match; splits.py:5-6 window and holdout log at splits.py:101-110 exist | wt-spec-card-1-pass-verdict-uses-a-valid |
| 2 | SPEC.md:2 cites a non-existent `system/layer_bible/wavetrend.md` (E2) | CONFIRMED | file not on disk and not tracked by git | wt-spec-cites-system-layer-bible-wavetre |
| 3 | Card 1 m (Holm) and feature bins unfrozen (E5) | CONFIRMED | SPEC.md:13 lists 5 features with no bin edges for features 1, 2 and 5; SPEC.md:6 text matches | wt-spec-card-1-m-holm-unfrozen-5-feature |
| 4 | Colloquial divergence event rule (E2/E3) | CONFIRMED | SPEC.md:11 and SPEC.md:12 quotes match the phrases cited | wt-spec-card-1-divergence-event-uses-col |
| 5 | Card 2 "paired net-bp difference" undefined (E4/E3) | CONFIRMED | SPEC.md:19 quote matches; nested dots are a subset of baseline dots, so no trade-level pairing exists | wt-spec-card-2-paired-net-bp-difference- |

No finding was NOT CONFIRMED. The five cards are raw; none is fixed here.
