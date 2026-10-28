# T071 - P7: Absorption event analysis after P2 (Fabio followup)

Opened 2026-10-06 by MTS-2026-10-06-1254Z-APP-ANA-research-agenda. Status QUEUED. Source: research agenda follow-up.

## Scope

P2 (Fabio v3 holdout) produced L3-FAIL result. Follow-up: analyze order-flow absorption patterns around Fabio signal events:
- **Trigger:** Fabio setup events (model signals from backtest/layers/fabio/)
- **Metric:** Big-trade absorption (b99/b999 volumes) at marked price levels, forward return post-absorption
- **Data:** orderflow_1m, Fabio event timestamps
- **Analysis:** Does absorption predict Fabio edge? (setup validity test)

## Rationale

P2 failed on backtest holdout (negative net R), but Fabio extracts highlight order-flow driven setups (footprint balance/imbalance detection). If absorption signatures align with Fabio events, the model logic may be sound but cost/fill issues in replay.

## Dependencies

- Requires Fabio event replay/timestamps from backtest
- May inform P2 retuning or P5/P6 optimization

## Pre-registration

Must pre-register:
- Absorption window (bars before/after signal)
- Big-trade thresholds (b99/b999 definitions from orderflow_bars.py)
- Price-level targeting (VAH/VAL/POC/marked zones from Fabio)
- Placebo control (random timestamps vs signal timestamps)

## Deliverable

Output: MyTradingSys/research/P7_ABSORPTION_POST_P2_YYYY-MM-DD.md
Result: Signal-time absorption signatures (n, mean volume, forward return) vs placebo

## Evidence added 2026-10-09 (volume study, MTS-2026-10-09-APP-ANA-btc-volume)

Absorption / exhaustion defined on 4h bars (RVadj >= 2 with range <= 0.8 x ATR14; or RVadj >= 2 at a 20-bar extreme closing off it) occur only 36-82 times in 4.5 years of BTC, so the registered 4h test is INSUFFICIENT-N (V1_DEV_RESULTS.md); descriptive numbers
(NOT evidence) are in V4_RESULTS.md, e.g. buying climax followed by +141 bp over 3 days [+12, +259] vs +36 bp for all bars, absorption in an uptrend +462 bp over 7 days [+139, +812]. The test belongs at 1m / aggTrades where n is large; thresholds there need their own pre-registration.
