# BLOCKED — LC1 UTC-day level hold test (2026-10-14)

**Verdict: BLOCKED.** The required Binance BTCUSDT perpetual 1-minute DEV bars for 2024-12 through 2025-03 are not present in this environment. Without those bars, no empirical level-hold result can be calculated; no family is labeled KEEP or DROP.

## What was checked

- Task scope/data window: `MyTradingSys/research/levels_confluence_2026-10-14/PLAN.md` (LC1 and “Data and windows” sections; DEV is 2024-12..2025-03).
- Kline loader expects CSVs under `<root>/klines`: `MyTradingSys/backtest/bt/bt_data.py:9-14`.
- Data inventory command: `python -c "from pathlib import Path; p=Path('F:/MTS/data/binance_raw'); print('binance_raw exists',p.exists()); print('children', [(str(x),sum(1 for _ in x.rglob('*.csv'))) for x in p.iterdir()] if p.exists() else []); print('repo Dumps',Path('Dumps').exists())"`
- Result: `binance_raw exists True`; its only child is `F:\MTS\data\binance_raw\aggTrades` with **0 CSV files**; repository `Dumps` does not exist. There is no `<root>/klines` dataset available for `load_klines`.

## Findings

| Severity | Evidence | Finding | Status |
|---|---|---|---|
| HIGH | `F:/MTS/data/binance_raw/aggTrades` has 0 CSV files; `Dumps` absent; `bt_data.py:9-14` loads only `<root>/klines/*.csv` | DEV OHLCV input is unavailable. Per-day levels, touches, five matched-distance random lines, day-block bootstrap CIs, and L1→L2 outcomes cannot be measured. | NOT_IN_DATA |
| HIGH | `PLAN.md`, LC1 steps 1–4 | Required outcomes are empirical and cannot be replaced by synthetic fixtures or inferred from another period. No KEEP/DROP list or L2 reached percentage is supportable. | BLOCKED |

## Parameters / provenance

The plan specifies the scope and level families. The task’s stop width is `max(0.40% of price, 0.10% level buffer)`; volume-profile bins are $10 and 70% value area. These are not run here. Validation (2025-04..2025-06) and holdout (2025-07+) were not accessed.

## Required to resume

Provide the BTCUSDT 1-minute kline CSV dataset for DEV 2024-12..2025-03 at a readable `<root>/klines` path (compatible with `bt_data.load_klines`). Then build and test the scoped implementation and compute the registered DEV comparisons. The card was not marked done.