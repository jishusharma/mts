# External Analyst & Imbalance Setup Layers — Execution Roadmap
**Date**: 2026-10-18  
**Family**: `callers` (`MyTradingSys/system/layer_index.json`)  
**Scope**: Multi-provider ingestion, fee-net kline verification, and testnet promotion for external analysts providing explicit `Entry / Stop Loss / Target` setups (benchmarking against Habib / Qriptal `B162`).  

---

## 1. What Changed on `origin/fast-track` (2026-10-18 Timeline)

| UTC / Local (+05:30) | Commit | Summary of Changes |
|---|---|---|
| `05:29Z` (`10:59 +05:30`) | `60a8d94a` | **Market Survey Shipped**: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md` categorized 11 verified analysts across 4 imbalance constructs (Construct 1: Volume Anomaly/Absorption, Construct 2: Fair Value Gaps, Construct 3: Footprint/Order-Flow Delta, Construct 4: Market/Volume Profile) and created card `review-imbalance-analysts-report-and-imp`. |
| `13:09Z` (`18:39 +05:30`) | `1e405a57` | **Review & Engine Built**: Delivered `MyTradingSys/research/analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md`, implemented the modular ingestion and kline-scoring stack (`schema.py`, `ingest_analysts.py`, `score_analysts.py`, `run_scorecard.py`, `test_analysts_ingestion_and_scorecard.py` — 9/9 unit tests passing), and created 3 ready build cards (`analyst-ingest-rlinda-tv`, `analyst-ingest-bennett-dpa`, `analyst-ingest-cryptochase-x`). |
| `14:01Z` (`19:31 +05:30`) | `e544506d` | **Strict Provenance Cleanup**: Purged the 4 illustrative sample rows from `MyTradingSys/research/analysts/SAMPLE_CALL_LEDGER.csv` so the ledger is strictly header-only until genuine, timestamped public calls are ingested (`NO ASSUMPTIONS, NO FABRICATIONS`). |
| `16:28Z` (`21:58 +05:30`) | *Current* | **Roadmap & Sync**: Regenerated `SCORECARD.md` from the clean header-only `SAMPLE_CALL_LEDGER.csv` (removing stale sample rows), closed completed card `review-imbalance-analysts-report-and-imp`, added `analyst-ingest-roman-x` (Construct 1 Volume Absorption peer to Habib), wired all `analyst-ingest-*` cards and `MyTradingSys/research/analysts/` into family `callers` in `layer_index.json` / `LAYERS.md`, and shipped this `ROADMAP.md`. |

---

## 2. End-to-End Phased Execution Roadmap

```
Phase 0 (DONE)             Phase 1 (READY NOW)               Phase 2 (GATE)                  Phase 3 (TESTNET)
──────────────────────     ─────────────────────────────     ───────────────────────────     ─────────────────────────
• Survey 11 analysts       • analyst-ingest-rlinda-tv        • Walk calls on 1m Binance      • Promote only analysts
  across 4 constructs      • analyst-ingest-bennett-dpa        BTCUSDT klines (0.05%/side      passing Phase 2
• Build schema.py,         • analyst-ingest-cryptochase-x      fee, stop-first collision)      (n >= 56, net R > 0)
  ingest_analysts.py,      • analyst-ingest-roman-x          • Statistical Power Gate:       • Dedicated testnet
  score_analysts.py        • B162 / D21 Qriptal Discord        - Triage: n >= 30 (60.5%)       subaccount per caller
• 9/9 unit tests green       & Sunday stream captions          - Promotion: n >= 56 (80%)      (strictly SOURCED SL/TP)
```

### Phase 0: Survey, Evaluation & Core Scoring Engine (`DONE`)
- **Survey Report**: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md`
- **Technical Evaluation**: `MyTradingSys/research/analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md`
- **Codebase (`MyTradingSys/research/analysts/`)**:
  - `schema.py`: Enforces directional price geometry (`LONG`: `stop_loss < entry_price < targets`; `SHORT`: `stop_loss > entry_price > targets`).
  - `ingest_analysts.py`: Deterministic parsers for TradingView ideas (`parse_tradingview_idea`), DailyPriceAction articles (`parse_dailypriceaction_article`), and social posts (`parse_social_call`).
  - `score_analysts.py` & `run_scorecard.py`: Scores calls on Binance 1m klines with `0.05%` fee per side (`FORMULAS.md:s17`), `24h` limit fill window, `7d` max hold, and conservative intra-bar stop-first collision (`qriptal_2026-10-10/score_calls.py:83-84`).
  - `test_analysts_ingestion_and_scorecard.py`: 9 unit tests verifying parsers, schema invariants, fee-net R math, and binomial power.

---

### Phase 1: Real Call Ingestion & Historical Backfill (`READY` — Next Up in Queue)

Each card below is `ready` in `MyTradingSys/system/tasks/` under family `callers` (`lane: SONNET`, `weight: ROUTINE`):

| Priority | Task Card ID | Target Analyst & Platform | Imbalance Construct | Output Ledger |
|---|---|---|---|---|
| **1A** | `analyst-ingest-rlinda-tv` | **RLinda** (`tradingview.com/u/RLinda/`) | Construct 4 (`S_R_LIQUIDITY_TRAP` / false breakouts; immutable Play-Button verification) | `MyTradingSys/research/analysts/rlinda/CALL_LEDGER.csv` |
| **1B** | `analyst-ingest-bennett-dpa` | **Justin Bennett** (`dailypriceaction.com`) | Construct 2 (`FVG_DISPLACEMENT` / unmitigated daily/4H FVGs & S/R retests) | `MyTradingSys/research/analysts/bennett/CALL_LEDGER.csv` |
| **1C** | `analyst-ingest-cryptochase-x` | **Crypto Chase** (`@Crypto_Chase`) | Construct 2 (`FVG_DISPLACEMENT` / HTF inefficiency fills & liquidity sweeps) | `MyTradingSys/research/analysts/cryptochase/CALL_LEDGER.csv` |
| **1D** | `analyst-ingest-roman-x` | **Roman Trading** (`@Roman_Trading`) | Construct 1 (`VOLUME_ABSORPTION` / CVD divergence — direct peer to Habib) | `MyTradingSys/research/analysts/roman/CALL_LEDGER.csv` |
| **1E** | `B162` / Decision `D21` | **Habib / Qriptal** (Discord & YouTube) | Construct 1 (`VOLUME_ABSORPTION` / small-body volume anomaly + key level + wick) | `MyTradingSys/research/qriptal_2026-10-10/CALL_LEDGER.csv` & `habib_trading_thoughts.md` |

**Hard Provenance Rule for Phase 1**:
- Every row written to `<analyst>/CALL_LEDGER.csv` MUST carry a real `source_url` (or verbatim Discord/stream reference) and an exact `published_utc` timestamp prior to trade entry. Zero synthetic or back-filled hindsight calls are permitted.

---

### Phase 2: Kline Verification & Statistical Power Gate (`PENDING PHASE 1 LEDGERS`)

Once Phase 1 ledgers accumulate historical and forward calls, `run_scorecard.py` evaluates each analyst on Binance USD-M `BTCUSDT` 1m klines:
1. **Execution Realism**:
   - Earliest fill check starts strictly at `published_utc` (no look-ahead).
   - Unfilled limit orders after `24h` expire as `NOT_FILLED` (excluded from win-rate denominator, tracked for fill-rate selectivity).
   - Both entry and exit incur `0.05%` taker fee (`10 bps` round-trip); if a bar touches both `stop_loss` and `target_1`, `LOSS` is assigned first.
2. **Sample Size & Statistical Power Gate (`SCORECARD.md` Section 2)**:
   - **Triage Floor ($n = 30$ resolved trades)**: Provides $60.5\%$ power against a $50\%$ coin-flip null at a claimed $67.1\%$ win rate (requires $\ge 20$ wins). Analysts with fee-net $\sum R < 0$ at $n = 30$ are dropped.
   - **Promotion Gate ($n = 56$ resolved trades)**: Provides **$81.0\%$ statistical power** at $\alpha = 0.05$ (requires $\ge 35$ wins, fee-net mean $R > 0$, and day-block bootstrap CI95 lower bound $> 0$).

---

### Phase 3: Algorithmic Construct Track (Footprint Stacked Imbalances)

While Construct 1 (candle-level volume anomaly fade) showed no standalone mechanical edge after fees (`imbalance_qriptal_2026-10-16/README.md`), Construct 3 (**TradingRiot Footprint Stacked Imbalances**) remains an open algorithmic research track:
- **Hypothesis**: $\ge 3$ consecutive diagonal bid/ask imbalances ($\ge 300\%$ ratio) at a pre-existing HTF level or value-area boundary, paired with delta absorption.
- **Data Requirement**: Historical Binance `aggTrades` (`F:/MTS/data/binance_raw/aggTrades`) on `DEV` (`< 2024-07-01`), gated by a count-and-power pre-registration (`PRE_REG_TEMPLATE.md`) before any outcome read.

---

### Phase 4: Testnet Shadow Execution (`layer:callers:<analyst_id>`)

- Any analyst clearing the Phase 2 Promotion Gate ($n \ge 56$ scored calls, fee-net CI95 low $> 0$) is promoted to an isolated testnet subaccount (following the `B162` architecture).
- Orders use strictly the analyst's stated `entry_price`, `stop_loss`, and `targets` (`SOURCED`), gated by the MTS live-engine safety checks (`fail_closed`).
