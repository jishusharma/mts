# PRE-REGISTRATION: Tom Probe Management and Transfer Arms (card tom-probe-prereg)

Frozen: 2026-10-18. Base: origin/fast-track.
Specification of record for the surviving probe arms following diagnostics (DIAG_BTC.md), chart recall (RECALL_DAX.md), DAX untuned backtest (DAX_BT_REPORT.md), failure taxonomy (BACKTEST_FAILURES_RESEARCH.md), and layer v2 specifications (TOM_LAYER_V2_SPEC.md, TOM_ON_BTC.md).

Every parameter and metric is labelled **SOURCED** (quote + file:line) or **OURS** (judgement, convention, or arithmetic derivation) per repo strict policy.

---

## 1. Survival Status of the Five Diagnostic Axes

From `PROBE_PLAN.md` hypotheses H1–H5 and the empirical results:

| Axis | Diagnostic Result | Evidence | Status in this Pre-Reg |
|---|---|---|---|
| **S (session)** | **SKIP** | DIAG_BTC.md:17-18: 8 windows tested with Bonferroni CI; 0 windows beat other trades (best US_open 0-2h diff +0.22 R [-0.41, +1.01] SOURCED: DIAG_BTC.md:25). | **PARKED** until v2 encoding exists (ROADMAP.md:22-23 SOURCED). |
| **Q (selection)** | **SKIP** | DIAG_BTC.md:18-19: first-in-session (-0.04 R) and first-in-day (+0.16 R) neither excluded 0 (SOURCED: DIAG_BTC.md:26). Proof 4 had only n=58 (-0.57 R, worse, underpowered). Market state and HTF bias missing from snapshot rows (N6 SOURCED: BACKTEST_FAILURES_RESEARCH.md:104-105). | **PARKED** until v2 snapshot features exist (ROADMAP.md:22-23 SOURCED). |
| **M (management)** | **GO** | DIAG_BTC.md:19: 40.0 % reach >= 1R and 27.4 % reach >= 2R before touching stop (rule: GO iff >=25% and >=10% SOURCED: DIAG_BTC.md:19). 27.6 % of stopped trades were >= 1R in profit first (SOURCED: DIAG_BTC.md:24). | **GO (SURVIVED)**. Re-measured under stop-width transfer rule (N5). |
| **F (stop/fee)** | **PREREQUISITE** | DIAG_BTC.md:24,33: median stop 0.084 % of price sits inside BTC noise (median 4h MAE 5.66 R = 0.47 % of price SOURCED: TOM_LAYER_V2_SPEC.md:288); fees cost ~2.8 R per loss (SOURCED: DIAG_BTC.md:24). | **ENFORCED** via stop-width transfer rule W_min (TOM_LAYER_V2_SPEC.md Section 11). |
| **Recall / Encoding** | **REVISION** | RECALL_DAX.md:3-4: 0 / 7 signal recall on Tom's own DAX trades (SOURCED: RECALL_DAX.md:3-4). DAX backtest at shift 0 had 0 trades due to proof ceiling of 2 on CFD data (SOURCED: DAX_BT_REPORT.md:93-97). | **GOVERNED** by SpikeFadeDetector (v2 encoding) and clean holdout partitions. |

Axis conclusions:
- **M (management): GO** (observed MFE >= 1R before stop 40.0%, >= 2R in 27.4% SOURCED: DIAG_BTC.md:19)
- **S (session): SKIP** (0 of 8 windows passed Bonferroni CI SOURCED: DIAG_BTC.md:17-18)
- **Q (selection): SKIP** (2 of 2 comparisons did not exclude 0 SOURCED: DIAG_BTC.md:18-19)

---

## 2. Stop-Width Transfer Rule (The F Arms)

In `DIAG_BTC.md`, management GO was measured on 0.084 % median stops (SOURCED: DIAG_BTC.md:33). On BTC perps, 0.084 % is minute-scale noise, so fees (~2.8 R per loss) overwhelm execution. Per **N5** (BACKTEST_FAILURES_RESEARCH.md:100-103 SOURCED), management arms must only be evaluated on trades passing the stop-width transfer rule:

1. **Noise floor:**
   $$W_{\text{noise}} = 0.88 \times N_5(\text{market})$$
   - $0.88$ is Tom's 20-point fixed stop on DAX (`k0zm5NYn0IQ:22-24` SOURCED: RECALL_DAX.md:23) divided by DAX median 5-minute true range $N_5 = 0.0897\ \%$ (OURS: TOM_LAYER_V2_SPEC.md:307).
   - On BTC ($N_5 = 0.1395\ \%$ OURS: TOM_LAYER_V2_SPEC.md:298), $W_{\text{noise}} = 0.88 \times 0.1395\ \% = 0.1228\ \% \approx 0.123\ \%$ of price (OURS: TOM_LAYER_V2_SPEC.md:307).
   - $N_5$ window: trailing 20 UTC days on BTC, 20 trading sessions on DAX (OURS: TOM_LAYER_V2_SPEC.md:314-315).

2. **Fee floor:**
   $$W_{\text{fee}} = \frac{\text{round-turn cost}}{0.25}$$
   - Sourced from "Stops are wide enough that fees cost under 0.25 R" (`PROJECT_VISION.md:234` SOURCED).
   - Under all-taker fees (`FEES_ALL_TAKER`, 0.05 % taker entry + 0.05 % taker exit = 0.10 % round turn SOURCED: ExecutionMathConstants.java:17):
     $$W_{\text{fee}} = \frac{0.10\ \%}{0.25} = 0.40\ \%\text{ of price (OURS: TOM_LAYER_V2_SPEC.md:323)}$$
   - Under Deribit maker fees (`FEES_DERIBIT`, 0.00 % maker entry, 0.00 % maker target, 0.05 % taker stop SOURCED: fees.py:25-35):
     $$W_{\text{fee}} = \frac{0.05\ \%}{0.25} = 0.20\ \%\text{ of price (OURS: TOM_LAYER_V2_SPEC.md:324)}$$

3. **Minimum stop width ($W_{\text{min}}$):**
   $$W_{\text{min}} = \max(W_{\text{noise}}, W_{\text{fee}})$$
   - **BTC All-Taker (`F_taker`):** W_min = max(0.123 %, 0.40 %) = 0.40 % of price (OURS: TOM_LAYER_V2_SPEC.md:323).
   - **BTC Deribit (`F_deribit`):** W_min = max(0.123 %, 0.20 %) = 0.20 % of price (trade-through fills required; OURS: TOM_LAYER_V2_SPEC.md:324).
   - **DAX (`F_dax`):** $W_{\text{min}} = 20\text{ points}$ (reported, not enforced: round-turn cost is ~0.1 point vs 25 EUR/pt, fee floor is 0.004 % SOURCED: TOM_LAYER_V2_SPEC.md:321,325).
   - Structural stops narrower than $W_{\text{min}}$ are **NOT traded** (logged `stop_below_min_width`). Stops are NEVER artificially widened (widening places stops where the trader never looked; SOURCED: TOM_LAYER_V2_SPEC.md:263-264).

---

## 3. The Pre-Registered Arms and Source Status

All arms are experimental conditions compared against baseline M0. Each arm has an explicit provenance tag:

| Arm ID | Name | Specification | Source Status |
|---|---|---|---|
| **M0** | **Fixed Bracket (Baseline)** | Stop at swing high/low; target at setup target; 8-bar timeout; 1 trade at a time; stop-first on ambiguous bars. | Stop/target: SOURCED (`tom_bt.py:11-19`). 8-bar timeout: **NO-SOURCE / OURS** (`PROBE_PLAN.md:15,54`). |
| **M1** | **Trailing Stop to 5m Volume Level** | Stop is trailed behind the most recent 5-minute volume level (POC/HVN) in trade direction, evaluated on completed 5-minute bar closes. | Trailing concept: **SOURCED** (`conditions/risk_protocol.md:634-635`, video `4MoNjEQ2Dd8:145-150`). Cadence (5m close): **NO-SOURCE / OURS**. |
| **M2** | **Partial Profit Take on Rotation/Stall** | Take 50 % position off at +1.0 R or when price stalls before untraded volume / VWAP; move stop on remaining 50 % to break-even (no-loss); let runner ride to target. | Partial & no-loss: **SOURCED** (`conditions/risk_protocol.md:5.4`, `TOM_ON_BTC.md:82-83`, video `n7ZSkjb7JXs:63-65`, `ujedEcmvBMk:120-125`). Size 50 % and +1 R trigger: **NO-SOURCE / OURS**. |
| **M3** | **One Re-entry After Stop** | If stopped at a valid zone and price immediately re-tests the zone with fresh confirmation within the same session, re-enter once with original risk. | Re-entry concept: **SOURCED** (`ANGLE_TRADE_CATALOG.md` rows 9-10, 14-15, 19; `RECALL_DAX.md:17` T3->T3b, video `ujedEcmvBMk:338-345`). Cap at 1 re-entry per session: **SOURCED** (`TOM_LAYER_V2_SPEC.md` section 2.4). |
| **M4** | **No Timeout (Session Exit)** | Remove the artificial 8-bar timeout. Trade runs until target, stop, or session close (DAX: 17:35 CET / 15:35 UTC; BTC: resolved or end of 24h trading day). | Absence of bar timeout: **SOURCED** (`TOM_ON_BTC.md:85`, `TOM_LAYER_V2_SPEC.md:A-M2`, `RECALL_DAX.md:20`). Session exit: SOURCED (`TOM_LAYER_V2_SPEC.md:A-M2`). |
| **M_all** | **Full Trader Management** | Composite combining M1 (trail) + M2 (partial at 1R) + M3 (1 re-entry) + M4 (no timeout). | Composite of Tom's trade management: **SOURCED** (`TOM_ON_BTC.md:81-86`, `ANGLE_TRADE_CATALOG.md:16`). |
| **F_taker** | **All-Taker Fee Model** | Round-turn fee 0.10 %; $W_{\text{min}} = 0.40\ \%$ stop width floor enforced on BTC. | Fee schedule: **SOURCED** (`ExecutionMathConstants.java:17`). Floor derivation: **OURS** (`TOM_LAYER_V2_SPEC.md:323`). |
| **F_deribit** | **Deribit Maker Model** | Maker in (0.00 %), maker target (0.00 %), taker stop (0.05 %); $W_{\text{min}} = 0.20\ \%$ stop width floor on BTC. Trade-through fills required. | Fee schedule: **SOURCED** (`fees.py:25-35`). Trade-through requirement: **SOURCED** (`BACKTEST_FAILURES_RESEARCH.md:40` C5, `TOM_LAYER_V2_SPEC.md:331`). |

---

## 4. Market Order & Execution Strategy

Per `PROBE_PLAN.md` Section 4:
1. **DAX (Home Market):** Evaluated first on dev data. Acts as the clean benchmark to test whether M1–M4 rescue performance on the asset Tom trades without crypto fee drag or noise distortion.
2. **BTC (Transfer Target):** Evaluated under the stop-width transfer rule ($W_{\text{min}} \ge 0.40\ \%$ for all-taker, $\ge 0.20\ \%$ for Deribit).
3. **Nasdaq Futures:** Parked until DAX or BTC shows edge.

---

## 5. Holdouts and Clean Partitions

Strict partition rules to prevent data snooping:

### BTC Partitions
- **Hist Period:** 2022-01-20 .. 2025-08-31 (SOURCED: DIAG_BTC.md:8).
- **Dev Period:** 2025-09-01 .. 2026-06-25 (SOURCED: DIAG_BTC.md:8). All tuning, selection, and M-arm trials run exclusively on Dev.
- **Burned Holdout:** 2026-06-26 .. 2026-09-26 (burned twice in prior research, B147 SOURCED; permanently excluded from all evaluation).
- **Clean Forward Holdout:** 2026-09-27 onward (OURS: PROBE_PLAN.md:74-75). Untouched. Read **ONCE** only when it holds $\ge 100$ trades of a frozen arm passing dev.

### DAX Partitions
- **Archive Range:** 2024-11-04 .. 2026-10-09 (SOURCED: PRE_REG_DAX.md:11).
- **Dev Period:** 2024-11-04 .. 2026-04-10, excluding the 10 candidate ledger days $\pm 1$ trading day per `HOLDOUT_CLEAN.json` (SOURCED: PRE_REG_DAX.md:45).
- **Clean Holdout:** 2026-04-11 .. 2026-10-09 (130 clean archive days after dropping the 26 candidate ledger days $\pm 1$ trading day listed in `HOLDOUT_CLEAN.json` SOURCED: PRE_REG_DAX.md:42).
- **Forward Holdout:** 2026-10-10 onward (SOURCED: PRE_REG_DAX.md:43). Read **ONCE** only at $\ge 100$ filled trades.

---

## 6. Honest Trial Accounting, DSR and PBO

### Planned Trials
This pre-registration authorizes:
$$\text{Planned Trials} = 6\text{ management configurations } (M0, M1, M2, M3, M4, M_{\text{all}}) \times 2\text{ markets } (\text{DAX}, \text{BTC}) \times 2\text{ fee profiles } (F_{\text{taker}}, F_{\text{deribit}}) = \mathbf{24\text{ trials}}$$

### Cumulative Lineage Trials
To prevent backtest overfitting, every prior attempt in the Tom probe lineage is counted in the Deflated Sharpe Ratio (DSR) and Probability of Backtest Overfitting (PBO):
- BTC rerun (2026-10-06): 4 trials (SOURCED: TOM_CORE_BT_RERUN_2026-10-06_full.md)
- DIAG_BTC (2026-10-11): 11 trials (8 session + 2 selection + 1 MFE SOURCED: DIAG_BTC.md:17-19)
- DAX recall: 2 trials (declared + sensitivity SOURCED: RECALL_DAX.md:26-39)
- DAX smoke backtest: 78 trials (SOURCED: `bt_runs/TRIAL_REGISTRY_SMOKE.csv`)
- Recall V2: 2 trials (literal + adjusted SOURCED: RECALL_DAX_V2.md)
- **Cumulative Prior Trials:** $4 + 11 + 2 + 78 + 2 = \mathbf{97\text{ trials}}$ (OURS).
- **Total Lineage Trials including this pre-reg:** $97 + 24 = \mathbf{121\text{ trials}}$ (OURS).

### Deflated Sharpe Ratio Threshold
Per Bailey & López de Prado (2014) and `FORMULAS.md` Section 15 (SOURCED):
$$E[\max_N \text{SR}] \approx (1 - \gamma) \Phi^{-1}\left(1 - \frac{1}{N}\right) + \gamma \Phi^{-1}\left(1 - \frac{1}{N \cdot e}\right)$$
where $\gamma \approx 0.5772$ (Euler-Mascheroni constant).
- For $N = 24$ (isolated pre-reg family): $E[\max \text{SR}] \approx 2.14 / \sqrt{\text{years}}$ (OURS).
- For $N = 121$ (cumulative lineage): $E[\max \text{SR}] \approx 2.76 / \sqrt{\text{years}}$ (OURS).
- **Pass Gate:** Any claimed edge must demonstrate a DSR $> 0.95$ computed against $N = 121$.

---

## 7. Methodological and Statistical Controls

1. **N5 Stop-Width Rule:** MFE/MAE re-measurement occurs strictly on candidate sets that satisfy $W_{\text{min}}$ ($\ge 0.40\ \%$ on BTC all-taker, $\ge 0.20\ \%$ on BTC Deribit).
2. **N7 Session-Matched Null:** The session-matched null distribution draws entry timestamps exclusively from within the same session window (e.g. 08:00–12:00 UTC for European/DAX open), using like-for-like limit order simulation (SOURCED: BACKTEST_FAILURES_RESEARCH.md:106-108).
3. **N8 Discretionary Frequency:** No maximum trade cap per day is imposed unless an explicit quote is sourced.
4. **Fill Model:** Both touch fills and trade-through fills are reported. For maker legs, only trade-through fills qualify for the official pass bar (touch fills are optimistic; SOURCED: BACKTEST_FAILURES_RESEARCH.md:40 C5).
5. **Stratification (B154):** All results must report pooled statistics alongside breakdowns by:
   - Session: Asia (00:00–08:00 UTC), DAX/London (08:00–13:30 UTC), US Open (13:30–18:00 UTC), US Close/Later (18:00–24:00 UTC).
   - Market Regime: Balance/Range, Trend Healthy, Trend Creeping, Transition.
6. **Power Rule:** Any stratum or period with $n < 100$ filled trades is labelled **"underpowered"**, NEVER "no edge" (SOURCED: BACKTEST_FAILURES_RESEARCH.md:124).
7. **Pass Bar:** Net R $95\ \%$ bootstrap confidence interval lower bound $> 0.0$ and $n \ge 100$ filled trades.

---

## 8. Control Room Decisions for NO-SOURCE Arms

The following operational choices are recorded for operator review:
1. **M1 Cadence:** Updated per 5-minute bar close (chosen to match Tom's primary 5m chart; NO-SOURCE / OURS).
2. **M2 Sizing:** 50 % partial take at +1.0 R with break-even stop on remainder (NO-SOURCE / OURS).
3. **W_min Window:** 20-day trailing $N_5$ lookback (NO-SOURCE / OURS).
