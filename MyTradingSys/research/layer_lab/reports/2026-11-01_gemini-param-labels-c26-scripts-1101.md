# Layer Lab Report: Parameter Labels for C26 Roadmap Scripts (phase1_recent, phase1_range, phase3_dev)

- **Task**: `gemini-param-labels-c26-scripts-1101`
- **Lane**: `CODEX`
- **Audited Scripts**:
  - `MyTradingSys/research/c26_roadmap_2026-11-01/phase1_recent.py`
  - `MyTradingSys/research/c26_roadmap_2026-11-01/phase1_range.py`
  - `MyTradingSys/research/c26_roadmap_2026-11-01/phase3_dev.py`
- **Audited Deliverables**:
  - `MyTradingSys/research/gemini_audits_2026-11-01/c26_scripts_param_labels.md`
  - `research/gemini_audits_2026-11-01/c26_scripts_param_labels.md`
- **Date**: 2026-11-01
- **Auditor**: Gemini 3.8 Flash (medium) worker (Antigravity JIS-NUC)

---

## 1. Executive Summary

This report establishes the parameter provenance audit for the C26 Roadmap code suite (`phase1_recent.py`, `phase1_range.py`, `phase3_dev.py`). Each tunable constant, indicator length, filter threshold, simulation geometry, and date window was evaluated against published trader literature, verbatim transcripts, and formal mathematical specifications to distinguish `SOURCED` parameters from engineering defaults (`OURS`).

- **Total Parameters Audited**: 49
- **Classification Counts**:
  - `SOURCED`: 15 (30.6%)
  - `OURS`: 34 (69.4%)
- **Verification Integrity**: 100% of parameter entries cite exact script file and line numbers, default values, and source quotes.

---

## 2. Key Parameter Categories

### 1. Mathematical and Trader Sourced Parameters (`SOURCED`: 15)
- **Technical Indicators**:
  - `RSI_PERIOD = 14`: J. Welles Wilder Jr. (1978) standard relative strength index (`FORMULAS.md` s1).
  - `WT_OB = 53`: LazyBear WaveTrend overbought threshold (`FORMULAS.md` s20).
  - `KR_K = 2`: Bill Williams 5-bar fractal half-width (`FORMULAS.md` s18.2).
  - `STOCH_TOP = 80`: Chande & Kroll Stochastic RSI standard overbought line (`FORMULAS.md` s23).
  - `REG_N = 200`: Standard 200-period trend regime filter benchmark (Paul Tudor Jones rule, `FORMULAS.md` s16).
  - `K = 3`: Malkan 3-candle pivot half-width (`extract_Wvq1TZh8aF0.md:13`).
- **Core Market Rules & Structural Definitions**:
  - `session_windows`: European and US cash market hours (Tom extract `Of_wlv3xaZo_v2.md:14`: "from 15:30 all the way through to 22:00 hours").
  - `KR_DOMINANT_RULE`: Krown dominant lower high definition (`KROWN_SETUP_CATALOG.md:820`: "Dominant lower high: the high from which a new low was made").
- **Costs & Statistical Harness**:
  - `FEE_PCT = 0.10 %`: Round-trip taker fee (`backtest/fees.py:BINANCE_TAKER` $0.05\% \times 2$).
  - `ALPHA = 0.05`: Standard statistical significance level.
  - `FAMILY = 12`: Holm (1979) step-down multiplicity adjustment.
  - `DEV_END_MS = 2024-07-01`: Sealed split boundary (`backtest/splits.py:2`).

### 2. Engineering and Protocol Parameters (`OURS`: 34)
- **C26 Geometry**: Pivot half-width $W=16$ bars (4h), pull-back depth $PB=0.8\%$, retest tolerance $NEAR=0.4\%$, hold confirmation $CONF=4$ bars (1h), and max age $MAXAGE=288$ bars (72h).
- **Study Horizons**: Evaluation hold periods ($HOLD=96$ bars = 24h), excursion lookahead caps ($16$ bars = 4h).
- **Execution & Filter Grids**: CVD impulse threshold ($1.5\sigma$), rolling volume profile log-bin ratios ($1.001$), HVN top $20\%$ cutoff, and protective stop distances ($1.0\%$ above H1).
- **Data Splitting**: DEV window start date locked to `2022-04-01` per desk agreement (`C26_REVALIDATION_2026-11-01.md:25`).

---

## 3. Epistemic Impact

Separating `SOURCED` trader rules from `OURS` engineering parameters prevents confirmation bias and curve-fitting:
1. When an edge fails in DEV (e.g. C26 arms netting $-0.216\%$ and Krown netting $-0.117\%$), the audit reveals whether the failure falsifies the trader hypothesis (Krown KR-S12) or the specific parameterization ($W=16$, $PB=0.8\%$).
2. All parameters are transparently mapped to the revalidation roadmap (`C26_REVALIDATION_2026-11-01.md`).
