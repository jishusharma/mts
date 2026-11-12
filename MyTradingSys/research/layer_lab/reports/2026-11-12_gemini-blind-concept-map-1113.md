# Gemini Blind Concept Map Report (Task: gemini-blind-concept-map-1113)

Date: 2026-11-12 (UTC)
Task: `gemini-blind-concept-map-1113`
Worker: `gemini-3.8-flash-low`

## Objective & Methodology

Pursuant to the operator gap hunt directive (2026-11-13), an independent, unbiased concept map of Tom Vorwald and Fabio Valentini's trading method was compiled from the canonical transcript files (`raw_transcripts_canonical/<id>_raw.txt`) across all 28 designated video IDs.

In strict compliance with task constraints:
1. Only canonical transcript text files were read; no repo documentation, existing extractions, or research notes were opened.
2. Every concept and decision step is documented with verbatim quotes, position tag (`BEGIN`, `MIDDLE`, or `END`), estimated timestamp (`[mm:ss]`), and Source GPS ID.
3. Every stated number is explicitly labeled `SOURCED` (referencing verbatim transcript speech) or noted as `None`.
4. All quotes and GPS tags were validated against `scripts/dev/verify_extract_quotes.py`.

## Deliverables

- **Map Document:** `MyTradingSys/research/layer_lab/gap_hunt_1113/gemini_blind_map.md`
- **Checker Verification:**
  `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/layer_lab/gap_hunt_1113/gemini_blind_map.md`
  Exit status: 0 (PASS, 0 problems across 97 validated quotes).

## Summary of Core Methodological Findings & Numbers

### 1. Market Auction & Profile Dynamics
- **Regime Distribution:** Markets trend stably only ~30% of the time, while ~70% of time is spent in balance/consolidation (`43JaKHRvxHk:BEGIN`, `Fj4FDZQxw0I:END`, `VumVuGnCcFM:END`). True trend days occur in only ~20% of trading sessions (`VumVuGnCcFM:END`).
- **Passive Liquidity:** >95% of observable market volume consists of passive limit orders (`NkQeOVDTAec:BEGIN`).
- **Single Print & Fair Value Zones:** Single prints formed on 30-minute charts represent swift unfair price discovery where price never retraced (`Fj4FDZQxw0I:MIDDLE`, `T6hDJcHrVBM:BEGIN`).

### 2. Decision Framework
- **Entry:** Entries are executed primarily via pullbacks or counter-trend shifts only after "proof" (absorption, rejection, or balance shift) is demonstrated at high volume or unfair price zones (`BVpYGKz9PBU:END`, `qLnQan0KGmQ:MIDDLE`, `wPMiyJXL0zU:MIDDLE`).
- **Stop Loss:** Mechanically placed behind structural invalidation levels (e.g. above prior high volume/balance nodes or outside single print zones), never arbitrarily (`BVpYGKz9PBU:MIDDLE`, `l8RZrBfzvp4:MIDDLE`, `ujedEcmvBMk:BEGIN`).
- **Target:** Anchored to high volume nodes, point of control (POC), or value area boundaries, frequently taking profit slightly ahead of crowded levels (`l8RZrBfzvp4:MIDDLE`, `qLnQan0KGmQ:END`, `yRvMW6lgN1o:BEGIN`).
- **Timeframes:** Context established on macro/30-minute charts; execution timed on 5-minute charts. Trading 5-minute charts without macro structure is identified as a primary cause of account loss (`vk0mkNPuhDc:BEGIN`, `Fj4FDZQxw0I:MIDDLE`).
- **Filters:**
  - VIX / Volatility >20 signifies elevated institutional risk and capital withdrawal (`C9n_d91Uitc:BEGIN`).
  - Index concentration: The "Magnificent 7" stocks hold over 30% weighting in S&P 500 / Nasdaq futures, necessitating monitoring of mega-cap capital flows (`v5EuDl9c0iI:BEGIN`, `Kg6sYKgtkrY:BEGIN`).
  - Economic news events (e.g., 14:30 GDP releases) require heightened risk management (`Ld1dhjGdTCA:BEGIN`).
  - Liquidity window: Highest market liquidity spans 08:30–17:35 cash hours; midday hours (13:00–15:00) exhibit low volume traps (`T6hDJcHrVBM:BEGIN`, `wPMiyJXL0zU:MIDDLE`).
- **Management & Statistical Edge:** Mathematical edge relies on asymmetric risk-reward ratios (typically 2.5:1, 3:1, up to 6:1) evaluated across 100–300 trades, generating robust profitability even with 30%–40% hit rates (`BVpYGKz9PBU:MIDDLE`, `UOBgXV20yCM:MIDDLE`, `NkQeOVDTAec:END`, `yRvMW6lgN1o:BEGIN`, `zQTbdEweG3c:BEGIN`).
- **No-Trade:** Absolute rules against blind 5-minute trading, naive mean reversion on trend days, and unhedged leveraged overnight exposure subject to gap risk (`vk0mkNPuhDc:BEGIN`, `43JaKHRvxHk:BEGIN`, `dh-ysRR8f-M:BEGIN`).
