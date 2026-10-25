# Layer Fact Sheet: callers

**Family**: `callers` (Posted trade calls: Qriptal, RLinda, Bennett, Crypto Chase, Roman)  
**Layer IDs**: `callers` (family container / multi-analyst ingestion & scoring)  
**Reference Specification**: `ANTIGRAVITY_LAPTOP.md` Item C  
**Sources Examined**:
- `MyTradingSys/system/LAYERS.md:208-220`
- `MyTradingSys/system/layer_index.json:206-253`
- `MyTradingSys/items/B162_qriptal_signal_layer.md:1-53`
- `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:1-376`
- `MyTradingSys/research/analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md:1-107`
- `MyTradingSys/research/analysts/ROADMAP.md:1-84`
- `MyTradingSys/research/analysts/SCORECARD.md:1-33`
- `MyTradingSys/research/analysts/schema.py:1-140`
- `MyTradingSys/research/analysts/ingest_analysts.py:1-260`
- `MyTradingSys/research/analysts/score_analysts.py:1-210`
- `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:1-74`
- `MyTradingSys/research/qriptal_2026-10-10/RULES.md:1-80`
- `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md:1-95`
- Ruling: `B190` (`scripts/dev/lab_query.py rulings callers`)

---

## 1. ORIGIN

- **Analyst Benchmark (Habib / Qriptal)**:
  - Quoted source: *"There is new research on Imbalance trading that DSA did - We have a analyst from you tube who also posts on discord. Habib his name. Imbalance trader. Discord is setup with his chanel - we need the feed - he provides trades with entried andtargets - he trades candles on diff time frames with imbalnces on diff exchanges - so we need his layer!"* (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:9`)
  - Quoted source: *"Working! It is easy - just place trades that he says! and do see his past record - verify."* (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:11`)
  - Quoted source: *"qriptal.com (operator paste): 86 setups, 67.1% win rate, 49 W / 13 BE / 24 L, avg winner 3.99%, avg loser 0.63%. Self-reported; not verified."* (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:23-24`)
  - Quoted source: *"Qriptal is an external signal to be scored, not a rule source. His 'imbalance' indicator is sold and undisclosed, so a rule built from it is REJECT tier (playbook Part I). His imbalance = small-body high-volume candle; it is not an FVG and not the order-book imbalance in research/imbalance_2026-10-10/RESEARCH.md"* (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:18-20`)
- **Crypto Chase (@Crypto_Chase)**:
  - Quoted source: *"Trading Style: Patient swing and intraday trader. Identifies HTF displacement imbalances, waits for price to retrace and fill the inefficiency, and enters on confirmation wicks or structural flips."* (SOURCED: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:101`)
  - Quoted source: *"Imbalance Construct: Fair Value Gaps (FVG), Liquidity Imbalances, S/R Deviations."* (SOURCED: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:100`)
- **Roman Trading (@Roman_Trading)**:
  - Quoted source: *"Imbalance Construct: Volume Anomaly / Absorption Imbalances & CVD Divergences (Virtually identical to Habib's Construct F)."* (SOURCED: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:119`)
  - Quoted source: *"Specializes in finding volume absorption candles at key horizontal support/resistance levels. When high volume enters at a swing low but price fails to break down (small body/long lower wick), he flags it as institutional absorption and executes reversal fades."* (SOURCED: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:120`)
- **Justin Bennett (@JustinBennettfx / Daily Price Action)**:
  - Quoted source: *"Methodology: Unmitigated Fair Value Gaps, Daily Price Action Breakouts & Retests."* (SOURCED: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:215`)
  - Quoted source: *"Posts daily free written market plans with explicit: Entry: Retest of unmitigated FVG or daily breakout level. Stop Loss: Logical structural invalidation level. Take Profit: Multiple tiers (TP1, TP2) based on opposing major liquidity pools."* (SOURCED: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:217-220`)
- **RLinda (TradingView Top Author)**:
  - Quoted source: *"Methodology: Price Action, False Breakouts, Key S/R Liquidity Traps."* (SOURCED: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:248`)
  - Quoted source: *"TradingView Play-Button Verification: Once published on TradingView, ideas cannot be edited or deleted. Anyone can press 'Play' to see the future price bars validate or invalidate the setup."* (SOURCED: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:256`)

---

## 2. PARAMETERS

- **Trade Direction (`direction`)**: `LONG` or `SHORT` (SOURCED: `MyTradingSys/research/analysts/schema.py:19-21`)
- **Entry Price (`entry_price`)**: Numerical execution level; limit or trigger level directly stated by the caller (SOURCED: `MyTradingSys/research/analysts/schema.py:46-47`)
- **Stop Loss (`stop_loss`)**: Explicit structural invalidation price stated by the caller; mandatory non-null (SOURCED: `MyTradingSys/research/analysts/schema.py:48-49`)
- **Profit Targets (`targets`)**: List of 1 to 5 target prices stated by the caller (SOURCED: `MyTradingSys/research/analysts/schema.py:50-51`)
- **Price Geometry Validation**:
  - For `LONG`: `stop_loss < entry_price < targets[0]` (OURS: `MyTradingSys/research/analysts/schema.py:65-68`)
  - For `SHORT`: `stop_loss > entry_price > targets[0]` (OURS: `MyTradingSys/research/analysts/schema.py:70-73`)
- **Taker Fee**: `0.05%` per side (`0.10%` round-trip) (SOURCED: `MyTradingSys/backtest/layers/FORMULAS.md:s17`; `MyTradingSys/research/analysts/score_analysts.py:27`)
- **Slippage**: `2 bps` (OURS: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:359`)
- **Fill Window**: `24 hours` (`1440` minutes) from `published_utc`; unreached limits expire as `NOT_FILLED` (OURS: `MyTradingSys/research/analysts/score_analysts.py:28`; `MyTradingSys/research/qriptal_2026-10-10/score_calls.py:30`)
- **Max Holding Period / Timeout Window**: `7 days` (`10080` minutes); unresolved positions close at market (OURS: `MyTradingSys/research/analysts/score_analysts.py:29`; `MyTradingSys/research/qriptal_2026-10-10/score_calls.py:31`)
- **Bar Collision Resolution**: Intra-candle collision between stop loss and profit target resolves to `LOSS` first (SOURCED: `MyTradingSys/research/analysts/score_analysts.py:126-128`; `MyTradingSys/research/qriptal_2026-10-10/score_calls.py:83-84`)
- **Target Exit Policy**: Primary metric exits 100% position at Target 1 (`target_1`) (OURS: `MyTradingSys/research/analysts/score_analysts.py:129-130`; `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:59`)
- **Statistical Power Thresholds**:
  - Alpha: `0.05` one-sided exact binomial test against `H0 = 50%` coin flip (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:38`)
  - Minimum sample for triage ($60.5\%$ power): `n = 30` resolved trades (OURS: `MyTradingSys/research/analysts/SCORECARD.md:18`; `MyTradingSys/research/analysts/ROADMAP.md:68`)
  - Minimum sample for promotion gate ($80\%$ - $81\%$ power): `n = 56` resolved trades (SOURCED: `MyTradingSys/research/analysts/SCORECARD.md:19,22`; `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:48,51`)

---

## 3. BACKTESTS

- **Habib / Qriptal Kline Scorecard (card `qriptal-score-binance`)**:
  - Report path: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:1-74`
  - Fee-net: Evaluated at `0.05%` taker fee per side (`0.10%` round-trip) (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:34,59`)
  - In-sample / Out-of-sample: DEV window `2025-09-01` to `2026-06-25`; HOLDOUT window `2026-06-26` to `2026-09-26` (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:7-13`)
  - Trades count ($n$): Scored $n = 0$ (DEV rows: 11 total, 0 ELIGIBLE; HOLDOUT rows: 67 total, 2 ELIGIBLE left unscored due to holdout partition seal; Total 81 candidate statements) (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:3,9-13`)
  - Result: No scored trades in DEV; statistical power is $0\%$ at $n = 0$ (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:3,38`)
- **Mechanical Volume Anomaly Candle Study (Habib Construct F baseline)**:
  - Report path: `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md:1-95`
  - Fee-net: Fee drag `0.09` to `0.38 R`; net edge after fees is flat to negative (SOURCED: `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md:81-83`)
  - In-sample / Out-of-sample: 22 named historical candles evaluated on Binance klines (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:41`)
  - Trades count ($n$): $n = 22$ volume anomaly candles (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:41`)
  - Result: Candle anomaly statistically above chance ($p = 0.003$), but pure mechanical fade has NO EDGE after fees (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:41`; `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:32`)
- **Multi-Provider Analysts Scorecard (RLinda, Justin Bennett, Crypto Chase, Roman Trading)**:
  - Report path: `MyTradingSys/research/analysts/SCORECARD.md:1-33`
  - Fee-net: Evaluated at `0.05%` per side (SOURCED: `MyTradingSys/research/analysts/SCORECARD.md:4`)
  - In-sample / Out-of-sample: NOT_IN_DATA (kline evaluation run pending real ledger ingestion; `SAMPLE_CALL_LEDGER.csv` maintained header-only per `ROADMAP.md:14`)
  - Trades count ($n$): $n = 0$ evaluated trades in canonical `SCORECARD.md` (SOURCED: `MyTradingSys/research/analysts/SCORECARD.md:8-9`; `MyTradingSys/research/analysts/ROADMAP.md:14-15`)

---

## 4. KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS

- **Rulings Query**:
  - `python scripts/dev/lab_query.py rulings callers` returns 1 closed ruling:
    - `B190` (Opened `2026-10-16`, Closed, Severity `LOW`): *"MTS-Backup git children flash visible console windows under the vbs/Store python.exe launcher"* (SOURCED: `lab_query.py rulings callers`)
- **Self-Reported Performance Assumptions**:
  - Qriptal claims `86 setups, 67.1% win rate, 49 W / 13 BE / 24 L, avg winner 3.99%, avg loser 0.63%` on `qriptal.com`: unverified and not backed by public entry/stop/target timestamps in repo data (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:23-24`; `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:28-34`)
  - Unstated whether claimed percentages represent raw price movements or unleveraged/leveraged account equity changes (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:34`)
- **Staged Ledger Sample Purge**:
  - 4 illustrative mock rows were initially included in `MyTradingSys/research/analysts/SAMPLE_CALL_LEDGER.csv` and subsequently removed in commit `e544506d` to prevent fabricated trades from polluting the scorecard (`NO ASSUMPTIONS, NO FABRICATIONS`) (SOURCED: `MyTradingSys/research/analysts/ROADMAP.md:14`)
- **Undisclosed Proprietary Indicators**:
  - Qriptal's commercial "imbalance indicator" is sold and closed-source; mechanical reproduction failed to replicate proprietary threshold (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:18-20,41`)
- **Social Media Call Survivorship / Deletion Bias**:
  - Spoken livestreams and Twitter posts carry potential survivorship or unpriced stop risks; 7 Qriptal statements had entries and targets but omitted priced stops, requiring classification as `NO-SOURCE` / unscored (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:55`; `MyTradingSys/research/analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md:30`)

---

## 5. CONFLUENCE

- **Confirming Other Layers**:
  - External caller setups act as discretionary confluence over raw mechanical imbalance occurrences (such as volume anomalies, Fair Value Gaps, and order-book delta imbalances) (SOURCED: `MyTradingSys/research/analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md:17`)
- **Confirmed By Other Layers**:
  - `live_engine` / Binance USD-M klines: Every ingested signal is verified against historical 1m price bars for fill feasibility and strict stop-loss checking before targets (SOURCED: `MyTradingSys/research/analysts/score_analysts.py:114-135`)
  - Key HTF Horizontal Support / Resistance & Order Flow: Callers' entries rely on confluence with pre-planned horizontal levels, value-area rotations, and wick sweeps (SOURCED: `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:28,120`)
  - Testnet Shadow Account Isolation: Intended to operate on isolated testnet subaccounts (`layer:callers:<analyst_id>`), confirmed by live engine risk limits and `fail_closed` guards (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:32`; `MyTradingSys/research/analysts/ROADMAP.md:81-84`)
- **Inter-analyst Correlation**:
  - NOT_IN_DATA (cross-analyst directional agreement or simultaneous trigger matrix has not been backtested)
