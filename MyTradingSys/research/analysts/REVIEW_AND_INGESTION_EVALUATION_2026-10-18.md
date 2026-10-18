# Imbalance Analysts Survey Review & Ingestion Strategy Evaluation
**Date**: 2026-10-18  
**Author**: Gemini Flash Worker (Session `review-imbalance-analysts-report-and-imp`)  
**Scope Ref**: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md`  
**Related Items**: `MyTradingSys/items/B162_qriptal_signal_layer.md`, `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md`  
**Status**: REVIEW COMPLETE & INGESTION ARCHITECTURE SPECIFIED  

---

## 1. Executive Review of Survey Report

We conducted a thorough technical review of `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md` across sections 5, 6, 7, and 8.

### 1.1 Alignment with MTS Baseline (`B162` & `imbalance_qriptal_2026-10-16`)
- **Baseline Context**: In MTS, Habib (Qriptal) was evaluated under `B162` and `imbalance_qriptal_2026-10-16/README.md`. Habib's core construct is the **Volume Anomaly Candle** (high volume spike with narrow candle body, indicating trapped aggressive traders or absorption).
- **Key Empirical Finding**: While the candle family is statistically confirmed above chance ($p = 0.003$, SOURCED: `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md:51`), a naive mechanical fade exhibits **no fee-net edge** alone (gross flat, fee drag 0.09 to 0.38 R, SOURCED: `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md:81`).
- **Strategic Implication**: External analyst signals provide the *discretionary confluence* (HTF bias, key level selection, sweep/wick confirmation) that turns raw imbalance occurrences into positive-expectancy setups. Surveying and scoring multiple independent analysts is the soundest empirical path to validate whether human imbalance experts beat retail fees.

---

## 2. Evaluation of the 4 Candidate Ingestion Routes

The survey outlines four distinct technical ingestion routes (Section 8.1). We evaluated each route against automation friction, data reliability, immutability, and maintenance overhead:

| Ingestion Route | Data Source & Mechanism | Immutability / Verification | Parsing Determinism | Latency & Feasibility | Recommendation |
|---|---|---|---|---|---|
| **Route 1: TradingView Play-Button Ideas** (e.g. RLinda) | Web scraping / RSS feed of TradingView author profile (`tradingview.com/u/<author>/`) | **Maximum**: Once published, ideas cannot be edited or deleted. Built-in "Play" button verifies future price bars. | **Very High**: Authors use standardized templates (`Entry`, `Stop Loss`, `Target 1-3`). | Low overhead; daily/swing frequency (1-5 calls/week). Feasibility: **10/10** (OURS). | **Top Priority (Phase 1)** |
| **Route 2: DailyPriceAction Formatted Web/RSS** (e.g. Justin Bennett) | Daily HTML/RSS feed scraper of `dailypriceaction.com/market-analysis/` | **High**: Timestamped blog entries with public archive dating back to 2014. | **Exceptional**: Structured text headings (`Market:`, `Entry:`, `Stop Loss:`, `Take Profit 1-2:`). | Low overhead; 1 daily update. Feasibility: **10/10** (OURS). | **Top Priority (Phase 1)** |
| **Route 3: YouTube Livestream Audio / Whisper** (e.g. Trader XO, Qriptal) | Video download (`yt-dlp`) + Whisper STT transcription + NLP price extractor | **Medium**: Unedited public video archives, but calls are spoken colloquially without strict syntax. | **Medium-Low**: Requires regex/LLM extraction to identify spoken price levels; high risk of ambiguous coordinates. | High compute overhead; weekly frequency; existing D21 DSA pipeline exists (`fetch-qriptal-habib-youtube-cap`). Feasibility: **6/10** (OURS). | **Secondary (Maintain via D21)** |
| **Route 4: Twitter / X Text Stream** (e.g. Crypto Chase, Roman Trading, TraderSZ) | X API / Nitter scraper / feed listener filtering tweets with price keywords | **Medium**: Timestamped, but tweets can be deleted or quoted inconsistently across threads. | **Medium**: Requires pattern matching across varied slang ("tapped", "looking for", "sl under wick"). | High platform friction (API paywalls / rate limits). Feasibility: **7/10** (OURS). | **Secondary (Phase 2)** |

### Conclusion on Routes:
1. **Route 1 (TradingView)** and **Route 2 (DailyPriceAction)** provide deterministic, noise-free, and machine-friendly trade setups with near-zero ongoing parsing maintenance.
2. **Route 3 (YouTube Whisper)** is already supported by MTS infrastructure (`B162` D21) and should be maintained for weekly swing macro bias.
3. **Route 4 (Twitter/X)** should use standardized intermediate schema injection via operator inbox or headless scrapers.

---

## 3. Evaluation of Candidate Analysts

We evaluated the primary candidates identified in Sections 5 and 6 of the survey:

### 3.1 Crypto Chase (@Crypto_Chase)
- **Construct**: Fair Value Gaps (FVG) and Liquidity S/R deviations (Construct 2).
- **Feasibility**: High. Clean chart threads with explicit entry limit and invalidation levels.
- **Role in MTS**: Primary representative for ICT/FVG displacement setups.

### 3.2 Roman Trading (@Roman_Trading)
- **Construct**: Volume Absorption & CVD Divergence (Construct 1 — direct counterpart to Habib).
- **Feasibility**: High. High-frequency daily calls on BTC/ETH identifying volume anomalies at key levels.
- **Role in MTS**: Perfect benchmark to test if volume anomaly absorption can be traded profitably with manual level discretion.

### 3.3 RLinda (TradingView Top Chartist)
- **Construct**: Price Action, Liquidity Traps & False Breakouts (Construct 4).
- **Feasibility**: **Highest (10/10)**. Every publication on TradingView follows a rigid format with explicit numerical Entry, Stop Loss, and 3 Target tiers.
- **Role in MTS**: Gold standard benchmark for automated machine ingestion.

### 3.4 Justin Bennett (Daily Price Action)
- **Construct**: Unmitigated Fair Value Gaps & Breakout/Retest (Construct 2).
- **Feasibility**: **Highest (10/10)**. Publishes daily written Bitcoin and Forex setups with exact invalidations and multi-tier take-profits.
- **Role in MTS**: Direct daily FVG signal feed with zero social media scraping fragility.

### 3.5 Trader XO (@Trader_XO)
- **Construct**: Volume Profile Imbalances (POC/VAH/VAL) and S/R Range Deviations (Construct 4).
- **Feasibility**: Medium-High. Best ingested via Sunday livestream audio transcriptions.
- **Role in MTS**: Weekly macro swing bias layer.

---

## 4. Priority Implementation Selection

To achieve maximum rigor and testability with minimal fragility, we select:
1. **RLinda** (TradingView) and **Justin Bennett** (Daily Price Action) as the **primary automated ingestion sources** (deterministic schemas, turnkey parsing).
2. **Crypto Chase** and **Roman Trading** as the **primary manual/semi-automated social signal inputs** (covering FVG and Volume Absorption constructs).

---

## 5. Ingestion & Scorecard Architecture Delivered

In `MyTradingSys/research/analysts/`, we implemented the full modular pipeline:
1. `schema.py`:
   - `AnalystSignal`: Validates price geometry (LONG requires $SL < Entry < Targets$, SHORT requires $SL > Entry > Targets$).
   - `SignalDirection`, `SignalStatus`, `ImbalanceConstruct`.
   - `AnalystCallLedgerRow`: Normalized ledger representation.
2. `ingest_analysts.py`:
   - Robust parsers for TradingView ideas (`parse_tradingview_idea`), DailyPriceAction plans (`parse_dailypriceaction_article`), and Social posts (`parse_social_call`).
   - Handles labeled target lines (`Target 1: 69,000`, `Take Profit 2: 65,000`).
3. `score_analysts.py`:
   - Kline walking engine executing trades with strict MTS standards:
     * Fee: 0.05% per side (SOURCED: `MyTradingSys/backtest/layers/FORMULAS.md:s17`).
     * Fill window: 24 hours (OURS: `MyTradingSys/research/qriptal_2026-10-10/score_calls.py:30`).
     * Timeout window: 7 days (OURS: `MyTradingSys/research/qriptal_2026-10-10/score_calls.py:31`).
     * Collision rule: Stop loss is checked first in every candle (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/score_calls.py:83-84`).
   - Exact binomial power test calculating sample size needed to reject null hypothesis (OURS).
4. `test_analysts_ingestion_and_scorecard.py`:
   - Unit test suite covering all 3 parsers, schema validation, and scorecard metrics (all tests pass).

---

## 6. Drafted Ingestion Task Cards

Three downstream task cards have been drafted in `MyTradingSys/system/tasks/`:
1. `analyst-ingest-rlinda-tv.json`: Automated RSS/scraper for RLinda TradingView publications.
2. `analyst-ingest-bennett-dpa.json`: DailyPriceAction RSS market plan ingestion.
3. `analyst-ingest-cryptochase-x.json`: Crypto Chase FVG social call listener.
