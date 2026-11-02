# Layer Lab Report: Parameter Labels Audit for CoinGlass Field Guide and Analyst Commentary

- **Task**: `gemini-coinglass-guide-source-labels-1102`
- **Lane**: `CODEX`
- **Date**: 2026-11-02
- **Auditor**: Gemini worker (Antigravity JIS-NUC)
- **Audited Deliverables**:
  - `MyTradingSys/research/coinglass_field_guide_2026-11-01/FIELD_GUIDE.md`
  - `MyTradingSys/research/coinglass_field_guide_2026-11-01/ANALYST_COMMENTARY.md`
- **Audit Output**:
  - `MyTradingSys/research/gemini_audits_2026-11-02/coinglass_guide_labels.md`

---

## 1. Executive Summary

A comprehensive numeric threshold, parameter, and quantitative assertion audit was conducted across `FIELD_GUIDE.md` and `ANALYST_COMMENTARY.md` (created 2026-11-01 in commit `79ec6e5fb322`). Each quantitative claim, threshold, window size, ratio, and orderbook metric was audited to label it as `SOURCED` (corroborated by vendor documentation, published papers, or exchange API specifications), `OURS` (internal point-in-time observations, empirical counters SEEN on 2026-11-01, internal backtest/study results, or local live_aid defaults), or `DIFF` (quoted source discrepancies).

### Summary Counts
- **Total Audited Parameters / Claims**: 76
- **SOURCED Parameters**: 57 (75.0%)
- **OURS Parameters**: 19 (25.0%)
- **DIFF (Discrepancies)**: 0 (0.0%)
- **Output Header**: `# SOURCED: 57, OURS: 19, DIFF: 0`

---

## 2. Key Findings & Categorization

### A. Core Sourced Specifications (`SOURCED`: 57)
1. **CoinGlass Liquidity Heatmap & Walls Rules (`FIELD_GUIDE.md:36-54`)**:
   - Wall qualification minimum size: `$1.5M USD` on BTC per row (`FIELD_GUIDE.md:39`).
   - Default price grid: `$10 USD` per row for BTC (`FIELD_GUIDE.md:44`).
   - Depth calculation band: `+/-1 %` default around price (`FIELD_GUIDE.md:44,54`).
   - Update frequency: `~2 s` live WebSocket refresh (`FIELD_GUIDE.md:36`).
   - History retention buffers: `1m` history reaches back `~2 days`, `1h` reaches back `~3 months` (`FIELD_GUIDE.md:36`).
   - Fill vs pull classification: touched and pulled within the same minute counts as touched (`FIELD_GUIDE.md:40`).
2. **Footprint & Order Flow Parameters (`FIELD_GUIDE.md:48-52`)**:
   - Diagonal imbalance threshold: `>= 300 %` of diagonal neighbour (`FIELD_GUIDE.md:49`; verified in `phase1_fp_look.py:3,10`).
   - Stacked imbalance: `3` consecutive price levels (`FIELD_GUIDE.md:49`).
   - Near-balanced shading: volume within `10 %` shaded grey (`FIELD_GUIDE.md:50`).
   - CVD divergence detector: swing separation `4-60 bars`, confirmed `5 bars late` with no repaint (`FIELD_GUIDE.md:51-52`).
3. **Exchange Architecture & API Contracts (`FIELD_GUIDE.md:95-112`)**:
   - Binance perpetual contract tick size: `0.1 USD` (`FIELD_GUIDE.md:95`).
   - Binance `/fapi/v1/depth` limit: default `100` levels used in `src/main/java/datafeed/MarketDataSnapshot.java:247`, max `1000` levels (`FIELD_GUIDE.md:112`).
   - `MarketDataSnapshot` depth band: `currentPrice * 0.99` to `currentPrice * 1.01` (`MarketDataSnapshot.java:64,69`).
   - Binance liquidation websocket throttle: `1 print/s per symbol` (`FIELD_GUIDE.md:102`).
4. **Analyst & Quantitative Literature Benchmarks (`ANALYST_COMMENTARY.md:82-126`)**:
   - Cointelegraph Research / ACM study on 2022-05-11 LUNA crash: `248,796` submitted & cancelled orders (`ANALYST_COMMENTARY.md:82`), `124` uniform orders within 1 hour (`ANALYST_COMMENTARY.md:83`), `$37M` vanished ladder (`ANALYST_COMMENTARY.md:84`).
   - Hasbrouck & Saar (2009): `~1/3` of limit orders cancelled within `2 s` in 2004 equities (`ANALYST_COMMENTARY.md:85`).
   - CoinAnk depth metrics (Sep 2025 to Apr 2026): aggregate `+/-1 %` depth `180-260M`, falling below `60M` for `10 days` in Feb 2026 (`ANALYST_COMMENTARY.md:88-89`).
   - Kaiko depth reports: Binance 1% depth `> 600M` at Oct 2025 high, `< 400M` post-crash (`ANALYST_COMMENTARY.md:113`).
   - Amberdata/Kaiko flash crash metrics: spreads up to `26.43 bps`, venue visible depth drop from `103.64M` to `0.17M` (`ANALYST_COMMENTARY.md:118`).

### B. Internal Measurements and Engineering Parameters (`OURS`: 19)
1. **Live SEEN Readings on 2026-11-01 (`FIELD_GUIDE.md:62-69`)**:
   - Wall events tab empirical counter on loaded 1m history (~2 days): `191 placed, 1 filled, 176 pulled` (`FIELD_GUIDE.md:17,67`).
   - Point-in-time orderbook depth at 17:32-17:35Z: Bid `190.6M` (2.5K BTC), Ask `288.3M` (3.7K BTC), imbalance `-20.4 %` (`FIELD_GUIDE.md:62-63`).
   - Largest resting walls: Bid `76,500` ($15.6M, -2.05%), Ask `78,350` ($31.2M, +0.32%) (`FIELD_GUIDE.md:64-65`).
   - Walls within `+/-3 %`: `10` total (2 bid, 8 ask) at `1.50M` threshold (`FIELD_GUIDE.md:66`).
   - Repeated spoofing cycles at single levels: Bid `77,000` (-1.4%) placed 5 times, Ask `78,850` (+1.0%) placed 3 times, each lasting `3-21 min` (`FIELD_GUIDE.md:68`).
   - Tooltip cell readings: `$10` row resting volume `$2.1M-$5.9M`, `+/-3 cells` aggregate `$25.20M`, cell bids `40.3 BTC` / `$3.14M`, mid distance `-0.14 %` (`FIELD_GUIDE.md:69`).
2. **Internal Desk Systems & Research Look Results**:
   - `live_aid` Deribit orderbook band: `+/-0.25 %` (`IT.domPct = 0.0025` in `tools/live_aid/live_aid_indicators.js:154,199`).
   - `live_aid` flow horizons: `60 s` taker delta and `15 min` CVD (`flowShortMs: 60000`, `flowLongMs: 900000`).
   - C26 Q8 research look result: CVD divergence hit rate on 30 seen take-outs equalled base rate (`2 of 30` in `PHASE1_RANGE.md:332`).
   - C26 Q7 research look result: Liquidation band proxy excursions (`14` reached band vs `11` stopped short in `PHASE1_RANGE.md:292`).

---

## 3. Discrepancy & Gap Analysis (`DIFF`: 0)

Every cited quote in `FIELD_GUIDE.md` and `ANALYST_COMMENTARY.md` matches its corresponding source without numerical discrepancies:
- The CoinGlass FAQ's qualitative statements ("A pulled wall is often more dangerous than a filled one", "the biggest walls are the easiest bait", "Can I trade straight from the heatmap? Better not") accurately reflect vendor guidance.
- The quantitative claims from academic and industry research (ACM LUNA study, Hasbrouck & Saar, CoinAnk, Kaiko, Amberdata) match verbatim.
- Key gap affirmed: No external literature or vendor provides an empirical conditional distribution of "wall pulled before touch" across cryptocurrency order books; the `191 placed / 1 filled / 176 pulled` count documented in `FIELD_GUIDE.md` provides an empirical baseline supporting the filed `wall-ledger-for-the-live-dashboard-place` card.

---

Noticed: No discrepancies (0 DIFF) detected across 76 audited parameters; 57 are directly SOURCED to external specifications or literature, and 19 are OURS empirical point-in-time observations or internal engineering parameters.
