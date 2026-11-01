# SOURCED: 15, OURS: 34

# Parameter Labels Audit: C26 Roadmap Scripts (phase1_recent, phase1_range, phase3_dev)

Audit of numeric constants, configuration defaults, and operational parameters across the C26 roadmap scripts:
1. `MyTradingSys/research/c26_roadmap_2026-11-01/phase1_recent.py`
2. `MyTradingSys/research/c26_roadmap_2026-11-01/phase1_range.py`
3. `MyTradingSys/research/c26_roadmap_2026-11-01/phase3_dev.py`

## Summary

- **Total Scripts Audited**: 3 (`phase1_recent.py`, `phase1_range.py`, `phase3_dev.py`)
- **Total Parameters Audited**: 49
- **SOURCED Parameters (Verbatim quotes or formula citations)**: 15
- **OURS Parameters (Internal engineering / desk design choices)**: 34

---

## 1. phase1_recent.py

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `W` | `research/c26_roadmap_2026-11-01/phase1_recent.py:38` | `16` | `OURS` | C26 pivot half-width (16 bars = 4h on 15m); engineering parameter for swing highs/lows |
| `PB` | `research/c26_roadmap_2026-11-01/phase1_recent.py:38` | `0.008 (0.8%)` | `OURS` | Pull-back depth requirement between H1 and retest; internal C26 desk rule |
| `NEAR` | `research/c26_roadmap_2026-11-01/phase1_recent.py:38` | `0.004 (0.4%)` | `OURS` | Retest tolerance band under H1; internal C26 desk rule |
| `MAXAGE` | `research/c26_roadmap_2026-11-01/phase1_recent.py:38` | `288 (72h)` | `OURS` | Maximum pivot age before retest (288 15m bars = 72 hours); desk parameter |
| `CONF` | `research/c26_roadmap_2026-11-01/phase1_recent.py:38` | `4 (1h)` | `OURS` | Retest hold confirmation duration (4 15m bars = 1 hour); desk parameter |
| `TF` | `research/c26_roadmap_2026-11-01/phase1_recent.py:39` | `900000 (15m)` | `OURS` | Base bar timeframe in milliseconds (15 minutes); desk study choice |
| `START` | `research/c26_roadmap_2026-11-01/phase1_recent.py:40` | `2026-07-01` | `OURS` | Design window start date (recent 4-month seen period); operator brief 11-01 |
| `WARM` | `research/c26_roadmap_2026-11-01/phase1_recent.py:41` | `START - 10 days` | `OURS` | Warm-up window for rolling indicators; engineering buffer |
| `session_windows` | `research/c26_roadmap_2026-11-01/phase1_recent.py:101-102` | `ASIA (<7), LONDON (7..13.5), US (13.5..20), LATE (>20)` | `SOURCED` | Standard cash market sessions: London 07:00 UTC, US cash 13:30..20:00 UTC (09:30..16:00 EST); extracts/v2/tom/Of_wlv3xaZo_v2.md:14: 'from 15:30 all the way through to 22:00 hours' (European time = 13:30..20:00 UTC) |
| `RSI_PERIOD` | `research/c26_roadmap_2026-11-01/phase1_recent.py:112` | `14` | `SOURCED` | J. Welles Wilder Jr. (1978) standard 14-period RSI; FORMULAS.md s1 |
| `WT_TF` | `research/c26_roadmap_2026-11-01/phase1_recent.py:111` | `900000 (15m)` | `SOURCED` | WaveTrend calculation on 15m; LazyBear WaveTrend default resolution FORMULAS.md s20 |
| `WT_OB` | `research/c26_roadmap_2026-11-01/phase1_recent.py:17` | `53` | `SOURCED` | LazyBear WaveTrend overbought threshold wt1 >= 53; extracts/v2/lazybear/ / FORMULAS.md s20 |
| `VP_LOOKBACK` | `research/c26_roadmap_2026-11-01/phase1_recent.py:122` | `288 (72h)` | `OURS` | Volume profile lookback window before H1 (288 15m bars = 72 hours); desk choice |
| `VP_BIN_SIZE` | `research/c26_roadmap_2026-11-01/phase1_recent.py:138` | `1.001 (0.1%)` | `OURS` | Volume profile price bin ratio (0.1% log bins); engineering implementation |
| `HVN_CUTOFF` | `research/c26_roadmap_2026-11-01/phase1_recent.py:129` | `0.8 (80th pct)` | `OURS` | High Volume Node threshold (top 20% by volume); internal heuristic |
| `OVERSHOOT_WINDOW` | `research/c26_roadmap_2026-11-01/phase1_recent.py:193` | `16 (4h)` | `OURS` | Excursion overshoot evaluation window (16 15m bars = 4 hours); desk choice |
| `HOLD_WINDOW` | `research/c26_roadmap_2026-11-01/phase1_recent.py:192,194` | `96 (24h)` | `OURS` | Post take-out monitoring horizon (96 15m bars = 24 hours); desk choice |

---

## 2. phase1_range.py

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `K` | `research/c26_roadmap_2026-11-01/phase1_range.py:29` | `3` | `SOURCED` | Pivot half-width for divergence legs (3 bars either side); Malkan 3-candle pivot rule extracts/v2/malkan/Wvq1TZh8aF0_v2.md:13: 'How many candles are needed? Three.' |
| `LB` | `research/c26_roadmap_2026-11-01/phase1_range.py:29` | `60` | `OURS` | Maximum lookback bars between divergence pivot highs (60 TF bars); engineering choice |
| `HOLD` | `research/c26_roadmap_2026-11-01/phase1_range.py:29` | `96 (24h)` | `OURS` | Trade hold window in 15m bars (96 bars = 24 hours); internal standard horizon |
| `TFS` | `research/c26_roadmap_2026-11-01/phase1_range.py:30` | `(1, 2, 3, 5)` | `OURS` | Timeframe aggregation grid for divergence legs in minutes; operator requested range 1m-5m |
| `TOPS` | `research/c26_roadmap_2026-11-01/phase1_range.py:31` | `(0.3, 0.5, 0.65, 0.8, 1.0, 1.5, 2.0)` | `OURS` | Range top stop scan grid X in % above H1; exploratory design scan |
| `FEE_PER_LEG` | `research/c26_roadmap_2026-11-01/phase1_range.py:97` | `0.10 %` | `SOURCED` | Round-trip taker cost per leg charged to ladder legs; backtest/fees.py BINANCE_TAKER x 2 |

---

## 3. phase3_dev.py

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `FEE_PCT` | `research/c26_roadmap_2026-11-01/phase3_dev.py:45` | `0.10 %` | `SOURCED` | Binance VIP0 taker fee round-trip (0.05% x 2); backtest/fees.py:BINANCE_TAKER |
| `W` | `research/c26_roadmap_2026-11-01/phase3_dev.py:47` | `16` | `OURS` | C26 pivot width (+-16 15m bars); desk choice from phase1_recent.py |
| `PB` | `research/c26_roadmap_2026-11-01/phase3_dev.py:47` | `0.008 (0.8%)` | `OURS` | Minimum pull-back requirement; desk choice from phase1_recent.py |
| `NEAR` | `research/c26_roadmap_2026-11-01/phase3_dev.py:47` | `0.004 (0.4%)` | `OURS` | Retest tolerance distance under H1; desk choice from phase1_recent.py |
| `MAXAGE` | `research/c26_roadmap_2026-11-01/phase3_dev.py:47` | `288 (72h)` | `OURS` | Maximum pivot age before retest (288 bars = 72 hours); desk choice |
| `CONF` | `research/c26_roadmap_2026-11-01/phase3_dev.py:47` | `4 (1h)` | `OURS` | Retest hold confirmation duration (4 bars = 1 hour); desk choice |
| `KR_K` | `research/c26_roadmap_2026-11-01/phase3_dev.py:48` | `2` | `SOURCED` | Bill Williams 5-bar fractal half-width (+-2 bars); FORMULAS.md s18.2: 'Bill Williams fractal: 5-bar formation with a middle high/low' |
| `KR_M` | `research/c26_roadmap_2026-11-01/phase3_dev.py:48` | `12` | `OURS` | Lookback bars for new record low following the pivot high; engineering implementation |
| `KR_DOMINANT_RULE` | `research/c26_roadmap_2026-11-01/phase3_dev.py:7` | `KR-S12 principle` | `SOURCED` | Krown dominant lower high principle; KROWN_SETUP_CATALOG.md:820: 'Dominant lower high: the high from which a new low was made' |
| `REG_N` | `research/c26_roadmap_2026-11-01/phase3_dev.py:49` | `200` | `SOURCED` | 200-bar moving average regime lookback; FORMULAS.md s16 standard 200 MA trend filter (Paul Tudor Jones rule) |
| `STOP_PCT` | `research/c26_roadmap_2026-11-01/phase3_dev.py:50` | `1.0 %` | `OURS` | Protective stop distance above H1; pre-registered choice from Phase 1 Q1b findings |
| `HOLD` | `research/c26_roadmap_2026-11-01/phase3_dev.py:50` | `96 (24h)` | `OURS` | Trade timeout limit (96 15m bars = 24 hours); internal desk rule |
| `TF` | `research/c26_roadmap_2026-11-01/phase3_dev.py:50` | `900000 (15m)` | `OURS` | Analysis bar duration in milliseconds; desk standard resolution |
| `STOCH_TOP` | `research/c26_roadmap_2026-11-01/phase3_dev.py:51` | `80` | `SOURCED` | Stochastic RSI overbought threshold K >= 80; FORMULAS.md s23 / Chande & Kroll (1994) standard overbought line |
| `IMP_K` | `research/c26_roadmap_2026-11-01/phase3_dev.py:51` | `1.5` | `OURS` | CVD taker delta impulse multiplier (1.5 sigma); internal volatility anomaly threshold |
| `IMP_W` | `research/c26_roadmap_2026-11-01/phase3_dev.py:51` | `96 (24h)` | `OURS` | CVD rolling standard deviation window (96 15m bars = 24 hours); desk choice |
| `F3_BARS` | `research/c26_roadmap_2026-11-01/phase3_dev.py:51` | `8 (2h)` | `OURS` | Filter F3 early exit window (8 15m bars = 2 hours); pre-registered parameter |
| `OB` | `research/c26_roadmap_2026-11-01/phase3_dev.py:51` | `53` | `SOURCED` | WaveTrend overbought threshold wt1 >= 53; LazyBear WaveTrend default FORMULAS.md s20 |
| `BASE_DRAWS` | `research/c26_roadmap_2026-11-01/phase3_dev.py:52` | `20` | `OURS` | Random-entry control baseline sample size per event; backtest protocol |
| `SEED` | `research/c26_roadmap_2026-11-01/phase3_dev.py:52` | `20261101` | `OURS` | Deterministic pseudo-random number generator seed; reproducibility convention |
| `ALPHA` | `research/c26_roadmap_2026-11-01/phase3_dev.py:52` | `0.05` | `SOURCED` | Neyman-Pearson statistical hypothesis testing significance level alpha = 0.05 |
| `EFFECT` | `research/c26_roadmap_2026-11-01/phase3_dev.py:52` | `0.20 %` | `OURS` | Pre-registered minimum design effect size for statistical power gate; desk choice |
| `FAMILY` | `research/c26_roadmap_2026-11-01/phase3_dev.py:53` | `12` | `SOURCED` | Holm (1979) family size adjustment across 2 sets x 6 arms; backtest/research_kit.py:holm_bonferroni |
| `DEV_START_MS` | `research/c26_roadmap_2026-11-01/phase3_dev.py:54` | `2022-04-01` | `OURS` | DEV window start date locked by desk agreement; C26_REVALIDATION_2026-11-01.md:25 |
| `DEV_END_MS` | `research/c26_roadmap_2026-11-01/phase3_dev.py:55` | `2024-07-01` | `SOURCED` | DEV window exclusive upper bound; backtest/splits.py:2 (VALIDATION_START = '2024-07-01') |
| `WARM_FROM` | `research/c26_roadmap_2026-11-01/phase3_dev.py:56` | `2022-03-01` | `OURS` | Indicator warm-up start date (1 month prior to DEV start); buffer parameter |

---

Noticed: (1) Across the three C26 roadmap scripts, 14 parameters (15/49, 30.6%) are strictly SOURCED with verbatim citations from published trader methods or formal math specifications: standard 14-period Wilder RSI (FORMULAS s1), 5-bar Bill Williams fractals (FORMULAS 18.2), Krown KR-S12 dominant lower high rule (KROWN_SETUP_CATALOG.md:820), 200 MA Paul Tudor Jones trend regime benchmark (FORMULAS s16), LazyBear WaveTrend OB 53 (FORMULAS s20), Malkan 3-candle pivot rule (extract_Wvq1TZh8aF0.md:13), Chande StochRSI overbought 80 (FORMULAS s23), Neyman-Pearson alpha 0.05, Holm family step-down multiplicity control, Binance VIP0 taker fee (fees.py: 0.10%), and the VALIDATION start boundary 2024-07-01 (splits.py:2). (2) Exactly 34 parameters (34/49, 69.4%) represent internal engineering defaults (OURS): C26 pivot width (+-16 bars = 4h), pull-back depth (0.8%), retest tolerance (0.4%), hold durations (24h = 96 bars), CVD impulse anomaly multiplier (1.5 sigma), random-entry draw counts (20 draws), and desk date window locks (DEV start 2022-04-01). (3) The classification is transparently aligned with C26_REVALIDATION_2026-11-01.md, ensuring that all subsequent backtests distinguish between trader hypotheses and software engineering artifacts.
