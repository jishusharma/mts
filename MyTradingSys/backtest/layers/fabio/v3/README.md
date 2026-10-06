# Fabio v3 Core

This module implements the Fabio v3 trading system as specified in `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md` (v3.1).

## Module Structure

The core is split into five sub-modules:

- **signals.py**: Price action recognition (ATR, balance detection, effort/result, volume profiling, breakout detection, exhaustion, failed auction, defended level)
- **fill.py**: Entry/exit execution (fill detection, missed winner tracking, order slippage)
- **costs.py**: Fee and slippage calculations (maker/taker fees, funding costs, legs with risk/reward metrics)
- **manage.py**: Position management (break-even updates, trailing stops, size adds, event-driven vs. distance-based)
- **day_gates.py**: Daily rules and window management (time gates, day aggregation, first-leg limits, market hours, sampling)
- **models.py**: Trade models A-D (specific entry/exit logic for different market conditions)
- **engine.py**: Orchestration (grid state machine, verdict tracking, model selection, backtest simulation)

## API Contract

The v3 core re-exports all public names from its sub-modules through `__init__.py`. See `pending_test_fabio_v3.py` (lines 9-41) for the complete spec-derived contract.

### Key Types

- **bars**: List of dicts with orderflow columns (t, o, h, l, c, buy_vol, sell_vol, delta, cvd_day, n_agg, n_trades, max_trade, b99_*, b999_*, thr99, thr999, thr_days, poc_price, poc_delta, poc_vol, fp, cvd)
- **trade**: Dict with keys {entry, D, stop0, stop, exit, reason, gross_r, fee_r, net_r, fill_idx, exit_idx, target, moves}
- **verdict**: Signal state name from spec (e.g., "setup", "probe", "armed", "filled")
- **grid params**: Required config for engine; no defaults (NS-grid, cell selection via config or TRIAL_REGISTRY.csv)

## Configuration

Grid parameters (NS-grid cell) must be provided as config; they are not defaulted. The engine convention mirrors spec state names for verdicts.

## Testing

Run the spec-derived test suite:

```bash
python -m pytest MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py -v
```

Run module-specific tests:

```bash
python -m pytest MyTradingSys/backtest/layers/fabio/v3/tests/ -v
```

Gate: `python scripts/dev/run_all_tests.py --quick` includes both.

## Isolation

The v3 core imports only stdlib and orderflow_bars; no dependencies on execution, layers.alerts, or Tom/core modules.
