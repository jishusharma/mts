# T060 Low-volatility anomaly on BTC

Opened 2026-10-01. Status OPEN. Severity MED.

## Source

Operator-supplied newsletter from paperswithbacktest, 2026-09-30. Underlying academic work:
- Ang, Hodrick, Xing, Zhang 2006 (low-volatility anomaly)
- Frazzini and Pedersen 2014 (betting against beta)
- Baker, Bradley, Wurgler 2011 (benchmarks as limits to arbitrage)

## Claim (not verified on our data)

Ranking US equities by trailing realized vol and holding value-weighted quintiles, monthly rebalance, 1963-2026:
- Lowest-vol quintile: 11.2% annualized return, 12.1% vol
- Highest-vol quintile: 6.6% annualized return, 28.4% vol
- Anomaly survived publication; Sharpe 0.48 pre-publication, 0.80 out-of-sample (2006-2026)

## Open question for MTS

Does the anomaly exist in crypto at any horizon MTS can compute?
BTC alone is one asset. Quintiles need a cross-section. Three candidate shapes:
1. Cross-sectional crypto panel: rank top N coins by trailing realized vol, hold low-vol basket.
2. Time-series state classification on BTC: classify regime by BTC realized vol alone, compare forward return by bucket.
3. Leave for equities only; do not adapt.

## Gate

Per methodology/playbook.md Part I: newsletter is T3 practitioner content, not admissible as core rule evidence. The backtest decides. No engine rule enters on this item alone.

## Next step

Choose the cross-sectional vs time-series shape, then spec a driver under MyTradingSys/backtest/layers/ with the same method as FABIO_L1 (IS/OOS 70/30, fees 0.10% RT, PBO).
