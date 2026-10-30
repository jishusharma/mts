# Parameter Labels Audit: promotion

Audit of numeric parameter defaults in `MyTradingSys/backtest/layers/promotion/`.

## Parameters

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `MIN_TRADES` | `MyTradingSys/backtest/layers/promotion/promote.py:40` | `30` | `OURS` | Inline comment: `# OURS: sanity floor on the OOS sample (GO_LIVE_BAR needs 200 testnet trades later); not from a trader` |
| `SIZE_CEILING_USD` | `MyTradingSys/backtest/layers/promotion/promote.py:41` | `10000` | `OURS` | Inline comment: `# = auto_trader.SIZE_CEILING_USD (test_promote asserts they match)` |
| `POWER_Z` | `MyTradingSys/backtest/layers/promotion/promote.py:42` | `0.84` | `OURS` | Inline comment: `# OURS: z for 80% power in the MDE trade floor` |
| `MDE_SAFETY` | `MyTradingSys/backtest/layers/promotion/promote.py:43` | `4` | `OURS` | Inline comment: `# OURS: safety factor on the MDE-based trade floor` |
| `BOOT_SEED` | `MyTradingSys/backtest/layers/promotion/promote.py:44` | `20261016` | `OURS` | Inline comment: `# OURS: bootstrap seed for the OOS recompute` |
| `BOOT_DRAWS` | `MyTradingSys/backtest/layers/promotion/promote.py:45` | `2000` | `OURS` | Inline comment: `# OURS` |
| `TOL_R` | `MyTradingSys/backtest/layers/promotion/promote.py:46` | `0.01` | `OURS` | Inline comment: `# OURS: max |manifest - recompute| for net_r and both CI ends, in R` |
| `TOL_N` | `MyTradingSys/backtest/layers/promotion/promote.py:47` | `0.05` | `OURS` | Inline comment: `# OURS: max relative |n_trades - rows in trades_csv|` |
| `holm_z alpha tail` | `MyTradingSys/backtest/layers/promotion/promote.py:59` | `0.025` | `OURS` | Docstring: `OURS: two-sided 5% Holm/Bonferroni critical z for variants trials in the ledger (z=1.96 for 1)` |
| `mde_floor 95% SE divisor` | `MyTradingSys/backtest/layers/promotion/promote.py:64` | `3.92` | `OURS` | Statistical 95% normal CI interval divisor ($2 \times 1.96 = 3.92$); inline comment in docstring: `se = (ci_high-ci_low)/3.92` |
| `recompute_oos alpha percentiles` | `MyTradingSys/backtest/layers/promotion/promote.py:87` | `0.025`, `0.975` | `OURS` | Docstring: `percentile bootstrap (95%) of the mean, seeded.` |
| `size_entry default ceiling` | `MyTradingSys/backtest/layers/promotion/registry.py:94` | `10000` | `OURS` | Internal maximum sizing cap matching `auto_trader.SIZE_CEILING_USD` |
| `size_entry contract tick/lot multiple` | `MyTradingSys/backtest/layers/promotion/registry.py:96,100` | `10` | `SOURCED` | Deribit exchange contract specification: docstring `a multiple of 10 (Deribit contract)` in `registry.py:96` |
