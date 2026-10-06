# T069 - P5: Funding settlement clock event study

Opened 2026-10-06 by MTS-2026-10-06-1254Z-APP-ANA-research-agenda. Status QUEUED. Source: research agenda follow-up.

## Scope

Event study around Deribit funding settlement times (00:00, 08:00, 16:00 UTC):
- **Metric:** Spread proxy (bid-ask in orderflow_1m), volume, realized volatility, forward return
- **Data:** F:/MTS/data/orderflow_1m + funding history 2025-09 onward (Deribit API)
- **Control:** Placebo clock times (random settlement-equivalent times)
- **Caveat:** Single-regime analysis (no regime-conditional tests)

## Rationale

Funding settlements create sharp liquidity shifts and often trigger quick reversals. Understanding the settlement signature may identify tactical entry/exit timing.

## Pre-registration

Must pre-register (commit before computation) per research brief:
- Exact metrics and windows
- Placebo control methodology
- NO-SOURCE tags for any unsourced thresholds
- Report effective n and bootstrap CI95

## Deliverable

Output: MyTradingSys/research/P5_FUNDING_SETTLEMENT_CLOCK_YYYY-MM-DD.md
